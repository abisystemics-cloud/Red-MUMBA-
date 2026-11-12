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
MAKER_FEE = 0.00015


@dataclass
class OrderStatus:
    status: str          # open | filled | canceled | rejected | unknown
    filled_sz: float
    avg_px: float


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
    async def post_only(self, coin: str, is_buy: bool, sz: float, px: float, reduce_only: bool) -> Fill: raise NotImplementedError
    async def order_status(self, coin: str, oid: int) -> OrderStatus: raise NotImplementedError
    async def cancel(self, coin: str, oid: int) -> None: ...
    async def closed_pnl_since(self, coin: str, since_ms: int) -> Optional[float]: return None
    def on_book(self, book: BookSnapshot) -> list[tuple[str, str, float]]: return []


# ----------------------------------------------------------------- Paper
class PaperBroker(Broker):
    """Simulation : exécution au meilleur prix opposé, stops sur le mid."""

    dry_run = True

    def __init__(self, equity: float, maker_fee: float = MAKER_FEE, taker_fee: float = TAKER_FEE):
        self.maker_fee, self.taker_fee = maker_fee, taker_fee
        self.resting: dict[int, dict] = {}
        self._oid = 0
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

    def _apply(self, coin: str, signed: float, px: float, fee_rate: float | None = None) -> float:
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
        fee = abs(signed) * px * (self.taker_fee if fee_rate is None else fee_rate)
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

    async def post_only(self, coin, is_buy, sz, px, reduce_only) -> Fill:
        b = self.books.get(coin)
        if b is None:
            return Fill(False, error="no book")
        if (is_buy and px >= b.best_ask) or (not is_buy and px <= b.best_bid):
            return Fill(False, error="post-only would cross")
        self._oid += 1
        self.resting[self._oid] = {"coin": coin, "is_buy": is_buy, "sz": sz, "px": px,
                                   "reduce_only": reduce_only, "status": "open", "filled": 0.0}
        return Fill(True, oid=self._oid)

    async def order_status(self, coin, oid) -> OrderStatus:
        o = self.resting.get(oid)
        if o is None:
            return OrderStatus("unknown", 0.0, 0.0)
        return OrderStatus(o["status"], o["filled"], o["px"])

    async def cancel(self, coin, oid) -> None:
        o = self.resting.get(oid)
        if o and o["status"] == "open":
            o["status"] = "canceled"

    def _match_resting(self, book: BookSnapshot) -> None:
        """Hypothèse prudente sur la file d'attente : un ordre maker n'est exécuté
        que si le prix TRAVERSE son niveau (ask ≤ notre bid, ou bid ≥ notre ask)."""
        for o in self.resting.values():
            if o["status"] != "open" or o["coin"] != book.coin:
                continue
            hit = book.best_ask <= o["px"] if o["is_buy"] else book.best_bid >= o["px"]
            if not hit:
                continue
            sz = o["sz"]
            if o["reduce_only"]:
                cur = self.pos.get(book.coin, [0.0, 0.0])[0]
                sz = min(sz, abs(cur))
            if sz > 0:
                self._apply(book.coin, sz if o["is_buy"] else -sz, o["px"], self.maker_fee)
            o["filled"], o["status"] = sz, "filled"

    async def trigger(self, coin, is_buy, sz, trigger_px, tpsl) -> Fill:
        self.triggers.setdefault(coin, []).append(
            {"is_buy": is_buy, "sz": sz, "px": trigger_px, "tpsl": tpsl})
        return Fill(True)

    async def cancel_all(self, coin) -> None:
        self.triggers.pop(coin, None)
        for o in self.resting.values():
            if o["coin"] == coin and o["status"] == "open":
                o["status"] = "canceled"

    def on_book(self, book: BookSnapshot) -> list[tuple[str, str, float]]:
        self.books[book.coin] = book
        self._match_resting(book)
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

    async def post_only(self, coin, is_buy, sz, px, reduce_only) -> Fill:
        px = round_px(px, self.sz_decimals(coin))
        t0 = time.perf_counter()
        resp = await asyncio.to_thread(self.exchange.order, coin, is_buy, sz, px,
                                       {"limit": {"tif": "Alo"}}, reduce_only)
        f = self._parse(resp, t0)
        if f.ok and f.filled_sz:  # ne devrait pas arriver avec ALO
            f.fee = f.filled_sz * f.avg_px * MAKER_FEE
        return f

    async def order_status(self, coin, oid) -> OrderStatus:
        r = await asyncio.to_thread(self.info.query_order_by_oid, self.account, oid)
        o = (r or {}).get("order") or {}
        st = o.get("status", "unknown")
        od = o.get("order") or {}
        orig, left = float(od.get("origSz") or 0), float(od.get("sz") or 0)
        status = {"open": "open", "filled": "filled"}.get(st, "canceled" if "cancel" in st else st)
        return OrderStatus(status, max(0.0, orig - left), float(od.get("limitPx") or 0))

    async def cancel(self, coin, oid) -> None:
        await asyncio.to_thread(self.exchange.cancel, coin, oid)

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
