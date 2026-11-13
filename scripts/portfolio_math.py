"""Couche mathématique sur la stratégie retenue (momentum + funding, long/short).

    python scripts/portfolio_math.py --from 2020-01 --to 2026-10 --split 2023-12

Pas de nouveaux signaux : on améliore la CONSTRUCTION du portefeuille, le RISQUE et la
VALIDATION statistique, chaque brique testée seule contre la référence.

Briques (une formule chacune) :
- inv_vol      : poids ∝ 1/σ_i (σ = écart-type 30 j) → chaque position porte le même risque ;
- beta_neutral : jambes long/short redimensionnées pour que Σ w_i·β_i ≈ 0 (β vs BTC, 60 j) ;
- vol_target   : exposition s_t = min(2, σ_cible / σ_t), σ_t = volatilité réalisée 30 j du
                 portefeuille ; σ_cible = médiane d'apprentissage (pas de paramètre libre) ;
- ewma_carry   : funding lissé par moyenne exponentielle (demi-vie 10 j) ;
- buffer       : hystérésis — on entre dans le top 20 %, on ne sort qu'au-delà de 35 %.
Règle fixée À L'AVANCE : une brique est ADOPTÉE si elle améliore le Sharpe
d'apprentissage ET, en vérification, soit le Sharpe d'au moins 0,10, soit la pire baisse
d'au moins 20 % (relatif) sans perdre plus de 0,05 de Sharpe.

Validation :
- intervalle de confiance du Sharpe par bootstrap stationnaire ;
- walk-forward : chaque année, le réglage est re-choisi avec les seules données passées ;
- Sharpe déflaté (chance après ~170 essais) ; levier de Kelly f* = μ/σ² ;
- petit compte : probabilité de perte et de baisse ≥ 50 % sur 5 mois ;
- durée nécessaire pour confirmer la stratégie en réel.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml_engine.stats import (deflated_sharpe, kelly_leverage, moments, probabilistic_sharpe, ruin_stats,  # noqa: E402
                             sharpe_ci, years_to_confirm)
from scripts.bar_research import Costs  # noqa: E402
from scripts.quant_research import (backtest, build_panel, carry_signal, hold_weights, mom_signal, rank01,  # noqa: E402
                                    stats, xs_weights)
from scripts.tsmom_robustness import ms, next_month  # noqa: E402

N_TRIALS_PROJECT = 170


def rolling_std(R: np.ndarray, n: int) -> np.ndarray:
    out = np.full(R.shape, np.nan)
    X = np.nan_to_num(R)
    c1 = np.cumsum(np.vstack([np.zeros((1, R.shape[1])), X]), axis=0)
    c2 = np.cumsum(np.vstack([np.zeros((1, R.shape[1])), X * X]), axis=0)
    m = (c1[n:] - c1[:-n]) / n
    out[n - 1:] = np.sqrt(np.maximum((c2[n:] - c2[:-n]) / n - m * m, 0))
    out[~np.isfinite(R)] = np.nan
    return out


def rolling_beta(R: np.ndarray, b: int, n: int) -> np.ndarray:
    X = np.nan_to_num(R)
    xb = X[:, [b]]

    def rsum(A):
        c = np.cumsum(np.vstack([np.zeros((1, A.shape[1])), A]), axis=0)
        out = np.full(A.shape, np.nan)
        out[n - 1:] = c[n:] - c[:-n]
        return out
    sxy, sx, sy, syy = rsum(X * xb), rsum(X), rsum(xb), rsum(xb * xb)
    cov = sxy / n - sx / n * sy / n
    var = syy / n - (sy / n) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        beta = cov / var
    beta[~np.isfinite(beta)] = 1.0
    return beta


def inv_vol(W: np.ndarray, vol: np.ndarray) -> np.ndarray:
    out = np.zeros_like(W)
    for t in range(W.shape[0]):
        for sign in (1, -1):
            m = (W[t] * sign > 0) & np.isfinite(vol[t]) & (vol[t] > 0)
            if m.any():
                x = 1 / vol[t, m]
                out[t, m] = sign * 0.5 * x / x.sum()
    return out


def beta_neutral(W: np.ndarray, beta: np.ndarray) -> np.ndarray:
    out = W.copy()
    for t in range(W.shape[0]):
        lo, sh = W[t] > 0, W[t] < 0
        if not (lo.any() and sh.any()):
            continue
        bl, bs = float((W[t, lo] * beta[t, lo]).sum()), float((-W[t, sh] * beta[t, sh]).sum())
        if bl <= 0 or bs <= 0:
            continue
        a = float(np.clip(2 * bs / (bl + bs), 0.5, 1.5))
        out[t, lo] *= a
        out[t, sh] *= 2 - a
    return out


def buffered_weights(sig: np.ndarray, hold: int, enter: float = 0.2, exit_: float = 0.35) -> np.ndarray:
    T, N = sig.shape
    W = np.zeros((T, N))
    longs: set[int] = set()
    shorts: set[int] = set()
    cur = np.zeros(N)
    for t in range(T):
        if t % hold == 0:
            ok = np.flatnonzero(np.isfinite(sig[t]))
            if len(ok) < 10:
                longs, shorts, cur = set(), set(), np.zeros(N)
            else:
                order = ok[np.argsort(sig[t, ok], kind="stable")]
                n = len(order)
                k, kx = max(2, int(n * enter)), max(3, int(n * exit_))
                top, bot = set(order[-k:].tolist()), set(order[:k].tolist())
                keep_top, keep_bot = set(order[-kx:].tolist()), set(order[:kx].tolist())
                longs = {j for j in longs if j in keep_top}
                shorts = {j for j in shorts if j in keep_bot}
                for j in reversed(order[-k:].tolist()):
                    if len(longs) < k and j in top:
                        longs.add(j)
                for j in order[:k].tolist():
                    if len(shorts) < k and j in bot:
                        shorts.add(j)
                cur = np.zeros(N)
                if longs and shorts:
                    cur[list(longs)] = 0.5 / len(longs)
                    cur[list(shorts)] = -0.5 / len(shorts)
        W[t] = cur
    return W


def ewma(F: np.ndarray, halflife: float) -> np.ndarray:
    a = 1 - 0.5 ** (1 / halflife)
    out = np.zeros_like(F)
    acc = np.zeros(F.shape[1])
    for t in range(F.shape[0]):
        acc = (1 - a) * acc + a * F[t]
        out[t] = acc
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start", default="2020-01")
    p.add_argument("--to", dest="end", default="2026-10")
    p.add_argument("--split", default="2023-12")
    p.add_argument("--cache", default="data/bars")
    p.add_argument("--out", default="data/reports")
    a = p.parse_args()
    coins, _raw, days, C, F, R, b = build_panel(Path(a.cache), a.start, a.end)
    T, N = C.shape
    split = ms(next_month(a.split))
    tr, te = days < split, days >= split
    cost, cost2 = Costs().side, Costs(mult=2.0).side
    mom14, car7 = mom_signal(C, 14), carry_signal(C, F, 7)
    blend = 0.5 * rank01(mom14) + 0.5 * rank01(car7)
    vol30, beta60 = rolling_std(R, 30), rolling_beta(R, b, 60)

    def ev(W):
        pnl, turn, chg = backtest(W, R, F, cost)
        pnl2, _, _ = backtest(W, R, F, cost2)
        return {"train": stats(pnl[tr], turn[tr], chg[tr]), "test": stats(pnl[te], turn[te], chg[te]),
                "test_cost_x2": stats(pnl2[te], turn[te], chg[te]), "_pnl": pnl, "_W": W}

    def vol_target(W):
        pnl, _, _ = backtest(W, R, F, cost)
        v = np.full(T, np.nan)
        for t in range(30, T):
            v[t] = pnl[t - 29:t + 1].std()
        target = float(np.nanmedian(v[tr]))
        s = np.where(np.isfinite(v) & (v > 0), np.minimum(2.0, target / v), 1.0)
        return W * s[:, None]

    W0 = hold_weights(blend, 7)
    car_ewma = -ewma(F, 10.0)
    car_ewma[~np.isfinite(C)] = np.nan
    bricks = {
        "inv_vol": lambda W: inv_vol(W, vol30),
        "beta_neutral": lambda W: beta_neutral(W, beta60),
        "vol_target": vol_target,
        "ewma_carry": lambda W: hold_weights(0.5 * rank01(mom14) + 0.5 * rank01(car_ewma), 7),
        "buffer": lambda W: buffered_weights(blend, 7),
    }
    base = ev(W0)
    rep: dict = {"baseline": {k: v for k, v in base.items() if not k.startswith("_")}, "bricks": {}}
    adopted = []
    for name, fn in bricks.items():
        r = ev(fn(W0))
        bt, rt = base["test"], r["test"]
        better_train = r["train"]["sharpe"] > base["train"]["sharpe"]
        helps = (rt["sharpe"] >= bt["sharpe"] + 0.10) or (rt["max_dd_pct"] <= 0.8 * bt["max_dd_pct"]
                                                         and rt["sharpe"] >= bt["sharpe"] - 0.05)
        ok = bool(better_train and helps)
        if ok:
            adopted.append(name)
        rep["bricks"][name] = {**{k: v for k, v in r.items() if not k.startswith("_")},
                               "improves_train": bool(better_train), "verdict": "ADOPTÉE" if ok else "ÉCARTÉE"}
        print(name, rep["bricks"][name]["verdict"], r["train"]["sharpe"], rt["sharpe"], rt["max_dd_pct"], flush=True)

    # combinaison des briques adoptées (ordre fixe : signal → sélection → poids → neutralité → exposition)
    sig = 0.5 * rank01(mom14) + 0.5 * rank01(car_ewma) if "ewma_carry" in adopted else blend
    W = buffered_weights(sig, 7) if "buffer" in adopted else hold_weights(sig, 7)
    if "inv_vol" in adopted:
        W = inv_vol(W, vol30)
    if "beta_neutral" in adopted:
        W = beta_neutral(W, beta60)
    if "vol_target" in adopted:
        W = vol_target(W)
    final = ev(W)
    rep["final"] = {"adopted": adopted, **{k: v for k, v in final.items() if not k.startswith("_")}}

    # ---------------------------------------------------------- validation
    val = {}
    for label, r in (("référence", base), ("version finale", final)):
        x = r["_pnl"][te]
        lo, hi = sharpe_ci(x)
        val[label] = {"sharpe": r["test"]["sharpe"], "sharpe_ci95": [round(lo, 2), round(hi, 2)],
                      "prob_true_sharpe_positive": round(probabilistic_sharpe(x), 3)}
    # walk-forward : chaque année, meilleur réglage sur le passé uniquement
    cands = {}
    for n in (3, 7, 14):
        for h in (1, 7):
            cands[f"carry {n}j/{h}j"] = backtest(hold_weights(carry_signal(C, F, n), h), R, F, cost)[0]
    for w in (0.5, 0.7):
        for h in (1, 7):
            cands[f"mélange {w}/{h}j"] = backtest(hold_weights(w * rank01(mom14) + (1 - w) * rank01(car7), h), R, F, cost)[0]
    year = np.array([np.datetime64(int(d), "ms").astype("datetime64[Y]").astype(int) + 1970 for d in days])
    wf, picks = [], {}
    for y in range(int(a.start[:4]) + 1, int(a.end[:4]) + 1):
        past, cur = year < y, year == y

        def sh(x):
            sd = x.std(ddof=1)
            return x.mean() / sd if sd > 0 else -9
        best = max(cands, key=lambda k: sh(cands[k][past]))
        picks[str(y)] = {"choice": best, "return_pct": round(float(np.prod(1 + cands[best][cur]) - 1) * 100, 1)}
        wf.append(cands[best][cur])
    wf = np.concatenate(wf)
    eq = np.cumprod(1 + wf)
    lo, hi = sharpe_ci(wf)
    var_trials = float(np.var([moments(v[te])[0] for v in cands.values()]))
    rep["walk_forward"] = {
        "years": picks, "sharpe": round(float(wf.mean() / wf.std(ddof=1) * math.sqrt(365)), 2),
        "sharpe_ci95": [round(lo, 2), round(hi, 2)], "return_pct": round(float(eq[-1] - 1) * 100, 1),
        "cagr_pct": round(float(eq[-1] ** (365 / len(wf)) - 1) * 100, 1),
        "max_dd_pct": round(float((1 - eq / np.maximum.accumulate(eq)).max()) * 100, 1),
        "prob_true_sharpe_positive": round(probabilistic_sharpe(wf), 3),
        "prob_not_luck_after_trials": round(deflated_sharpe(wf, N_TRIALS_PROJECT, var_trials), 3),
        "kelly_leverage_full": round(kelly_leverage(wf), 1), "kelly_leverage_half": round(kelly_leverage(wf) / 2, 1)}
    s_wf = rep["walk_forward"]["sharpe"]
    rep["time_to_confirm"] = {"years_for_95pct": round(years_to_confirm(s_wf), 1),
                              "expected_t_stat_after_5_months": round(s_wf * math.sqrt(5 / 12), 2)}

    # petit compte : 5 mois, k positions par côté, rééquilibrage hebdomadaire
    rep["small_account_5_months"] = {}
    for k in (2, 3):
        Wk = np.zeros((T, N))
        cur = np.zeros(N)
        for t in range(T):
            if t % 7 == 0:
                cur = xs_weights(blend[t], k_fixed=k)
            Wk[t] = cur
        pk = backtest(Wk, R, F, cost)[0]
        pk = pk[np.flatnonzero(np.abs(Wk).sum(axis=1) > 0)[0]:]
        for g in (1.0, 2.0):
            r5 = ruin_stats(pk, 150, leverage=g)
            rep["small_account_5_months"][f"{k}+{k} positions, exposition {g:g}×"] = {kk: round(v, 3 if kk.startswith("p_") else 1)
                                                                                    for kk, v in r5.items()}

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "portfolio_math.json").write_text(json.dumps(rep, indent=2, default=str))
    cols = ["sharpe", "return_pct", "max_dd_pct", "orders_per_month"]

    def row(label, r):
        return (f"| {label} | " + " | ".join(str(r["train"].get(c)) for c in cols[:3]) + " | "
                + " | ".join(str(r["test"].get(c)) for c in cols) + f" | {r['test_cost_x2']['sharpe']} |")
    md = ["# Couche mathématique sur la stratégie momentum + funding", "",
          f"Apprentissage {a.start} → {a.split} · vérification {next_month(a.split)} → {a.end} · {N} marchés · exposition 1×", "",
          "| version | appr. Sharpe | appr. rendement % | appr. baisse % | vérif. Sharpe | vérif. rendement % | vérif. baisse % | ordres/mois | vérif. Sharpe coûts ×2 |",
          "|---|---|---|---|---|---|---|---|---|", row("référence", rep["baseline"])]
    md += [row(f"{k} — **{v['verdict']}**", v) for k, v in rep["bricks"].items()]
    md += [row(f"**version finale** ({', '.join(adopted) or 'aucune brique'})", rep["final"]), "",
           "## Validation", "", f"- intervalle de confiance du Sharpe (vérification) : {val}",
           f"- walk-forward {int(a.start[:4]) + 1}–{a.end[:4]} : {rep['walk_forward']}",
           f"- durée pour confirmer en réel : {rep['time_to_confirm']}", "",
           "## Petit compte sur 5 mois (bootstrap, 5 000 trajectoires)", "",
           "| configuration | P(finir en perte) | P(baisse ≥ 50 %) | rendement médian % | 5 % pire | 5 % meilleur |", "|---|---|---|---|---|---|"]
    md += [f"| {k} | {v['p_loss']} | {v['p_drawdown_over_limit']} | {v['median_return_pct']} | {v['p5_return_pct']} | {v['p95_return_pct']} |"
           for k, v in rep["small_account_5_months"].items()]
    (out / "portfolio_math.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
