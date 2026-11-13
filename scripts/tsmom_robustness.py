"""Contrôles de solidité du momentum 6 h (sans réoptimisation).

    python scripts/tsmom_robustness.py --coins BTC,ETH,SOL --from 2020-01 --to 2026-10 --split 2023-12

Le réglage a été choisi AVANT ces contrôles par bar_research.py : L = 28 bougies de 6 h
(≈ 7 jours), long seulement. Critères fixés à l'avance — il « PASSE » si tous tiennent :
  A. voisinage : sur la vérification, ≥ 3 des 4 durées voisines (20, 24, 32, 36) ont un
     rendement > 0 (un vrai effet ne dépend pas d'un réglage précis) ;
  B. marchés : sur la vérification, rendement > 0 sur chacun des marchés pris seul ;
  C. années : ≥ 5 des 7 années civiles 2020-2026 positives (échantillon complet) ;
  D. au-delà du marché : alpha > 0 (régression des rendements journaliers sur un
     portefeuille acheteur équipondéré des mêmes marchés), sur la vérification.
La version long/short (même L) et un risque plus élevé sont reportés pour information.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.bar_research import (H, SYMBOLS, Costs, daily_returns, load_funding, load_klines,  # noqa: E402
                                  months, resample, simulate, summarize, tsmom)


def ms(mo: str) -> float:
    y, m = map(int, mo.split("-"))
    return datetime(y, m, 1, tzinfo=timezone.utc).timestamp() * 1000


def next_month(mo: str) -> str:
    y, m = map(int, mo.split("-"))
    return f"{y + (m == 12):04d}-{m % 12 + 1:02d}"


def run(data, coins, L, long_only, start, end, risk=0.5, costs=Costs()):
    per = {c: simulate(data[c]["6h"], tsmom(data[c]["6h"], L, long_only), costs, *data[c]["fund"],
                       risk_pct=risk, start_ms=start, end_ms=end) for c in coins}
    return per, summarize(per)


def portfolio_daily(per) -> dict[int, float]:
    days: dict[int, list[float]] = {}
    for res in per.values():
        for d, r in daily_returns(res["t"], res["e"]).items():
            days.setdefault(d, []).append(r)
    return {d: float(np.mean(v)) for d, v in days.items()}


def market_daily(data, coins, start, end) -> dict[int, float]:
    days: dict[int, list[float]] = {}
    for c in coins:
        b = data[c]["6h"]
        m = (b.ts >= start) & (b.ts < end)
        t, px = b.ts[m], b.c[m]
        for d, r in daily_returns(t, px / px[0]).items():
            days.setdefault(d, []).append(r)
    return {d: float(np.mean(v)) for d, v in days.items()}


def alpha(strat: dict[int, float], mkt: dict[int, float]) -> dict:
    ks = sorted(set(strat) & set(mkt))
    y = np.asarray([strat[k] for k in ks])
    x = np.asarray([mkt[k] for k in ks])
    X = np.column_stack([np.ones_like(x), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    s2 = resid @ resid / max(len(y) - 2, 1)
    se = math.sqrt(s2 * np.linalg.inv(X.T @ X)[0, 0])
    return {"alpha_ann_pct": round(float(coef[0]) * 365 * 100, 2), "beta": round(float(coef[1]), 3),
            "t_alpha": round(float(coef[0]) / se, 2) if se > 0 else 0.0, "days": len(ks)}


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
    ml = months(a.start, a.end)
    data = {}
    for c in coins:
        sym = SYMBOLS.get(c, f"{c}USDT")
        data[c] = {"6h": resample(load_klines(sym, ml, Path(a.cache)), 6 * H),
                   "fund": load_funding(sym, ml, Path(a.cache))}
    full = (ms(a.start), ms(next_month(a.end)))
    test = (ms(next_month(a.split)), full[1])
    L0, LO = 28, True
    rep: dict = {"chosen": {"L": L0, "long_only": LO}, "periods": {"test": [next_month(a.split), a.end]}}

    # A. voisinage
    rep["A_neighbours"] = {}
    for L in (20, 24, L0, 32, 36):
        for lo in (True, False):
            _, s = run(data, coins, L, lo, *test)
            rep["A_neighbours"][f"L={L} {'long' if lo else 'long/short'}"] = s
    neigh = [rep["A_neighbours"][f"L={L} long"]["return_pct"] for L in (20, 24, 32, 36)]
    A = sum(r > 0 for r in neigh) >= 3

    # B. marchés pris seuls
    per_test, s_test = run(data, coins, L0, LO, *test)
    rep["B_coins"] = {c: summarize({c: per_test[c]}) for c in coins}
    B = all(v["return_pct"] > 0 for v in rep["B_coins"].values())

    # C. années civiles
    rep["C_years"] = {}
    for y in range(int(a.start[:4]), int(a.end[:4]) + 1):
        _, s = run(data, coins, L0, LO, ms(f"{y}-01"), min(ms(f"{y + 1}-01"), full[1]))
        rep["C_years"][str(y)] = s
    C = sum(v["return_pct"] > 0 for v in rep["C_years"].values()) >= 5

    # D. alpha vs marché acheteur
    rep["D_alpha_test"] = alpha(portfolio_daily(per_test), market_daily(data, coins, *test))
    per_ls, _ = run(data, coins, L0, False, *test)
    rep["D_alpha_test_long_short"] = alpha(portfolio_daily(per_ls), market_daily(data, coins, *test))
    D = rep["D_alpha_test"]["alpha_ann_pct"] > 0

    # information : risque plus élevé (levier ≈ 1×) et marché acheteur simple
    rep["info_risk"] = {f"risk {r}%": run(data, coins, L0, LO, *test, risk=r)[1] for r in (0.5, 2.0, 4.0)}
    mk = market_daily(data, coins, *test)
    eq = np.cumprod([1 + mk[k] for k in sorted(mk)])
    dd = 1 - eq / np.maximum.accumulate(eq)
    rep["info_buy_and_hold_test"] = {"return_pct": round((eq[-1] - 1) * 100, 1), "max_dd_pct": round(dd.max() * 100, 1)}

    rep["checks"] = {"A_neighbours": A, "B_coins": B, "C_years": C, "D_alpha": D}
    rep["verdict"] = "PASSE" if all(rep["checks"].values()) else "ÉCHOUE"

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "robustness_tsmom.json").write_text(json.dumps(rep, indent=2, default=str))
    cols = ["trades", "return_pct", "max_dd_pct", "sharpe", "profit_factor", "win_rate"]

    def table(title, d):
        md = [f"## {title}", "", "| | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
        md += [f"| {k} | " + " | ".join(str(v.get(c)) for c in cols) + " |" for k, v in d.items()]
        return md + [""]
    md = [f"# Contrôles de solidité — momentum 6 h (L={L0}, long seulement)", "",
          f"**Verdict : {rep['verdict']}** — {rep['checks']}", "",
          f"Vérification {next_month(a.split)} → {a.end} · marchés {', '.join(coins)}", ""]
    md += table("A. Durées voisines (vérification)", rep["A_neighbours"])
    md += table("B. Chaque marché seul (vérification)", rep["B_coins"])
    md += table("C. Par année civile", rep["C_years"])
    md += ["## D. Au-delà du marché (vérification)", "",
           f"- long seulement : {rep['D_alpha_test']}", f"- long/short : {rep['D_alpha_test_long_short']}",
           f"- marché acheteur équipondéré : {rep['info_buy_and_hold_test']}", ""]
    md += table("Information : effet du risque par trade (vérification)", rep["info_risk"])
    (out / "robustness_tsmom.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
