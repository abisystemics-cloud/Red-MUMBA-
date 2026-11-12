"""Diagnostic des signaux + test de sensibilité du seuil, avec période de vérification.

    python scripts/sweep.py --from 2026-09-01 --split 2026-10-15 --to 2026-11-11

1. Diagnostic (toute la période) : distribution du score composite et de la
   contribution de chaque signal, part du temps où |score| dépasse chaque seuil.
2. Grille (seuil d'entrée × persistance) backtestée sur la période d'APPRENTISSAGE
   seulement (from → split). Le meilleur réglage est choisi selon une règle fixée
   à l'avance : Sharpe maximal parmi ceux qui ont ≥ --min-trades trades et un
   drawdown < 10 %.
3. Ce réglage, et lui seul, est rejoué sur la période de VÉRIFICATION (split → to),
   jamais vue pendant le choix. Les autres réglages sont aussi rejoués pour
   transparence, mais ne servent pas à décider.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.config import load_config  # noqa: E402
from core.events import AssetCtx, BookSnapshot, ExternalQuote, LiquidationMap, Trade, WhaleBias  # noqa: E402
from ml_engine.features import FeatureEngine  # noqa: E402
from ml_engine.recorder import iter_events, to_event  # noqa: E402
from scripts.backtest import _ms, run as run_period  # noqa: E402

TERMS = ("obi", "cvd", "premium", "poc", "funding", "liq", "whale")


def contributions(f, cfg) -> dict:
    """Même décomposition que ml_engine.strategy.composite_score, terme par terme."""
    w = cfg.weights
    obi = f.obi_z * (1 - f.spoof_bid) if f.obi_z > 0 else f.obi_z * (1 - f.spoof_ask)
    poc = -max(-3.0, min(3.0, f.poc_dist_bps / 20.0)) if math.isfinite(f.poc_dist_bps) else 0.0
    liq = 0.0
    if math.isfinite(f.liq_magnet_bps) and abs(f.liq_magnet_bps) <= cfg.liq_max_dist_bps:
        liq = max(-3.0, min(3.0, f.liq_magnet_bps / 50.0))
    return {"obi": w.obi * obi, "cvd": w.cvd * f.cvd_slope_z, "premium": w.premium * -f.premium_z,
            "poc": w.poc * poc, "funding": w.funding * -max(-3.0, min(3.0, f.funding_z)),
            "liq": w.liq * liq, "whale": w.whale * 3.0 * max(-1.0, min(1.0, f.whale_bias))}


def diagnose(cfg, rec_dir: str, start: str, end: str, coins: list[str], max_samples: int = 400_000) -> dict:
    engines = {c: FeatureEngine(c, cfg.strategy, 5000) for c in coins}
    samples: dict[str, list[list[float]]] = {c: [] for c in coins}
    for rec in iter_events(rec_dir, _ms(start), _ms(end, True), coins):
        ev = to_event(rec)
        if ev is None:
            continue
        e = engines[ev.coin]
        if isinstance(ev, Trade):
            e.on_trade(ev)
        elif isinstance(ev, ExternalQuote):
            e.on_ext(ev)
        elif isinstance(ev, AssetCtx):
            e.on_ctx(ev)
        elif isinstance(ev, WhaleBias):
            e.on_whale(ev)
        elif isinstance(ev, LiquidationMap):
            e.on_liq(ev)
        elif isinstance(ev, BookSnapshot) and len(ev.bids) and len(ev.asks):
            f = e.on_book(ev, now_ms=ev.exch_ts)
            if len(samples[ev.coin]) < max_samples:
                c = contributions(f, cfg.strategy)
                samples[ev.coin].append([c[t] for t in TERMS])
    out = {}
    for coin, rows in samples.items():
        if not rows:
            continue
        a = np.array(rows)
        score = a.sum(axis=1)
        out[coin] = {
            "n": len(rows),
            "score_quantiles": {q: round(float(np.quantile(score, q / 100)), 3) for q in (1, 5, 25, 50, 75, 95, 99)},
            "score_std": round(float(score.std()), 3),
            "share_abs_score_above": {t: round(float((np.abs(score) >= t).mean() * 100), 3)
                                      for t in (0.4, 0.6, 0.8, 1.0, 1.2, 1.4)},
            "term_std": {t: round(float(a[:, i].std()), 3) for i, t in enumerate(TERMS)},
            "term_active_pct": {t: round(float((np.abs(a[:, i]) > 1e-9).mean() * 100), 1) for i, t in enumerate(TERMS)},
        }
    return out


def _job(args):
    cfg_dict, start, end, coins, rec_dir, entry, persist = args
    from core.config import AppConfig
    cfg = AppConfig.model_validate(cfg_dict)
    cfg = cfg.model_copy(update={"strategy": cfg.strategy.model_copy(
        update={"entry_threshold": entry, "persistence_ticks": persist})})
    r = run_period(cfg, start, end, coins, None, rec_dir)
    return {"entry": entry, "persistence": persist, "period": f"{start}→{end}", **r["summary"],
            "fees_usd": r["fees_usd"], "funding_usd": r["funding_usd"]}


def pick(rows: list[dict], min_trades: int, max_dd: float) -> dict | None:
    ok = [r for r in rows if r["trades"] >= min_trades and r["max_dd_pct"] < max_dd]
    return max(ok, key=lambda r: r["sharpe"]) if ok else None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start", required=True)
    p.add_argument("--split", required=True, help="dernier jour de la période d'apprentissage")
    p.add_argument("--to", dest="end", required=True)
    p.add_argument("--coins", default=None)
    p.add_argument("--entries", default="0.6,0.8,1.0,1.2")
    p.add_argument("--persistences", default="2,6")
    p.add_argument("--min-trades", type=int, default=30)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config.yaml"))
    p.add_argument("--recordings", default="data/recordings")
    p.add_argument("--out", default="data/reports")
    a = p.parse_args()
    cfg = load_config(a.config)
    coins = a.coins.split(",") if a.coins else [m.coin for m in cfg.markets]
    test_start = (date.fromisoformat(a.split) + timedelta(days=1)).isoformat()
    t0 = time.time()

    diag = diagnose(cfg, a.recordings, a.start, a.end, coins)
    print("diagnostic done", round(time.time() - t0), "s", flush=True)

    grid = [(float(e), int(k)) for e in a.entries.split(",") for k in a.persistences.split(",")]
    base = cfg.model_dump()
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        train = list(ex.map(_job, [(base, a.start, a.split, coins, a.recordings, e, k) for e, k in grid]))
        print("train done", round(time.time() - t0), "s", flush=True)
        test = list(ex.map(_job, [(base, test_start, a.end, coins, a.recordings, e, k) for e, k in grid]))
    choice = pick(train, a.min_trades, cfg.research.max_drawdown_pct)
    chosen_test = None
    if choice:
        chosen_test = next(r for r in test if r["entry"] == choice["entry"] and r["persistence"] == choice["persistence"])
    verdict = "pas de réglage éligible sur l'apprentissage"
    if chosen_test:
        holds = (chosen_test["return_pct"] > 0 and chosen_test["sharpe"] > 0
                 and chosen_test["max_dd_pct"] < cfg.research.max_drawdown_pct
                 and chosen_test["trades"] >= max(10, a.min_trades // 3))
        verdict = "TIENT sur la période de vérification" if holds else "NE TIENT PAS sur la période de vérification"
    rep = {"periods": {"train": [a.start, a.split], "test": [test_start, a.end]}, "coins": coins,
           "rule": f"Sharpe max parmi trades ≥ {a.min_trades} et drawdown < {cfg.research.max_drawdown_pct} % (apprentissage)",
           "diagnostic": diag, "train": train, "test": test, "choice": choice, "choice_on_test": chosen_test,
           "verdict": verdict, "runtime_s": round(time.time() - t0)}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"sweep_{a.start}_{a.end}"
    (out / f"{stem}.json").write_text(json.dumps(rep, indent=2, default=str))
    md = [f"# Diagnostic et sensibilité {a.start} → {a.end}", "", f"**Verdict : {verdict}**", "",
          f"Apprentissage {a.start} → {a.split} · vérification {test_start} → {a.end} · règle : {rep['rule']}", "",
          "## Diagnostic des signaux", ""]
    for coin, d in diag.items():
        md += [f"### {coin} ({d['n']:,} instantanés)", "", f"- écart-type du score : {d['score_std']}",
               f"- quantiles du score : {d['score_quantiles']}",
               f"- % du temps où |score| ≥ seuil : {d['share_abs_score_above']}",
               f"- écart-type de la contribution de chaque signal : {d['term_std']}",
               f"- % du temps où chaque signal est actif : {d['term_active_pct']}", ""]
    cols = ["entry", "persistence", "trades", "return_pct", "max_dd_pct", "sharpe", "win_rate", "profit_factor",
            "maker_fill_rate", "fees_usd"]
    for name, rows in (("Apprentissage", train), ("Vérification (information seulement)", test)):
        md += [f"## {name}", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        md += ["| " + " | ".join(str(r.get(c)) for c in cols) + " |" for r in rows] + [""]
    md += ["## Réglage choisi", "", f"- sur l'apprentissage : {choice}", f"- sur la vérification : {chosen_test}"]
    (out / f"{stem}.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
