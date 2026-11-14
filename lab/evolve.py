"""Évolution : le laboratoire invente lui-même de nouvelles règles, nuit après nuit.

Aucune IA ici : c'est une recherche évolutive ordinaire.
1. PROPOSER — chaque nuit, `per_night` candidates : des mutations (un ou deux paramètres
   déplacés d'un cran) des meilleures règles connues, plus quelques tirages au hasard.
2. ÉVALUER — exactement la même fiche de score que le catalogue (lab/research.py).
3. SÉLECTIONNER — une candidate n'est adoptée que si elle passe la porte ET si son
   Sharpe déflaté atteint `min_dsr`. Le Sharpe déflaté compte TOUS les essais faits
   depuis le début (compteur `trials`) : plus le laboratoire essaie, plus la barre
   monte. C'est le garde-fou contre le sur-apprentissage (à force d'essayer, on finit
   toujours par trouver une règle chanceuse).
4. APPRENDRE À MARCHER — `max_new` adoptions par nuit au plus ; une règle adoptée
   n'est pas « bonne » : elle entre en paper trading et doit y faire ses preuves.
5. OUBLIER — une règle née ici et suspendue par le gouverneur est retirée ; au-delà de
   `max_born` règles, les plus faibles cèdent leur place.
Les données « propres » (≥ 2026-07) ne servent JAMAIS à sélectionner : elles restent
un contrôle honnête.
"""
from __future__ import annotations

import numpy as np

from lab.catalog import GATES, Spec, spec

CFG = {"per_night": 16, "max_new": 2, "max_born": 24, "min_dsr": 0.6, "random_share": 0.3}
GRID = {"w": (0.3, 0.4, 0.5, 0.6, 0.7, 0.8), "mom": (5, 7, 10, 14, 21, 28, 42), "carry": (2, 3, 5, 7, 10, 14, 21),
        "hold": (1, 2, 3, 5, 7, 14), "k": (0, 2, 3, 4, 5), "gate": (None,) + GATES, "model": ("ridge", "gbm")}
FAMILIES = {"blend": ("w", "mom", "carry", "hold", "k", "gate"), "carry": ("carry", "hold", "k", "gate"),
            "xsmom": ("mom", "hold", "k", "gate"), "ml": ("model", "hold", "k", "gate")}


def _make(family: str, params: dict) -> Spec:
    return spec(family, **{k: v for k, v in params.items() if v is not None})


def born_specs(state: dict) -> list[Spec]:
    return [_make(b["family"], b["params"]) for b in state.get("evolve", {}).get("born", [])]


def _random(rng) -> Spec:
    fam = list(FAMILIES)[int(rng.integers(len(FAMILIES)))]
    return _make(fam, {k: GRID[k][int(rng.integers(len(GRID[k])))] for k in FAMILIES[fam]})


def _mutate(rng, family: str, params: dict) -> Spec:
    p = {k: params.get(k) for k in FAMILIES[family]}
    for key in rng.choice(FAMILIES[family], size=int(rng.integers(1, 3)), replace=False):
        grid = GRID[key]
        if key in ("gate", "model") or p[key] not in grid:
            p[key] = grid[int(rng.integers(len(grid)))]
        else:
            i = grid.index(p[key]) + int(rng.choice((-1, 1)))
            p[key] = grid[min(max(i, 0), len(grid) - 1)]
    return _make(family, p)


def propose(state: dict, score: dict | None, known: set[str], seed: int, cfg: dict | None = None) -> list[Spec]:
    """Les candidates de la nuit : jamais une règle déjà connue ni déjà essayée."""
    cfg = {**CFG, **(cfg or {})}
    ev = state.setdefault("evolve", {"trials": 0, "born": [], "seen": [], "log": []})
    rng = np.random.default_rng(seed)
    rules = (score or {}).get("rules", {})
    parents = [(r["family"], r["params"]) for _, r in sorted(rules.items(), key=lambda x: -x[1]["post_sharpe_ci95"][0])
               if r["gate"] and r["family"] in FAMILIES and r["params"].get("gate") != "claude_risk"][:12]
    taken, out = known | set(ev["seen"]), []
    for _ in range(cfg["per_night"] * 20):
        if len(out) >= cfg["per_night"]:
            break
        c = _mutate(rng, *parents[int(rng.integers(len(parents)))]) if parents and rng.random() > cfg["random_share"] else _random(rng)
        if c.name not in taken:
            taken.add(c.name)
            out.append(c)
    return out


def select(state: dict, score: dict, cands: list[Spec], today: str, cfg: dict | None = None) -> list[str]:
    """Adopte, retire, tient le compte des essais. → lignes pour le journal."""
    cfg = {**CFG, **(cfg or {})}
    ev = state.setdefault("evolve", {"trials": 0, "born": [], "seen": [], "log": []})
    rules, lines = score["rules"], []
    ev["trials"] += len(cands)
    ev["seen"] = (ev["seen"] + [c.name for c in cands])[-5000:]
    status = state.get("status", {})
    for b in [b for b in ev["born"] if status.get(b["name"], {}).get("state") == "suspended"]:
        ev["born"].remove(b)
        lines.append(f"{today} — ÉVOLUTION : {b['name']} retirée (suspendue en paper trading)")
    ok = sorted((c for c in cands if rules[c.name]["gate"] and rules[c.name]["deflated_sharpe"] >= cfg["min_dsr"]),
                key=lambda c: -rules[c.name]["deflated_sharpe"])[:cfg["max_new"]]
    for c in ok:
        r = rules[c.name]
        ev["born"].append({"name": c.name, "family": c.family, "params": dict(c.params), "born": today, "dsr": r["deflated_sharpe"]})
        lines.append(f"{today} — ÉVOLUTION : nouvelle règle {c.name} adoptée en paper trading (Sharpe ≥ 2024 {r['post']['sharpe']}, "
                     f"déflaté {r['deflated_sharpe']} sur {ev['trials']} essais)")
    for b in ev["born"]:
        if b["name"] in rules:
            b["dsr"] = rules[b["name"]]["deflated_sharpe"]
    while len(ev["born"]) > cfg["max_born"]:
        worst = min(ev["born"], key=lambda b: b["dsr"])
        ev["born"].remove(worst)
        lines.append(f"{today} — ÉVOLUTION : {worst['name']} cède sa place (la plus faible des règles nées ici)")
    best = max((rules[c.name]["deflated_sharpe"] for c in cands), default=0.0)
    ev["log"] = (ev["log"] + [{"day": today, "tested": len(cands), "adopted": len(ok), "best_dsr": best,
                               "passed_gate": sum(rules[c.name]["gate"] for c in cands)}])[-90:]
    if not ok:
        lines.append(f"{today} — ÉVOLUTION : {len(cands)} règles essayées, aucune adoptée (meilleur Sharpe déflaté {best}, seuil {cfg['min_dsr']})")
    return lines
