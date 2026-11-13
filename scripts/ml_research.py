"""Machine learning + trois habitudes de poker, testés contre la stratégie de référence.

    python scripts/ml_research.py --from 2020-01 --to 2026-10 --split 2023-12

Référence : mélange 50/50 momentum 14 j + funding 7 j, top/bottom 20 %, hebdomadaire.

A. MACHINE LEARNING (aucun LLM : des modèles statistiques entraînés sur le passé)
   Le modèle apprend, pour chaque marché et chaque jour, à prédire son rang de
   rendement sur les 7 jours suivants à partir de 10 caractéristiques (momentum 3/7/
   14/28 j, funding 3/7/14 j, volatilité, bêta, retour 1 j). Deux modèles du livre
   StatQuest, hyperparamètres FIXÉS d'avance (pas de réglage = pas d'essais cachés) :
   - régression ridge (linéaire régularisée) ;
   - gradient boosting (arbres de décision) ;
   plus leur moyenne. Entraînement « walk-forward » : chaque 1er janvier le modèle est
   ré-entraîné sur tout le passé (avec 7 jours de purge) puis trade l'année suivante.
   ADOPTÉ si, sur 2021–fin ET sur la vérification, Sharpe ≥ référence + 0,10 et
   rendement > 0 à coûts ×2.

B. POKER
   1. « Forget the pot » : les poids ne dépendent que du classement du jour, jamais du
      prix d'entrée ni du gain/perte en cours — vérifié par construction (pas de test).
   2. « Pick your table » : ne jouer gros que quand la table est bonne — exposition 1×
      quand la dispersion des funding (écart-type entre marchés) dépasse sa médiane
      180 j, 0,5× sinon.
   3. « Plug your leaks » : d'où viennent gains et pertes (jambe long / short, prix /
      funding, frais, marchés) ; puis la fuite la plus évidente est colmatée : jambe
      short remplacée par une couverture BTC (une seule vente, liquide).
   Même règle d'adoption que portfolio_math.py.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml_engine.stats import sharpe_ci  # noqa: E402
from scripts.bar_research import Costs  # noqa: E402
from scripts.portfolio_math import rolling_beta, rolling_std  # noqa: E402
from scripts.quant_research import backtest, build_panel, carry_signal, hold_weights, mom_signal, rank01, stats  # noqa: E402
from scripts.tsmom_robustness import ms, next_month  # noqa: E402

FEATURES = ["mom3", "mom7", "mom14", "mom28", "carry3", "carry7", "carry14", "vol30", "beta60", "rev1"]
HORIZON = 7


def year_of(days: np.ndarray) -> np.ndarray:
    return np.array([np.datetime64(int(d), "ms").astype("datetime64[Y]").astype(int) + 1970 for d in days])


def make_features(C, F, R, b) -> np.ndarray:
    raw = [mom_signal(C, 3), mom_signal(C, 7), mom_signal(C, 14), mom_signal(C, 28),
           carry_signal(C, F, 3), carry_signal(C, F, 7), carry_signal(C, F, 14),
           rolling_std(R, 30), np.where(np.isfinite(C), rolling_beta(R, b, 60), np.nan), -mom_signal(C, 1)]
    X = np.stack([rank01(x) for x in raw], axis=2)  # rangs 0..1 par jour : robustes aux valeurs extrêmes
    return X


def make_target(C, F, R) -> np.ndarray:
    T, N = C.shape
    net = np.nan_to_num(R) - np.nan_to_num(F)
    c = np.cumsum(np.vstack([np.zeros((1, N)), net]), axis=0)
    y = np.full((T, N), np.nan)
    y[:T - HORIZON] = c[HORIZON + 1:] - c[1:T - HORIZON + 1]  # somme des jours t+1..t+7
    y[~np.isfinite(C)] = np.nan
    y[:T - HORIZON][~np.isfinite(C[HORIZON:])] = np.nan
    return rank01(y) - 0.5


def walk_forward_scores(X, y, years, first_year, last_year, make_model) -> tuple[np.ndarray, list]:
    T, N, K = X.shape
    score = np.full((T, N), np.nan)
    ok_x = np.isfinite(X).all(axis=2)
    info = []
    for yr in range(first_year, last_year + 1):
        start = int(np.flatnonzero(years == yr)[0])
        tr_mask = np.zeros((T, N), bool)
        tr_mask[:max(start - HORIZON, 0)] = True  # purge : la cible ne déborde pas sur l'année tradée
        tr_mask &= ok_x & np.isfinite(y)
        if tr_mask.sum() < 500:
            continue
        m = make_model()
        m.fit(X[tr_mask], y[tr_mask])
        te = np.zeros((T, N), bool)
        te[years == yr] = True
        te &= ok_x
        score[te] = m.predict(X[te])
        info.append((yr, int(tr_mask.sum()), m))
    return score, info


def main() -> int:
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import Ridge

    p = argparse.ArgumentParser()
    p.add_argument("--from", dest="start", default="2020-01")
    p.add_argument("--to", dest="end", default="2026-10")
    p.add_argument("--split", default="2023-12")
    p.add_argument("--cache", default="data/bars")
    p.add_argument("--out", default="data/reports")
    a = p.parse_args()
    coins, _raw, days, C, F, R, b = build_panel(Path(a.cache), a.start, a.end)
    T, N = C.shape
    years = year_of(days)
    y0, y1 = int(a.start[:4]) + 1, int(a.end[:4])
    split = ms(next_month(a.split))
    wf, te, tr = years >= y0, days >= split, days < split
    cost, cost2 = Costs().side, Costs(mult=2.0).side
    mom14, car7 = mom_signal(C, 14), carry_signal(C, F, 7)
    blend = 0.5 * rank01(mom14) + 0.5 * rank01(car7)
    W0 = hold_weights(blend, 7)

    def ev(W, spans):
        pnl, turn, chg = backtest(W, R, F, cost)
        pnl2, _, _ = backtest(W, R, F, cost2)
        out = {k: stats(pnl[m], turn[m], chg[m]) for k, m in spans.items()}
        out.update({f"{k}_cost_x2": stats(pnl2[m], turn[m], chg[m]) for k, m in spans.items()})
        return out, pnl

    # ------------------------------------------------------------ A. ML
    spans_ml = {"walk_forward": wf, "test": te}
    base_ml, base_pnl = ev(W0, spans_ml)
    X, y = make_features(C, F, R, b), make_target(C, F, R)
    models = {
        "ridge": lambda: Ridge(alpha=10.0),
        "gradient_boosting": lambda: HistGradientBoostingRegressor(
            max_depth=3, learning_rate=0.05, max_iter=200, min_samples_leaf=50, l2_regularization=1.0, random_state=0),
    }
    rep: dict = {"universe": coins, "features": FEATURES, "ml": {"reference": base_ml}}
    scores = {}
    for name, mk in models.items():
        sc, info = walk_forward_scores(X, y, years, y0, y1, mk)
        scores[name] = sc
        r, _ = ev(hold_weights(sc, 7), spans_ml)
        rep["ml"][name] = r
        if name == "ridge" and info:
            rep["ml"]["ridge_coefficients_last_fit"] = dict(zip(FEATURES, [round(float(c), 3) for c in info[-1][2].coef_], strict=True))
            rep["ml"]["training_rows_last_fit"] = info[-1][1]
        print(name, r["walk_forward"]["sharpe"], r["test"]["sharpe"], flush=True)
    ens = (rank01(scores["ridge"]) + rank01(scores["gradient_boosting"])) / 2
    rep["ml"]["ensemble"], ens_pnl = ev(hold_weights(ens, 7), spans_ml)
    for name in ("ridge", "gradient_boosting", "ensemble"):
        r = rep["ml"][name]
        ok = all(r[s]["sharpe"] >= base_ml[s]["sharpe"] + 0.10 and r[f"{s}_cost_x2"]["return_pct"] > 0 for s in spans_ml)
        r["verdict"] = "ADOPTÉ" if ok else "ÉCARTÉ"
    lo, hi = sharpe_ci(ens_pnl[wf])
    rep["ml"]["ensemble"]["walk_forward_sharpe_ci95"] = [round(lo, 2), round(hi, 2)]
    lo, hi = sharpe_ci(base_pnl[wf])
    rep["ml"]["reference"]["walk_forward_sharpe_ci95"] = [round(lo, 2), round(hi, 2)]

    # --------------------------------------------------------- B. poker
    spans = {"train": tr, "test": te}
    base, _ = ev(W0, spans)
    rep["poker"] = {"reference": base}
    # 2. pick your table : dispersion des funding
    disp = np.nanstd(car7, axis=1)
    med = np.full(T, np.nan)
    for t in range(180, T):
        med[t] = np.nanmedian(disp[t - 180:t])
    gate = np.where(np.isfinite(med) & (disp < med), 0.5, 1.0)
    # 3. plug your leaks : attribution puis couverture BTC
    r_net, Fz = np.nan_to_num(R), np.nan_to_num(F)
    dW = np.abs(np.diff(W0, axis=0, prepend=np.zeros((1, N))))
    Wl, Ws = np.clip(W0, 0, None), np.clip(W0, None, 0)

    def contrib(mask):
        m = mask[1:]
        per_coin = ((W0[:-1] * (r_net[1:] - Fz[1:]))[m]).sum(axis=0) * 100
        order = np.argsort(per_coin)
        return {"long_price_pct": round(float((Wl[:-1] * r_net[1:])[m].sum()) * 100, 1),
                "short_price_pct": round(float((Ws[:-1] * r_net[1:])[m].sum()) * 100, 1),
                "long_funding_pct": round(float((-Wl[:-1] * Fz[1:])[m].sum()) * 100, 1),
                "short_funding_pct": round(float((-Ws[:-1] * Fz[1:])[m].sum()) * 100, 1),
                "costs_pct": round(-cost * float(dW[:-1][m].sum()) * 100, 1),
                "worst_coins": {coins[j]: round(float(per_coin[j]), 1) for j in order[:4]},
                "best_coins": {coins[j]: round(float(per_coin[j]), 1) for j in order[-4:][::-1]}}
    rep["poker"]["leaks"] = {"train": contrib(tr), "test": contrib(te)}
    beta = rolling_beta(R, b, 60)
    Wh = Wl.copy()
    Wh[:, b] -= (Wl * beta).sum(axis=1)
    variants = {"pick_your_table (dispersion des funding)": W0 * gate[:, None],
                "plug_leak (short remplacé par couverture BTC)": Wh}
    for name, W in variants.items():
        r, _ = ev(W, spans)
        bt, rt = base["test"], r["test"]
        ok = r["train"]["sharpe"] > base["train"]["sharpe"] and (
            rt["sharpe"] >= bt["sharpe"] + 0.10 or (rt["max_dd_pct"] <= 0.8 * bt["max_dd_pct"] and rt["sharpe"] >= bt["sharpe"] - 0.05))
        r["verdict"] = "ADOPTÉE" if ok else "ÉCARTÉE"
        rep["poker"][name] = r

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "ml_research.json").write_text(json.dumps(rep, indent=2, default=str))
    cols = ["sharpe", "return_pct", "max_dd_pct", "orders_per_month"]
    md = ["# Machine learning et habitudes de poker", "", f"{N} marchés · exposition 1× · walk-forward {y0}–{y1}", "",
          "## A. Machine learning (ré-entraîné chaque année sur le passé)", "",
          "| modèle | verdict | WF Sharpe | WF rendement % | WF baisse % | vérif. Sharpe | vérif. rendement % | vérif. baisse % | ordres/mois | vérif. Sharpe coûts ×2 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for k in ("reference", "ridge", "gradient_boosting", "ensemble"):
        r = rep["ml"][k]
        md.append(f"| {k} | {r.get('verdict', '–')} | " + " | ".join(str(r["walk_forward"][c]) for c in cols[:3]) + " | "
                  + " | ".join(str(r["test"][c]) for c in cols) + f" | {r['test_cost_x2']['sharpe']} |")
    md += ["", f"- intervalle 95 % du Sharpe walk-forward : référence {rep['ml']['reference']['walk_forward_sharpe_ci95']}, "
           f"ensemble {rep['ml']['ensemble']['walk_forward_sharpe_ci95']}",
           f"- poids appris par la ridge (dernier entraînement, {rep['ml'].get('training_rows_last_fit')} lignes) : "
           f"{rep['ml'].get('ridge_coefficients_last_fit')}", "",
           "## B. Poker", "", f"- fuites (apprentissage) : {rep['poker']['leaks']['train']}",
           f"- fuites (vérification) : {rep['poker']['leaks']['test']}", "",
           "| version | verdict | appr. Sharpe | appr. baisse % | vérif. Sharpe | vérif. rendement % | vérif. baisse % | vérif. Sharpe coûts ×2 |",
           "|---|---|---|---|---|---|---|---|"]
    for k, r in rep["poker"].items():
        if k == "leaks":
            continue
        md.append(f"| {k} | {r.get('verdict', '–')} | {r['train']['sharpe']} | {r['train']['max_dd_pct']} | {r['test']['sharpe']} | "
                  f"{r['test']['return_pct']} | {r['test']['max_dd_pct']} | {r['test_cost_x2']['sharpe']} |")
    (out / "ml_research.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
