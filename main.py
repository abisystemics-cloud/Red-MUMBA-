"""Point d'entrée : orchestre l'essaim d'agents.

    python main.py --role all        # tout dans un process (dev)
    python main.py --role live       # Pôle 1 : trading temps réel
    python main.py --role research   # Pôle 2 : R&D (conteneur séparé en prod)
    python main.py --optimize        # un cycle R&D forcé (optimisation), puis sortie
    python scripts/backtest.py --from 2026-09-01 --to 2026-10-31   # backtest sur historique
    python main.py --go-live         # rapport go/no-go (code retour 0 = GO, 3 = NO-GO)
    python main.py --demo            # marché synthétique + interface sur http://localhost:8080 (mot de passe : demo)

Chaque agent tourne sous un superviseur qui le redémarre (backoff exponentiel)
s'il plante ; au-delà de `MAX_RESTARTS` en 10 minutes, le process s'arrête
proprement et Docker le relance (état propre). Un serveur HTTP minimal expose
/health (sondes Docker / Render / AWS), /status et l'interface web temps réel
(core/web.py, ui/index.html), protégée par UI_PASSWORD.
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
from agents.ui_state import UIStateAgent
from core.bus import EventBus
from core.config import ConfigStore
from core.logging_setup import setup_logging
from core.web import WebServer

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


def apply_demo(store: ConfigStore) -> None:
    """Mode démo : marché synthétique, paper trading, réglages nerveux pour voir de l'activité."""
    cfg = store.current
    store._cfg = cfg.model_copy(update={
        "runtime": cfg.runtime.model_copy(update={"network": "testnet", "dry_run": True}),
        "data": cfg.data.model_copy(update={
            "record_market_data": False,
            "liquidations": cfg.data.liquidations.model_copy(update={"provider": "disabled"}),
            "whales": cfg.data.whales.model_copy(update={"provider": "disabled"})}),
        "macro": cfg.macro.model_copy(update={"enabled": False}),
        "strategy": cfg.strategy.model_copy(update={
            "entry_threshold": 0.8, "persistence_ticks": 2, "cooldown_s": 20, "max_hold_s": 300,
            "zscore_window": 300, "cvd_window_s": 60, "max_spread_bps": 10}),
        "execution": cfg.execution.model_copy(update={"maker_timeout_s": 10}),
        "telemetry": cfg.telemetry.model_copy(update={"local_log_dir": "data/demo_telemetry"}),
        "research": cfg.research.model_copy(update={"enabled": False}),
        "control": cfg.control.model_copy(update={"enabled": False}),
    })


async def amain(args) -> int:
    store = ConfigStore(args.config)
    if args.demo:
        apply_demo(store)
        os.environ.setdefault("UI_PASSWORD", "demo")
        for k in ("POSTHOG_API_KEY", "TELEGRAM_BOT_TOKEN", "PERPLEXITY_API_KEY", "CONTROL_GITHUB_REPO"):
            os.environ.pop(k, None)
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

    demo_extra = None
    data_kw = {}
    if args.demo:
        from demo.feeds import demo_connect
        connect, demo_extra = demo_connect([m.coin for m in cfg.markets], speed=args.demo_speed)
        data_kw["connect_fn"] = connect

    agents: list[BaseAgent] = []
    if args.role in ("all", "live"):
        agents += [
            HyperliquidDataAgent(bus, store, http_session=http, **data_kw),
            QuantAgent(bus, store),
            MacroEdgeAgent(bus, store, http_session=http),
            ValidationAgent(bus, store),
            ExecutionAgent(bus, store, make_broker(store)),
        ]
    if args.role in ("all", "research"):
        agents.append(BacktestingAgent(bus, store, http_session=http))
    agents.append(TelemetryAgent(bus, store, http_session=http))
    agents.append(ControlAgent(bus, store, args.role, lambda: compact_status(agents), http_session=http))
    ui = None
    if args.role in ("all", "live"):
        ui = UIStateAgent(bus, store, lambda: {a.name: a.health() for a in agents})
        agents.append(ui)

    log.info("starting swarm role=%s network=%s dry_run=%s demo=%s agents=%s", args.role,
             cfg.runtime.network, cfg.runtime.dry_run, args.demo, [a.name for a in agents])
    tasks = [asyncio.create_task(supervise(a, stop, fatal), name=a.name) for a in agents]
    if not args.demo:
        tasks.append(asyncio.create_task(store.watch(stop), name="config-watch"))
    if demo_extra:
        tasks.append(asyncio.create_task(demo_extra(bus, stop), name="demo-positioning"))

    def health() -> dict:
        stale = [a.name for a in agents if a.health().get("stale")]
        return {"ok": not stale, "stale": stale}

    web = WebServer(bus=bus, store=store, health_fn=health,
                    status_fn=lambda: {"agents": {a.name: a.health() for a in agents}, "bus": bus.stats(),
                                       "config_reloads": store.reload_count,
                                       "network": store.current.runtime.network,
                                       "dry_run": store.current.runtime.dry_run},
                    snapshot_fn=ui.snapshot if ui else None)
    port = int(os.getenv("PORT", cfg.runtime.health_port))
    tasks.append(asyncio.create_task(web.serve(port, stop), name="web"))
    if args.demo:
        log.warning("DEMO: open http://localhost:%d  (password: %s)", port,
                    "demo" if os.environ.get("UI_PASSWORD") == "demo" else "UI_PASSWORD")

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
    p.add_argument("--optimize", action="store_true", help="run one forced research (optimization) cycle and exit")
    p.add_argument("--go-live", action="store_true", help="print the go/no-go report and exit")
    p.add_argument("--demo", action="store_true", help="synthetic market + paper trading + UI (no network, no keys)")
    p.add_argument("--demo-speed", type=float, default=3.0, help="demo time acceleration (1 = real time)")
    args = p.parse_args()
    if args.go_live:
        setup_logging("WARNING")
        store = ConfigStore(args.config)
        agent = BacktestingAgent(EventBus(), store, use_process_pool=False)
        rep = asyncio.run(agent.go_live_report())
        from ml_engine.go_live import format_report
        print(format_report(rep))
        sys.exit(0 if rep["go"] else 3)
    if args.optimize:
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
