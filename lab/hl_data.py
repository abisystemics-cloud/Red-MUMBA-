"""Données récentes Hyperliquid (API publique, sans clé) : clôtures journalières et
funding horaire agrégé par jour, pour les marchés du catalogue. C'est le lieu
d'exécution visé, donc les signaux du paper trading sont calculés dessus."""
from __future__ import annotations

import json
import time
import urllib.request

import numpy as np

URL = "https://api.hyperliquid.xyz/info"
DAY_MS = 86_400_000


def hl_post(body: dict, retries: int = 4):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except Exception as e:  # noqa: BLE001 — réseau : on réessaie avec recul
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"Hyperliquid API: {last}")


def fetch_panel(coins: list[str], lookback_days: int = 75, now_ms: int | None = None, post=hl_post,
                pause_s: float = 0.6) -> dict:
    now_ms = now_ms or int(time.time() * 1000)
    last_closed = now_ms // DAY_MS * DAY_MS - DAY_MS          # ouverture du dernier jour UTC terminé
    start = last_closed - (lookback_days - 1) * DAY_MS
    days = np.arange(start, last_closed + 1, DAY_MS, dtype=np.float64)
    T = len(days)
    kept, cols_c, cols_f = [], [], []
    for coin in coins:
        try:
            candles = post({"type": "candleSnapshot", "req": {"coin": coin, "interval": "1d",
                                                             "startTime": int(start), "endTime": int(last_closed + DAY_MS - 1)}})
        except RuntimeError:
            candles = None
        time.sleep(pause_s)
        if not candles:
            continue
        c = np.full(T, np.nan)
        for k in candles:
            i = int((int(k["t"]) - start) // DAY_MS)
            if 0 <= i < T and int(k["t"]) % DAY_MS == 0:
                c[i] = float(k["c"])
        if np.isfinite(c).sum() < 30 or not np.isfinite(c[-1]):
            continue
        f = np.zeros(T)
        cursor = int(start)
        for _ in range(12):
            try:
                rows = post({"type": "fundingHistory", "coin": coin, "startTime": cursor, "endTime": int(last_closed + DAY_MS - 1)})
            except RuntimeError:
                rows = None
            time.sleep(pause_s)
            if not rows:
                break
            for r in rows:
                i = int((int(r["time"]) - start) // DAY_MS)
                if 0 <= i < T:
                    f[i] += float(r["fundingRate"])
            if len(rows) < 500:
                break
            cursor = int(rows[-1]["time"]) + 1
        kept.append(coin)
        cols_c.append(c)
        cols_f.append(f)
    if not kept:
        raise RuntimeError("aucun marché récupéré depuis Hyperliquid")
    C, F = np.column_stack(cols_c), np.column_stack(cols_f)
    R = np.full(C.shape, np.nan)
    R[1:] = C[1:] / C[:-1] - 1
    return {"coins": kept, "days": days, "C": C, "F": F, "R": R, "source": "hyperliquid"}
