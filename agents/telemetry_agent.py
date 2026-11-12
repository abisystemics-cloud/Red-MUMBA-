"""Agent 6 — Telemetry Agent (l'observateur).

Collecte chaque événement d'exécution (ordres, fills, slippage, latence, PnL,
equity, signaux validés/rejetés) et les envoie :
- à PostHog via l'API `/batch/` (lots toutes les `flush_interval_s`, jamais
  dans le chemin critique : l'envoi réseau est découplé du trading) ;
- dans des fichiers JSONL locaux journaliers (source de vérité de secours,
  lue par l'agent R&D si PostHog est indisponible).

Les dashboards PostHog sont créés par `scripts/posthog_dashboard.py`.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from agents.base import BaseAgent
from core.events import Topic

EVENT_PREFIX = "hlswarm_"


class TelemetryAgent(BaseAgent):
    name = "telemetry"

    def __init__(self, bus, store, http_session=None):
        super().__init__(bus, store)
        self._http = http_session
        self.sub = bus.subscribe(Topic.TELEMETRY, self.name, maxsize=50_000)
        self._buf: list[dict] = []
        self.sent = 0
        self.failed_batches = 0
        self.dir = Path(self.cfg.telemetry.local_log_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._day = None
        self._fh = None
        self.api_key = os.getenv("POSTHOG_API_KEY")

    def _local(self, rec: dict) -> None:
        day = rec["timestamp"][:10]
        if day != self._day:
            if self._fh:
                self._fh.close()
            self._day = day
            self._fh = open(self.dir / f"telemetry_{day}.jsonl", "a", encoding="utf-8")
        self._fh.write(json.dumps(rec, separators=(",", ":"), default=str) + "\n")

    def _wrap(self, ev: dict) -> dict:
        ev = dict(ev)
        name = ev.pop("event", "event")
        ts = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        ev.setdefault("network", self.cfg.runtime.network)
        return {"event": EVENT_PREFIX + name, "distinct_id": self.cfg.telemetry.distinct_id,
                "timestamp": ts, "properties": ev}

    async def _flush(self) -> None:
        if not self._buf:
            return
        batch, self._buf = self._buf, []
        if self._fh:
            self._fh.flush()
        if not (self.api_key and self._http):
            return
        url = self.cfg.telemetry.posthog_host.rstrip("/") + "/batch/"
        for i in range(0, len(batch), self.cfg.telemetry.batch_size):
            chunk = batch[i:i + self.cfg.telemetry.batch_size]
            try:
                async with self._http.post(url, json={"api_key": self.api_key, "batch": chunk},
                                           timeout=10) as r:
                    if r.status >= 400:
                        raise RuntimeError(f"HTTP {r.status}")
                self.sent += len(chunk)
            except Exception as exc:  # noqa: BLE001 — la télémétrie n'arrête jamais le trading
                self.failed_batches += 1
                if self.failed_batches % 20 == 1:
                    self.log.warning("posthog batch failed (%s); events kept in local JSONL", exc)

    async def run(self, stop: asyncio.Event) -> None:
        interval = self.cfg.telemetry.flush_interval_s
        last = time.monotonic()
        try:
            while not stop.is_set():
                timeout = max(0.0, interval - (time.monotonic() - last))
                try:
                    ev = await asyncio.wait_for(self.sub.get(), timeout=timeout)
                    rec = self._wrap(ev)
                    self._local(rec)
                    self._buf.append(rec)
                except asyncio.TimeoutError:
                    pass
                if time.monotonic() - last >= interval or len(self._buf) >= self.cfg.telemetry.batch_size:
                    await self._flush()
                    last = time.monotonic()
                    self.beat()
        finally:
            await self._flush()

    async def shutdown(self) -> None:
        await self._flush()
        if self._fh:
            self._fh.close()

    def health(self) -> dict:
        h = super().health()
        h.update(sent=self.sent, failed_batches=self.failed_batches, buffered=len(self._buf),
                 posthog=bool(self.api_key))
        return h


def read_local_telemetry(directory: str | Path, since_ms: int) -> list[dict]:
    out = []
    for p in sorted(Path(directory).glob("telemetry_*.jsonl")):
        with open(p, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                ts = datetime.fromisoformat(rec["timestamp"]).timestamp() * 1000
                if ts >= since_ms:
                    out.append(rec)
    return out
