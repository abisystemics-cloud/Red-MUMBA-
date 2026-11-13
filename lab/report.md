# Laboratoire hl-swarm — rapport

Généré le 2026-11-13 20:38 UTC · 30 marchés Hyperliquid, dernier jour clôturé 2026-11-12

Simulation uniquement : aucun ordre réel.

## Champion

**blend(carry=7,hold=1,k=0,mom=14,w=0.7)** depuis le 2026-11-13 (provisoire)

- positions simulées pour 1000 $ : AVAX +83 $, ATOM +83 $, ARB +83 $, INJ +83 $, ICP +83 $, RUNE +83 $, ETH -83 $, SOL -83 $, XRP -83 $, NEAR -83 $, SEI -83 $, BCH -83 $
- positions simulées pour 50 $ : aucune (ordres sous le minimum de 10 $)

## Livres de paper trading

| règle | capital $ | jours | rendement % | pire baisse % | Sharpe | ordres | ordres ignorés (< 10 $) | état | test séquentiel | porte backtest |
|---|---|---|---|---|---|---|---|---|---|---|
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 1000 | 0 | 0.0 | 0.0 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 50 | 0 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 1000 | 0 | 0.0 | 0.0 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 50 | 0 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 1000 | 0 | 0.0 | 0.0 | – | 6 | 0 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 50 | 0 | 0.0 | 0.0 | – | 0 | 6 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 1000 | 0 | 0.0 | 0.0 | – | 6 | 0 | paper | continue | non |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 50 | 0 | 0.0 | 0.0 | – | 0 | 6 | paper | continue | non |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 1000 | 0 | 0.0 | 0.0 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 50 | 0 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 1000 | 0 | 0.0 | 0.0 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 50 | 0 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 1000 | 0 | 0.0 | 0.0 | – | 6 | 0 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 50 | 0 | 0.0 | 0.0 | – | 0 | 6 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 1000 | 0 | 0.0 | 0.0 | – | 6 | 0 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 50 | 0 | 0.0 | 0.0 | – | 0 | 6 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 1000 | 0 | 0.0 | 0.0 | – | 12 | 0 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 50 | 0 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| carry(carry=14,hold=7,k=3) | 1000 | 0 | 0.0 | 0.0 | – | 6 | 0 | paper | continue | non |
| carry(carry=14,hold=7,k=3) | 50 | 0 | 0.0 | 0.0 | – | 0 | 6 | paper | continue | non |
| carry(carry=3,hold=7,k=0) | 1000 | 0 | 0.0 | 0.0 | – | 12 | 0 | paper | continue | oui |
| carry(carry=3,hold=7,k=0) | 50 | 0 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| carry(carry=3,hold=7,k=3) | 1000 | 0 | 0.0 | 0.0 | – | 6 | 0 | paper | continue | non |
| carry(carry=3,hold=7,k=3) | 50 | 0 | 0.0 | 0.0 | – | 0 | 6 | paper | continue | non |
| carry(carry=7,hold=7,k=0) | 1000 | 0 | 0.0 | 0.0 | – | 12 | 0 | paper | continue | oui |
| carry(carry=7,hold=7,k=0) | 50 | 0 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 1000 | 0 | 0.0 | 0.0 | – | 6 | 0 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 50 | 0 | 0.0 | 0.0 | – | 0 | 6 | paper | continue | oui |
| trend(hold=1,mom=14) | 1000 | 0 | 0.0 | 0.0 | – | 3 | 0 | paper | continue | non |
| trend(hold=1,mom=14) | 50 | 0 | 0.0 | 0.0 | – | 0 | 3 | paper | continue | non |
| trend(hold=1,mom=28) | 1000 | 0 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=28) | 50 | 0 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=7) | 1000 | 0 | 0.0 | 0.0 | – | 4 | 0 | paper | continue | non |
| trend(hold=1,mom=7) | 50 | 0 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 1000 | 0 | 0.0 | 0.0 | – | 12 | 0 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 50 | 0 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 1000 | 0 | 0.0 | 0.0 | – | 12 | 0 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 50 | 0 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | non |

## Fiche de score du catalogue (19 règles, historique long)

| règle | porte | Sharpe < 2024 | Sharpe ≥ 2024 | IC 95 % | rendement ≥ 2024 coûts ×2 % | baisse ≥ 2024 % | données propres (≥ 2026-07) % | Sharpe déflaté |
|---|---|---|---|---|---|---|---|---|
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.844 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.792 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | oui | 0.88 | 1.26 | [0.26, 2.33] | 96.4 | 15.9 | -9.8 | 0.744 |
| carry(carry=7,hold=7,k=0) | oui | 0.7 | 1.25 | [0.25, 2.18] | 70.6 | 12.6 | 0.7 | 0.75 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | oui | 1.66 | 1.22 | [0.24, 2.22] | 47.1 | 11.2 | -0.9 | 0.728 |
| carry(carry=3,hold=7,k=0) | oui | 0.63 | 1.23 | [0.2, 2.31] | 61.8 | 14.9 | -12.9 | 0.728 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | oui | 1.35 | 1.21 | [0.12, 2.24] | 70.2 | 20.9 | -1.4 | 0.726 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | oui | 1.1 | 1.14 | [0.04, 2.31] | 119.6 | 29.3 | -8.0 | 0.683 |
| carry(carry=7,hold=7,k=3) | oui | 0.51 | 1.07 | [0.04, 2.06] | 71.8 | 19.6 | -6.1 | 0.633 |
| carry(carry=14,hold=7,k=0) | oui | 0.42 | 1.09 | [0.04, 2.09] | 58.4 | 13.6 | -1.8 | 0.644 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | non | 1.42 | 1.04 | [-0.08, 2.1] | 97.5 | 22.3 | -15.0 | 0.619 |
| carry(carry=14,hold=7,k=3) | non | 0.43 | 0.91 | [-0.08, 1.83] | 70.6 | 21.0 | 0.6 | 0.531 |
| carry(carry=3,hold=7,k=3) | non | 0.92 | 0.88 | [-0.13, 1.92] | 58.4 | 25.5 | -16.8 | 0.508 |
| xsmom(hold=7,k=0,mom=14) | non | 1.12 | 0.8 | [-0.23, 1.88] | 46.1 | 24.9 | -13.5 | 0.459 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | non | 1.31 | 0.73 | [-0.42, 1.82] | 12.8 | 30.9 | -23.0 | 0.407 |
| xsmom(hold=7,k=0,mom=28) | non | 1.47 | -0.07 | [-1.02, 0.9] | -19.8 | 36.0 | -14.7 | 0.057 |
| trend(hold=1,mom=14) | non | 1.4 | 0.17 | [-1.07, 1.44] | -11.2 | 58.0 | 11.9 | 0.121 |
| trend(hold=1,mom=28) | non | 1.59 | 0.12 | [-1.16, 1.32] | -13.0 | 59.3 | 16.6 | 0.104 |
| trend(hold=1,mom=7) | non | 1.57 | 0.07 | [-1.24, 1.33] | -22.1 | 63.7 | 16.5 | 0.09 |

## Journal des décisions (les 40 dernières)

- 2026-11-13 — fiche de score recalculée sur 2020-01 → 2026-10 : 10 règles sur 19 passent la porte
- 2026-11-13 — champion PROVISOIRE : blend(carry=7,hold=1,k=0,mom=14,w=0.7) (meilleure borne basse de Sharpe au backtest, en attendant 28 jours de paper trading)
