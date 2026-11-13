import numpy as np

from ml_engine.stats import deflated_sharpe, expected_max_sharpe, probabilistic_sharpe
from scripts.quant_research import backtest, hold_weights, pairs_weights, xs_weights


def test_xs_weights_are_dollar_neutral():
    sig = np.arange(20, dtype=float)
    sig[3] = np.nan
    w = xs_weights(sig)
    assert abs(w.sum()) < 1e-12 and abs(np.abs(w).sum() - 1) < 1e-12
    assert w[19] > 0 > w[0] and w[3] == 0
    assert not xs_weights(np.arange(5, dtype=float)).any()  # trop peu de marchés


def test_backtest_uses_yesterdays_weights_and_charges_turnover():
    W = np.array([[0.0, 0.0], [0.5, -0.5], [0.5, -0.5]])
    R = np.array([[0.0, 0.0], [0.10, 0.10], [0.02, -0.02]])
    pnl, turn, chg = backtest(W, R, np.zeros_like(R), cost=0.001)
    assert pnl[1] == 0.0                      # les poids du jour 1 ne gagnent rien le jour 1
    assert abs(pnl[2] - (0.02 - 0.001 * 1.0)) < 1e-12 and chg[1] == 2


def test_hold_and_pairs_run():
    rng = np.random.default_rng(0)
    C = 100 * np.exp(np.cumsum(rng.normal(0, 0.02, (200, 12)), axis=0))
    W = hold_weights(C[7:] / C[:-7] - 1, 7)
    assert (W[0] == W[6]).all()
    Wp = pairs_weights(C, 0, 1.5, 30)
    assert np.isfinite(Wp).all() and np.abs(Wp).sum() > 0


def test_luck_tests():
    rng = np.random.default_rng(1)
    good = rng.normal(0.002, 0.01, 1000)
    noise = rng.normal(0.0, 0.01, 1000)
    assert probabilistic_sharpe(good) > 0.99 > probabilistic_sharpe(noise)
    assert expected_max_sharpe(150, 0.001) > expected_max_sharpe(10, 0.001) > 0
    assert deflated_sharpe(good, 150, 0.0005) < probabilistic_sharpe(good)


def test_portfolio_math_bricks():
    from scripts.portfolio_math import beta_neutral, buffered_weights, ewma, inv_vol, rolling_beta, rolling_std
    rng = np.random.default_rng(3)
    mkt = rng.normal(0, 0.02, (300, 1))
    R = mkt * np.linspace(0.5, 2.0, 12) + rng.normal(0, 0.01, (300, 12))
    vol, beta = rolling_std(R, 30), rolling_beta(R, 0, 60)
    assert abs(beta[-1, 0] - 1) < 1e-9 and beta[-1, -1] > beta[-1, 1]
    W = np.tile(xs_weights(np.arange(12.0)), (300, 1))
    Wi = inv_vol(W, vol)
    assert abs(Wi[-1].sum()) < 1e-9 and abs(np.abs(Wi[-1]).sum() - 1) < 1e-9
    Wb = beta_neutral(W, beta)
    assert abs((Wb[-1] * beta[-1]).sum()) < abs((W[-1] * beta[-1]).sum())  # bêta net réduit
    assert abs(np.abs(Wb[-1]).sum() - 1) < 1e-9
    sig = np.cumsum(rng.normal(0, 1, (300, 12)), axis=0)
    turn_plain = np.abs(np.diff(hold_weights(sig, 7), axis=0)).sum()
    turn_buf = np.abs(np.diff(buffered_weights(sig, 7), axis=0)).sum()
    assert turn_buf < turn_plain
    assert abs(ewma(np.ones((200, 2)), 10)[-1, 0] - 1) < 1e-3


def test_uncertainty_tools():
    from ml_engine.stats import SPRTMonitor, kelly_leverage, ruin_stats, sharpe_ci, stationary_bootstrap, years_to_confirm
    rng = np.random.default_rng(5)
    r = rng.normal(0.001, 0.01, 800)
    assert stationary_bootstrap(r, 10, 50).shape == (10, 50)
    lo, hi = sharpe_ci(r, n_paths=300)
    assert lo < r.mean() / r.std() * np.sqrt(365) < hi
    safe, risky = ruin_stats(r, 150, 1.0, n_paths=500), ruin_stats(r, 150, 4.0, n_paths=500)
    assert risky["p_drawdown_over_limit"] >= safe["p_drawdown_over_limit"]
    assert abs(kelly_leverage(r) - r.mean() / r.var(ddof=1)) < 1e-9
    assert abs(years_to_confirm(1.645) - 1) < 1e-3 and years_to_confirm(0.5) > years_to_confirm(2)
    good, bad = SPRTMonitor(1.5, 0.01), SPRTMonitor(1.5, 0.01)
    out_g = [good.update(x) for x in rng.normal(1.5 / np.sqrt(365) * 0.01, 0.01, 4000)]
    out_b = [bad.update(x) for x in rng.normal(-0.0005, 0.01, 4000)]
    assert "confirmed" in out_g and "rejected" in out_b
