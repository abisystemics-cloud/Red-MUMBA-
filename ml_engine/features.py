"""Moteur de features microstructure — incrémental, O(1) ou O(profondeur) par tick.

Le MÊME code tourne en live (agent Quant) et en backtest (agent R&D) : c'est la
condition pour qu'un backtest dise quelque chose du live.

Features :
- OBI  : Order Book Imbalance pondéré par la profondeur (décroissance expo).
- CVD  : Cumulative Volume Delta (volume agresseur acheteur − vendeur) et sa
         pente sur une fenêtre glissante.
- VPVR : Volume Profile Visible Range sur fenêtre glissante → POC (Point of
         Control) ; buckets logarithmiques de largeur constante en bps.
- Spoofing : gros ordres proches du top qui disparaissent vite sans être
         exécutés.
- Premium cross-exchange : écart HL vs médiane Binance/Bybit (en bps) + z-score
         (le z-score retire la base structurelle liée au funding).
- Volatilité réalisée EWMA, variation d'OI, funding, distance au cluster de
  liquidations le plus proche.
"""
from __future__ import annotations

import math
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from core.events import (AssetCtx, BookSnapshot, ExternalQuote, FeatureVector,
                         LiquidationMap, Trade)


class RollingZ:
    """z-score sur fenêtre glissante (sommes incrémentales)."""

    __slots__ = ("n", "buf", "s", "ss")

    def __init__(self, n: int):
        self.n = max(2, int(n))
        self.buf: deque[float] = deque()
        self.s = 0.0
        self.ss = 0.0

    def update(self, x: float) -> float:
        if not math.isfinite(x):
            return 0.0
        self.buf.append(x)
        self.s += x
        self.ss += x * x
        if len(self.buf) > self.n:
            old = self.buf.popleft()
            self.s -= old
            self.ss -= old * old
        k = len(self.buf)
        if k < 10:
            return 0.0
        mean = self.s / k
        var = max(self.ss / k - mean * mean, 1e-18)
        return (x - mean) / math.sqrt(var)


def order_book_imbalance(bids: np.ndarray, asks: np.ndarray, depth: int, decay: float) -> float:
    """OBI ∈ [-1, 1] ; >0 = pression acheteuse."""
    d = min(depth, len(bids), len(asks))
    if d == 0:
        return 0.0
    w = np.exp(-decay * np.arange(d))
    b = float(np.dot(bids[:d, 1], w))
    a = float(np.dot(asks[:d, 1], w))
    tot = a + b
    return (b - a) / tot if tot > 0 else 0.0


def log_bucket(px: float, bucket_bps: float) -> int:
    return int(round(math.log(px) / math.log1p(bucket_bps / 1e4)))


def bucket_price(idx: int, bucket_bps: float) -> float:
    return math.exp(idx * math.log1p(bucket_bps / 1e4))


@dataclass
class SpoofDetector:
    size_mult: float
    max_life_s: float
    near_levels: int = 10
    decay_s: float = 15.0
    _tracked: dict = field(default_factory=lambda: {"bid": {}, "ask": {}})
    _traded: dict = field(default_factory=lambda: defaultdict(float))
    _score: dict = field(default_factory=lambda: {"bid": 0.0, "ask": 0.0})
    _last_ts: int = 0
    events: int = 0

    def on_trade(self, t: Trade) -> None:
        self._traded[round(t.px, 8)] += t.sz

    def on_book(self, book: BookSnapshot) -> tuple[float, float]:
        ts = book.exch_ts
        if self._last_ts:
            dt = max(0.0, (ts - self._last_ts) / 1000)
            k = math.exp(-dt / self.decay_s)
            for s in self._score:
                self._score[s] *= k
        self._last_ts = ts
        for side, levels in (("bid", book.bids), ("ask", book.asks)):
            lv = levels[: self.near_levels]
            if len(lv) < 3:
                continue
            med = float(np.median(lv[:, 1]))
            current = {round(float(p), 8): float(s) for p, s in lv}
            tracked = self._tracked[side]
            # ordres suivis qui ont disparu / fondu de >80 %
            for px, (first_ts, size) in list(tracked.items()):
                now_sz = current.get(px, 0.0)
                if now_sz < 0.2 * size:
                    life = (ts - first_ts) / 1000
                    executed = self._traded.get(px, 0.0)
                    if life <= self.max_life_s and executed < 0.2 * size:
                        self._score[side] += 1.0
                        self.events += 1
                    del tracked[px]
                elif (ts - first_ts) / 1000 > self.max_life_s:
                    del tracked[px]  # ordre "honnête" : il est resté
            for px, sz in current.items():
                if med > 0 and sz > self.size_mult * med and px not in tracked:
                    tracked[px] = (ts, sz)
        if len(self._traded) > 5000:
            self._traded.clear()
        return (1 - math.exp(-self._score["bid"]), 1 - math.exp(-self._score["ask"]))


class FeatureEngine:
    """État de features d'UNE paire. `on_book` renvoie un FeatureVector."""

    def __init__(self, coin: str, cfg, max_staleness_ms: int = 2500):
        self.coin = coin
        self.max_staleness_ms = max_staleness_ms
        self.apply_config(cfg)
        self.cvd = 0.0
        self._cvd_hist: deque[tuple[int, float]] = deque()
        self._vp_trades: deque[tuple[int, int, float]] = deque()
        self._vp: dict[int, float] = defaultdict(float)
        self._ext: dict[str, ExternalQuote] = {}
        self._ctx_hist: deque[tuple[int, float]] = deque()
        self._last_ctx: Optional[AssetCtx] = None
        self._liq: Optional[LiquidationMap] = None
        self._prev_mid: Optional[tuple[int, float]] = None
        self._var_per_s = 0.0
        self.last_book_ts = 0

    def apply_config(self, cfg) -> None:
        """Appelé au hot-reload : nouveaux paramètres, état conservé."""
        self.cfg = cfg
        if not hasattr(self, "z_obi") or self.z_obi.n != cfg.zscore_window:
            self.z_obi = RollingZ(cfg.zscore_window)
            self.z_cvd = RollingZ(cfg.zscore_window)
            self.z_prem = RollingZ(cfg.zscore_window)
        prev = getattr(self, "spoof", None)
        self.spoof = SpoofDetector(cfg.spoof_size_mult, cfg.spoof_max_life_s, near_levels=cfg.obi_depth)
        if prev is not None:
            self.spoof._score = prev._score

    # ----------------------------------------------------------- entrées
    def on_trade(self, t: Trade) -> None:
        signed = t.sz if t.is_buy else -t.sz
        self.cvd += signed
        self._cvd_hist.append((t.ts, self.cvd))
        horizon = t.ts - self.cfg.cvd_window_s * 1000
        while self._cvd_hist and self._cvd_hist[0][0] < horizon:
            self._cvd_hist.popleft()
        b = log_bucket(t.px, self.cfg.vpvr_bucket_bps)
        self._vp[b] += t.sz
        self._vp_trades.append((t.ts, b, t.sz))
        horizon = t.ts - self.cfg.vpvr_window_s * 1000
        while self._vp_trades and self._vp_trades[0][0] < horizon:
            _, ob, osz = self._vp_trades.popleft()
            self._vp[ob] -= osz
            if self._vp[ob] <= 1e-12:
                del self._vp[ob]
        self.spoof.on_trade(t)

    def on_ext(self, q: ExternalQuote) -> None:
        self._ext[q.venue] = q

    def on_ctx(self, c: AssetCtx) -> None:
        self._last_ctx = c
        self._ctx_hist.append((c.ts, c.open_interest))
        while self._ctx_hist and self._ctx_hist[0][0] < c.ts - 300_000:
            self._ctx_hist.popleft()

    def on_liq(self, m: LiquidationMap) -> None:
        self._liq = m

    # ----------------------------------------------------------- calcul
    def poc(self) -> float:
        if not self._vp:
            return float("nan")
        b = max(self._vp.items(), key=lambda kv: kv[1])[0]
        return bucket_price(b, self.cfg.vpvr_bucket_bps)

    def on_book(self, book: BookSnapshot, now_ms: Optional[int] = None) -> FeatureVector:
        cfg = self.cfg
        now = now_ms if now_ms is not None else book.recv_ts
        mid = book.mid
        self.last_book_ts = book.exch_ts

        obi = order_book_imbalance(book.bids, book.asks, cfg.obi_depth, cfg.obi_decay)
        obi_z = self.z_obi.update(obi)

        slope = 0.0
        if len(self._cvd_hist) >= 2:
            slope = self._cvd_hist[-1][1] - self._cvd_hist[0][1]
        cvd_z = self.z_cvd.update(slope)

        poc = self.poc()
        poc_dist = (mid - poc) / poc * 1e4 if poc == poc and poc > 0 else 0.0

        fresh = [q for q in self._ext.values() if now - q.ts <= self.max_staleness_ms]
        if fresh:
            ext_mid = float(np.median([q.mid for q in fresh]))
            premium = (mid - ext_mid) / ext_mid * 1e4
            ext_age = int(now - max(q.ts for q in fresh))
        else:
            premium = 0.0
            ext_age = 10 ** 9
        prem_z = self.z_prem.update(premium) if fresh else 0.0

        if self._prev_mid is not None:
            pts, pmid = self._prev_mid
            dt = max(1e-3, (book.exch_ts - pts) / 1000)
            r = math.log(mid / pmid) if pmid > 0 and mid > 0 else 0.0
            alpha = 1 - math.exp(-dt / 60.0)
            self._var_per_s = (1 - alpha) * self._var_per_s + alpha * (r * r / dt)
        self._prev_mid = (book.exch_ts, mid)
        vol_bps = math.sqrt(self._var_per_s) * 1e4

        spoof_bid, spoof_ask = self.spoof.on_book(book)

        oi_chg = 0.0
        if len(self._ctx_hist) >= 2 and self._ctx_hist[0][1] > 0:
            oi_chg = (self._ctx_hist[-1][1] / self._ctx_hist[0][1] - 1) * 100

        liq_bps = float("nan")
        if self._liq and self._liq.clusters:
            px, _ = max(self._liq.clusters, key=lambda c: c[1] / (1 + abs(c[0] - mid) / mid * 1e4))
            liq_bps = (px - mid) / mid * 1e4

        return FeatureVector(
            coin=self.coin, ts=book.exch_ts, mid=mid, spread_bps=book.spread_bps,
            obi=obi, obi_z=obi_z, cvd=self.cvd, cvd_slope_z=cvd_z,
            poc=poc, poc_dist_bps=poc_dist, premium_bps=premium, premium_z=prem_z,
            spoof_bid=spoof_bid, spoof_ask=spoof_ask, realized_vol_bps=vol_bps,
            oi_change_pct=oi_chg,
            funding=self._last_ctx.funding if self._last_ctx else 0.0,
            book_age_ms=int(now - book.exch_ts), ext_age_ms=ext_age,
            liq_magnet_bps=liq_bps, source_recv_ns=book.recv_ns,
        )
