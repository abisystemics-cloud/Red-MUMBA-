"""Faux flux temps réel (Hyperliquid + Binance + Bybit) pour le mode démo.

`python main.py --demo` lance l'essaim complet en paper trading sur un marché
synthétique rejoué en temps réel (ou accéléré), sans réseau ni clé, pour voir
l'interface fonctionner.
"""
from __future__ import annotations

import asyncio
import random

from core.events import WhaleBias, Topic, now_ms
from demo.fakes import make_connect
from demo.synthetic import generate


def demo_connect(coins: list[str], speed: float = 1.0, seed: int = 21):
    """Retourne (connect_fn, extra_task_factory). `speed` > 1 accélère le temps."""
    streams = {c: generate(6 * 3600, coin=c, seed=seed + i, start_px=60_000.0 if c == "BTC" else 3_000.0)
               for i, c in enumerate(coins)}
    ext_q: asyncio.Queue = asyncio.Queue()
    byb_q: asyncio.Queue = asyncio.Queue()

    async def hl():
        iters = {c: iter(s) for c, s in streams.items()}
        while True:
            progressed = False
            for c, it in iters.items():
                for r in it:
                    ts = now_ms()
                    progressed = True
                    if r["t"] == "book":
                        yield {"channel": "l2Book", "data": {"coin": c, "time": ts, "levels": [
                            [{"px": str(p), "sz": str(s), "n": 1} for p, s in r["b"]],
                            [{"px": str(p), "sz": str(s), "n": 1} for p, s in r["a"]]]}}
                        break  # un carnet par marché et par tick
                    if r["t"] == "trade":
                        yield {"channel": "trades", "data": [{"coin": c, "side": "B" if r["buy"] else "A",
                                                               "px": str(r["px"]), "sz": str(r["sz"]),
                                                               "time": ts, "tid": random.randint(1, 10 ** 9)}]}
                    elif r["t"] == "ctx":
                        f = 1e-5 + random.gauss(0, 4e-5)
                        yield {"channel": "activeAssetCtx", "data": {"coin": c, "ctx": {
                            "openInterest": str(r["oi"]), "funding": str(f), "markPx": str(r["m"]),
                            "oraclePx": str(r["o"]), "dayNtlVlm": "1", "premium": "0"}}}
                    elif r["t"] == "ext":
                        ext_q.put_nowait(r | {"coin": c})
            if not progressed:  # fin de la série : on repart du début
                iters = {c: iter(s) for c, s in streams.items()}
            await asyncio.sleep(0.5 / speed)

    async def binance():
        while True:
            r = await ext_q.get()
            if r["v"] == "binance":
                sym = f"{r['coin']}USDT"
                yield {"stream": f"{sym.lower()}@bookTicker", "data": {"s": sym, "b": str(r["bid"]), "a": str(r["ask"])}}
                byb_q.put_nowait(r)

    async def bybit():
        while True:
            r = await byb_q.get()
            sym = f"{r['coin']}USDT"
            yield {"topic": f"orderbook.1.{sym}", "type": "snapshot",
                   "data": {"s": sym, "b": [[str(r["bid"] * 0.99999), "1"]], "a": [[str(r["ask"] * 1.00001), "1"]]}}

    connect = make_connect({"wss://api.hyperliquid-testnet.xyz": hl, "wss://api.hyperliquid.xyz": hl,
                            "wss://fstream.binance.com": binance, "wss://stream.bybit.com": bybit}, {})

    async def positioning(bus, stop: asyncio.Event):
        """Biais de positionnement synthétique (marche aléatoire), toutes les 15 s."""
        bias = {c: 0.0 for c in coins}
        while not stop.is_set():
            for c in coins:
                bias[c] = max(-1.0, min(1.0, bias[c] + random.gauss(0, 0.08)))
                bus.publish(Topic.WHALES, WhaleBias(c, now_ms(), bias[c], 200, 5e8))
            try:
                await asyncio.wait_for(stop.wait(), timeout=15 / speed)
            except asyncio.TimeoutError:
                pass

    return connect, positioning
