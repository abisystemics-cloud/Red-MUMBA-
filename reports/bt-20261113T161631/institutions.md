# Suivre les institutions et la géopolitique — tests

Apprentissage 2020-01 → 2023-12 · vérification 2024-01 → 2026-10 · BTC, ETH, SOL

Sources : {'cot_weeks': 448, 'coinbase_days': 2711, 'premium_days': 2710, 'gpr_days': 15281}

| signal | comme filtre du momentum | seul |
|---|---|---|
| cot_asset_managers | **N'AIDE PAS** {'net_rising_weeks': 4} | **NE TIENT PAS** {'net_rising_weeks': 2} |
| coinbase_premium | **N'AIDE PAS** {'mean_days': 3} | **TIENT** {'mean_days': 7} |
| geopolitical_risk | **N'AIDE PAS** {'max_ratio_vs_1y': 1.25} | **non testé seul**  |

## Comme filtre du momentum

| réglage | période | trades | signal_on_pct | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|---|---|
| momentum seul | train | 697 | 100.0 | 26.0 | 4.83 | 1.55 | 1.83 | 0.314 |
| momentum seul | test | 541 | 100.0 | 7.25 | 3.51 | 0.74 | 1.37 | 0.301 |
| cot_asset_managers {'net_rising_weeks': 2} | train | 433 | 55.5 | 8.06 | 4.98 | 0.74 | 1.45 | 0.307 |
| cot_asset_managers {'net_rising_weeks': 2} | test | 280 | 45.8 | 2.1 | 3.11 | 0.34 | 1.21 | 0.289 |
| cot_asset_managers {'net_rising_weeks': 4} | train | 408 | 55.6 | 19.94 | 3.61 | 1.43 | 2.0 | 0.299 |
| cot_asset_managers {'net_rising_weeks': 4} | test | 270 | 43.1 | 2.01 | 3.15 | 0.33 | 1.2 | 0.289 |
| cot_asset_managers {'net_rising_weeks': 8} | train | 411 | 57.8 | 14.21 | 4.15 | 1.09 | 1.7 | 0.294 |
| cot_asset_managers {'net_rising_weeks': 8} | test | 261 | 45.1 | -0.58 | 5.42 | -0.08 | 0.96 | 0.226 |
| coinbase_premium {'mean_days': 3} | train | 582 | 77.3 | 20.36 | 3.86 | 1.36 | 1.75 | 0.323 |
| coinbase_premium {'mean_days': 3} | test | 285 | 43.9 | 4.74 | 2.85 | 0.66 | 1.44 | 0.323 |
| coinbase_premium {'mean_days': 7} | train | 582 | 79.7 | 17.89 | 5.07 | 1.25 | 1.68 | 0.323 |
| coinbase_premium {'mean_days': 7} | test | 246 | 42.5 | 5.7 | 2.28 | 0.81 | 1.67 | 0.333 |
| coinbase_premium {'mean_days': 14} | train | 587 | 81.0 | 16.27 | 5.26 | 1.17 | 1.61 | 0.31 |
| coinbase_premium {'mean_days': 14} | test | 238 | 43.2 | 1.89 | 3.79 | 0.32 | 1.23 | 0.294 |
| geopolitical_risk {'max_ratio_vs_1y': 1.25} | train | 582 | 82.1 | 19.08 | 5.1 | 1.26 | 1.71 | 0.302 |
| geopolitical_risk {'max_ratio_vs_1y': 1.25} | test | 461 | 81.4 | 5.34 | 3.9 | 0.59 | 1.29 | 0.304 |
| geopolitical_risk {'max_ratio_vs_1y': 1.5} | train | 641 | 89.6 | 18.65 | 5.77 | 1.22 | 1.63 | 0.306 |
| geopolitical_risk {'max_ratio_vs_1y': 1.5} | test | 504 | 92.8 | 6.78 | 3.94 | 0.71 | 1.36 | 0.302 |
| geopolitical_risk {'max_ratio_vs_1y': 2.0} | train | 676 | 94.9 | 18.56 | 6.64 | 1.2 | 1.6 | 0.305 |
| geopolitical_risk {'max_ratio_vs_1y': 2.0} | test | 532 | 98.0 | 7.02 | 3.51 | 0.72 | 1.36 | 0.299 |

## Signal seul

| réglage | période | trades | signal_on_pct | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|---|---|
| cot_asset_managers {'net_rising_weeks': 2} | train | 184 | 55.5 | 16.59 | 6.63 | 1.01 | 2.05 | 0.391 |
| cot_asset_managers {'net_rising_weeks': 2} | test | 120 | 45.8 | 0.14 | 3.51 | 0.03 | 1.02 | 0.392 |
| cot_asset_managers {'net_rising_weeks': 4} | train | 154 | 55.6 | 14.8 | 8.36 | 0.96 | 1.93 | 0.325 |
| cot_asset_managers {'net_rising_weeks': 4} | test | 111 | 43.1 | -0.24 | 4.92 | -0.01 | 0.98 | 0.369 |
| cot_asset_managers {'net_rising_weeks': 8} | train | 139 | 57.8 | 9.91 | 7.32 | 0.63 | 1.63 | 0.317 |
| cot_asset_managers {'net_rising_weeks': 8} | test | 91 | 45.1 | -2.5 | 6.6 | -0.29 | 0.76 | 0.297 |
| coinbase_premium {'mean_days': 3} | train | 251 | 77.3 | 21.63 | 6.03 | 0.96 | 2.01 | 0.382 |
| coinbase_premium {'mean_days': 3} | test | 150 | 43.9 | 8.85 | 2.95 | 1.03 | 1.98 | 0.427 |
| coinbase_premium {'mean_days': 7} | train | 128 | 79.7 | 32.72 | 5.39 | 1.29 | 3.51 | 0.312 |
| coinbase_premium {'mean_days': 7} | test | 85 | 42.5 | 7.73 | 2.89 | 0.92 | 2.26 | 0.412 |
| coinbase_premium {'mean_days': 14} | train | 81 | 81.0 | 116.36 | 43.36 | 0.81 | 11.55 | 0.235 |
| coinbase_premium {'mean_days': 14} | test | 80 | 43.2 | 1.35 | 4.21 | 0.17 | 1.21 | 0.35 |
