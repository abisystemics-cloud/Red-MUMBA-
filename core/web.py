"""Serveur HTTP minimal (asyncio pur, sans dépendance) : sondes + interface temps réel.

Routes :
  GET  /health            sonde (200 / 503) — toujours publique
  GET  /status            état détaillé des agents — authentifié
  GET  /                  interface web (ui/index.html)
  POST /api/login         {"password": "..."} → cookie de session
  POST /api/logout
  GET  /api/snapshot      état temps réel (JSON) — authentifié
  GET  /api/stream        même état poussé chaque seconde (Server-Sent Events) — authentifié
  POST /api/control       commande de la liste blanche (pause, flatten…) — authentifié

Sécurité : l'interface n'est active que si UI_PASSWORD est défini. Le cookie de
session est un HMAC du mot de passe (HttpOnly, SameSite=Strict) ; changer le
mot de passe invalide toutes les sessions. Les commandes passent par la même
liste blanche que le canal de supervision : elles ne peuvent que réduire le risque.
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Callable, Optional

from agents.control_agent import validate_command
from core.events import ControlCommand, Topic

log = logging.getLogger("core.web")
UI_DIR = Path(__file__).resolve().parents[1] / "ui"
COOKIE = "hlswarm_ui"


def session_token(password: str) -> str:
    return hmac.new(password.encode(), b"hl-swarm-ui-v1", hashlib.sha256).hexdigest()


class WebServer:
    def __init__(self, *, bus, store, health_fn: Callable[[], dict], status_fn: Callable[[], dict],
                 snapshot_fn: Optional[Callable[[], dict]], password: Optional[str] = None,
                 push_interval_s: float = 1.0):
        self.bus = bus
        self.store = store
        self.health_fn = health_fn
        self.status_fn = status_fn
        self.snapshot_fn = snapshot_fn
        self.password = password if password is not None else os.getenv("UI_PASSWORD")
        self.token = session_token(self.password) if self.password else None
        self.push_interval_s = push_interval_s
        self._failed_logins = 0
        self.streams = 0

    # ------------------------------------------------------------ helpers
    @staticmethod
    def _resp(code: int, body: bytes | str, ctype: str = "application/json",
              extra: Optional[dict] = None) -> bytes:
        if isinstance(body, str):
            body = body.encode()
        reason = {200: "OK", 204: "No Content", 400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
                  404: "Not Found", 405: "Method Not Allowed", 429: "Too Many Requests",
                  503: "Service Unavailable"}.get(code, "OK")
        headers = {"Content-Type": ctype, "Content-Length": str(len(body)), "Connection": "close",
                   "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                   "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer"}
        headers.update(extra or {})
        head = f"HTTP/1.1 {code} {reason}\r\n" + "".join(f"{k}: {v}\r\n" for k, v in headers.items())
        return head.encode() + b"\r\n" + body

    def _json(self, code: int, obj, extra: Optional[dict] = None) -> bytes:
        return self._resp(code, json.dumps(obj, default=str, separators=(",", ":")), extra=extra)

    def authed(self, headers: dict) -> bool:
        if not self.token:
            return False
        for part in headers.get("cookie", "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == COOKIE and hmac.compare_digest(v, self.token):
                return True
        return False

    @staticmethod
    async def _read_request(reader: asyncio.StreamReader):
        line = (await asyncio.wait_for(reader.readline(), 10)).decode("latin-1").strip()
        if not line:
            return None
        method, _, rest = line.partition(" ")
        path = rest.split(" ")[0]
        headers: dict[str, str] = {}
        while True:
            h = (await asyncio.wait_for(reader.readline(), 10)).decode("latin-1")
            if h in ("\r\n", "\n", ""):
                break
            k, _, v = h.partition(":")
            headers[k.strip().lower()] = v.strip()
        body = b""
        n = int(headers.get("content-length", "0") or 0)
        if 0 < n <= 64_000:
            body = await asyncio.wait_for(reader.readexactly(n), 10)
        return method.upper(), path.split("?")[0], headers, body

    # ------------------------------------------------------------- routes
    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            req = await self._read_request(reader)
            if req is None:
                return
            method, path, headers, body = req
            if path == "/api/stream" and method == "GET":
                if not self.authed(headers):
                    writer.write(self._json(401, {"error": "login required"}))
                else:
                    await self._stream(writer)
                return
            writer.write(await self.route(method, path, headers, body))
            await writer.drain()
        except (asyncio.TimeoutError, ConnectionError, asyncio.IncompleteReadError):
            pass
        except Exception:  # noqa: BLE001
            log.exception("web handler error")
        finally:
            try:
                writer.close()
            except Exception:  # noqa: BLE001
                pass

    async def route(self, method: str, path: str, headers: dict, body: bytes) -> bytes:
        if path.startswith("/health"):
            h = self.health_fn()
            return self._json(200 if h.get("ok") else 503, h)
        if path in ("/", "/index.html"):
            if not self.token:
                return self._resp(503, "<h1>Interface désactivée</h1><p>Définir la variable UI_PASSWORD.</p>",
                                  "text/html; charset=utf-8")
            return self._resp(200, (UI_DIR / "index.html").read_bytes(), "text/html; charset=utf-8",
                              {"Content-Security-Policy": "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                                                          "script-src 'self' 'unsafe-inline'; connect-src 'self'"})
        if path == "/api/login" and method == "POST":
            return await self._login(body)
        if path == "/api/logout" and method == "POST":
            return self._json(200, {"ok": True},
                              {"Set-Cookie": f"{COOKIE}=; Max-Age=0; Path=/; HttpOnly; SameSite=Strict"})
        if not self.authed(headers):
            return self._json(401, {"error": "login required"})
        if path == "/status":
            return self._json(200, self.status_fn())
        if path == "/api/snapshot":
            return self._json(200, self.snapshot_fn() if self.snapshot_fn else {})
        if path == "/api/control" and method == "POST":
            return self._control(body)
        return self._json(404, {"error": "not found"})

    async def _login(self, body: bytes) -> bytes:
        if not self.token:
            return self._json(503, {"error": "UI_PASSWORD not set"})
        try:
            pw = str(json.loads(body or b"{}").get("password", ""))
        except ValueError:
            pw = ""
        if hmac.compare_digest(session_token(pw), self.token):
            self._failed_logins = 0
            return self._json(200, {"ok": True}, {
                "Set-Cookie": f"{COOKIE}={self.token}; Max-Age=2592000; Path=/; HttpOnly; SameSite=Strict"})
        self._failed_logins += 1
        await asyncio.sleep(min(5.0, 0.5 * self._failed_logins))  # freine les essais en rafale
        log.warning("UI login failed (%d)", self._failed_logins)
        return self._json(401, {"error": "mot de passe incorrect"})

    def _control(self, body: bytes) -> bytes:
        try:
            req = json.loads(body or b"{}")
        except ValueError:
            return self._json(400, {"error": "invalid json"})
        cmd = {"id": f"ui-{time.strftime('%Y%m%dT%H%M%S', time.gmtime())}-{uuid.uuid4().hex[:6]}",
               "cmd": req.get("cmd"), "args": req.get("args") or {}, "reason": str(req.get("reason") or "interface"),
               "issued_by": "ui"}
        why = validate_command(cmd, [m.coin for m in self.store.current.markets])
        self.bus.publish(Topic.TELEMETRY, {"event": "command_ack", "command_id": cmd["id"], "cmd": cmd["cmd"],
                                           "status": "rejected" if why else "dispatched", "detail": why or cmd["reason"],
                                           "role": "live", "issued_by": "ui"})
        if why:
            return self._json(400, {"error": why})
        if cmd["cmd"] != "ping":
            self.bus.publish(Topic.CONTROL, ControlCommand(cmd["id"], cmd["cmd"], cmd["args"], cmd["reason"], "ui"))
        log.warning("UI COMMAND %s %s (%s)", cmd["cmd"], cmd["args"], cmd["reason"])
        return self._json(200, {"ok": True, "id": cmd["id"]})

    async def _stream(self, writer: asyncio.StreamWriter) -> None:
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nCache-Control: no-store\r\n"
                     b"Connection: keep-alive\r\nX-Accel-Buffering: no\r\n\r\n")
        await writer.drain()
        self.streams += 1
        try:
            while True:
                snap = self.snapshot_fn() if self.snapshot_fn else {}
                writer.write(b"data: " + json.dumps(snap, default=str, separators=(",", ":")).encode() + b"\n\n")
                await writer.drain()
                await asyncio.sleep(self.push_interval_s)
        finally:
            self.streams -= 1

    async def serve(self, port: int, stop: asyncio.Event) -> None:
        server = await asyncio.start_server(self.handle, "0.0.0.0", port)
        log.info("web server on :%d (/health%s)", port, ", UI enabled" if self.token else ", UI disabled")
        async with server:
            await stop.wait()
