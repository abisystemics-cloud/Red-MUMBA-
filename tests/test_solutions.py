"""Tests des améliorations : exécution maker, nouveaux signaux, walk-forward
durci, alertes, rapport go/no-go."""
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from agents.brokers import PaperBroker
from agents.data_agent import HyperliquidDataAgent
from core.alerts import Alerter, alert_for
from core.config import load_config
from core.events import AssetCtx, BookSnapshot, WhaleBias
from ml_engine.backtester import run_backtest
from ml_engine.features import FeatureEngine
from ml_engine.go_live import evaluate, format_report
from ml_engine.optimizer import required_margin
from ml_engine.strategy import composite_score
from demo.synthetic import generate

CFG = load_config(Path(__file__).resolve().parents[1] / "config.yaml")


def book(ts, bid, ask, coin="BTC"):
    return BookSnapshot(coin, ts, ts, np.array([[bid - i, 1.0] for i in range(5)], float),
                        np.array([[ask + i, 1.0] for i in range(5)], float))


# ------------------------------------------------------------ 1. maker
def test_paper_post_only_fills_only_when_price_trades_through():
    async def scenario():
        b = PaperBroker(10_000)
        b.on_book(book(0, 100, 101))
        rej = await b.post_only("BTC", True, 1.0, 101, False)          # croiserait → refusé
        assert not rej.ok and "cross" in rej.error
        f = await b.post_only("BTC", True, 1.0, 100, False)
        b.on_book(book(1, 100, 101))                                   # rien ne traverse
        assert (await b.order_status("BTC", f.oid)).status == "open"
        b.on_book(book(2, 99, 100))                                    # ask touche notre bid
        st = await b.order_status("BTC", f.oid)
        assert st.status == "filled" and st.filled_sz == 1.0 and st.avg_px == 100
        sz, px = await b.position("BTC")
        assert sz == 1.0 and px == 100
        assert abs(b.cash - (10_000 - 100 * 0.00015)) < 1e-9          # frais maker
    asyncio.run(scenario())


def test_paper_cancel_all_cancels_resting_orders():
    async def scenario():
        b = PaperBroker(10_000)
        b.on_book(book(0, 100, 101))
        f = await b.post_only("BTC", False, 1.0, 101, False)
        await b.cancel_all("BTC")
        b.on_book(book(1, 102, 103))
        assert (await b.order_status("BTC", f.oid)).status == "canceled"
    asyncio.run(scenario())


def test_maker_mode_cuts_costs_vs_taker_on_same_signals():
    st = CFG.strategy.model_copy(update={"entry_threshold": 0.5, "persistence_ticks": 2, "cooldown_s": 30,
                                         "max_hold_s": 600, "zscore_window": 300, "cvd_window_s": 60})
    recs = generate(3600, seed=4)
    taker = run_backtest(recs, st, CFG.risk, exec_cfg=CFG.execution.model_copy(update={"mode": "taker"}))
    maker = run_backtest(recs, st, CFG.risk, exec_cfg=CFG.execution)
    assert maker.maker_attempts > 0
    fees_t = sum(t.fees for t in taker.trades) / max(1, taker.n_trades)
    fees_m = sum(t.fees for t in maker.trades) / max(1, maker.n_trades)
    assert fees_m < fees_t


# ------------------------------------------------------- 2. nouveaux signaux
def _features(**ctx_overrides):
    e = FeatureEngine("BTC", CFG.strategy)
    for i in range(30):  # historique de funding calme
        e.on_ctx(AssetCtx("BTC", i, 1e9, 1e-5 * (1 + (i % 3) * 0.01), 100, 100))
    for k, v in ctx_overrides.items():
        if k == "funding":
            e.on_ctx(AssetCtx("BTC", 99, 1e9, v, 100, 100))
        if k == "whale":
            e.on_whale(WhaleBias("BTC", 1000, v, 5, 1e6))
    return e.on_book(book(1000, 100, 101), now_ms=1000)


def test_extreme_funding_gives_contrarian_score():
    calm = composite_score(_features(), CFG.strategy)
    crowded_longs = _features(funding=5e-4)
    assert crowded_longs.funding_z > 3
    assert composite_score(crowded_longs, CFG.strategy) < calm


def test_whale_bias_moves_score_in_its_direction():
    long_w = composite_score(_features(whale=0.8), CFG.strategy)
    short_w = composite_score(_features(whale=-0.8), CFG.strategy)
    assert long_w > short_w


def test_whale_aggregation_from_clearinghouse_state():
    states = [
        {"assetPositions": [{"position": {"coin": "BTC", "szi": "2", "positionValue": "120000"}},
                            {"position": {"coin": "ETH", "szi": "-10", "positionValue": "30000"}}]},
        {"assetPositions": [{"position": {"coin": "BTC", "szi": "-1", "positionValue": "40000"}}]},
    ]
    out = {w.coin: w for w in HyperliquidDataAgent.aggregate_whales(states, ["BTC", "ETH", "SOL"], 1)}
    assert abs(out["BTC"].bias - 0.5) < 1e-9 and out["BTC"].n_wallets == 2
    assert out["ETH"].bias == -1.0
    assert out["SOL"].bias == 0.0 and out["SOL"].n_wallets == 0


def test_backtest_charges_funding_to_longs_when_positive():
    st = CFG.strategy.model_copy(update={"entry_threshold": 0.5, "persistence_ticks": 2, "cooldown_s": 30,
                                         "max_hold_s": 600, "zscore_window": 300, "cvd_window_s": 60})
    recs = generate(1800, seed=4)
    for r in recs:
        if r["t"] == "ctx":
            r["f"] = 1e-3  # funding très élevé
    res = run_backtest(recs, st, CFG.risk, exec_cfg=CFG.execution.model_copy(update={"mode": "taker"}))
    longs = [t for t in res.trades if t.side == "long"]
    shorts = [t for t in res.trades if t.side == "short"]
    assert all(t.funding >= 0 for t in longs) and all(t.funding <= 0 for t in shorts)


# ------------------------------------------------- 4. walk-forward durci
def test_required_margin_grows_with_trials():
    a = required_margin(CFG.research.model_copy(update={"n_trials": 5}))
    b = required_margin(CFG.research.model_copy(update={"n_trials": 200}))
    assert b > a > 0


def test_auto_deploy_is_off_by_default():
    assert CFG.research.auto_deploy is False


# ------------------------------------------------------------ 5. alertes
def test_alert_mapping_and_rate_limit():
    assert alert_for({"event": "feed_down", "feed": "hyperliquid"})[0] == "feed:hyperliquid"
    assert alert_for({"event": "order", "status": "rejected", "kind": "stop", "coin": "BTC"})
    assert alert_for({"event": "order", "status": "filled", "kind": "entry"}) is None
    assert alert_for({"event": "risk_level", "level": "normal"}) is None
    a = Alerter(CFG.alerts)
    assert a.should_send("k", now=0) and not a.should_send("k", now=10) and a.should_send("k", now=400)


# ----------------------------------------------------------- 6. go/no-go
def _trades(n, pnl_fn, days=28):
    t0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
    return [((t0 + timedelta(days=days * i / n)).isoformat(), pnl_fn(i)) for i in range(n)]


def test_go_live_green_when_all_criteria_met():
    rep = evaluate(_trades(240, lambda i: 12 if i % 3 else -10), 10_000, CFG.go_live)
    assert rep["go"] and rep["verdict"] == "GO", format_report(rep)


def test_go_live_red_on_too_few_trades_or_low_pf():
    few = evaluate(_trades(50, lambda i: 10), 10_000, CFG.go_live)
    assert not few["go"] and not few["criteria"]["trades"]["pass"]
    weak = evaluate(_trades(240, lambda i: 10 if i % 2 else -10), 10_000, CFG.go_live)
    assert not weak["criteria"]["profit_factor"]["pass"]
    assert "NO-GO" in format_report(weak)
