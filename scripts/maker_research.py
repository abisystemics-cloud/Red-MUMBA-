"""Entrées en ordres postés (maker) : est-ce que ça rend les stratégies candidates viables ?

    python scripts/maker_research.py --from 2020-01 --to 2026-10 --split 2023-12

Aucun réglage de stratégie n'est modifié (paramètres gelés des tests précédents) :
- momentum 6 h (L = 28, long) sur BTC/ETH/SOL, puis sur 30 marchés ;
- cassure 96 h sur bougies 1 h, 30 marchés ;
- prime Coinbase 7 j sur BTC/ETH/SOL.
Seul le mode d'entrée change : taker / maker_skip / maker_taker (voir simulate()).
Modèle prudent : l'ordre posté au prix de clôture n'est exécuté que si la bougie suivante
TRAVERSE ce prix — on rate donc les départs en flèche (sélection adverse incluse).

Règle fixée À L'AVANCE, par stratégie : mode au meilleur Sharpe d'apprentissage ;
« TIENT » si en vérification Sharpe ≥ 0,8, PF ≥ 1,2, rendement > 0, DD < 25 %, et
rendement > 0 à coûts ×2.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.bar_research import BASE, H, Costs, _get, load_funding, load_klines, months, resample, simulate, summarize, tsmom  # noqa: E402
from scripts.filter_research import daily_flag_to_bars  # noqa: E402
from scripts.institution_research import follow, load_binance_spot_daily, load_coinbase_daily, positive_mean  # noqa: E402
from scripts.tsmom_robustness import ms, next_month  # noqa: E402
from scripts.universe_research import CORE, OTHERS, breakout  # noqa: E402

MODES = ("taker", "maker_skip", "maker_taker")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start", default="2020-01")
    p.add_argument("--to", dest="end", default="2026-10")
    p.add_argument("--split", default="2023-12")
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
    with ThreadPoolExecutor(16) as ex:
        list(ex.map(prefetch, [(k, f"{c}USDT", mo) for c in coins for mo in ml for k in ("k", "f")]))
    data = {}
    for c in coins:
        b1 = load_klines(f"{c}USDT", ml, cache, "1h")
        if len(b1) >= 2000:
            data[c] = {"1h": b1, "6h": resample(b1, 6 * H), "fund": load_funding(f"{c}USDT", ml, cache)}
    coins = [c for c in coins if c in data]
    core = [c for c in CORE if c in data]
    cb_t, cb_c = load_coinbase_daily(cache, "2019-06", a.end)
    bn_t, bn_c = load_binance_spot_daily(cache, months("2019-06", a.end))
    common = np.intersect1d(cb_t, bn_t)
    prem = cb_c[np.searchsorted(cb_t, common)] / bn_c[np.searchsorted(bn_t, common)] - 1 if len(common) else np.asarray([])
    train, test = (ms(a.start), ms(next_month(a.split))), (ms(next_month(a.split)), ms(next_month(a.end)))

    def premium(b):
        return follow(b, daily_flag_to_bars(b.ts + 6 * H, common, positive_mean(prem, 7), 1.01))
    cases = {
        "momentum 6h — BTC/ETH/SOL": ("6h", core, lambda b: tsmom(b, 28, True)),
        f"momentum 6h — {len(coins)} marchés": ("6h", coins, lambda b: tsmom(b, 28, True)),
        f"cassure 96h (1h) — {len(coins)} marchés": ("1h", coins, lambda b: breakout(b, 96)),
    }
    if len(common) > 500:
        cases["prime Coinbase 7j — BTC/ETH/SOL"] = ("6h", core, premium)

    def run(tf, universe, build, window, mode, costs=Costs()):
        per = {c: simulate(data[c][tf], build(data[c][tf]), costs, *data[c]["fund"],
                           start_ms=window[0], end_ms=window[1], entry_mode=mode) for c in universe}
        s = summarize(per)
        att = sum(r["maker_attempts"] for r in per.values())
        s["fill_rate"] = round(sum(r["maker_fills"] for r in per.values()) / att, 2) if att else None
        s["trades_per_month"] = round(s["trades"] / max((window[1] - window[0]) / (30.44 * 86_400_000), 1), 1)
        return s

    rep: dict = {"periods": {"train": [a.start, a.split], "test": [next_month(a.split), a.end]}, "cases": {}}
    for name, (tf, uni, build) in cases.items():
        rows = {m: {"train": run(tf, uni, build, train, m), "test": run(tf, uni, build, test, m)} for m in MODES}
        best = max(MODES, key=lambda m: rows[m]["train"]["sharpe"])
        stress = run(tf, uni, build, test, best, Costs(mult=2.0))
        t = rows[best]["test"]
        ok = (t["sharpe"] >= 0.8 and t["profit_factor"] >= 1.2 and t["return_pct"] > 0 and t["max_dd_pct"] < 25
              and stress["return_pct"] > 0)
        rep["cases"][name] = {"rows": rows, "choice": best, "stress": stress, "verdict": "TIENT" if ok else "NE TIENT PAS"}
        print(name, best, rep["cases"][name]["verdict"], flush=True)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "maker.json").write_text(json.dumps(rep, indent=2, default=str))
    cols = ["trades", "trades_per_month", "fill_rate", "return_pct", "max_dd_pct", "sharpe", "profit_factor", "win_rate"]
    md = ["# Entrées maker sur les stratégies candidates", "",
          f"Apprentissage {a.start} → {a.split} · vérification {next_month(a.split)} → {a.end}", "",
          "| stratégie | mode choisi (apprentissage) | verdict | vérif. Sharpe | coûts ×2 rendement % |", "|---|---|---|---|---|"]
    md += [f"| {k} | {v['choice']} | **{v['verdict']}** | {v['rows'][v['choice']]['test']['sharpe']} | {v['stress']['return_pct']} |"
           for k, v in rep["cases"].items()]
    md += ["", "| stratégie | mode | période | " + " | ".join(cols) + " |", "|---|---|---|" + "---|" * len(cols)]
    for k, v in rep["cases"].items():
        for m in MODES:
            for per in ("train", "test"):
                md.append(f"| {k} | {m} | {per} | " + " | ".join(str(v["rows"][m][per].get(c)) for c in cols) + " |")
    (out / "maker.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
