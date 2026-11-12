"""Agent 5 — L1 Execution & Risk Agent (le sniper).

Pour chaque signal validé :
1. `decide()` (politique partagée avec le backtest) → ENTER / EXIT / HOLD.
2. Entrée : taille = Kelly fractionnel borné × stop dynamique fondé sur la
   variance (ml_engine.risk). En mode `maker` (défaut) : ordre post-only (ALO)
   au meilleur prix, replacé si le marché s'éloigne, abandonné après
   `maker_timeout_s` ; en mode `taker` : IOC limité à `slippage_bps`.
   Puis pose immédiate d'un stop-loss et d'un take-profit *reduce-only* côté
   exchange (le stop vit sur Hyperliquid : il protège même si ce process meurt).
3. Sortie : tentative maker courte (les stops restent en place pendant ce
   temps), puis annulation des triggers et IOC reduce-only pour le reliquat.

Garde-fous : HALT macro → aucune entrée (+ flatten si configuré) ; disjoncteur
perte journalière / pertes consécutives ; un verrou par marché ; réconciliation
périodique avec la position réelle sur l'exchange.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass
from typing import Optional

from agents.base import BaseAgent
from agents.brokers import Broker, Fill
from core.events import (BookSnapshot, FillEvent, MacroState, OrderEvent, RiskLevel,
                         Side, Signal, Topic, now_ms)
from ml_engine.risk import CircuitBreaker, TradeStats, size_position
from ml_engine.strategy import Action, PositionView, decide


@dataclass
class OpenTrade:
    side: Side
    qty: float
    entry_px: float
    entry_ts: int
    risk_usd: float
    stop_px: float
    tp_px: float
    fees: float


class ExecutionAgent(BaseAgent):
    name = "execution"

    def __init__(self, bus, store, broker: Broker):
        super().__init__(bus, store)
        self.broker = broker
        r = self.cfg.risk
        self.stats = TradeStats(r.prior_win_rate, r.prior_payoff)
        self.breaker = CircuitBreaker(r.daily_loss_limit_pct, r.max_consecutive_losses)
        self.views = {m.coin: PositionView(last_exit_ts=0) for m in self.cfg.markets}
        self.open: dict[str, OpenTrade] = {}
        self.locks = {m.coin: asyncio.Lock() for m in self.cfg.markets}
        self.books: dict[str, BookSnapshot] = {}
        self.macro: Optional[MacroState] = None
        self.equity = r.paper_equity_usd
        self.sig_sub = bus.subscribe(Topic.VALIDATED, self.name, maxsize=64)
        self.risk_sub = bus.subscribe(Topic.RISK_STATE, self.name, maxsize=64)
        self.book_sub = bus.subscribe(Topic.BOOK, self.name, maxsize=64)
        self.realized_pnl = 0.0
        self._stop = asyncio.Event()
        self._breaker_reported = False

    # --------------------------------------------------------------- utils
    @property
    def level(self) -> RiskLevel:
        if self.breaker.tripped:
            return RiskLevel.HALT
        return self.macro.level if self.macro else RiskLevel.HALT

    def _tele(self, **kw) -> None:
        self.bus.publish(Topic.TELEMETRY, kw)

    def _order_event(self, coin, side, size, px, kind, fill: Fill) -> None:
        ev = OrderEvent(coin, now_ms(), side, size, px, kind, uuid.uuid4().hex[:12],
                        "filled" if fill.ok and fill.filled_sz else ("accepted" if fill.ok else "rejected"),
                        fill.latency_ms, {"error": fill.error} if fill.error else {})
        self.bus.publish(Topic.ORDER, ev)
        self._tele(event="order", coin=coin, side=side.value, kind=kind, size=size, limit_px=px,
                   status=ev.status, latency_ms=round(fill.latency_ms, 3), error=fill.error or None,
                   dry_run=self.broker.dry_run)

    # ------------------------------------------------------------ actions
    async def _enter(self, sig: Signal, long_: bool) -> None:
        coin, f, r = sig.coin, sig.features, self.cfg.risk
        book = self.books.get(coin)
        if book is None:
            return
        ref = book.best_ask if long_ else book.best_bid
        d = size_position(equity=self.equity, px=ref, is_long=long_, vol_bps=f.realized_vol_bps,
                          stats=self.stats, cfg=r, level=self.level,
                          sz_decimals=self.broker.sz_decimals(coin))
        if d.qty <= 0:
            self.log.info("%s entry skipped: %s", coin, d.reason or "size rounds to 0")
            return
        side = Side.LONG if long_ else Side.SHORT
        if self.cfg.execution.mode == "maker":
            fill = await self._work_maker(coin, long_, d.qty, self.cfg.execution.maker_timeout_s, False)
            self._order_event(coin, side, d.qty, ref, "entry_maker", fill)
        else:
            limit = ref * (1 + r.slippage_bps / 1e4) if long_ else ref * (1 - r.slippage_bps / 1e4)
            fill = await self.broker.ioc(coin, long_, d.qty, limit, reduce_only=False)
            self._order_event(coin, side, d.qty, limit, "entry", fill)
        if not (fill.ok and fill.filled_sz > 0):
            return
        sign = 1 if long_ else -1
        stop_px = fill.avg_px * (1 - sign * d.stop_bps / 1e4)
        tp_px = fill.avg_px * (1 + sign * d.stop_bps * r.take_profit_r / 1e4)
        sl = await self.broker.trigger(coin, not long_, fill.filled_sz, stop_px, "sl")
        tp = await self.broker.trigger(coin, not long_, fill.filled_sz, tp_px, "tp")
        self._order_event(coin, side, fill.filled_sz, stop_px, "stop", sl)
        self._order_event(coin, side, fill.filled_sz, tp_px, "tp", tp)
        if not sl.ok:
            self.log.error("%s STOP-LOSS REJECTED (%s) → closing position immediately", coin, sl.error)
            self.open[coin] = OpenTrade(side, fill.filled_sz, fill.avg_px, now_ms(), d.risk_usd,
                                        stop_px, tp_px, fill.fee)
            self.views[coin].side, self.views[coin].entry_ts = side, now_ms()
            await self._exit(coin, "stop_rejected")
            return
        self.open[coin] = OpenTrade(side, fill.filled_sz, fill.avg_px, now_ms(), d.risk_usd, stop_px, tp_px, fill.fee)
        self.views[coin].side, self.views[coin].entry_ts = side, now_ms()
        if self._stop.is_set():  # arrêt demandé pendant que l'ordre travaillait
            await self._exit(coin, "shutdown")
            return
        slip = (fill.avg_px / ref - 1) * 1e4 * sign
        self.bus.publish(Topic.FILL, FillEvent(coin, now_ms(), side, fill.filled_sz, fill.avg_px, fill.fee,
                                               ref, slip, 0.0, "entry", self.broker.dry_run))
        self._tele(event="fill", coin=coin, kind="entry", side=side.value, size=fill.filled_sz,
                   px=fill.avg_px, expected_px=ref, slippage_bps=round(slip, 3), fee=fill.fee,
                   stop_bps=round(d.stop_bps, 2), kelly_raw=round(d.kelly_raw, 4),
                   kelly_used=round(d.kelly_used, 5), risk_usd=round(d.risk_usd, 2),
                   signal_score=round(sig.score, 3), decision_latency_ms=round(fill.latency_ms, 3),
                   dry_run=self.broker.dry_run)

    async def _work_maker(self, coin: str, is_buy: bool, sz: float, timeout_s: float,
                          reduce_only: bool) -> Fill:
        """Travaille un ordre post-only au meilleur prix de son côté : replacé si
        le marché s'éloigne de plus de `requote_bps`, annulé à l'échéance.
        Retourne la quantité réellement exécutée (éventuellement partielle)."""
        ec = self.cfg.execution
        szd = self.broker.sz_decimals(coin)
        filled = notional = 0.0
        requotes = 0
        t0 = time.perf_counter()
        deadline = time.monotonic() + timeout_s
        last_err = ""
        while (filled < sz - 1e-12 and time.monotonic() < deadline and requotes <= ec.max_requotes
               and not self._stop.is_set()):
            book = self.books.get(coin)
            if book is None:
                break
            px = book.best_bid if is_buy else book.best_ask
            f = await self.broker.post_only(coin, is_buy, round(sz - filled, szd), px, reduce_only)
            if not f.ok or f.oid is None:
                last_err = f.error or "post-only rejected"
                requotes += 1
                await asyncio.sleep(0.2)
                continue
            while time.monotonic() < deadline and not self._stop.is_set():
                await asyncio.sleep(0.25)
                st = await self.broker.order_status(coin, f.oid)
                if st.status != "open":
                    break
                b = self.books.get(coin)
                best = (b.best_bid if is_buy else b.best_ask) if b else px
                away = (best - px) / px * 1e4 if is_buy else (px - best) / px * 1e4
                if away > ec.requote_bps and requotes < ec.max_requotes:
                    break
            await self.broker.cancel(coin, f.oid)
            st = await self.broker.order_status(coin, f.oid)
            if st.filled_sz > 0:
                filled += st.filled_sz
                notional += st.filled_sz * (st.avg_px or px)
            if st.status != "filled":
                requotes += 1
        avg = notional / filled if filled else 0.0
        fee = notional * ec.maker_fee_bps / 1e4
        return Fill(filled > 0, round(filled, szd), avg, fee, (time.perf_counter() - t0) * 1000,
                    error="" if filled else (last_err or "maker order not filled before timeout"))

    async def _exit(self, coin: str, reason: str) -> None:
        t = self.open.get(coin)
        if t is None:
            return
        long_ = t.side == Side.LONG
        qty_done = notional = fees = 0.0
        ref_book = self.books.get(coin)
        ref = (ref_book.best_bid if long_ else ref_book.best_ask) if ref_book else t.entry_px
        urgent = reason in ("macro_halt", "circuit_breaker", "shutdown", "stop_rejected")
        if self.cfg.execution.mode == "maker" and not urgent:
            mf = await self._work_maker(coin, not long_, t.qty, self.cfg.execution.exit_maker_timeout_s, True)
            self._order_event(coin, t.side, t.qty, ref, "exit_maker", mf)
            qty_done, notional, fees = mf.filled_sz, mf.filled_sz * mf.avg_px, mf.fee
            if coin not in self.open:  # stop/TP déclenché pendant la tentative
                await self.broker.cancel_all(coin)
                return
        await self.broker.cancel_all(coin)
        remaining = round(t.qty - qty_done, self.broker.sz_decimals(coin))
        if remaining > 0:
            pos_sz, _ = await self.broker.position(coin)
            remaining = min(remaining, abs(pos_sz))
        if remaining > 0:
            book = self.books.get(coin)
            px_ref = (book.best_bid if long_ else book.best_ask) if book else t.entry_px
            slip = self.cfg.risk.slippage_bps * 3 / 1e4  # sortie : on accepte plus de slippage
            limit = px_ref * (1 - slip) if long_ else px_ref * (1 + slip)
            fill = await self.broker.ioc(coin, not long_, remaining, limit, reduce_only=True)
            self._order_event(coin, t.side, remaining, limit, "exit", fill)
            if not (fill.ok and fill.filled_sz > 0):
                if qty_done <= 0:
                    self.log.error("%s exit failed (%s) — will retry on next tick", coin, fill.error)
                    return
            else:
                qty_done += fill.filled_sz
                notional += fill.filled_sz * fill.avg_px
                fees += fill.fee
        if qty_done <= 0:
            # position déjà fermée côté exchange (stop/TP touché pendant la tentative)
            b = self.books.get(coin)
            self._close_bookkeeping(coin, (await self.broker.closed_pnl_since(coin, t.entry_ts)) or 0.0,
                                    b.mid if b else t.entry_px, "exchange_trigger")
            return
        avg = notional / qty_done
        sign = 1 if long_ else -1
        pnl = sign * (avg - t.entry_px) * qty_done - fees - t.fees
        slip_bps = (ref / avg - 1) * 1e4 * sign if avg else 0.0
        self._close_bookkeeping(coin, pnl, avg, reason, slip_bps, ref)

    def _close_bookkeeping(self, coin: str, pnl: float, px: float, reason: str,
                           slip_bps: float = 0.0, ref: float = 0.0) -> None:
        t = self.open.pop(coin, None)
        if t is None:  # déjà clôturé (ex. stop touché pendant une sortie maker)
            return
        self.realized_pnl += pnl
        self.stats.add(pnl / t.risk_usd if t.risk_usd else 0.0)
        self.breaker.on_trade_closed(pnl)
        v = self.views[coin]
        v.side, v.last_exit_ts = Side.FLAT, now_ms()
        self.bus.publish(Topic.FILL, FillEvent(coin, now_ms(), t.side, t.qty, px, 0.0, ref or px,
                                               slip_bps, pnl, "exit", self.broker.dry_run))
        self._tele(event="trade_closed", coin=coin, side=t.side.value, reason=reason,
                   entry_px=t.entry_px, exit_px=px, size=t.qty, pnl=round(pnl, 4),
                   r_multiple=round(pnl / t.risk_usd, 3) if t.risk_usd else None,
                   hold_s=round((now_ms() - t.entry_ts) / 1000, 1), slippage_bps=round(slip_bps, 3),
                   realized_pnl_total=round(self.realized_pnl, 4), dry_run=self.broker.dry_run)
        self.log.info("%s closed %s (%s) pnl=%.4f", coin, t.side.value, reason, pnl)

    async def flatten_all(self, reason: str) -> None:
        for coin in list(self.open):
            async with self.locks[coin]:
                await self._exit(coin, reason)

    # ------------------------------------------------------------- loops
    async def _on_signal(self, sig: Signal) -> None:
        coin = sig.coin
        if coin not in self.locks or self.locks[coin].locked():
            return
        async with self.locks[coin]:
            if sig.features.book_age_ms > self.cfg.data.max_staleness_ms:
                return
            side = sig.side if sig.validated else Side.FLAT
            if sig.side != Side.FLAT and not sig.validated and coin not in self.open:
                return
            act = decide(side, sig.score, self.views[coin], now_ms(), self.cfg.strategy)
            if act == Action.EXIT and coin in self.open:
                await self._exit(coin, "signal")
            elif act in (Action.ENTER_LONG, Action.ENTER_SHORT) and coin not in self.open:
                if self.level == RiskLevel.HALT or self._stop.is_set():
                    return
                await self._enter(sig, act == Action.ENTER_LONG)

    async def _books(self) -> None:
        while True:
            b: BookSnapshot = await self.book_sub.get()
            self.books[b.coin] = b
            for coin, kind, px in self.broker.on_book(b):  # stops simulés (paper)
                if coin in self.open:
                    t = self.open[coin]
                    sign = 1 if t.side == Side.LONG else -1
                    pnl = sign * (px - t.entry_px) * t.qty - t.fees - px * t.qty * 0.00045
                    self._close_bookkeeping(coin, pnl, px, kind)

    async def _risk(self) -> None:
        while True:
            st: MacroState = await self.risk_sub.get()
            prev = self.macro.level if self.macro else None
            self.macro = st
            if st.level == RiskLevel.HALT and prev != RiskLevel.HALT and self.cfg.risk.flatten_on_halt and self.open:
                self.log.warning("HALT received → flattening all positions")
                await self.flatten_all("macro_halt")

    async def _reconcile(self, stop: asyncio.Event) -> None:
        """Toutes les 5 s : equity, disjoncteur, et positions fermées côté
        exchange (stop/TP touché) ou divergentes."""
        while not stop.is_set():
            try:
                self.equity = await self.broker.equity()
                self.breaker.on_equity(self.equity, now_ms())
                if self.breaker.tripped and not self._breaker_reported:
                    self._breaker_reported = True
                    self._tele(event="breaker", reason=self.breaker.tripped_reason)
                elif not self.breaker.tripped:
                    self._breaker_reported = False
                if self.breaker.tripped and self.open:
                    self.log.error("circuit breaker: %s → flatten", self.breaker.tripped_reason)
                    await self.flatten_all("circuit_breaker")
                if not self.broker.dry_run:
                    for coin, t in list(self.open.items()):
                        async with self.locks[coin]:
                            sz, _ = await self.broker.position(coin)
                            if abs(sz) < 1e-12 and coin in self.open:
                                pnl = await self.broker.closed_pnl_since(coin, t.entry_ts)
                                b = self.books.get(coin)
                                self._close_bookkeeping(coin, pnl if pnl is not None else 0.0,
                                                        b.mid if b else t.entry_px, "exchange_trigger")
                self._tele(event="equity", equity=round(self.equity, 4), realized_pnl=round(self.realized_pnl, 4),
                           open_positions=len(self.open), level=self.level.value,
                           breaker=self.breaker.tripped_reason or None, dry_run=self.broker.dry_run)
                self.beat()
            except Exception as exc:  # noqa: BLE001
                self.errors += 1
                self.log.warning("reconcile failed: %s", exc)
            try:
                await asyncio.wait_for(stop.wait(), timeout=5)
            except asyncio.TimeoutError:
                pass

    async def run(self, stop: asyncio.Event) -> None:
        self._stop = stop
        await self.broker.start()
        self.equity = await self.broker.equity()
        tasks = [asyncio.create_task(c) for c in (self._books(), self._risk(), self._reconcile(stop))]
        try:
            while not stop.is_set():
                try:
                    sig = await asyncio.wait_for(self.sig_sub.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                try:
                    await self._on_signal(sig)
                except Exception:  # noqa: BLE001
                    self.errors += 1
                    self.log.exception("execution error on %s", sig.coin)
        finally:
            for t in tasks:
                t.cancel()

    async def shutdown(self) -> None:
        if self.cfg.risk.flatten_on_halt and self.open:
            self.log.warning("shutdown → flattening %d positions", len(self.open))
            await self.flatten_all("shutdown")

    def health(self) -> dict:
        h = super().health()
        h.update(equity=round(self.equity, 2), realized_pnl=round(self.realized_pnl, 4),
                 open={c: {"side": t.side.value, "qty": t.qty, "entry": t.entry_px} for c, t in self.open.items()},
                 level=self.level.value, breaker=self.breaker.tripped_reason or None,
                 win_rate_est=round(self.stats.win_rate(), 3), payoff_est=round(self.stats.payoff(), 3),
                 dry_run=self.broker.dry_run)
        return h
