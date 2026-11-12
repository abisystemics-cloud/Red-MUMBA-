"""Générateur de marché synthétique (tests + simulation sans réseau).

Le prix CEX suit une marche aléatoire ; Hyperliquid le suit avec un retard
(lead-lag), ce qui donne au signal "premium" un avantage mesurable.
"""
from __future__ import annotations

import math
import random


def generate(n_seconds: int = 3600, coin: str = "BTC", start_px: float = 60_000.0,
             seed: int = 7, lag_ticks: int = 3, tick_ms: int = 500) -> list[dict]:
    rng = random.Random(seed)
    recs: list[dict] = []
    cex = start_px
    hist: list[float] = []
    ts = 1_760_000_000_000
    oi = 1e9
    for _ in range(int(n_seconds * 1000 / tick_ms)):
        ts += tick_ms
        cex *= math.exp(rng.gauss(0, 0.00025))
        hist.append(cex)
        hl = hist[-lag_ticks] if len(hist) >= lag_ticks else cex
        hl *= 1 + rng.gauss(0, 0.00003)
        tick = 1.0
        bid0 = math.floor(hl / tick) * tick
        bids = [[bid0 - i * tick, round(rng.uniform(0.5, 3.0), 4)] for i in range(20)]
        asks = [[bid0 + (i + 1) * tick, round(rng.uniform(0.5, 3.0), 4)] for i in range(20)]
        drift = cex - hl
        tilt = max(-0.9, min(0.9, drift / (hl * 0.0005)))
        for lv in bids[:5]:
            lv[1] = round(lv[1] * (1 + tilt), 4) if tilt > 0 else lv[1]
        for lv in asks[:5]:
            lv[1] = round(lv[1] * (1 - tilt), 4) if tilt < 0 else lv[1]
        recs.append({"t": "ext", "coin": coin, "ts": ts - 50, "v": "binance", "bid": cex - 0.5, "ask": cex + 0.5})
        recs.append({"t": "ext", "coin": coin, "ts": ts - 40, "v": "bybit", "bid": cex - 0.6, "ask": cex + 0.6})
        for _ in range(rng.randint(0, 4)):
            buy = rng.random() < 0.5 + tilt * 0.4
            recs.append({"t": "trade", "coin": coin, "ts": ts - 10,
                         "px": asks[0][0] if buy else bids[0][0],
                         "sz": round(rng.expovariate(2.0), 4), "buy": buy})
        if rng.random() < 0.02:
            oi *= 1 + rng.gauss(0, 0.002)
            recs.append({"t": "ctx", "coin": coin, "ts": ts - 5, "oi": oi, "f": 1e-5, "m": hl, "o": cex})
        recs.append({"t": "book", "coin": coin, "ts": ts, "b": bids, "a": asks})
    recs.sort(key=lambda r: r["ts"])
    return recs
