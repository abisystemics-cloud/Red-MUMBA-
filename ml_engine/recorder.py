"""Enregistrement du flux de marché (jsonl.gz horaire) et relecture pour le backtest."""
from __future__ import annotations

import calendar
import gzip
import heapq
import json
import re
import time
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np

from core.events import AssetCtx, BookSnapshot, ExternalQuote, LiquidationMap, Trade, WhaleBias


class MarketRecorder:
    def __init__(self, directory: str | Path, flush_every: int = 500):
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.flush_every = flush_every
        self._hour = None
        self._fh = None
        self._n = 0
        self._closed = False

    def _file(self, ts_ms: int):
        hour = time.strftime("%Y%m%dT%H", time.gmtime(ts_ms / 1000))
        if hour != self._hour:
            if self._fh:
                self._fh.close()
            self._hour = hour
            self._fh = gzip.open(self.dir / f"md_{hour}.jsonl.gz", "at", encoding="utf-8")
        return self._fh

    def write(self, rec: dict) -> None:
        if self._closed:
            return
        fh = self._file(rec["ts"])
        fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
        self._n += 1
        if self._n % self.flush_every == 0:
            fh.flush()

    def book(self, b: BookSnapshot, levels: int = 20) -> None:
        self.write({"t": "book", "coin": b.coin, "ts": b.exch_ts,
                    "b": b.bids[:levels].round(8).tolist(), "a": b.asks[:levels].round(8).tolist()})

    def trade(self, t: Trade) -> None:
        self.write({"t": "trade", "coin": t.coin, "ts": t.ts, "px": t.px, "sz": t.sz, "buy": t.is_buy})

    def ext(self, q: ExternalQuote) -> None:
        self.write({"t": "ext", "coin": q.coin, "ts": q.ts, "v": q.venue, "bid": q.bid, "ask": q.ask})

    def ctx(self, c: AssetCtx) -> None:
        self.write({"t": "ctx", "coin": c.coin, "ts": c.ts, "oi": c.open_interest,
                    "f": c.funding, "m": c.mark_px, "o": c.oracle_px})

    def whale(self, w: WhaleBias) -> None:
        self.write({"t": "whale", "coin": w.coin, "ts": w.ts, "bias": w.bias, "n": w.n_wallets, "g": w.gross_usd})

    def liq(self, m: LiquidationMap) -> None:
        self.write({"t": "liq", "coin": m.coin, "ts": m.ts, "c": m.clusters, "src": m.source})

    def close(self) -> None:
        self._closed = True
        if self._fh:
            self._fh.close()
            self._fh = None


def _iter_file(path: Path, since_ms: int) -> Iterator[dict]:
    try:
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue  # dernière ligne tronquée d'un fichier en cours d'écriture
                if rec["ts"] >= since_ms:
                    yield rec
    except (EOFError, OSError):
        return


def _file_start_ms(p: Path) -> int:
    m = re.match(r"md_(\d{8}T\d{2})", p.name)
    if not m:
        return 0
    return calendar.timegm(time.strptime(m.group(1), "%Y%m%dT%H")) * 1000


def iter_events(directory: str | Path, since_ms: int = 0, until_ms: int | None = None,
                coins: Iterable[str] | None = None) -> Iterator[dict]:
    """Flux chronologique de tous les fichiers md_*.jsonl.gz (live et historiques,
    un fichier par heure), en mémoire constante : adapté à des mois de données.
    Les fichiers ne sont ouverts qu'au moment où le flux atteint leur heure de
    début (quelques fichiers ouverts à la fois, jamais des milliers)."""
    files = sorted(Path(directory).glob("md_*.jsonl.gz"), key=lambda p: (_file_start_ms(p), p.name))
    # un nom sans heure (start = 0) est toujours lu : il est ouvert dès le début
    files = [p for p in files if _file_start_ms(p) == 0 or (_file_start_ms(p) + 3_600_000 >= since_ms
             and (until_ms is None or _file_start_ms(p) <= until_ms))]
    keep = set(coins) if coins else None
    heap: list = []
    nxt = 0
    seq = 0

    def open_next() -> None:
        nonlocal nxt, seq
        it = _iter_file(files[nxt], since_ms)
        nxt += 1
        for rec in it:
            heapq.heappush(heap, (rec["ts"], seq, rec, it))
            seq += 1
            break

    while nxt < len(files) or heap:
        while nxt < len(files) and (not heap or _file_start_ms(files[nxt]) <= heap[0][0]):
            open_next()
        if not heap:
            continue
        ts, _, rec, it = heapq.heappop(heap)
        for nrec in it:
            heapq.heappush(heap, (nrec["ts"], seq, nrec, it))
            seq += 1
            break
        if until_ms is not None and ts > until_ms:
            continue
        if keep is None or rec["coin"] in keep:
            yield rec


def load_events(directory: str | Path, since_ms: int = 0, coin: str | None = None) -> list[dict]:
    return list(iter_events(directory, since_ms, coins=[coin] if coin else None))


def to_event(rec: dict):
    t = rec["t"]
    if t == "book":
        return BookSnapshot(rec["coin"], rec["ts"], rec["ts"],
                            np.asarray(rec["b"], dtype=float).reshape(-1, 2),
                            np.asarray(rec["a"], dtype=float).reshape(-1, 2))
    if t == "trade":
        return Trade(rec["coin"], rec["ts"], rec["px"], rec["sz"], rec["buy"])
    if t == "ext":
        return ExternalQuote(rec["v"], rec["coin"], rec["ts"], rec["bid"], rec["ask"])
    if t == "ctx":
        return AssetCtx(rec["coin"], rec["ts"], rec["oi"], rec["f"], rec["m"], rec["o"])
    if t == "whale":
        return WhaleBias(rec["coin"], rec["ts"], rec["bias"], rec["n"], rec["g"])
    if t == "liq":
        return LiquidationMap(rec["coin"], rec["ts"], [tuple(c) for c in rec["c"]], rec["src"])
    return None
