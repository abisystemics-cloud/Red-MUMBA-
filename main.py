"""Point d'entrée : orchestre l'essaim d'agents.

    python main.py --role all        # tout dans un process (dev)
    python main.py --role live       # Pôle 1 : trading temps réel
    python main.py --role research   # Pôle 2 : R&D (conteneur séparé en prod)
    python main.py --backtest        # un cycle R&D forcé, puis sortie
    python main.py --go-live         # rapport go/no-go (code retour 0 = GO, 3 = NO-GO)

Chaque agent tourne sous un superviseur qui le redémarre (backoff exponentiel)
s'il plante ; au-delà de `MAX_RESTARTS` en 10 minutes, le process s'arrête
proprement et Docker le relance (état propre). Un serveur HTTP minimal expose
/health (sondes Docker / Render / AWS) et /status.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import signal
import sys
import time

from agents import (BacktestingAgent, ExecutionAgent, HyperliquidDataAgent, MacroEdgeAgent,
                    QuantAgent, TelemetryAgent, ValidationAgent)
from agents.base import BaseAgent
from agents.brokers import HyperliquidBroker, PaperBroker
from agents.control_agent import ControlAgent, compact_status
from core.bus import EventBus
from core.config import ConfigStore
from core.logging_setup import setup_logging

log = logging.getLogger("main")
MAX_RESTARTS = 8


async def supervise(agent: BaseAgent, stop: asyncio.Event, fatal: asyncio.Event) -> None:
    restarts: list[float] = []
    while not stop.is_set():
        try:
            await agent.run(stop)
            return
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            agent.errors += 1
            log.exception("agent %s crashed", agent.name)
            now = time.monotonic()
            restarts = [t for t in restarts if now - t < 600] + [now]
            if len(restarts) > MAX_RESTARTS:
                log.critical("agent %s keeps crashing → stopping process", agent.name)
                fatal.set()
                stop.set()
                return
            delay = min(30, 2 ** len(restarts))
            log.warning("restarting %s in %ss", agent.name, delay)
            try:
                await asyncio.wait_for(stop.wait(), timeout=delay)
            except asyncio.TimeoutError:
                pass


async def health_server(agents: list[BaseAgent], bus: EventBus, store: ConfigStore, port: int,
                        stop: asyncio.Event) -> None:
    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            line = (await asyncio.wait_for(reader.readline(), 5)).decode(errors="ignore")
            path = line.split(" ")[1] if " " in line else "/"
            status = {a.name: a.health() for a in agents}
            stale = [n for n, h in status.items() if h.get("stale")]
            if path.startswith("/health"):
                code, body = (503, {"ok": False, "stale": stale}) if stale else (200, {"ok": True})
            else:
                code, body = 200, {"agents": status, "bus": bus.stats(),
                                   "config_reloads": store.reload_count,
                                   "network": store.current.runtime.network,
                                   "dry_run": store.current.runtime.dry_run}
            payload = json.dumps(body, default=str).encode()
            writer.write(f"HTTP/1.1 {code} {'OK' if code == 200 else 'Service Unavailable'}\r\n"
                         f"Content-Type: application/json\r\nContent-Length: {len(payload)}\r\n"
                         "Connection: close\r\n\r\n".encode() + payload)
            await writer.drain()
        except Exception:  # noqa: BLE001
            pass
        finally:
            writer.close()

    server = await asyncio.start_server(handle, "0.0.0.0", port)
    log.info("health server on :%d (/health, /status)", port)
    async with server:
        await stop.wait()


def make_http_session():
    try:
        import aiohttp
    except ImportError:
        log.warning("aiohttp not installed: PostHog/Perplexity/Coinglass disabled")
        return None
    return aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60))


def make_broker(store: ConfigStore):
    cfg = store.current
    if cfg.runtime.dry_run:
        log.warning("DRY RUN — paper trading with %.0f USD", cfg.risk.paper_equity_usd)
        return PaperBroker(cfg.risk.paper_equity_usd)
    if cfg.is_mainnet and not cfg.live_trading_armed():
        log.critical("mainnet with dry_run=false requires LIVE_TRADING_CONFIRM=I_UNDERSTAND_THE_RISKS")
        sys.exit(2)
    for var in ("HL_ACCOUNT_ADDRESS", "HL_API_WALLET_PRIVATE_KEY"):
        if not os.getenv(var):
            log.critical("missing %s for live execution", var)
            sys.exit(2)
    log.warning("LIVE EXECUTION on %s", cfg.runtime.network.upper())
    return HyperliquidBroker(cfg.hl_api_url())


async def amain(args) -> int:
    store = ConfigStore(args.config)
    cfg = store.current
    setup_logging(os.getenv("LOG_LEVEL", cfg.runtime.log_level))
    bus = EventBus()
    http = make_http_session()
    stop, fatal = asyncio.Event(), asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:  # Windows
            pass

    agents: list[BaseAgent] = []
    if args.role in ("all", "live"):
        agents += [
            HyperliquidDataAgent(bus, store, http_session=http),
            QuantAgent(bus, store),
            MacroEdgeAgent(bus, store, http_session=http),
            ValidationAgent(bus, store),
            ExecutionAgent(bus, store, make_broker(store)),
        ]
    if args.role in ("all", "research"):
        agents.append(BacktestingAgent(bus, store, http_session=http))
    agents.append(TelemetryAgent(bus, store, http_session=http))
    agents.append(ControlAgent(bus, store, args.role, lambda: compact_status(agents), http_session=http))

    log.info("starting swarm role=%s network=%s dry_run=%s agents=%s", args.role,
             cfg.runtime.network, cfg.runtime.dry_run, [a.name for a in agents])
    tasks = [asyncio.create_task(supervise(a, stop, fatal), name=a.name) for a in agents]
    tasks.append(asyncio.create_task(store.watch(stop), name="config-watch"))
    port = int(os.getenv("PORT", cfg.runtime.health_port))
    tasks.append(asyncio.create_task(health_server(agents, bus, store, port, stop), name="health"))

    await stop.wait()
    log.warning("shutdown requested")
    for a in sorted(agents, key=lambda a: a.name != "execution"):  # execution d'abord
        try:
            await asyncio.wait_for(a.shutdown(), timeout=20)
        except Exception:  # noqa: BLE001
            log.exception("shutdown error in %s", a.name)
    for t in tasks:
        t.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    if http:
        await http.close()
    return 1 if fatal.is_set() else 0


def main() -> None:
    p = argparse.ArgumentParser(description="Hyperliquid multi-agent trading swarm")
    p.add_argument("--config", default=os.getenv("CONFIG_PATH", "config.yaml"))
    p.add_argument("--role", choices=("all", "live", "research"), default=os.getenv("ROLE", "all"))
    p.add_argument("--backtest", action="store_true", help="run one forced research cycle and exit")
    p.add_argument("--go-live", action="store_true", help="print the go/no-go report and exit")
    args = p.parse_args()
    if args.go_live:
        setup_logging("WARNING")
        store = ConfigStore(args.config)
        agent = BacktestingAgent(EventBus(), store, use_process_pool=False)
        rep = asyncio.run(agent.go_live_report())
        from ml_engine.go_live import format_report
        print(format_report(rep))
        sys.exit(0 if rep["go"] else 3)
    if args.backtest:
        setup_logging("INFO")
        store = ConfigStore(args.config)
        agent = BacktestingAgent(EventBus(), store, use_process_pool=False)
        state = asyncio.run(agent.run_once(force=True))
        print(json.dumps(agent.last_run, indent=2, default=str))
        sys.exit(0 if state.get("done") else 1)
    try:
        import uvloop  # boucle d'événements plus rapide (Linux/macOS)
        runner = uvloop.run
    except ImportError:
        runner = asyncio.run
    sys.exit(runner(amain(args)))


if __name__ == "__main__":
    main()
