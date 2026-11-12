"""Simulation bout-en-bout du Pôle 1 sans réseau :
faux flux Hyperliquid/Binance/Bybit → Data → Quant → Macro → Validation →
Execution (paper) → Telemetry (JSONL local)."""
import asyncio
import json
from pathlib import Path

import yaml

from agents import (ExecutionAgent, HyperliquidDataAgent, MacroEdgeAgent, QuantAgent,
                    TelemetryAgent, ValidationAgent)
from agents.brokers import PaperBroker
from core.bus import EventBus
from core.config import ConfigStore
from core.events import now_ms
from demo.fakes import make_connect
from demo.synthetic import generate

ROOT = Path(__file__).resolve().parents[1]


def _config(tmp_path: Path) -> Path:
    raw = yaml.safe_load((ROOT / "config.yaml").read_text())
    raw["markets"] = [{"coin": "BTC", "binance": "btcusdt", "bybit": "BTCUSDT"}]
    raw["data"]["recordings_dir"] = str(tmp_path / "rec")
    raw["data"]["liquidations"]["provider"] = "disabled"
    raw["telemetry"]["local_log_dir"] = str(tmp_path / "tele")
    raw["telemetry"]["flush_interval_s"] = 0.1
    raw["strategy"].update(entry_threshold=0.8, persistence_ticks=1, cooldown_s=0,
                           max_spread_bps=10, zscore_window=100)
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(raw))
    return p


def _feeds(n_books: int):
    recs = generate(n_books // 2 + 10, seed=11)
    ext_q: asyncio.Queue = asyncio.Queue()

    async def hl():
        await asyncio.sleep(0.3)  # laisse la macro publier son premier état
        for r in recs:
            ts = now_ms()
            if r["t"] == "book":
                yield {"channel": "l2Book", "data": {"coin": "BTC", "time": ts, "levels": [
                    [{"px": str(p), "sz": str(s), "n": 1} for p, s in r["b"]],
                    [{"px": str(p), "sz": str(s), "n": 1} for p, s in r["a"]]]}}
                await asyncio.sleep(0.002)
            elif r["t"] == "trade":
                yield {"channel": "trades", "data": [{"coin": "BTC", "side": "B" if r["buy"] else "A",
                                                       "px": str(r["px"]), "sz": str(r["sz"]),
                                                       "time": ts, "tid": 1}]}
            elif r["t"] == "ctx":
                yield {"channel": "activeAssetCtx", "data": {"coin": "BTC", "ctx": {
                    "openInterest": str(r["oi"]), "funding": "0.00001", "markPx": str(r["m"]),
                    "oraclePx": str(r["o"]), "dayNtlVlm": "1", "premium": "0"}}}
            elif r["t"] == "ext":
                ext_q.put_nowait(r)

    async def binance():
        while True:
            r = await ext_q.get()
            if r["v"] == "binance":
                yield {"stream": "btcusdt@bookTicker", "data": {"s": "BTCUSDT", "b": str(r["bid"]), "a": str(r["ask"])}}
                bybit_q.put_nowait(r)

    bybit_q: asyncio.Queue = asyncio.Queue()

    async def bybit():
        while True:
            r = await bybit_q.get()
            yield {"topic": "orderbook.1.BTCUSDT", "type": "snapshot",
                   "data": {"s": "BTCUSDT", "b": [[str(r["bid"]), "1"]], "a": [[str(r["ask"]), "1"]]}}

    return {"wss://api.hyperliquid-testnet.xyz": hl, "wss://fstream.binance.com": binance,
            "wss://stream.bybit.com": bybit}


async def _run_swarm(cfg_path: Path, seconds: float, kill_file: Path):
    store = ConfigStore(cfg_path)
    bus = EventBus()
    sent: dict = {}
    connect = make_connect(_feeds(4000), sent)
    broker = PaperBroker(10_000)
    agents = [HyperliquidDataAgent(bus, store, connect_fn=connect), QuantAgent(bus, store),
              MacroEdgeAgent(bus, store, kill_file=str(kill_file)), ValidationAgent(bus, store),
              ExecutionAgent(bus, store, broker), TelemetryAgent(bus, store)]
    stop = asyncio.Event()
    tasks = [asyncio.create_task(a.run(stop)) for a in agents]
    await asyncio.sleep(seconds)
    stop.set()
    for a in agents:
        await a.shutdown()
    await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), 10)
    return agents, bus, sent, broker


def test_live_pipeline_trades_in_paper(tmp_path):
    cfg = _config(tmp_path)
    agents, bus, sent, broker = asyncio.run(_run_swarm(cfg, 6.0, tmp_path / "KILL"))
    data, quant, macro, val, exe, tele = agents
    # abonnements Hyperliquid envoyés (book + trades + ctx) et ping configuré
    subs = [m["subscription"]["type"] for m in sent["wss://api.hyperliquid-testnet.xyz"] if m.get("method") == "subscribe"]
    assert set(subs) == {"l2Book", "trades", "activeAssetCtx"}
    assert sent["wss://stream.bybit.com"][0]["args"] == ["orderbook.1.BTCUSDT"]
    pub = bus.stats()["published"]
    assert pub["book"] > 300 and pub["ext_quote"] > 300 and pub["signal"] > 300
    assert val.stats["accepted"] > 0, val.stats
    assert "latency_us" in quant.health()
    lines = [json.loads(ln) for f in (tmp_path / "tele").glob("*.jsonl") for ln in f.read_text().splitlines()]
    events = {x["event"] for x in lines}
    assert "hlswarm_order" in events and "hlswarm_fill" in events, events
    fills = [x for x in lines if x["event"] == "hlswarm_fill"]
    assert all("slippage_bps" in f["properties"] for f in fills)
    assert not exe.open                         # flatten à l'arrêt
    assert list((tmp_path / "rec").glob("md_*.jsonl.gz"))   # données enregistrées pour le backtest


def test_kill_switch_blocks_entries(tmp_path):
    cfg = _config(tmp_path)
    kill = tmp_path / "KILL"
    kill.write_text("stop")
    agents, bus, _, _ = asyncio.run(_run_swarm(cfg, 3.0, kill))
    macro, val = agents[2], agents[3]
    assert macro.state.level.value == "halt"
    assert val.stats["accepted"] == 0
    lines = [json.loads(ln) for f in (tmp_path / "tele").glob("*.jsonl") for ln in f.read_text().splitlines()]
    assert not [x for x in lines if x["event"] == "hlswarm_order" and x["properties"]["kind"] == "entry"]
