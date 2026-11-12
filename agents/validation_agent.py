"""Agent 4 — Validation Agent (l'auditeur).

Croise chaque signal d'ENTRÉE de l'agent Quant avec l'état macro et la qualité
des données, et rejette les faux positifs. Règles fail-closed : au moindre
doute (donnée périmée, état macro inconnu), on ne trade pas.

Les signaux FLAT (sorties) passent toujours : un filtre ne doit jamais
empêcher de RÉDUIRE le risque.
"""
from __future__ import annotations

import asyncio
from collections import Counter

from agents.base import BaseAgent
from core.events import MacroState, RiskLevel, Side, Signal, Topic, now_ms

MACRO_STALE_MS = 15_000
SPOOF_REJECT = 0.6
PREMIUM_CHASE_Z = 2.0
FUNDING_AGAINST = 5e-4   # taux horaire Hyperliquid


def validate(sig: Signal, macro: MacroState | None, cfg, now: int) -> list[str]:
    """Retourne la liste des motifs de rejet (vide = validé)."""
    if sig.side == Side.FLAT:
        return []
    f, st = sig.features, cfg.strategy
    why: list[str] = []
    if macro is None or now - macro.ts > MACRO_STALE_MS:
        why.append("macro state unknown/stale")
    elif macro.level == RiskLevel.HALT:
        why.append("macro HALT: " + "; ".join(macro.reasons)[:200])
    if f.book_age_ms > cfg.data.max_staleness_ms:
        why.append(f"book stale {f.book_age_ms}ms")
    if f.ext_age_ms > cfg.data.max_staleness_ms:
        why.append("external reference prices stale")
    if f.spread_bps > st.max_spread_bps:
        why.append(f"spread {f.spread_bps:.1f}bps > {st.max_spread_bps}")
    long_ = sig.side == Side.LONG
    if (long_ and f.spoof_bid > SPOOF_REJECT) or (not long_ and f.spoof_ask > SPOOF_REJECT):
        why.append("supporting book side looks spoofed")
    if (long_ and f.premium_z > PREMIUM_CHASE_Z) or (not long_ and f.premium_z < -PREMIUM_CHASE_Z):
        why.append("chasing: HL already priced past CEX reference")
    if (long_ and f.funding > FUNDING_AGAINST) or (not long_ and f.funding < -FUNDING_AGAINST):
        why.append(f"funding {f.funding:.5f} against position")
    return why


class ValidationAgent(BaseAgent):
    name = "validation"

    def __init__(self, bus, store):
        super().__init__(bus, store)
        self.sig_sub = bus.subscribe(Topic.SIGNAL, self.name, maxsize=256)
        self.risk_sub = bus.subscribe(Topic.RISK_STATE, self.name, maxsize=64)
        self.macro: MacroState | None = None
        self.stats: Counter = Counter()
        self._last_tele: dict[str, tuple] = {}

    async def _risk(self) -> None:
        while True:
            self.macro = await self.risk_sub.get()

    async def run(self, stop: asyncio.Event) -> None:
        rt = asyncio.create_task(self._risk())
        try:
            while not stop.is_set():
                try:
                    sig: Signal = await asyncio.wait_for(self.sig_sub.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                reasons = validate(sig, self.macro, self.cfg, now_ms())
                sig.validated = not reasons
                sig.rejections = reasons
                if sig.side != Side.FLAT:
                    self.stats["accepted" if sig.validated else "rejected"] += 1
                    for r in reasons:
                        self.stats[r.split(":")[0].split(" ")[0]] += 1
                self.bus.publish(Topic.VALIDATED, sig)
                key = (sig.side, sig.validated, tuple(r.split(" ")[0] for r in reasons))
                prev = self._last_tele.get(sig.coin)
                if sig.side != Side.FLAT and (prev is None or prev[0] != key or sig.ts - prev[1] > 30_000):
                    # télémétrie sur changement d'état seulement (coût PostHog maîtrisé)
                    self._last_tele[sig.coin] = (key, sig.ts)
                    self.bus.publish(Topic.TELEMETRY, {
                        "event": "signal", "coin": sig.coin, "side": sig.side.value,
                        "score": round(sig.score, 3), "validated": sig.validated,
                        "rejections": reasons})
                self.beat()
        finally:
            rt.cancel()

    def health(self) -> dict:
        h = super().health()
        h["stats"] = dict(self.stats)
        return h
