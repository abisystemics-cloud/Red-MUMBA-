"""Backtest événementiel : rejoue le flux enregistré à travers EXACTEMENT les
mêmes FeatureEngine / SignalModel / decide / size_position que le live.

Modèle d'exécution (volontairement conservateur) :
- mode `maker` : ordre posté au meilleur prix de son côté ; exécuté seulement si
  le prix TRAVERSE ce niveau (hypothèse pessimiste sur la file d'attente) ;
  replacé si le marché s'éloigne de `requote_bps` (au plus `max_requotes`
  fois), abandonné après `maker_timeout_s`. Les sorties tentent le maker
  pendant `exit_maker_timeout_s` puis passent en taker ;
- mode `taker` : entrée/sortie au meilleur prix opposé + slippage ;
- stop et take-profit déclenchés sur le mid, exécutés en taker ;
- funding Hyperliquid (taux horaire) payé/reçu au prorata du temps de détention.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from core.config import ExecutionCfg
from core.events import (AssetCtx, BookSnapshot, ExternalQuote, LiquidationMap, RiskLevel,
                         Side, Trade, WhaleBias)
from ml_engine.features import FeatureEngine
from ml_engine.recorder import to_event
from ml_engine.risk import TradeStats, size_position
from ml_engine.strategy import Action, PositionView, SignalModel, decide


@dataclass
class BTTrade:
    coin: str
    side: str
    entry_ts: int
    exit_ts: int
    entry_px: float
    exit_px: float
    qty: float
    pnl: float
    reason: str
    fees: float = 0.0
    funding: float = 0.0


@dataclass
class BTResult:
    trades: list[BTTrade] = field(default_factory=list)
    equity_curve: list[tuple[int, float]] = field(default_factory=list)
    start_equity: float = 0.0
    maker_attempts: int = 0
    maker_fills: int = 0

    @property
    def n_trades(self) -> int:
        return len(self.trades)

    @property
    def final_equity(self) -> float:
        return self.equity_curve[-1][1] if self.equity_curve else self.start_equity

    @property
    def total_return_pct(self) -> float:
        return (self.final_equity / self.start_equity - 1) * 100 if self.start_equity else 0.0

    @property
    def max_drawdown_pct(self) -> float:
        if not self.equity_curve:
            return 0.0
        eq = np.array([e for _, e in self.equity_curve])
        peak = np.maximum.accumulate(eq)
        return float(((peak - eq) / peak).max() * 100)

    @property
    def win_rate(self) -> float:
        return sum(t.pnl > 0 for t in self.trades) / self.n_trades if self.trades else 0.0

    @property
    def profit_factor(self) -> float:
        gains = sum(t.pnl for t in self.trades if t.pnl > 0)
        losses = -sum(t.pnl for t in self.trades if t.pnl < 0)
        return gains / losses if losses > 0 else (float("inf") if gains > 0 else 0.0)

    @property
    def sharpe(self) -> float:
        """Sharpe annualisé sur rendements par minute de la courbe d'equity."""
        if len(self.equity_curve) < 3:
            return 0.0
        ts = np.array([t for t, _ in self.equity_curve], dtype=float)
        eq = np.array([e for _, e in self.equity_curve], dtype=float)
        grid = np.arange(ts[0], ts[-1], 60_000.0)
        if len(grid) < 3:
            return 0.0
        idx = np.searchsorted(ts, grid, side="right") - 1
        r = np.diff(eq[idx]) / eq[idx][:-1]
        sd = r.std()
        return float(r.mean() / sd * math.sqrt(525_600)) if sd > 0 else 0.0

    def summary(self) -> dict:
        pf = self.profit_factor
        return {"trades": self.n_trades, "return_pct": round(self.total_return_pct, 3),
                "max_dd_pct": round(self.max_drawdown_pct, 3), "sharpe": round(self.sharpe, 3),
                "win_rate": round(self.win_rate, 3),
                "profit_factor": round(pf, 3) if math.isfinite(pf) else None,
                "maker_fill_rate": round(self.maker_fills / self.maker_attempts, 3) if self.maker_attempts else None}


@dataclass
class _Pending:
    kind: str            # entry | exit
    is_buy: bool
    px: float
    sz: float
    deadline: int
    requotes: int = 0
    size: object = None  # SizeDecision pour une entrée


def run_backtest(records: list[dict], strategy_cfg, risk_cfg, *, exec_cfg: Optional[ExecutionCfg] = None,
                 equity: float = 10_000.0, sz_decimals: int = 4, max_staleness_ms: int = 2500) -> BTResult:
    ec = exec_cfg or ExecutionCfg()
    maker = ec.mode == "maker"
    engines: dict[str, FeatureEngine] = {}
    models: dict[str, SignalModel] = {}
    pos: dict[str, dict] = {}
    pend: dict[str, _Pending] = {}
    views: dict[str, PositionView] = {}
    funding: dict[str, float] = {}
    last_ts: dict[str, int] = {}
    stats = TradeStats(risk_cfg.prior_win_rate, risk_cfg.prior_payoff)
    res = BTResult(start_equity=equity)
    cash = equity
    slip = risk_cfg.slippage_bps / 1e4
    f_taker, f_maker = ec.taker_fee_bps / 1e4, ec.maker_fee_bps / 1e4

    def eng(coin: str) -> FeatureEngine:
        if coin not in engines:
            engines[coin] = FeatureEngine(coin, strategy_cfg, max_staleness_ms)
            models[coin] = SignalModel(strategy_cfg)
            views[coin] = PositionView(last_exit_ts=-10 ** 15)
        return engines[coin]

    def open_pos(coin: str, long_: bool, px: float, qty: float, d, ts: int, fee_rate: float) -> None:
        nonlocal cash
        fee = fee_rate * px * qty
        cash -= fee
        sign = 1 if long_ else -1
        pos[coin] = {"side": Side.LONG if long_ else Side.SHORT, "px": px, "qty": qty,
                     "stop": px * (1 - sign * d.stop_bps / 1e4),
                     "tp": px * (1 + sign * d.stop_bps * risk_cfg.take_profit_r / 1e4),
                     "ts": ts, "risk": d.risk_usd, "fees": fee, "funding": 0.0}
        views[coin].side, views[coin].entry_ts = pos[coin]["side"], ts

    def close(coin: str, px: float, ts: int, reason: str, fee_rate: float) -> None:
        nonlocal cash
        p = pos.pop(coin)
        pend.pop(coin, None)
        sign = 1 if p["side"] == Side.LONG else -1
        fee = fee_rate * px * p["qty"]
        gross = sign * (px - p["px"]) * p["qty"]
        cash += gross - fee
        pnl = gross - fee - p["fees"] - p["funding"]
        stats.add(pnl / (p["risk"] or 1))
        res.trades.append(BTTrade(coin, p["side"].value, p["ts"], ts, p["px"], px, p["qty"], pnl, reason,
                                  p["fees"] + fee, p["funding"]))
        views[coin].side, views[coin].last_exit_ts = Side.FLAT, ts

    for rec in records:
        ev = to_event(rec)
        if ev is None:
            continue
        e = eng(ev.coin)
        if isinstance(ev, Trade):
            e.on_trade(ev)
            continue
        if isinstance(ev, ExternalQuote):
            e.on_ext(ev)
            continue
        if isinstance(ev, AssetCtx):
            e.on_ctx(ev)
            funding[ev.coin] = ev.funding
            continue
        if isinstance(ev, WhaleBias):
            e.on_whale(ev)
            continue
        if isinstance(ev, LiquidationMap):
            e.on_liq(ev)
            continue
        if not isinstance(ev, BookSnapshot) or not len(ev.bids) or not len(ev.asks):
            continue
        f = e.on_book(ev, now_ms=ev.exch_ts)
        coin, ts, mid = ev.coin, ev.exch_ts, f.mid
        bid, ask = ev.best_bid, ev.best_ask

        # funding couru (taux horaire, payé par les longs s'il est positif)
        if coin in pos and coin in last_ts:
            p = pos[coin]
            dt_h = (ts - last_ts[coin]) / 3_600_000
            pay = (1 if p["side"] == Side.LONG else -1) * funding.get(coin, 0.0) * p["qty"] * mid * dt_h
            p["funding"] += pay
            cash -= pay
        last_ts[coin] = ts

        # ordres maker en attente
        o = pend.get(coin)
        if o is not None:
            if (o.is_buy and ask <= o.px) or (not o.is_buy and bid >= o.px):
                res.maker_fills += 1
                pend.pop(coin)
                if o.kind == "entry":
                    open_pos(coin, o.is_buy, o.px, o.sz, o.size, ts, f_maker)
                elif coin in pos:
                    close(coin, o.px, ts, "signal_maker", f_maker)
            elif ts >= o.deadline:
                pend.pop(coin)
                if o.kind == "exit" and coin in pos:
                    long_ = pos[coin]["side"] == Side.LONG
                    close(coin, bid * (1 - slip) if long_ else ask * (1 + slip), ts, "signal_taker", f_taker)
                elif o.kind == "entry":
                    views[coin].last_exit_ts = ts  # cooldown après un échec d'entrée
            else:
                best = bid if o.is_buy else ask
                away = (best - o.px) / o.px * 1e4 if o.is_buy else (o.px - best) / o.px * 1e4
                if away > ec.requote_bps and o.requotes < ec.max_requotes:
                    o.px, o.requotes = best, o.requotes + 1
                    res.maker_attempts += 1

        # stops / TP (taker)
        if coin in pos:
            p = pos[coin]
            long_ = p["side"] == Side.LONG
            if (long_ and mid <= p["stop"]) or (not long_ and mid >= p["stop"]):
                close(coin, p["stop"] * (1 - slip if long_ else 1 + slip), ts, "stop", f_taker)
            elif (long_ and mid >= p["tp"]) or (not long_ and mid <= p["tp"]):
                close(coin, p["tp"], ts, "tp", f_taker)

        side, score = models[coin].update(f)
        if f.spread_bps > strategy_cfg.max_spread_bps:
            side = Side.FLAT
        if coin in pend:
            pass  # un ordre travaille déjà sur ce marché
        else:
            act = decide(side, score, views[coin], ts, strategy_cfg)
            if act == Action.EXIT and coin in pos:
                long_ = pos[coin]["side"] == Side.LONG
                if maker:
                    pend[coin] = _Pending("exit", not long_, ask if long_ else bid, pos[coin]["qty"],
                                          ts + int(ec.exit_maker_timeout_s * 1000))
                    res.maker_attempts += 1
                else:
                    close(coin, bid * (1 - slip) if long_ else ask * (1 + slip), ts, "signal", f_taker)
            elif act in (Action.ENTER_LONG, Action.ENTER_SHORT) and coin not in pos:
                long_ = act == Action.ENTER_LONG
                ref = bid if (maker and long_) else ask if maker else (ask * (1 + slip) if long_ else bid * (1 - slip))
                d = size_position(equity=cash, px=ref, is_long=long_, vol_bps=f.realized_vol_bps,
                                  stats=stats, cfg=risk_cfg, level=RiskLevel.NORMAL, sz_decimals=sz_decimals)
                if d.qty > 0:
                    if maker:
                        pend[coin] = _Pending("entry", long_, ref, d.qty, ts + int(ec.maker_timeout_s * 1000),
                                              size=d)
                        res.maker_attempts += 1
                    else:
                        open_pos(coin, long_, ref, d.qty, d, ts, f_taker)

        # mark-to-market
        mtm = cash
        for c, p in pos.items():
            m = engines[c]._prev_mid[1] if engines[c]._prev_mid else p["px"]
            mtm += (1 if p["side"] == Side.LONG else -1) * (m - p["px"]) * p["qty"]
        res.equity_curve.append((ts, mtm))

    # clôture finale au dernier mid (taker)
    for coin in list(pos):
        close(coin, engines[coin]._prev_mid[1], res.equity_curve[-1][0] if res.equity_curve else 0, "end", f_taker)
    if res.equity_curve:
        res.equity_curve.append((res.equity_curve[-1][0] + 1, cash))
    return res
