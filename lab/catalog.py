"""Le catalogue : toutes les règles que le laboratoire sait jouer et comparer.

Une règle = une famille + des paramètres. Le laboratoire ne « devine » rien : il
génère les combinaisons de cette grille, les évalue toutes de la même façon, et laisse
le paper trading départager. Ajouter une idée = ajouter une famille ici.

Familles :
- blend : rang(momentum L j) × w + rang(funding bas sur n j) × (1 − w), long/short ;
- carry : funding seul (long les funding bas, short les hauts) ;
- xsmom : momentum relatif seul, long/short ;
- trend : chaque marché en hausse sur L jours est acheté (long seulement).
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
        return self.family + "(" + ",".join(f"{k}={v:g}" for k, v in self.params) + ")"

    def p(self, key: str, default: float = 0) -> float:
        return dict(self.params).get(key, default)


def spec(family: str, **params) -> Spec:
    return Spec(family, tuple(sorted(params.items())))


def default_catalog() -> list[Spec]:
    cat = [spec("blend", w=w, mom=14, carry=7, hold=h, k=k) for w in (0.5, 0.7) for h in (1, 7) for k in (0, 3)]
    cat += [spec("carry", carry=n, hold=7, k=k) for n in (3, 7, 14) for k in (0, 3)]
    cat += [spec("xsmom", mom=L, hold=7, k=0) for L in (14, 28)]
    cat += [spec("trend", mom=L, hold=1) for L in (7, 14, 28)]
    return cat


def signal(panel: dict, s: Spec) -> np.ndarray:
    C, F = panel["C"], panel["F"]
    if s.family == "blend":
        w = s.p("w")
        return w * rank01(mom_signal(C, int(s.p("mom")))) + (1 - w) * rank01(carry_signal(C, F, int(s.p("carry"))))
    if s.family == "carry":
        return carry_signal(C, F, int(s.p("carry")))
    if s.family in ("xsmom", "trend"):
        return mom_signal(C, int(s.p("mom")))
    raise ValueError(f"famille inconnue : {s.family}")


def weights(panel: dict, s: Spec) -> np.ndarray:
    """Poids cibles (T×N) ; la ligne t n'utilise que les données ≤ clôture du jour t."""
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
    return W
