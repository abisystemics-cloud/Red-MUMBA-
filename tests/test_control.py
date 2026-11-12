"""Canal de supervision : commandes descendantes, comptes rendus montants."""
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from agents import ExecutionAgent, MacroEdgeAgent, ValidationAgent
from agents.brokers import PaperBroker
from agents.control_agent import ControlAgent, compact_status, validate_command
from core.alerts import alert_for
from core.bus import EventBus
from core.config import ConfigStore
from core.events import Topic

ROOT = Path(__file__).resolve().parents[1]


def _store(tmp_path):
    raw = yaml.safe_load((ROOT / "config.yaml").read_text())
    raw["control"]["poll_seconds"] = 0.05
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(raw))
    return ConfigStore(p)


def cmd(cid, name, minutes_ago=0, **args):
    t = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return {"id": cid, "cmd": name, "args": args, "reason": "test", "issued_by": "claude",
            "issued_at": t.isoformat()}


def test_whitelist_and_bounds():
    coins = ["BTC", "ETH"]
    assert validate_command(cmd("1", "pause"), coins) is None
    assert "within [0, 1]" in validate_command(cmd("2", "set_risk_scale", scale=1.5), coins)
    assert validate_command(cmd("3", "set_risk_scale", scale=0.5), coins) is None
    assert validate_command(cmd("4", "disable_coin", coin="DOGE"), coins)
    assert validate_command(cmd("5", "withdraw", amount=100), coins)       # hors liste blanche
    assert validate_command(cmd("6", "go_live_mainnet"), coins)


def test_commands_apply_and_report_back(tmp_path):
    store = _store(tmp_path)
    bus = EventBus()
    tele = bus.subscribe(Topic.TELEMETRY, "t", maxsize=1000)
    macro = MacroEdgeAgent(bus, store, kill_file=str(tmp_path / "KILL"))
    val = ValidationAgent(bus, store)
    exe = ExecutionAgent(bus, store, PaperBroker(10_000))
    agents = [macro, val, exe]
    doc = {"commands": [
        cmd("a", "pause"), cmd("b", "set_risk_scale", scale=0.25), cmd("c", "disable_coin", coin="ETH"),
        cmd("d", "set_risk_scale", scale=3), cmd("e", "flatten", minutes_ago=600), cmd("f", "ping"),
        cmd("g", "go_live_report"),     # destinée au conteneur research : ignorée ici
    ]}

    async def fetch():
        return doc

    ctl = ControlAgent(bus, store, "live", lambda: compact_status(agents), fetch_fn=fetch,
                       state_dir=str(tmp_path))
    agents.append(ctl)

    async def scenario():
        stop = asyncio.Event()
        tasks = [asyncio.create_task(a.run(stop)) for a in agents]
        await asyncio.sleep(1.0)
        stop.set()
        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), 10)

    asyncio.run(scenario())
    events = []
    while not tele.queue.empty():
        events.append(tele.queue.get_nowait())
    acks = {e["command_id"]: e["status"] for e in events if e["event"] == "command_ack"}
    assert acks == {"a": "dispatched", "b": "dispatched", "c": "dispatched", "d": "rejected",
                    "e": "expired", "f": "dispatched"}
    applied = {e["command_id"] for e in events if e["event"] == "command_applied"}
    assert applied == {"a", "b", "c"}
    assert macro.state.level.value == "halt" and "supervisor pause" in macro.state.reasons[0]
    assert exe.risk_scale == 0.25 and val.disabled == {"ETH"}
    snaps = [e for e in events if e["event"] == "status_snapshot"]
    assert any(s["trigger"] == "ping:f" for s in snaps)
    assert compact_status(agents)["execution"]["risk_scale"] == 0.25
    # une commande déjà traitée n'est jamais rejouée (même après redémarrage)
    ctl2 = ControlAgent(bus, store, "live", lambda: {}, fetch_fn=fetch, state_dir=str(tmp_path))
    assert asyncio.run(ctl2.process(doc)) == 0


def test_supervisor_actions_are_announced():
    assert alert_for({"event": "command_applied", "command_id": "x", "cmd": "pause", "agent": "macro"})
    assert alert_for({"event": "command_ack", "status": "rejected", "cmd": "set_risk_scale",
                      "command_id": "y", "detail": "too high"})
