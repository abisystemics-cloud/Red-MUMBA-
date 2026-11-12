"""Canal de supervision (superviseur humain ou Claude ↔ essaim).

DESCENDANT (commandes) : le superviseur écrit `control/commands.json` dans la
branche GitHub `control` du dépôt. Chaque modification est un commit : l'historique
git sert de journal d'audit (qui a ordonné quoi, quand, pourquoi). Le bot lit ce
fichier toutes les `poll_seconds` avec un jeton GitHub en LECTURE SEULE.

MONTANT (comptes rendus) : via la télémétrie PostHog —
- `command_ack`     : commande reçue (dispatched / rejected / expired) ;
- `command_applied` : commande appliquée par l'agent concerné ;
- `status_snapshot` : état complet de l'essaim toutes les `status_interval_s`
  et en réponse à `ping`.

Les commandes sont une LISTE BLANCHE bornée. Aucune ne peut augmenter le risque
au-delà de config.yaml, passer en réel, ni toucher aux fonds :

| commande         | effet                                             | rôle     |
|------------------|---------------------------------------------------|----------|
| ping             | renvoie un status_snapshot immédiat               | tous     |
| pause            | HALT : plus aucune nouvelle entrée                | live     |
| resume           | lève la pause du superviseur                      | live     |
| flatten          | ferme toutes les positions                        | live     |
| set_risk_scale   | taille × scale, scale ∈ [0, 1] (réduction seule)  | live     |
| disable_coin     | plus d'entrées sur ce marché                      | live     |
| enable_coin      | réautorise ce marché                              | live     |
| go_live_report   | produit le rapport go/no-go maintenant            | research |
| research_run     | lance un cycle R&D forcé maintenant               | research |
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from agents.base import BaseAgent
from core.events import ControlCommand, Topic, now_ms

LIVE_CMDS = {"pause", "resume", "flatten", "set_risk_scale", "disable_coin", "enable_coin"}
RESEARCH_CMDS = {"go_live_report", "research_run"}
ALL_CMDS = LIVE_CMDS | RESEARCH_CMDS | {"ping"}


def validate_command(c: dict, coins: list[str]) -> Optional[str]:
    """Retourne un motif de rejet, ou None si la commande est valide."""
    if not isinstance(c, dict) or not c.get("id") or c.get("cmd") not in ALL_CMDS:
        return f"unknown or malformed command: {c.get('cmd') if isinstance(c, dict) else c!r}"
    args = c.get("args") or {}
    if c["cmd"] == "set_risk_scale":
        try:
            scale = float(args.get("scale"))
        except (TypeError, ValueError):
            return "set_risk_scale needs args.scale"
        if not 0 <= scale <= 1:
            return "risk scale must be within [0, 1] (supervisor can only reduce risk)"
    if c["cmd"] in ("disable_coin", "enable_coin") and args.get("coin") not in coins:
        return f"unknown coin {args.get('coin')!r}"
    return None


def _parse_ts(s: str) -> float:
    return datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()


class ControlAgent(BaseAgent):
    name = "control"

    def __init__(self, bus, store, role: str, status_fn: Callable[[], dict], http_session=None,
                 fetch_fn: Optional[Callable] = None, state_dir: str = "data"):
        super().__init__(bus, store)
        self.role = role
        self.status_fn = status_fn
        self._http = http_session
        self._fetch = fetch_fn or self._fetch_github
        self.repo = os.getenv("CONTROL_GITHUB_REPO")
        self.token = os.getenv("CONTROL_GITHUB_TOKEN")
        self.state_path = Path(state_dir) / f"control_state_{role}.json"
        self.seen: set[str] = set()
        try:
            self.seen = set(json.loads(self.state_path.read_text())["seen"])
        except (OSError, ValueError, KeyError):
            pass
        self.handled = 0
        self.last_poll_error: Optional[str] = None
        self.stale_after_s = max(90.0, self.cfg.control.poll_seconds * 4)

    # ---------------------------------------------------------- source
    async def _fetch_github(self) -> Optional[dict]:
        if not (self.repo and self._http):
            return None
        cc = self.cfg.control
        url = f"https://api.github.com/repos/{self.repo}/contents/{cc.path}?ref={cc.branch}"
        headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        async with self._http.get(url, headers=headers, timeout=15) as r:
            if r.status == 404:
                return {"commands": []}
            r.raise_for_status()
            body = await r.json()
        return json.loads(base64.b64decode(body["content"]).decode())

    def _save(self) -> None:
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.state_path.with_suffix(".tmp")
            tmp.write_text(json.dumps({"seen": sorted(self.seen)[-2000:]}))
            os.replace(tmp, self.state_path)
        except OSError:
            pass

    # -------------------------------------------------------- handling
    def _ack(self, c: dict, status: str, detail: str = "") -> None:
        self.bus.publish(Topic.TELEMETRY, {"event": "command_ack", "command_id": c.get("id"),
                                           "cmd": c.get("cmd"), "status": status, "detail": detail,
                                           "role": self.role, "issued_by": c.get("issued_by")})

    def snapshot(self, trigger: str) -> None:
        self.bus.publish(Topic.TELEMETRY, {"event": "status_snapshot", "role": self.role,
                                           "trigger": trigger, "status": self.status_fn()})

    async def process(self, doc: Optional[dict]) -> int:
        n = 0
        coins = [m.coin for m in self.cfg.markets]
        mine = LIVE_CMDS if self.role == "live" else RESEARCH_CMDS if self.role == "research" else LIVE_CMDS | RESEARCH_CMDS
        for c in (doc or {}).get("commands", []):
            cid = c.get("id") if isinstance(c, dict) else None
            if not cid or cid in self.seen:
                continue
            cmd = c.get("cmd")
            if cmd != "ping" and cmd in ALL_CMDS and cmd not in mine:
                continue  # commande destinée à l'autre conteneur : on la laisse
            self.seen.add(cid)
            n += 1
            why = validate_command(c, coins)
            if why:
                self._ack(c, "rejected", why)
                continue
            try:
                age = time.time() - _parse_ts(c.get("issued_at"))
            except (TypeError, ValueError):
                self._ack(c, "rejected", "missing or invalid issued_at")
                continue
            if age > self.cfg.control.max_command_age_s:
                self._ack(c, "expired", f"issued {int(age)}s ago")
                continue
            self._ack(c, "dispatched", c.get("reason", ""))
            self.log.warning("SUPERVISOR COMMAND %s %s (%s) by %s", cmd, c.get("args"), c.get("reason"),
                             c.get("issued_by"))
            if cmd == "ping":
                self.snapshot(f"ping:{cid}")
            else:
                self.bus.publish(Topic.CONTROL, ControlCommand(cid, cmd, c.get("args") or {},
                                                               c.get("reason", ""), c.get("issued_by", "")))
            self.handled += 1
        if n:
            self._save()
        return n

    async def run(self, stop: asyncio.Event) -> None:
        cc = self.cfg.control
        last_status = 0.0
        while not stop.is_set():
            if cc.enabled:
                try:
                    await self.process(await self._fetch())
                    self.last_poll_error = None
                except Exception as exc:  # noqa: BLE001 — le canal ne doit jamais casser le trading
                    self.errors += 1
                    self.last_poll_error = str(exc)[:200]
            if time.monotonic() - last_status >= cc.status_interval_s:
                self.snapshot("periodic")
                last_status = time.monotonic()
            self.beat()
            try:
                await asyncio.wait_for(stop.wait(), timeout=cc.poll_seconds)
            except asyncio.TimeoutError:
                pass

    def health(self) -> dict[str, Any]:
        h = super().health()
        h.update(handled=self.handled, channel=bool(self.repo), last_poll_error=self.last_poll_error)
        return h


def compact_status(agents: list[BaseAgent]) -> dict:
    """Résumé lisible de l'état de l'essaim pour le superviseur."""
    out: dict[str, Any] = {"ts": now_ms()}
    for a in agents:
        h = a.health()
        keep = {k: v for k, v in h.items() if k in (
            "stale", "errors", "level", "reasons", "equity", "realized_pnl", "open", "breaker",
            "dry_run", "risk_scale", "paused", "disabled_coins", "stats", "latency_us", "feeds",
            "runs", "last", "win_rate_est")}
        out[a.name] = keep
    return out
