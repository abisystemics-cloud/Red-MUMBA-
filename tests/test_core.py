import asyncio
import shutil
from pathlib import Path

import pytest
import yaml

from core.bus import EventBus
from core.config import ConfigStore, atomic_update_strategy, load_config
from core.events import Topic
from core.ws_client import ResilientWebSocket
from tests.fakes import make_connect

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def cfg_path(tmp_path):
    p = tmp_path / "config.yaml"
    shutil.copy(ROOT / "config.yaml", p)
    return p


def test_config_loads_and_defaults_are_safe(cfg_path):
    cfg = load_config(cfg_path)
    assert cfg.runtime.network == "testnet"
    assert cfg.runtime.dry_run is True
    assert cfg.live_trading_armed() is False


def test_atomic_update_preserves_comments_and_hot_reloads(cfg_path, tmp_path):
    store = ConfigStore(cfg_path)
    new = store.current.strategy.model_dump()
    new["entry_threshold"] = 2.2
    atomic_update_strategy(cfg_path, new, tmp_path / "hist")
    text = cfg_path.read_text()
    assert "# hl-swarm — configuration centrale" in text      # commentaires conservés
    assert yaml.safe_load(text)["risk"]["kelly_fraction"] == 0.25
    assert list((tmp_path / "hist").glob("config.*.yaml"))      # sauvegarde d'audit
    assert asyncio.run(store.check_reload()) is True
    assert store.current.strategy.entry_threshold == 2.2


def test_invalid_reload_is_rejected(cfg_path):
    store = ConfigStore(cfg_path)
    raw = yaml.safe_load(cfg_path.read_text())
    raw["risk"]["kelly_fraction"] = 5  # invalide
    cfg_path.write_text(yaml.safe_dump(raw))
    import os
    import time
    os.utime(cfg_path, (time.time() + 5, time.time() + 5))
    assert asyncio.run(store.check_reload()) is False
    assert store.current.risk.kelly_fraction == 0.25


def test_cold_sections_not_hot_applied(cfg_path):
    store = ConfigStore(cfg_path)
    raw = yaml.safe_load(cfg_path.read_text())
    raw["runtime"]["dry_run"] = False
    raw["strategy"]["cooldown_s"] = 99
    cfg_path.write_text(yaml.safe_dump(raw))
    import os
    import time
    os.utime(cfg_path, (time.time() + 5, time.time() + 5))
    asyncio.run(store.check_reload())
    assert store.current.runtime.dry_run is True    # nécessite un redémarrage
    assert store.current.strategy.cooldown_s == 99   # appliqué à chaud


def test_bus_drop_oldest():
    bus = EventBus()
    sub = bus.subscribe(Topic.BOOK, "t", maxsize=3)
    for i in range(10):
        bus.publish(Topic.BOOK, i)
    assert sub.dropped == 7
    assert [sub.queue.get_nowait() for _ in range(3)] == [7, 8, 9]


def test_ws_reconnects_and_resubscribes():
    async def producer():
        for i in range(3):
            yield {"channel": "x", "i": i}
            await asyncio.sleep(0)

    sent: dict = {}
    got = []

    async def scenario():
        ws = ResilientWebSocket("t", "wss://fake", lambda m: got.append(m),
                                connect_fn=make_connect({"wss://fake": producer}, sent, fail_after=3),
                                backoff_base_s=0.01, backoff_max_s=0.02)
        ws.add_subscription({"method": "subscribe", "subscription": {"type": "trades", "coin": "BTC"}})
        stop = asyncio.Event()
        task = asyncio.create_task(ws.run(stop))
        while ws.reconnects < 3:
            await asyncio.sleep(0.01)
        stop.set()
        await asyncio.wait_for(task, 2)
        return ws

    ws = asyncio.run(scenario())
    assert ws.reconnects >= 3
    assert len(sent["wss://fake"]) >= 3          # réabonné à chaque connexion
    assert len(got) >= 9


def test_ws_stale_socket_is_recycled():
    async def silent():
        if False:
            yield {}
        await asyncio.sleep(10)

    async def scenario():
        ws = ResilientWebSocket("t", "wss://s", lambda m: None, stale_after_s=0.15, heartbeat_s=0.05,
                                heartbeat_msg={"method": "ping"},
                                connect_fn=make_connect({"wss://s": silent}, sent := {}),
                                backoff_base_s=0.01, backoff_max_s=0.02)
        stop = asyncio.Event()
        task = asyncio.create_task(ws.run(stop))
        await asyncio.sleep(0.6)
        stop.set()
        await asyncio.wait_for(task, 2)
        return ws, sent

    ws, sent = asyncio.run(scenario())
    assert ws.reconnects >= 1
    assert "stale" in (ws.last_error or "")
    assert {"method": "ping"} in sent["wss://s"]
