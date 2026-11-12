"""Backtest événementiel : rejoue le flux enregistré à travers EXACTEMENT les
mêmes FeatureEngine / SignalModel / decide / size_position que le live.

Modèle d'exécution (volontairement conservateur) :
- entrée et sortie en taker au meilleur prix opposé + slippage_bps ;
- frais taker Hyperliquid (par défaut 4,5 bps par côté) ;
- stop et take-profit déclenchés sur le mid, exécutés au prix du stop
  dégradé du slippage.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from core.events import BookSnapshot, ExternalQuote, RiskLevel, Side, Trade, AssetCtx
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


@dataclass
class BTResult:
    trades: list[BTTrade] = field(default_factory=list)
    equity_curve: list[tuple[int, float]] = field(default_factory=list)
    start_equity: float = 0.0

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
        return {"trades": self.n_trades, "return_pct": round(self.total_return_pct, 3),
                "max_dd_pct": round(self.max_drawdown_pct, 3), "sharpe": round(self.sharpe, 3),
                "win_rate": round(self.win_rate, 3)}


def run_backtest(records: list[dict], strategy_cfg, risk_cfg, *, equity: float = 10_000.0,
                 fee_bps: float = 4.5, sz_decimals: int = 4, max_staleness_ms: int = 2500) -> BTResult:
    engines: dict[str, FeatureEngine] = {}
    models: dict[str, SignalModel] = {}
    pos: dict[str, dict] = {}
    views: dict[str, PositionView] = {}
    stats = TradeStats(risk_cfg.prior_win_rate, risk_cfg.prior_payoff)
    res = BTResult(start_equity=equity)
    cash = equity
    slip = risk_cfg.slippage_bps / 1e4
    fee = fee_bps / 1e4

    def eng(coin: str) -> FeatureEngine:
        if coin not in engines:
            engines[coin] = FeatureEngine(coin, strategy_cfg, max_staleness_ms)
            models[coin] = SignalModel(strategy_cfg)
            views[coin] = PositionView(last_exit_ts=-10 ** 15)
        return engines[coin]

    def close(coin: str, px: float, ts: int, reason: str) -> None:
        nonlocal cash
        p = pos.pop(coin)
        sign = 1 if p["side"] == Side.LONG else -1
        pnl = sign * (px - p["px"]) * p["qty"] - fee * px * p["qty"]
        cash += pnl
        stats.add(pnl / (p["risk"] or 1))
        res.trades.append(BTTrade(coin, p["side"].value, p["ts"], ts, p["px"], px, p["qty"], pnl, reason))
        views[coin].side = Side.FLAT
        views[coin].last_exit_ts = ts

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
            continue
        if not isinstance(ev, BookSnapshot) or not len(ev.bids) or not len(ev.asks):
            continue
        f = e.on_book(ev, now_ms=ev.exch_ts)
        coin, ts, mid = ev.coin, ev.exch_ts, f.mid
        # stops / TP
        if coin in pos:
            p = pos[coin]
            long_ = p["side"] == Side.LONG
            if (long_ and mid <= p["stop"]) or (not long_ and mid >= p["stop"]):
                close(coin, p["stop"] * (1 - slip if long_ else 1 + slip), ts, "stop")
            elif (long_ and mid >= p["tp"]) or (not long_ and mid <= p["tp"]):
                close(coin, p["tp"], ts, "tp")
        side, score = models[coin].update(f)
        if f.spread_bps > strategy_cfg.max_spread_bps:
            side = Side.FLAT
        act = decide(side, score, views[coin], ts, strategy_cfg)
        if act == Action.EXIT and coin in pos:
            long_ = pos[coin]["side"] == Side.LONG
            close(coin, (ev.best_bid * (1 - slip)) if long_ else (ev.best_ask * (1 + slip)), ts, "signal")
        elif act in (Action.ENTER_LONG, Action.ENTER_SHORT) and coin not in pos:
            long_ = act == Action.ENTER_LONG
            px = ev.best_ask * (1 + slip) if long_ else ev.best_bid * (1 - slip)
            d = size_position(equity=cash, px=px, is_long=long_, vol_bps=f.realized_vol_bps,
                              stats=stats, cfg=risk_cfg, level=RiskLevel.NORMAL, sz_decimals=sz_decimals)
            if d.qty > 0:
                cash -= fee * px * d.qty
                pos[coin] = {"side": Side.LONG if long_ else Side.SHORT, "px": px, "qty": d.qty,
                             "stop": d.stop_px, "tp": d.tp_px, "ts": ts, "risk": d.risk_usd}
                views[coin].side = pos[coin]["side"]
                views[coin].entry_ts = ts
        # mark-to-market
        mtm = cash
        for c, p in pos.items():
            m = engines[c]._prev_mid[1] if engines[c]._prev_mid else p["px"]
            mtm += (1 if p["side"] == Side.LONG else -1) * (m - p["px"]) * p["qty"]
        res.equity_curve.append((ts, mtm))

    # clôture finale au dernier mid
    for coin in list(pos):
        m = engines[coin]._prev_mid[1]
        close(coin, m, res.equity_curve[-1][0] if res.equity_curve else 0, "end")
    if res.equity_curve:
        res.equity_curve.append((res.equity_curve[-1][0] + 1, cash))
    return res
