import numpy as np

from scripts.filter_research import DAY, H, above_sma, daily_flag_to_bars, fomc_allow, rising, _day_ms


def test_daily_flag_is_lagged_no_lookahead():
    t = np.array([0.0, DAY, 2 * DAY])
    flag = np.array([False, True, False])
    bars = np.array([DAY + 1, 2 * DAY + 1, 3 * DAY, 3 * DAY + 1, 4 * DAY])
    out = daily_flag_to_bars(bars, t, flag, lag_days=2)
    # la valeur du jour 1 (True) n'est visible qu'à partir du jour 3
    assert out.tolist() == [False, False, True, True, False]


def test_sma_and_rising():
    v = np.array([1.0, 2, 3, 2, 1, 5])
    assert above_sma(v, 3).tolist() == [False, False, True, False, False, True]
    assert rising(v, 2).tolist() == [False, False, True, False, False, True]


def test_fomc_blocks_window_only():
    dec = _day_ms("2024-01-31") + 19 * H
    bars = np.array([dec - 25 * H, dec - 24 * H, dec, dec + 5 * H, dec + 6 * H])
    assert fomc_allow(bars, 24).tolist() == [True, False, False, False, True]
