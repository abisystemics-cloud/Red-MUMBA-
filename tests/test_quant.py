import numpy as np
import pytest

from core.config import load_config
from core.events import BookSnapshot, MacroState, RiskLevel, Side, Signal, Trade
from ml_engine.backtester import run_backtest
from ml_engine.features import FeatureEngine, SpoofDetector, order_book_imbalance
from ml_engine.optimizer import optimize, propose
from ml_engine.risk import (CircuitBreaker, TradeStats, kelly_fraction, round_px,
                            size_position)
from agents.validation_agent import validate
from tests.synthetic import generate
from pathlib import Path
import random

CFG = load_config(Path(__file__).resolve().parents[1] / "config.yaml")


def book(ts, bids, asks, coin="BTC"):
    return BookSnapshot(coin, ts, ts, np.array(bids, float), np.array(asks, float))


def test_obi_sign_and_bounds():
    b = np.array([[100, 10], [99, 10]], float)
    a = np.array([[101, 1], [102, 1]], float)
    v = order_book_imbalance(b, a, 2, 0.1)
    assert 0 < v <= 1
    assert order_book_imbalance(a * [1, 0] + [0, 1], b, 2, 0.1) < v


def test_cvd_and_poc():
    e = FeatureEngine("BTC", CFG.strategy)
    for i in range(50):
        e.on_trade(Trade("BTC", 1000 + i, 100.0, 1.0, True))
    for i in range(10):
        e.on_trade(Trade("BTC", 2000 + i, 105.0, 1.0, False))
    assert e.cvd == 40
    assert abs(e.poc() - 100.0) / 100 < 0.001


def test_spoof_detector_flags_vanishing_wall():
    sd = SpoofDetector(size_mult=5, max_life_s=3)
    base_b = [[100 - i, 1.0] for i in range(10)]
    asks = [[101 + i, 1.0] for i in range(10)]
    wall = [r[:] for r in base_b]
    wall[2][1] = 50.0
    sd.on_book(book(0, base_b, asks))
    sd.on_book(book(500, wall, asks))
    bid_score, _ = sd.on_book(book(1500, base_b, asks))   # disparu, non exécuté
    assert sd.events == 1 and bid_score > 0.5

    sd2 = SpoofDetector(size_mult=5, max_life_s=3)
    sd2.on_book(book(500, wall, asks))
    sd2.on_trade(Trade("BTC", 900, 98.0, 45.0, False))     # exécuté = honnête
    sd2.on_book(book(1500, base_b, asks))
    assert sd2.events == 0


def test_kelly_and_sizing():
    assert kelly_fraction(0.5, 1.0) == 0
    assert kelly_fraction(0.6, 1.0) == pytest.approx(0.2)
    st = TradeStats(0.55, 1.5)
    d = size_position(equity=10_000, px=60_000, is_long=True, vol_bps=3.0, stats=st,
                      cfg=CFG.risk, level=RiskLevel.NORMAL)
    assert d.qty > 0
    loss_at_stop = d.qty * (60_000 - d.stop_px)
    assert loss_at_stop <= 10_000 * CFG.risk.max_risk_per_trade_pct / 100 + 1e-6
    assert d.notional <= CFG.risk.max_position_notional_usd + 1e-6
    half = size_position(equity=10_000, px=60_000, is_long=True, vol_bps=3.0, stats=st,
                         cfg=CFG.risk, level=RiskLevel.CAUTION)
    assert half.risk_usd == pytest.approx(d.risk_usd / 2)
    halt = size_position(equity=10_000, px=60_000, is_long=True, vol_bps=3.0, stats=st,
                         cfg=CFG.risk, level=RiskLevel.HALT)
    assert halt.qty == 0


def test_circuit_breaker():
    cb = CircuitBreaker(3.0, 3)
    cb.on_equity(10_000, 0)
    cb.on_equity(9_650, 1000)
    assert cb.tripped
    cb2 = CircuitBreaker(3.0, 3)
    for _ in range(3):
        cb2.on_trade_closed(-1)
    assert cb2.tripped


def test_round_px_hyperliquid_rules():
    assert round_px(60123.456, 5) == 60123.0
    assert round_px(1.234567, 0) == 1.2346


def _sig(side, **kw):
    e = FeatureEngine("BTC", CFG.strategy)
    f = e.on_book(book(1000, [[100, 1]] * 3, [[101, 1]] * 3), now_ms=1000)
    f.spread_bps, f.ext_age_ms = 1.0, 10
    for k, v in kw.items():
        setattr(f, k, v)
    return Signal("BTC", 1000, side, 2.0, f)


def test_validation_rules():
    ok = MacroState(1000, RiskLevel.NORMAL, [])
    assert validate(_sig(Side.LONG), ok, CFG, 1000) == []
    assert validate(_sig(Side.LONG), MacroState(1000, RiskLevel.HALT, ["x"]), CFG, 1000)
    assert validate(_sig(Side.LONG), None, CFG, 1000)                      # fail-closed
    assert validate(_sig(Side.LONG, spoof_bid=0.9), ok, CFG, 1000)
    assert validate(_sig(Side.SHORT, spoof_bid=0.9), ok, CFG, 1000) == []
    assert validate(_sig(Side.LONG, book_age_ms=10_000), ok, CFG, 1000)
    assert validate(_sig(Side.FLAT), MacroState(1000, RiskLevel.HALT, []), CFG, 1000) == []


FAST = {"entry_threshold": 0.5, "persistence_ticks": 2, "cooldown_s": 30, "max_hold_s": 600,
        "zscore_window": 300, "cvd_window_s": 60}


def test_backtest_produces_trades_with_lower_threshold():
    st = CFG.strategy.model_copy(update=FAST)
    r = run_backtest(generate(1800), st, CFG.risk, exec_cfg=CFG.execution.model_copy(update={"mode": "taker"}))
    assert r.n_trades >= 2
    assert 0 <= r.max_drawdown_pct < 100
    assert len(r.equity_curve) > 100


def test_optimizer_respects_bounds_and_change_cap():
    cur = CFG.strategy.model_dump()
    rng = random.Random(1)
    for _ in range(50):
        c = propose(cur, CFG.research.bounds, 30, rng)
        assert 1.0 <= c["entry_threshold"] <= 3.0
        assert abs(c["entry_threshold"] - cur["entry_threshold"]) <= cur["entry_threshold"] * 0.3 + 1e-9
        assert isinstance(c["persistence_ticks"], int)


def test_optimizer_end_to_end():
    rc = CFG.research.model_copy(update={"n_trials": 6, "min_trades_for_eval": 4, "min_oos_trades": 3})
    st = CFG.strategy.model_copy(update={**FAST, "entry_threshold": 1.0})
    rep = optimize(generate(2400, seed=3), st, CFG.risk, rc, seed=1)
    assert rep.trials == 6
    assert isinstance(rep.accepted, bool) and rep.reason
    if rep.accepted:
        assert rep.best_oos["max_dd_pct"] < rc.max_drawdown_pct
