# Laboratoire hl-swarm — rapport

Généré le 2026-11-13 21:53 UTC · 30 marchés Hyperliquid, dernier jour clôturé 2026-11-12

Simulation uniquement : aucun ordre réel.

## Champion

**blend(carry=7,hold=1,k=0,mom=14,w=0.7)** depuis le 2026-11-13 (provisoire)

- positions simulées pour 1000 $ : AVAX +83 $, ATOM +83 $, ARB +83 $, INJ +83 $, ICP +83 $, RUNE +83 $, ETH -83 $, SOL -83 $, XRP -83 $, NEAR -83 $, SEI -83 $, BCH -83 $
- positions simulées pour 50 $ : aucune (ordres sous le minimum de 10 $)

## Contexte du jour (macro, institutions, géopolitique)

| indicateur | feu | source |
|---|---|---|
| Nasdaq au-dessus de sa moyenne 100 j | rouge | yahoo, 2126 jours |
| Stablecoins en hausse sur 30 j | rouge | DefiLlama, 3272 jours |
| Prime Coinbase positive (7 j) | rouge | Coinbase vs Binance spot, 500 jours |
| Gérants d'actifs CME en hausse (4 sem.) | rouge | CFTC, 448 semaines |
| Risque géopolitique calme | vert | indice GPR, 15281 jours |
| Hors fenêtre de décision de la Fed | vert | calendrier de la Fed (liste jusqu'à fin 2026) |
| Ton de la presse mondiale sur les cryptos en amélioration | indisponible | indisponible (TypeError) |
| Presse mondiale : tensions géopolitiques calmes | vert | GDELT, 469 jours |
| Indice Fear & Greed au-dessus de sa moyenne 30 j | rouge | alternative.me, 3204 jours |

## Machine learning

Dernier entraînement le 2026-11-13 sur l'historique 2020-01 → 2026-10 (62102 exemples). Modèles en service aujourd'hui : gbm, ridge.

Ce que la régression a appris (poids les plus forts) : vol30 -0.062, carry7 +0.045, mom7 -0.028, mom14 +0.023, carry3 +0.022.

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

## Fiche de score du catalogue (45 règles, historique long)

| règle | porte | Sharpe < 2024 | Sharpe ≥ 2024 | IC 95 % | rendement ≥ 2024 coûts ×2 % | baisse ≥ 2024 % | données propres (≥ 2026-07) % | Sharpe déflaté |
|---|---|---|---|---|---|---|---|---|
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | oui | 1.05 | 1.58 | [0.53, 2.55] | 116.9 | 12.5 | -8.9 | 0.824 |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | oui | 1.21 | 1.58 | [0.45, 2.63] | 87.4 | 14.8 | -12.7 | 0.827 |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | oui | 1.41 | 1.53 | [0.44, 2.57] | 58.4 | 12.0 | -10.4 | 0.802 |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | oui | 1.03 | 1.42 | [0.43, 2.35] | 80.5 | 10.7 | -6.9 | 0.742 |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | oui | 1.32 | 1.53 | [0.43, 2.6] | 84.2 | 14.9 | -12.0 | 0.798 |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | oui | 1.0 | 1.45 | [0.4, 2.42] | 105.3 | 13.1 | -9.8 | 0.756 |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | oui | 0.95 | 1.52 | [0.4, 2.47] | 83.2 | 10.2 | -7.0 | 0.799 |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.15 | 1.52 | [0.35, 2.57] | 81.2 | 14.7 | -9.4 | 0.795 |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | oui | 1.16 | 1.37 | [0.34, 2.39] | 97.4 | 15.7 | -13.8 | 0.709 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.764 |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.45 | [0.32, 2.53] | 75.2 | 15.1 | -12.0 | 0.759 |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.41 | [0.31, 2.44] | 95.1 | 17.0 | -15.2 | 0.736 |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | oui | 0.96 | 1.37 | [0.31, 2.35] | 64.6 | 12.6 | -9.7 | 0.714 |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | oui | 1.08 | 1.4 | [0.3, 2.43] | 56.9 | 16.1 | -6.0 | 0.737 |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | oui | 1.15 | 1.38 | [0.29, 2.5] | 67.0 | 15.2 | -9.8 | 0.722 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.701 |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.35 | [0.28, 2.36] | 96.7 | 15.7 | -13.8 | 0.698 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | oui | 0.88 | 1.26 | [0.26, 2.33] | 96.4 | 15.9 | -9.8 | 0.644 |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | oui | 1.1 | 1.28 | [0.26, 2.28] | 57.3 | 15.7 | -13.8 | 0.661 |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | oui | 1.18 | 1.28 | [0.26, 2.26] | 50.1 | 14.3 | -9.1 | 0.66 |
| carry(carry=7,hold=7,k=0) | oui | 0.7 | 1.25 | [0.25, 2.18] | 70.6 | 12.6 | 0.7 | 0.647 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | oui | 1.66 | 1.22 | [0.24, 2.22] | 47.1 | 11.2 | -0.9 | 0.624 |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | oui | 1.29 | 1.34 | [0.22, 2.42] | 60.5 | 17.1 | -14.9 | 0.696 |
| carry(carry=3,hold=7,k=0) | oui | 0.63 | 1.23 | [0.2, 2.31] | 61.8 | 14.9 | -12.9 | 0.625 |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | oui | 1.18 | 1.25 | [0.15, 2.26] | 82.8 | 17.1 | -14.5 | 0.639 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | oui | 1.35 | 1.21 | [0.12, 2.24] | 70.2 | 20.9 | -1.4 | 0.62 |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | oui | 1.34 | 1.14 | [0.07, 2.19] | 29.4 | 16.4 | -14.1 | 0.569 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | oui | 1.1 | 1.14 | [0.04, 2.31] | 119.6 | 29.3 | -8.0 | 0.571 |
| carry(carry=7,hold=7,k=3) | oui | 0.51 | 1.07 | [0.04, 2.06] | 71.8 | 19.6 | -6.1 | 0.52 |
| carry(carry=14,hold=7,k=0) | oui | 0.42 | 1.09 | [0.04, 2.09] | 58.4 | 13.6 | -1.8 | 0.532 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | non | 1.42 | 1.04 | [-0.08, 2.1] | 97.5 | 22.3 | -15.0 | 0.504 |
| carry(carry=14,hold=7,k=3) | non | 0.43 | 0.91 | [-0.08, 1.83] | 70.6 | 21.0 | 0.6 | 0.416 |
| carry(carry=3,hold=7,k=3) | non | 0.92 | 0.88 | [-0.13, 1.92] | 58.4 | 25.5 | -16.8 | 0.391 |
| xsmom(hold=7,k=0,mom=14) | non | 1.12 | 0.8 | [-0.23, 1.88] | 46.1 | 24.9 | -13.5 | 0.348 |
| premium(hold=1) | non | 1.4 | 0.67 | [-0.31, 1.72] | 63.3 | 26.6 | 0.0 | 0.269 |
| ml(hold=7,k=0,model=ridge) | non | -0.25 | 0.7 | [-0.36, 1.85] | 32.2 | 22.8 | -21.8 | 0.285 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | non | 1.31 | 0.73 | [-0.42, 1.82] | 12.8 | 30.9 | -23.0 | 0.299 |
| ml(hold=7,k=0,model=gbm) | non | 0.26 | 0.73 | [-0.49, 1.98] | 26.1 | 25.9 | -18.8 | 0.305 |
| trend(gate=premium,hold=1,mom=14) | non | 1.27 | 0.31 | [-0.95, 1.61] | 7.1 | 49.2 | 6.4 | 0.113 |
| xsmom(hold=7,k=0,mom=28) | non | 1.47 | -0.07 | [-1.02, 0.9] | -19.8 | 36.0 | -14.7 | 0.031 |
| trend(hold=1,mom=14) | non | 1.4 | 0.17 | [-1.07, 1.44] | -11.2 | 58.0 | 11.9 | 0.073 |
| trend(gate=risk_on,hold=1,mom=14) | non | 1.32 | 0.23 | [-1.09, 1.5] | -3.7 | 53.9 | 6.4 | 0.088 |
| trend(gate=nasdaq,hold=1,mom=14) | non | 1.5 | 0.17 | [-1.1, 1.43] | -9.3 | 55.8 | 8.5 | 0.074 |
| trend(hold=1,mom=28) | non | 1.59 | 0.12 | [-1.16, 1.32] | -13.0 | 59.3 | 16.6 | 0.061 |
| trend(hold=1,mom=7) | non | 1.57 | 0.07 | [-1.24, 1.33] | -22.1 | 63.7 | 16.5 | 0.052 |

## Journal des décisions (les 40 dernières)

- 2026-11-13 — fiche de score recalculée sur 2020-01 → 2026-10 : 10 règles sur 19 passent la porte
- 2026-11-13 — champion PROVISOIRE : blend(carry=7,hold=1,k=0,mom=14,w=0.7) (meilleure borne basse de Sharpe au backtest, en attendant 28 jours de paper trading)
- 2026-11-13 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-13 — fiche de score recalculée sur 2020-01 → 2026-10 : 24 règles sur 39 passent la porte
- 2026-11-13 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-13 — fiche de score recalculée sur 2020-01 → 2026-10 : 30 règles sur 45 passent la porte
