"""Faux serveurs WebSocket pour tester sans réseau."""
from __future__ import annotations

import asyncio
import json
from typing import Callable


class FakeWS:
    def __init__(self, producer: Callable, sent: list, fail_after: int | None = None):
        self._producer = producer
        self.sent = sent
        self.fail_after = fail_after

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def send(self, raw: str) -> None:
        self.sent.append(json.loads(raw))

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        n = 0
        async for msg in self._producer():
            yield json.dumps(msg)
            n += 1
            if self.fail_after is not None and n >= self.fail_after:
                raise ConnectionResetError("simulated drop")
        while True:  # garde la connexion ouverte
            await asyncio.sleep(3600)
            yield "{}"


def make_connect(routes: dict[str, Callable], sent: dict[str, list], fail_after: int | None = None):
    """routes : préfixe d'URL -> fonction async génératrice de messages."""
    def connect(url: str):
        for prefix, producer in routes.items():
            if url.startswith(prefix):
                return FakeWS(producer, sent.setdefault(prefix, []), fail_after)
        raise ConnectionRefusedError(url)
    return connect
