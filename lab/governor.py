"""Gouvernance : qui est le champion, qui est suspendu — par des règles fixes.

- Suspension d'une règle : son test séquentiel (SPRT) rejette l'avantage annoncé par
  le backtest, ou son livre de paper trading perd plus de `max_dd_pct`.
- Champion : la règle que l'exécution réelle suivrait. Tant qu'aucune règle n'a
  `min_days` de paper trading, le champion est PROVISOIRE (meilleure borne basse de
  Sharpe du backtest parmi celles qui passent la porte). Ensuite, un challenger ne
  détrône le champion que si son Sharpe de paper trading le dépasse d'au moins
  `margin`, et pas plus d'une fois par `min_days`.
Chaque décision est écrite avec sa raison.
"""
from __future__ import annotations

from ml_engine.stats import SPRTMonitor

DEFAULTS = {"min_days": 28, "margin": 0.5, "max_dd_pct": 25.0, "reference_capital": 1000.0, "sharpe_cap": 1.5}


def sprt_status(history: list, expected_sharpe: float, daily_vol: float) -> str:
    if expected_sharpe <= 0 or daily_vol <= 0:
        return "continue"
    m = SPRTMonitor(expected_sharpe, daily_vol)
    out = "continue"
    for _, r in history:
        out = m.update(r)
        if out != "continue":
            break
    return out


def decide(state: dict, score: dict | None, book_stats, today: str, cfg: dict | None = None) -> list[str]:
    cfg = {**DEFAULTS, **(cfg or {})}
    decisions: list[str] = []
    status = state.setdefault("status", {})
    rules = (score or {}).get("rules", {})
    cap = cfg["reference_capital"]
    perf = {}
    for bk in state.get("books", {}).values():
        if bk["capital"] != cap:
            continue
        name = bk["spec"]
        st = book_stats(bk)
        perf[name] = st
        row = rules.get(name)
        verdict = sprt_status(bk["history"], min(row["post"]["sharpe"], cfg["sharpe_cap"]), row["post_daily_vol"]) if row else "continue"
        prev = status.get(name, {}).get("state", "paper")
        new = prev
        if prev != "suspended":
            if verdict == "rejected":
                new, why = "suspended", "le test séquentiel rejette l'avantage du backtest"
            elif st["max_dd_pct"] > cfg["max_dd_pct"]:
                new, why = "suspended", f"baisse de {st['max_dd_pct']} % en paper trading (limite {cfg['max_dd_pct']} %)"
            if new != prev:
                decisions.append(f"{today} — SUSPENSION de {name} : {why}")
        status[name] = {"state": new, "sprt": verdict, "gate": bool(row["gate"]) if row else None}

    if not rules:
        decisions.append(f"{today} — pas encore de fiche de score : aucun champion désigné")
        return decisions
    eligible = [n for n, s in status.items() if s["state"] != "suspended" and s["gate"]]
    champ = state.get("champion")
    if champ and (champ["name"] not in eligible):
        decisions.append(f"{today} — le champion {champ['name']} n'est plus éligible (suspendu ou porte perdue)")
        champ = None
    seasoned = [n for n in eligible if perf.get(n, {}).get("days", 0) >= cfg["min_days"] and perf[n]["sharpe"] is not None]
    if not eligible:
        if state.get("champion"):
            decisions.append(f"{today} — plus aucune règle éligible : pas de champion")
        state["champion"] = None
        return decisions
    if not seasoned:
        best = max(eligible, key=lambda n: rules[n]["post_sharpe_ci95"][0])
        if not champ or (champ.get("provisional") and champ["name"] != best):
            state["champion"] = {"name": best, "since": today, "provisional": True}
            decisions.append(f"{today} — champion PROVISOIRE : {best} (meilleure borne basse de Sharpe au backtest, "
                             f"en attendant {cfg['min_days']} jours de paper trading)")
        return decisions
    best = max(seasoned, key=lambda n: perf[n]["sharpe"])
    if not champ or champ.get("provisional"):
        state["champion"] = {"name": best, "since": today, "provisional": False}
        decisions.append(f"{today} — champion : {best} (Sharpe paper {perf[best]['sharpe']} sur {perf[best]['days']} jours)")
    elif best != champ["name"]:
        cur = perf.get(champ["name"], {}).get("sharpe")
        days_since = _days_between(champ["since"], today)
        if cur is not None and perf[best]["sharpe"] > cur + cfg["margin"] and days_since >= cfg["min_days"]:
            state["champion"] = {"name": best, "since": today, "provisional": False}
            decisions.append(f"{today} — NOUVEAU champion : {best} (Sharpe paper {perf[best]['sharpe']}) remplace "
                             f"{champ['name']} ({cur})")
    return decisions


def _days_between(a: str, b: str) -> int:
    from datetime import date
    return (date.fromisoformat(b) - date.fromisoformat(a)).days
