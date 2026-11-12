"""Serveur web : authentification, instantané, flux SSE, commandes bornées."""
import asyncio
import json
import socket
from pathlib import Path

from core.bus import EventBus
from core.config import ConfigStore
from core.events import Topic
from core.web import WebServer

ROOT = Path(__file__).resolve().parents[1]


def _port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


async def _req(port, method, path, body=None, cookie=None):
    r, w = await asyncio.open_connection("127.0.0.1", port)
    data = json.dumps(body).encode() if body is not None else b""
    head = f"{method} {path} HTTP/1.1\r\nHost: x\r\nContent-Length: {len(data)}\r\n"
    if cookie:
        head += f"Cookie: {cookie}\r\n"
    w.write(head.encode() + b"\r\n" + data)
    await w.drain()
    raw = await asyncio.wait_for(r.read(), 5)
    w.close()
    head, _, payload = raw.partition(b"\r\n\r\n")
    status = int(head.split()[1])
    headers = dict(line.split(": ", 1) for line in head.decode().split("\r\n")[1:] if ": " in line)
    return status, headers, payload


def test_web_auth_snapshot_and_bounded_controls():
    store = ConfigStore(ROOT / "config.yaml")
    bus = EventBus()
    ctl = bus.subscribe(Topic.CONTROL, "t")
    tele = bus.subscribe(Topic.TELEMETRY, "t")
    web = WebServer(bus=bus, store=store, health_fn=lambda: {"ok": True}, status_fn=lambda: {"agents": {}},
                    snapshot_fn=lambda: {"hello": "world"}, password="s3cret", push_interval_s=0.05)
    port = _port()

    async def scenario():
        stop = asyncio.Event()
        task = asyncio.create_task(web.serve(port, stop))
        await asyncio.sleep(0.2)
        out = {}
        out["health"] = (await _req(port, "GET", "/health"))[0]
        out["unauth_snapshot"] = (await _req(port, "GET", "/api/snapshot"))[0]
        out["unauth_status"] = (await _req(port, "GET", "/status"))[0]
        out["unauth_control"] = (await _req(port, "POST", "/api/control", {"cmd": "flatten"}))[0]
        out["bad_login"] = (await _req(port, "POST", "/api/login", {"password": "x"}))[0]
        st, hd, _ = await _req(port, "POST", "/api/login", {"password": "s3cret"})
        cookie = hd["Set-Cookie"].split(";")[0]
        out["login"] = st
        out["httponly"] = "HttpOnly" in hd["Set-Cookie"] and "SameSite=Strict" in hd["Set-Cookie"]
        st, _, body = await _req(port, "GET", "/api/snapshot", cookie=cookie)
        out["snapshot"] = (st, json.loads(body))
        out["index"] = (await _req(port, "GET", "/", cookie=cookie))[0]
        out["ok_cmd"] = (await _req(port, "POST", "/api/control", {"cmd": "set_risk_scale", "args": {"scale": 0.3}},
                                    cookie=cookie))[0]
        out["raise_risk"] = (await _req(port, "POST", "/api/control", {"cmd": "set_risk_scale", "args": {"scale": 5}},
                                        cookie=cookie))[0]
        out["unknown_cmd"] = (await _req(port, "POST", "/api/control", {"cmd": "go_mainnet"}, cookie=cookie))[0]
        # flux SSE : au moins deux messages
        r, w = await asyncio.open_connection("127.0.0.1", port)
        w.write(f"GET /api/stream HTTP/1.1\r\nHost: x\r\nCookie: {cookie}\r\n\r\n".encode())
        await w.drain()
        buf = b""
        while buf.count(b"data: ") < 2:
            buf += await asyncio.wait_for(r.read(1024), 3)
        w.close()
        out["sse"] = buf
        stop.set()
        await asyncio.wait_for(task, 3)
        return out

    out = asyncio.run(scenario())
    assert out["health"] == 200
    assert out["unauth_snapshot"] == out["unauth_status"] == out["unauth_control"] == 401
    assert out["bad_login"] == 401 and out["login"] == 200 and out["httponly"]
    assert out["snapshot"] == (200, {"hello": "world"})
    assert out["index"] == 200
    assert out["ok_cmd"] == 200 and out["raise_risk"] == 400 and out["unknown_cmd"] == 400
    assert b"text/event-stream" in out["sse"] and b'{"hello":"world"}' in out["sse"]
    cmds = []
    while not ctl.queue.empty():
        cmds.append(ctl.queue.get_nowait())
    assert [(c.cmd, c.args) for c in cmds] == [("set_risk_scale", {"scale": 0.3})]
    acks = [tele.queue.get_nowait() for _ in range(tele.queue.qsize())]
    assert [a["status"] for a in acks] == ["dispatched", "rejected", "rejected"]


def test_ui_disabled_without_password(monkeypatch):
    monkeypatch.delenv("UI_PASSWORD", raising=False)
    store = ConfigStore(ROOT / "config.yaml")
    web = WebServer(bus=EventBus(), store=store, health_fn=lambda: {"ok": True}, status_fn=dict,
                    snapshot_fn=dict)
    port = _port()

    async def scenario():
        stop = asyncio.Event()
        task = asyncio.create_task(web.serve(port, stop))
        await asyncio.sleep(0.2)
        res = [(await _req(port, "GET", p))[0] for p in ("/health", "/", "/api/snapshot")]
        res.append((await _req(port, "POST", "/api/login", {"password": ""}))[0])
        stop.set()
        await asyncio.wait_for(task, 3)
        return res

    assert asyncio.run(scenario()) == [200, 503, 401, 503]
