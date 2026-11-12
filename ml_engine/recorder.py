"""Enregistrement du flux de marché (jsonl.gz horaire) et relecture pour le backtest."""
from __future__ import annotations

import gzip
import heapq
import json
import time
from pathlib import Path
from typing import Iterator

import numpy as np

from core.events import AssetCtx, BookSnapshot, ExternalQuote, Trade


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


def load_events(directory: str | Path, since_ms: int = 0, coin: str | None = None) -> list[dict]:
    files = sorted(Path(directory).glob("md_*.jsonl.gz"))
    streams = [_iter_file(p, since_ms) for p in files]
    out = [r for r in heapq.merge(*streams, key=lambda r: r["ts"]) if coin is None or r["coin"] == coin]
    return out


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
    return None
