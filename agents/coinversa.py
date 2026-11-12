"""Client Coinversa Pulse (API REST, en-tête X-API-Key) et conversion en événements.

Deux usages :
- positionnement : biais long/short des catégories de traders, de « money_printer »
  (les plus rentables) à « giga_rekt » (les plus perdants). Signal = biais des
  rentables moins biais des perdants (les perdants servent d'indicateur inverse) ;
- liquidations : carte des prix où des positions ouvertes seraient liquidées.

Les parseurs sont tolérants : la route d'historique renvoie netBias en pourcentage
(−100..100), la route live en ratio (−1..1). Ils sont normalisés ici en ratio, et
recalculés depuis les notionnels quand ceux-ci sont présents.
"""
from __future__ import annotations

import os
from collections import defaultdict
from typing import Any, Iterable, Optional

from core.events import WhaleBias


def _rows(body: Any) -> list[dict]:
    if isinstance(body, list):
        return body
    if isinstance(body, dict):
        for k in ("rows", "data", "snapshots", "items", "results"):
            v = body.get(k)
            if isinstance(v, list):
                return v
    return []


def _tier(row: dict) -> str:
    return str(row.get("tier") or row.get("pnlTier") or row.get("sizeTier") or "")


def tier_bias(row: dict) -> float:
    ln, sn = row.get("longNotional"), row.get("shortNotional")
    if ln is not None and sn is not None:
        tot = float(ln) + float(sn)
        return (float(ln) - float(sn)) / tot if tot > 0 else 0.0
    nb = float(row.get("netBias") or 0.0)
    return nb / 100.0 if abs(nb) > 1.0 else nb


def _group(rows: Iterable[dict], tiers: set[str]) -> tuple[float, float, int]:
    long_n = short_n = 0.0
    accounts = 0
    for r in rows:
        if _tier(r) not in tiers:
            continue
        ln, sn = r.get("longNotional"), r.get("shortNotional")
        if ln is None or sn is None:  # pas de notionnels : on reconstitue un poids unitaire
            b = tier_bias(r)
            ln, sn = (1 + b) / 2, (1 - b) / 2
        long_n += float(ln)
        short_n += float(sn)
        accounts += int(r.get("accountCount") or 0)
    tot = long_n + short_n
    return ((long_n - short_n) / tot if tot > 0 else 0.0), tot, accounts


def positioning_signal(rows: list[dict], cfg) -> tuple[float, float, int]:
    """(signal ∈ [-1, 1], notionnel considéré, comptes) pour UN instantané."""
    smart, g1, a1 = _group(rows, set(cfg.smart_tiers))
    crowd, g2, a2 = _group(rows, set(cfg.crowd_tiers))
    w = cfg.smart_weight
    sig = w * smart - (1 - w) * crowd
    return max(-1.0, min(1.0, sig)), g1 + g2, a1 + a2


def snapshots_to_bias(body: Any, coin: str, cfg) -> list[WhaleBias]:
    """Regroupe les lignes par horodatage (un instantané = toutes les catégories)."""
    by_ts: dict[int, list[dict]] = defaultdict(list)
    for r in _rows(body):
        if r.get("tierType") not in (None, "pnl"):
            continue
        if r.get("coin") not in (None, coin):
            continue
        ts = r.get("timestamp")
        if ts is None:
            continue
        by_ts[int(ts)].append(r)
    out = []
    for ts in sorted(by_ts):
        sig, gross, n = positioning_signal(by_ts[ts], cfg)
        out.append(WhaleBias(coin, ts, sig, n, gross))
    return out


def heatmap_to_clusters(body: Any, top: int = 15) -> list[tuple[float, float]]:
    buckets = body.get("buckets") if isinstance(body, dict) else None
    out = []
    for b in buckets or []:
        lo, hi = b.get("priceLow"), b.get("priceHigh")
        usd = b.get("totalNotionalAtRisk")
        if lo is None or hi is None or usd is None:
            continue
        out.append(((float(lo) + float(hi)) / 2, float(usd)))
    return sorted(out, key=lambda c: -c[1])[:top]


class CoinversaClient:
    def __init__(self, cfg, http_session, api_key: Optional[str] = None):
        self.cfg = cfg
        self._http = http_session
        self.key = api_key or os.getenv("COINVERSA_API_KEY")

    @property
    def ready(self) -> bool:
        return bool(self.key and self._http)

    async def get(self, path: str, params: Optional[dict] = None) -> Any:
        url = self.cfg.base_url.rstrip("/") + path
        async with self._http.get(url, params=params or {}, headers={"X-API-Key": self.key},
                                  timeout=20) as r:
            r.raise_for_status()
            return await r.json()

    async def latest_bias(self, coin: str) -> Optional[WhaleBias]:
        body = await self.get(self.cfg.cohort_history_path, {"coin": coin, "since": "2h"})
        snaps = snapshots_to_bias(body, coin, self.cfg)
        return snaps[-1] if snaps else None

    async def heatmap(self, coin: str) -> list[tuple[float, float]]:
        body = await self.get(self.cfg.heatmap_path.format(coin=coin),
                              {"coin": coin, "buckets": self.cfg.heatmap_buckets,
                               "range": self.cfg.heatmap_range_pct})
        return heatmap_to_clusters(body)
