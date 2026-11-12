"""Classe de base des agents : cycle de vie, santé, accès bus/config."""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from core.bus import EventBus
from core.config import AppConfig, ConfigStore


class BaseAgent:
    name: str = "agent"
    stale_after_s: float = 90.0   # /health renvoie 503 au-delà

    def __init__(self, bus: EventBus, store: ConfigStore):
        self.bus = bus
        self.store = store
        self.log = logging.getLogger(f"agent.{self.name}")
        self.started_at = time.time()
        self.last_heartbeat = time.monotonic()
        self.errors = 0
        store.subscribe(self._on_config)

    @property
    def cfg(self) -> AppConfig:
        return self.store.current

    def beat(self) -> None:
        self.last_heartbeat = time.monotonic()

    async def _on_config(self, old: AppConfig, new: AppConfig) -> None:
        await self.on_config_change(old, new)

    async def on_config_change(self, old: AppConfig, new: AppConfig) -> None:  # override
        return None

    async def run(self, stop: asyncio.Event) -> None:  # override
        raise NotImplementedError

    async def shutdown(self) -> None:  # override
        return None

    def health(self) -> dict[str, Any]:
        return {
            "alive_s": round(time.time() - self.started_at, 1),
            "since_heartbeat_s": round(time.monotonic() - self.last_heartbeat, 2),
            "errors": self.errors,
            "stale": time.monotonic() - self.last_heartbeat > self.stale_after_s,
        }
