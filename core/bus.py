"""Bus d'événements asynchrone en mémoire (pub/sub).

Chaque abonné a sa propre file bornée. Si un abonné lent sature sa file, les
messages les plus anciens sont jetés (politique "drop-oldest") : en trading
temps réel, une donnée périmée vaut moins que pas de donnée, et un agent lent
ne doit jamais bloquer le flux des autres.
"""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from typing import Any

from .events import Topic

log = logging.getLogger("core.bus")


class Subscription:
    def __init__(self, topic: Topic, name: str, maxsize: int):
        self.topic = topic
        self.name = name
        self.queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=maxsize)
        self.dropped = 0

    def __aiter__(self):
        return self

    async def __anext__(self) -> Any:
        return await self.queue.get()

    async def get(self) -> Any:
        return await self.queue.get()


class EventBus:
    def __init__(self, default_maxsize: int = 10_000):
        self._subs: dict[Topic, list[Subscription]] = defaultdict(list)
        self._default_maxsize = default_maxsize
        self.published: dict[Topic, int] = defaultdict(int)

    def subscribe(self, topic: Topic, name: str, maxsize: int | None = None) -> Subscription:
        sub = Subscription(topic, name, maxsize or self._default_maxsize)
        self._subs[topic].append(sub)
        return sub

    def publish(self, topic: Topic, msg: Any) -> None:
        """Non bloquant, appelable depuis n'importe quelle coroutine."""
        self.published[topic] += 1
        for sub in self._subs.get(topic, ()):
            q = sub.queue
            if q.full():
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                sub.dropped += 1
                if sub.dropped % 1000 == 1:
                    log.warning("subscriber %s on %s is lagging (dropped=%d)",
                                sub.name, topic.value, sub.dropped)
            q.put_nowait(msg)

    def stats(self) -> dict[str, Any]:
        return {
            "published": {t.value: n for t, n in self.published.items()},
            "lag": {
                f"{s.topic.value}:{s.name}": {"qsize": s.queue.qsize(), "dropped": s.dropped}
                for subs in self._subs.values() for s in subs
            },
        }
