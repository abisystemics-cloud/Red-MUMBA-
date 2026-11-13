"""Machine learning en service : deux modèles qui s'entraînent seuls, sans LLM.

Chaque lundi, sur tout l'historique : le modèle apprend à prédire, pour chaque marché,
son rang de rendement net (prix − funding) sur les 7 jours suivants, à partir de
10 caractéristiques de marché (rangs de momentum, funding, volatilité, bêta) et des
6 feux de contexte (macro, institutions, géopolitique).
- `ridge` : régression linéaire régularisée — sauvegardée en clair (coefficients) ;
- `gbm`   : gradient boosting (arbres de décision) — peut combiner contexte × marché.
Hyperparamètres fixes (aucun réglage caché). La fiche de score des règles ML est
calculée en « walk-forward » (ré-entraînement chaque année sur le passé seulement) :
le modèle n'est jamais noté sur des données qu'il a vues.
"""
from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np

from lab.context import KEYS as CTX_KEYS
from scripts.ml_research import FEATURES, HORIZON, make_features, make_target, walk_forward_scores, year_of

MODELS = ("ridge", "gbm")
FEATURE_NAMES = list(FEATURES) + [f"ctx_{k}" for k in CTX_KEYS]


def features(panel: dict) -> np.ndarray:
    C, F, R = panel["C"], panel["F"], panel["R"]
    b = panel["coins"].index("BTC") if "BTC" in panel["coins"] else 0
    X = make_features(C, F, R, b)
    T, N, _ = X.shape
    ctx = panel.get("ctx") or {}
    cols = []
    for k in CTX_KEYS:
        f = ctx.get(k)
        cols.append(np.full(T, 0.5) if f is None else np.asarray(f, dtype=float))
    Z = np.repeat(np.stack(cols, axis=1)[:, None, :], N, axis=1)
    Z = np.where(np.isfinite(X[:, :, :1]), Z, np.nan)          # marché absent → ligne ignorée
    return np.concatenate([X, Z], axis=2)


def make_model(kind: str):
    if kind == "ridge":
        from sklearn.linear_model import Ridge
        return Ridge(alpha=10.0)
    from sklearn.ensemble import HistGradientBoostingRegressor
    return HistGradientBoostingRegressor(max_depth=3, learning_rate=0.05, max_iter=200, min_samples_leaf=50,
                                         l2_regularization=1.0, random_state=0)


def walk_forward(panel: dict, kind: str) -> np.ndarray:
    """Scores honnêtes pour la fiche de score : chaque année est prédite par un modèle
    entraîné uniquement sur les années précédentes."""
    X, y, years = features(panel), make_target(panel["C"], panel["F"], panel["R"]), year_of(panel["days"])
    first = int(years[0]) + 1
    sc, _ = walk_forward_scores(X, y, years, first, int(years[-1]), lambda: make_model(kind))
    return sc


def train_final(panel: dict, kind: str):
    X, y = features(panel), make_target(panel["C"], panel["F"], panel["R"])
    m = np.isfinite(X).all(axis=2) & np.isfinite(y)
    model = make_model(kind)
    model.fit(X[m], y[m])
    return model, int(m.sum())


def save(model, kind: str, sdir: Path, meta: dict) -> None:
    d = sdir / "models"
    d.mkdir(parents=True, exist_ok=True)
    if kind == "ridge":
        (d / "ridge.json").write_text(json.dumps({"coef": [float(c) for c in model.coef_], "intercept": float(model.intercept_),
                                                  "features": FEATURE_NAMES, **meta}, indent=1))
    else:
        (d / f"{kind}.pkl").write_bytes(pickle.dumps(model))
        (d / f"{kind}.json").write_text(json.dumps(meta, indent=1))


def predict(kind: str, sdir: Path, panel: dict) -> np.ndarray | None:
    """Scores du jour à partir du modèle sauvegardé ; None si le modèle manque ou ne se charge pas."""
    d = sdir / "models"
    X = features(panel)
    ok = np.isfinite(X).all(axis=2)
    out = np.full(X.shape[:2], np.nan)
    try:
        if kind == "ridge":
            m = json.loads((d / "ridge.json").read_text())
            if m.get("features") != FEATURE_NAMES:
                return None
            out[ok] = X[ok] @ np.asarray(m["coef"]) + m["intercept"]
        else:
            model = pickle.loads((d / f"{kind}.pkl").read_bytes())  # noqa: S301 — fichier écrit par ce même laboratoire
            out[ok] = model.predict(X[ok])
    except Exception:  # noqa: BLE001 — modèle absent ou incompatible : la règle reste à plat
        return None
    return out


__all__ = ["MODELS", "FEATURE_NAMES", "HORIZON", "features", "walk_forward", "train_final", "save", "predict"]
