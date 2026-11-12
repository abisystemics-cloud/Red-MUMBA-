import asyncio
import gzip
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from agents.research_agent import BacktestingAgent, performance_from_trades
from core.bus import EventBus
from core.config import ConfigStore
from core.events import now_ms
from tests.synthetic import generate

ROOT = Path(__file__).resolve().parents[1]


def _setup(tmp_path: Path, auto_deploy=True, bad_perf=True):
    raw = yaml.safe_load((ROOT / "config.yaml").read_text())
    raw["data"]["recordings_dir"] = str(tmp_path / "rec")
    raw["telemetry"]["local_log_dir"] = str(tmp_path / "tele")
    raw["research"].update(n_trials=4, min_trades_for_eval=10, auto_deploy=auto_deploy, min_oos_trades=3)
    raw["strategy"].update(entry_threshold=1.0, persistence_ticks=2, cooldown_s=30, max_hold_s=600,
                           zscore_window=300, cvd_window_s=60)
    cfg = tmp_path / "config.yaml"
    cfg.write_text(yaml.safe_dump(raw))
    # marché enregistré (horodaté "maintenant")
    (tmp_path / "rec").mkdir()
    recs = generate(2400, seed=5)
    shift = now_ms() - recs[-1]["ts"] - 1000
    with gzip.open(tmp_path / "rec" / "md_test.jsonl.gz", "wt") as fh:
        for r in recs:
            r["ts"] += shift
            fh.write(json.dumps(r) + "\n")
    # télémétrie : 30 trades perdants
    (tmp_path / "tele").mkdir()
    ts = datetime.now(timezone.utc).isoformat()
    with open(tmp_path / "tele" / "telemetry_x.jsonl", "w") as fh:
        for i in range(30):
            pnl = -1.0 if (bad_perf and i % 3) else 1.0
            fh.write(json.dumps({"event": "hlswarm_trade_closed", "timestamp": ts,
                                 "properties": {"pnl": pnl, "r_multiple": pnl}}) + "\n")
    return cfg


def test_performance_metrics():
    p = performance_from_trades([1, -1, 2, -1], [1, -1, 2, -1])
    assert p["n_trades"] == 4 and p["win_rate"] == 0.5 and p["max_dd_abs"] == 1


def test_healthy_system_is_left_alone(tmp_path):
    cfg = _setup(tmp_path, bad_perf=False)
    agent = BacktestingAgent(EventBus(), ConfigStore(cfg), use_process_pool=False)
    state = asyncio.run(agent.run_once())
    assert state["done"] == "healthy" and "report" not in state


def test_degraded_system_triggers_backtest_and_guarded_deploy(tmp_path):
    cfg = _setup(tmp_path)
    store = ConfigStore(cfg)
    before = cfg.read_text()
    agent = BacktestingAgent(EventBus(), store, use_process_pool=False)
    state = asyncio.run(agent.run_once())
    assert state["degraded"] is True
    assert state["profile"]["by_type"]["book"] > 2000
    rep = state["report"]
    assert rep["trials"] == 4
    if rep["accepted"]:
        assert state["done"] == "deployed" and cfg.read_text() != before
        assert rep["best_oos"]["max_dd_pct"] < 10
    else:
        assert state["done"].startswith("rejected") and cfg.read_text() == before
