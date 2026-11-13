# Contrôles de solidité — prime Coinbase (moyenne 7 jours > 0)

**Verdict : PASSE** — {'A_neighbours': True, 'B_coins': True, 'C_years': True, 'D_alpha': True}

Vérification 2024-01 → 2026-10 · marchés BTC, ETH, SOL

## A. Durées voisines (vérification)

| | trades | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|
| 5 jours | 111 | 8.43 | 2.6 | 0.98 | 2.24 | 0.405 |
| 6 jours | 84 | 9.27 | 1.89 | 1.11 | 2.92 | 0.464 |
| 7 jours | 85 | 7.73 | 2.89 | 0.92 | 2.26 | 0.412 |
| 8 jours | 92 | 1.72 | 3.54 | 0.22 | 1.25 | 0.348 |
| 9 jours | 97 | 2.38 | 3.29 | 0.3 | 1.34 | 0.361 |

## B. Chaque marché seul (vérification)

| | trades | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|
| BTC | 28 | 6.81 | 3.73 | 0.71 | 2.14 | 0.429 |
| ETH | 27 | 12.9 | 3.23 | 1.2 | 3.27 | 0.444 |
| SOL | 30 | 3.57 | 3.52 | 0.46 | 1.55 | 0.367 |

## C. Par année civile

| | trades | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|
| 2020 | 31 | 18.56 | 5.39 | 1.9 | 7.04 | 0.29 |
| 2021 | 22 | 7.91 | 3.01 | 2.02 | 4.47 | 0.409 |
| 2022 | 54 | -3.17 | 3.47 | -1.16 | 0.36 | 0.185 |
| 2023 | 27 | 6.8 | 2.53 | 1.58 | 4.34 | 0.444 |
| 2024 | 40 | 7.36 | 1.68 | 2.04 | 4.12 | 0.5 |
| 2025 | 39 | -0.09 | 2.82 | -0.01 | 0.99 | 0.256 |
| 2026 | 6 | 0.43 | 0.92 | 0.44 | 84.03 | 0.833 |

## D. Au-delà du marché (vérification)

- {'alpha_ann_pct': 1.88, 'beta': 0.028, 't_alpha': 1.34, 'days': 1035}

## Information

- lien avec le momentum : {'correlation': 0.58, 'sharpe_premium': 0.92, 'sharpe_momentum': 0.74, 'sharpe_50_50': 0.92, 'return_50_50_pct': 7.52, 'max_dd_50_50_pct': 3.01}
- coûts ×2 : {'trades': 85, 'return_pct': np.float64(7.45), 'cagr_pct': np.float64(2.57), 'max_dd_pct': 2.94, 'sharpe': 0.88, 'profit_factor': np.float64(2.19), 'win_rate': 0.4, 'avg_bars': 61.8}

## Effet du risque par trade (vérification)

| | trades | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|
| risk 0.5% | 85 | 7.73 | 2.89 | 0.92 | 2.26 | 0.412 |
| risk 2.0% | 85 | 31.46 | 10.97 | 0.91 | 2.25 | 0.412 |
| risk 4.0% | 85 | 63.56 | 20.58 | 0.91 | 2.24 | 0.412 |

