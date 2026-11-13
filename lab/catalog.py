"""Le catalogue : toutes les règles que le laboratoire sait jouer et comparer.

Une règle = une famille + des paramètres. Le laboratoire ne « devine » rien : il
génère les combinaisons de cette grille, les évalue toutes de la même façon, et laisse
le paper trading départager. Ajouter une idée = ajouter une famille ici.

Familles :
- blend : rang(momentum L j) × w + rang(funding bas sur n j) × (1 − w), long/short ;
- carry : funding seul (long les funding bas, short les hauts) ;
- xsmom : momentum relatif seul, long/short ;
- trend : chaque marché en hausse sur L jours est acheté (long seulement) ;
- premium : BTC, ETH et SOL achetés tant que la prime Coinbase est positive (demande
  institutionnelle américaine) ;
- ml : long/short sur les scores d'un modèle de machine learning ré-entraîné chaque
  semaine (`ridge` ou `gbm`, voir lab/ml.py).
`gate` (facultatif) branche une règle sur le contexte : exposition pleine quand le feu
est vert, divisée par deux quand il est rouge. Feux : nasdaq, stable, premium, cot, gpr,
fomc, news_tone, geo_news, fng (voir lab/context.py) et risk_on (au moins la moitié des cinq premiers au vert).
`k` = nombre de marchés par côté (0 = 20 % de l'univers) ; `hold` = jours entre deux
rééquilibrages, calés sur le calendrier (jour epoch % hold) pour que backtest et temps
réel tombent sur les mêmes dates.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from scripts.quant_research import carry_signal, mom_signal, rank01, xs_weights

DAY_MS = 86_400_000


@dataclass(frozen=True)
class Spec:
    family: str
    params: tuple  # ((clé, valeur), ...) triées

    @property
    def name(self) -> str:
        fmt = lambda v: v if isinstance(v, str) else f"{v:g}"  # noqa: E731
        return self.family + "(" + ",".join(f"{k}={fmt(v)}" for k, v in self.params) + ")"

    def p(self, key: str, default=0):
        return dict(self.params).get(key, default)


def spec(family: str, **params) -> Spec:
    return Spec(family, tuple(sorted(params.items())))


def default_catalog() -> list[Spec]:
    cat = [spec("blend", w=w, mom=14, carry=7, hold=h, k=k) for w in (0.5, 0.7) for h in (1, 7) for k in (0, 3)]
    cat += [spec("carry", carry=n, hold=7, k=k) for n in (3, 7, 14) for k in (0, 3)]
    cat += [spec("xsmom", mom=L, hold=7, k=0) for L in (14, 28)]
    cat += [spec("trend", mom=L, hold=1) for L in (7, 14, 28)]
    # règles branchées sur le contexte (macro, institutions, géopolitique)
    cat += [spec("blend", w=w, mom=14, carry=7, hold=h, k=0, gate=g)
            for (w, h) in ((0.5, 7), (0.7, 1)) for g in GATES]
    cat += [spec("trend", mom=14, hold=1, gate=g) for g in ("nasdaq", "premium", "risk_on")]
    cat += [spec("premium", hold=1)]
    # règles apprises par machine learning (ré-entraînées chaque lundi)
    cat += [spec("ml", model=m, hold=7, k=0) for m in ("ridge", "gbm")]
    return cat


GATES = ("nasdaq", "stable", "premium", "cot", "gpr", "fomc", "risk_on", "news_tone", "geo_news", "fng")


def gate_flag(panel: dict, gate: str) -> np.ndarray:
    """Feu vert (True) / rouge par jour ; une source indisponible compte comme verte."""
    ctx = panel.get("ctx") or {}
    T = len(panel["days"])
    if gate == "risk_on":
        avail = [np.asarray(ctx[g], dtype=float) for g in ("nasdaq", "stable", "premium", "cot", "gpr") if ctx.get(g) is not None]
        return np.mean(avail, axis=0) >= 0.5 if avail else np.ones(T, bool)
    f = ctx.get(gate)
    return np.ones(T, bool) if f is None else np.asarray(f, dtype=bool)


def signal(panel: dict, s: Spec) -> np.ndarray:
    C, F = panel["C"], panel["F"]
    if s.family == "blend":
        w = s.p("w")
        return w * rank01(mom_signal(C, int(s.p("mom")))) + (1 - w) * rank01(carry_signal(C, F, int(s.p("carry"))))
    if s.family == "carry":
        return carry_signal(C, F, int(s.p("carry")))
    if s.family in ("xsmom", "trend"):
        return mom_signal(C, int(s.p("mom")))
    if s.family == "ml":
        sc = (panel.get("ml_scores") or {}).get(s.p("model"))
        return np.full(C.shape, np.nan) if sc is None else sc
    raise ValueError(f"famille inconnue : {s.family}")


def weights(panel: dict, s: Spec) -> np.ndarray:
    """Poids cibles (T×N) ; la ligne t n'utilise que les données ≤ clôture du jour t."""
    if s.family == "premium":
        T, N = panel["C"].shape
        W = np.zeros((T, N))
        flag = (panel.get("ctx") or {}).get("premium")
        idx = [panel["coins"].index(c) for c in ("BTC", "ETH", "SOL") if c in panel["coins"]]
        if flag is not None and idx:
            W[:, idx] = np.asarray(flag, dtype=float)[:, None] / len(idx)
        return W
    sig = signal(panel, s)
    T, N = sig.shape
    day_idx = (np.asarray(panel["days"]) // DAY_MS).astype(np.int64)
    hold = max(int(s.p("hold", 1)), 1)
    W = np.zeros((T, N))
    cur = np.zeros(N)
    started = False
    for t in range(T):
        if day_idx[t] % hold == 0 or not started:
            if s.family == "trend":
                ok = np.isfinite(sig[t])
                cur = np.where(ok & (np.nan_to_num(sig[t]) > 0), 1.0 / max(int(ok.sum()), 1), 0.0) if ok.sum() >= 3 else np.zeros(N)
            else:
                cur = xs_weights(sig[t], k_fixed=int(s.p("k")))
            started = started or bool(np.isfinite(sig[t]).any())
        W[t] = cur
    gate = s.p("gate", None)
    if gate:
        W = W * np.where(gate_flag(panel, gate), 1.0, 0.5)[:, None]
    return W
