"""Tests d'intégration contre le VRAI testnet Hyperliquid (aucun fonds réel).

    HL_INTEGRATION=1 pytest tests/integration -v                 # lecture seule
    HL_INTEGRATION=1 HL_ACCOUNT_ADDRESS=0x... HL_API_WALLET_PRIVATE_KEY=0x... \
        pytest tests/integration -v                              # + ordres

Les tests d'ordres posent un ordre post-only à 50 % sous le marché (il ne peut
pas s'exécuter), vérifient qu'il est ouvert, puis l'annulent.
"""
import asyncio
import json
import math
import os
import urllib.request

import pytest

from agents.data_agent import parse_hl_book, parse_hl_ctx, parse_hl_trades
from core.events import now_ms
from core.ws_client import ResilientWebSocket

WS = "wss://api.hyperliquid-testnet.xyz/ws"
API = "https://api.hyperliquid-testnet.xyz"
needs_keys = pytest.mark.skipif(
    not (os.getenv("HL_ACCOUNT_ADDRESS") and os.getenv("HL_API_WALLET_PRIVATE_KEY")),
    reason="HL_ACCOUNT_ADDRESS / HL_API_WALLET_PRIVATE_KEY (testnet) required")


def _info(body: dict):
    req = urllib.request.Request(API + "/info", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def test_info_meta_lists_btc():
    meta = _info({"type": "meta"})
    assert any(a["name"] == "BTC" for a in meta["universe"])


def test_websocket_streams_book_trades_and_ctx():
    got: dict[str, object] = {}

    def on_msg(m):
        ch = m.get("channel")
        if ch == "l2Book":
            got["book"] = parse_hl_book(m["data"], now_ms())
        elif ch == "trades" and m["data"]:
            got["trades"] = parse_hl_trades(m["data"])
        elif ch == "activeAssetCtx":
            got["ctx"] = parse_hl_ctx(m["data"], now_ms())

    async def scenario():
        ws = ResilientWebSocket("it", WS, on_msg, heartbeat_msg={"method": "ping"})
        for sub in ({"type": "l2Book", "coin": "BTC"}, {"type": "trades", "coin": "BTC"},
                    {"type": "activeAssetCtx", "coin": "BTC"}):
            ws.add_subscription({"method": "subscribe", "subscription": sub})
        stop = asyncio.Event()
        task = asyncio.create_task(ws.run(stop))
        for _ in range(300):
            if "book" in got and "ctx" in got:
                break
            await asyncio.sleep(0.1)
        stop.set()
        await asyncio.wait_for(task, 10)

    asyncio.run(scenario())
    book = got["book"]
    assert len(book.bids) > 0 and book.best_bid < book.best_ask
    assert got["ctx"].mark_px > 0


def test_whale_endpoint_shape():
    st = _info({"type": "clearinghouseState", "user": "0x0000000000000000000000000000000000000000"})
    assert "assetPositions" in st


@needs_keys
def test_post_only_place_status_cancel():
    from agents.brokers import HyperliquidBroker

    async def scenario():
        b = HyperliquidBroker(API)
        await b.start()
        snap = _info({"type": "l2Book", "coin": "BTC"})
        best_bid = float(snap["levels"][0][0]["px"])
        px = best_bid * 0.5
        szd = b.sz_decimals("BTC")
        sz = math.ceil(12 / px * 10 ** szd) / 10 ** szd       # ≥ 10 USD minimum
        f = await b.post_only("BTC", True, sz, px, False)
        assert f.ok and f.oid, f.error
        st = await b.order_status("BTC", f.oid)
        assert st.status == "open", st
        await b.cancel("BTC", f.oid)
        st = await b.order_status("BTC", f.oid)
        assert st.status == "canceled", st
        assert await b.equity() >= 0

    asyncio.run(scenario())
