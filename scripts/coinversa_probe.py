"""Vérifie la clé Coinversa et trouve les bons chemins d'API (une requête par essai).

    COINVERSA_API_KEY=... python scripts/coinversa_probe.py

Affiche, pour chaque route utilisée par le bot, si elle répond, et propose la
valeur à mettre dans config.yaml (data.coinversa.*) si le chemin par défaut
ne fonctionne pas. Écrit aussi data/reports/coinversa_probe.json.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agents.coinversa import heatmap_to_clusters, snapshots_to_bias  # noqa: E402
from core.config import load_config  # noqa: E402

HEATMAP_CANDIDATES = [
    "/live/liquidation-heatmap/{coin}", "/live/liquidations/heatmap/{coin}", "/live/heatmap/{coin}",
    "/live/risk/coins/{coin}/heatmap", "/live/liquidation-heatmap?coin={coin}",
    "/live/liquidations/heatmap?coin={coin}",
]
COHORT_CANDIDATES = ["/pulse/cohort-bias/history", "/live/cohort-bias/history"]


def get(base: str, path: str, key: str, params: str = "") -> tuple[int, object]:
    sep = "&" if "?" in path else "?"
    url = base.rstrip("/") + path + (sep + params if params else "")
    req = urllib.request.Request(url, headers={"X-API-Key": key, "User-Agent": "hl-swarm-probe"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # noqa: BLE001
        return 0, str(e)


def main() -> int:
    key = os.getenv("COINVERSA_API_KEY")
    if not key:
        print("COINVERSA_API_KEY manquante", file=sys.stderr)
        return 2
    cfg = load_config(Path(__file__).resolve().parents[1] / "config.yaml").data.coinversa
    out: dict = {"base_url": cfg.base_url}
    st, body = get(cfg.base_url, "/pulse/my-plan", key)
    out["plan"] = {"status": st, "body": body}
    found_cohort = None
    for path in [cfg.cohort_history_path] + [c for c in COHORT_CANDIDATES if c != cfg.cohort_history_path]:
        st, body = get(cfg.base_url, path, key, "coin=BTC&since=2h&tierType=pnl")
        snaps = snapshots_to_bias(body, "BTC", cfg) if st == 200 else []
        print(f"cohort  {path:45s} HTTP {st}  snapshots={len(snaps)}")
        if snaps and not found_cohort:
            found_cohort = path
            out["cohort_sample"] = {"ts": snaps[-1].ts, "signal": snaps[-1].bias}
    found_heat = None
    for path in [cfg.heatmap_path] + [c for c in HEATMAP_CANDIDATES if c != cfg.heatmap_path]:
        st, body = get(cfg.base_url, path.format(coin="BTC"), key, "buckets=20&range=10")
        clusters = heatmap_to_clusters(body) if st == 200 else []
        print(f"heatmap {path:45s} HTTP {st}  clusters={len(clusters)}")
        if clusters and not found_heat:
            found_heat = path
    out["cohort_history_path"] = found_cohort
    out["heatmap_path"] = found_heat
    rep = Path("data/reports")
    rep.mkdir(parents=True, exist_ok=True)
    (rep / "coinversa_probe.json").write_text(json.dumps(out, indent=2, default=str))
    print(json.dumps({"cohort_history_path": found_cohort, "heatmap_path": found_heat}, indent=2))
    if found_heat and found_heat != cfg.heatmap_path:
        print(f"→ mettre data.coinversa.heatmap_path: {found_heat} dans config.yaml")
    return 0 if found_cohort else 1


if __name__ == "__main__":
    sys.exit(main())
