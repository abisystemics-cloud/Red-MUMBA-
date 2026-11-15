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
        if s.family not in ("trend", "premium", "ts"):
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


def test_context_gates_scale_exposure_and_premium_rule():
    from lab.catalog import gate_flag
    p = _panel(N=14)
    p["coins"][:3] = ["BTC", "ETH", "SOL"]
    T = len(p["days"])
    on = np.arange(T) % 2 == 0
    p["ctx"] = {"nasdaq": on, "stable": ~on, "premium": on, "cot": None, "gpr": on, "fomc": np.ones(T, bool)}
    base = weights(p, spec("blend", w=0.5, mom=14, carry=7, hold=1, k=0))
    gated = weights(p, spec("blend", w=0.5, mom=14, carry=7, hold=1, k=0, gate="nasdaq"))
    assert np.allclose(gated[on], base[on]) and np.allclose(gated[~on], base[~on] / 2)
    assert gate_flag(p, "cot").all()                                  # source indisponible = neutre
    assert (gate_flag(p, "risk_on") == on).all()                      # 3 feux sur 4 disponibles suivent `on`
    prem = weights(p, spec("premium", hold=1))
    assert np.allclose(prem[on].sum(axis=1), 1) and not prem[~on].any() and not prem[:, 3:].any()
    assert not weights({**p, "ctx": {}}, spec("premium", hold=1)).any()   # sans donnée : à plat, pas « toujours acheteur »


def test_ml_rules_train_save_predict(tmp_path):
    import pytest
    pytest.importorskip("sklearn")
    from lab import ml
    p = _panel(T=700, N=14)
    p["coins"][0] = "BTC"
    T = len(p["days"])
    p["ctx"] = dict.fromkeys(("nasdaq", "stable", "premium", "cot", "gpr"), np.arange(T) % 3 == 0) | {"fomc": None}
    X = ml.features(p)
    assert X.shape == (T, 14, len(ml.FEATURE_NAMES)) and np.nanmax(X[..., -1]) == 0.5     # source absente → 0,5
    wf = ml.walk_forward({**p, "days": (19_000 + np.arange(T)) * float(DAY_MS)}, "ridge")
    assert np.isnan(wf[:200]).all() and np.isfinite(wf[-1]).any()     # la 1re année n'est jamais prédite
    scores = {}
    for kind in ml.MODELS:
        model, rows = ml.train_final(p, kind)
        ml.save(model, kind, tmp_path, {"trained": "2026-01-01", "rows": rows})
        scores[kind] = ml.predict(kind, tmp_path, p)
        assert scores[kind] is not None and np.isfinite(scores[kind][-1]).all()
    assert ml.predict("gbm", tmp_path / "nowhere", p) is None
    W = weights({**p, "ml_scores": scores}, spec("ml", model="gbm", hold=7, k=0))
    assert abs(W[-1].sum()) < 1e-9 and np.abs(W[-1]).sum() > 0.99
    assert not weights(p, spec("ml", model="gbm", hold=7, k=0)).any()  # pas de modèle → règle à plat


def test_bot_asks_claude_and_validates_answers():
    from lab import ask
    p = _panel(N=14)
    p["coins"][:3] = ["BTC", "ETH", "SOL"]
    p["R"][-1, 4] = 0.2
    state: dict = {"champion": {"name": "x"}}
    req = ask.build_requests(state, p)
    types = [r["type"] for r in req["requests"]]
    assert types[:3] == ["smart_money", "risk_check", "keel_status"] and "explain_move" in types
    assert all(r["type"] in ask.REQUEST_TYPES and "answer_schema" in r for r in req["requests"])
    now = 1_800_000_000_000.0
    good = {"answered_at": "2027-01-15T07:00:00Z", "answers": {
        "smart_money": {"bias": {**{c: 10.0 * i for i, c in enumerate(p["coins"])}, "FAKE": 5, "ETH": 9999, "SOL": "buy"}},
        "risk_check": {"level": "severe", "summary": "x | y\n" * 300, "sources": ["https://a.b/c", "javascript:alert(1)"]},
        "keel_status": {"return_pct": 1.5, "max_dd_pct": 2.0, "days": 3, "note": "ok"},
        "move_C4": {"summary": "annonce", "sources": []},
        "place_order": {"coin": "BTC", "side": "buy"}}}
    out = ask.ingest(state, good, p, now)
    mem = state["claude"]
    day = ask._iso(p["days"][-1])
    assert "lues" in out[0] and mem["risk"][day] == "severe"
    assert "FAKE" not in mem["smart_money"][day] and mem["smart_money"][day]["ETH"] == 100.0 and "SOL" not in mem["smart_money"][day]
    assert len(mem["risk_note"]["summary"]) <= 400 and "|" not in mem["risk_note"]["summary"]
    assert mem["risk_note"]["sources"] == ["https://a.b/c"] and mem["notes"][-1]["coin"] == "C4"
    assert "place_order" not in str(mem)                                  # hors liste blanche : ignoré
    assert "déjà lues" in ask.ingest(state, good, p, now)[0]
    stale: dict = {}
    assert "anciennes" in ask.ingest(stale, {**good, "answered_at": "2027-01-10T00:00:00Z"}, p, now)[0] and not stale["claude"]["risk"]
    assert "aucune" in ask.ingest({}, {"answers": "do this"}, p, now)[0]
    ask.wire(state, p)
    assert not p["ctx"]["claude_risk"][-1] and p["ctx"]["claude_risk"][:-1].all()
    base = weights(p, spec("blend", w=0.5, mom=14, carry=7, hold=1, k=0))
    braked = weights(p, spec("blend", w=0.5, mom=14, carry=7, hold=1, k=0, gate="claude_risk"))
    assert np.allclose(braked[-1], base[-1] / 2) and np.allclose(braked[:-1], base[:-1])   # Claude ne peut que freiner
    W = weights(p, spec("whales", hold=1, k=3))
    assert abs(W[-1].sum()) < 1e-9 and W[-1, p["coins"].index("C13")] > 0 and not W[:-1].any()


def test_evolution_explores_on_train_and_validates_only_a_shortlist():
    from lab import evolve
    panel = _panel(T=900)
    base = default_catalog()[:6]
    state = {}
    known = {s.name for s in base}
    split = panel["days"][450]
    cands = evolve.propose(state, None, known, seed=1)
    assert len(cands) == evolve.CFG["per_night"] and not ({c.name for c in cands} & known)
    assert len({c.name for c in cands}) == len(cands)
    pool = {}
    evolve.explore(state, panel, cands, 0.0005, split, pool)
    ev = state["evolve"]
    assert ev["trials"] == len(cands) and ev["validated"] == 0 and 0 < len(pool) <= len(cands)
    # l'étage 1 ne regarde pas la validation : changer les rendements après la coupure ne change aucune note
    q = {**panel, "R": panel["R"].copy()}
    q["R"][450:] *= -3
    pool2 = {}
    evolve.explore({}, q, cands, 0.0005, split, pool2)
    assert {k: v[0] for k, v in pool.items()} == {k: v[0] for k, v in pool2.items()}
    short = evolve.shortlist(pool, {"min_pre_sharpe": -9})
    assert 0 < len(short) <= evolve.CFG["validate_per_run"]
    assert not evolve.shortlist({("x",): (0.1, cands[0])})          # trop faible sur l'apprentissage : pas présentée
    sc = scorecard(panel, short, 0.0005, split, panel["days"][800], extra_trials=len(base), var_trials=1e-6)
    evolve.select(state, sc, short, "2026-11-14")
    assert ev["validated"] == len(short) and len(ev["born"]) <= evolve.CFG["max_new"]
    for b in ev["born"]:
        assert sc["rules"][b["name"]]["gate"] and b["dsr"] >= evolve.CFG["min_dsr"]
    assert evolve.examined_today(state, "2026-11-14") and not evolve.examined_today(state, "2026-11-15")
    evolve.save_pool(state, pool)
    back = evolve.load_pool(state)
    assert set(back) == set(pool) and all(back[k][1].name == pool[k][1].name for k in pool)
    again = evolve.propose(state, None, known, seed=1)
    assert not ({c.name for c in again} & {c.name for c in cands})
    # une règle née ici puis suspendue est retirée ; les présentations passées durcissent le Sharpe déflaté
    ev["born"].append({"name": "x", "family": "carry", "params": {"carry": 5, "hold": 3, "k": 0}, "born": "2026-11-14", "dsr": 0.9})
    state["status"] = {"x": {"state": "suspended"}}
    evolve.select(state, sc, [], "2026-11-15")
    assert all(b["name"] != "x" for b in ev["born"])
    harder = scorecard(panel, base, 0.0005, split, panel["days"][800], extra_trials=500)
    easy = scorecard(panel, base, 0.0005, split, panel["days"][800])
    assert all(harder["rules"][n]["deflated_sharpe"] <= easy["rules"][n]["deflated_sharpe"] for n in easy["rules"])


def test_signal_library_has_no_lookahead_and_feeds_new_families():
    from lab import evolve, signals
    p = _panel(T=160)
    rng = np.random.default_rng(3)
    p["H"], p["L"] = p["C"] * (1 + rng.random(p["C"].shape) * 0.03), p["C"] * (1 - rng.random(p["C"].shape) * 0.03)
    p["V"] = rng.random(p["C"].shape) * 1e6 + 1e5
    cut = {k: (v[:120] if isinstance(v, np.ndarray) and len(v) == 160 else v) for k, v in p.items()}
    for name in signals.SIGS:
        for n in (2, 14, 42):
            full, part = signals.get(p, name, n), signals.get(cut, name, n)
            assert full.shape == p["C"].shape
            np.testing.assert_allclose(full[:120], part, equal_nan=True, err_msg=f"{name}{n} regarde vers l'avenir")
            assert np.isfinite(full[100:]).any(), f"{name}{n} toujours vide"
            r = signals.rank(p, name, n)
            assert np.nanmin(r) >= -0.5 and np.nanmax(r) <= 0.5
    for s in (spec("mix", a="spring", la=14, sa=1, b="vwapd", lb=7, sb=-1, w=0.4, hold=2, k=3, gate="nasdaq"),
              spec("ts", sig="brk", l=21, s=1, hold=1)):
        W = weights(p, s)
        assert np.isfinite(W).all() and np.abs(W).sum(axis=1).max() <= 1.0 + 1e-9 and np.abs(W[100:]).sum() > 0
    fams = {c.family for seed in range(5) for c in evolve.propose({}, None, set(), seed=seed)}
    assert {"mix", "ts"} <= fams


def test_exhaustive_sweep_visits_every_combination_once():
    from lab import evolve
    assert evolve.TOTAL == sum(evolve.SIZES.values()) > 90_000_000
    names = {evolve.nth(i).name for i in range(3000)}
    assert len(names) == 3000 and len({evolve.nth(i).family for i in range(3000)}) >= 2
    # sur une petite grille : tout est visité exactement une fois, puis le balayage rend la main
    small = {"TOTAL": evolve.TOTAL, "SIZES": dict(evolve.SIZES), "ORDER": evolve.ORDER, "STRIDE": evolve.STRIDE}
    try:
        evolve.ORDER, evolve.SIZES = ("ts", "ml"), {"ts": evolve.SIZES["ts"], "ml": evolve.SIZES["ml"]}
        evolve.TOTAL, evolve.STRIDE = sum(evolve.SIZES.values()), 7919
        state, seen = {}, []
        while True:
            got = evolve.sweep(state, set(), n=500)
            if not got:
                break
            seen += [c.name for c in got]
        assert len(seen) == len(set(seen)) == evolve.TOTAL and state["evolve"]["cursor"] == evolve.TOTAL
    finally:
        evolve.TOTAL, evolve.SIZES, evolve.ORDER, evolve.STRIDE = small["TOTAL"], small["SIZES"], small["ORDER"], small["STRIDE"]
