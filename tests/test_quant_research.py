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
