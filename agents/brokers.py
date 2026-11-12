"""Brokers : Hyperliquid L1 (API wallet) et Paper (simulation).

Sécurité du wallet : on utilise un *API wallet* (agent wallet) Hyperliquid,
créé depuis l'interface (More → API). Il peut signer des ordres pour le compte
principal mais ne peut PAS retirer de fonds. Sa clé privée est la seule
donnée sensible ; l'adresse du compte principal est publique.
"""
from __future__ import annotations

import asyncio
import logging
import math
import os
import time
from dataclasses import dataclass, field
from typing import Optional

from core.events import BookSnapshot
from ml_engine.risk import round_px

log = logging.getLogger("broker")

TAKER_FEE = 0.00045


@dataclass
class Fill:
    ok: bool
    filled_sz: float = 0.0
    avg_px: float = 0.0
    fee: float = 0.0
    latency_ms: float = 0.0
    oid: Optional[int] = None
    error: str = ""
    raw: dict = field(default_factory=dict)


class Broker:
    dry_run = True

    async def start(self) -> None: ...
    async def equity(self) -> float: raise NotImplementedError
    async def position(self, coin: str) -> tuple[float, float]: raise NotImplementedError
    def sz_decimals(self, coin: str) -> int: return 4
    async def ioc(self, coin: str, is_buy: bool, sz: float, limit_px: float, reduce_only: bool) -> Fill: raise NotImplementedError
    async def trigger(self, coin: str, is_buy: bool, sz: float, trigger_px: float, tpsl: str) -> Fill: raise NotImplementedError
    async def cancel_all(self, coin: str) -> None: ...
    async def closed_pnl_since(self, coin: str, since_ms: int) -> Optional[float]: return None
    def on_book(self, book: BookSnapshot) -> list[tuple[str, str, float]]: return []


# ----------------------------------------------------------------- Paper
class PaperBroker(Broker):
    """Simulation : exécution au meilleur prix opposé, stops sur le mid."""

    dry_run = True

    def __init__(self, equity: float):
        self.cash = equity
        self.books: dict[str, BookSnapshot] = {}
        self.pos: dict[str, list[float]] = {}          # coin -> [signed_sz, entry_px]
        self.triggers: dict[str, list[dict]] = {}

    async def equity(self) -> float:
        eq = self.cash
        for c, (sz, px) in self.pos.items():
            b = self.books.get(c)
            if b is not None and sz:
                eq += sz * (b.mid - px)
        return eq

    async def position(self, coin: str) -> tuple[float, float]:
        sz, px = self.pos.get(coin, [0.0, 0.0])
        return sz, px

    def _apply(self, coin: str, signed: float, px: float) -> float:
        sz, entry = self.pos.get(coin, [0.0, 0.0])
        realized = 0.0
        if sz and math.copysign(1, sz) != math.copysign(1, signed):
            closing = min(abs(sz), abs(signed))
            realized = closing * (px - entry) * math.copysign(1, sz)
            sz_new = sz + signed
            self.pos[coin] = [sz_new, entry if abs(sz_new) > 1e-12 else 0.0]
        else:
            new = sz + signed
            entry = (abs(sz) * entry + abs(signed) * px) / abs(new) if new else 0.0
            self.pos[coin] = [new, entry]
        fee = abs(signed) * px * TAKER_FEE
        self.cash += realized - fee
        if abs(self.pos[coin][0]) < 1e-12:
            self.pos.pop(coin, None)
        return fee

    async def ioc(self, coin, is_buy, sz, limit_px, reduce_only) -> Fill:
        t0 = time.perf_counter()
        b = self.books.get(coin)
        if b is None:
            return Fill(False, error="no book")
        px = b.best_ask if is_buy else b.best_bid
        if (is_buy and px > limit_px) or (not is_buy and px < limit_px):
            return Fill(False, error="IOC not marketable within slippage")
        if reduce_only:
            cur, _ = await self.position(coin)
            sz = min(sz, abs(cur))
            if sz <= 0:
                return Fill(False, error="reduce-only on flat position")
        fee = self._apply(coin, sz if is_buy else -sz, px)
        return Fill(True, sz, px, fee, (time.perf_counter() - t0) * 1000)

    async def trigger(self, coin, is_buy, sz, trigger_px, tpsl) -> Fill:
        self.triggers.setdefault(coin, []).append(
            {"is_buy": is_buy, "sz": sz, "px": trigger_px, "tpsl": tpsl})
        return Fill(True)

    async def cancel_all(self, coin) -> None:
        self.triggers.pop(coin, None)

    def on_book(self, book: BookSnapshot) -> list[tuple[str, str, float]]:
        self.books[book.coin] = book
        hit = []
        for t in list(self.triggers.get(book.coin, [])):
            m = book.mid
            # SL d'un long = vente déclenchée sous le prix ; TP d'un long = vente au-dessus
            sell = not t["is_buy"]
            cond = (m <= t["px"]) if (sell and t["tpsl"] == "sl") or (not sell and t["tpsl"] == "tp") else (m >= t["px"])
            if cond and book.coin in self.pos:
                px = t["px"]
                cur = self.pos[book.coin][0]
                self._apply(book.coin, -cur, px)
                self.triggers.pop(book.coin, None)
                hit.append((book.coin, t["tpsl"], px))
                break
        return hit


# ------------------------------------------------------------ Hyperliquid
class HyperliquidBroker(Broker):
    dry_run = False

    def __init__(self, api_url: str):
        self.api_url = api_url
        self.account = os.environ["HL_ACCOUNT_ADDRESS"]
        self._key = os.environ["HL_API_WALLET_PRIVATE_KEY"]
        self._szd: dict[str, int] = {}
        self.exchange = None
        self.info = None

    async def start(self) -> None:
        from eth_account import Account
        from hyperliquid.exchange import Exchange
        from hyperliquid.info import Info

        wallet = Account.from_key(self._key)
        self.info = Info(self.api_url, skip_ws=True)
        self.exchange = Exchange(wallet, self.api_url, account_address=self.account)
        meta = await asyncio.to_thread(self.info.meta)
        self._szd = {a["name"]: int(a["szDecimals"]) for a in meta["universe"]}
        log.info("hyperliquid broker ready: account=%s api_wallet=%s assets=%d",
                 self.account, wallet.address, len(self._szd))

    def sz_decimals(self, coin: str) -> int:
        return self._szd.get(coin, 4)

    async def _state(self) -> dict:
        return await asyncio.to_thread(self.info.user_state, self.account)

    async def equity(self) -> float:
        st = await self._state()
        return float(st["marginSummary"]["accountValue"])

    async def position(self, coin: str) -> tuple[float, float]:
        st = await self._state()
        for ap in st.get("assetPositions", []):
            p = ap.get("position", {})
            if p.get("coin") == coin:
                return float(p.get("szi") or 0), float(p.get("entryPx") or 0)
        return 0.0, 0.0

    @staticmethod
    def _parse(resp: dict, t0: float) -> Fill:
        lat = (time.perf_counter() - t0) * 1000
        if resp.get("status") != "ok":
            return Fill(False, latency_ms=lat, error=str(resp.get("response")), raw=resp)
        statuses = resp["response"]["data"]["statuses"]
        s = statuses[0] if statuses else {}
        if "filled" in s:
            f = s["filled"]
            sz, px = float(f["totalSz"]), float(f["avgPx"])
            return Fill(True, sz, px, sz * px * TAKER_FEE, lat, f.get("oid"), raw=resp)
        if "resting" in s:
            return Fill(True, latency_ms=lat, oid=s["resting"].get("oid"), raw=resp)
        return Fill(False, latency_ms=lat, error=str(s.get("error", s)), raw=resp)

    async def ioc(self, coin, is_buy, sz, limit_px, reduce_only) -> Fill:
        px = round_px(limit_px, self.sz_decimals(coin))
        t0 = time.perf_counter()
        resp = await asyncio.to_thread(self.exchange.order, coin, is_buy, sz, px,
                                       {"limit": {"tif": "Ioc"}}, reduce_only)
        return self._parse(resp, t0)

    async def trigger(self, coin, is_buy, sz, trigger_px, tpsl) -> Fill:
        px = round_px(trigger_px, self.sz_decimals(coin))
        t0 = time.perf_counter()
        order_type = {"trigger": {"triggerPx": px, "isMarket": True, "tpsl": tpsl}}
        resp = await asyncio.to_thread(self.exchange.order, coin, is_buy, sz, px, order_type, True)
        return self._parse(resp, t0)

    async def cancel_all(self, coin) -> None:
        orders = await asyncio.to_thread(self.info.frontend_open_orders, self.account)
        reqs = [{"coin": o["coin"], "oid": o["oid"]} for o in orders if o.get("coin") == coin]
        if reqs:
            await asyncio.to_thread(self.exchange.bulk_cancel, reqs)

    async def closed_pnl_since(self, coin: str, since_ms: int) -> Optional[float]:
        fills = await asyncio.to_thread(self.info.user_fills, self.account)
        rel = [f for f in fills if f.get("coin") == coin and int(f.get("time", 0)) >= since_ms]
        if not rel:
            return None
        return sum(float(f.get("closedPnl") or 0) - float(f.get("fee") or 0) for f in rel)
