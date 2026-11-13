"""Paper trading multi-stratégies : un « livre » simulé par règle et par capital.

Chaque jour clôturé : le livre encaisse le rendement (prix − funding) des poids tenus,
puis se rééquilibre vers les poids cibles de sa règle, avec :
- frais taker + glissement sur chaque ordre ;
- la règle Hyperliquid des 10 $ minimum : un ordre d'ouverture ou d'augmentation plus
  petit est IGNORÉ (une clôture complète reste permise). Un livre à 50 $ montre donc
  ce qui serait réellement exécutable avec ce capital.
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

from lab.catalog import Spec, weights

MIN_ORDER_USD = 10.0


def iso(day_ms: float) -> str:
    return datetime.fromtimestamp(day_ms / 1000, timezone.utc).strftime("%Y-%m-%d")


def book_key(s: Spec, capital: float) -> str:
    return f"{s.name}@{capital:g}"


def step_books(state: dict, panel: dict, catalog: list[Spec], cost: float, capitals=(1000.0, 50.0)) -> list[str]:
    """Avance tous les livres jusqu'au dernier jour clôturé du panel. → journal lisible."""
    days, coins, R, F = panel["days"], panel["coins"], np.nan_to_num(panel["R"]), np.nan_to_num(panel["F"])
    books = state.setdefault("books", {})
    last = state.get("last_day")
    first_run = last is None
    todo = [len(days) - 1] if first_run else [i for i in range(len(days)) if days[i] > last]
    if not todo:
        return [f"aucun nouveau jour clôturé depuis le {iso(last)}"]
    log = []
    for s in catalog:
        W = weights(panel, s)
        for cap in capitals:
            bk = books.setdefault(book_key(s, cap), {"spec": s.name, "capital": cap, "equity": 1.0, "weights": {},
                                                    "history": [], "orders": 0, "skipped_orders": 0, "started": iso(days[todo[0]])})
            for i in todo:
                cur = np.array([bk["weights"].get(c, 0.0) for c in coins])
                pnl = 0.0 if first_run else float((cur * (R[i] - F[i])).sum())
                # marchés sortis du panel : on les considère clôturés sans gain ni perte
                bk["equity"] *= 1 + pnl
                target = W[i]
                delta = target - cur
                notional = np.abs(delta) * cap * bk["equity"]
                closing = (target == 0) & (cur != 0)
                wanted = np.abs(delta) > 1e-9
                allowed = wanted & ((notional >= MIN_ORDER_USD) | closing)
                new = np.where(allowed, target, cur)
                fee = cost * float(np.abs(new - cur).sum())
                bk["equity"] *= 1 - fee
                bk["orders"] += int(allowed.sum())
                bk["skipped_orders"] += int((wanted & ~allowed).sum())
                bk["weights"] = {c: round(float(w), 6) for c, w in zip(coins, new, strict=True) if abs(w) > 1e-9}
                if not first_run:
                    bk["history"].append([iso(days[i]), round(pnl - fee, 6)])
    state["last_day"] = float(days[todo[-1]])
    log.append(f"{len(todo)} jour(s) traité(s) jusqu'au {iso(days[todo[-1]])} — {len(books)} livres")
    return log


def book_stats(bk: dict) -> dict:
    r = np.array([x[1] for x in bk["history"]], dtype=float)
    if len(r) == 0:
        return {"days": 0, "return_pct": 0.0, "max_dd_pct": 0.0, "sharpe": None}
    eq = np.cumprod(1 + r)
    sd = r.std(ddof=1) if len(r) > 1 else 0.0
    return {"days": len(r), "return_pct": round(float(eq[-1] - 1) * 100, 2),
            "max_dd_pct": round(float((1 - eq / np.maximum.accumulate(np.maximum(eq, 1.0))).max()) * 100, 2),
            "sharpe": round(float(r.mean() / sd * np.sqrt(365)), 2) if sd > 0 and len(r) >= 14 else None}
