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
Et trois feux tirés d'un balayage du web, sans aucun LLM (ce sont des comptages) :
- news_tone : ton moyen des articles de presse mondiaux sur les cryptos (GDELT, qui
              indexe la presse en ligne de presque tous les pays) meilleur sur 7 jours
              que sur 90 jours ;
- geo_news  : part de la presse mondiale consacrée aux sanctions, invasions et frappes
              — calme si la moyenne 7 j ≤ 1,5 × la moyenne 1 an (GDELT, quotidien, là où
              l'indice GPR a plusieurs jours de retard) ;
- fng       : indice « Fear & Greed » des cryptos au-dessus de sa moyenne 30 jours
              (alternative.me : volatilité, volumes, réseaux sociaux, recherches Google).
Une source en panne donne `None` : les règles qui en dépendent la traitent comme
neutre, et le rapport le signale.
"""
from __future__ import annotations

import json
import shutil
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

from scripts.bar_research import _get, _ms, _rows, months
from scripts.filter_research import (_fetch, above_sma, daily_flag_to_bars, fomc_allow, load_nasdaq, load_stablecoins,
                                     rising)
from scripts.institution_research import (calm, load_binance_spot_daily, load_coinbase_daily, load_cot, load_gpr,
                                          positive_mean, trailing_mean)

DAY_MS = 86_400_000
KEYS = ("nasdaq", "stable", "premium", "cot", "gpr", "fomc", "news_tone", "geo_news", "fng")
CRYPTO_QUERY = "(bitcoin OR cryptocurrency OR ethereum)"
GEO_QUERY = '(sanctions OR invasion OR airstrike OR "missile attack")'
LABELS = {"nasdaq": "Nasdaq au-dessus de sa moyenne 100 j", "stable": "Stablecoins en hausse sur 30 j",
          "premium": "Prime Coinbase positive (7 j)", "cot": "Gérants d'actifs CME en hausse (4 sem.)",
          "gpr": "Risque géopolitique calme", "fomc": "Hors fenêtre de décision de la Fed",
          "news_tone": "Ton de la presse mondiale sur les cryptos en amélioration",
          "geo_news": "Presse mondiale : tensions géopolitiques calmes", "fng": "Indice Fear & Greed au-dessus de sa moyenne 30 j"}


def _gdelt_daily(query: str, mode: str, start: datetime, cache: Path, name: str) -> tuple[np.ndarray, np.ndarray]:
    """Série journalière GDELT (ton moyen ou part de la couverture) pour une recherche."""
    now = datetime.now(timezone.utc)
    url = ("https://api.gdeltproject.org/api/v2/doc/doc?query=" + urllib.parse.quote(query) + f"&mode={mode}&format=json"
           f"&startdatetime={start:%Y%m%d}000000&enddatetime={now:%Y%m%d%H%M%S}")
    raw = _fetch(url, cache / "macro" / name)
    time.sleep(6)   # GDELT : une requête toutes les 5 secondes
    if not raw or not raw.lstrip().startswith(b"{"):   # limite de débit ou page d'erreur : un second essai, plus tard
        (cache / "macro" / name).unlink(missing_ok=True)
        time.sleep(25)
        raw = _fetch(url, cache / "macro" / name)
        time.sleep(6)
    if not raw:
        raise RuntimeError("GDELT ne répond pas")
    acc: dict[float, list[float]] = {}
    for d in json.loads(raw)["timeline"][0]["data"]:
        day = datetime.strptime(str(d["date"])[:8], "%Y%m%d").replace(tzinfo=timezone.utc).timestamp() * 1000
        acc.setdefault(day, []).append(float(d["value"]))
    ks = sorted(acc)
    return np.asarray(ks), np.asarray([float(np.mean(acc[k])) for k in ks])


def _fear_greed(cache: Path) -> tuple[np.ndarray, np.ndarray]:
    raw = _fetch("https://api.alternative.me/fng/?limit=0&format=json", cache / "macro" / "fng.json")
    rows = sorted((float(r["timestamp"]) * 1000, float(r["value"])) for r in json.loads(raw)["data"])
    return np.asarray([r[0] for r in rows]), np.asarray([r[1] for r in rows])


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

    def news_tone():
        t, v = _gdelt_daily(CRYPTO_QUERY, "timelinetone", first, cache, "gdelt_tone.json")
        if len(t) < 120:
            return None, f"indisponible ({len(t)} jours)"
        short, long_ = trailing_mean(v, 7), trailing_mean(v, 90)
        return daily_flag_to_bars(close, t, np.isfinite(long_) & (short > long_), 1), f"GDELT, {len(t)} jours"

    def geo_news():
        t, v = _gdelt_daily(GEO_QUERY, "timelinevol", first, cache, "gdelt_geo.json")
        if len(t) < 380:
            return None, f"indisponible ({len(t)} jours)"
        return daily_flag_to_bars(close, t, calm(v, 1.5), 1), f"GDELT, {len(t)} jours"

    def fng():
        t, v = _fear_greed(cache)
        if len(t) < 60:
            return None, "indisponible"
        m = trailing_mean(v, 30)
        return daily_flag_to_bars(close, t, np.isfinite(m) & (v > m), 0), f"alternative.me, {len(t)} jours"

    attempt("news_tone", news_tone)
    attempt("geo_news", geo_news)
    attempt("fng", fng)
    attempt("nasdaq", nasdaq)
    attempt("stable", stable)
    attempt("cot", cot)
    attempt("gpr", gpr)
    attempt("premium", premium)
    ctx["fomc"], info["fomc"] = fomc_allow(close, 24), "calendrier de la Fed (liste jusqu'à fin 2026)"
    return ctx, info
