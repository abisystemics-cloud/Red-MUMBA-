import numpy as np

from scripts.bar_research import (Bars, Costs, Entry, Strategy, funding_fade, resample, simulate, spring,
                                  summarize, tsmom, vwap_rotation, vwap_trend)

H = 3_600_000


def _bars(n=3000, seed=0, step=15 * 60_000):
    rng = np.random.default_rng(seed)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.003, n)))
    o = np.concatenate([[100], c[:-1]])
    h = np.maximum(o, c) * (1 + abs(rng.normal(0, 0.001, n)))
    lo = np.minimum(o, c) * (1 - abs(rng.normal(0, 0.001, n)))
    v = rng.uniform(1, 3, n)
    ts = 1_600_000_000_000 + np.arange(n) * step
    return Bars(ts.astype(float), o, h, lo, c, v, v * rng.uniform(0.3, 0.7, n))


def test_resample_preserves_ohlc():
    b = _bars(96)
    r = resample(b, H)
    assert len(r) in (24, 25)
    assert r.h.max() == b.h.max() and r.l.min() == b.l.min() and abs(r.v.sum() - b.v.sum()) < 1e-9


def test_stop_hit_and_costs():
    b = _bars(10)
    b.o[:] = 100
    b.c[:] = 100
    b.h[:] = 100.5
    b.l[:] = 99.5
    b.l[5] = 98.0  # le stop à 99 est touché dans la bougie 5
    fired = [False]

    def entry(i):
        if not fired[0]:
            fired[0] = True
            return Entry(+1, 99.0, None)
        return None
    res = simulate(b, Strategy(entry, warmup=1), Costs(), np.array([]), np.array([]), risk_pct=0.5)
    t = res["trades"][0]
    assert t["why"] == "stop"
    # perte au stop ≈ risque (0.5 %) + coûts sur un levier de 0.5
    assert -0.0060 < t["ret"] < -0.0050


def test_strategies_run_on_random_walk_without_crashing():
    b15 = _bars(6000)
    b30, b1h, b6h = resample(b15, H // 2), resample(b15, H), resample(b15, 6 * H)
    ft = b1h.ts[::8] + H / 2
    fr = np.random.default_rng(1).normal(1e-4, 1e-4, len(ft))
    for bars, st in ((b30, vwap_rotation(b30, 1.0, 1.0)), (b30, vwap_trend(b30, 0.5, 1.0)),
                     (b1h, spring(b1h, 24, 12.0, "mid")), (b6h, tsmom(b6h, 4, False)),
                     (b1h, funding_fade(b1h, ft, fr, 2.0, 24))):
        res = simulate(bars, st, Costs(), ft, fr)
        s = summarize({"X": res})
        assert s["max_dd_pct"] >= 0 and np.isfinite(s["return_pct"])


def test_universe_strategies_and_prev_windows():
    from scripts.universe_research import breakout, prev_max, prev_median, reversal
    x = np.array([1.0, 3, 2, 5, 4])
    assert np.isnan(prev_max(x, 2)[1]) and prev_max(x, 2)[2:].tolist() == [3.0, 3.0, 5.0]  # fenêtre AVANT la bougie
    assert prev_median(x, 3)[3:].tolist() == [2.0, 3.0]
    b = resample(_bars(8000), H)
    for st in (breakout(b, 24), reversal(b, 2.0, 4)):
        s = summarize({"X": simulate(b, st, Costs(), np.array([]), np.array([]))})
        assert np.isfinite(s["return_pct"])
