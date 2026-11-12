"""Agrège en mémoire l'état temps réel affiché par l'interface web.

Écoute le bus (features, signaux validés, niveau de risque, télémétrie) et
expose `snapshot()` : un dictionnaire JSON compact envoyé au navigateur
chaque seconde. Aucune écriture, aucun effet sur le trading.
"""
from __future__ import annotations

import asyncio
import math
import time
from collections import deque
from typing import Any, Callable

from agents.base import BaseAgent
from core.events import Topic, now_ms

EVENT_KINDS = {"order", "fill", "trade_closed", "risk_level", "breaker", "feed_down", "feed_up",
               "command_ack", "command_applied", "signal", "research_run", "go_live_report"}


def _num(x: Any, nd: int = 4) -> Any:
    if isinstance(x, float):
        return round(x, nd) if math.isfinite(x) else None
    return x


class UIStateAgent(BaseAgent):
    name = "ui"

    def __init__(self, bus, store, status_fn: Callable[[], dict]):
        super().__init__(bus, store)
        self.status_fn = status_fn
        self.subs = {t: bus.subscribe(t, self.name, maxsize=ms) for t, ms in (
            (Topic.FEATURES, 256), (Topic.VALIDATED, 256), (Topic.RISK_STATE, 64), (Topic.TELEMETRY, 5000))}
        self.markets: dict[str, dict] = {}
        self.risk: dict = {"level": "unknown", "reasons": []}
        self.events: deque = deque(maxlen=300)
        self.equity: deque = deque(maxlen=17_280)   # 24 h à 5 s
        self.started = time.time()
        self.stale_after_s = 3600

    # ---------------------------------------------------------- consumers
    def on_features(self, f) -> None:
        m = self.markets.setdefault(f.coin, {})
        m.update(coin=f.coin, ts=f.ts, mid=_num(f.mid, 6), spread_bps=_num(f.spread_bps, 2),
                 vol_bps=_num(f.realized_vol_bps, 2),
                 features={"obi": _num(f.obi_z, 2), "cvd": _num(f.cvd_slope_z, 2),
                           "premium": _num(-f.premium_z, 2), "funding": _num(-f.funding_z, 2),
                           "whales": _num(3 * f.whale_bias, 2),
                           "liq": _num(max(-3, min(3, f.liq_magnet_bps / 50)), 2)
                           if math.isfinite(f.liq_magnet_bps) else None},
                 raw={"premium_bps": _num(f.premium_bps, 2), "funding": _num(f.funding, 7),
                      "whale_bias": _num(f.whale_bias, 3), "liq_bps": _num(f.liq_magnet_bps, 1),
                      "spoof_bid": _num(f.spoof_bid, 2), "spoof_ask": _num(f.spoof_ask, 2),
                      "poc_dist_bps": _num(f.poc_dist_bps, 1)})

    def on_signal(self, s) -> None:
        m = self.markets.setdefault(s.coin, {})
        m.update(score=_num(s.score, 3), side=s.side.value, validated=s.validated,
                 rejections=s.rejections[:3])

    def on_risk(self, st) -> None:
        self.risk = {"level": st.level.value, "reasons": st.reasons, "ts": st.ts,
                     "llm_risk_score": st.llm_risk_score}

    def on_telemetry(self, ev: dict) -> None:
        kind = ev.get("event")
        if kind == "equity":
            self.equity.append((now_ms(), ev.get("equity")))
        if kind in EVENT_KINDS:
            self.events.append({"ts": now_ms(), **{k: v for k, v in ev.items() if k != "status_snapshot"}})

    async def _consume(self, topic: Topic, fn) -> None:
        sub = self.subs[topic]
        while True:
            fn(await sub.get())

    async def run(self, stop: asyncio.Event) -> None:
        tasks = [asyncio.create_task(self._consume(t, fn)) for t, fn in (
            (Topic.FEATURES, self.on_features), (Topic.VALIDATED, self.on_signal),
            (Topic.RISK_STATE, self.on_risk), (Topic.TELEMETRY, self.on_telemetry))]
        try:
            while not stop.is_set():
                self.beat()
                try:
                    await asyncio.wait_for(stop.wait(), timeout=5)
                except asyncio.TimeoutError:
                    pass
        finally:
            for t in tasks:
                t.cancel()

    # ------------------------------------------------------------ output
    def equity_series(self, points: int = 300) -> list[list]:
        data = [(t, e) for t, e in self.equity if e is not None]
        if len(data) <= points:
            return [[t, round(e, 2)] for t, e in data]
        step = len(data) / points
        return [[data[int(i * step)][0], round(data[int(i * step)][1], 2)] for i in range(points)] + \
               [[data[-1][0], round(data[-1][1], 2)]]

    def snapshot(self) -> dict:
        cfg = self.cfg
        status = self.status_fn()
        exe = status.get("execution", {})
        open_pos = []
        unreal = 0.0
        for coin, p in (exe.get("open") or {}).items():
            mid = (self.markets.get(coin) or {}).get("mid")
            sign = 1 if p["side"] == "long" else -1
            u = sign * (mid - p["entry"]) * p["qty"] if mid else None
            unreal += u or 0.0
            open_pos.append({"coin": coin, "side": p["side"], "qty": p["qty"], "entry": p["entry"],
                             "mark": mid, "upnl": _num(u, 2)})
        st = cfg.strategy
        return {
            "ts": now_ms(),
            "uptime_s": int(time.time() - self.started),
            "mode": {"network": cfg.runtime.network, "dry_run": cfg.runtime.dry_run,
                     "execution": cfg.execution.mode},
            "risk": self.risk,
            "account": {"equity": exe.get("equity"), "realized_pnl": exe.get("realized_pnl"),
                        "unrealized_pnl": round(unreal, 2), "risk_scale": exe.get("risk_scale", 1.0),
                        "breaker": exe.get("breaker"), "win_rate_est": exe.get("win_rate_est"),
                        "start_equity": cfg.risk.paper_equity_usd},
            "positions": open_pos,
            "markets": [self.markets[c] for c in sorted(self.markets)],
            "thresholds": {"entry": st.entry_threshold, "exit": st.exit_threshold},
            "disabled_coins": (status.get("validation") or {}).get("disabled_coins", []),
            "paused": (status.get("macro") or {}).get("paused"),
            "feeds": (status.get("data") or {}).get("feeds", {}),
            "agents": {name: {"stale": h.get("stale"), "errors": h.get("errors")} for name, h in status.items()
                       if isinstance(h, dict) and "stale" in h},
            "equity": self.equity_series(),
            "events": list(self.events)[-60:][::-1],
        }
