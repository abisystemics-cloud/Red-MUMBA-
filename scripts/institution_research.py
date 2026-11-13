"""« Suivre les institutions » et géopolitique : est-ce que ça améliore le bot ?

    python scripts/institution_research.py --coins BTC,ETH,SOL --from 2020-01 --to 2026-10 --split 2023-12

Trois signaux avec un historique long, gratuit et public :
- cot      : rapport hebdomadaire de la CFTC (Traders in Financial Futures) sur les
             futures Bitcoin du CME — position nette des « asset managers » (fonds,
             ETF à futures) en hausse sur N semaines. Publié le vendredi pour le mardi :
             utilisé avec 4 jours de retard ;
- premium  : prime Coinbase (BTC-USD Coinbase vs BTCUSDT Binance spot), indicateur
             classique de la demande institutionnelle américaine — moyenne N jours > 0 ;
- gpr      : indice quotidien de risque géopolitique (Caldara & Iacoviello) — pas
             d'entrée quand sa moyenne 7 j dépasse k × sa moyenne 1 an (2 j de retard).

Chaque signal est testé de deux façons, règles fixées À L'AVANCE :
1. comme FILTRE d'entrée du momentum 6 h (L = 28, long seulement) — même règle que
   filter_research.py : réglage choisi sur l'apprentissage, « AIDE » si en vérification
   Sharpe ≥ momentum seul + 0,10, rendement > 0, ≥ 50 % des trades gardés ;
2. SEUL (cot, premium) : acheter quand le signal est vert, sortir quand il s'éteint,
   stop 3 ATR — même règle que bar_research.py : « TIENT » si en vérification
   Sharpe ≥ 0,8, PF ≥ 1,2, rendement > 0, DD < 25 %, rendement > 0 à coûts ×2.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.bar_research import (H, SYMBOLS, Costs, Entry, Strategy, _get, _ms, _rows, atr,  # noqa: E402
                                  load_funding, load_klines, months, resample, simulate, summarize, tsmom)
from scripts.filter_research import _day_ms, _fetch, daily_flag_to_bars, rising, with_filter  # noqa: E402

L0 = 28


# ------------------------------------------------------------------ données
def load_cot(cache: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """→ (dates du mardi, net asset managers, net leveraged funds) en contrats CME BTC."""
    raw = _fetch("https://publicreporting.cftc.gov/resource/gpe5-46if.json?cftc_contract_market_code=133741"
                 "&$limit=5000&$order=report_date_as_yyyy_mm_dd", cache / "macro" / "cot_btc.json")
    t, am, lev = [], [], []
    try:
        for r in json.loads(raw) if raw else []:
            t.append(_day_ms(r["report_date_as_yyyy_mm_dd"][:10]))
            am.append(float(r["asset_mgr_positions_long"]) - float(r["asset_mgr_positions_short"]))
            lev.append(float(r["lev_money_positions_long"]) - float(r["lev_money_positions_short"]))
    except (KeyError, ValueError, TypeError) as e:
        print("  ! COT parse:", e, file=sys.stderr)
        n = min(len(am), len(lev))
        t, am, lev = t[:n], am[:n], lev[:n]
    return np.asarray(t), np.asarray(am), np.asarray(lev)


def load_coinbase_daily(cache: Path, start: str, end: str) -> tuple[np.ndarray, np.ndarray]:
    t0, t1 = _day_ms(start + "-01") / 1000, _day_ms(end + "-28") / 1000 + 4 * 86400
    out: dict[float, float] = {}
    s = t0
    while s < t1:
        e = min(s + 299 * 86400, t1)
        iso = [datetime.fromtimestamp(x, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") for x in (s, e)]
        raw = _fetch(f"https://api.exchange.coinbase.com/products/BTC-USD/candles?granularity=86400"
                     f"&start={iso[0]}&end={iso[1]}", cache / "macro" / f"coinbase_{int(s)}.json")
        try:
            for row in json.loads(raw) if raw else []:
                out[float(row[0]) * 1000] = float(row[4])
        except (ValueError, TypeError, IndexError):
            pass
        s = e + 86400
    ks = sorted(out)
    return np.asarray(ks), np.asarray([out[k] for k in ks])


def load_binance_spot_daily(cache: Path, mlist: list[str]) -> tuple[np.ndarray, np.ndarray]:
    t, c = [], []
    for mo in mlist:
        raw = _get(f"https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1d/BTCUSDT-1d-{mo}.zip",
                   cache / "spot" / f"BTCUSDT-1d-{mo}.zip")
        for r in _rows(raw) if raw else []:
            t.append(float(_ms(r[0])))
            c.append(float(r[4]))
    return np.asarray(t), np.asarray(c)


def load_gpr(cache: Path) -> tuple[np.ndarray, np.ndarray]:
    raw = _fetch("https://www.matteoiacoviello.com/gpr_files/data_gpr_daily_recent.xls",
                 cache / "macro" / "gpr_daily.xls")
    if not raw:
        return np.asarray([]), np.asarray([])
    try:
        import xlrd
        sh = xlrd.open_workbook(file_contents=raw).sheet_by_index(0)
        head = [str(x).strip().upper() for x in sh.row_values(0)]
        i_day, i_gpr = head.index("DAY"), head.index("GPRD")
        t, v = [], []
        for r in range(1, sh.nrows):
            row = sh.row_values(r)
            try:
                d = str(int(float(row[i_day])))
                t.append(_day_ms(f"{d[:4]}-{d[4:6]}-{d[6:8]}"))
                v.append(float(row[i_gpr]))
            except (ValueError, TypeError):
                if len(t) > len(v):
                    t.pop()
        return np.asarray(t), np.asarray(v)
    except Exception as e:  # noqa: BLE001 — format externe : on signale et on continue sans
        print("  ! GPR parse:", e, file=sys.stderr)
        return np.asarray([]), np.asarray([])


def trailing_mean(v: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        c = np.cumsum(np.concatenate([[0.0], v]))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def calm(v: np.ndarray, k: float) -> np.ndarray:
    short, long_ = trailing_mean(v, 7), trailing_mean(v, 365)
    return np.isfinite(long_) & (short <= k * long_)


def positive_mean(v: np.ndarray, n: int) -> np.ndarray:
    m = trailing_mean(v, n)
    return np.isfinite(m) & (m > 0)


def follow(b, flag: np.ndarray, stop_atr: float = 3.0) -> Strategy:
    """Signal seul : long tant que le drapeau est vert."""
    a = atr(b, 14)

    def entry(i: int):
        return Entry(+1, b.c[i] - stop_atr * a[i], None) if flag[i] and np.isfinite(a[i]) else None
    return Strategy(entry, lambda i, s, e: not flag[i], warmup=20)


# --------------------------------------------------------------------- main
def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--coins", default="BTC,ETH,SOL")
    p.add_argument("--from", dest="start", default="2020-01")
    p.add_argument("--to", dest="end", default="2026-10")
    p.add_argument("--split", default="2023-12")
    p.add_argument("--cache", default="data/bars")
    p.add_argument("--out", default="data/reports")
    a = p.parse_args()
    coins, cache, ml = a.coins.split(","), Path(a.cache), months(a.start, a.end)

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
    cot_t, cot_am, cot_lev = load_cot(cache)
    cb_t, cb_c = load_coinbase_daily(cache, "2019-06", a.end)
    bn_t, bn_c = load_binance_spot_daily(cache, months("2019-06", a.end))
    common = np.intersect1d(cb_t, bn_t)
    prem = cb_c[np.searchsorted(cb_t, common)] / bn_c[np.searchsorted(bn_t, common)] - 1 if len(common) else np.asarray([])
    gpr_t, gpr_v = load_gpr(cache)
    sources = {"cot_weeks": len(cot_t), "coinbase_days": len(cb_t), "premium_days": len(common), "gpr_days": len(gpr_t)}
    print("sources", sources, flush=True)

    def close_ts(c):
        return data[c]["6h"].ts + 6 * H

    grids = {
        "cot_asset_managers": [({"net_rising_weeks": n}, (lambda c, n=n: daily_flag_to_bars(close_ts(c), cot_t, rising(cot_am, n), 4)))
                               for n in (2, 4, 8)] if len(cot_t) > 100 else [],
        "coinbase_premium": [({"mean_days": n}, (lambda c, n=n: daily_flag_to_bars(close_ts(c), common, positive_mean(prem, n), 1.01)))
                             for n in (3, 7, 14)] if len(common) > 500 else [],
        "geopolitical_risk": [({"max_ratio_vs_1y": k}, (lambda c, k=k: daily_flag_to_bars(close_ts(c), gpr_t, calm(gpr_v, k), 2)))
                              for k in (1.25, 1.5, 2.0)] if len(gpr_t) > 500 else [],
    }

    def run(build, window, costs=Costs()):
        per, share = {}, []
        for c in coins:
            b = data[c]["6h"]
            st, al = build(c, b)
            if al is not None:
                m = (b.ts >= window[0]) & (b.ts < window[1])
                share.append(float(al[m].mean()) if m.any() else 0.0)
            per[c] = simulate(b, st, costs, *data[c]["fund"], start_ms=window[0], end_ms=window[1])
        s = summarize(per)
        s["signal_on_pct"] = round(float(np.mean(share)) * 100, 1) if share else 100.0
        return s

    def as_filter(fn):
        def build(c, b):
            al = fn(c)
            return with_filter(tsmom(b, L0, True), al), al
        return build

    def alone(fn):
        def build(c, b):
            al = fn(c)
            return follow(b, al), al
        return build

    def base_build(c, b):
        return tsmom(b, L0, True), None
    base = {"train": run(base_build, train), "test": run(base_build, test)}
    rep = {"sources": sources, "baseline_momentum": base, "as_filter": {}, "alone": {},
           "periods": {"train": [a.start, a.split], "test": [nxt(a.split), a.end]}}
    for name, grid in grids.items():
        if not grid:
            rep["as_filter"][name] = rep["alone"][name] = {"verdict": "DONNÉES INDISPONIBLES", "rows": [], "choice": None}
            continue
        # 1) filtre du momentum
        rows = [{"params": prm, "train": run(as_filter(fn), train), "test": run(as_filter(fn), test)} for prm, fn in grid]
        ok = [r for r in rows if r["train"]["trades"] >= 0.5 * base["train"]["trades"]]
        ch = max(ok, key=lambda r: r["train"]["sharpe"]) if ok else None
        verdict = "pas de réglage éligible"
        if ch:
            t = ch["test"]
            verdict = "AIDE" if (t["sharpe"] >= base["test"]["sharpe"] + 0.10 and t["return_pct"] > 0
                                 and t["trades"] >= 0.5 * base["test"]["trades"]) else "N'AIDE PAS"
        rep["as_filter"][name] = {"rows": rows, "choice": ch["params"] if ch else None, "verdict": verdict}
        # 2) signal seul
        if name == "geopolitical_risk":
            continue
        rows = [{"params": prm, "train": run(alone(fn), train), "test": run(alone(fn), test)} for prm, fn in grid]
        ok = [r for r in rows if r["train"]["trades"] >= 40]
        ch = max(ok, key=lambda r: r["train"]["sharpe"]) if ok else None
        verdict, stress = "pas de réglage éligible (trop peu de trades)", None
        if ch:
            fn = grid[rows.index(ch)][1]
            stress = run(alone(fn), test, Costs(mult=2.0))
            t = ch["test"]
            verdict = "TIENT" if (t["sharpe"] >= 0.8 and t["profit_factor"] >= 1.2 and t["return_pct"] > 0
                                  and t["max_dd_pct"] < 25 and stress["return_pct"] > 0) else "NE TIENT PAS"
        rep["alone"][name] = {"rows": rows, "choice": ch["params"] if ch else None, "verdict": verdict, "stress": stress}
        print(name, rep["as_filter"][name]["verdict"], "|", verdict, flush=True)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "institutions.json").write_text(json.dumps(rep, indent=2, default=str))
    cols = ["trades", "signal_on_pct", "return_pct", "max_dd_pct", "sharpe", "profit_factor", "win_rate"]

    def line(label, per, s):
        return f"| {label} | {per} | " + " | ".join(str(s.get(c)) for c in cols) + " |"
    md = ["# Suivre les institutions et la géopolitique — tests", "",
          f"Apprentissage {a.start} → {a.split} · vérification {nxt(a.split)} → {a.end} · {', '.join(coins)}", "",
          f"Sources : {sources}", "", "| signal | comme filtre du momentum | seul |", "|---|---|---|"]
    for k in grids:
        f, s = rep["as_filter"][k], rep["alone"].get(k, {"verdict": "non testé seul", "choice": None})
        md.append(f"| {k} | **{f['verdict']}** {f['choice'] or ''} | **{s['verdict']}** {s['choice'] or ''} |")
    for title, block in (("Comme filtre du momentum", rep["as_filter"]), ("Signal seul", rep["alone"])):
        md += ["", f"## {title}", "", "| réglage | période | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
        if title.startswith("Comme"):
            md += [line("momentum seul", "train", base["train"]), line("momentum seul", "test", base["test"])]
        for k, v in block.items():
            for r in v["rows"]:
                md += [line(f"{k} {r['params']}", "train", r["train"]), line(f"{k} {r['params']}", "test", r["test"])]
    (out / "institutions.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
