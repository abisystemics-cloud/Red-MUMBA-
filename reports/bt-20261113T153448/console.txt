# Contrôles de solidité — momentum 6 h (L=28, long seulement)

**Verdict : PASSE** — {'A_neighbours': np.True_, 'B_coins': True, 'C_years': np.True_, 'D_alpha': True}

Vérification 2024-01 → 2026-10 · marchés BTC, ETH, SOL

## A. Durées voisines (vérification)

| | trades | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|
| L=20 long | 672 | 6.73 | 4.32 | 0.69 | 1.29 | 0.307 |
| L=20 long/short | 1043 | 7.77 | 4.42 | 0.66 | 1.2 | 0.326 |
| L=24 long | 608 | 8.31 | 3.47 | 0.85 | 1.38 | 0.334 |
| L=24 long/short | 936 | 9.88 | 4.26 | 0.83 | 1.28 | 0.317 |
| L=28 long | 541 | 7.25 | 3.51 | 0.74 | 1.37 | 0.301 |
| L=28 long/short | 837 | 8.77 | 3.34 | 0.74 | 1.26 | 0.321 |
| L=32 long | 512 | 8.0 | 3.46 | 0.83 | 1.42 | 0.342 |
| L=32 long/short | 798 | 10.12 | 2.79 | 0.84 | 1.32 | 0.342 |
| L=36 long | 484 | 6.74 | 3.98 | 0.71 | 1.38 | 0.314 |
| L=36 long/short | 767 | 5.43 | 3.58 | 0.49 | 1.18 | 0.319 |

## B. Chaque marché seul (vérification)

| | trades | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|
| BTC | 183 | 5.41 | 4.34 | 0.51 | 1.28 | 0.311 |
| ETH | 180 | 7.63 | 5.43 | 0.62 | 1.36 | 0.306 |
| SOL | 178 | 8.53 | 3.79 | 0.75 | 1.49 | 0.287 |

## C. Par année civile

| | trades | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|
| 2020 | 131 | 11.8 | 1.91 | 2.34 | 2.94 | 0.374 |
| 2021 | 203 | 5.39 | 1.94 | 1.73 | 1.74 | 0.365 |
| 2022 | 190 | -2.93 | 3.85 | -1.28 | 0.55 | 0.247 |
| 2023 | 176 | 9.81 | 3.15 | 2.27 | 2.49 | 0.29 |
| 2024 | 177 | 3.2 | 2.82 | 0.98 | 1.46 | 0.249 |
| 2025 | 207 | 0.97 | 2.62 | 0.34 | 1.15 | 0.353 |
| 2026 | 159 | 2.93 | 1.93 | 0.88 | 1.56 | 0.296 |

## D. Au-delà du marché (vérification)

- long seulement : {'alpha_ann_pct': 1.5, 'beta': 0.037, 't_alpha': 0.97, 'days': 1035}
- long/short : {'alpha_ann_pct': 3.07, 'beta': -0.001, 't_alpha': 1.25, 'days': 1035}
- marché acheteur équipondéré : {'return_pct': np.float64(32.3), 'max_dd_pct': np.float64(64.3)}

## Information : effet du risque par trade (vérification)

| | trades | return_pct | max_dd_pct | sharpe | profit_factor | win_rate |
|---|---|---|---|---|---|---|
| risk 0.5% | 541 | 7.25 | 3.51 | 0.74 | 1.37 | 0.301 |
| risk 2.0% | 541 | 28.38 | 13.39 | 0.73 | 1.37 | 0.301 |
| risk 4.0% | 541 | 53.46 | 25.13 | 0.71 | 1.36 | 0.301 |

