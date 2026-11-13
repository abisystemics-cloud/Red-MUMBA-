"""Contexte de marché : macro, flux institutionnels, géopolitique.

Six indicateurs journaliers, chacun ramené à un feu vert / rouge et décalé du délai
réel de publication (aucun regard vers le futur) :
- nasdaq  : Nasdaq Composite au-dessus de sa moyenne 100 jours (Yahoo/FRED, +2 j) ;
- stable  : offre totale de stablecoins en hausse sur 30 jours (DefiLlama, +1 j) ;
- premium : prime Coinbase positive en moyenne sur 7 jours — demande américaine,
            souvent institutionnelle (Coinbase vs Binance spot, +1 j) ;
- cot     : position nette des gérants d'actifs sur les futures Bitcoin du CME en hausse
            sur 4 semaines (rapport CFTC, +4 j) ;
- gpr     : risque géopolitique calme — moyenne 7 j ≤ 1,5 × moyenne 1 an (indice
            Caldara-Iacoviello, +2 j) ;
- fomc    : hors des 24 h précédant une décision de la Fed.
Une source en panne donne `None` : les règles qui en dépendent la traitent comme
neutre, et le rapport le signale.
"""
from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from scripts.bar_research import _get, _ms, _rows, months
from scripts.filter_research import above_sma, daily_flag_to_bars, fomc_allow, load_nasdaq, load_stablecoins, rising
from scripts.institution_research import (calm, load_binance_spot_daily, load_coinbase_daily, load_cot, load_gpr,
                                          positive_mean)

DAY_MS = 86_400_000
KEYS = ("nasdaq", "stable", "premium", "cot", "gpr", "fomc")
LABELS = {"nasdaq": "Nasdaq au-dessus de sa moyenne 100 j", "stable": "Stablecoins en hausse sur 30 j",
          "premium": "Prime Coinbase positive (7 j)", "cot": "Gérants d'actifs CME en hausse (4 sem.)",
          "gpr": "Risque géopolitique calme", "fomc": "Hors fenêtre de décision de la Fed"}


def _spot_recent(cache: Path, n_days: int) -> dict[float, float]:
    out = {}
    today = datetime.now(timezone.utc).date()
    for k in range(1, n_days + 1):
        d = (today - timedelta(days=k)).isoformat()
        raw = _get(f"https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1d/BTCUSDT-1d-{d}.zip",
                   cache / "spot" / f"day-{d}.zip")
        for r in _rows(raw) if raw else []:
            out[float(_ms(r[0]))] = float(r[4])
    return out


def build_context(days: np.ndarray, cache: Path, live: bool) -> tuple[dict, dict]:
    """→ ({clé: tableau booléen aligné sur `days` ou None}, {clé: note sur la source})."""
    shutil.rmtree(cache / "macro", ignore_errors=True)   # toujours des données fraîches
    close = np.asarray(days, dtype=float) + DAY_MS
    now = datetime.now(timezone.utc)
    this_month = f"{now.year:04d}-{now.month:02d}"
    first = datetime.fromtimestamp(float(days[0]) / 1000, timezone.utc) - timedelta(days=420)
    start_month = f"{first.year:04d}-{first.month:02d}"
    ctx: dict = dict.fromkeys(KEYS)
    info: dict = {}

    def attempt(key, fn):
        try:
            ctx[key], info[key] = fn()
        except Exception as e:  # noqa: BLE001 — une source externe en panne ne doit pas arrêter le laboratoire
            ctx[key], info[key] = None, f"indisponible ({type(e).__name__})"

    def nasdaq():
        t, v, src = load_nasdaq(cache)
        if len(t) < 150:
            return None, "indisponible"
        return daily_flag_to_bars(close, t, above_sma(v, 100), 2), f"{src}, {len(t)} jours"

    def stable():
        t, v = load_stablecoins(cache)
        if len(t) < 60:
            return None, "indisponible"
        return daily_flag_to_bars(close, t, rising(v, 30), 1), f"DefiLlama, {len(t)} jours"

    def cot():
        t, am, _lev = load_cot(cache)
        if len(t) < 20:
            return None, "indisponible"
        return daily_flag_to_bars(close, t, rising(am, 4), 4), f"CFTC, {len(t)} semaines"

    def gpr():
        t, v = load_gpr(cache)
        if len(t) < 400:
            return None, "indisponible"
        return daily_flag_to_bars(close, t, calm(v, 1.5), 2), f"indice GPR, {len(t)} jours"

    def premium():
        cb_t, cb_c = load_coinbase_daily(cache, start_month, this_month)
        last_full = f"{now.year - (now.month == 1):04d}-{(now.month - 2) % 12 + 1:02d}"
        bn_t, bn_c = load_binance_spot_daily(cache, months(start_month, last_full))
        spot = dict(zip(bn_t.tolist(), bn_c.tolist(), strict=True))
        if live:
            spot.update(_spot_recent(cache, 45))
        common = np.asarray(sorted(set(cb_t.tolist()) & set(spot)))
        if len(common) < 30:
            return None, "indisponible"
        cb = dict(zip(cb_t.tolist(), cb_c.tolist(), strict=True))
        prem = np.asarray([cb[k] / spot[k] - 1 for k in common])
        return daily_flag_to_bars(close, common, positive_mean(prem, 7), 1.01), f"Coinbase vs Binance spot, {len(common)} jours"

    attempt("nasdaq", nasdaq)
    attempt("stable", stable)
    attempt("cot", cot)
    attempt("gpr", gpr)
    attempt("premium", premium)
    ctx["fomc"], info["fomc"] = fomc_allow(close, 24), "calendrier de la Fed (liste jusqu'à fin 2026)"
    return ctx, info
