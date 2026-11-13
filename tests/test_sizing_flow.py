from core.config import RiskCfg
from core.events import RiskLevel
from ml_engine.risk import TradeStats, size_position
from scripts.import_history import parse_binance_flow


def _losing_stats(cfg):
    st = TradeStats(cfg.prior_win_rate, cfg.prior_payoff)
    for _ in range(3):
        st.add(-0.01)
    return st


def test_kelly_locks_out_after_three_losses_but_fixed_does_not():
    kelly = RiskCfg()
    st = _losing_stats(kelly)
    d = size_position(equity=10_000, px=100, is_long=True, vol_bps=1.0, stats=st, cfg=kelly, level=RiskLevel.NORMAL)
    assert d.qty == 0  # le comportement qui figeait les backtests à 3 trades
    fixed = RiskCfg(sizing="fixed")
    d = size_position(equity=10_000, px=100, is_long=True, vol_bps=1.0, stats=st, cfg=fixed, level=RiskLevel.NORMAL)
    assert d.qty > 0 and abs(d.risk_usd - 10_000 * fixed.max_risk_per_trade_pct / 100) < 1e-6


def test_binance_flow_buckets_by_aggressor():
    text = ("agg_trade_id,price,quantity,first_trade_id,last_trade_id,transact_time,is_buyer_maker\n"
            "1,100,1,1,1,1000,false\n2,102,1,2,2,1500,false\n3,101,2,3,3,1900,true\n4,99,1,4,4,2100,true\n")
    out = parse_binance_flow(text, "BTC", bucket_ms=2000)
    assert [(r["buy"], r["sz"]) for r in out] == [(False, 2.0), (True, 2.0), (False, 1.0)]
    buy = out[1]
    assert buy["px"] == 101 and buy["t"] == "trade" and buy["ts"] == 1999
