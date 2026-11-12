"""Import historique, client Coinversa et backtest sur période."""
import gzip
import json
from pathlib import Path

from agents.coinversa import heatmap_to_clusters, positioning_signal, snapshots_to_bias
from core.config import load_config
from scripts.backtest import run as run_period
from scripts.import_history import (downsample, parse_asset_ctxs, parse_binance_agg_trades,
                                    parse_binance_book_ticker, parse_fill_block, parse_l2_line, write_hours)
from demo.synthetic import generate

CFG = load_config(Path(__file__).resolve().parents[1] / "config.yaml")
LV = [[{"px": "100.0", "sz": "2", "n": 1}, {"px": "99.5", "sz": "1", "n": 1}],
      [{"px": "100.5", "sz": "3", "n": 2}]]


def test_parse_l2_line_envelopes():
    a = json.dumps({"time": "2026-09-01T00:00:00.1", "ver_num": 1,
                    "raw": {"channel": "l2Book", "data": {"coin": "BTC", "time": 1788220800100, "levels": LV}}})
    b = json.dumps({"coin": "BTC", "time": 1788220800100, "levels": LV})
    for line in (a, b):
        r = parse_l2_line(line, 10)
        assert r["coin"] == "BTC" and r["ts"] == 1788220800100
        assert r["b"] == [[100.0, 2.0], [99.5, 1.0]] and r["a"] == [[100.5, 3.0]]
    assert parse_l2_line("garbage", 10) is None
    assert parse_l2_line(json.dumps({"data": {"coin": "BTC", "time": 1, "levels": [[], []]}}), 10) is None


def test_parse_asset_ctxs_header_variants():
    text = "time,coin,funding,open_interest,prev_day_px,day_ntl_vlm,premium,oracle_px,mark_px,mid_px\n" \
           "2026-09-01T00:00:00Z,BTC,0.0000125,30000.5,1,2,0,60010,60000,60005\n" \
           "2026-09-01T00:00:00Z,DOGE,0.1,1,1,1,0,1,1,1\n"
    rows = parse_asset_ctxs(text, {"BTC"})
    assert rows == [{"t": "ctx", "coin": "BTC", "ts": 1788220800000, "oi": 30000.5, "f": 0.0000125,
                     "m": 60000.0, "o": 60010.0}]


def test_parse_binance_files():
    bt = "update_id,best_bid_price,best_bid_qty,best_ask_price,best_ask_qty,transaction_time,event_time\n" \
         "1,60000.1,2,60000.2,3,1788220800000,1788220800001\n"
    assert list(parse_binance_book_ticker(bt, "BTC"))[0]["bid"] == 60000.1
    agg = "1,60000,0.5,1,1,1788220800000,true\n"
    r = list(parse_binance_agg_trades(agg, "BTC"))[0]
    assert r["bid"] < 60000 < r["ask"] and r["v"] == "binance"


def test_parse_fill_block_keeps_taker_side_only():
    line = json.dumps({"block_number": 1, "events": [
        ["0xa", {"coin": "BTC", "px": "60000", "sz": "0.1", "side": "B", "time": 5, "crossed": True}],
        ["0xb", {"coin": "BTC", "px": "60000", "sz": "0.1", "side": "A", "time": 5, "crossed": False}],
        ["0xc", {"coin": "SOL", "px": "150", "sz": "1", "side": "A", "time": 5, "crossed": True}]]})
    tr = parse_fill_block(line, {"BTC"})
    assert tr == [{"t": "trade", "coin": "BTC", "ts": 5, "px": 60000.0, "sz": 0.1, "buy": True}]


def test_downsample_per_coin_and_venue():
    recs = [{"coin": "BTC", "ts": t, "v": "binance"} for t in range(0, 5000, 100)]
    assert len(downsample(recs, 1000)) == 5


# ----------------------------------------------------------- Coinversa
ROWS_PCT = [  # format réel de /pulse/cohort-bias/history (netBias en %)
    {"timestamp": 1, "coin": "BTC", "tierType": "pnl", "tier": "money_printer",
     "longNotional": 381.0, "shortNotional": 743.0, "netBias": -32.1, "accountCount": 160},
    {"timestamp": 1, "coin": "BTC", "tierType": "pnl", "tier": "smart_money",
     "longNotional": 156.0, "shortNotional": 130.0, "netBias": 9.1, "accountCount": 499},
    {"timestamp": 1, "coin": "BTC", "tierType": "pnl", "tier": "full_rekt",
     "longNotional": 278.0, "shortNotional": 94.0, "netBias": 49.3, "accountCount": 381},
    {"timestamp": 1, "coin": "BTC", "tierType": "size", "tier": "heavyweights",
     "longNotional": 1.0, "shortNotional": 9.0, "netBias": -80, "accountCount": 5},
]


def test_positioning_signal_smart_vs_crowd():
    snaps = snapshots_to_bias({"rows": ROWS_PCT}, "BTC", CFG.data.coinversa)
    assert len(snaps) == 1
    s = snaps[0]
    smart = (381 + 156 - 743 - 130) / (381 + 156 + 743 + 130)   # rentables nets courts
    crowd = (278 - 94) / (278 + 94)                              # perdants nets longs
    assert abs(s.bias - (0.6 * smart - 0.4 * crowd)) < 1e-9
    assert s.bias < 0 and s.n_wallets == 160 + 499 + 381


def test_positioning_without_notionals_uses_ratio_or_percent():
    rows = [{"tier": "money_printer", "netBias": 50}, {"tier": "full_rekt", "netBias": -0.5}]
    sig, _, _ = positioning_signal(rows, CFG.data.coinversa)
    assert abs(sig - (0.6 * 0.5 + 0.4 * 0.5)) < 1e-9


def test_heatmap_to_clusters_real_shape():
    body = {"coin": "BTC", "currentPrice": 71495, "buckets": [
        {"priceLow": 68635.2, "priceHigh": 70065.1, "totalNotionalAtRisk": 125e6},
        {"priceLow": 71495, "priceHigh": 72924.9, "totalNotionalAtRisk": 44e6}]}
    cl = heatmap_to_clusters(body)
    assert cl[0] == ((68635.2 + 70065.1) / 2, 125e6) and len(cl) == 2


# ------------------------------------------------- backtest sur période
def test_period_backtest_end_to_end(tmp_path):
    recs = generate(4 * 3600, seed=9)
    t0 = recs[0]["ts"]
    for k in range(0, 4 * 3600 * 1000, 3600 * 1000):
        recs.append({"t": "whale", "coin": "BTC", "ts": t0 + k, "bias": 0.5, "n": 10, "g": 1e6})
    rec_dir = tmp_path / "recordings"
    rec_dir.mkdir()
    assert write_hours(recs, rec_dir) >= 4
    files = sorted(rec_dir.glob("md_*_hist.jsonl.gz"))
    with gzip.open(files[0], "rt") as fh:
        ts = [json.loads(x)["ts"] for x in fh]
    assert ts == sorted(ts)
    import time
    day = time.strftime("%Y-%m-%d", time.gmtime(t0 / 1000))
    end = time.strftime("%Y-%m-%d", time.gmtime(recs[-1]["ts"] / 1000 + 86400))
    cfg = CFG.model_copy(update={"strategy": CFG.strategy.model_copy(update={
        "entry_threshold": 0.5, "persistence_ticks": 2, "cooldown_s": 30, "max_hold_s": 600,
        "zscore_window": 300, "cvd_window_s": 60})})
    r = run_period(cfg, day, end, ["BTC"], "taker", str(rec_dir))
    assert r["events"]["book"] > 20000 and r["events"]["whale"] == 4
    assert r["signals_available"]["positioning"] and not r["signals_available"]["liquidations"]
    assert r["go_no_go"]["verdict"] in ("GO", "NO-GO")
    assert r["summary"]["trades"] == sum(m["trades"] for m in r["monthly"].values())
