"""Filtres « fondamentaux » posés sur le momentum 6 h (L = 28, long seulement).

    python scripts/filter_research.py --coins BTC,ETH,SOL --from 2020-01 --to 2026-10 --split 2023-12

Trois filtres d'ENTRÉE, pas plus (un filtre n'interdit que l'ouverture d'une position ;
les sorties restent celles du momentum) :
- macro       : Nasdaq Composite au-dessus de sa moyenne N jours (FRED, série NASDAQCOM) ;
- stablecoins : offre totale de stablecoins en hausse sur N jours (DefiLlama) ;
- fomc        : pas d'entrée dans les K heures avant une décision de la Fed (ni 6 h après).

Sans regard vers le futur : une valeur journalière datée J n'est utilisée qu'à partir
de J + 2 jours (Nasdaq) ou J + 1 jour (stablecoins).

Règle fixée À L'AVANCE, par filtre : réglage au meilleur Sharpe d'apprentissage parmi
ceux qui gardent ≥ 50 % des trades du momentum seul. Le filtre « AIDE » si, sur la
vérification jamais vue, Sharpe ≥ Sharpe du momentum seul + 0,10, rendement > 0 et
≥ 50 % des trades conservés. Sinon il est écarté.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.bar_research import (H, SYMBOLS, Costs, Strategy, load_funding, load_klines, months,  # noqa: E402
                                  resample, simulate, summarize, tsmom)

DAY = 86_400_000
L0 = 28

# Décisions du FOMC (date de l'annonce, ~19:00 UTC), réunions d'urgence de mars 2020 incluses.
FOMC = """2020-01-29 2020-03-03 2020-03-15 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05 2020-12-16
2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15
2022-01-26 2022-03-16 2022-05-04 2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14
2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01 2023-12-13
2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18
2025-01-29 2025-03-19 2025-05-07 2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10
2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29 2026-09-16 2026-10-28 2026-12-09""".split()


def _day_ms(d: str) -> float:
    return datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000


def _fetch(url: str, cache: Path) -> Optional[bytes]:
    if cache.exists() and cache.stat().st_size > 0:
        return cache.read_bytes()
    cache.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (hl-swarm research)"})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
            cache.write_bytes(data)
            return data
        except Exception as e:  # noqa: BLE001 — réseau : on réessaie puis on signale
            print(f"  ! {url}: {e}", file=sys.stderr, flush=True)
            time.sleep(3 * (attempt + 1))
    return None


def load_fred(series: str, cache_dir: Path) -> tuple[np.ndarray, np.ndarray]:
    raw = _fetch(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd=2018-06-01",
                 cache_dir / "macro" / f"{series}.csv")
    ts, val = [], []
    for row in csv.reader(io.StringIO(raw.decode())) if raw else []:
        try:
            ts.append(_day_ms(row[0]))
            val.append(float(row[1]))
        except (ValueError, IndexError):
            if ts and len(ts) > len(val):
                ts.pop()
    return np.asarray(ts), np.asarray(val)


def load_nasdaq(cache_dir: Path) -> tuple[np.ndarray, np.ndarray, str]:
    """Nasdaq Composite journalier : FRED, sinon Yahoo Finance, sinon Stooq."""
    t, v = load_fred("NASDAQCOM", cache_dir)
    if len(t) > 500:
        return t, v, "fred"
    raw = _fetch("https://query1.finance.yahoo.com/v8/finance/chart/%5EIXIC?period1=1527811200&period2=1900000000"
                 "&interval=1d", cache_dir / "macro" / "ixic_yahoo.json")
    try:
        res = json.loads(raw)["chart"]["result"][0]
        ts = np.asarray(res["timestamp"], dtype=np.float64)
        cl = np.asarray([np.nan if x is None else x for x in res["indicators"]["quote"][0]["close"]], dtype=np.float64)
        ok = np.isfinite(cl)
        ts = np.floor(ts[ok] / 86400) * DAY  # date de séance à 00:00 UTC
        if ok.sum() > 500:
            return ts, cl[ok], "yahoo"
    except (TypeError, KeyError, ValueError, IndexError):
        pass
    raw = _fetch("https://stooq.com/q/d/l/?s=^ndq&i=d", cache_dir / "macro" / "ndq_stooq.csv")
    ts, val = [], []
    for row in csv.reader(io.StringIO(raw.decode(errors="ignore"))) if raw else []:
        try:
            d, c = _day_ms(row[0]), float(row[4])
        except (ValueError, IndexError):
            continue
        if d >= _day_ms("2018-06-01"):
            ts.append(d)
            val.append(c)
    return np.asarray(ts), np.asarray(val), "stooq" if len(ts) > 500 else "indisponible"


def load_stablecoins(cache_dir: Path) -> tuple[np.ndarray, np.ndarray]:
    raw = _fetch("https://stablecoins.llama.fi/stablecoincharts/all", cache_dir / "macro" / "stablecoins.json")
    ts, val = [], []
    for it in json.loads(raw) if raw else []:
        tot = it.get("totalCirculatingUSD") or {}
        v = sum(float(x) for x in tot.values() if isinstance(x, (int, float)))
        if v > 0:
            ts.append(float(it["date"]) * 1000)
            val.append(v)
    return np.asarray(ts), np.asarray(val)


# ---------------------------------------------------------------- filtres
def daily_flag_to_bars(bar_close: np.ndarray, t: np.ndarray, flag: np.ndarray, lag_days: float) -> np.ndarray:
    """flag[j] (calculé avec les données jusqu'à t[j] inclus) n'est utilisable qu'à t[j] + lag."""
    if len(t) == 0:
        return np.zeros(len(bar_close), bool)
    idx = np.searchsorted(t + lag_days * DAY, bar_close, side="right") - 1
    out = np.zeros(len(bar_close), bool)
    ok = idx >= 0
    out[ok] = flag[idx[ok]]
    return out


def above_sma(v: np.ndarray, n: int) -> np.ndarray:
    out = np.zeros(len(v), bool)
    if len(v) > n:
        c = np.cumsum(np.concatenate([[0.0], v]))
        sma = (c[n:] - c[:-n]) / n
        out[n - 1:] = v[n - 1:] > sma
    return out


def rising(v: np.ndarray, n: int) -> np.ndarray:
    out = np.zeros(len(v), bool)
    out[n:] = v[n:] > v[:-n]
    return out


def fomc_allow(bar_close: np.ndarray, before_h: int, after_h: int = 6) -> np.ndarray:
    allow = np.ones(len(bar_close), bool)
    for d in FOMC:
        dec = _day_ms(d) + 19 * H
        allow &= ~((bar_close >= dec - before_h * H) & (bar_close < dec + after_h * H))
    return allow


def with_filter(strat: Strategy, allow: np.ndarray) -> Strategy:
    return Strategy(lambda i: strat.entry(i) if allow[i] else None, strat.exit, strat.warmup)


# ------------------------------------------------------------------- main
def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--coins", default="BTC,ETH,SOL")
    p.add_argument("--from", dest="start", default="2020-01")
    p.add_argument("--to", dest="end", default="2026-10")
    p.add_argument("--split", default="2023-12")
    p.add_argument("--cache", default="data/bars")
    p.add_argument("--out", default="data/reports")
    a = p.parse_args()
    coins = a.coins.split(",")
    cache = Path(a.cache)
    ml = months(a.start, a.end)

    def ms(mo: str) -> float:
        y, m = map(int, mo.split("-"))
        return datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000

    def nxt(mo: str) -> str:
        y, m = map(int, mo.split("-"))
        return f"{y + (m == 12):04d}-{m % 12 + 1:02d}"
    train, test = (ms(a.start), ms(nxt(a.split))), (ms(nxt(a.split)), ms(nxt(a.end)))

    data = {}
    for c in coins:
        sym = SYMBOLS.get(c, f"{c}USDT")
        data[c] = {"6h": resample(load_klines(sym, ml, cache), 6 * H), "fund": load_funding(sym, ml, cache)}
    nq_t, nq_v, nq_src = load_nasdaq(cache)
    if nq_src == "indisponible":
        nq_t, nq_v = np.asarray([]), np.asarray([])
    st_t, st_v = load_stablecoins(cache)
    sources = {"nasdaq_days": len(nq_t), "nasdaq_source": nq_src, "stablecoin_days": len(st_t), "fomc_dates": len(FOMC)}
    print("sources", sources, flush=True)

    def close_ts(c):
        return data[c]["6h"].ts + 6 * H

    grids: dict[str, list[tuple[dict, callable]]] = {
        "macro": [({"nasdaq_sma_days": n}, (lambda c, n=n: daily_flag_to_bars(close_ts(c), nq_t, above_sma(nq_v, n), 2)))
                  for n in (50, 100, 200)] if len(nq_t) else [],
        "stablecoins": [({"rising_days": n}, (lambda c, n=n: daily_flag_to_bars(close_ts(c), st_t, rising(st_v, n), 1)))
                        for n in (7, 14, 30)] if len(st_t) else [],
        "fomc": [({"no_entry_hours_before": k}, (lambda c, k=k: fomc_allow(close_ts(c), k))) for k in (24, 48, 72)],
    }

    def run(allow_fn, window, costs=Costs()):
        per, share = {}, []
        for c in coins:
            b = data[c]["6h"]
            st = tsmom(b, L0, True)
            if allow_fn is not None:
                al = allow_fn(c)
                m = (b.ts >= window[0]) & (b.ts < window[1])
                share.append(float(al[m].mean()) if m.any() else 0.0)
                st = with_filter(st, al)
            per[c] = simulate(b, st, costs, *data[c]["fund"], start_ms=window[0], end_ms=window[1])
        s = summarize(per)
        s["allowed_pct"] = round(float(np.mean(share)) * 100, 1) if share else 100.0
        return s

    base = {"train": run(None, train), "test": run(None, test)}
    rep = {"strategy": {"L": L0, "long_only": True}, "sources": sources, "baseline": base, "filters": {},
           "periods": {"train": [a.start, a.split], "test": [nxt(a.split), a.end]}}
    helpful = []
    for name, grid in grids.items():
        if not grid:
            rep["filters"][name] = {"verdict": "DONNÉES INDISPONIBLES", "rows": [], "choice": None}
            continue
        rows = [{"params": prm, "train": run(fn, train), "test": run(fn, test)} for prm, fn in grid]
        ok = [r for r in rows if r["train"]["trades"] >= 0.5 * base["train"]["trades"]]
        choice = max(ok, key=lambda r: r["train"]["sharpe"]) if ok else None
        verdict = "pas de réglage éligible"
        if choice:
            t = choice["test"]
            helps = (t["sharpe"] >= base["test"]["sharpe"] + 0.10 and t["return_pct"] > 0
                     and t["trades"] >= 0.5 * base["test"]["trades"])
            verdict = "AIDE" if helps else "N'AIDE PAS"
            if helps:
                helpful.append(grid[rows.index(choice)][1])
        rep["filters"][name] = {"rows": rows, "choice": choice["params"] if choice else None, "verdict": verdict}
        print(name, verdict, flush=True)
    if len(helpful) > 1:
        def both(c):
            al = helpful[0](c)
            for f in helpful[1:]:
                al = al & f(c)
            return al
        rep["combined_helpful"] = {"train": run(both, train), "test": run(both, test)}

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "filters_tsmom.json").write_text(json.dumps(rep, indent=2, default=str))
    cols = ["trades", "allowed_pct", "return_pct", "max_dd_pct", "sharpe", "profit_factor", "win_rate"]

    def line(label, per, s):
        return f"| {label} | {per} | " + " | ".join(str(s.get(c)) for c in cols) + " |"
    md = [f"# Filtres fondamentaux sur le momentum 6 h (L={L0}, long seulement)", "",
          f"Apprentissage {a.start} → {a.split} · vérification {nxt(a.split)} → {a.end} · {', '.join(coins)}", "",
          f"Sources : {sources}", "",
          "| filtre | réglage choisi | verdict |", "|---|---|---|"]
    md += [f"| {k} | {v['choice']} | **{v['verdict']}** |" for k, v in rep["filters"].items()]
    md += ["", "| réglage | période | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols),
           line("momentum seul", "train", base["train"]), line("momentum seul", "test", base["test"])]
    for k, v in rep["filters"].items():
        for r in v["rows"]:
            md += [line(f"{k} {r['params']}", "train", r["train"]), line(f"{k} {r['params']}", "test", r["test"])]
    if "combined_helpful" in rep:
        md += [line("filtres utiles combinés", "train", rep["combined_helpful"]["train"]),
               line("filtres utiles combinés", "test", rep["combined_helpful"]["test"])]
    (out / "filters_tsmom.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
