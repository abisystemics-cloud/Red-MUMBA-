"""Pilote du laboratoire.

    python -m lab.run daily  --state state/lab     # chaque jour : données HL, paper, suspensions
    python -m lab.run weekly --state state/lab     # chaque semaine : fiche de score + champion

L'état (livres, statuts, champion, journal des décisions) vit dans un dossier JSON,
versionné sur la branche `lab-state` par le workflow GitHub. Rien n'est envoyé à un
exchange : c'est de la simulation.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from lab import ask, context, evolve, governor, hl_data, ml, paper, research, signals
from lab.catalog import default_catalog
from scripts.bar_research import Costs

CLEAN_FROM = "2026-07"   # premier mois postérieur aux connaissances de l'assistant concepteur
SPLIT = "2024-01"


def load(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=float))


def report(state: dict, score: dict | None, panel_info: str) -> str:
    champ = state.get("champion")
    md = ["# Laboratoire hl-swarm — rapport", "", f"Généré le {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · {panel_info}", "",
          "Simulation uniquement : aucun ordre réel.", ""]
    md += ["## Champion", "", (f"**{champ['name']}** depuis le {champ['since']}" + (" (provisoire)" if champ.get("provisional") else ""))
           if champ else "Aucun pour l'instant.", ""]
    if champ:
        for cap in (1000.0, 50.0):
            bk = state["books"].get(f"{champ['name']}@{cap:g}")
            if bk:
                pos = ", ".join(f"{c} {w * cap * bk['equity']:+.0f} $" for c, w in sorted(bk["weights"].items(), key=lambda x: -x[1]))
                md.append(f"- positions simulées pour {cap:g} $ : {pos or 'aucune (ordres sous le minimum de 10 $)'}")
        md.append("")
    c = state.get("context")
    if c:
        md += ["## Contexte du jour (macro, institutions, géopolitique)", "", "| indicateur | feu | source |", "|---|---|---|"]
        md += [f"| {context.LABELS[k]} | {'vert' if c['flags'].get(k) else 'rouge' if c['flags'].get(k) is False else 'indisponible'} | "
               f"{c['info'].get(k, '')} |" for k in context.KEYS]
        md.append("")
    cl = state.get("claude")
    if cl:
        md += ["## Échanges avec Claude (connecteurs)", "", "Dernière lecture : " + cl.get("last_log", "aucune réponse reçue pour l'instant") + ".", ""]
        rn = cl.get("risk_note")
        if rn:
            md.append(f"- Risque signalé pour le {rn['day']} : **{rn['level']}** — {rn['summary']} " + " ".join(f"[source]({u})" for u in rn["sources"]))
        if cl.get("keel"):
            k = cl["keel"]
            md.append(f"- Paper trading Keel au {k['day']} : {k['return_pct']:+.2f} % en {k['days']} jours, pire baisse {k['max_dd_pct']:.2f} %. {k['note']}")
        if cl.get("smart_money"):
            d, row = sorted(cl["smart_money"].items())[-1]
            top = sorted(row.items(), key=lambda x: -x[1])
            md.append(f"- Gros traders au {d} : les plus acheteurs {', '.join(f'{c} {v:+.0f}' for c, v in top[:3])} ; "
                      f"les plus vendeurs {', '.join(f'{c} {v:+.0f}' for c, v in top[-3:])}")
        md += [f"- {n['day']} · {n['coin']} : {n['summary']} " + " ".join(f"[source]({u})" for u in n["sources"]) for n in cl.get("notes", [])[-5:]]
        md.append("")
    m = state.get("ml")
    if m:
        md += ["## Machine learning", "", f"Dernier entraînement le {m['trained']} sur l'historique {m['history'][0]} → {m['history'][1]} "
               f"({m['rows']} exemples). Modèles en service aujourd'hui : {', '.join(m.get('live', [])) or 'aucun'}.", ""]
        if m.get("ridge_top"):
            md += ["Ce que la régression a appris (poids les plus forts) : " + ", ".join(f"{k} {v:+.3f}" for k, v in m["ridge_top"]) + ".", ""]
    ev = state.get("evolve")
    if ev:
        last = ev["log"][-1] if ev.get("log") else {}
        md += ["## Évolution (règles inventées par le laboratoire)", "",
               f"{ev['trials']} règles explorées depuis le début en {ev.get('runs', 0)} passages (jugées sur l'apprentissage seul), "
               f"{ev.get('validated', 0)} présentées à la validation, {len(ev['born'])} en service.", ""]
        if last.get("names"):
            md += [f"Présentées à la validation au dernier passage ({last['day']}) :", ""] + [f"- {n}" for n in last["names"]] + [""]
        md += ["Règles nées ici, en paper trading :", ""]
        md += [f"- {b['name']} — née le {b['born']}, Sharpe déflaté {b['dsr']}" for b in ev["born"]] + [""]
    md += ["## Livres de paper trading", "",
           "| règle | capital $ | jours | rendement % | pire baisse % | Sharpe | ordres | ordres ignorés (< 10 $) | état | test séquentiel | porte backtest |",
           "|---|---|---|---|---|---|---|---|---|---|---|"]
    for key in sorted(state.get("books", {})):
        bk = state["books"][key]
        st, s = paper.book_stats(bk), state.get("status", {}).get(bk["spec"], {})
        md.append(f"| {bk['spec']} | {bk['capital']:g} | {st['days']} | {st['return_pct']} | {st['max_dd_pct']} | "
                  f"{st['sharpe'] if st['sharpe'] is not None else '–'} | {bk['orders']} | {bk['skipped_orders']} | "
                  f"{s.get('state', 'paper')} | {s.get('sprt', '–')} | {'oui' if s.get('gate') else 'non' if s.get('gate') is False else '–'} |")
    if score:
        md += ["", f"## Fiche de score du catalogue ({score['n_rules']} règles, historique long)", "",
               "| règle | porte | Sharpe < 2024 | Sharpe ≥ 2024 | IC 95 % | rendement ≥ 2024 coûts ×2 % | baisse ≥ 2024 % | "
               "données propres (≥ 2026-07) % | Sharpe déflaté |", "|---|---|---|---|---|---|---|---|---|"]
        for name, r in sorted(score["rules"].items(), key=lambda x: -x[1]["post_sharpe_ci95"][0]):
            md.append(f"| {name} | {'oui' if r['gate'] else 'non'} | {r['pre']['sharpe']} | {r['post']['sharpe']} | "
                      f"{r['post_sharpe_ci95']} | {r['post_cost_x2_return_pct']} | {r['post']['max_dd_pct']} | "
                      f"{r['clean']['return_pct']} | {r['deflated_sharpe']} |")
    md += ["", "## Journal des décisions (les 40 dernières)", ""] + [f"- {d}" for d in state.get("decisions", [])[-40:]]
    return "\n".join(md) + "\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("daily", "weekly"))
    p.add_argument("--state", default="state/lab")
    p.add_argument("--cache", default="data/bars")
    p.add_argument("--history-from", default="2020-01")
    p.add_argument("--answers", default=None, help="fichier answers.json déposé par Claude (branche claude-answers)")
    a = p.parse_args()
    sdir = Path(a.state)
    state = load(sdir / "state.json", {})
    score = load(sdir / "scorecard.json", None)
    catalog = default_catalog() + evolve.born_specs(state)
    save(sdir / "catalog.json", [{"name": s.name, "family": s.family, "params": dict(s.params)} for s in catalog])
    cost = Costs().side
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log = state.setdefault("decisions", [])

    if a.mode == "weekly":
        from scripts.quant_research import build_panel
        from scripts.tsmom_robustness import ms
        end = datetime.now(timezone.utc)
        last_full = f"{end.year - (end.month == 1):04d}-{(end.month - 2) % 12 + 1:02d}"   # dernier mois complet
        coins, raw, days, C, F, R, _b = build_panel(Path(a.cache), a.history_from, last_full)
        hist = {"coins": coins, "days": days, "C": C, "F": F, "R": R}
        hist["H"], hist["L"], hist["V"] = signals.daily_hlv(raw, coins, days)
        hist["ctx"], _ = context.build_context(days, Path(a.cache), live=False)
        hist["ml_scores"], rows, ridge_top = {}, 0, []
        for kind in ml.MODELS:
            try:
                hist["ml_scores"][kind] = ml.walk_forward(hist, kind)
                model, rows = ml.train_final(hist, kind)
                ml.save(model, kind, sdir, {"trained": today, "rows": rows, "history": [a.history_from, last_full]})
                if kind == "ridge":
                    ridge_top = sorted(zip(ml.FEATURE_NAMES, [float(x) for x in model.coef_], strict=True),
                                       key=lambda kv: -abs(kv[1]))[:5]
            except Exception as e:  # noqa: BLE001 — un modèle qui échoue ne bloque pas le reste du laboratoire
                log.append(f"{today} — entraînement {kind} impossible : {type(e).__name__}: {e}")
        state["ml"] = {"trained": today, "rows": rows, "history": [a.history_from, last_full], "ridge_top": ridge_top}
        log.append(f"{today} — modèles ML ré-entraînés sur {rows} exemples")
        # Évolution en deux étages (voir lab/evolve.py) : explorer sur l'apprentissage, ne présenter que les meilleures
        # à la validation. En mode boucle (lab/loop.json) l'exploration dure `minutes` minutes ; sinon une génération.
        base = default_catalog()
        loop = load(Path(__file__).with_name("loop.json"), {})
        deadline = time.time() + 60 * float(loop.get("minutes", 0)) * bool(loop.get("enabled"))
        known = evolve.born_specs(state)
        names = {s.name for s in base + known}
        ev = evolve._state(state)
        ev0, val0 = ev["trials"], ev["validated"]
        full = research.scorecard(hist, base + known, cost, ms(SPLIT), ms(CLEAN_FROM), extra_trials=val0)
        pool, gens = {}, 0
        while True:
            cands = evolve.propose(state, full, names, seed=ev["trials"] + gens)
            evolve.explore(state, hist, cands, cost, ms(SPLIT), pool)
            gens += 1
            if time.time() >= deadline or not cands:
                break
        short = evolve.shortlist(pool)
        if short:
            sc = research.scorecard(hist, short, cost, ms(SPLIT), ms(CLEAN_FROM), extra_trials=len(base) + len(known) + val0,
                                    var_trials=full["var_trials"])
            log += evolve.select(state, sc, short, today)
            full["rules"].update({b["name"]: sc["rules"][b["name"]] for b in ev["born"] if b["name"] in sc["rules"]})
        else:
            log += evolve.select(state, full, [], today)
        for b in ev["born"]:
            b["dsr"] = full["rules"].get(b["name"], {}).get("deflated_sharpe", b["dsr"])
        ev["runs"] = ev.get("runs", 0) + 1
        log.append(f"{today} — ÉVOLUTION : {ev['trials'] - ev0} règles explorées en {gens} générations, {len(short)} présentées à la "
                   f"validation, {len(ev['born'])} règles nées en service ({ev['trials']} explorées et {ev['validated']} présentées depuis le début)")
        catalog = base + evolve.born_specs(state)
        keep = {s.name for s in catalog}
        score = {**full, "rules": {n: r for n, r in full["rules"].items() if n in keep}, "n_rules": len(catalog),
                 "n_trials": len(base) + ev["validated"]}
        save(sdir / "catalog.json", [{"name": s.name, "family": s.family, "params": dict(s.params)} for s in catalog])
        score["history"] = [a.history_from, last_full]
        save(sdir / "scorecard.json", score)
        log.append(f"{today} — fiche de score recalculée sur {a.history_from} → {last_full} : "
                   f"{sum(r['gate'] for r in score['rules'].values())} règles sur {score['n_rules']} passent la porte")

    from scripts.universe_research import CORE, OTHERS
    panel = hl_data.fetch_panel(CORE + OTHERS, now_ms=int(time.time() * 1000))
    panel["ctx"], cinfo = context.build_context(panel["days"], Path(a.cache), live=True)
    state["context"] = {"flags": {k: (None if v is None else bool(v[-1])) for k, v in panel["ctx"].items()}, "info": cinfo}
    panel["ml_scores"] = {k: sc for k in ml.MODELS if (sc := ml.predict(k, sdir, panel)) is not None}
    if "ml" in state:
        state["ml"]["live"] = sorted(panel["ml_scores"])
    answers = None
    if a.answers and Path(a.answers).exists():
        try:
            answers = json.loads(Path(a.answers).read_text())
        except ValueError:
            answers = None
    for line in ask.ingest(state, answers, panel, time.time() * 1000):
        print(line, flush=True)
        state["claude"]["last_log"] = f"{today} — {line}"
    ask.wire(state, panel)
    for line in paper.step_books(state, panel, catalog, cost):
        print(line, flush=True)
    log += governor.decide(state, score, paper.book_stats, today)
    save(sdir / "requests.json", ask.build_requests(state, panel))
    save(sdir / "state.json", state)
    info = f"{len(panel['coins'])} marchés Hyperliquid, dernier jour clôturé {paper.iso(panel['days'][-1])}"
    (sdir / "report.md").write_text(report(state, score, info))
    print((sdir / "report.md").read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
