import numpy as np

from lab import governor, hl_data, paper
from lab.catalog import DAY_MS, default_catalog, spec, weights
from lab.research import scorecard


def _panel(T=400, N=14, seed=0, start_day=19_000):
    rng = np.random.default_rng(seed)
    R = rng.normal(0.0005, 0.03, (T, N))
    C = 100 * np.exp(np.cumsum(R, axis=0))
    R = np.vstack([np.full((1, N), np.nan), C[1:] / C[:-1] - 1])
    F = rng.normal(0.0002, 0.0003, (T, N))
    return {"coins": [f"C{j}" for j in range(N)], "days": (start_day + np.arange(T)) * float(DAY_MS), "C": C, "F": F, "R": R}


def test_catalog_names_unique_and_weights_sane():
    cat = default_catalog()
    assert len({s.name for s in cat}) == len(cat) >= 15
    p = _panel()
    for s in cat:
        W = weights(p, s)
        assert np.isfinite(W).all() and np.abs(W).sum(axis=1).max() <= 1 + 1e-9
        if s.family != "trend":
            assert abs(W[-1].sum()) < 1e-9  # long/short : exposition nette nulle
    weekly = weights(p, spec("carry", carry=7, hold=7, k=3))
    idx = (p["days"] // DAY_MS).astype(int)
    changes = np.flatnonzero(np.abs(np.diff(weekly, axis=0)).sum(axis=1) > 0) + 1
    assert all(idx[c] % 7 == 0 for c in changes[1:])  # rééquilibrages calés sur le calendrier


def test_weights_do_not_look_ahead():
    p = _panel()
    s = spec("blend", w=0.5, mom=14, carry=7, hold=1, k=0)
    W1 = weights(p, s)
    q = {**p, "C": p["C"].copy(), "F": p["F"].copy()}
    q["C"][300:] *= 1.5
    q["F"][300:] += 0.01
    assert np.allclose(W1[:300], weights(q, s)[:300])


def test_paper_books_respect_min_order_and_accrue_pnl():
    p = _panel()
    cat = [spec("blend", w=0.5, mom=14, carry=7, hold=1, k=3), spec("blend", w=0.5, mom=14, carry=7, hold=1, k=0)]
    state: dict = {}
    first = {**p, **{k: p[k][:390] for k in ("days", "C", "F", "R")}}
    paper.step_books(state, first, cat, cost=0.00065)
    assert all(not b["history"] for b in state["books"].values())      # premier passage : positions prises, pas de PnL
    paper.step_books(state, p, cat, cost=0.00065)
    big, small = state["books"][paper.book_key(cat[0], 1000.0)], state["books"][paper.book_key(cat[1], 50.0)]
    assert len(big["history"]) == 10 and big["orders"] > 0
    # 50 $ répartis sur ~2×2 marchés à 20 % d'un univers de 14 → 12,5 $ : passe ; un quintile plus large ne passerait pas
    tiny = {"books": {}}
    wide = _panel(N=40)
    paper.step_books(tiny, wide, [spec("carry", carry=7, hold=1, k=0)], cost=0.00065, capitals=(50.0,))
    bk = next(iter(tiny["books"].values()))
    assert bk["orders"] == 0 and bk["skipped_orders"] > 0 and not bk["weights"]   # 50 $ / 16 positions < 10 $
    assert small["capital"] == 50.0


def test_scorecard_and_governor_flow():
    p = _panel(T=900)
    cat = default_catalog()[:6]
    sc = scorecard(p, cat, 0.00065, p["days"][500], p["days"][800])
    assert set(sc["rules"]) == {s.name for s in cat}
    row = next(iter(sc["rules"].values()))
    assert {"pre", "post", "clean", "gate", "deflated_sharpe", "post_sharpe_ci95"} <= set(row)
    for r in sc["rules"].values():
        r["gate"] = True
    state: dict = {}
    paper.step_books(state, {**p, **{k: p[k][:860] for k in ("days", "C", "F", "R")}}, cat, 0.00065)
    d1 = governor.decide(state, sc, paper.book_stats, "2026-01-01")
    assert state["champion"]["provisional"] and any("PROVISOIRE" in x for x in d1)
    paper.step_books(state, p, cat, 0.00065)
    governor.decide(state, sc, paper.book_stats, "2026-02-15")
    assert state["champion"] and not state["champion"]["provisional"]
    # une règle dont le livre s'effondre est suspendue et ne peut plus être championne
    name = state["champion"]["name"]
    state["books"][f"{name}@1000"]["history"] += [["x", -0.1]] * 5
    d3 = governor.decide(state, sc, paper.book_stats, "2026-03-20")
    assert state["status"][name]["state"] == "suspended" and any("SUSPENSION" in x for x in d3)
    assert state["champion"] is None or state["champion"]["name"] != name
    assert governor.decide({"books": state["books"]}, None, paper.book_stats, "2026-03-21")[-1].endswith("aucun champion désigné")


def test_hl_panel_parsing_with_fake_api():
    now = 20_000 * DAY_MS + 5 * 3_600_000
    last = 19_999 * DAY_MS

    def fake(body):
        if body["type"] == "candleSnapshot":
            if body["req"]["coin"] == "GONE":
                return []
            s = body["req"]["startTime"]
            rows = [{"t": s + i * DAY_MS, "c": str(100 + i)} for i in range(40)]
            return rows + [{"t": now // DAY_MS * DAY_MS, "c": "999"}]      # bougie du jour en cours : ignorée
        return [{"time": last + 3_600_000 * h, "fundingRate": "0.0001"} for h in range(24)]
    p = hl_data.fetch_panel(["AAA", "GONE", "BBB"], lookback_days=40, now_ms=now, post=fake, pause_s=0)
    assert p["coins"] == ["AAA", "BBB"] and p["C"].shape == (40, 2)
    assert p["days"][-1] == last and p["C"][-1, 0] == 139
    assert abs(p["F"][-1, 0] - 0.0024) < 1e-12 and p["F"][:-1].sum() == 0


def test_paper_step_is_idempotent_without_new_day():
    p = _panel()
    cat = [spec("carry", carry=7, hold=1, k=3)]
    state: dict = {}
    paper.step_books(state, {**p, **{k: p[k][:399] for k in ("days", "C", "F", "R")}}, cat, 0.00065)
    paper.step_books(state, p, cat, 0.00065)
    snap = {k: (b["equity"], len(b["history"])) for k, b in state["books"].items()}
    out = paper.step_books(state, p, cat, 0.00065)
    assert "aucun nouveau jour" in out[0]
    assert snap == {k: (b["equity"], len(b["history"])) for k, b in state["books"].items()}
