"""Importe un historique de marché au format lu par le backtester.

    python scripts/import_history.py --from 2026-09-01 --to 2026-10-31 --coins BTC,ETH

Sources (chacune désactivable) :
- Hyperliquid, archive S3 officielle `hyperliquid-archive` (le DEMANDEUR paie le
  transfert, ~0,09 $/Go) : snapshots L2 du carnet (market_data/<date>/<h>/l2Book/<coin>.lz4)
  et contextes d'actifs journaliers (asset_ctxs/<date>.csv.lz4 : funding, OI, prix).
  Identifiants : AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY.
- Hyperliquid, fills (`hl-mainnet-node-data/node_fills_by_block`, option --with-trades) :
  toutes les exécutions du marché, volumineux ; sert au CVD et au POC.
- Binance USDⓈ-M, data.binance.vision (gratuit) : meilleur bid/ask (bookTicker),
  repli sur les aggTrades : prix de référence pour le premium cross-exchange.
- Coinversa Pulse (COINVERSA_API_KEY) : biais long/short des catégories de traders.

Sortie : un fichier par heure `md_<YYYYMMDD>T<HH>_hist.jsonl.gz` dans --out, trié
par horodatage, + un rapport de couverture (heures manquantes par source) dans
data/reports/. L'archive S3 est mise à jour environ une fois par mois, sans
garantie de complétude : les trous sont signalés, jamais comblés.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Iterator, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agents.coinversa import snapshots_to_bias  # noqa: E402
from core.config import load_config  # noqa: E402

ARCHIVE = "hyperliquid-archive"
NODE = "hl-mainnet-node-data"


# ----------------------------------------------------------------- parsers
def parse_l2_line(line: str, levels: int) -> Optional[dict]:
    """Une ligne de l'archive l2Book → enregistrement 'book'. Tolérant aux variantes
    d'enveloppe ({raw:{data}}, {data}, ou l'objet directement)."""
    try:
        obj = json.loads(line)
    except ValueError:
        return None
    data = obj.get("raw", obj)
    data = data.get("data", data) if isinstance(data, dict) else None
    if not isinstance(data, dict) or "levels" not in data:
        return None
    lv = data["levels"]
    if len(lv) != 2 or not lv[0] or not lv[1]:
        return None
    ts = data.get("time")
    if ts is None:
        return None
    b = [[float(x["px"]), float(x["sz"])] for x in lv[0][:levels]]
    a = [[float(x["px"]), float(x["sz"])] for x in lv[1][:levels]]
    return {"t": "book", "coin": data["coin"], "ts": int(ts), "b": b, "a": a}


def _num(row: dict, *names: str) -> Optional[float]:
    for n in names:
        v = row.get(n)
        if v not in (None, ""):
            try:
                return float(v)
            except ValueError:
                pass
    return None


def _ts_any(v) -> Optional[int]:
    if v in (None, ""):
        return None
    try:
        x = float(v)
        return int(x if x > 1e12 else x * 1000)
    except ValueError:
        return int(datetime.fromisoformat(str(v).replace("Z", "+00:00")).replace(
            tzinfo=timezone.utc).timestamp() * 1000)


def parse_asset_ctxs(text: str, coins: set[str]) -> list[dict]:
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        row = {k.strip().lower(): v for k, v in row.items() if k}
        coin = row.get("coin")
        if coin not in coins:
            continue
        ts = _ts_any(row.get("time") or row.get("timestamp"))
        oi = _num(row, "open_interest", "openinterest")
        f = _num(row, "funding")
        if ts is None or oi is None or f is None:
            continue
        mark = _num(row, "mark_px", "markpx") or 0.0
        oracle = _num(row, "oracle_px", "oraclepx") or mark
        out.append({"t": "ctx", "coin": coin, "ts": ts, "oi": oi, "f": f, "m": mark, "o": oracle})
    return out


def parse_fill_block(line: str, coins: set[str]) -> list[dict]:
    """Ligne node_fills_by_block → trades (côté agresseur uniquement : crossed=True)."""
    try:
        obj = json.loads(line)
    except ValueError:
        return []
    events = obj.get("events", obj if isinstance(obj, list) else [])
    out = []
    for ev in events:
        fill = ev[1] if isinstance(ev, list) and len(ev) == 2 else ev
        if not isinstance(fill, dict) or fill.get("coin") not in coins or not fill.get("crossed"):
            continue
        out.append({"t": "trade", "coin": fill["coin"], "ts": int(fill["time"]), "px": float(fill["px"]),
                    "sz": float(fill["sz"]), "buy": fill.get("side") == "B"})
    return out


def parse_binance_book_ticker(text: str, coin: str) -> Iterator[dict]:
    for row in csv.reader(io.StringIO(text)):
        if not row or not row[0][:1].isdigit():
            continue  # en-tête
        # update_id, best_bid_price, best_bid_qty, best_ask_price, best_ask_qty, transaction_time, event_time
        try:
            yield {"t": "ext", "coin": coin, "ts": int(row[5]), "v": "binance",
                   "bid": float(row[1]), "ask": float(row[3])}
        except (IndexError, ValueError):
            continue


def parse_binance_agg_trades(text: str, coin: str) -> Iterator[dict]:
    for row in csv.reader(io.StringIO(text)):
        if not row or not row[0][:1].isdigit():
            continue
        # agg_trade_id, price, quantity, first_trade_id, last_trade_id, transact_time, is_buyer_maker
        try:
            px = float(row[1])
            yield {"t": "ext", "coin": coin, "ts": int(row[5]), "v": "binance",
                   "bid": px * (1 - 0.5e-4), "ask": px * (1 + 0.5e-4)}
        except (IndexError, ValueError):
            continue


def parse_binance_flow(text: str, coin: str, bucket_ms: int = 2000) -> list[dict]:
    """aggTrades → flux agresseur agrégé par tranche de `bucket_ms` (un enregistrement
    acheteur + un vendeur par tranche, au VWAP). Sert de proxy au flux Hyperliquid
    pour le CVD et le profil de volume quand les fills HL ne sont pas importés."""
    acc: dict[tuple[int, bool], list[float]] = {}
    for row in csv.reader(io.StringIO(text)):
        if not row or not row[0][:1].isdigit():
            continue
        try:
            px, q, ts = float(row[1]), float(row[2]), int(row[5])
        except (IndexError, ValueError):
            continue
        buy = row[6].strip().lower() != "true"  # is_buyer_maker=true → vendeur agresseur
        a = acc.setdefault((ts - ts % bucket_ms, buy), [0.0, 0.0])
        a[0] += px * q
        a[1] += q
    return [{"t": "trade", "coin": coin, "ts": b + bucket_ms - 1, "px": v / q, "sz": q, "buy": buy, "src": "binance"}
            for (b, buy), (v, q) in sorted(acc.items()) if q > 0]


def downsample(recs: Iterable[dict], interval_ms: int) -> list[dict]:
    out, last = [], {}
    for r in recs:
        k = (r["coin"], r.get("v"))
        if interval_ms <= 0 or r["ts"] - last.get(k, -10 ** 15) >= interval_ms:
            out.append(r)
            last[k] = r["ts"]
    return out


# ----------------------------------------------------------------- sources
class S3Source:
    def __init__(self):
        import boto3
        import lz4.frame
        self.s3 = boto3.client("s3")
        self.lz4 = lz4.frame
        self.bytes = 0

    def get(self, bucket: str, key: str) -> Optional[bytes]:
        try:
            obj = self.s3.get_object(Bucket=bucket, Key=key, RequestPayer="requester")
        except self.s3.exceptions.NoSuchKey:
            return None
        except Exception as exc:  # noqa: BLE001
            if "NoSuchKey" in str(exc) or "404" in str(exc) or "AccessDenied" in str(exc):
                if "AccessDenied" in str(exc):
                    print(f"  ! access denied on s3://{bucket}/{key}", file=sys.stderr)
                return None
            raise
        raw = obj["Body"].read()
        self.bytes += len(raw)
        return self.lz4.decompress(raw) if key.endswith(".lz4") else raw

    def keys(self, bucket: str, prefix: str) -> list[str]:
        out, token = [], None
        while True:
            kw = {"Bucket": bucket, "Prefix": prefix, "RequestPayer": "requester"}
            if token:
                kw["ContinuationToken"] = token
            r = self.s3.list_objects_v2(**kw)
            out += [o["Key"] for o in r.get("Contents", [])]
            if not r.get("IsTruncated"):
                return out
            token = r["NextContinuationToken"]


def http_get(url: str, headers: Optional[dict] = None, timeout: int = 60) -> Optional[bytes]:
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "hl-swarm-import"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def binance_day(symbol: str, coin: str, day: date, flow: bool = False) -> tuple[list[dict], str, list[dict]]:
    """→ (cotations de référence, source, flux agresseur si `flow` et aggTrades dispo)."""
    d = day.isoformat()
    for kind, parser in (("bookTicker", parse_binance_book_ticker), ("aggTrades", parse_binance_agg_trades)):
        if flow and kind == "bookTicker":
            continue  # le flux exige les aggTrades
        url = f"https://data.binance.vision/data/futures/um/daily/{kind}/{symbol}/{symbol}-{kind}-{d}.zip"
        raw = http_get(url)
        if raw is None:
            continue
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            text = z.read(z.namelist()[0]).decode()
        fl = parse_binance_flow(text, coin) if flow and kind == "aggTrades" else []
        return list(parser(text, coin)), kind, fl
    return [], "missing", []


def coinversa_range(coin: str, start: datetime, end: datetime, cfg) -> list[dict]:
    key = os.getenv("COINVERSA_API_KEY")
    if not key:
        return []
    out, cur = [], start
    while cur < end:
        nxt = min(end, cur + timedelta(days=2))
        q = urllib.parse.urlencode({"coin": coin, "startTime": cur.isoformat().replace("+00:00", "Z"),
                                    "endTime": nxt.isoformat().replace("+00:00", "Z"),
                                    "tierType": "pnl", "limit": 2000})
        raw = http_get(f"{cfg.base_url.rstrip('/')}{cfg.cohort_history_path}?{q}", {"X-API-Key": key})
        if raw:
            for wb in snapshots_to_bias(json.loads(raw), coin, cfg):
                out.append({"t": "whale", "coin": coin, "ts": wb.ts, "bias": wb.bias,
                            "n": wb.n_wallets, "g": wb.gross_usd})
        cur = nxt
        time.sleep(0.2)
    return out


# ------------------------------------------------------------------- main
def write_hours(recs: list[dict], out: Path) -> int:
    by_hour: dict[str, list[dict]] = defaultdict(list)
    for r in recs:
        by_hour[time.strftime("%Y%m%dT%H", time.gmtime(r["ts"] / 1000))].append(r)
    for h, rows in by_hour.items():
        rows.sort(key=lambda r: r["ts"])
        with gzip.open(out / f"md_{h}_hist.jsonl.gz", "wt", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    return len(by_hour)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start", required=True)
    p.add_argument("--to", dest="end", required=True)
    p.add_argument("--coins", default="BTC,ETH")
    p.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config.yaml"))
    p.add_argument("--out", default="data/recordings")
    p.add_argument("--book-interval-ms", type=int, default=2000)
    p.add_argument("--ext-interval-ms", type=int, default=1000)
    p.add_argument("--levels", type=int, default=10)
    p.add_argument("--with-trades", action="store_true", help="fills Hyperliquid (volumineux)")
    p.add_argument("--binance-flow", action="store_true",
                   help="flux agresseur Binance (aggTrades) comme proxy du flux pour CVD/POC")
    p.add_argument("--fills-prefix", default="node_fills_by_block/hourly/")
    p.add_argument("--no-s3", action="store_true")
    p.add_argument("--no-binance", action="store_true")
    p.add_argument("--no-coinversa", action="store_true")
    a = p.parse_args()

    cfg = load_config(a.config)
    coins = [c.strip() for c in a.coins.split(",") if c.strip()]
    bin_sym = {m.coin: (m.binance or f"{m.coin}usdt").upper() for m in cfg.markets}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    d0, d1 = date.fromisoformat(a.start), date.fromisoformat(a.end)
    s3 = None if a.no_s3 else S3Source()
    cov: dict = {"from": a.start, "to": a.end, "coins": coins, "days": {}}

    whales: dict[str, list[dict]] = {}
    if not a.no_coinversa:
        start = datetime(d0.year, d0.month, d0.day, tzinfo=timezone.utc)
        end = datetime(d1.year, d1.month, d1.day, tzinfo=timezone.utc) + timedelta(days=1)
        for c in coins:
            whales[c] = coinversa_range(c, start, end, cfg.data.coinversa)
            print(f"coinversa {c}: {len(whales[c])} positioning snapshots")

    day = d0
    while day <= d1:
        ds = day.strftime("%Y%m%d")
        recs: list[dict] = []
        dcov = {"book_hours": {}, "ctx": 0, "trades": 0, "binance": {}, "whale": 0}
        if s3:
            for c in coins:
                n_hours = 0
                for h in range(24):
                    raw = s3.get(ARCHIVE, f"market_data/{ds}/{h}/l2Book/{c}.lz4")
                    if raw is None:
                        continue
                    n_hours += 1
                    books = (parse_l2_line(ln, a.levels) for ln in raw.decode().splitlines())
                    recs += downsample((b for b in books if b), a.book_interval_ms)
                dcov["book_hours"][c] = n_hours
            raw = s3.get(ARCHIVE, f"asset_ctxs/{ds}.csv.lz4")
            if raw:
                ctx = parse_asset_ctxs(raw.decode(), set(coins))
                dcov["ctx"] = len(ctx)
                recs += ctx
            if a.with_trades:
                for key in s3.keys(NODE, f"{a.fills_prefix}{ds}/"):
                    raw = s3.get(NODE, key)
                    if raw:
                        tr = [t for ln in raw.decode().splitlines() for t in parse_fill_block(ln, set(coins))]
                        dcov["trades"] += len(tr)
                        recs += tr
        if not a.no_binance:
            for c in coins:
                ext, kind, fl = binance_day(bin_sym.get(c, f"{c}USDT"), c, day, flow=a.binance_flow)
                ext = downsample(ext, a.ext_interval_ms)
                dcov["binance"][c] = {"source": kind, "rows": len(ext), "flow": len(fl)}
                recs += ext + fl
        lo = int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp() * 1000)
        for c in coins:
            w = [r for r in whales.get(c, []) if lo <= r["ts"] < lo + 86_400_000]
            dcov["whale"] += len(w)
            recs += w
        hours = write_hours(recs, out) if recs else 0
        cov["days"][day.isoformat()] = dcov
        print(f"{day}: {len(recs):>8} records, {hours} hourly files, books={dcov['book_hours']}, "
              f"ctx={dcov['ctx']}, binance={ {k: v['source'] for k, v in dcov['binance'].items()} }, "
              f"whale={dcov['whale']}" + (f", trades={dcov['trades']}" if a.with_trades else ""))
        day += timedelta(days=1)

    if s3:
        cov["s3_gb_downloaded"] = round(s3.bytes / 1e9, 3)
    missing = {d: v["book_hours"] for d, v in cov["days"].items() if any(n < 24 for n in v["book_hours"].values())}
    cov["days_with_missing_book_hours"] = missing
    rep = Path(a.out).parent / "reports"
    rep.mkdir(parents=True, exist_ok=True)
    (rep / f"import_coverage_{a.start}_{a.end}.json").write_text(json.dumps(cov, indent=2))
    print(f"done. S3 downloaded: {cov.get('s3_gb_downloaded', 0)} GB; days with missing book hours: {len(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
