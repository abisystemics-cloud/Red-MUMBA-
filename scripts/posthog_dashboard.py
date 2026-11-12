"""Crée (ou recrée) le dashboard PostHog "hl-swarm — Live Trading".

    POSTHOG_PERSONAL_API_KEY=phx_... POSTHOG_PROJECT_ID=12345 \
    POSTHOG_API_HOST=https://eu.posthog.com python scripts/posthog_dashboard.py

Tuiles : PnL cumulé, latence des ordres (p50/p99), slippage moyen par marché,
taux de signaux rejetés par motif, equity, R-multiples par trade.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

INSIGHTS = {
    "PnL cumulé (USD)": """
        SELECT toStartOfFiveMinutes(timestamp) AS t,
               sum(sum(toFloat(properties.pnl))) OVER (ORDER BY t) AS cum_pnl
        FROM events WHERE event = 'hlswarm_trade_closed' AND timestamp > now() - INTERVAL 7 DAY
        GROUP BY t ORDER BY t""",
    "Latence ordres (ms) p50 / p99": """
        SELECT toStartOfHour(timestamp) AS t,
               quantile(0.5)(toFloat(properties.latency_ms)) AS p50,
               quantile(0.99)(toFloat(properties.latency_ms)) AS p99
        FROM events WHERE event = 'hlswarm_order' AND timestamp > now() - INTERVAL 7 DAY
        GROUP BY t ORDER BY t""",
    "Slippage moyen (bps) par marché": """
        SELECT properties.coin AS coin, avg(toFloat(properties.slippage_bps)) AS slippage_bps,
               count() AS fills
        FROM events WHERE event = 'hlswarm_fill' AND timestamp > now() - INTERVAL 7 DAY
        GROUP BY coin ORDER BY fills DESC""",
    "Signaux : validés vs rejetés": """
        SELECT toStartOfHour(timestamp) AS t, properties.validated AS validated, count() AS n
        FROM events WHERE event = 'hlswarm_signal' AND timestamp > now() - INTERVAL 3 DAY
        GROUP BY t, validated ORDER BY t""",
    "Equity": """
        SELECT toStartOfFiveMinutes(timestamp) AS t, argMax(toFloat(properties.equity), timestamp) AS equity
        FROM events WHERE event = 'hlswarm_equity' AND timestamp > now() - INTERVAL 7 DAY
        GROUP BY t ORDER BY t""",
    "R-multiple par trade": """
        SELECT timestamp, properties.coin AS coin, properties.reason AS reason,
               toFloat(properties.r_multiple) AS r
        FROM events WHERE event = 'hlswarm_trade_closed' ORDER BY timestamp DESC LIMIT 500""",
    "Cycles R&D (backtests)": """
        SELECT timestamp, properties.done AS outcome, properties.reason AS reason
        FROM events WHERE event = 'hlswarm_research_run' ORDER BY timestamp DESC LIMIT 100""",
}


def _req(method: str, url: str, key: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.loads(resp.read() or b"{}")


def main() -> int:
    key = os.getenv("POSTHOG_PERSONAL_API_KEY")
    pid = os.getenv("POSTHOG_PROJECT_ID")
    host = (os.getenv("POSTHOG_API_HOST") or "https://eu.posthog.com").rstrip("/")
    if not (key and pid):
        print("POSTHOG_PERSONAL_API_KEY and POSTHOG_PROJECT_ID are required", file=sys.stderr)
        return 2
    base = f"{host}/api/projects/{pid}"
    dash = _req("POST", f"{base}/dashboards/", key,
                {"name": "hl-swarm — Live Trading", "description": "Exécution, slippage, PnL, R&D"})
    for name, q in INSIGHTS.items():
        _req("POST", f"{base}/insights/", key, {
            "name": name, "dashboards": [dash["id"]],
            "query": {"kind": "DataVisualizationNode",
                      "source": {"kind": "HogQLQuery", "query": " ".join(q.split())}}})
        print("  +", name)
    print(f"dashboard created: {host}/project/{pid}/dashboard/{dash['id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
