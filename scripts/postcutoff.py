"""Test « propre » : uniquement des données postérieures à la date de fin de connaissance
de l'assistant qui a conçu les stratégies (fin juin 2026).

    python scripts/postcutoff.py --from 2020-01 --to 2026-10 --clean-from 2026-07

Tous les réglages sont GELÉS tels qu'ils ont été choisis auparavant ; rien n'est ajusté
ici. La période est courte (4 mois) : elle ne peut pas prouver un avantage, seulement
montrer si une stratégie s'effondre sur des données que personne n'avait vues.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.bar_research import H, Costs, months, simulate, tsmom  # noqa: E402
from scripts.filter_research import daily_flag_to_bars  # noqa: E402
from scripts.institution_research import follow, load_binance_spot_daily, load_coinbase_daily, positive_mean  # noqa: E402
from scripts.ml_research import make_features, make_target, walk_forward_scores, year_of  # noqa: E402
from scripts.quant_research import backtest, build_panel, carry_signal, hold_weights, mom_signal, rank01  # noqa: E402
from scripts.tsmom_robustness import ms, next_month, portfolio_daily  # noqa: E402
from scripts.universe_research import CORE  # noqa: E402


def summarize(pnl: np.ndarray, days: np.ndarray) -> dict:
    eq = np.cumprod(1 + pnl)
    sd = pnl.std(ddof=1) if len(pnl) > 1 else 0.0
    mo = {}
    for d, r in zip(days, pnl, strict=True):
        k = str(np.datetime64(int(d), "ms").astype("datetime64[M]"))
        mo[k] = mo.get(k, 1.0) * (1 + r)
    return {"days": len(pnl), "return_pct": round(float(eq[-1] - 1) * 100, 2),
            "max_dd_pct": round(float((1 - eq / np.maximum.accumulate(eq)).max()) * 100, 2),
            "sharpe": round(float(pnl.mean() / sd * math.sqrt(365)), 2) if sd > 0 else 0.0,
            "t_stat": round(float(pnl.mean() / sd * math.sqrt(len(pnl))), 2) if sd > 0 else 0.0,
            "months": {k: round((v - 1) * 100, 2) for k, v in mo.items()}}


def main() -> int:
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import Ridge

    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start", default="2020-01")
    p.add_argument("--to", dest="end", default="2026-10")
    p.add_argument("--clean-from", default="2026-07")
    p.add_argument("--split", default=None, help="ignoré")
    p.add_argument("--cache", default="data/bars")
    p.add_argument("--out", default="data/reports")
    a = p.parse_args()
    cache = Path(a.cache)
    coins, raw, days, C, F, R, b = build_panel(cache, a.start, a.end)
    T, N = C.shape
    c0, c1 = ms(a.clean_from), ms(next_month(a.end))
    clean = days >= c0
    cost = Costs().side
    mom14, car7 = mom_signal(C, 14), carry_signal(C, F, 7)
    blend = 0.5 * rank01(mom14) + 0.5 * rank01(car7)
    res = {}

    def add(name, W):
        res[name] = summarize(backtest(W, R, F, cost)[0][clean], days[clean])
    add("mélange momentum + funding (30 marchés, hebdo)", hold_weights(blend, 7))
    add("portage du funding (3 j / hebdo)", hold_weights(carry_signal(C, F, 3), 7))
    add("petit compte 2+2", hold_weights(blend, 7, k_fixed=2))
    add("petit compte 3+3", hold_weights(blend, 7, k_fixed=3))
    add("momentum relatif seul (28 j)", hold_weights(mom_signal(C, 28), 1))
    X, y, years = make_features(C, F, R, b), make_target(C, F, R), year_of(days)
    yr = int(a.end[:4])
    for name, mk in (("ML ridge", lambda: Ridge(alpha=10.0)),
                     ("ML gradient boosting", lambda: HistGradientBoostingRegressor(
                         max_depth=3, learning_rate=0.05, max_iter=200, min_samples_leaf=50, l2_regularization=1.0, random_state=0))):
        sc, _ = walk_forward_scores(X, y, years, yr, yr, mk)
        add(name, hold_weights(sc, 7))

    def from_sim(per):
        d = portfolio_daily(per)
        ks = sorted(d)
        return summarize(np.asarray([d[k] for k in ks]), np.asarray(ks, dtype=float) * 86_400_000)
    core = [c for c in CORE if c in raw]
    res["momentum 7 j (BTC/ETH/SOL)"] = from_sim({c: simulate(raw[c]["6h"], tsmom(raw[c]["6h"], 28, True), Costs(),
                                                              *raw[c]["fund"], start_ms=c0, end_ms=c1) for c in core})
    cb_t, cb_c = load_coinbase_daily(cache, "2019-06", a.end)
    bn_t, bn_c = load_binance_spot_daily(cache, months("2019-06", a.end))
    common = np.intersect1d(cb_t, bn_t)
    if len(common) > 500:
        prem = cb_c[np.searchsorted(cb_t, common)] / bn_c[np.searchsorted(bn_t, common)] - 1
        per = {}
        for c in core:
            bb = raw[c]["6h"]
            per[c] = simulate(bb, follow(bb, daily_flag_to_bars(bb.ts + 6 * H, common, positive_mean(prem, 7), 1.01)),
                              Costs(), *raw[c]["fund"], start_ms=c0, end_ms=c1)
        res["prime Coinbase (BTC/ETH/SOL)"] = from_sim(per)
    mk = np.nanmean(np.nan_to_num(R[clean]), axis=1)
    res["acheter et garder les 30 marchés (repère)"] = summarize(mk, days[clean])

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "postcutoff.json").write_text(json.dumps(res, indent=2))
    mos = sorted({m for v in res.values() for m in v["months"]})
    md = [f"# Test propre : {a.clean_from} → {a.end} (données jamais vues)", "",
          "| stratégie | rendement % | pire baisse % | Sharpe | t-stat | " + " | ".join(mos) + " |",
          "|---|---|---|---|---|" + "---|" * len(mos)]
    md += [f"| {k} | {v['return_pct']} | {v['max_dd_pct']} | {v['sharpe']} | {v['t_stat']} | "
           + " | ".join(str(v["months"].get(m, "")) for m in mos) + " |" for k, v in res.items()]
    (out / "postcutoff.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
