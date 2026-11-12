"""Agent 7 — Backtesting & Adaptive Learning Agent (le scientifique).

Boucle de fond orchestrée par un graphe LangGraph (repli intégré si LangGraph
n'est pas installé) :

  collect_performance ─▶ assess ──(sain)──▶ FIN
                           │
                       (dégradé)
                           ▼
                     explore_data ──(données insuffisantes)──▶ FIN
                           ▼
                       optimize   (walk-forward, process séparé)
                           ▼
                        deploy    (réécriture atomique de config.yaml
                                   → hot-reload, WebSockets intacts)

Le calcul lourd tourne dans un ProcessPoolExecutor pour ne jamais bloquer
la boucle asyncio du trading quand tout tourne dans un seul conteneur.

Par défaut (`auto_deploy: false`) l'agent PROPOSE : il écrit
`config.proposed.yaml` et envoie une alerte ; un humain valide en copiant la
section dans config.yaml. Il produit aussi un rapport go/no-go périodique
(`go_live`) dans `data/reports/`.
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Callable, Optional, TypedDict

import yaml

from agents.base import BaseAgent
from agents.telemetry_agent import read_local_telemetry
from core.config import ExecutionCfg, RiskCfg, ResearchCfg, StrategyCfg, atomic_update_strategy
from core.events import Topic, now_ms
from ml_engine.go_live import evaluate as go_live_evaluate
from ml_engine.go_live import format_report
from ml_engine.recorder import load_events


class ResearchState(TypedDict, total=False):
    force: bool
    perf: dict
    degraded: bool
    reason: str
    profile: dict
    records: list
    report: dict
    deployed: bool
    done: str


# ---------------------------------------------------------- mini-graphe
class _MiniGraph:
    """Sous-ensemble de l'API StateGraph de LangGraph (repli sans dépendance)."""

    END = "__end__"

    def __init__(self):
        self.nodes: dict[str, Callable] = {}
        self.edges: dict[str, str] = {}
        self.cond: dict[str, tuple[Callable, dict]] = {}
        self.entry = None

    def add_node(self, name, fn):
        self.nodes[name] = fn

    def add_edge(self, a, b):
        self.edges[a] = b

    def add_conditional_edges(self, a, router, mapping):
        self.cond[a] = (router, mapping)

    def set_entry_point(self, name):
        self.entry = name

    def compile(self):
        return self

    async def ainvoke(self, state: dict) -> dict:
        node = self.entry
        while node and node != self.END:
            upd = await self.nodes[node](state)
            state = {**state, **(upd or {})}
            if node in self.cond:
                router, mapping = self.cond[node]
                node = mapping[router(state)]
            else:
                node = self.edges.get(node, self.END)
        return state


def _build_graph(nodes: dict[str, Callable], routers: dict[str, Callable]):
    try:
        from langgraph.graph import END, StateGraph
        g = StateGraph(ResearchState)
    except ImportError:  # pragma: no cover — dépend de l'environnement
        g, END = _MiniGraph(), _MiniGraph.END
    for n, fn in nodes.items():
        g.add_node(n, fn)
    g.set_entry_point("collect_performance")
    g.add_edge("collect_performance", "assess")
    g.add_conditional_edges("assess", routers["assess"], {"explore": "explore_data", "stop": END})
    g.add_conditional_edges("explore_data", routers["explore"], {"optimize": "optimize", "stop": END})
    g.add_edge("optimize", "deploy")
    g.add_edge("deploy", END)
    return g.compile()


# ------------------------------------------------ calcul (process séparé)
def _optimize_job(records: list, strategy: dict, risk: dict, research: dict, seed: int,
                  execution: dict | None = None) -> dict:
    from ml_engine.optimizer import optimize
    rep = optimize(records, StrategyCfg.model_validate(strategy), RiskCfg.model_validate(risk),
                   ResearchCfg.model_validate(research), seed=seed,
                   exec_cfg=ExecutionCfg.model_validate(execution) if execution else None)
    return {"accepted": rep.accepted, "reason": rep.reason, "current_oos": rep.current_oos,
            "best_oos": rep.best_oos, "best_params": rep.best_params, "trials": rep.trials}


def performance_from_trades(pnls: list[float], rs: list[float]) -> dict:
    n = len(pnls)
    if n == 0:
        return {"n_trades": 0}
    wins = sum(p > 0 for p in pnls)
    m = sum(rs) / n if rs else 0.0
    sd = math.sqrt(sum((r - m) ** 2 for r in rs) / (n - 1)) if n > 1 else 0.0
    if sd > 0:
        sharpe = m / sd * math.sqrt(n)
    else:
        sharpe = float("inf") if m > 0 else (float("-inf") if m < 0 else 0.0)
    eq, peak, mdd = 0.0, 0.0, 0.0
    for p in pnls:
        eq += p
        peak = max(peak, eq)
        mdd = max(mdd, peak - eq)
    return {"n_trades": n, "win_rate": wins / n, "pnl": sum(pnls),
            "sharpe_per_trade": sharpe, "max_dd_abs": mdd}


class BacktestingAgent(BaseAgent):
    name = "research"

    def __init__(self, bus, store, http_session=None, use_process_pool: bool = True):
        super().__init__(bus, store)
        self._http = http_session
        self._pool = ProcessPoolExecutor(max_workers=1) if use_process_pool else None
        self.last_run: Optional[dict] = None
        self.runs = 0
        self.stale_after_s = self.cfg.research.check_interval_s * 2 + 3600
        self.ctl = bus.subscribe(Topic.CONTROL, self.name, maxsize=16)
        self.graph = _build_graph(
            {"collect_performance": self.collect_performance, "assess": self.assess,
             "explore_data": self.explore_data, "optimize": self.optimize, "deploy": self.deploy},
            {"assess": lambda s: "explore" if s.get("degraded") else "stop",
             "explore": lambda s: "optimize" if s.get("records") else "stop"})

    # ---------------------------------------------------------- nodes
    async def _posthog_trades(self, hours: int) -> Optional[list[list[Any]]]:
        key, pid = os.getenv("POSTHOG_PERSONAL_API_KEY"), os.getenv("POSTHOG_PROJECT_ID")
        if not (key and pid and self._http):
            return None
        host = os.getenv("POSTHOG_API_HOST") or self.cfg.telemetry.posthog_host.replace(".i.posthog.com", ".posthog.com")
        q = ("SELECT timestamp, toFloat(properties.pnl), toFloat(properties.r_multiple) FROM events "
             f"WHERE event = 'hlswarm_trade_closed' AND timestamp > now() - INTERVAL {int(hours)} HOUR "
             f"AND properties.network = '{self.cfg.runtime.network}' ORDER BY timestamp LIMIT 10000")
        async with self._http.post(f"{host.rstrip('/')}/api/projects/{pid}/query/",
                                   json={"query": {"kind": "HogQLQuery", "query": q}},
                                   headers={"Authorization": f"Bearer {key}"}, timeout=60) as r:
            r.raise_for_status()
            return (await r.json()).get("results", [])

    async def closed_trades(self, hours: int) -> tuple[list[list[Any]], str]:
        """[[timestamp, pnl, r_multiple], …] depuis PostHog, sinon la télémétrie locale."""
        try:
            rows = await self._posthog_trades(hours)
            if rows is not None:
                return rows, "posthog"
        except Exception as exc:  # noqa: BLE001
            self.log.warning("PostHog query failed (%s) → local telemetry", exc)
        since = now_ms() - hours * 3_600_000
        recs = [r for r in read_local_telemetry(self.cfg.telemetry.local_log_dir, since)
                if r["event"] == "hlswarm_trade_closed"
                and r["properties"].get("network", self.cfg.runtime.network) == self.cfg.runtime.network]
        return [[r["timestamp"], r["properties"].get("pnl"), r["properties"].get("r_multiple")] for r in recs], "local"

    async def collect_performance(self, s: ResearchState) -> dict:
        rows, source = await self.closed_trades(self.cfg.research.lookback_hours)
        pnls = [float(r[1] or 0) for r in rows]
        rs = [float(r[2] or 0) for r in rows]
        perf = performance_from_trades(pnls, rs)
        perf["source"] = source
        return {"perf": perf}

    async def assess(self, s: ResearchState) -> dict:
        rc, p = self.cfg.research, s["perf"]
        if s.get("force"):
            return {"degraded": True, "reason": "forced run"}
        if p["n_trades"] < rc.min_trades_for_eval:
            return {"degraded": False, "reason": f"only {p['n_trades']} trades (< {rc.min_trades_for_eval})",
                    "done": "insufficient_trades"}
        why = []
        if p["sharpe_per_trade"] < rc.degrade_sharpe_below:
            why.append(f"sharpe {p['sharpe_per_trade']:.2f} < {rc.degrade_sharpe_below}")
        if p["win_rate"] < rc.degrade_winrate_below:
            why.append(f"win rate {p['win_rate']:.2f} < {rc.degrade_winrate_below}")
        return {"degraded": bool(why), "reason": "; ".join(why) or "healthy",
                "done": None if why else "healthy"}

    async def explore_data(self, s: ResearchState) -> dict:
        rc = self.cfg.research
        since = now_ms() - rc.lookback_hours * 3_600_000
        recs = await asyncio.to_thread(load_events, self.cfg.data.recordings_dir, since)
        prof: dict[str, Any] = {"events": len(recs), "by_type": {}, "by_coin": {}, "max_gap_s": 0.0}
        last_book: dict[str, int] = {}
        for r in recs:
            prof["by_type"][r["t"]] = prof["by_type"].get(r["t"], 0) + 1
            prof["by_coin"][r["coin"]] = prof["by_coin"].get(r["coin"], 0) + 1
            if r["t"] == "book":
                lb = last_book.get(r["coin"])
                if lb:
                    prof["max_gap_s"] = max(prof["max_gap_s"], (r["ts"] - lb) / 1000)
                last_book[r["coin"]] = r["ts"]
        if prof["by_type"].get("book", 0) < 2000:
            return {"profile": prof, "records": [], "done": "insufficient_market_data"}
        return {"profile": prof, "records": recs}

    async def optimize(self, s: ResearchState) -> dict:
        args = (s["records"], self.cfg.strategy.model_dump(), self.cfg.risk.model_dump(),
                self.cfg.research.model_dump(), now_ms() % 2 ** 31, self.cfg.execution.model_dump())
        if self._pool:
            rep = await asyncio.get_running_loop().run_in_executor(self._pool, _optimize_job, *args)
        else:
            rep = await asyncio.to_thread(_optimize_job, *args)
        return {"report": rep, "records": []}  # libère la mémoire

    async def deploy(self, s: ResearchState) -> dict:
        rep = s["report"]
        if not rep["accepted"]:
            return {"deployed": False, "done": f"rejected: {rep['reason']}"}
        path = Path(self.store.path)
        if self.cfg.research.auto_deploy:
            backup = await asyncio.to_thread(atomic_update_strategy, path, rep["best_params"])
            await self.store.check_reload()  # applique immédiatement dans ce process
            self.log.warning("NEW STRATEGY DEPLOYED (backup %s): %s", backup, rep["best_oos"])
            return {"deployed": True, "done": "deployed"}
        prop = path.with_suffix(".proposed.yaml")
        prop.write_text(yaml.safe_dump({"strategy": rep["best_params"], "oos": rep["best_oos"],
                                        "current_oos": rep["current_oos"]},
                                       sort_keys=False), encoding="utf-8")
        return {"deployed": False, "done": f"proposal written to {prop.name} (validation humaine requise)"}

    # -------------------------------------------------------- go / no-go
    async def go_live_report(self) -> dict:
        gl = self.cfg.go_live
        rows, source = await self.closed_trades(int(gl.weeks * 7 * 24))
        rep = go_live_evaluate([(r[0], r[1]) for r in rows], self.cfg.risk.paper_equity_usd, gl)
        rep["source"] = source
        rep["network"] = self.cfg.runtime.network
        out = Path(self.cfg.data.recordings_dir).parent / "reports"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"go_live_{time.strftime('%Y%m%d', time.gmtime())}.json").write_text(
            json.dumps(rep, indent=2, default=str), encoding="utf-8")
        text = format_report(rep)
        self.bus.publish(Topic.TELEMETRY, {"event": "go_live_report", "verdict": rep["verdict"],
                                           "criteria": rep["criteria"], "text": text})
        self.log.info(text)
        return rep

    # ------------------------------------------------------------ run
    async def run_once(self, force: bool = False) -> dict:
        state = await self.graph.ainvoke({"force": force})
        self.runs += 1
        summary = {k: state.get(k) for k in ("perf", "degraded", "reason", "profile", "report", "deployed", "done")}
        if summary.get("report"):
            summary["report"] = {k: v for k, v in summary["report"].items() if k != "best_params"}
        self.last_run = summary
        self.bus.publish(Topic.TELEMETRY, {"event": "research_run", **{
            k: v for k, v in summary.items() if k != "profile"}})
        self.log.info("research run: %s", summary.get("done") or summary.get("reason"))
        return state

    async def _control(self) -> None:
        while True:
            c = await self.ctl.get()
            try:
                if c.cmd == "go_live_report":
                    rep = await self.go_live_report()
                    result = rep["verdict"]
                elif c.cmd == "research_run":
                    st = await self.run_once(force=True)
                    result = st.get("done") or st.get("reason")
                else:
                    continue
            except Exception as exc:  # noqa: BLE001
                result = f"failed: {exc}"
            self.bus.publish(Topic.TELEMETRY, {"event": "command_applied", "command_id": c.id, "cmd": c.cmd,
                                               "agent": self.name, "result": result})

    async def run(self, stop: asyncio.Event) -> None:
        ctl_task = asyncio.create_task(self._control())
        try:
            await self._run(stop)
        finally:
            ctl_task.cancel()

    async def _run(self, stop: asyncio.Event) -> None:
        if not self.cfg.research.enabled:
            await stop.wait()
            return
        await asyncio.sleep(5)
        last_report = 0.0
        while not stop.is_set():
            try:
                await self.run_once(force=os.getenv("RESEARCH_FORCE") == "1")
            except Exception:  # noqa: BLE001
                self.errors += 1
                self.log.exception("research run failed")
            if time.monotonic() - last_report >= self.cfg.go_live.report_interval_h * 3600 or not last_report:
                try:
                    await self.go_live_report()
                    last_report = time.monotonic()
                except Exception:  # noqa: BLE001
                    self.errors += 1
                    self.log.exception("go-live report failed")
            self.beat()
            try:
                await asyncio.wait_for(stop.wait(), timeout=self.cfg.research.check_interval_s)
            except asyncio.TimeoutError:
                pass

    async def shutdown(self) -> None:
        if self._pool:
            self._pool.shutdown(wait=False, cancel_futures=True)

    def health(self) -> dict:
        h = super().health()
        h.update(runs=self.runs, last=self.last_run and self.last_run.get("done"))
        return h
