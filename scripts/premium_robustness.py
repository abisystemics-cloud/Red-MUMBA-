"""Contrôles de solidité du signal « prime Coinbase » (sans réoptimisation).

    python scripts/premium_robustness.py --coins BTC,ETH,SOL --from 2020-01 --to 2026-10 --split 2023-12

Réglage choisi AVANT ces contrôles par institution_research.py : moyenne 7 jours de la
prime Coinbase > 0 → long, sortie quand elle repasse ≤ 0, stop 3 ATR. Mêmes critères
que pour le momentum, fixés à l'avance — « PASSE » si tous tiennent :
  A. voisinage : en vérification, ≥ 3 des 4 durées voisines (5, 6, 8, 9 jours) > 0 ;
  B. marchés : en vérification, rendement > 0 sur chaque marché pris seul ;
  C. années : ≥ 5 des 7 années civiles positives ;
  D. au-delà du marché : alpha > 0 face à un portefeuille acheteur équipondéré.
Pour information : corrélation avec le momentum 6 h et portefeuille 50/50 des deux.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.bar_research import H, SYMBOLS, Costs, load_funding, load_klines, months, resample, simulate, summarize, tsmom  # noqa: E402
from scripts.filter_research import daily_flag_to_bars  # noqa: E402
from scripts.institution_research import follow, load_binance_spot_daily, load_coinbase_daily, positive_mean  # noqa: E402
from scripts.tsmom_robustness import alpha, market_daily, ms, next_month, portfolio_daily  # noqa: E402

N0 = 7


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
    data = {}
    for c in coins:
        sym = SYMBOLS.get(c, f"{c}USDT")
        data[c] = {"6h": resample(load_klines(sym, ml, cache), 6 * H), "fund": load_funding(sym, ml, cache)}
    cb_t, cb_c = load_coinbase_daily(cache, "2019-06", a.end)
    bn_t, bn_c = load_binance_spot_daily(cache, months("2019-06", a.end))
    common = np.intersect1d(cb_t, bn_t)
    if len(common) < 500:
        print("données de prime indisponibles")
        return 1
    prem = cb_c[np.searchsorted(cb_t, common)] / bn_c[np.searchsorted(bn_t, common)] - 1
    full = (ms(a.start), ms(next_month(a.end)))
    test = (ms(next_month(a.split)), full[1])

    def run(n, window, only=None, risk=0.5, costs=Costs()):
        per = {}
        for c in only or coins:
            b = data[c]["6h"]
            flag = daily_flag_to_bars(b.ts + 6 * H, common, positive_mean(prem, n), 1.01)
            per[c] = simulate(b, follow(b, flag), costs, *data[c]["fund"], risk_pct=risk,
                              start_ms=window[0], end_ms=window[1])
        return per, summarize(per)

    rep: dict = {"chosen": {"mean_days": N0}, "periods": {"test": [next_month(a.split), a.end]}}
    rep["A_neighbours"] = {f"{n} jours": run(n, test)[1] for n in (5, 6, N0, 8, 9)}
    A = sum(rep["A_neighbours"][f"{n} jours"]["return_pct"] > 0 for n in (5, 6, 8, 9)) >= 3
    per_test, _ = run(N0, test)
    rep["B_coins"] = {c: summarize({c: per_test[c]}) for c in coins}
    B = all(v["return_pct"] > 0 for v in rep["B_coins"].values())
    rep["C_years"] = {}
    for y in range(int(a.start[:4]), int(a.end[:4]) + 1):
        rep["C_years"][str(y)] = run(N0, (ms(f"{y}-01"), min(ms(f"{y + 1}-01"), full[1])))[1]
    C = sum(v["return_pct"] > 0 for v in rep["C_years"].values()) >= 5
    strat_d = portfolio_daily(per_test)
    rep["D_alpha_test"] = alpha(strat_d, market_daily(data, coins, *test))
    D = rep["D_alpha_test"]["alpha_ann_pct"] > 0

    # information : lien avec le momentum, portefeuille 50/50, risque plus élevé
    mom = {c: simulate(data[c]["6h"], tsmom(data[c]["6h"], 28, True), Costs(), *data[c]["fund"],
                       start_ms=test[0], end_ms=test[1]) for c in coins}
    mom_d = portfolio_daily(mom)
    ks = sorted(set(strat_d) & set(mom_d))
    x, y = np.asarray([strat_d[k] for k in ks]), np.asarray([mom_d[k] for k in ks])
    combo = (x + y) / 2
    eq = np.cumprod(1 + combo)

    def sharpe(r):
        return round(float(r.mean() / r.std(ddof=1) * np.sqrt(365)), 2) if r.std() > 0 else 0.0
    rep["info_vs_momentum"] = {"correlation": round(float(np.corrcoef(x, y)[0, 1]), 2),
                               "sharpe_premium": sharpe(x), "sharpe_momentum": sharpe(y), "sharpe_50_50": sharpe(combo),
                               "return_50_50_pct": round(float(eq[-1] - 1) * 100, 2),
                               "max_dd_50_50_pct": round(float((1 - eq / np.maximum.accumulate(eq)).max()) * 100, 2)}
    rep["info_risk"] = {f"risk {r}%": run(N0, test, risk=r)[1] for r in (0.5, 2.0, 4.0)}
    rep["info_costs_x2"] = run(N0, test, costs=Costs(mult=2.0))[1]
    rep["checks"] = {"A_neighbours": bool(A), "B_coins": bool(B), "C_years": bool(C), "D_alpha": bool(D)}
    rep["verdict"] = "PASSE" if all(rep["checks"].values()) else "ÉCHOUE"

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "robustness_premium.json").write_text(json.dumps(rep, indent=2, default=str))
    cols = ["trades", "return_pct", "max_dd_pct", "sharpe", "profit_factor", "win_rate"]

    def table(title, d):
        md = [f"## {title}", "", "| | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
        return md + [f"| {k} | " + " | ".join(str(v.get(c)) for c in cols) + " |" for k, v in d.items()] + [""]
    md = [f"# Contrôles de solidité — prime Coinbase (moyenne {N0} jours > 0)", "",
          f"**Verdict : {rep['verdict']}** — {rep['checks']}", "",
          f"Vérification {next_month(a.split)} → {a.end} · marchés {', '.join(coins)}", ""]
    md += table("A. Durées voisines (vérification)", rep["A_neighbours"])
    md += table("B. Chaque marché seul (vérification)", rep["B_coins"])
    md += table("C. Par année civile", rep["C_years"])
    md += ["## D. Au-delà du marché (vérification)", "", f"- {rep['D_alpha_test']}", "",
           "## Information", "", f"- lien avec le momentum : {rep['info_vs_momentum']}",
           f"- coûts ×2 : {rep['info_costs_x2']}", ""]
    md += table("Effet du risque par trade (vérification)", rep["info_risk"])
    (out / "robustness_premium.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
