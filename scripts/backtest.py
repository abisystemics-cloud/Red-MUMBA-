"""Backtest de la configuration actuelle sur une période, avec rapport complet.

    python scripts/backtest.py --from 2026-09-01 --to 2026-10-31
    python scripts/backtest.py --from 2026-09-01 --to 2026-10-31 --mode taker --coins BTC

Lit en flux les fichiers md_*.jsonl.gz (enregistrements live + import historique),
rejoue la stratégie exacte du bot, puis écrit dans data/reports/ :
- backtest_<from>_<to>.json : résumé, résultats mois par mois et semaine par semaine,
  trades, couverture des signaux, verdict go/no-go ;
- backtest_<from>_<to>.md   : la même chose, lisible.

Verdict : mêmes seuils que `go_live` (trades, profit factor, drawdown), et la
régularité est exigée sur ≥ 60 % des semaines de la période.
Code retour : 0 = GO, 3 = NO-GO, 2 = pas assez de données.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.config import load_config  # noqa: E402
from ml_engine.backtester import run_backtest  # noqa: E402
from ml_engine.go_live import evaluate  # noqa: E402
from ml_engine.recorder import iter_events  # noqa: E402


def _ms(d: str, end: bool = False) -> int:
    x = date.fromisoformat(d)
    t = datetime(x.year, x.month, x.day, tzinfo=timezone.utc).timestamp() * 1000
    return int(t + (86_400_000 - 1 if end else 0))


class Coverage:
    """Compte les types d'événements rejoués (le rapport dit quels signaux étaient actifs)."""

    def __init__(self, it):
        self.it = it
        self.counts: dict[str, int] = defaultdict(int)

    def __iter__(self):
        for r in self.it:
            self.counts[r["t"]] += 1
            yield r


def run(cfg, start: str, end: str, coins, mode: str | None, rec_dir: str) -> dict:
    ex = cfg.execution.model_copy(update={"mode": mode}) if mode else cfg.execution
    cov = Coverage(iter_events(rec_dir, _ms(start), _ms(end, True), coins))
    t0 = time.time()
    res = run_backtest(cov, cfg.strategy, cfg.risk, exec_cfg=ex, equity=cfg.risk.paper_equity_usd,
                       max_staleness_ms=max(cfg.data.max_staleness_ms, 5000), curve_step_ms=60_000,
                       progress=lambda n: n and print(f"  … {n:,} events", flush=True))
    months: dict[str, dict] = defaultdict(lambda: {"trades": 0, "pnl": 0.0, "wins": 0})
    for t in res.trades:
        m = time.strftime("%Y-%m", time.gmtime(t.exit_ts / 1000))
        months[m]["trades"] += 1
        months[m]["pnl"] = round(months[m]["pnl"] + t.pnl, 2)
        months[m]["wins"] += int(t.pnl > 0)
    n_weeks = max(1, math.ceil((_ms(end, True) - _ms(start)) / (7 * 86_400_000)))
    gl = cfg.go_live.model_copy(update={"weeks": n_weeks, "min_positive_weeks": math.ceil(0.6 * n_weeks)})
    verdict = evaluate([(t.exit_ts, t.pnl) for t in res.trades], res.start_equity, gl)
    reasons = defaultdict(int)
    for t in res.trades:
        reasons[t.reason] += 1
    return {
        "period": {"from": start, "to": end, "coins": coins, "execution_mode": ex.mode},
        "runtime_s": round(time.time() - t0, 1),
        "events": dict(cov.counts),
        "signals_available": {
            "order_book": cov.counts.get("book", 0) > 0,
            "trades_cvd_poc": cov.counts.get("trade", 0) > 0,
            "cex_premium": cov.counts.get("ext", 0) > 0,
            "funding": cov.counts.get("ctx", 0) > 0,
            "positioning": cov.counts.get("whale", 0) > 0,
            "liquidations": cov.counts.get("liq", 0) > 0,
        },
        "summary": res.summary(),
        "fees_usd": round(sum(t.fees for t in res.trades), 2),
        "funding_usd": round(sum(t.funding for t in res.trades), 2),
        "exit_reasons": dict(reasons),
        "monthly": dict(sorted(months.items())),
        "weekly_pnl": verdict["weekly_pnl"],
        "go_no_go": {"verdict": verdict["verdict"], "criteria": verdict["criteria"]},
        "strategy": cfg.strategy.model_dump(),
        "trades": [t.__dict__ for t in res.trades[-500:]],
    }


def to_markdown(r: dict) -> str:
    s, g = r["summary"], r["go_no_go"]
    lines = [f"# Backtest {r['period']['from']} → {r['period']['to']} ({', '.join(r['period']['coins'])}, "
             f"mode {r['period']['execution_mode']})", "",
             f"**Verdict : {g['verdict']}**", "",
             "| Indicateur | Valeur |", "|---|---|"]
    for k, v in s.items():
        lines.append(f"| {k} | {v} |")
    lines += [f"| fees_usd | {r['fees_usd']} |", f"| funding_usd | {r['funding_usd']} |", "",
              "## Critères", "", "| Critère | Valeur | Cible | OK |", "|---|---|---|---|"]
    for k, c in g["criteria"].items():
        lines.append(f"| {k} | {c['value']} | {c['target']} | {'oui' if c['pass'] else 'non'} |")
    lines += ["", "## Mois par mois", "", "| Mois | Trades | PnL (USD) | Gagnants |", "|---|---|---|---|"]
    for m, v in r["monthly"].items():
        lines.append(f"| {m} | {v['trades']} | {v['pnl']} | {v['wins']} |")
    lines += ["", "## Signaux présents dans les données", ""]
    lines += [f"- {k} : {'oui' if v else 'NON (non testé)'}" for k, v in r["signals_available"].items()]
    lines += ["", f"Événements rejoués : {r['events']} — durée {r['runtime_s']} s"]
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start", required=True)
    p.add_argument("--to", dest="end", required=True)
    p.add_argument("--coins", default=None)
    p.add_argument("--mode", choices=("maker", "taker"), default=None)
    p.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config.yaml"))
    p.add_argument("--recordings", default="data/recordings")
    p.add_argument("--out", default="data/reports")
    a = p.parse_args()
    cfg = load_config(a.config)
    coins = a.coins.split(",") if a.coins else [m.coin for m in cfg.markets]
    r = run(cfg, a.start, a.end, coins, a.mode, a.recordings)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stem = f"backtest_{a.start}_{a.end}"
    (out / f"{stem}.json").write_text(json.dumps(r, indent=2, default=str))
    md = to_markdown(r)
    (out / f"{stem}.md").write_text(md)
    print(md)
    if not r["events"].get("book"):
        return 2
    return 0 if r["go_no_go"]["verdict"] == "GO" else 3


if __name__ == "__main__":
    sys.exit(main())
