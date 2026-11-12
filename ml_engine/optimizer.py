"""Recherche d'hyperparamètres sous contraintes (walk-forward + garde-fous).

Règles qui empêchent l'agent R&D de "sur-optimiser" en production :
1. Les paramètres candidats restent dans `research.bounds`.
2. Chaque paramètre ne bouge pas de plus de `max_param_change_pct` par mise à jour.
3. Optimisation sur la partie in-sample, DÉCISION sur la partie out-of-sample.
4. Rejet si le max drawdown OOS ≥ `max_drawdown_pct` (10 % par défaut), si le
   candidat n'est pas rentable OOS (rendement et Sharpe > 0), si le nombre de
   trades OOS est trop faible, ou s'il ne bat pas la config actuelle sur l'OOS.
"""
from __future__ import annotations

import copy
import logging
import random
from dataclasses import dataclass, field
from typing import Any

from core.config import StrategyCfg
from ml_engine.backtester import BTResult, run_backtest

log = logging.getLogger("ml.optimizer")


def _get(d: dict, dotted: str) -> Any:
    for k in dotted.split("."):
        d = d[k]
    return d


def _set(d: dict, dotted: str, v: Any) -> None:
    keys = dotted.split(".")
    for k in keys[:-1]:
        d = d[k]
    d[keys[-1]] = v


def propose(current: dict, bounds: dict[str, list[float]], max_change_pct: float,
            rng: random.Random) -> dict:
    cand = copy.deepcopy(current)
    for key, (lo, hi) in bounds.items():
        cur = _get(current, key)
        span = abs(cur) * max_change_pct / 100 if cur else (hi - lo) * max_change_pct / 100
        v = min(hi, max(lo, cur + rng.uniform(-span, span)))
        if isinstance(cur, int) and not isinstance(cur, bool):
            v = int(round(v))
        else:
            v = round(v, 4)
        _set(cand, key, v)
    return cand


def objective(r: BTResult, max_dd: float) -> float:
    if r.max_drawdown_pct >= max_dd or r.n_trades == 0:
        return -1e9
    return r.sharpe - 0.1 * r.max_drawdown_pct


@dataclass
class OptimizationReport:
    accepted: bool
    reason: str
    current_oos: dict
    best_oos: dict | None = None
    best_params: dict | None = None
    trials: int = 0
    history: list[dict] = field(default_factory=list)


def optimize(records: list[dict], current_strategy: StrategyCfg, risk_cfg, research_cfg,
             seed: int | None = None, equity: float = 10_000.0) -> OptimizationReport:
    if len(records) < 1000:
        return OptimizationReport(False, f"not enough data ({len(records)} events)", {})
    cut = int(len(records) * (1 - research_cfg.oos_fraction))
    is_data, oos_data = records[:cut], records[cut:]
    cur = current_strategy.model_dump()
    rng = random.Random(seed)

    cur_oos = run_backtest(oos_data, current_strategy, risk_cfg, equity=equity)
    best_params, best_is = None, -1e18
    history = []
    for i in range(research_cfg.n_trials):
        params = propose(cur, research_cfg.bounds, research_cfg.max_param_change_pct, rng)
        cfg = StrategyCfg.model_validate(params)
        r = run_backtest(is_data, cfg, risk_cfg, equity=equity)
        score = objective(r, research_cfg.max_drawdown_pct)
        history.append({"trial": i, "is": r.summary(), "score": round(score, 4)})
        if score > best_is:
            best_is, best_params = score, params

    if best_params is None:
        return OptimizationReport(False, "no candidate", cur_oos.summary(), trials=research_cfg.n_trials)
    best_oos = run_backtest(oos_data, StrategyCfg.model_validate(best_params), risk_cfg, equity=equity)
    rep = OptimizationReport(False, "", cur_oos.summary(), best_oos.summary(), best_params,
                             research_cfg.n_trials, history)
    min_trades = max(5, research_cfg.min_trades_for_eval // 2)
    if best_oos.max_drawdown_pct >= research_cfg.max_drawdown_pct:
        rep.reason = f"OOS max drawdown {best_oos.max_drawdown_pct:.2f}% >= {research_cfg.max_drawdown_pct}%"
    elif best_oos.total_return_pct <= 0 or best_oos.sharpe <= 0:
        rep.reason = (f"candidate not profitable out-of-sample (return {best_oos.total_return_pct:.3f}%, "
                      f"sharpe {best_oos.sharpe:.2f})")
    elif best_oos.n_trades < min_trades:
        rep.reason = f"OOS trades {best_oos.n_trades} < {min_trades}"
    elif objective(best_oos, research_cfg.max_drawdown_pct) <= objective(cur_oos, research_cfg.max_drawdown_pct):
        rep.reason = "candidate does not beat current config out-of-sample"
    else:
        rep.accepted, rep.reason = True, "validated out-of-sample"
    log.info("optimization: accepted=%s reason=%s cur=%s best=%s",
             rep.accepted, rep.reason, rep.current_oos, rep.best_oos)
    return rep
