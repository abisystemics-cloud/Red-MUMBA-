"""Outils statistiques du « mathématicien » : un Sharpe est-il réel ou dû à la chance ?

- probabilistic_sharpe : probabilité que le vrai Sharpe dépasse un seuil, compte tenu
  de la longueur de l'échantillon, de l'asymétrie et des queues épaisses
  (Bailey & López de Prado, 2012) ;
- expected_max_sharpe : Sharpe maximal attendu PAR PUR HASARD après N essais ;
- deflated_sharpe : probabilité que le vrai Sharpe dépasse ce maximum-là (2014).
  En dessous de ~0,95, on ne peut pas exclure que le résultat vienne de la recherche
  elle-même (on a essayé beaucoup de stratégies et gardé les meilleures).
Tous les Sharpe sont PAR PÉRIODE (non annualisés) dans ces fonctions.
"""
from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np

_N = NormalDist()
EULER = 0.5772156649015329


def moments(r: np.ndarray) -> tuple[float, float, float, int]:
    """→ (Sharpe par période, asymétrie, kurtosis, T)."""
    r = np.asarray(r, dtype=float)
    t = len(r)
    sd = r.std(ddof=1) if t > 1 else 0.0
    if sd <= 0:
        return 0.0, 0.0, 3.0, t
    z = (r - r.mean()) / r.std()
    return float(r.mean() / sd), float((z ** 3).mean()), float((z ** 4).mean()), t


def probabilistic_sharpe(r: np.ndarray, benchmark: float = 0.0) -> float:
    sr, skew, kurt, t = moments(r)
    if t < 3:
        return 0.5
    den = math.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr * sr, 1e-12))
    return _N.cdf((sr - benchmark) * math.sqrt(t - 1) / den)


def expected_max_sharpe(n_trials: int, var_trials: float) -> float:
    if n_trials < 2 or var_trials <= 0:
        return 0.0
    a = _N.inv_cdf(1 - 1 / n_trials)
    b = _N.inv_cdf(1 - 1 / (n_trials * math.e))
    return math.sqrt(var_trials) * ((1 - EULER) * a + EULER * b)


def deflated_sharpe(r: np.ndarray, n_trials: int, var_trials: float) -> float:
    return probabilistic_sharpe(r, expected_max_sharpe(n_trials, var_trials))
