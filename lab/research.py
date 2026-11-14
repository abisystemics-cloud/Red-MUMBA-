"""Recherche automatique : la fiche de score de TOUT le catalogue sur l'historique long.

Chaque règle reçoit les mêmes mesures ; une règle n'entre en paper trading comme
challenger sérieux que si elle passe la « porte » :
- Sharpe positif avant 2024 ET borne basse de l'intervalle de confiance > 0 depuis 2024 ;
- rendement positif depuis 2024 avec des coûts doublés.
Le Sharpe déflaté tient compte du nombre de règles du catalogue (plus on en essaie,
plus la barre monte).
"""
from __future__ import annotations

import math

import numpy as np

from lab.catalog import Spec, weights
from ml_engine.stats import deflated_sharpe, moments, sharpe_ci
from scripts.quant_research import backtest, stats


def scorecard(panel: dict, catalog: list[Spec], cost: float, split_ms: float, clean_ms: float, extra_trials: int = 0,
              var_trials: float | None = None) -> dict:
    """`extra_trials` = règles déjà essayées puis écartées par lab/evolve.py : elles comptent dans le Sharpe déflaté."""
    days, R, F = np.asarray(panel["days"]), panel["R"], panel["F"]
    pre, post, clean = days < split_ms, days >= split_ms, days >= clean_ms
    rows, series = {}, {}
    for s in catalog:
        W = weights(panel, s)
        pnl, turn, chg = backtest(W, R, F, cost)
        pnl2, _, _ = backtest(W, R, F, 2 * cost)
        series[s.name] = pnl
        lo, hi = sharpe_ci(pnl[post], n_paths=1000)
        rows[s.name] = {"family": s.family, "params": dict(s.params),
                        "pre": stats(pnl[pre], turn[pre], chg[pre]), "post": stats(pnl[post], turn[post], chg[post]),
                        "clean": stats(pnl[clean], turn[clean], chg[clean]),
                        "post_cost_x2_return_pct": stats(pnl2[post], turn[post], chg[post])["return_pct"],
                        "post_sharpe_ci95": [round(lo, 2), round(hi, 2)],
                        "post_daily_vol": float(pnl[post].std(ddof=1))}
    if var_trials is None:
        var_trials = float(np.var([moments(p[post])[0] for p in series.values()]))
    for name, row in rows.items():
        row["deflated_sharpe"] = round(deflated_sharpe(series[name][post], len(catalog) + extra_trials, var_trials), 3)
        row["gate"] = bool(row["pre"]["sharpe"] > 0 and row["post_sharpe_ci95"][0] > 0 and row["post_cost_x2_return_pct"] > 0)
    return {"n_rules": len(catalog), "rules": rows, "var_trials": var_trials, "sqrt365": math.sqrt(365)}
