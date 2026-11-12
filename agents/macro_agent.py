"""Agent 3 — Macro Edge Agent (le radar / kill switch).

Le niveau de risque global (NORMAL / CAUTION / HALT) est le MAXIMUM de
plusieurs détecteurs indépendants — aucun ne peut en abaisser un autre :

1. Kill switch manuel : présence du fichier `data/KILL` → HALT immédiat.
2. Fenêtres d'annonces macro planifiées (FOMC, CPI…) → HALT.
3. Choc de marché : |variation BTC sur 60 s| sur Binance > seuil → HALT.
4. Intégrité des données : divergence Binance/Bybit > seuil → HALT
   (un des flux est faux ou un venue est en train de casser).
5. Radar actualité : un LLM de recherche web (Perplexity Sonar) note le
   risque "cygne noir" ∈ [0, 1] toutes les `poll_seconds`. Il ne peut
   qu'escalader vers CAUTION/HALT, jamais ouvrir ni agrandir un trade.

Le LLM est hors du chemin critique : son résultat est mis en cache et lu
par la boucle d'évaluation, qui tourne en continu sans l'attendre.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

from agents.base import BaseAgent
from core.events import MacroState, RiskLevel, Topic, now_ms

ORDER = {RiskLevel.NORMAL: 0, RiskLevel.CAUTION: 1, RiskLevel.HALT: 2}

LLM_PROMPT = (
    "You are a risk officer for a crypto perpetual futures desk. Using only news from the "
    "last 6 hours, assess the probability of an extreme market dislocation in BTC/ETH in the "
    "next 2 hours (exchange hack or insolvency, stablecoin depeg, major regulatory action, "
    "war/terror event, surprise central-bank move, Hyperliquid outage or exploit). "
    'Answer ONLY with JSON: {"risk_score": <0..1>, "events": ["..."], "summary": "..."}'
)


def parse_llm_json(text: str) -> Optional[dict]:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
        s = float(d.get("risk_score"))
        if not 0 <= s <= 1:
            return None
        d["risk_score"] = s
        return d
    except (ValueError, TypeError):
        return None


class MacroEdgeAgent(BaseAgent):
    name = "macro"

    def __init__(self, bus, store, http_session=None, kill_file: str = "data/KILL"):
        super().__init__(bus, store)
        self._http = http_session
        self.kill_file = Path(kill_file)
        self.sub = bus.subscribe(Topic.EXT_QUOTE, self.name, maxsize=4096)
        self._btc: deque[tuple[int, float]] = deque()
        self._last_mid: dict[tuple[str, str], tuple[int, float]] = {}
        self.llm: Optional[dict] = None
        self.llm_ts = 0
        self.state = MacroState(now_ms(), RiskLevel.NORMAL, [])
        self.supervisor_pause: Optional[str] = None
        self.ctl = bus.subscribe(Topic.CONTROL, self.name, maxsize=64)

    # --------------------------------------------------------- detectors
    def _on_quote(self, q) -> None:
        self._last_mid[(q.venue, q.coin)] = (q.ts, q.mid)
        if q.coin == "BTC" and q.venue == "binance":
            self._btc.append((q.ts, q.mid))
            while self._btc and self._btc[0][0] < q.ts - 60_000:
                self._btc.popleft()

    def evaluate(self, now: Optional[int] = None) -> MacroState:
        now = now or now_ms()
        mc = self.cfg.macro
        level, reasons = RiskLevel.NORMAL, []

        def raise_to(lv: RiskLevel, why: str) -> None:
            nonlocal level
            reasons.append(why)
            if ORDER[lv] > ORDER[level]:
                level = lv

        if self.kill_file.exists():
            raise_to(RiskLevel.HALT, "manual kill switch file present")
        if self.supervisor_pause is not None:
            raise_to(RiskLevel.HALT, f"supervisor pause: {self.supervisor_pause}")

        for ev in mc.scheduled_events:
            try:
                at = int(datetime.fromisoformat(ev.at.replace("Z", "+00:00")).timestamp() * 1000)
            except ValueError:
                continue
            if at - mc.blackout_minutes_before * 60_000 <= now <= at + mc.blackout_minutes_after * 60_000:
                raise_to(RiskLevel.HALT, f"scheduled event blackout: {ev.name}")

        if len(self._btc) >= 2 and now - self._btc[-1][0] < 5_000:
            lo = min(p for _, p in self._btc)
            hi = max(p for _, p in self._btc)
            move = (hi / lo - 1) * 100
            if move >= mc.btc_1m_move_halt_pct:
                raise_to(RiskLevel.HALT, f"BTC 60s range {move:.2f}% >= {mc.btc_1m_move_halt_pct}%")

        for m in self.cfg.markets:
            a = self._last_mid.get(("binance", m.coin))
            b = self._last_mid.get(("bybit", m.coin))
            if a and b and now - a[0] < 5_000 and now - b[0] < 5_000:
                div = abs(a[1] / b[1] - 1) * 1e4
                if div >= mc.cex_divergence_halt_bps:
                    raise_to(RiskLevel.HALT, f"{m.coin} Binance/Bybit divergence {div:.0f}bps")

        if self.llm and now - self.llm_ts < 2 * mc.poll_seconds * 1000:
            s = self.llm["risk_score"]
            if s >= mc.llm_halt_threshold:
                raise_to(RiskLevel.HALT, f"news radar risk {s:.2f}: {self.llm.get('summary', '')[:160]}")
            elif s >= mc.llm_caution_threshold:
                raise_to(RiskLevel.CAUTION, f"news radar risk {s:.2f}")

        return MacroState(now, level, reasons, self.llm["risk_score"] if self.llm else None)

    # ------------------------------------------------------------- LLM
    async def _query_llm(self) -> Optional[dict]:
        key = os.getenv("PERPLEXITY_API_KEY")
        if not key or self._http is None:
            return None
        body = {"model": self.cfg.macro.llm_model, "temperature": 0,
                "messages": [{"role": "user", "content": LLM_PROMPT}]}
        async with self._http.post("https://api.perplexity.ai/chat/completions", json=body,
                                   headers={"Authorization": f"Bearer {key}"}, timeout=60) as r:
            r.raise_for_status()
            data = await r.json()
        return parse_llm_json(data["choices"][0]["message"]["content"])

    async def _llm_loop(self, stop: asyncio.Event) -> None:
        if not self.cfg.macro.enabled:
            return
        while not stop.is_set():
            try:
                res = await self._query_llm()
                if res:
                    self.llm, self.llm_ts = res, now_ms()
                    self.log.info("news radar risk_score=%.2f events=%s", res["risk_score"], res.get("events"))
            except Exception as exc:  # noqa: BLE001 — l'échec du radar ne bloque rien
                self.errors += 1
                self.log.warning("news radar failed: %s", exc)
            try:
                await asyncio.wait_for(stop.wait(), timeout=self.cfg.macro.poll_seconds)
            except asyncio.TimeoutError:
                pass

    async def _control(self) -> None:
        while True:
            c = await self.ctl.get()
            if c.cmd == "pause":
                self.supervisor_pause = c.reason or "no reason given"
            elif c.cmd == "resume":
                self.supervisor_pause = None
            else:
                continue
            self.bus.publish(Topic.TELEMETRY, {"event": "command_applied", "command_id": c.id, "cmd": c.cmd, "agent": self.name, "paused": self.supervisor_pause is not None})

    async def _quotes(self) -> None:
        while True:
            self._on_quote(await self.sub.get())

    async def run(self, stop: asyncio.Event) -> None:
        tasks = [asyncio.create_task(self._quotes()), asyncio.create_task(self._llm_loop(stop)),
                 asyncio.create_task(self._control())]
        last_pub = 0.0
        try:
            while not stop.is_set():
                st = self.evaluate()
                changed = st.level != self.state.level
                if changed:
                    self.log.warning("RISK LEVEL %s -> %s %s", self.state.level.value, st.level.value, st.reasons)
                    self.bus.publish(Topic.TELEMETRY, {"event": "risk_level", "level": st.level.value,
                                                       "previous": self.state.level.value, "reasons": st.reasons})
                if changed or time.monotonic() - last_pub > 5:
                    self.bus.publish(Topic.RISK_STATE, st)
                    last_pub = time.monotonic()
                self.state = st
                self.beat()
                await asyncio.sleep(0.25)
        finally:
            for t in tasks:
                t.cancel()

    def health(self) -> dict:
        h = super().health()
        h["level"] = self.state.level.value
        h["reasons"] = self.state.reasons
        h["llm_risk_score"] = self.state.llm_risk_score
        h["paused"] = self.supervisor_pause
        return h
