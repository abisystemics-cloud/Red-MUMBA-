"""Modèles mathématiques « market-neutral » sur 30 marchés + test anti-chance.

    python scripts/quant_research.py --from 2020-01 --to 2026-10 --split 2023-12

Familles (portefeuilles long/short, exposition brute 1× le capital, nette ≈ 0) :
- xs_carry    : classement par funding moyen ; long les funding les plus bas, short
                les plus hauts (prime de portage en coupe transversale) ;
- xs_momentum : long les 20 % qui ont le plus monté sur L jours, short les 20 % du bas ;
- xs_reversal : l'inverse sur 1-3 jours (retour à la moyenne de court terme) ;
- combo       : mélange des rangs momentum + carry ;
- pairs_ou    : chaque alt contre BTC — écart log(alt) − β·log(BTC) modélisé comme un
                processus de retour à la moyenne (Ornstein-Uhlenbeck) : on prend l'écart
                à contre-sens quand son z-score dépasse k, sortie au retour à 0.
Décision à la clôture du jour J, rendement du jour J+1, frais taker + glissement sur
chaque changement de poids, funding payé/reçu.

Règle fixée À L'AVANCE, par famille : réglage au meilleur Sharpe d'apprentissage ;
« TIENT » si en vérification Sharpe ≥ 0,8, rendement > 0, DD < 25 %, rendement > 0 à
coûts ×2. En plus, pour chaque candidat : Sharpe « déflaté » (probabilité que le
résultat ne soit pas dû à la chance après ~150 essais dans tout le projet).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml_engine.stats import deflated_sharpe, moments, probabilistic_sharpe  # noqa: E402
from scripts.bar_research import BASE, H, Costs, _get, load_funding, load_klines, months, resample, simulate, tsmom  # noqa: E402
from scripts.filter_research import daily_flag_to_bars  # noqa: E402
from scripts.institution_research import follow, load_binance_spot_daily, load_coinbase_daily, positive_mean  # noqa: E402
from scripts.tsmom_robustness import ms, next_month, portfolio_daily  # noqa: E402
from scripts.universe_research import CORE, OTHERS  # noqa: E402

DAY = 24 * H
N_TRIALS_PROJECT = 150  # ordre de grandeur des réglages essayés depuis le début


def xs_weights(sig: np.ndarray, frac: float = 0.2, min_n: int = 10) -> np.ndarray:
    w = np.zeros(len(sig))
    ok = np.flatnonzero(np.isfinite(sig))
    if len(ok) < min_n:
        return w
    k = max(2, int(len(ok) * frac))
    order = ok[np.argsort(sig[ok], kind="stable")]
    w[order[-k:]] = 0.5 / k
    w[order[:k]] = -0.5 / k
    return w


def hold_weights(sig: np.ndarray, hold: int) -> np.ndarray:
    """sig[t] connu à la clôture du jour t → poids tenus `hold` jours."""
    W = np.zeros_like(sig)
    cur = np.zeros(sig.shape[1])
    for t in range(sig.shape[0]):
        if t % hold == 0:
            cur = xs_weights(sig[t])
        W[t] = cur
    return W


def rank01(x: np.ndarray) -> np.ndarray:
    out = np.full(x.shape, np.nan)
    for t in range(x.shape[0]):
        ok = np.flatnonzero(np.isfinite(x[t]))
        if len(ok) > 1:
            out[t, ok[np.argsort(x[t, ok], kind="stable")]] = np.linspace(0, 1, len(ok))
    return out


def pairs_weights(C: np.ndarray, b: int, k: float, win: int) -> np.ndarray:
    T, N = C.shape
    W = np.zeros((T, N))
    logc = np.log(C)
    alts = [j for j in range(N) if j != b]
    u = 1 / (2 * len(alts))
    for j in alts:
        pos, locked = 0, False
        for t in range(win, T):
            la, lb = logc[t - win + 1:t + 1, j], logc[t - win + 1:t + 1, b]
            if not (np.isfinite(la).all() and np.isfinite(lb).all()):
                pos = 0
                continue
            vb = lb.var()
            if vb <= 0:
                continue
            beta = float(np.cov(la, lb, bias=True)[0, 1] / vb)
            s = la - beta * lb
            sd = s.std()
            if sd <= 0:
                continue
            z = (s[-1] - s.mean()) / sd
            if pos == 0:
                if abs(z) < k:
                    locked = False
                elif not locked and abs(z) < k + 2:
                    pos = -1 if z > 0 else 1
            elif z * pos >= 0:
                pos = 0
            elif abs(z) > k + 2:  # l'écart s'emballe : la relation a cassé, on coupe
                pos, locked = 0, True
            W[t, j] += pos * u
            W[t, b] -= pos * beta * u
    return W


def backtest(W: np.ndarray, R: np.ndarray, F: np.ndarray, cost: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """→ (pnl[t] gagné le jour t avec les poids de t−1, turnover[t], nb de changements[t])."""
    r = np.nan_to_num(R) - np.nan_to_num(F)
    dW = np.abs(np.diff(W, axis=0, prepend=np.zeros((1, W.shape[1]))))
    pnl = np.zeros(W.shape[0])
    pnl[1:] = (W[:-1] * r[1:]).sum(axis=1) - cost * dW[:-1].sum(axis=1)
    return pnl, dW.sum(axis=1), (dW > 1e-9).sum(axis=1)


def stats(pnl: np.ndarray, turn: np.ndarray, chg: np.ndarray) -> dict:
    if len(pnl) < 30:
        return {"sharpe": 0.0, "return_pct": 0.0, "max_dd_pct": 0.0, "orders_per_month": 0.0}
    eq = np.cumprod(1 + pnl)
    dd = 1 - eq / np.maximum.accumulate(eq)
    sd = pnl.std(ddof=1)
    yrs = len(pnl) / 365
    return {"sharpe": round(float(pnl.mean() / sd * math.sqrt(365)), 2) if sd > 0 else 0.0,
            "return_pct": round(float(eq[-1] - 1) * 100, 1),
            "cagr_pct": round(float(eq[-1] ** (1 / yrs) - 1) * 100, 1) if eq[-1] > 0 else None,
            "max_dd_pct": round(float(dd.max()) * 100, 1),
            "orders_per_month": round(float(chg.sum() / (len(pnl) / 30.44)), 0),
            "turnover_per_month": round(float(turn.sum() / (len(pnl) / 30.44)), 1)}


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
    raw = {}
    for c in coins:
        b1 = load_klines(f"{c}USDT", ml, cache, "1h")
        if len(b1) >= 2000:
            raw[c] = {"1h": b1, "6h": resample(b1, 6 * H), "fund": load_funding(f"{c}USDT", ml, cache)}
    coins = [c for c in coins if c in raw]
    t0, t1 = ms(a.start), ms(next_month(a.end))
    days = np.arange(t0, t1, DAY)
    T, N = len(days), len(coins)
    C, F = np.full((T, N), np.nan), np.zeros((T, N))
    for j, c in enumerate(coins):
        d = resample(raw[c]["1h"], DAY)
        idx = ((d.ts - t0) // DAY).astype(int)
        ok = (idx >= 0) & (idx < T)
        C[idx[ok], j] = d.c[ok]
        ft, fr = raw[c]["fund"]
        fi = ((ft - t0) // DAY).astype(int)
        okf = (fi >= 0) & (fi < T)
        np.add.at(F[:, j], fi[okf], fr[okf])
    R = np.full((T, N), np.nan)
    R[1:] = C[1:] / C[:-1] - 1
    b = coins.index("BTC")

    def mom(L):
        out = np.full((T, N), np.nan)
        out[L:] = C[L:] / C[:-L] - 1
        return out

    def carry(n):
        out = np.full((T, N), np.nan)
        c = np.cumsum(np.vstack([np.zeros((1, N)), F]), axis=0)
        out[n - 1:] = -(c[n:] - c[:-n]) / n
        out[~np.isfinite(C)] = np.nan
        return out
    grids = {
        "xs_carry": [({"funding_days": n, "hold_days": h}, (lambda n=n, h=h: hold_weights(carry(n), h)))
                     for n in (3, 7, 14) for h in (1, 7)],
        "xs_momentum": [({"lookback_days": L, "hold_days": h}, (lambda L=L, h=h: hold_weights(mom(L), h)))
                        for L in (7, 14, 28) for h in (1, 7)],
        "xs_reversal": [({"lookback_days": L}, (lambda L=L: hold_weights(-mom(L), 1))) for L in (1, 3)],
        "combo_mom_carry": [({"mom_weight": w, "hold_days": h},
                             (lambda w=w, h=h: hold_weights(w * rank01(mom(14)) + (1 - w) * rank01(carry(7)), h)))
                            for w in (0.5, 0.7) for h in (1, 7)],
        "pairs_ou": [({"z_entry": k, "window_days": w}, (lambda k=k, w=w: pairs_weights(C, b, k, w)))
                     for k in (1.5, 2.0) for w in (30, 60)],
    }
    split = ms(next_month(a.split))
    tr, te = days < split, days >= split
    base_cost, cost2 = Costs().side, Costs(mult=2.0).side
    rep: dict = {"universe": coins, "families": {}, "periods": {"train": [a.start, a.split], "test": [next_month(a.split), a.end]}}
    val_sharpes, chosen_series = [], {}
    for fam, grid in grids.items():
        rows = []
        for prm, fn in grid:
            W = fn()
            pnl, turn, chg = backtest(W, R, F, base_cost)
            pnl2, _, _ = backtest(W, R, F, cost2)
            rows.append({"params": prm, "train": stats(pnl[tr], turn[tr], chg[tr]), "test": stats(pnl[te], turn[te], chg[te]),
                         "test_cost_x2": stats(pnl2[te], turn[te], chg[te]), "_pnl": pnl[te]})
            val_sharpes.append(moments(pnl[te])[0])
            print(fam, prm, rows[-1]["train"]["sharpe"], rows[-1]["test"]["sharpe"], flush=True)
        ch = max(rows, key=lambda r: r["train"]["sharpe"])
        t = ch["test"]
        ok = t["sharpe"] >= 0.8 and t["return_pct"] > 0 and t["max_dd_pct"] < 25 and ch["test_cost_x2"]["return_pct"] > 0
        chosen_series[fam] = ch["_pnl"]
        rep["families"][fam] = {"rows": [{k: v for k, v in r.items() if k != "_pnl"} for r in rows],
                                "choice": ch["params"], "verdict": "TIENT" if ok else "NE TIENT PAS"}

    # candidats déjà retenus : momentum 6 h et prime Coinbase (BTC/ETH/SOL), séries journalières de vérification
    test_w = (split, t1)
    per = {c: simulate(raw[c]["6h"], tsmom(raw[c]["6h"], 28, True), Costs(), *raw[c]["fund"],
                       start_ms=test_w[0], end_ms=test_w[1]) for c in CORE if c in raw}
    d = portfolio_daily(per)
    chosen_series["momentum_6h (déjà retenu)"] = np.asarray([d[k] for k in sorted(d)])
    cb_t, cb_c = load_coinbase_daily(cache, "2019-06", a.end)
    bn_t, bn_c = load_binance_spot_daily(cache, months("2019-06", a.end))
    common = np.intersect1d(cb_t, bn_t)
    if len(common) > 500:
        prem = cb_c[np.searchsorted(cb_t, common)] / bn_c[np.searchsorted(bn_t, common)] - 1
        per = {}
        for c in CORE:
            if c in raw:
                bb = raw[c]["6h"]
                flag = daily_flag_to_bars(bb.ts + 6 * H, common, positive_mean(prem, 7), 1.01)
                per[c] = simulate(bb, follow(bb, flag), Costs(), *raw[c]["fund"], start_ms=test_w[0], end_ms=test_w[1])
        d = portfolio_daily(per)
        chosen_series["prime_coinbase (déjà retenu)"] = np.asarray([d[k] for k in sorted(d)])

    var_trials = float(np.var(val_sharpes)) if len(val_sharpes) > 1 else 0.0
    rep["luck_test"] = {"n_trials": N_TRIALS_PROJECT, "var_trial_sharpes_daily": var_trials, "strategies": {}}
    for name, r in chosen_series.items():
        sr = moments(r)[0]
        rep["luck_test"]["strategies"][name] = {
            "sharpe_annualized": round(sr * math.sqrt(365), 2),
            "prob_true_sharpe_positive": round(probabilistic_sharpe(r), 3),
            "prob_not_luck_after_trials": round(deflated_sharpe(r, N_TRIALS_PROJECT, var_trials), 3)}

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "quant.json").write_text(json.dumps(rep, indent=2, default=str))
    cols = ["sharpe", "return_pct", "cagr_pct", "max_dd_pct", "orders_per_month", "turnover_per_month"]
    md = [f"# Modèles market-neutral sur {N} marchés + test anti-chance", "",
          f"Apprentissage {a.start} → {a.split} · vérification {next_month(a.split)} → {a.end} · exposition brute 1×", "",
          "| famille | réglage choisi | verdict |", "|---|---|---|"]
    md += [f"| {k} | {v['choice']} | **{v['verdict']}** |" for k, v in rep["families"].items()]
    md += ["", "## Test anti-chance (vérification)", "",
           "| stratégie | Sharpe | P(vrai Sharpe > 0) | P(pas dû à la chance après ~150 essais) |", "|---|---|---|---|"]
    md += [f"| {k} | {v['sharpe_annualized']} | {v['prob_true_sharpe_positive']} | {v['prob_not_luck_after_trials']} |"
           for k, v in rep["luck_test"]["strategies"].items()]
    md += ["", "## Détail", "", "| réglage | période | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
    for k, v in rep["families"].items():
        for r in v["rows"]:
            for per_ in ("train", "test", "test_cost_x2"):
                md.append(f"| {k} {r['params']} | {per_} | " + " | ".join(str(r[per_].get(c)) for c in cols) + " |")
    (out / "quant.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
