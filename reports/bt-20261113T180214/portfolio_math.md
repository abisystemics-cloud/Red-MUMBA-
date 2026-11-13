# Couche mathématique sur la stratégie momentum + funding

Apprentissage 2020-01 → 2023-12 · vérification 2024-01 → 2026-10 · 30 marchés · exposition 1×

| version | appr. Sharpe | appr. rendement % | appr. baisse % | vérif. Sharpe | vérif. rendement % | vérif. baisse % | ordres/mois | vérif. Sharpe coûts ×2 |
|---|---|---|---|---|---|---|---|---|
| référence | 1.07 | 235.1 | 37.9 | 1.53 | 152.0 | 13.1 | 54.0 | 1.37 |
| inv_vol — **ÉCARTÉE** | 1.18 | 258.5 | 35.8 | 1.6 | 162.6 | 13.4 | 391.0 | 1.41 |
| beta_neutral — **ÉCARTÉE** | 0.64 | 91.4 | 46.8 | 1.57 | 162.2 | 16.4 | 391.0 | 1.4 |
| vol_target — **ÉCARTÉE** | 1.16 | 221.3 | 28.5 | 1.51 | 203.7 | 19.3 | 362.0 | 1.31 |
| ewma_carry — **ÉCARTÉE** | 1.07 | 241.1 | 28.5 | 1.12 | 90.3 | 14.5 | 45.0 | 0.98 |
| buffer — **ÉCARTÉE** | 1.41 | 446.0 | 28.1 | 1.47 | 139.3 | 15.4 | 37.0 | 1.35 |
| **version finale** (aucune brique) | 1.07 | 235.1 | 37.9 | 1.53 | 152.0 | 13.1 | 54.0 | 1.37 |

## Validation

- intervalle de confiance du Sharpe (vérification) : {'référence': {'sharpe': 1.53, 'sharpe_ci95': [0.45, 2.66], 'prob_true_sharpe_positive': 0.995}, 'version finale': {'sharpe': 1.53, 'sharpe_ci95': [0.45, 2.66], 'prob_true_sharpe_positive': 0.995}}
- walk-forward 2021–2026 : {'years': {'2021': {'choice': 'carry 3j/7j', 'return_pct': 326.3}, '2022': {'choice': 'carry 3j/7j', 'return_pct': 3.0}, '2023': {'choice': 'mélange 0.5/1j', 'return_pct': 31.4}, '2024': {'choice': 'mélange 0.5/1j', 'return_pct': 26.1}, '2025': {'choice': 'mélange 0.5/1j', 'return_pct': 37.3}, '2026': {'choice': 'mélange 0.5/1j', 'return_pct': 16.4}}, 'sharpe': 1.39, 'sharpe_ci95': [0.62, 2.08], 'return_pct': 1061.7, 'cagr_pct': 52.2, 'max_dd_pct': 29.9, 'prob_true_sharpe_positive': 1.0, 'prob_not_luck_after_trials': 0.983, 'kelly_leverage_full': 4.1, 'kelly_leverage_half': 2.0}
- durée pour confirmer en réel : {'years_for_95pct': 1.4, 'expected_t_stat_after_5_months': 0.9}

## Petit compte sur 5 mois (bootstrap, 5 000 trajectoires)

| configuration | P(finir en perte) | P(baisse ≥ 50 %) | rendement médian % | 5 % pire | 5 % meilleur |
|---|---|---|---|---|---|
| 2+2 positions, exposition 1× | 0.348 | 0.027 | 10.9 | -30.7 | 96.1 |
| 2+2 positions, exposition 2× | 0.401 | 0.267 | 14.2 | -57.7 | 243.2 |
| 3+3 positions, exposition 1× | 0.284 | 0.006 | 13.5 | -23.0 | 74.9 |
| 3+3 positions, exposition 2× | 0.325 | 0.153 | 22.9 | -45.3 | 185.4 |
