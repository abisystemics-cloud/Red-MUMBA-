# Filtres fondamentaux sur le momentum 6 h (L=28, long seulement)

Apprentissage 2020-01 → 2023-12 · vérification 2024-01 → 2026-10 · BTC, ETH, SOL

Sources : {'nasdaq_days': 0, 'stablecoin_days': 3272, 'fomc_dates': 57}

| filtre | réglage choisi | verdict |
|---|---|---|
| macro | None | **DONNÉES INDISPONIBLES** |
| stablecoins | {'rising_days': 30} | **N'AIDE PAS** |
| fomc | {'no_entry_hours_before': 24} | **N'AIDE PAS** |

| réglage | période | trades | allowed_pct | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|---|---|
| momentum seul | train | 697 | 100.0 | 26.0 | 4.83 | 1.55 | 1.83 | 0.314 |
| momentum seul | test | 541 | 100.0 | 7.25 | 3.51 | 0.74 | 1.37 | 0.301 |
| stablecoins {'rising_days': 7} | train | 512 | 65.3 | 20.37 | 4.23 | 1.44 | 1.86 | 0.334 |
| stablecoins {'rising_days': 7} | test | 444 | 71.9 | 6.86 | 3.27 | 0.74 | 1.41 | 0.302 |
| stablecoins {'rising_days': 14} | train | 495 | 65.5 | 20.19 | 4.67 | 1.44 | 1.87 | 0.333 |
| stablecoins {'rising_days': 14} | test | 440 | 76.4 | 7.55 | 3.45 | 0.8 | 1.46 | 0.305 |
| stablecoins {'rising_days': 30} | train | 441 | 62.0 | 21.77 | 2.82 | 1.58 | 2.11 | 0.356 |
| stablecoins {'rising_days': 30} | test | 457 | 83.6 | 4.12 | 2.95 | 0.51 | 1.25 | 0.304 |
| fomc {'no_entry_hours_before': 24} | train | 690 | 97.2 | 26.13 | 4.8 | 1.56 | 1.84 | 0.316 |
| fomc {'no_entry_hours_before': 24} | test | 532 | 97.2 | 6.51 | 3.42 | 0.68 | 1.34 | 0.297 |
| fomc {'no_entry_hours_before': 48} | train | 679 | 94.9 | 24.4 | 4.87 | 1.49 | 1.78 | 0.314 |
| fomc {'no_entry_hours_before': 48} | test | 522 | 95.0 | 6.56 | 3.42 | 0.68 | 1.34 | 0.301 |
| fomc {'no_entry_hours_before': 72} | train | 671 | 92.7 | 24.3 | 4.77 | 1.49 | 1.79 | 0.313 |
| fomc {'no_entry_hours_before': 72} | test | 505 | 92.8 | 7.15 | 3.49 | 0.74 | 1.39 | 0.299 |
