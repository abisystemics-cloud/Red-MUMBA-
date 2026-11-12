"""Agent 1 — Hyperliquid Data Agent (le flux sanguin).

Flux :
- Hyperliquid WS : l2Book, trades (Time & Sales), activeAssetCtx (OI, funding,
  mark/oracle) pour chaque marché.
- Binance USDⓈ-M et Bybit linear : meilleur bid/ask en temps réel (WebSockets
  publics directs — c'est la seule façon d'avoir ces prix à la milliseconde ;
  une API agrégée de type CoinGecko a des minutes de retard).
- Carte des liquidations : API Coinglass (clé requise) ou, à défaut, extraction
  Firecrawl d'une page publique, à basse fréquence (≥ 60 s).

Toutes les sources sont normalisées en événements (core.events) publiés sur le
bus et, si activé, enregistrées pour le backtest.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

import numpy as np

from agents.base import BaseAgent
from core.events import (AssetCtx, BookSnapshot, ExternalQuote, LiquidationMap,
                         Topic, Trade, now_ms)
from core.ws_client import ResilientWebSocket
from ml_engine.recorder import MarketRecorder


def parse_hl_book(data: dict, recv_ts: int) -> BookSnapshot:
    lv = data["levels"]
    bids = np.array([[float(x["px"]), float(x["sz"])] for x in lv[0]], dtype=float).reshape(-1, 2)
    asks = np.array([[float(x["px"]), float(x["sz"])] for x in lv[1]], dtype=float).reshape(-1, 2)
    return BookSnapshot(data["coin"], int(data["time"]), recv_ts, bids, asks)


def parse_hl_trades(data: list[dict]) -> list[Trade]:
    # Hyperliquid : side "B" = l'agresseur achète, "A" = l'agresseur vend.
    return [Trade(t["coin"], int(t["time"]), float(t["px"]), float(t["sz"]), t["side"] == "B", t.get("tid"))
            for t in data]


def parse_hl_ctx(data: dict, ts: int) -> AssetCtx:
    c = data["ctx"]
    f = lambda k: float(c.get(k) or 0.0)  # noqa: E731
    return AssetCtx(data["coin"], ts, f("openInterest"), f("funding"), f("markPx"),
                    f("oraclePx"), f("dayNtlVlm"), f("premium"))


class HyperliquidDataAgent(BaseAgent):
    name = "data"

    def __init__(self, bus, store, connect_fn=None, http_session=None):
        super().__init__(bus, store)
        cfg = self.cfg
        self.coins = [m.coin for m in cfg.markets]
        self._bin_map = {m.binance.lower(): m.coin for m in cfg.markets if m.binance}
        self._byb_map = {m.bybit.upper(): m.coin for m in cfg.markets if m.bybit}
        kw = {"connect_fn": connect_fn} if connect_fn else {}
        self.recorder = MarketRecorder(cfg.data.recordings_dir) if cfg.data.record_market_data else None
        self._http = http_session
        self.last_seen: dict[str, int] = {}

        self.hl_ws = ResilientWebSocket("hyperliquid", cfg.hl_ws_url(), self._on_hl,
                                        heartbeat_msg={"method": "ping"}, heartbeat_s=30,
                                        stale_after_s=45, **kw)
        h = cfg.data.hyperliquid
        for coin in self.coins:
            book_sub: dict[str, Any] = {"type": "l2Book", "coin": coin}
            if h.n_sig_figs:
                book_sub["nSigFigs"] = h.n_sig_figs
            if os.getenv("HL_BOOK_WS_URL"):  # fournisseur 100 niveaux (paramètre non public)
                book_sub["nLevels"] = h.book_levels
            for sub in (book_sub, {"type": "trades", "coin": coin}, {"type": "activeAssetCtx", "coin": coin}):
                self.hl_ws.add_subscription({"method": "subscribe", "subscription": sub})

        streams = "/".join(f"{s}@bookTicker" for s in self._bin_map)
        self.bin_ws = ResilientWebSocket("binance", f"{cfg.data.binance_ws}?streams={streams}",
                                         self._on_binance, stale_after_s=30, **kw) if streams else None
        self.byb_ws = ResilientWebSocket("bybit", cfg.data.bybit_ws, self._on_bybit,
                                         heartbeat_msg={"op": "ping"}, heartbeat_s=20,
                                         stale_after_s=45, **kw) if self._byb_map else None
        if self.byb_ws:
            self.byb_ws.add_subscription({"op": "subscribe",
                                          "args": [f"orderbook.1.{s}" for s in self._byb_map]})
        self._bybit_book: dict[str, list[float]] = {}

    # ------------------------------------------------------------ handlers
    def _on_hl(self, msg: dict) -> None:
        ch = msg.get("channel")
        data = msg.get("data")
        recv = now_ms()
        if ch == "l2Book":
            book = parse_hl_book(data, recv)
            if len(book.bids) and len(book.asks):
                self.bus.publish(Topic.BOOK, book)
                self.last_seen[f"book:{book.coin}"] = recv
                if self.recorder:
                    self.recorder.book(book)
        elif ch == "trades":
            trades = parse_hl_trades(data)
            if trades:
                self.bus.publish(Topic.TRADE, trades)
                self.last_seen[f"trades:{trades[0].coin}"] = recv
                if self.recorder:
                    for t in trades:
                        self.recorder.trade(t)
        elif ch == "activeAssetCtx":
            ctx = parse_hl_ctx(data, recv)
            self.bus.publish(Topic.ASSET_CTX, ctx)
            if self.recorder:
                self.recorder.ctx(ctx)
        elif ch == "error":
            self.errors += 1
            self.log.error("hyperliquid ws error: %s", data)
        self.beat()

    def _emit_ext(self, q: ExternalQuote) -> None:
        self.bus.publish(Topic.EXT_QUOTE, q)
        self.last_seen[f"{q.venue}:{q.coin}"] = q.ts
        if self.recorder:
            self.recorder.ext(q)

    def _on_binance(self, msg: dict) -> None:
        d = msg.get("data") or {}
        coin = self._bin_map.get(str(d.get("s", "")).lower())
        if coin:
            self._emit_ext(ExternalQuote("binance", coin, now_ms(), float(d["b"]), float(d["a"])))

    def _on_bybit(self, msg: dict) -> None:
        topic = msg.get("topic", "")
        if not topic.startswith("orderbook."):
            return
        d = msg.get("data") or {}
        sym = d.get("s") or topic.rsplit(".", 1)[-1]
        coin = self._byb_map.get(sym)
        if not coin:
            return
        st = self._bybit_book.setdefault(sym, [float("nan"), float("nan")])
        if d.get("b"):
            st[0] = float(d["b"][0][0])
        if d.get("a"):
            st[1] = float(d["a"][0][0])
        if st[0] == st[0] and st[1] == st[1]:
            self._emit_ext(ExternalQuote("bybit", coin, now_ms(), st[0], st[1]))

    # ------------------------------------------------------- liquidations
    async def _poll_liquidations(self, stop: asyncio.Event) -> None:
        lc = self.cfg.data.liquidations
        if lc.provider == "disabled" or self._http is None:
            return
        warned = False
        while not stop.is_set():
            for m in self.cfg.markets:
                try:
                    clusters = await (self._coinglass(m) if lc.provider == "coinglass" else self._firecrawl(m))
                    if clusters:
                        self.bus.publish(Topic.LIQ_MAP, LiquidationMap(m.coin, now_ms(), clusters, lc.provider))
                except Exception as exc:  # noqa: BLE001
                    if not warned:
                        self.log.warning("liquidation source %s unavailable: %s", lc.provider, exc)
                        warned = True
            try:
                await asyncio.wait_for(stop.wait(), timeout=lc.poll_seconds)
            except asyncio.TimeoutError:
                pass

    async def _coinglass(self, m) -> list[tuple[float, float]]:
        key = os.getenv("COINGLASS_API_KEY")
        if not key:
            raise RuntimeError("COINGLASS_API_KEY not set")
        lc = self.cfg.data.liquidations
        url = lc.coinglass_base_url + lc.coinglass_heatmap_path
        params = {"exchange": "Binance", "symbol": (m.bybit or f"{m.coin}USDT"), "range": "3d"}
        async with self._http.get(url, params=params, headers={"CG-API-KEY": key}, timeout=15) as r:
            r.raise_for_status()
            body = await r.json()
        data = body.get("data") or {}
        prices = data.get("y") or data.get("y_axis") or []
        liq = data.get("liq") or data.get("liquidation_leverage_data") or []
        agg: dict[int, float] = {}
        for x in liq:
            if len(x) >= 3:
                agg[int(x[1])] = agg.get(int(x[1]), 0.0) + float(x[2])
        out = [(float(prices[i]), v) for i, v in agg.items() if 0 <= i < len(prices)]
        return sorted(out, key=lambda c: -c[1])[:15]

    async def _firecrawl(self, m) -> list[tuple[float, float]]:
        key = os.getenv("FIRECRAWL_API_KEY")
        url = self.cfg.data.liquidations.firecrawl_url
        if not key or not url:
            raise RuntimeError("FIRECRAWL_API_KEY or firecrawl_url missing")
        schema = {"type": "object", "properties": {"clusters": {"type": "array", "items": {
            "type": "object", "properties": {"price": {"type": "number"}, "usd": {"type": "number"}}}}}}
        payload = {"url": url.format(coin=m.coin), "formats": ["json"],
                   "jsonOptions": {"schema": schema,
                                   "prompt": f"Liquidation clusters for {m.coin}: price level and USD size"}}
        api = os.getenv("FIRECRAWL_API_URL", "https://api.firecrawl.dev/v1/scrape")
        async with self._http.post(api, json=payload, headers={"Authorization": f"Bearer {key}"},
                                   timeout=60) as r:
            r.raise_for_status()
            body = await r.json()
        cl = ((body.get("data") or {}).get("json") or {}).get("clusters") or []
        return [(float(c["price"]), float(c["usd"])) for c in cl if "price" in c and "usd" in c]

    # ------------------------------------------------------------- run
    async def run(self, stop: asyncio.Event) -> None:
        tasks = [asyncio.create_task(self.hl_ws.run(stop), name="ws-hyperliquid")]
        if self.bin_ws:
            tasks.append(asyncio.create_task(self.bin_ws.run(stop), name="ws-binance"))
        if self.byb_ws:
            tasks.append(asyncio.create_task(self.byb_ws.run(stop), name="ws-bybit"))
        tasks.append(asyncio.create_task(self._poll_liquidations(stop), name="liquidations"))
        try:
            await asyncio.gather(*tasks)
        finally:
            for t in tasks:
                t.cancel()

    async def shutdown(self) -> None:
        if self.recorder:
            self.recorder.close()

    def health(self) -> dict:
        h = super().health()
        now = now_ms()
        h["feeds"] = {k: now - v for k, v in self.last_seen.items()}
        for ws in (self.hl_ws, self.bin_ws, self.byb_ws):
            if ws:
                h[ws.name] = {"connected": ws.connected.is_set(), "reconnects": ws.reconnects,
                              "messages": ws.messages, "last_error": ws.last_error}
        return h
