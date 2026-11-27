# Laboratoire hl-swarm — rapport

Généré le 2026-11-27 22:58 UTC · 30 marchés Hyperliquid, dernier jour clôturé 2026-11-26

Simulation uniquement : aucun ordre réel.

## Champion

**blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5)** depuis le 2026-11-14 (provisoire)

- positions simulées pour 1000 $ : ADA +42 $, SEI +42 $, BCH +42 $, XLM +42 $, TRX +42 $, RUNE +42 $, DOGE -42 $, APT -42 $, TIA -42 $, UNI -42 $, FIL -42 $, ICP -42 $
- positions simulées pour 50 $ : aucune (ordres sous le minimum de 10 $)

## Contexte du jour (macro, institutions, géopolitique)

| indicateur | feu | source |
|---|---|---|
| Nasdaq au-dessus de sa moyenne 100 j | rouge | yahoo, 2135 jours |
| Stablecoins en hausse sur 30 j | rouge | DefiLlama, 3286 jours |
| Prime Coinbase positive (7 j) | rouge | Coinbase vs Binance spot, 513 jours |
| Gérants d'actifs CME en hausse (4 sem.) | rouge | CFTC, 450 semaines |
| Risque géopolitique calme | vert | indice GPR, 15302 jours |
| Hors fenêtre de décision de la Fed | vert | calendrier de la Fed (liste jusqu'à fin 2026) |
| Ton de la presse mondiale sur les cryptos en amélioration | rouge | GDELT, 469 jours |
| Presse mondiale : tensions géopolitiques calmes | vert | GDELT, 469 jours |
| Indice Fear & Greed au-dessus de sa moyenne 30 j | rouge | alternative.me, 3218 jours |

## Échanges avec Claude (connecteurs)

Dernière lecture : 2026-11-27 — réponses de Claude du 2026-11-26T23:41Z déjà lues.

- Risque signalé pour le 2026-11-26 : **none** — Aucun événement grave daté des dernières 24 heures trouvé (piratage ou faillite d'exchange, panne d'Hyperliquid, décrochage de stablecoin, choc réglementaire, escalade militaire majeure) ; les résultats de recherche renvoient à des événements plus anciens, donc niveau neutre. 
- Paper trading Keel au 2026-11-26 : +0.66 % en 14 jours, pire baisse 1.14 %. Paper run actif depuis le 13/11 (14 évaluations, Sharpe 1.81). 53 % des ordres récents refusés sous le minimum de 10 $ (ADA bloquée). Critères de graduation d'âge (13/21 j) et d'évaluations (14/20) pa
- Gros traders au 2026-11-25 : les plus acheteurs ADA +25, DOT +19, ARB +17 ; les plus vendeurs TIA -62, HBAR -70, LTC -75
- 2026-11-13 · TIA : Aucune cause précise identifiée par la recherche web pour la baisse de TIA du 13/11 : pas d'annonce ni d'incident trouvé. Le jeton est en tendance baissière depuis début novembre, dans un secteur des blockchains de couche 1 en recul. [source](https://www.coinbase.com/en-fr/price/celestia)
- 2026-11-14 · TIA : Aucune nouvelle propre à Celestia : la baisse du 13/11 accompagne le repli général du marché crypto (bitcoin en forte baisse, sentiment de peur extrême). Le jeton restait en tendance baissière sous toutes ses moyennes mobiles. [source](https://coinmarketcap.com/top-stories/6af75f3f0ada0c77afaf1484/) [source](https://tradersunion.com/news/cryptocurrency-news/show/4240045-celestia-drops-11-63percent-today/)
- 2026-11-15 · APT : Aucun catalyseur propre à Aptos n'a été trouvé (ni annonce, ni incident réseau, ni décision réglementaire). La baisse s'inscrit dans le repli général du marché du 14 novembre, le bitcoin touchant un plus bas de trois mois vers 62 000 $ sur fond de liquidations. [source](https://www.diariobitcoin.com/analisis/aptos-apt-cae-1546-el-14-de-noviembre-de-2026-y-queda-bajo-presion-tecnica/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · INJ : Aucune cause propre à Injective n'a été trouvée : la baisse d'environ 15 % a eu lieu pendant le vote sur la mise à jour Veyra, pourtant bien soutenue par la communauté. Elle suit le repli général du marché crypto du 14 novembre et une pression vendeuse déjà installée depuis plusieurs jours. [source](https://tradersunion.com/news/cryptocurrency-news/show/4250138-injective-slides-15-18percent-today-to/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · UNI : Pas de cause propre à Uniswap : selon CoinMarketCap, la baisse d'environ 15 % vient du repli général du marché (bitcoin sous 68 000 $, inflation américaine plus forte que prévu, dollar et taux en hausse). Elle a été amplifiée par la perte de la zone technique des 6 $ et un positionnement baissier des traders. [source](https://coinmarketcap.com/top-stories/6af7ddf10ada0c77afaf9379/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)

## Machine learning

Dernier entraînement le 2026-11-27 sur l'historique 2020-01 → 2026-10 (62102 exemples). Modèles en service aujourd'hui : gbm, ridge.

Ce que la régression a appris (poids les plus forts) : carry7 +0.051, brk21 +0.046, vol30 -0.046, mom7 -0.040, spring14 +0.031.

## Évolution (règles inventées par le laboratoire)

86381760 règles explorées depuis le début en 259 passages (jugées sur l'apprentissage seul), 100 présentées à la validation, 2 en service.

Balayage exhaustif : 84839840 combinaisons sur 92490684 essayées (91.7 %).

Présentées à la validation au dernier passage (2026-11-27) :

- mix(a=riskmom,b=illiq,gate=geo_news,hold=3,k=5,la=42,lb=14,sa=1,sb=1,w=0.4) → porte non, déflaté 0.0
- mix(a=brk,b=illiq,gate=news_tone,hold=14,k=5,la=28,lb=42,sa=1,sb=1,w=0.5) → porte non, déflaté 0.0
- mix(a=illiq,b=mom,gate=fomc,hold=5,k=5,la=2,lb=28,sa=1,sb=1,w=0.7) → porte non, déflaté 0.0
- mix(a=vwapd,b=illiq,gate=news_tone,hold=14,k=4,la=5,lb=14,sa=1,sb=1,w=0.5) → porte non, déflaté 0.0
- mix(a=illiq,b=riskmom,gate=nasdaq,hold=3,k=5,la=3,lb=42,sa=1,sb=1,w=0.5) → porte non, déflaté 0.008
- mix(a=illiq,b=z,gate=fng,hold=5,k=5,la=3,lb=21,sa=1,sb=1,w=0.6) → porte non, déflaté 0.009

Règles nées ici, en paper trading :

- blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) — née le 2026-11-14, Sharpe déflaté 0.503
- blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) — née le 2026-11-14, Sharpe déflaté 0.442

## Livres de paper trading

| règle | capital $ | jours | rendement % | pire baisse % | Sharpe | ordres | ordres ignorés (< 10 $) | état | test séquentiel | porte backtest |
|---|---|---|---|---|---|---|---|---|---|---|
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 13 | 0.57 | 0.66 | – | 61 | 119 | paper | continue | oui |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 1000 | 13 | 0.19 | 1.45 | – | 79 | 99 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 1000 | 13 | 1.09 | 1.28 | – | 63 | 106 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 0.98 | 0.73 | 3.28 | 61 | 131 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 0.68 | 0.64 | 2.54 | 39 | 142 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 0.98 | 0.73 | 3.28 | 61 | 131 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 0.68 | 0.64 | 2.54 | 39 | 142 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 1.95 | 1.45 | 3.28 | 61 | 131 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 1.34 | 1.28 | 2.54 | 39 | 142 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 1.95 | 1.45 | 3.28 | 61 | 131 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 1.34 | 1.28 | 2.54 | 39 | 142 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 1.95 | 1.45 | 3.28 | 61 | 131 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 1.34 | 1.28 | 2.54 | 39 | 142 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 0.98 | 0.73 | 3.28 | 61 | 131 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 0.68 | 0.64 | 2.54 | 39 | 142 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | -0.04 | 1.92 | -0.03 | 100 | 92 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 0.2 | 1.28 | 0.55 | 73 | 108 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 0.98 | 0.73 | 3.28 | 61 | 131 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 1000 | 13 | 1.19 | 0.3 | – | 42 | 129 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 0.68 | 0.64 | 2.54 | 39 | 142 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 0.98 | 0.73 | 3.28 | 61 | 131 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 0.68 | 0.64 | 2.54 | 39 | 142 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 0.98 | 0.73 | 3.28 | 61 | 131 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 0.68 | 0.64 | 2.54 | 39 | 142 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 1000 | 14 | 4.04 | 0.75 | 8.24 | 78 | 135 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 2.33 | 1.45 | 3.9 | 71 | 138 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 1000 | 14 | 6.81 | 0.51 | 15.23 | 56 | 59 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 90 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 1000 | 14 | 8.26 | 1.56 | 10.02 | 50 | 62 | paper | continue | non |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 90 | paper | continue | non |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 2.1 | 1.28 | 3.87 | 39 | 154 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 1000 | 14 | -1.24 | 2.34 | -1.98 | 35 | 155 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 1000 | 14 | 1.04 | 2.96 | 1.87 | 28 | 73 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 90 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 1000 | 14 | 1.53 | 2.96 | 2.44 | 26 | 74 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 90 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 1000 | 14 | 2.4 | 0.98 | 5.1 | 29 | 159 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 50 | 14 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| carry(carry=14,hold=7,k=3) | 1000 | 14 | 5.43 | 1.57 | 7.67 | 18 | 78 | paper | continue | non |
| carry(carry=14,hold=7,k=3) | 50 | 14 | 0.0 | 0.0 | – | 0 | 90 | paper | continue | non |
| carry(carry=3,hold=7,k=0) | 1000 | 14 | 4.01 | 0.84 | 7.37 | 39 | 151 | paper | continue | oui |
| carry(carry=3,hold=7,k=0) | 50 | 14 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| carry(carry=3,hold=7,k=3) | 1000 | 14 | -0.96 | 2.72 | -1.11 | 27 | 73 | paper | continue | non |
| carry(carry=3,hold=7,k=3) | 50 | 14 | 0.0 | 0.0 | – | 0 | 90 | paper | continue | non |
| carry(carry=7,hold=7,k=0) | 1000 | 14 | 2.74 | 0.8 | 6.18 | 40 | 152 | paper | continue | oui |
| carry(carry=7,hold=7,k=0) | 50 | 14 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 1000 | 14 | 6.2 | 0.79 | 9.14 | 22 | 76 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 50 | 14 | 0.0 | 0.0 | – | 0 | 90 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 1000 | 13 | 1.11 | 1.06 | – | 43 | 128 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 13 | 2.06 | 0.88 | – | 39 | 130 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | oui |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 1000 | 13 | 1.77 | 1.01 | – | 91 | 104 | paper | continue | non |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 1000 | 13 | 1.8 | 1.22 | – | 38 | 131 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 1000 | 13 | -3.22 | 3.22 | – | 153 | 70 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 13 | 3.3 | 0.83 | – | 133 | 83 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 50 | 13 | 0.0 | 0.0 | – | 0 | 156 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 1000 | 14 | 0.1 | 1.4 | 0.28 | 65 | 128 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 1000 | 14 | 2.91 | 3.21 | 4.15 | 54 | 133 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | non |
| premium(hold=1) | 1000 | 14 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| premium(hold=1) | 50 | 14 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 1000 | 14 | -0.5 | 0.5 | -8.85 | 8 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 50 | 14 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 1000 | 14 | -0.5 | 0.5 | -8.85 | 8 | 0 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 50 | 14 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 1000 | 14 | -0.5 | 0.5 | -8.85 | 8 | 0 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 50 | 14 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(hold=1,mom=14) | 1000 | 14 | -0.88 | 1.0 | -7.37 | 12 | 1 | paper | continue | non |
| trend(hold=1,mom=14) | 50 | 14 | 0.0 | 0.0 | – | 0 | 7 | paper | continue | non |
| trend(hold=1,mom=28) | 1000 | 14 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=28) | 50 | 14 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=7) | 1000 | 14 | -1.57 | 1.59 | -9.56 | 31 | 3 | paper | continue | non |
| trend(hold=1,mom=7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 22 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 1000 | 13 | -1.96 | 10.55 | – | 55 | 335 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 50 | 13 | 0.0 | 0.0 | – | 0 | 390 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 1000 | 13 | -2.74 | 10.88 | – | 40 | 350 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 50 | 13 | 0.0 | 0.0 | – | 0 | 390 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 1000 | 13 | 1.02 | 2.82 | – | 111 | 125 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 50 | 13 | 0.0 | 0.0 | – | 0 | 183 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 1000 | 13 | 1.62 | 5.62 | – | 40 | 350 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 50 | 13 | 0.0 | 0.0 | – | 0 | 390 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 1000 | 13 | 1.53 | 5.62 | – | 33 | 357 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 50 | 13 | 0.0 | 0.0 | – | 0 | 390 | paper | continue | non |
| whales(hold=1,k=0) | 1000 | 13 | -3.53 | 3.53 | – | 82 | 19 | paper | continue | non |
| whales(hold=1,k=0) | 50 | 13 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | non |
| whales(hold=1,k=3) | 1000 | 13 | -2.35 | 2.38 | – | 42 | 9 | paper | continue | non |
| whales(hold=1,k=3) | 50 | 13 | 0.0 | 0.0 | – | 0 | 30 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 1000 | 14 | -4.2 | 5.0 | -6.3 | 35 | 154 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 50 | 14 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 1000 | 14 | 4.7 | 0.97 | 8.09 | 26 | 161 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 50 | 14 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | non |

## Fiche de score du catalogue (62 règles, historique long)

| règle | porte | Sharpe < 2024 | Sharpe ≥ 2024 | IC 95 % | rendement ≥ 2024 coûts ×2 % | baisse ≥ 2024 % | données propres (≥ 2026-07) % | Sharpe déflaté |
|---|---|---|---|---|---|---|---|---|
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | oui | 1.04 | 1.58 | [0.53, 2.55] | 116.6 | 12.5 | -8.9 | 0.495 |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.1 | 1.59 | [0.46, 2.62] | 95.8 | 18.2 | -8.6 | 0.503 |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | oui | 1.21 | 1.58 | [0.45, 2.63] | 87.4 | 14.8 | -12.7 | 0.495 |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | oui | 1.41 | 1.53 | [0.44, 2.57] | 58.4 | 12.0 | -10.4 | 0.46 |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | oui | 1.03 | 1.42 | [0.43, 2.35] | 80.5 | 10.7 | -6.9 | 0.389 |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | oui | 1.32 | 1.53 | [0.43, 2.6] | 84.2 | 14.9 | -12.0 | 0.457 |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | oui | 1.51 | 1.36 | [0.43, 2.33] | 93.0 | 13.6 | -11.2 | 0.35 |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | oui | 1.0 | 1.45 | [0.4, 2.42] | 105.7 | 13.1 | -9.8 | 0.41 |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | oui | 0.95 | 1.52 | [0.4, 2.47] | 83.2 | 10.2 | -7.0 | 0.453 |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.14 | 1.52 | [0.35, 2.57] | 81.4 | 14.7 | -9.4 | 0.451 |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | oui | 0.82 | 1.5 | [0.35, 2.57] | 77.4 | 11.3 | -2.7 | 0.442 |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | oui | 1.16 | 1.37 | [0.34, 2.39] | 97.4 | 15.7 | -13.8 | 0.355 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.411 |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.411 |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.45 | [0.32, 2.53] | 75.2 | 15.1 | -12.0 | 0.405 |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.41 | [0.31, 2.44] | 95.1 | 17.0 | -15.2 | 0.379 |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | oui | 0.96 | 1.37 | [0.31, 2.35] | 64.6 | 12.6 | -9.7 | 0.356 |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | oui | 1.16 | 1.4 | [0.31, 2.5] | 69.5 | 14.5 | -9.8 | 0.375 |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | oui | 1.08 | 1.4 | [0.3, 2.43] | 56.9 | 16.1 | -6.0 | 0.373 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.346 |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.35 | [0.28, 2.36] | 96.7 | 15.7 | -13.8 | 0.343 |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.346 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | oui | 0.88 | 1.26 | [0.26, 2.33] | 96.4 | 15.9 | -9.8 | 0.291 |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | oui | 1.1 | 1.28 | [0.26, 2.28] | 57.3 | 15.7 | -13.8 | 0.303 |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | oui | 1.18 | 1.28 | [0.26, 2.26] | 50.1 | 14.3 | -9.1 | 0.298 |
| carry(carry=7,hold=7,k=0) | oui | 0.7 | 1.25 | [0.25, 2.18] | 70.6 | 12.6 | 0.7 | 0.28 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | oui | 1.66 | 1.22 | [0.24, 2.22] | 47.1 | 11.2 | -0.9 | 0.269 |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | oui | 1.29 | 1.34 | [0.22, 2.42] | 60.5 | 17.1 | -14.9 | 0.333 |
| carry(carry=3,hold=7,k=0) | oui | 0.63 | 1.23 | [0.2, 2.31] | 61.8 | 14.9 | -12.9 | 0.27 |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | oui | 1.18 | 1.25 | [0.15, 2.26] | 82.8 | 17.1 | -14.5 | 0.285 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | oui | 1.35 | 1.21 | [0.12, 2.24] | 70.2 | 20.9 | -1.4 | 0.259 |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | oui | 1.34 | 1.14 | [0.07, 2.19] | 29.4 | 16.4 | -14.1 | 0.221 |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | oui | 0.21 | 0.99 | [0.07, 2.0] | 54.6 | 13.1 | -0.8 | 0.157 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | oui | 1.1 | 1.14 | [0.04, 2.31] | 119.6 | 29.3 | -8.0 | 0.219 |
| carry(carry=7,hold=7,k=3) | oui | 0.51 | 1.07 | [0.04, 2.06] | 71.8 | 19.6 | -6.1 | 0.19 |
| carry(carry=14,hold=7,k=0) | oui | 0.42 | 1.09 | [0.04, 2.09] | 58.4 | 13.6 | -1.8 | 0.199 |
| whales(hold=1,k=0) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.004 |
| whales(hold=1,k=3) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.004 |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | non | -0.35 | 1.06 | [-0.06, 2.23] | 81.8 | 27.3 | -12.2 | 0.188 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | non | 1.42 | 1.04 | [-0.08, 2.1] | 97.5 | 22.3 | -15.0 | 0.176 |
| carry(carry=14,hold=7,k=3) | non | 0.43 | 0.91 | [-0.08, 1.83] | 70.6 | 21.0 | 0.6 | 0.126 |
| carry(carry=3,hold=7,k=3) | non | 0.92 | 0.88 | [-0.13, 1.92] | 58.4 | 25.5 | -16.8 | 0.108 |
| xsmom(hold=7,k=0,mom=14) | non | 1.12 | 0.8 | [-0.23, 1.88] | 46.1 | 24.9 | -13.5 | 0.094 |
| premium(hold=1) | non | 1.4 | 0.67 | [-0.31, 1.72] | 63.3 | 26.6 | 0.0 | 0.06 |
| ml(hold=7,k=0,model=ridge) | non | 0.8 | 0.67 | [-0.34, 1.7] | 28.6 | 23.5 | -18.2 | 0.061 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | non | 1.31 | 0.73 | [-0.42, 1.82] | 12.8 | 30.9 | -23.0 | 0.071 |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | non | 0.42 | 0.63 | [-0.44, 1.65] | -5.4 | 13.1 | 3.2 | 0.052 |
| ml(hold=7,k=0,model=gbm) | non | -0.09 | 0.58 | [-0.59, 1.67] | 18.2 | 21.0 | -16.1 | 0.045 |
| ts(hold=1,l=14,s=1,sig=spring) | non | -1.07 | 0.15 | [-0.84, 1.24] | -8.9 | 20.9 | 3.4 | 0.007 |
| trend(gate=premium,hold=1,mom=14) | non | 1.27 | 0.31 | [-0.95, 1.61] | 7.1 | 49.2 | 6.4 | 0.017 |
| ts(hold=1,l=21,s=1,sig=brk) | non | 0.67 | 0.21 | [-0.96, 1.27] | -20.3 | 62.9 | 2.7 | 0.01 |
| xsmom(hold=7,k=0,mom=28) | non | 1.47 | -0.07 | [-1.02, 0.9] | -19.8 | 36.0 | -14.7 | 0.003 |
| trend(hold=1,mom=14) | non | 1.4 | 0.17 | [-1.07, 1.44] | -11.2 | 58.0 | 11.9 | 0.009 |
| trend(gate=risk_on,hold=1,mom=14) | non | 1.31 | 0.23 | [-1.09, 1.51] | -3.4 | 53.9 | 6.4 | 0.012 |
| trend(gate=nasdaq,hold=1,mom=14) | non | 1.5 | 0.17 | [-1.1, 1.43] | -9.3 | 55.8 | 8.5 | 0.009 |
| ts(hold=1,l=10,s=-1,sig=z) | non | -0.87 | -0.13 | [-1.1, 0.94] | -58.2 | 61.9 | 1.2 | 0.002 |
| ts(hold=1,l=14,s=1,sig=vwapd) | non | 0.46 | -0.05 | [-1.13, 0.9] | -49.4 | 61.2 | -10.4 | 0.003 |
| trend(hold=1,mom=28) | non | 1.59 | 0.12 | [-1.16, 1.32] | -13.0 | 59.3 | 16.6 | 0.007 |
| ts(hold=1,l=14,s=-1,sig=vwapd) | non | -0.66 | -0.22 | [-1.16, 0.84] | -61.0 | 65.7 | 0.9 | 0.001 |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | non | 0.46 | -0.09 | [-1.17, 0.86] | -53.5 | 39.4 | -1.6 | 0.002 |
| trend(hold=1,mom=7) | non | 1.57 | 0.07 | [-1.24, 1.33] | -22.1 | 63.7 | 16.5 | 0.005 |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | non | -0.62 | -0.53 | [-1.6, 0.56] | -54.1 | 31.9 | -11.5 | 0.0 |

## Journal des décisions (les 40 dernières)

- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 352864 règles explorées en 22054 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (82300688 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 262768 règles explorées en 16423 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (82563456 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 353360 règles explorées en 22085 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (82916816 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 250448 règles explorées en 15653 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (83167264 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 357344 règles explorées en 22334 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (83524608 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 256400 règles explorées en 16025 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (83781008 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 272832 règles explorées en 17052 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (84053840 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 415808 règles explorées en 25988 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (84469648 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 467440 règles explorées en 29215 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (84937088 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 354672 règles explorées en 22167 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (85291760 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 356208 règles explorées en 22263 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (85647968 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 417856 règles explorées en 26116 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (86065824 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 315936 règles explorées en 19746 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (86381760 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
