"""Plus de trades par l'ÉTENDUE (30 marchés) et par des horizons plus courts (1 h).

    python scripts/universe_research.py --from 2020-01 --to 2026-10 --split 2023-12

Deux questions, règles fixées À L'AVANCE :

1. Le momentum 6 h (L = 28), réglé sur BTC/ETH/SOL uniquement, marche-t-il tel quel
   sur 27 AUTRES marchés qu'il n'a jamais vus ? (aucun réglage → test hors échantillon
   pur). « PASSE » si, sur la vérification : Sharpe ≥ 0,5, rendement > 0, et ≥ 60 % des
   marchés positifs sur toute la période.

2. Des stratégies plus actives sur bougies 1 h, sur les 30 marchés :
   - breakout  : cassure du plus haut/bas de N heures, sortie sur le canal N/2 ;
   - tsmom_1h  : momentum sur 24 / 72 heures ;
   - reversal  : rebond après une bougie de panique (chute > k ATR sur gros volume).
   Réglage choisi sur l'apprentissage (≥ 200 trades), « TIENT » si en vérification
   Sharpe ≥ 0,8, PF ≥ 1,2, rendement > 0, DD < 25 % et rendement > 0 à coûts ×2.

Biais connu : les 30 marchés sont ceux qui existent encore aujourd'hui (survivants).
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.bar_research import (BASE, H, Bars, Costs, Entry, Strategy, _get, atr, load_funding,  # noqa: E402
                                  load_klines, months, resample, simulate, summarize, tsmom)

CORE = ["BTC", "ETH", "SOL"]
OTHERS = ["BNB", "XRP", "DOGE", "ADA", "AVAX", "LINK", "LTC", "DOT", "ATOM", "NEAR", "APT", "ARB", "OP", "SUI",
          "INJ", "TIA", "SEI", "AAVE", "UNI", "FIL", "BCH", "ETC", "XLM", "TRX", "HBAR", "ICP", "RUNE"]


def prev_max(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) > n:
        out[n:] = sliding_window_view(x, n)[:-1].max(axis=1)
    return out


def prev_min(x: np.ndarray, n: int) -> np.ndarray:
    return -prev_max(-x, n)


def prev_median(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) > n:
        out[n:] = np.median(sliding_window_view(x, n)[:-1], axis=1)
    return out


def breakout(b: Bars, n: int) -> Strategy:
    a = atr(b, 14)
    hi, lo = prev_max(b.h, n), prev_min(b.l, n)
    xhi, xlo = prev_max(b.h, n // 2), prev_min(b.l, n // 2)

    def entry(i: int):
        if not (np.isfinite(hi[i]) and np.isfinite(a[i])):
            return None
        if b.c[i] > hi[i]:
            return Entry(+1, b.c[i] - 2 * a[i], None)
        if b.c[i] < lo[i]:
            return Entry(-1, b.c[i] + 2 * a[i], None)
        return None

    def exit_(i: int, side: int, i0: int) -> bool:
        return b.c[i] < xlo[i] if side > 0 else b.c[i] > xhi[i]
    return Strategy(entry, exit_, warmup=n + 20)


def reversal(b: Bars, k: float, hold: int) -> Strategy:
    a = atr(b, 14)
    vmed = prev_median(b.v, 24)

    def entry(i: int):
        if i < 30 or not np.isfinite(a[i - 1]) or not np.isfinite(vmed[i]) or b.v[i] < 2 * vmed[i]:
            return None
        move = b.c[i] - b.o[i]
        if move < -k * a[i - 1]:
            return Entry(+1, b.l[i] - 0.5 * a[i - 1], None, max_bars=hold)
        if move > k * a[i - 1]:
            return Entry(-1, b.h[i] + 0.5 * a[i - 1], None, max_bars=hold)
        return None
    return Strategy(entry, warmup=40)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start", default="2020-01")
    p.add_argument("--to", dest="end", default="2026-10")
    p.add_argument("--split", default="2023-12")
    p.add_argument("--coins", default=None, help="ignoré (univers fixe)")
    p.add_argument("--cache", default="data/bars")
    p.add_argument("--out", default="data/reports")
    a = p.parse_args()
    cache, ml = Path(a.cache), months(a.start, a.end)
    coins = CORE + OTHERS

    def prefetch(job):
        kind, sym, mo = job
        if kind == "k":
            _get(f"{BASE}/klines/{sym}/1h/{sym}-1h-{mo}.zip", cache / "klines" / sym / f"1h-{mo}.zip")
        else:
            _get(f"{BASE}/fundingRate/{sym}/{sym}-fundingRate-{mo}.zip", cache / "funding" / sym / f"{mo}.zip")
    jobs = [(k, f"{c}USDT", mo) for c in coins for mo in ml for k in ("k", "f")]
    with ThreadPoolExecutor(16) as ex:
        list(ex.map(prefetch, jobs))
    data = {}
    for c in coins:
        b1 = load_klines(f"{c}USDT", ml, cache, "1h")
        if len(b1) < 2000:
            print("skip", c, len(b1), flush=True)
            continue
        data[c] = {"1h": b1, "6h": resample(b1, 6 * H), "fund": load_funding(f"{c}USDT", ml, cache)}
    coins = [c for c in coins if c in data]
    others = [c for c in OTHERS if c in data]
    print("marchés chargés :", len(coins), flush=True)

    def ms(mo: str) -> float:
        y, m = map(int, mo.split("-"))
        return datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000

    def nxt(mo: str) -> str:
        y, m = map(int, mo.split("-"))
        return f"{y + (m == 12):04d}-{m % 12 + 1:02d}"
    train, test, full = (ms(a.start), ms(nxt(a.split))), (ms(nxt(a.split)), ms(nxt(a.end))), (ms(a.start), ms(nxt(a.end)))

    def run(build, tf, window, universe, costs=Costs()):
        per = {c: simulate(data[c][tf], build(data[c][tf]), costs, *data[c]["fund"],
                           start_ms=window[0], end_ms=window[1]) for c in universe}
        s = summarize(per)
        s["trades_per_month"] = round(s["trades"] / max((window[1] - window[0]) / (30.44 * 86_400_000), 1), 1)
        return per, s

    rep: dict = {"universe": coins, "periods": {"train": [a.start, a.split], "test": [nxt(a.split), a.end]}}

    # 1) momentum 6 h, réglage gelé, sur les marchés jamais vus
    q1 = {}
    for label, lo in (("long seulement", True), ("long/short", False)):
        def build(b, lo=lo):
            return tsmom(b, 28, lo)
        per_full, s_full = run(build, "6h", full, others)
        _, s_test = run(build, "6h", test, others)
        _, s_all = run(build, "6h", test, coins)
        pos = [summarize({c: per_full[c]})["return_pct"] > 0 for c in others]
        ok = s_test["sharpe"] >= 0.5 and s_test["return_pct"] > 0 and np.mean(pos) >= 0.6
        q1[label] = {"others_full": s_full, "others_test": s_test, "all30_test": s_all,
                     "coins_positive_pct": round(float(np.mean(pos)) * 100), "verdict": "PASSE" if ok else "ÉCHOUE"}
        print("momentum 6h", label, q1[label]["verdict"], flush=True)
    rep["momentum_6h_unseen_markets"] = q1

    # 2) familles plus actives sur 1 h
    grids = {
        "breakout": [({"n_hours": n}, (lambda b, n=n: breakout(b, n))) for n in (24, 48, 96)],
        "tsmom_1h": [({"lookback_h": n, "long_only": lo}, (lambda b, n=n, lo=lo: tsmom(b, n, lo)))
                     for n in (24, 72) for lo in (True, False)],
        "reversal": [({"k_atr": k, "hold_h": hh}, (lambda b, k=k, hh=hh: reversal(b, k, hh)))
                     for k in (2.0, 3.0) for hh in (4, 12)],
    }
    rep["active_1h"] = {}
    for fam, grid in grids.items():
        rows = [{"params": prm, "train": run(fn, "1h", train, coins)[1], "test": run(fn, "1h", test, coins)[1]}
                for prm, fn in grid]
        ok = [r for r in rows if r["train"]["trades"] >= 200]
        ch = max(ok, key=lambda r: r["train"]["sharpe"]) if ok else None
        verdict, stress = "pas de réglage éligible", None
        if ch:
            stress = run(grid[rows.index(ch)][1], "1h", test, coins, Costs(mult=2.0))[1]
            t = ch["test"]
            verdict = "TIENT" if (t["sharpe"] >= 0.8 and t["profit_factor"] >= 1.2 and t["return_pct"] > 0
                                  and t["max_dd_pct"] < 25 and stress["return_pct"] > 0) else "NE TIENT PAS"
        rep["active_1h"][fam] = {"rows": rows, "choice": ch["params"] if ch else None, "verdict": verdict, "stress": stress}
        print(fam, verdict, flush=True)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "universe.json").write_text(json.dumps(rep, indent=2, default=str))
    cols = ["trades", "trades_per_month", "return_pct", "max_dd_pct", "sharpe", "profit_factor", "win_rate"]

    def line(label, per, s):
        return f"| {label} | {per} | " + " | ".join(str(s.get(c)) for c in cols) + " |"
    head = ["| | période | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
    md = [f"# Univers élargi ({len(coins)} marchés) et stratégies 1 h", "",
          f"Apprentissage {a.start} → {a.split} · vérification {nxt(a.split)} → {a.end}", "",
          "## 1. Momentum 6 h (réglage gelé) sur les marchés jamais vus", ""] + head
    for label, v in q1.items():
        md += [line(f"{label} — {len(others)} autres marchés", "tout", v["others_full"]),
               line(f"{label} — {len(others)} autres marchés", "test", v["others_test"]),
               line(f"{label} — les {len(coins)} marchés", "test", v["all30_test"]),
               f"| {label} | verdict | **{v['verdict']}** ({v['coins_positive_pct']} % des marchés positifs) |" + " |" * (len(cols) - 1)]
    md += ["", "## 2. Stratégies actives sur 1 h", "", "| famille | réglage choisi | verdict | coûts ×2 (rendement %) |", "|---|---|---|---|"]
    md += [f"| {k} | {v['choice']} | **{v['verdict']}** | {v['stress']['return_pct'] if v['stress'] else '-'} |"
           for k, v in rep["active_1h"].items()]
    md += [""] + head
    for k, v in rep["active_1h"].items():
        for r in v["rows"]:
            md += [line(f"{k} {r['params']}", "train", r["train"]), line(f"{k} {r['params']}", "test", r["test"])]
    (out / "universe.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
