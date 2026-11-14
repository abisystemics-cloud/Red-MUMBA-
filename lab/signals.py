"""Bibliothèque de signaux : la « nourriture » du laboratoire.

Chaque signal est un tableau jours × marchés calculé sur les seules données ≤ clôture du
jour (aucun regard vers l'avenir). Plus la valeur est haute, plus le signal « dit
hausse » ; les règles peuvent le prendre à l'endroit ou à l'envers (paramètre de signe).

Prix et tendance : mom (rendement sur L jours), riskmom (rendement / volatilité),
  brk (place de la clôture dans le couloir plus-haut/plus-bas de L jours — cassures),
  z (écart à la moyenne en nombre d'écarts-types — bandes de Bollinger).
Livres (Trader Dale, Wyckoff) : vwapd (écart de la clôture au VWAP de L jours),
  vsurge (volume du jour / volume moyen), spring (faux cassage du bas refermé au-dessus
  = +1 ; faux cassage du haut refermé en dessous = −1 ; mémoire de 3 jours).
Risque : vol (volatilité), maxret (plus forte hausse d'un jour — effet loterie),
  illiq (mouvement de prix par dollar échangé).
Financement : carry (funding bas = bon), fchg (funding en hausse).
"""
from __future__ import annotations

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from scripts.quant_research import carry_signal, mom_signal

DAY_MS = 86_400_000
LB = (2, 3, 5, 7, 10, 14, 21, 28, 42)
SIGS = ("mom", "riskmom", "brk", "z", "vwapd", "vsurge", "spring", "vol", "maxret", "illiq", "carry", "fchg")
TS_SIGS = ("mom", "riskmom", "brk", "z", "vwapd", "spring", "carry", "fchg")   # signaux qui ont un zéro naturel


def daily_hlv(raw: dict, coins: list[str], days: np.ndarray):
    """Plus-haut, plus-bas et volume en dollars par jour, alignés sur le panel historique."""
    from scripts.bar_research import resample
    T, N, t0 = len(days), len(coins), days[0]
    H, L, V = (np.full((T, N), np.nan) for _ in range(3))
    for j, c in enumerate(coins):
        d = resample(raw[c]["1h"], DAY_MS)
        idx = ((d.ts - t0) // DAY_MS).astype(int)
        ok = (idx >= 0) & (idx < T)
        H[idx[ok], j], L[idx[ok], j], V[idx[ok], j] = d.h[ok], d.l[ok], (d.v * d.c)[ok]
    return H, L, V


def _roll(x: np.ndarray, n: int, fn) -> np.ndarray:
    out = np.full(x.shape, np.nan)
    if len(x) >= n:
        out[n - 1:] = fn(sliding_window_view(x, n, axis=0), axis=-1)
    return out


def _lag(x: np.ndarray) -> np.ndarray:
    out = np.full(x.shape, np.nan)
    out[1:] = x[:-1]
    return out


def _div(a, b):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(np.isfinite(b) & (b != 0), a / b, np.nan)


def compute(panel: dict, name: str, n: int) -> np.ndarray:
    C, F, R = panel["C"], panel["F"], panel["R"]
    H, L = panel.get("H", C), panel.get("L", C)
    V = panel.get("V", np.where(np.isfinite(C), 1.0, np.nan))
    if name == "mom":
        return mom_signal(C, n)
    if name == "carry":
        return carry_signal(C, F, n)
    if name == "vol":
        return _roll(R, n, np.std)
    if name == "riskmom":
        return _div(mom_signal(C, n), _roll(R, max(n, 5), np.std))
    if name == "brk":
        lo = _roll(L, n, np.min)
        return _div(C - lo, _roll(H, n, np.max) - lo) - 0.5
    if name == "z":
        return _div(C - _roll(C, n, np.mean), _roll(C, max(n, 3), np.std))
    if name == "vwapd":
        return _div(C, _div(_roll((H + L + C) / 3 * V, n, np.sum), _roll(V, n, np.sum))) - 1
    if name == "vsurge":
        return np.log(_div(V, _roll(V, n, np.mean)))
    if name == "maxret":
        return _roll(R, n, np.max)
    if name == "illiq":
        return np.log(_roll(_div(np.abs(R), V), n, np.mean))
    if name == "fchg":
        return -(carry_signal(C, F, n) - np.vstack([np.full((n, C.shape[1]), np.nan), carry_signal(C, F, n)[:-n]]))
    if name == "spring":
        pl, ph = _lag(_roll(L, n, np.min)), _lag(_roll(H, n, np.max))
        ev = np.where((L < pl) & (C > pl), 1.0, 0.0) - np.where((H > ph) & (C < ph), 1.0, 0.0)
        ev = np.where(np.isfinite(pl) & np.isfinite(C), ev, np.nan)
        return _roll(ev, 3, np.sum)
    raise ValueError(f"signal inconnu : {name}")


def get(panel: dict, name: str, n: int) -> np.ndarray:
    cache = panel.setdefault("_sig", {})
    key = (name, int(n))
    if key not in cache:
        cache[key] = compute(panel, name, int(n))
    return cache[key]


def rank(panel: dict, name: str, n: int) -> np.ndarray:
    """Rang du jour centré sur 0 (−0,5 … +0,5), ex æquo au même rang (important pour `spring`)."""
    cache = panel.setdefault("_rank", {})
    key = (name, int(n))
    if key not in cache:
        x = get(panel, name, n)
        out = np.full(x.shape, np.nan)
        for t in range(x.shape[0]):
            ok = np.flatnonzero(np.isfinite(x[t]))
            if len(ok) > 1:
                _, inv, cnt = np.unique(x[t, ok], return_inverse=True, return_counts=True)
                first = np.cumsum(cnt) - cnt
                out[t, ok] = (first + (cnt - 1) / 2)[inv] / (len(ok) - 1) - 0.5
        cache[key] = out
    return cache[key]
