"""Client WebSocket résilient.

- Reconnexion automatique, backoff exponentiel plafonné + jitter.
- Réabonnement automatique de toutes les souscriptions après reconnexion.
- Heartbeat applicatif configurable (Hyperliquid : {"method":"ping"} ;
  Bybit : {"op":"ping"}) en plus des ping/pong du protocole.
- Watchdog de silence : si aucun message n'arrive pendant `stale_after_s`,
  la connexion est considérée morte et recyclée (cas des sockets "zombies").
- Le connecteur (`connect_fn`) est injectable pour les tests.
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from typing import Any, Awaitable, Callable, Optional

log = logging.getLogger("core.ws")

MessageHandler = Callable[[Any], Awaitable[None] | None]


def _default_connect(url: str):
    import websockets  # import tardif : dépendance runtime seulement

    return websockets.connect(
        url,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=5,
        max_size=2 ** 24,
        open_timeout=10,
    )


class ResilientWebSocket:
    def __init__(
        self,
        name: str,
        url: str,
        on_message: MessageHandler,
        *,
        heartbeat_msg: Optional[dict] = None,
        heartbeat_s: float = 30.0,
        stale_after_s: float = 45.0,
        backoff_base_s: float = 0.5,
        backoff_max_s: float = 30.0,
        connect_fn: Callable[[str], Any] = _default_connect,
        on_connect: Optional[Callable[[], Awaitable[None] | None]] = None,
    ):
        self.name = name
        self.url = url
        self.on_message = on_message
        self.heartbeat_msg = heartbeat_msg
        self.heartbeat_s = heartbeat_s
        self.stale_after_s = stale_after_s
        self.backoff_base_s = backoff_base_s
        self.backoff_max_s = backoff_max_s
        self.connect_fn = connect_fn
        self.on_connect = on_connect

        self._subscriptions: list[dict] = []
        self._ws = None
        self._last_msg = time.monotonic()
        self.connected = asyncio.Event()
        self.reconnects = 0
        self.messages = 0
        self.last_error: Optional[str] = None

    # ------------------------------------------------------------------ API
    def add_subscription(self, msg: dict) -> None:
        """Enregistre une souscription (rejouée à chaque (re)connexion)."""
        self._subscriptions.append(msg)

    async def send(self, msg: dict) -> None:
        if self._ws is not None:
            await self._ws.send(json.dumps(msg, separators=(",", ":")))

    @property
    def seconds_since_last_message(self) -> float:
        return time.monotonic() - self._last_msg

    async def run(self, stop: asyncio.Event) -> None:
        attempt = 0
        while not stop.is_set():
            try:
                async with self.connect_fn(self.url) as ws:
                    self._ws = ws
                    self._last_msg = time.monotonic()
                    for sub in self._subscriptions:
                        await self.send(sub)
                    if self.on_connect:
                        r = self.on_connect()
                        if asyncio.iscoroutine(r):
                            await r
                    self.connected.set()
                    log.info("[%s] connected %s (%d subs)", self.name, self.url, len(self._subscriptions))
                    attempt = 0
                    await self._session(ws, stop)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 — toute erreur => reconnexion
                self.last_error = f"{type(exc).__name__}: {exc}"
                log.warning("[%s] connection error: %s", self.name, self.last_error)
            finally:
                self._ws = None
                self.connected.clear()
            if stop.is_set():
                break
            attempt += 1
            self.reconnects += 1
            delay = min(self.backoff_max_s, self.backoff_base_s * 2 ** min(attempt, 10))
            delay *= random.uniform(0.5, 1.0)
            log.info("[%s] reconnecting in %.2fs (attempt %d)", self.name, delay, attempt)
            try:
                await asyncio.wait_for(stop.wait(), timeout=delay)
            except asyncio.TimeoutError:
                pass

    # ------------------------------------------------------------ internals
    async def _session(self, ws, stop: asyncio.Event) -> None:
        reader = asyncio.create_task(self._reader(ws))
        keeper = asyncio.create_task(self._keepalive())
        stopper = asyncio.create_task(stop.wait())
        done, pending = await asyncio.wait(
            {reader, keeper, stopper}, return_when=asyncio.FIRST_COMPLETED
        )
        for t in pending:
            t.cancel()
        for t in done:
            if t is not stopper and t.exception():
                raise t.exception()  # type: ignore[misc]

    async def _reader(self, ws) -> None:
        async for raw in ws:
            self._last_msg = time.monotonic()
            self.messages += 1
            try:
                msg = json.loads(raw)
            except (TypeError, ValueError):
                continue
            try:
                r = self.on_message(msg)
                if asyncio.iscoroutine(r):
                    await r
            except Exception:  # noqa: BLE001 — un message corrompu ne tue pas la socket
                log.exception("[%s] handler error", self.name)
        raise ConnectionError("server closed the connection")

    async def _keepalive(self) -> None:
        interval = min(self.heartbeat_s, self.stale_after_s / 3)
        last_hb = time.monotonic()
        while True:
            await asyncio.sleep(interval)
            if self.seconds_since_last_message > self.stale_after_s:
                raise TimeoutError(f"no message for {self.stale_after_s}s (stale socket)")
            if self.heartbeat_msg and time.monotonic() - last_hb >= self.heartbeat_s:
                await self.send(self.heartbeat_msg)
                last_hb = time.monotonic()
