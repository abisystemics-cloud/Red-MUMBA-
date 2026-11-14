"""Évolution : le laboratoire invente lui-même de nouvelles règles, passage après passage.

Aucune IA ici : c'est une recherche évolutive ordinaire, en deux étages pour ne pas se
mentir à soi-même.
1. EXPLORER (autant qu'on veut) — des milliers de candidates par passage : mutations des
   meilleures règles connues et tirages au hasard dans la bibliothèque de signaux. Elles
   ne sont jugées QUE sur la période d'apprentissage (avant 2024), frais doublés.
2. PRÉSENTER À L'EXAMEN (très peu) — UNE fois par jour, seules les `validate_per_run`
   meilleures de toutes les explorations depuis le dernier examen (gardées dans
   `state.evolve.pool`), de types différents, sont confrontées à la période de validation (depuis 2024) avec
   la fiche de score complète. Une candidate n'est adoptée que si elle passe la porte ET
   si son Sharpe déflaté atteint `min_dsr`. Le Sharpe déflaté compte toutes les règles
   déjà présentées à l'examen (compteur `validated`) : plus on en présente, plus la
   barre monte. Explorer est gratuit ; regarder la validation se paie.
   (Le 14/11/2026, la première version confrontait chaque candidate à la validation :
   après 73 000 essais le Sharpe déflaté de toutes les règles était tombé à ~0,02 —
   plus rien ne pouvait être distingué de la chance. D'où les deux étages.)
3. APPRENDRE À MARCHER — `max_new` adoptions par JOUR au plus ; une règle adoptée n'est
   pas « bonne » : elle entre en paper trading et doit y faire ses preuves.
4. OUBLIER — une règle née ici et suspendue par le gouverneur est retirée ; au-delà de
   `max_born` règles, les plus faibles cèdent leur place.
Les données « propres » (≥ 2026-07) ne servent JAMAIS à sélectionner.
"""
from __future__ import annotations

import math
import zlib

import numpy as np

from lab.catalog import GATES, Spec, spec
from lab.signals import LB, SIGS, TS_SIGS

CFG = {"per_night": 16, "max_new": 2, "max_born": 24, "min_dsr": 0.6, "random_share": 0.5, "validate_per_run": 6,
       "min_pre_sharpe": 0.8}
GRID = {"w": (0.3, 0.4, 0.5, 0.6, 0.7, 0.8), "mom": (5, 7, 10, 14, 21, 28, 42), "carry": (2, 3, 5, 7, 10, 14, 21),
        "hold": (1, 2, 3, 5, 7, 14), "k": (0, 2, 3, 4, 5), "gate": (None,) + GATES, "model": ("ridge", "gbm"),
        "a": SIGS, "b": SIGS, "sig": TS_SIGS, "la": LB, "lb": LB, "l": LB, "sa": (1, -1), "sb": (1, -1), "s": (1, -1)}
CATEGORICAL = ("gate", "model", "a", "b", "sig", "sa", "sb", "s")
FAMILIES = {"blend": ("w", "mom", "carry", "hold", "k", "gate"), "carry": ("carry", "hold", "k", "gate"),
            "xsmom": ("mom", "hold", "k", "gate"), "ml": ("model", "hold", "k", "gate"),
            "mix": ("a", "la", "sa", "b", "lb", "sb", "w", "hold", "k", "gate"), "ts": ("sig", "l", "s", "hold", "gate")}
DRAW = ("mix",) * 6 + ("ts",) * 2 + ("blend", "carry", "xsmom", "ml")   # le hasard explore surtout la bibliothèque de signaux


def _h(name: str) -> str:
    return f"{zlib.crc32(name.encode()):08x}"


def _make(family: str, params: dict) -> Spec:
    return spec(family, **{k: v for k, v in params.items() if v is not None})


def born_specs(state: dict) -> list[Spec]:
    return [_make(b["family"], b["params"]) for b in state.get("evolve", {}).get("born", [])]


def _random(rng) -> Spec:
    fam = DRAW[int(rng.integers(len(DRAW)))]
    return _make(fam, {k: GRID[k][int(rng.integers(len(GRID[k])))] for k in FAMILIES[fam]})


def _mutate(rng, family: str, params: dict) -> Spec:
    p = {k: params.get(k) for k in FAMILIES[family]}
    for key in rng.choice(FAMILIES[family], size=int(rng.integers(1, 3)), replace=False):
        grid = GRID[key]
        if key in CATEGORICAL or p[key] not in grid:
            p[key] = grid[int(rng.integers(len(grid)))]
        else:
            i = grid.index(p[key]) + int(rng.choice((-1, 1)))
            p[key] = grid[min(max(i, 0), len(grid) - 1)]
    return _make(family, p)


def propose(state: dict, score: dict | None, known: set[str], seed: int, cfg: dict | None = None) -> list[Spec]:
    """Les candidates de la nuit : jamais une règle déjà connue ni déjà essayée."""
    cfg = {**CFG, **(cfg or {})}
    ev = _state(state)
    rng = np.random.default_rng(seed)
    rules = (score or {}).get("rules", {})
    parents = [(r["family"], r["params"]) for _, r in sorted(rules.items(), key=lambda x: -x[1]["pre"]["sharpe"])
               if r["pre"]["sharpe"] > 0 and r["family"] in FAMILIES and r["params"].get("gate") != "claude_risk"][:12]
    taken, out = {_h(n) for n in known} | set(ev["seen"]), []
    for _ in range(cfg["per_night"] * 20):
        if len(out) >= cfg["per_night"]:
            break
        c = _mutate(rng, *parents[int(rng.integers(len(parents)))]) if parents and rng.random() > cfg["random_share"] else _random(rng)
        if _h(c.name) not in taken:
            taken.add(_h(c.name))
            out.append(c)
    return out


def _state(state: dict) -> dict:
    ev = state.setdefault("evolve", {"trials": 0, "born": [], "seen": [], "log": []})
    ev.setdefault("validated", 16 if ev["trials"] else 0)   # 14/11 : les 2 premières adoptions venaient d'un lot de 16
    return ev


def explore(state: dict, panel: dict, cands: list[Spec], cost: float, split_ms: float, pool: dict) -> None:
    """Étage 1 : note chaque candidate sur l'apprentissage seul (frais doublés) ; `pool` garde la meilleure de chaque type."""
    from lab.catalog import weights
    from scripts.quant_research import backtest
    ev = _state(state)
    pre = np.asarray(panel["days"]) < split_ms
    for c in cands:
        pnl, _, _ = backtest(weights(panel, c), panel["R"], panel["F"], 2 * cost)
        r = pnl[pre]
        sd = float(r.std(ddof=1)) if len(r) > 2 else 0.0
        sh = float(r.mean() / sd * math.sqrt(365)) if sd > 0 else 0.0
        sig = _sig(c)
        if sh > pool.get(sig, (-9.0, None))[0]:
            pool[sig] = (sh, c)
    ev["trials"] += len(cands)
    ev["seen"] = ([x for x in ev["seen"] if len(x) == 8] + [_h(c.name) for c in cands])[-60000:]


def _sig(c: Spec) -> tuple:
    return (c.family,) + tuple(c.p(k, None) for k in ("a", "b", "sig", "model"))


def load_pool(state: dict) -> dict:
    """Les meilleures candidates des passages précédents, en attente de l'examen quotidien."""
    out = {}
    for e in _state(state).get("pool", []):
        c = _make(e["family"], e["params"])
        out[_sig(c)] = (e["pre"], c)
    return out


def save_pool(state: dict, pool: dict, keep: int = 40) -> None:
    best = sorted(pool.values(), key=lambda x: -x[0])[:keep]
    _state(state)["pool"] = [{"pre": round(sh, 3), "family": c.family, "params": dict(c.params)} for sh, c in best]


def examined_today(state: dict, today: str) -> bool:
    return any(g["day"] == today and g["tested"] for g in _state(state)["log"])


def shortlist(pool: dict, cfg: dict | None = None) -> list[Spec]:
    cfg = {**CFG, **(cfg or {})}
    best = sorted(pool.values(), key=lambda x: -x[0])[:cfg["validate_per_run"]]
    return [c for sh, c in best if sh >= cfg["min_pre_sharpe"]]


def select(state: dict, score: dict, cands: list[Spec], today: str, cfg: dict | None = None) -> list[str]:
    """Étage 2 : `cands` = les rares candidates présentées à la validation. Adopte, retire, tient les comptes."""
    cfg = {**CFG, **(cfg or {})}
    ev = _state(state)
    rules, lines = score["rules"], []
    ev["validated"] += len(cands)
    status = state.get("status", {})
    for b in [b for b in ev["born"] if status.get(b["name"], {}).get("state") == "suspended"]:
        ev["born"].remove(b)
        lines.append(f"{today} — ÉVOLUTION : {b['name']} retirée (suspendue en paper trading)")
    ok = sorted((c for c in cands if rules[c.name]["gate"] and rules[c.name]["deflated_sharpe"] >= cfg["min_dsr"]),
                key=lambda c: -rules[c.name]["deflated_sharpe"])
    ok = ok[:max(cfg["max_new"] - sum(g["adopted"] for g in ev["log"] if g["day"] == today), 0)]
    for c in ok:
        r = rules[c.name]
        ev["born"].append({"name": c.name, "family": c.family, "params": dict(c.params), "born": today, "dsr": r["deflated_sharpe"]})
        lines.append(f"{today} — ÉVOLUTION : nouvelle règle {c.name} adoptée en paper trading (Sharpe ≥ 2024 {r['post']['sharpe']}, "
                     f"déflaté {r['deflated_sharpe']} sur {ev['validated']} règles présentées à la validation)")
    for b in ev["born"]:
        if b["name"] in rules:
            b["dsr"] = rules[b["name"]]["deflated_sharpe"]
    while len(ev["born"]) > cfg["max_born"]:
        worst = min(ev["born"], key=lambda b: b["dsr"])
        ev["born"].remove(worst)
        lines.append(f"{today} — ÉVOLUTION : {worst['name']} cède sa place (la plus faible des règles nées ici)")
    best = max((rules[c.name]["deflated_sharpe"] for c in cands), default=0.0)
    if not cands:
        return lines
    ev["log"] = (ev["log"] + [{"day": today, "tested": len(cands), "adopted": len(ok), "best_dsr": best,
                               "passed_gate": sum(rules[c.name]["gate"] for c in cands),
                               "names": [f"{c.name} → porte {'oui' if rules[c.name]['gate'] else 'non'}, déflaté {rules[c.name]['deflated_sharpe']}"
                                         for c in cands]}])[-120:]
    return lines
