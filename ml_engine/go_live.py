"""Critères de passage en réel, fixés AVANT de voir les résultats (`go_live`).

Le rapport est vert seulement si TOUS les critères le sont :
- assez de trades pour que le résultat ne soit pas du hasard ;
- profit factor (gains / pertes) au-dessus du seuil, frais inclus ;
- max drawdown sous le plafond ;
- régularité : au moins N semaines positives sur les M dernières.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Iterable

WEEK_MS = 7 * 86_400_000


def _ts_ms(ts) -> int:
    if isinstance(ts, (int, float)):
        return int(ts)
    return int(datetime.fromisoformat(str(ts).replace("Z", "+00:00")).timestamp() * 1000)


def evaluate(trades: Iterable[tuple], start_equity: float, cfg) -> dict:
    """trades : itérable de (timestamp, pnl_usd). Retourne le rapport complet."""
    rows = sorted(((_ts_ms(t), float(p or 0)) for t, p in trades), key=lambda r: r[0])
    pnls = [p for _, p in rows]
    gains = sum(p for p in pnls if p > 0)
    losses = -sum(p for p in pnls if p < 0)
    pf = gains / losses if losses > 0 else (math.inf if gains > 0 else 0.0)

    eq, peak, mdd = start_equity, start_equity, 0.0
    for p in pnls:
        eq += p
        peak = max(peak, eq)
        mdd = max(mdd, (peak - eq) / peak * 100 if peak > 0 else 0.0)

    weeks: list[float] = []
    if rows:
        end = rows[-1][0]
        for w in range(cfg.weeks):
            hi, lo = end - w * WEEK_MS, end - (w + 1) * WEEK_MS
            weeks.append(sum(p for t, p in rows if lo < t <= hi))
    positive_weeks = sum(1 for w in weeks if w > 0)

    criteria = {
        "trades": {"value": len(rows), "target": f">= {cfg.min_trades}", "pass": len(rows) >= cfg.min_trades},
        "profit_factor": {"value": round(pf, 3) if math.isfinite(pf) else "inf",
                          "target": f">= {cfg.min_profit_factor}", "pass": pf >= cfg.min_profit_factor},
        "max_drawdown_pct": {"value": round(mdd, 3), "target": f"<= {cfg.max_drawdown_pct}",
                             "pass": mdd <= cfg.max_drawdown_pct},
        "positive_weeks": {"value": f"{positive_weeks}/{cfg.weeks}",
                           "target": f">= {cfg.min_positive_weeks}/{cfg.weeks}",
                           "pass": positive_weeks >= cfg.min_positive_weeks},
    }
    go = all(c["pass"] for c in criteria.values())
    return {"go": go, "verdict": "GO" if go else "NO-GO", "criteria": criteria,
            "pnl_total": round(sum(pnls), 2), "weekly_pnl": [round(w, 2) for w in weeks]}


def format_report(rep: dict) -> str:
    lines = [f"Rapport go/no-go : {rep['verdict']}  (PnL total {rep['pnl_total']} USD)"]
    for name, c in rep["criteria"].items():
        lines.append(f"  {'OK ' if c['pass'] else 'KO '} {name}: {c['value']} (cible {c['target']})")
    return "\n".join(lines)
