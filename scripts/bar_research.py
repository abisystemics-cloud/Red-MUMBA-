"""Recherche sur bougies : stratégies lentes (heures → jours), testées sur des années.

    python scripts/bar_research.py --coins BTC,ETH,SOL --from 2020-01 --to 2026-10 --split 2023-12

Pourquoi : le backtest tick-à-tick (microstructure, minutes) n'a aucun avantage
au-dessus des frais. Ici on teste des familles de stratégies à horizon plus long,
où les frais pèsent peu, sur ~7 ans de bougies Binance USDⓈ-M gratuites
(data.binance.vision) au lieu de 10 semaines.

Familles (règles mécaniques tirées des livres fournis + littérature) :
- vwap_rotation : VWAP hebdo ancré + bandes σ (Trader Dale, « VWAP Rotation ») —
  marché latéral (bandes plates), on achète la bande basse / vend la haute, TP au VWAP ;
- vwap_trend    : même VWAP, bandes en pente (« VWAP Trend ») — achat du repli sur
  la 1re bande dans le sens de la tendance, sortie à la clôture de l'autre côté du VWAP ;
- spring        : Wyckoff spring / upthrust — fausse cassure d'un range sur volume
  élevé avec réintégration dans la même bougie (absorption), cible milieu/haut du range ;
- tsmom         : momentum temporel 6 h (littérature académique), long/short ou long seul ;
- funding       : funding Binance extrême (z-score 30 j) pris à contre-sens.

Exécution : signal à la clôture d'une bougie, ordre à l'ouverture de la suivante
(pas de regard vers le futur) ; stop/TP vérifiés sur le haut/bas des bougies
suivantes, le stop est supposé touché en premier si les deux le sont. Coûts :
frais taker Hyperliquid + glissement à chaque côté, funding payé/reçu. Taille :
risque fixe par trade (perte au stop = risk_pct), levier plafonné.

Règle de décision fixée À L'AVANCE (par famille) : réglage au meilleur Sharpe sur
l'apprentissage parmi ceux avec ≥ min_trades trades ; la famille « TIENT » si, sur la
vérification jamais vue : Sharpe ≥ 0.8, profit factor ≥ 1.2, rendement > 0, drawdown
< 25 %, et rendement toujours > 0 avec des coûts doublés.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

import numpy as np

BASE = "https://data.binance.vision/data/futures/um/monthly"
SYMBOLS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT", "SOL": "SOLUSDT"}
H = 3_600_000


# ------------------------------------------------------------------ données
def months(start: str, end: str) -> list[str]:
    y, m = map(int, start.split("-"))
    ye, me = map(int, end.split("-"))
    out = []
    while (y, m) <= (ye, me):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def _get(url: str, cache: Path) -> Optional[bytes]:
    if cache.exists():
        return cache.read_bytes() or None
    cache.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            cache.write_bytes(data)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                cache.write_bytes(b"")
                return None
            time.sleep(2 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 * (attempt + 1))
    return None


def _rows(raw: bytes):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        text = z.read(z.namelist()[0]).decode()
    for row in csv.reader(io.StringIO(text)):
        if row and row[0][:1].isdigit():
            yield row


def _ms(v: str) -> int:
    t = int(float(v))
    return t // 1000 if t > 10 ** 14 else t  # µs → ms si besoin


@dataclass
class Bars:
    ts: np.ndarray   # ouverture (ms)
    o: np.ndarray
    h: np.ndarray
    l: np.ndarray  # noqa: E741
    c: np.ndarray
    v: np.ndarray
    tbv: np.ndarray  # volume acheteur agresseur

    def __len__(self) -> int:
        return len(self.ts)


def load_klines(sym: str, mlist: list[str], cache_dir: Path, interval: str = "15m") -> Bars:
    cols = [[] for _ in range(7)]
    for mo in mlist:
        raw = _get(f"{BASE}/klines/{sym}/{interval}/{sym}-{interval}-{mo}.zip",
                   cache_dir / "klines" / sym / f"{interval}-{mo}.zip")
        if not raw:
            continue
        for r in _rows(raw):
            vals = (_ms(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9]))
            for k, x in enumerate(vals):
                cols[k].append(x)
    a = [np.asarray(x, dtype=np.float64) for x in cols]
    order = np.argsort(a[0], kind="stable")
    a = [x[order] for x in a]
    keep = np.concatenate([[True], np.diff(a[0]) > 0]) if len(a[0]) else np.zeros(0, bool)
    return Bars(*[x[keep] for x in a])


def load_funding(sym: str, mlist: list[str], cache_dir: Path) -> tuple[np.ndarray, np.ndarray]:
    ts, rate = [], []
    for mo in mlist:
        raw = _get(f"{BASE}/fundingRate/{sym}/{sym}-fundingRate-{mo}.zip",
                   cache_dir / "funding" / sym / f"{mo}.zip")
        if not raw:
            continue
        for r in _rows(raw):
            try:
                ts.append(_ms(r[0]))
                rate.append(float(r[-1]))
            except (ValueError, IndexError):
                continue
    t, f = np.asarray(ts, dtype=np.float64), np.asarray(rate, dtype=np.float64)
    o = np.argsort(t)
    return t[o], f[o]


def resample(b: Bars, period_ms: int) -> Bars:
    g = (b.ts // period_ms).astype(np.int64)
    starts = np.flatnonzero(np.concatenate([[True], g[1:] != g[:-1]]))
    ends = np.concatenate([starts[1:], [len(g)]]) - 1
    return Bars(g[starts].astype(np.float64) * period_ms, b.o[starts],
                np.maximum.reduceat(b.h, starts), np.minimum.reduceat(b.l, starts), b.c[ends],
                np.add.reduceat(b.v, starts), np.add.reduceat(b.tbv, starts))


# ---------------------------------------------------------------- indicateurs
def atr(b: Bars, n: int = 14) -> np.ndarray:
    pc = np.concatenate([[b.c[0]], b.c[:-1]])
    tr = np.maximum(b.h - b.l, np.maximum(abs(b.h - pc), abs(b.l - pc)))
    out = np.full(len(tr), np.nan)
    if len(tr) > n:
        out[n - 1] = tr[:n].mean()
        for i in range(n, len(tr)):
            out[i] = out[i - 1] + (tr[i] - out[i - 1]) / n
    return out


def weekly_vwap(b: Bars) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """VWAP ancré au lundi 00:00 UTC + écart-type pondéré par le volume (bandes de Dale)."""
    week = ((b.ts // H + 72) // 168).astype(np.int64)  # epoch = jeudi → décalage de 72 h vers lundi
    tp = (b.h + b.l + b.c) / 3
    vwap, sd, since = np.empty(len(b)), np.empty(len(b)), np.empty(len(b))
    pv = pv2 = vv = 0.0
    k = 0
    for i in range(len(b)):
        if i == 0 or week[i] != week[i - 1]:
            pv = pv2 = vv = 0.0
            k = 0
        pv += tp[i] * b.v[i]
        pv2 += tp[i] * tp[i] * b.v[i]
        vv += b.v[i]
        k += 1
        m = pv / vv if vv > 0 else tp[i]
        vwap[i] = m
        sd[i] = math.sqrt(max(pv2 / vv - m * m, 0.0)) if vv > 0 else 0.0
        since[i] = k
    return vwap, sd, since


def rolling_max(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].max()
    return out


def rolling_min(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = x[i - n:i].min()
    return out


def rolling_median(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = np.median(x[i - n:i])
    return out


# -------------------------------------------------------------------- moteur
@dataclass
class Entry:
    side: int                    # +1 long, -1 short
    stop: float
    target: Optional[float] = None
    max_bars: int = 10 ** 9


@dataclass
class Strategy:
    """`entry(i)` → Entry ou None ; `exit(i, side, entry_i)` → True pour sortir à l'ouverture suivante."""
    entry: Callable[[int], Optional[Entry]]
    exit: Callable[[int, int, int], bool] = lambda i, s, e: False
    warmup: int = 200


@dataclass
class Costs:
    fee_bps: float = 4.5      # taker Hyperliquid
    slip_bps: float = 2.0
    mult: float = 1.0
    maker_fee_bps: float = 1.5  # ordre posté (ALO) Hyperliquid, sans glissement

    @property
    def maker_side(self) -> float:
        return self.maker_fee_bps * self.mult / 1e4

    @property
    def side(self) -> float:
        return (self.fee_bps + self.slip_bps) * self.mult / 1e4


def simulate(b: Bars, strat: Strategy, costs: Costs, fund_t: np.ndarray, fund_r: np.ndarray, *,
             risk_pct: float = 0.5, max_lev: float = 3.0, start_ms: float = -1, end_ms: float = 1e18,
             entry_mode: str = "taker") -> dict:
    """Une position à la fois. Equity en multiplicatif, valorisée à chaque clôture.

    entry_mode :
    - taker       : entrée au marché à l'ouverture de la bougie suivante ;
    - maker_skip  : ordre posté au prix de clôture du signal, exécuté seulement si la
                    bougie suivante TRAVERSE ce prix (hypothèse pessimiste) ; sinon abandonné
                    (le signal peut se représenter à la clôture suivante) ;
    - maker_taker : idem, mais après un échec le prochain signal entre au marché.
    Les sorties (signal, stop) restent au marché."""
    n = len(b)
    eq = 1.0
    curve_t, curve_e, trades = [], [], []
    pos = None   # dict(side, px, stop, target, lev, i0, max_bars, eq0)
    pending: Optional[tuple] = None
    fi = int(np.searchsorted(fund_t, b.ts[0])) if len(fund_t) else 0
    cs = costs.side
    cm = costs.maker_side
    force_taker = False
    attempts = fills = 0

    def close(px: float, i: int, why: str):
        nonlocal eq, pos
        g = pos["side"] * (px / pos["px"] - 1)
        r = pos["lev"] * (g - cs)
        eq *= (1 + r)
        tr_eq = eq / pos["eq0"] - 1
        trades.append({"i0": pos["i0"], "i1": i, "side": pos["side"], "ret": tr_eq, "why": why,
                       "bars": i - pos["i0"]})
        pos = None

    for i in range(strat.warmup, n):
        in_window = start_ms <= b.ts[i] < end_ms
        # 1) exécution de l'ordre décidé à la clôture précédente
        if pending is not None:
            kind, arg = pending
            pending = None
            if kind == "exit" and pos is not None:
                close(b.o[i], i, "signal")
            elif kind == "entry" and pos is None and in_window:
                e: Entry = arg
                px, ce, ok = b.o[i], cs, True
                if entry_mode != "taker" and not force_taker:
                    limit = b.c[i - 1]
                    attempts += 1
                    ok = (b.l[i] < limit) if e.side > 0 else (b.h[i] > limit)
                    if ok:
                        px, ce = limit, cm
                        fills += 1
                    elif entry_mode == "maker_taker":
                        force_taker = True
                else:
                    force_taker = False
                stop_pct = abs(px - e.stop) / px
                if ok and stop_pct > 1e-4 and (px - e.stop) * e.side > 0:
                    lev = min(max_lev, risk_pct / 100 / stop_pct)
                    eq *= (1 - lev * ce)
                    pos = {"side": e.side, "px": px, "stop": e.stop, "target": e.target, "lev": lev,
                           "i0": i, "max_bars": e.max_bars, "eq0": eq / (1 - lev * ce)}
        # 2) stop / objectif dans la bougie i (stop prioritaire, gap → ouverture)
        if pos is not None:
            s, st, tg = pos["side"], pos["stop"], pos["target"]
            if (s > 0 and b.l[i] <= st) or (s < 0 and b.h[i] >= st):
                px = b.o[i] if (s > 0 and b.o[i] < st) or (s < 0 and b.o[i] > st) else st
                close(px, i, "stop")
            elif tg is not None and ((s > 0 and b.h[i] >= tg) or (s < 0 and b.l[i] <= tg)):
                px = b.o[i] if (s > 0 and b.o[i] > tg) or (s < 0 and b.o[i] < tg) else tg
                close(px, i, "target")
        # 3) funding échu pendant la bougie (long paie si taux > 0)
        t_close = b.ts[i + 1] if i + 1 < n else b.ts[i] + (b.ts[i] - b.ts[i - 1])
        while fi < len(fund_t) and fund_t[fi] < t_close:
            if pos is not None and fund_t[fi] >= b.ts[pos["i0"]]:
                eq *= (1 - pos["side"] * fund_r[fi] * pos["lev"])
            fi += 1
        # 4) décisions à la clôture
        if pos is not None:
            if i - pos["i0"] + 1 >= pos["max_bars"] or strat.exit(i, pos["side"], pos["i0"]) or not in_window:
                pending = ("exit", None)
        elif in_window and i + 1 < n:
            e = strat.entry(i)
            if e is not None:
                pending = ("entry", e)
        # valorisation
        if in_window:
            m = eq
            if pos is not None:
                m = eq * (1 + pos["lev"] * pos["side"] * (b.c[i] / pos["px"] - 1))
            curve_t.append(b.ts[i])
            curve_e.append(m)
    if pos is not None:
        close(b.c[-1], n - 1, "end")
        if curve_e:
            curve_e[-1] = eq
    return {"t": np.asarray(curve_t), "e": np.asarray(curve_e), "trades": trades,
            "maker_attempts": attempts, "maker_fills": fills}


def daily_returns(t: np.ndarray, e: np.ndarray) -> dict[int, float]:
    if len(t) == 0:
        return {}
    day = (t // 86_400_000).astype(np.int64)
    last = np.flatnonzero(np.concatenate([day[1:] != day[:-1], [True]]))
    de = e[last]
    prev = np.concatenate([[1.0 if len(de) else 0.0], de[:-1]])
    prev[0] = e[0] if e[0] > 0 else 1.0
    return dict(zip(day[last].tolist(), (de / prev - 1).tolist(), strict=True))


def summarize(per_coin: dict[str, dict]) -> dict:
    """Portefeuille équipondéré des marchés (moyenne des rendements journaliers)."""
    days: dict[int, list[float]] = {}
    trades = []
    for res in per_coin.values():
        for d, r in daily_returns(res["t"], res["e"]).items():
            days.setdefault(d, []).append(r)
        trades += res["trades"]
    if not days:
        return {"trades": 0, "return_pct": 0.0, "max_dd_pct": 0.0, "sharpe": 0.0, "profit_factor": 0.0,
                "win_rate": 0.0, "avg_bars": 0.0}
    ks = sorted(days)
    r = np.asarray([np.mean(days[k]) for k in ks])
    eq = np.cumprod(1 + r)
    dd = 1 - eq / np.maximum.accumulate(eq)
    sd = r.std(ddof=1) if len(r) > 1 else 0.0
    wins = [t["ret"] for t in trades if t["ret"] > 0]
    losses = [-t["ret"] for t in trades if t["ret"] < 0]
    years = len(r) / 365
    return {"trades": len(trades), "return_pct": round((eq[-1] - 1) * 100, 2),
            "cagr_pct": round((eq[-1] ** (1 / years) - 1) * 100, 2) if years > 0 and eq[-1] > 0 else None,
            "max_dd_pct": round(float(dd.max()) * 100, 2),
            "sharpe": round(float(r.mean() / sd * math.sqrt(365)), 2) if sd > 0 else 0.0,
            "profit_factor": round(sum(wins) / sum(losses), 2) if losses else (99.0 if wins else 0.0),
            "win_rate": round(len(wins) / len(trades), 3) if trades else 0.0,
            "avg_bars": round(float(np.mean([t["bars"] for t in trades])), 1) if trades else 0.0}


# ---------------------------------------------------------------- stratégies
def vwap_rotation(b: Bars, k: float, flat: float, lookback: int = 24) -> Strategy:
    """Dale « VWAP Rotation » sur 30 min : bandes plates → achat bande basse k·σ, TP VWAP."""
    vw, sd, since = weekly_vwap(b)
    up1 = vw + sd

    def entry(i: int) -> Optional[Entry]:
        if since[i] < 48 or i < lookback or sd[i] <= 0:
            return None
        slope = (up1[i] - up1[i - lookback]) / sd[i]
        if abs(slope) > flat:
            return None
        lo, hi = vw[i] - k * sd[i], vw[i] + k * sd[i]
        if b.l[i] <= lo < b.c[i] or (b.c[i] <= lo and b.c[i - 1] > vw[i - 1] - k * sd[i - 1]):
            return Entry(+1, vw[i] - (k + 1.5) * sd[i], vw[i], max_bars=96)
        if b.h[i] >= hi > b.c[i] or (b.c[i] >= hi and b.c[i - 1] < vw[i - 1] + k * sd[i - 1]):
            return Entry(-1, vw[i] + (k + 1.5) * sd[i], vw[i], max_bars=96)
        return None

    def exit_(i: int, side: int, i0: int) -> bool:
        return since[i] == 1  # nouvelle semaine : le VWAP est réinitialisé
    return Strategy(entry, exit_, warmup=60)


def vwap_trend(b: Bars, steep: float, stop_sd: float, lookback: int = 24) -> Strategy:
    """Dale « VWAP Trend » : bandes en pente, repli sur la 1re bande → entrée dans le sens."""
    vw, sd, since = weekly_vwap(b)
    up1, lo1 = vw + sd, vw - sd

    def entry(i: int) -> Optional[Entry]:
        if since[i] < 48 or i < lookback or sd[i] <= 0:
            return None
        s_up = (up1[i] - up1[i - lookback]) / sd[i]
        s_lo = (lo1[i] - lo1[i - lookback]) / sd[i]
        if s_up > steep and s_lo > 0 and b.c[i - 1] > up1[i - 1] and b.l[i] <= up1[i] < b.c[i]:
            return Entry(+1, vw[i] - stop_sd * sd[i], None, max_bars=336)
        if s_lo < -steep and s_up < 0 and b.c[i - 1] < lo1[i - 1] and b.h[i] >= lo1[i] > b.c[i]:
            return Entry(-1, vw[i] + stop_sd * sd[i], None, max_bars=336)
        return None

    def exit_(i: int, side: int, i0: int) -> bool:
        return (side > 0 and b.c[i] < vw[i]) or (side < 0 and b.c[i] > vw[i]) or since[i] == 1
    return Strategy(entry, exit_, warmup=60)


def spring(b: Bars, L: int, max_width_atr: float, target: str, vol_mult: float = 1.5) -> Strategy:
    """Wyckoff spring/upthrust sur 1 h : range étroit, mèche sous le bas du range sur
    volume élevé, clôture de retour dans le range dans la moitié haute de la bougie."""
    a = atr(b, 14)
    hi, lo = rolling_max(b.h, L), rolling_min(b.l, L)
    vmed = rolling_median(b.v, L)

    def entry(i: int) -> Optional[Entry]:
        if not (np.isfinite(hi[i]) and np.isfinite(a[i])) or a[i] <= 0:
            return None
        width = hi[i] - lo[i]
        if width <= 0 or width / a[i] > max_width_atr or b.v[i] < vol_mult * vmed[i]:
            return None
        rng = b.h[i] - b.l[i]
        if rng <= 0:
            return None
        pos_in_bar = (b.c[i] - b.l[i]) / rng
        mid = (hi[i] + lo[i]) / 2
        if b.l[i] < lo[i] < b.c[i] and b.c[i] < mid and pos_in_bar >= 0.5:
            return Entry(+1, b.l[i] - 0.1 * a[i], mid if target == "mid" else hi[i], max_bars=3 * L)
        if b.h[i] > hi[i] > b.c[i] and b.c[i] > mid and pos_in_bar <= 0.5:
            return Entry(-1, b.h[i] + 0.1 * a[i], mid if target == "mid" else lo[i], max_bars=3 * L)
        return None
    return Strategy(entry, warmup=L + 20)


def tsmom(b: Bars, L: int, long_only: bool, stop_atr: float = 3.0) -> Strategy:
    """Momentum temporel sur bougies 6 h : signe du rendement sur L bougies ; stop suiveur."""
    a = atr(b, 14)
    sig = np.zeros(len(b))
    sig[L:] = np.sign(b.c[L:] / b.c[:-L] - 1)

    def entry(i: int) -> Optional[Entry]:
        if not np.isfinite(a[i]) or sig[i] == 0 or (long_only and sig[i] < 0):
            return None
        s = int(sig[i])
        return Entry(s, b.c[i] - s * stop_atr * a[i], None)

    def exit_(i: int, side: int, i0: int) -> bool:
        return sig[i] != side
    return Strategy(entry, exit_, warmup=max(L, 20) + 1)


def funding_fade(b: Bars, ft: np.ndarray, fr: np.ndarray, z_thr: float, hold_h: int, window: int = 90) -> Strategy:
    """Funding Binance extrême (z-score sur ~30 j de relevés) pris à contre-sens, bougies 1 h."""
    a = atr(b, 14)
    z = np.full(len(fr), np.nan)
    for j in range(window, len(fr)):
        w = fr[j - window:j]
        s = w.std()
        if s > 0:
            z[j] = (fr[j] - w.mean()) / s
    idx = np.searchsorted(ft, b.ts + H, side="right") - 1  # dernier funding connu à la clôture
    last_used = [-1]

    def entry(i: int) -> Optional[Entry]:
        j = idx[i]
        if j < 0 or j == last_used[0] or not np.isfinite(z[j]) or not np.isfinite(a[i]):
            return None
        if abs(z[j]) < z_thr:
            return None
        last_used[0] = j
        s = -1 if z[j] > 0 else +1
        return Entry(s, b.c[i] - s * 4 * a[i], None, max_bars=hold_h)
    return Strategy(entry, warmup=30)


# ------------------------------------------------------------------- grilles
def families(data: dict) -> dict[str, list[tuple[dict, Callable]]]:
    """Chaque réglage → fonction(coin) qui renvoie (bougies, stratégie)."""
    g: dict[str, list] = {}
    g["vwap_rotation"] = [({"k": k, "flat": f}, (lambda c, k=k, f=f: (data[c]["30m"], vwap_rotation(data[c]["30m"], k, f))))
                          for k in (1.0, 2.0) for f in (0.5, 1.0)]
    g["vwap_trend"] = [({"steep": s, "stop_sd": st}, (lambda c, s=s, st=st: (data[c]["30m"], vwap_trend(data[c]["30m"], s, st))))
                       for s in (0.5, 1.0) for st in (0.25, 1.0)]
    g["spring"] = [({"L": L, "width_atr": w, "target": t},
                    (lambda c, L=L, w=w, t=t: (data[c]["1h"], spring(data[c]["1h"], L, w, t))))
                   for L in (24, 72) for w in (6.0, 12.0) for t in ("mid", "top")]
    g["tsmom"] = [({"L": L, "long_only": lo}, (lambda c, L=L, lo=lo: (data[c]["6h"], tsmom(data[c]["6h"], L, lo))))
                  for L in (4, 12, 28) for lo in (False, True)]
    g["funding"] = [({"z": z, "hold_h": hh},
                     (lambda c, z=z, hh=hh: (data[c]["1h"], funding_fade(data[c]["1h"], *data[c]["fund"], z, hh))))
                    for z in (2.0, 3.0) for hh in (24, 72)]
    return g


def run_config(data, coins, build, start_ms, end_ms, costs: Costs) -> dict:
    per = {}
    for c in coins:
        bars, strat = build(c)
        if len(bars) < 300:
            continue
        per[c] = simulate(bars, strat, costs, *data[c]["fund"], start_ms=start_ms, end_ms=end_ms)
    return summarize(per)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--coins", default="BTC,ETH,SOL")
    p.add_argument("--from", dest="start", default="2020-01")
    p.add_argument("--to", dest="end", default="2026-10")
    p.add_argument("--split", default="2023-12", help="dernier mois de l'apprentissage")
    p.add_argument("--min-trades", type=int, default=40)
    p.add_argument("--cache", default="data/bars")
    p.add_argument("--out", default="data/reports")
    a = p.parse_args()
    t0 = time.time()
    coins = a.coins.split(",")
    ml = months(a.start, a.end)
    cache = Path(a.cache)
    data = {}
    for c in coins:
        sym = SYMBOLS.get(c, f"{c}USDT")
        b15 = load_klines(sym, ml, cache)
        ft, fr = load_funding(sym, ml, cache)
        data[c] = {"30m": resample(b15, H // 2), "1h": resample(b15, H), "6h": resample(b15, 6 * H), "fund": (ft, fr)}
        print(f"{c}: {len(b15)} bougies 15 min, {len(ft)} funding", flush=True)

    def mstart(mo: str) -> float:
        y, m = map(int, mo.split("-"))
        return datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000
    nxt = months(a.split, a.end)
    test_from = nxt[1] if len(nxt) > 1 else a.end
    train = (mstart(a.start), mstart(test_from))
    ey, em = map(int, a.end.split("-"))
    after_end = f"{ey + (em == 12):04d}-{em % 12 + 1:02d}"
    test = (mstart(test_from), mstart(after_end))

    report = {"periods": {"train": [a.start, a.split], "test": [test_from, a.end]}, "coins": coins,
              "rule": (f"par famille : meilleur Sharpe d'apprentissage parmi trades ≥ {a.min_trades} ; TIENT si en "
                       "vérification Sharpe ≥ 0.8, PF ≥ 1.2, rendement > 0, DD < 25 %, et rendement > 0 à coûts ×2"),
              "families": {}}
    base, stress = Costs(), Costs(mult=2.0)
    for fam, grid in families(data).items():
        rows = []
        for params, build in grid:
            tr = run_config(data, coins, build, *train, base)
            te = run_config(data, coins, build, *test, base)
            rows.append({"params": params, "train": tr, "test": te})
            print(fam, params, "train", tr["sharpe"], tr["trades"], "| test", te["sharpe"], te["trades"], flush=True)
        ok = [r for r in rows if r["train"]["trades"] >= a.min_trades]
        choice = max(ok, key=lambda r: r["train"]["sharpe"]) if ok else None
        verdict, stress_res = "pas de réglage éligible", None
        if choice:
            build = grid[rows.index(choice)][1]
            stress_res = run_config(data, coins, build, *test, stress)
            t = choice["test"]
            holds = (t["sharpe"] >= 0.8 and t["profit_factor"] >= 1.2 and t["return_pct"] > 0
                     and t["max_dd_pct"] < 25 and stress_res["return_pct"] > 0)
            verdict = "TIENT" if holds else "NE TIENT PAS"
        report["families"][fam] = {"rows": rows, "choice": choice["params"] if choice else None,
                                   "stress_test": stress_res, "verdict": verdict}
    report["runtime_s"] = round(time.time() - t0)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"bars_{a.start}_{a.end}"
    (out / f"{stem}.json").write_text(json.dumps(report, indent=2, default=str))
    cols = ["trades", "return_pct", "cagr_pct", "max_dd_pct", "sharpe", "profit_factor", "win_rate", "avg_bars"]
    md = [f"# Recherche sur bougies {a.start} → {a.end} ({', '.join(coins)})", "",
          f"Apprentissage {a.start} → {a.split} · vérification {test_from} → {a.end}", "",
          f"Règle : {report['rule']}", ""]
    md += ["| famille | réglage choisi | verdict | vérif. Sharpe | vérif. rendement % | vérif. DD % | coûts ×2 rendement % |",
           "|---|---|---|---|---|---|---|"]
    for fam, f in report["families"].items():
        ch = next((r for r in f["rows"] if r["params"] == f["choice"]), None)
        md.append(f"| {fam} | {f['choice']} | **{f['verdict']}** | {ch['test']['sharpe'] if ch else '-'} | "
                  f"{ch['test']['return_pct'] if ch else '-'} | {ch['test']['max_dd_pct'] if ch else '-'} | "
                  f"{f['stress_test']['return_pct'] if f['stress_test'] else '-'} |")
    md.append("")
    for fam, f in report["families"].items():
        md += [f"## {fam}", "", "| réglage | période | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
        for r in f["rows"]:
            for per in ("train", "test"):
                md.append(f"| {r['params']} | {per} | " + " | ".join(str(r[per].get(c)) for c in cols) + " |")
        md.append("")
    (out / f"{stem}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
