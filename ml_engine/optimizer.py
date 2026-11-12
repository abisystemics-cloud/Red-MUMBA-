"""Recherche d'hyperparamètres sous contraintes (walk-forward + garde-fous).

Règles qui empêchent l'agent R&D de "sur-optimiser" en production :
1. Les paramètres candidats restent dans `research.bounds`.
2. Chaque paramètre ne bouge pas de plus de `max_param_change_pct` par mise à jour.
3. L'in-sample est découpé en `folds` périodes consécutives : un candidat est
   noté sur sa PIRE période (il doit tenir dans tous les régimes, pas dans un seul).
4. La décision se prend sur une période hors échantillon jamais vue.
5. Rejet si : max drawdown OOS ≥ `max_drawdown_pct` ; candidat non rentable OOS ;
   moins de `min_oos_trades` trades OOS ; amélioration du Sharpe OOS inférieure à
   `min_sharpe_improvement` × √ln(n_trials) (plus on essaie de combinaisons, plus
   il est facile d'en trouver une bonne par hasard : la marge exigée augmente).
"""
from __future__ import annotations

import copy
import logging
import math
import random
from dataclasses import dataclass, field
from typing import Any

from core.config import ExecutionCfg, StrategyCfg
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


def _folds(records: list[dict], k: int) -> list[list[dict]]:
    k = max(1, k)
    n = len(records)
    return [records[i * n // k:(i + 1) * n // k] for i in range(k)]


def required_margin(research_cfg) -> float:
    return research_cfg.min_sharpe_improvement * math.sqrt(math.log(max(2, research_cfg.n_trials)))


def optimize(records: list[dict], current_strategy: StrategyCfg, risk_cfg, research_cfg,
             seed: int | None = None, equity: float = 10_000.0,
             exec_cfg: ExecutionCfg | None = None) -> OptimizationReport:
    if len(records) < 1000:
        return OptimizationReport(False, f"not enough data ({len(records)} events)", {})
    cut = int(len(records) * (1 - research_cfg.oos_fraction))
    is_folds, oos_data = _folds(records[:cut], research_cfg.folds), records[cut:]
    cur = current_strategy.model_dump()
    rng = random.Random(seed)
    bt = lambda data, cfg: run_backtest(data, cfg, risk_cfg, equity=equity, exec_cfg=exec_cfg)  # noqa: E731

    cur_oos = bt(oos_data, current_strategy)
    best_params, best_is = None, -1e18
    history = []
    for i in range(research_cfg.n_trials):
        params = propose(cur, research_cfg.bounds, research_cfg.max_param_change_pct, rng)
        cfg = StrategyCfg.model_validate(params)
        fold_scores = [objective(bt(fd, cfg), research_cfg.max_drawdown_pct) for fd in is_folds]
        score = min(fold_scores)  # robustesse : la pire période fait foi
        history.append({"trial": i, "fold_scores": [round(x, 3) for x in fold_scores], "score": round(score, 4)})
        if score > best_is:
            best_is, best_params = score, params

    if best_params is None or best_is <= -1e9:
        return OptimizationReport(False, "no candidate survives every in-sample period", cur_oos.summary(),
                                  trials=research_cfg.n_trials, history=history)
    best_oos = bt(oos_data, StrategyCfg.model_validate(best_params))
    rep = OptimizationReport(False, "", cur_oos.summary(), best_oos.summary(), best_params,
                             research_cfg.n_trials, history)
    margin = required_margin(research_cfg)
    if best_oos.max_drawdown_pct >= research_cfg.max_drawdown_pct:
        rep.reason = f"OOS max drawdown {best_oos.max_drawdown_pct:.2f}% >= {research_cfg.max_drawdown_pct}%"
    elif best_oos.total_return_pct <= 0 or best_oos.sharpe <= 0:
        rep.reason = (f"candidate not profitable out-of-sample (return {best_oos.total_return_pct:.3f}%, "
                      f"sharpe {best_oos.sharpe:.2f})")
    elif best_oos.n_trades < research_cfg.min_oos_trades:
        rep.reason = f"OOS trades {best_oos.n_trades} < {research_cfg.min_oos_trades}"
    elif best_oos.sharpe - max(cur_oos.sharpe, 0.0) < margin:
        rep.reason = (f"OOS sharpe gain {best_oos.sharpe - max(cur_oos.sharpe, 0.0):.2f} "
                      f"< required margin {margin:.2f} for {research_cfg.n_trials} trials")
    else:
        rep.accepted, rep.reason = True, "validated on every in-sample period and out-of-sample"
    log.info("optimization: accepted=%s reason=%s cur=%s best=%s",
             rep.accepted, rep.reason, rep.current_oos, rep.best_oos)
    return rep
