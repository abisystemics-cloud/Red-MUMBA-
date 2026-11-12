"""Agent 2 — Quant & Stat Agent (le cerveau mathématique).

Consomme le flux normalisé de l'agent Data, maintient un FeatureEngine par
marché (OBI, CVD, VPVR/POC, spoofing, premium cross-exchange, volatilité) et
publie à chaque snapshot du carnet :
- un FeatureVector (Topic.FEATURES) — aussi exposé en tenseur numpy ;
- un Signal brut (Topic.SIGNAL) issu du SignalModel partagé avec le backtest.

Latence mesurée : du recv du carnet à la publication du signal.
"""
from __future__ import annotations

import asyncio

import numpy as np

from agents.base import BaseAgent
from core.events import FeatureVector, Signal, Topic, mono_ns
from ml_engine.features import FeatureEngine
from ml_engine.strategy import SignalModel

TENSOR_FIELDS = ("mid", "spread_bps", "obi", "obi_z", "cvd", "cvd_slope_z", "poc_dist_bps",
                 "premium_bps", "premium_z", "spoof_bid", "spoof_ask", "realized_vol_bps",
                 "oi_change_pct", "funding", "funding_z", "whale_bias")


def to_tensor(f: FeatureVector) -> np.ndarray:
    return np.array([getattr(f, k) for k in TENSOR_FIELDS], dtype=np.float32)


class QuantAgent(BaseAgent):
    name = "quant"

    def __init__(self, bus, store):
        super().__init__(bus, store)
        st = self.cfg.strategy
        self.engines = {m.coin: FeatureEngine(m.coin, st, self.cfg.data.max_staleness_ms)
                        for m in self.cfg.markets}
        self.models = {c: SignalModel(st) for c in self.engines}
        self.subs = {t: bus.subscribe(t, self.name, maxsize=ms) for t, ms in (
            (Topic.BOOK, 64), (Topic.TRADE, 4096), (Topic.ASSET_CTX, 256),
            (Topic.EXT_QUOTE, 4096), (Topic.LIQ_MAP, 16), (Topic.WHALES, 16))}
        self.latency_us: list[float] = []

    async def on_config_change(self, old, new) -> None:
        for c, e in self.engines.items():
            e.apply_config(new.strategy)
            self.models[c].apply_config(new.strategy)
        self.log.info("strategy parameters hot-swapped (state preserved)")

    async def _consume_side(self, topic: Topic) -> None:
        sub = self.subs[topic]
        while True:
            msg = await sub.get()
            if topic == Topic.TRADE:
                for t in msg:
                    e = self.engines.get(t.coin)
                    if e:
                        e.on_trade(t)
            else:
                e = self.engines.get(msg.coin)
                if e is None:
                    continue
                {Topic.ASSET_CTX: e.on_ctx, Topic.EXT_QUOTE: e.on_ext, Topic.LIQ_MAP: e.on_liq,
                 Topic.WHALES: e.on_whale}[topic](msg)

    async def _consume_books(self) -> None:
        sub = self.subs[Topic.BOOK]
        while True:
            book = await sub.get()
            e = self.engines.get(book.coin)
            if e is None:
                continue
            f = e.on_book(book)
            side, score = self.models[book.coin].update(f)
            self.bus.publish(Topic.FEATURES, f)
            self.bus.publish(Topic.SIGNAL, Signal(book.coin, f.ts, side, score, f))
            lat = (mono_ns() - book.recv_ns) / 1000
            self.latency_us.append(lat)
            if len(self.latency_us) > 1000:
                self.latency_us = self.latency_us[-500:]
            self.beat()

    async def run(self, stop: asyncio.Event) -> None:
        tasks = [asyncio.create_task(self._consume_books())]
        tasks += [asyncio.create_task(self._consume_side(t))
                  for t in (Topic.TRADE, Topic.ASSET_CTX, Topic.EXT_QUOTE, Topic.LIQ_MAP, Topic.WHALES)]
        await stop.wait()
        for t in tasks:
            t.cancel()

    def health(self) -> dict:
        h = super().health()
        if self.latency_us:
            a = np.array(self.latency_us)
            h["latency_us"] = {"p50": round(float(np.percentile(a, 50)), 1),
                               "p99": round(float(np.percentile(a, 99)), 1)}
        h["spoof_events"] = {c: e.spoof.events for c, e in self.engines.items()}
        return h
