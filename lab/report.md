# Laboratoire hl-swarm — rapport

Généré le 2026-11-14 23:09 UTC · 30 marchés Hyperliquid, dernier jour clôturé 2026-11-13

Simulation uniquement : aucun ordre réel.

## Champion

**blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5)** depuis le 2026-11-14 (provisoire)

- positions simulées pour 1000 $ : AVAX +42 $, ATOM +42 $, INJ +42 $, AAVE +42 $, ICP +42 $, RUNE +42 $, BTC -42 $, XRP -42 $, NEAR -42 $, SEI -42 $, FIL -42 $, HBAR -42 $
- positions simulées pour 50 $ : aucune (ordres sous le minimum de 10 $)

## Contexte du jour (macro, institutions, géopolitique)

| indicateur | feu | source |
|---|---|---|
| Nasdaq au-dessus de sa moyenne 100 j | rouge | yahoo, 2126 jours |
| Stablecoins en hausse sur 30 j | rouge | DefiLlama, 3273 jours |
| Prime Coinbase positive (7 j) | rouge | Coinbase vs Binance spot, 501 jours |
| Gérants d'actifs CME en hausse (4 sem.) | rouge | CFTC, 448 semaines |
| Risque géopolitique calme | vert | indice GPR, 15281 jours |
| Hors fenêtre de décision de la Fed | vert | calendrier de la Fed (liste jusqu'à fin 2026) |
| Ton de la presse mondiale sur les cryptos en amélioration | rouge | GDELT, 470 jours |
| Presse mondiale : tensions géopolitiques calmes | vert | GDELT, 470 jours |
| Indice Fear & Greed au-dessus de sa moyenne 30 j | rouge | alternative.me, 3205 jours |

## Échanges avec Claude (connecteurs)

Dernière lecture : 2026-11-14 — réponses de Claude du 2026-11-14T03:25Z déjà lues.

- Risque signalé pour le 2026-11-13 : **none** — Aucun événement grave confirmé dans les dernières 24 heures d'après la recherche web. Le dernier fait notable (soupçon de piratage d'un exchange) date du 30 octobre. 
- Paper trading Keel au 2026-11-13 : +0.20 % en 1 jours, pire baisse 0.00 %. 1 évaluation depuis le 13/11, 24 ordres exécutés, 6 ignorés sous le minimum de 10 $ ; prochaine évaluation le 14/11 à 12:00 UTC
- Gros traders au 2026-11-13 : les plus acheteurs BCH +18, ETC +17, ADA +16 ; les plus vendeurs ICP -51, OP -72, SEI -82
- 2026-11-13 · TIA : Aucune cause précise identifiée par la recherche web pour la baisse de TIA du 13/11 : pas d'annonce ni d'incident trouvé. Le jeton est en tendance baissière depuis début novembre, dans un secteur des blockchains de couche 1 en recul. [source](https://www.coinbase.com/en-fr/price/celestia)

## Machine learning

Dernier entraînement le 2026-11-14 sur l'historique 2020-01 → 2026-10 (62102 exemples). Modèles en service aujourd'hui : gbm, ridge.

Ce que la régression a appris (poids les plus forts) : carry7 +0.051, brk21 +0.046, vol30 -0.046, mom7 -0.040, spring14 +0.031.

## Évolution (règles inventées par le laboratoire)

287552 règles explorées depuis le début en 4 passages (jugées sur l'apprentissage seul), 22 présentées à la validation, 2 en service.

Présentées à la validation au dernier passage (2026-11-14) :

- mix(a=brk,b=illiq,gate=nasdaq,hold=7,k=5,la=42,lb=21,sa=1,sb=1,w=0.3) → porte non, déflaté 0.0
- mix(a=z,b=illiq,gate=nasdaq,hold=2,k=5,la=14,lb=10,sa=1,sb=1,w=0.4) → porte non, déflaté 0.014
- mix(a=illiq,b=brk,gate=geo_news,hold=14,k=5,la=10,lb=21,sa=1,sb=1,w=0.6) → porte non, déflaté 0.0
- mix(a=illiq,b=riskmom,gate=fng,hold=14,k=5,la=5,lb=2,sa=1,sb=1,w=0.5) → porte non, déflaté 0.0
- mix(a=illiq,b=vwapd,gate=fomc,hold=14,k=5,la=21,lb=3,sa=1,sb=1,w=0.5) → porte non, déflaté 0.0
- mix(a=riskmom,b=illiq,gate=fomc,hold=7,k=4,la=42,lb=3,sa=1,sb=1,w=0.3) → porte non, déflaté 0.0

Règles nées ici, en paper trading :

- blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) — née le 2026-11-14, Sharpe déflaté 0.592
- blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) — née le 2026-11-14, Sharpe déflaté 0.532

## Livres de paper trading

| règle | capital $ | jours | rendement % | pire baisse % | Sharpe | ordres | ordres ignorés (< 10 $) | état | test séquentiel | porte backtest |
|---|---|---|---|---|---|---|---|---|---|---|
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.07 | 0.07 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.07 | 0.07 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.07 | 0.07 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.07 | 0.07 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.07 | 0.07 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.07 | 0.07 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | -0.03 | 0.03 | – | 12 | 0 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 1000 | 1 | 0.63 | 0.0 | – | 22 | 7 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 1000 | 1 | 0.3 | 0.0 | – | 22 | 7 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 1000 | 1 | 0.9 | 0.0 | – | 12 | 3 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 1000 | 1 | 0.9 | 0.0 | – | 12 | 3 | paper | continue | non |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | non |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 1000 | 1 | 0.69 | 0.0 | – | 12 | 12 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 1000 | 1 | 0.36 | 0.0 | – | 12 | 12 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 1000 | 1 | 0.96 | 0.0 | – | 6 | 6 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 1000 | 1 | 0.96 | 0.0 | – | 6 | 6 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 1000 | 1 | 0.74 | 0.0 | – | 12 | 12 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 50 | 1 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | oui |
| carry(carry=14,hold=7,k=3) | 1000 | 1 | 0.39 | 0.0 | – | 6 | 6 | paper | continue | non |
| carry(carry=14,hold=7,k=3) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | non |
| carry(carry=3,hold=7,k=0) | 1000 | 1 | 0.86 | 0.0 | – | 12 | 12 | paper | continue | oui |
| carry(carry=3,hold=7,k=0) | 50 | 1 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | oui |
| carry(carry=3,hold=7,k=3) | 1000 | 1 | 1.73 | 0.0 | – | 6 | 6 | paper | continue | non |
| carry(carry=3,hold=7,k=3) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | non |
| carry(carry=7,hold=7,k=0) | 1000 | 1 | 0.95 | 0.0 | – | 12 | 12 | paper | continue | oui |
| carry(carry=7,hold=7,k=0) | 50 | 1 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 1000 | 1 | 1.81 | 0.0 | – | 6 | 6 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | oui |
| ml(hold=7,k=0,model=gbm) | 1000 | 1 | -0.07 | 0.07 | – | 12 | 0 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 1000 | 1 | -0.07 | 0.07 | – | 12 | 0 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 50 | 1 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | non |
| premium(hold=1) | 1000 | 1 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| premium(hold=1) | 50 | 1 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 1000 | 1 | -0.0 | 0.0 | – | 1 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 50 | 1 | 0.0 | 0.0 | – | 0 | 1 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 1000 | 1 | -0.0 | 0.0 | – | 1 | 0 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 50 | 1 | 0.0 | 0.0 | – | 0 | 1 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 1000 | 1 | -0.0 | 0.0 | – | 1 | 0 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 50 | 1 | 0.0 | 0.0 | – | 0 | 1 | paper | continue | non |
| trend(hold=1,mom=14) | 1000 | 1 | 0.12 | 0.0 | – | 5 | 1 | paper | continue | non |
| trend(hold=1,mom=14) | 50 | 1 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(hold=1,mom=28) | 1000 | 1 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=28) | 50 | 1 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=7) | 1000 | 1 | -0.71 | 0.71 | – | 7 | 1 | paper | continue | non |
| trend(hold=1,mom=7) | 50 | 1 | 0.0 | 0.0 | – | 0 | 5 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 1000 | 1 | 0.31 | 0.0 | – | 12 | 12 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 50 | 1 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 1000 | 1 | 0.47 | 0.0 | – | 12 | 12 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 50 | 1 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | non |

## Fiche de score du catalogue (62 règles, historique long)

| règle | porte | Sharpe < 2024 | Sharpe ≥ 2024 | IC 95 % | rendement ≥ 2024 coûts ×2 % | baisse ≥ 2024 % | données propres (≥ 2026-07) % | Sharpe déflaté |
|---|---|---|---|---|---|---|---|---|
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | oui | 1.05 | 1.58 | [0.53, 2.55] | 116.9 | 12.5 | -8.9 | 0.587 |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | oui | 1.21 | 1.58 | [0.45, 2.63] | 87.4 | 14.8 | -12.7 | 0.587 |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.1 | 1.59 | [0.45, 2.62] | 95.3 | 18.4 | -8.6 | 0.592 |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | oui | 1.41 | 1.53 | [0.44, 2.57] | 58.4 | 12.0 | -10.4 | 0.552 |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | oui | 1.03 | 1.42 | [0.43, 2.35] | 80.5 | 10.7 | -6.9 | 0.477 |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | oui | 1.32 | 1.53 | [0.43, 2.6] | 84.2 | 14.9 | -12.0 | 0.548 |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | oui | 1.51 | 1.36 | [0.43, 2.33] | 93.0 | 13.6 | -11.2 | 0.436 |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | oui | 1.0 | 1.45 | [0.4, 2.42] | 105.3 | 13.1 | -9.8 | 0.498 |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | oui | 0.95 | 1.52 | [0.4, 2.47] | 83.2 | 10.2 | -7.0 | 0.545 |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.15 | 1.52 | [0.35, 2.57] | 81.2 | 14.7 | -9.4 | 0.542 |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | oui | 0.82 | 1.5 | [0.35, 2.57] | 77.4 | 11.3 | -2.7 | 0.532 |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | oui | 1.16 | 1.37 | [0.34, 2.39] | 97.4 | 15.7 | -13.8 | 0.441 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.502 |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.502 |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.45 | [0.32, 2.53] | 75.2 | 15.1 | -12.0 | 0.496 |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.41 | [0.31, 2.44] | 95.1 | 17.0 | -15.2 | 0.468 |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | oui | 0.96 | 1.37 | [0.31, 2.35] | 64.6 | 12.6 | -9.7 | 0.443 |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | oui | 1.08 | 1.4 | [0.3, 2.43] | 56.9 | 16.1 | -6.0 | 0.463 |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | oui | 1.15 | 1.38 | [0.29, 2.5] | 67.0 | 15.2 | -9.8 | 0.449 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.432 |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.35 | [0.28, 2.36] | 96.7 | 15.7 | -13.8 | 0.429 |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.432 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | oui | 0.88 | 1.26 | [0.26, 2.33] | 96.4 | 15.9 | -9.8 | 0.371 |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | oui | 1.1 | 1.28 | [0.26, 2.28] | 57.3 | 15.7 | -13.8 | 0.386 |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | oui | 1.18 | 1.28 | [0.26, 2.26] | 50.1 | 14.3 | -9.1 | 0.382 |
| carry(carry=7,hold=7,k=0) | oui | 0.7 | 1.25 | [0.25, 2.18] | 70.6 | 12.6 | 0.7 | 0.363 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | oui | 1.66 | 1.22 | [0.24, 2.22] | 47.1 | 11.2 | -0.9 | 0.349 |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | oui | 1.29 | 1.34 | [0.22, 2.42] | 60.5 | 17.1 | -14.9 | 0.419 |
| carry(carry=3,hold=7,k=0) | oui | 0.63 | 1.23 | [0.2, 2.31] | 61.8 | 14.9 | -12.9 | 0.349 |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | oui | 1.18 | 1.25 | [0.15, 2.26] | 82.8 | 17.1 | -14.5 | 0.366 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | oui | 1.35 | 1.21 | [0.12, 2.24] | 70.2 | 20.9 | -1.4 | 0.339 |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | oui | 1.34 | 1.14 | [0.07, 2.19] | 29.4 | 16.4 | -14.1 | 0.294 |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | oui | 0.21 | 0.99 | [0.07, 2.0] | 54.6 | 13.1 | -0.8 | 0.217 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | oui | 1.1 | 1.14 | [0.04, 2.31] | 119.6 | 29.3 | -8.0 | 0.293 |
| carry(carry=7,hold=7,k=3) | oui | 0.51 | 1.07 | [0.04, 2.06] | 71.8 | 19.6 | -6.1 | 0.257 |
| carry(carry=14,hold=7,k=0) | oui | 0.42 | 1.09 | [0.04, 2.09] | 58.4 | 13.6 | -1.8 | 0.267 |
| whales(hold=1,k=0) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.007 |
| whales(hold=1,k=3) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.007 |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | non | -0.35 | 1.06 | [-0.06, 2.23] | 81.8 | 27.3 | -12.2 | 0.253 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | non | 1.42 | 1.04 | [-0.08, 2.1] | 97.5 | 22.3 | -15.0 | 0.241 |
| carry(carry=14,hold=7,k=3) | non | 0.43 | 0.91 | [-0.08, 1.83] | 70.6 | 21.0 | 0.6 | 0.179 |
| carry(carry=3,hold=7,k=3) | non | 0.92 | 0.88 | [-0.13, 1.92] | 58.4 | 25.5 | -16.8 | 0.158 |
| xsmom(hold=7,k=0,mom=14) | non | 1.12 | 0.8 | [-0.23, 1.88] | 46.1 | 24.9 | -13.5 | 0.137 |
| premium(hold=1) | non | 1.4 | 0.67 | [-0.31, 1.72] | 63.3 | 26.6 | 0.0 | 0.092 |
| ml(hold=7,k=0,model=ridge) | non | 0.8 | 0.67 | [-0.34, 1.7] | 28.6 | 23.5 | -18.2 | 0.093 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | non | 1.31 | 0.73 | [-0.42, 1.82] | 12.8 | 30.9 | -23.0 | 0.108 |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | non | 0.42 | 0.63 | [-0.44, 1.65] | -5.4 | 13.1 | 3.2 | 0.081 |
| ml(hold=7,k=0,model=gbm) | non | -0.09 | 0.55 | [-0.66, 1.63] | 16.6 | 22.5 | -17.4 | 0.064 |
| ts(hold=1,l=14,s=1,sig=spring) | non | -1.07 | 0.15 | [-0.84, 1.24] | -8.9 | 20.9 | 3.4 | 0.014 |
| trend(gate=premium,hold=1,mom=14) | non | 1.27 | 0.31 | [-0.95, 1.61] | 7.1 | 49.2 | 6.4 | 0.028 |
| ts(hold=1,l=21,s=1,sig=brk) | non | 0.67 | 0.21 | [-0.96, 1.27] | -20.3 | 62.9 | 2.7 | 0.018 |
| xsmom(hold=7,k=0,mom=28) | non | 1.47 | -0.07 | [-1.02, 0.9] | -19.8 | 36.0 | -14.7 | 0.005 |
| trend(hold=1,mom=14) | non | 1.4 | 0.17 | [-1.07, 1.44] | -11.2 | 58.0 | 11.9 | 0.016 |
| trend(gate=risk_on,hold=1,mom=14) | non | 1.32 | 0.23 | [-1.09, 1.5] | -3.7 | 53.9 | 6.4 | 0.02 |
| trend(gate=nasdaq,hold=1,mom=14) | non | 1.5 | 0.17 | [-1.1, 1.43] | -9.3 | 55.8 | 8.5 | 0.016 |
| ts(hold=1,l=10,s=-1,sig=z) | non | -0.87 | -0.13 | [-1.1, 0.94] | -58.2 | 61.9 | 1.2 | 0.004 |
| ts(hold=1,l=14,s=1,sig=vwapd) | non | 0.46 | -0.05 | [-1.13, 0.9] | -49.4 | 61.2 | -10.4 | 0.006 |
| trend(hold=1,mom=28) | non | 1.59 | 0.12 | [-1.16, 1.32] | -13.0 | 59.3 | 16.6 | 0.012 |
| ts(hold=1,l=14,s=-1,sig=vwapd) | non | -0.66 | -0.22 | [-1.16, 0.84] | -61.0 | 65.7 | 0.9 | 0.002 |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | non | 0.46 | -0.09 | [-1.17, 0.86] | -53.5 | 39.4 | -1.6 | 0.005 |
| trend(hold=1,mom=7) | non | 1.57 | 0.07 | [-1.24, 1.33] | -22.1 | 63.7 | 16.5 | 0.01 |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | non | -0.62 | -0.53 | [-1.6, 0.56] | -54.1 | 31.9 | -11.5 | 0.0 |

## Journal des décisions (les 40 dernières)

- 2026-11-13 — fiche de score recalculée sur 2020-01 → 2026-10 : 10 règles sur 19 passent la porte
- 2026-11-13 — champion PROVISOIRE : blend(carry=7,hold=1,k=0,mom=14,w=0.7) (meilleure borne basse de Sharpe au backtest, en attendant 28 jours de paper trading)
- 2026-11-13 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-13 — fiche de score recalculée sur 2020-01 → 2026-10 : 24 règles sur 39 passent la porte
- 2026-11-13 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-13 — fiche de score recalculée sur 2020-01 → 2026-10 : 30 règles sur 45 passent la porte
- 2026-11-14 — champion PROVISOIRE : blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) (meilleure borne basse de Sharpe au backtest, en attendant 28 jours de paper trading)
- 2026-11-14 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-14 — fiche de score recalculée sur 2020-01 → 2026-10 : 32 règles sur 49 passent la porte
- 2026-11-14 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-14 — ÉVOLUTION : nouvelle règle blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) adoptée en paper trading (Sharpe ≥ 2024 1.59, déflaté 0.738 sur 16 essais)
- 2026-11-14 — ÉVOLUTION : nouvelle règle blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) adoptée en paper trading (Sharpe ≥ 2024 1.5, déflaté 0.683 sur 16 essais)
- 2026-11-14 — fiche de score recalculée sur 2020-01 → 2026-10 : 34 règles sur 51 passent la porte
- 2026-11-14 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-14 — ÉVOLUTION : 22480 règles essayées en 1405 générations, 2 règles nées en service, 22496 essais depuis le début
- 2026-11-14 — fiche de score recalculée sur 2020-01 → 2026-10 : 34 règles sur 51 passent la porte
- 2026-11-14 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-14 — ÉVOLUTION : 50768 règles essayées en 3173 générations, 2 règles nées en service, 73264 essais depuis le début
- 2026-11-14 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-14 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-14 — ÉVOLUTION : 91664 règles explorées en 5729 générations, 6 présentées à la validation, 2 règles nées en service (164928 explorées et 22 présentées depuis le début)
- 2026-11-14 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-14 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-14 — ÉVOLUTION : 122624 règles explorées en 7664 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (287552 explorées et 22 présentées depuis le début)
- 2026-11-14 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
