"""Alertes humaines (Telegram), avec anti-spam par clé.

Configurer TELEGRAM_BOT_TOKEN et TELEGRAM_CHAT_ID. Sans eux, les alertes sont
seulement journalisées (niveau WARNING) : rien ne casse.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Optional

log = logging.getLogger("core.alerts")


def alert_for(ev: dict) -> Optional[tuple[str, str]]:
    """Traduit un événement de télémétrie en (clé anti-spam, message), ou None."""
    name = ev.get("event")
    net = ev.get("network", "")
    if name == "feed_down":
        return f"feed:{ev.get('feed')}", f"[{net}] Flux {ev.get('feed')} coupé ({ev.get('last_error') or 'silence'})"
    if name == "risk_level" and ev.get("level") in ("halt", "caution"):
        return f"risk:{ev.get('level')}", f"[{net}] Niveau de risque {ev['level'].upper()} : {'; '.join(ev.get('reasons') or [])[:300]}"
    if name == "breaker":
        return "breaker", f"[{net}] Disjoncteur déclenché : {ev.get('reason')} — positions fermées"
    if name == "order" and ev.get("status") == "rejected" and ev.get("kind") in ("stop", "tp"):
        return f"protect:{ev.get('coin')}", f"[{net}] CRITIQUE : ordre {ev.get('kind')} refusé sur {ev.get('coin')} ({ev.get('error')})"
    if name == "research_run" and str(ev.get("done") or "").startswith(("proposal", "deployed")):
        return "research", f"[{net}] Agent R&D : {ev.get('done')}"
    if name == "command_applied":
        return (f"cmd:{ev.get('command_id')}",
                f"[{net}] Superviseur : commande « {ev.get('cmd')} » appliquée par {ev.get('agent')}"
                + (f" → {ev.get('result')}" if ev.get("result") else ""))
    if name == "command_ack" and ev.get("status") == "rejected":
        return f"cmdrej:{ev.get('command_id')}", f"[{net}] Commande refusée ({ev.get('cmd')}) : {ev.get('detail')}"
    if name == "go_live_report":
        return "go_live", f"[{net}] {ev.get('text')}"
    return None


class Alerter:
    def __init__(self, cfg, http_session=None):
        self.cfg = cfg
        self._http = http_session
        self._last: dict[str, float] = {}
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat = os.getenv("TELEGRAM_CHAT_ID")
        self.sent = 0

    def should_send(self, key: str, now: Optional[float] = None) -> bool:
        now = now if now is not None else time.monotonic()
        last = self._last.get(key)
        if last is not None and now - last < self.cfg.min_interval_s:
            return False
        self._last[key] = now
        return True

    async def send(self, key: str, text: str) -> bool:
        if not self.cfg.enabled or not self.should_send(key):
            return False
        log.warning("ALERT %s", text)
        if not (self.token and self.chat and self._http):
            return False
        try:
            async with self._http.post(f"https://api.telegram.org/bot{self.token}/sendMessage",
                                       json={"chat_id": self.chat, "text": text[:4000]}, timeout=10) as r:
                ok = r.status < 400
        except Exception as exc:  # noqa: BLE001 — une alerte ratée ne casse rien
            log.warning("telegram alert failed: %s", exc)
            return False
        self.sent += int(ok)
        return ok
