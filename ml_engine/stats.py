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


# ----------------------------------------------------------- incertitude
def stationary_bootstrap(r: np.ndarray, n_paths: int, length: int | None = None, mean_block: int = 10,
                         seed: int = 0) -> np.ndarray:
    """Bootstrap stationnaire (Politis & Romano) : rééchantillonne des blocs de longueur
    géométrique pour conserver l'autocorrélation et les grappes de volatilité."""
    r = np.asarray(r, dtype=float)
    n = len(r)
    length = length or n
    rng = np.random.default_rng(seed)
    idx = np.empty((n_paths, length), dtype=np.int64)
    idx[:, 0] = rng.integers(0, n, n_paths)
    jump = rng.random((n_paths, length)) < 1 / mean_block
    fresh = rng.integers(0, n, (n_paths, length))
    for t in range(1, length):
        idx[:, t] = np.where(jump[:, t], fresh[:, t], (idx[:, t - 1] + 1) % n)
    return r[idx]


def sharpe_ci(r: np.ndarray, periods: int = 365, n_paths: int = 2000, level: float = 0.95) -> tuple[float, float]:
    paths = stationary_bootstrap(r, n_paths)
    sd = paths.std(axis=1, ddof=1)
    s = np.where(sd > 0, paths.mean(axis=1) / sd, 0.0) * math.sqrt(periods)
    lo, hi = np.quantile(s, [(1 - level) / 2, 1 - (1 - level) / 2])
    return float(lo), float(hi)


def ruin_stats(r: np.ndarray, horizon: int, leverage: float = 1.0, dd_limit: float = 0.5, n_paths: int = 5000,
               seed: int = 1) -> dict:
    """Sur `horizon` jours rejoués par bootstrap : probabilité de finir en perte, de subir
    une baisse ≥ dd_limit (assimilée à la ruine d'un petit compte), rendement médian."""
    paths = np.clip(stationary_bootstrap(r, n_paths, horizon, seed=seed) * leverage, -0.999, None)
    eq = np.cumprod(1 + paths, axis=1)
    dd = 1 - eq / np.maximum.accumulate(np.maximum(eq, 1.0), axis=1)
    return {"p_loss": float((eq[:, -1] < 1).mean()), "p_drawdown_over_limit": float((dd.max(axis=1) >= dd_limit).mean()),
            "median_return_pct": float(np.median(eq[:, -1]) - 1) * 100,
            "p5_return_pct": float(np.quantile(eq[:, -1], 0.05) - 1) * 100,
            "p95_return_pct": float(np.quantile(eq[:, -1], 0.95) - 1) * 100}


def kelly_leverage(r: np.ndarray) -> float:
    """Levier de Kelly continu f* = μ / σ² (rendements par période)."""
    r = np.asarray(r, dtype=float)
    v = r.var(ddof=1)
    return float(r.mean() / v) if v > 0 else 0.0


def years_to_confirm(sharpe_annual: float, confidence: float = 0.95) -> float:
    """Durée d'observation pour que le Sharpe attendu soit distinguable de 0 (test unilatéral)."""
    if sharpe_annual <= 0:
        return float("inf")
    return (_N.inv_cdf(confidence) / sharpe_annual) ** 2


class SPRTMonitor:
    """Test séquentiel de Wald sur les rendements journaliers réels :
    H1 = « le bot a le Sharpe du backtest » contre H0 = « il n'a aucun avantage ».
    Dit chaque jour : continuer / avantage confirmé / avantage rejeté, avec des taux
    d'erreur fixés à l'avance (alpha = fausse confirmation, beta = faux rejet)."""

    def __init__(self, sharpe_annual: float, daily_vol: float, alpha: float = 0.05, beta: float = 0.2, periods: int = 365):
        self.mu1 = sharpe_annual / math.sqrt(periods) * daily_vol
        self.var = daily_vol ** 2
        self.upper = math.log((1 - beta) / alpha)
        self.lower = math.log(beta / (1 - alpha))
        self.llr = 0.0
        self.n = 0

    def update(self, r: float) -> str:
        self.llr += (self.mu1 * r - self.mu1 ** 2 / 2) / self.var
        self.n += 1
        if self.llr >= self.upper:
            return "confirmed"
        if self.llr <= self.lower:
            return "rejected"
        return "continue"
