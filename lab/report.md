# Laboratoire hl-swarm — rapport

Généré le 2026-11-21 12:43 UTC · 30 marchés Hyperliquid, dernier jour clôturé 2026-11-20

Simulation uniquement : aucun ordre réel.

## Champion

**blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5)** depuis le 2026-11-14 (provisoire)

- positions simulées pour 1000 $ : AVAX +42 $, ATOM +42 $, XLM +42 $, TRX +42 $, ICP +42 $, RUNE +42 $, BTC -42 $, ETH -42 $, DOT -42 $, ARB -42 $, UNI -42 $, HBAR -42 $
- positions simulées pour 50 $ : aucune (ordres sous le minimum de 10 $)

## Contexte du jour (macro, institutions, géopolitique)

| indicateur | feu | source |
|---|---|---|
| Nasdaq au-dessus de sa moyenne 100 j | rouge | yahoo, 2131 jours |
| Stablecoins en hausse sur 30 j | rouge | DefiLlama, 3280 jours |
| Prime Coinbase positive (7 j) | rouge | Coinbase vs Binance spot, 507 jours |
| Gérants d'actifs CME en hausse (4 sem.) | rouge | CFTC, 450 semaines |
| Risque géopolitique calme | vert | indice GPR, 15295 jours |
| Hors fenêtre de décision de la Fed | vert | calendrier de la Fed (liste jusqu'à fin 2026) |
| Ton de la presse mondiale sur les cryptos en amélioration | rouge | GDELT, 469 jours |
| Presse mondiale : tensions géopolitiques calmes | vert | GDELT, 469 jours |
| Indice Fear & Greed au-dessus de sa moyenne 30 j | rouge | alternative.me, 3212 jours |

## Échanges avec Claude (connecteurs)

Dernière lecture : 2026-11-21 — réponses de Claude du 2026-11-20T23:45Z déjà lues.

- Risque signalé pour le 2026-11-20 : **none** — Aucun événement grave daté des dernières 24 heures n'a été trouvé (pas de piratage ou faillite d'exchange, de panne d'Hyperliquid, de décrochage de stablecoin ni de choc réglementaire ou militaire majeur). Les résultats trouvés concernent des événements plus anciens (ex. piratage Binance fin octobre 2026). [source](https://www.theblock.co/newsletters/the-daily/2026-10-30-binance-hack-polymarket-more-crypto-news-432181)
- Paper trading Keel au 2026-11-20 : +0.41 % en 8 jours, pire baisse 1.14 %. Paper run actif, 8 évaluations sur 7 jours, Sharpe 1,82 (court historique) ; 58 % des ordres des 7 derniers jours refusés car < 10 $ (capital simulé 1 000 $).
- Gros traders au 2026-11-20 : les plus acheteurs ETC +28, FIL +19, DOT +18 ; les plus vendeurs OP -51, SEI -61, TIA -64
- 2026-11-13 · TIA : Aucune cause précise identifiée par la recherche web pour la baisse de TIA du 13/11 : pas d'annonce ni d'incident trouvé. Le jeton est en tendance baissière depuis début novembre, dans un secteur des blockchains de couche 1 en recul. [source](https://www.coinbase.com/en-fr/price/celestia)
- 2026-11-14 · TIA : Aucune nouvelle propre à Celestia : la baisse du 13/11 accompagne le repli général du marché crypto (bitcoin en forte baisse, sentiment de peur extrême). Le jeton restait en tendance baissière sous toutes ses moyennes mobiles. [source](https://coinmarketcap.com/top-stories/6af75f3f0ada0c77afaf1484/) [source](https://tradersunion.com/news/cryptocurrency-news/show/4240045-celestia-drops-11-63percent-today/)
- 2026-11-15 · APT : Aucun catalyseur propre à Aptos n'a été trouvé (ni annonce, ni incident réseau, ni décision réglementaire). La baisse s'inscrit dans le repli général du marché du 14 novembre, le bitcoin touchant un plus bas de trois mois vers 62 000 $ sur fond de liquidations. [source](https://www.diariobitcoin.com/analisis/aptos-apt-cae-1546-el-14-de-noviembre-de-2026-y-queda-bajo-presion-tecnica/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · INJ : Aucune cause propre à Injective n'a été trouvée : la baisse d'environ 15 % a eu lieu pendant le vote sur la mise à jour Veyra, pourtant bien soutenue par la communauté. Elle suit le repli général du marché crypto du 14 novembre et une pression vendeuse déjà installée depuis plusieurs jours. [source](https://tradersunion.com/news/cryptocurrency-news/show/4250138-injective-slides-15-18percent-today-to/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · UNI : Pas de cause propre à Uniswap : selon CoinMarketCap, la baisse d'environ 15 % vient du repli général du marché (bitcoin sous 68 000 $, inflation américaine plus forte que prévu, dollar et taux en hausse). Elle a été amplifiée par la perte de la zone technique des 6 $ et un positionnement baissier des traders. [source](https://coinmarketcap.com/top-stories/6af7ddf10ada0c77afaf9379/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)

## Machine learning

Dernier entraînement le 2026-11-21 sur l'historique 2020-01 → 2026-10 (62102 exemples). Modèles en service aujourd'hui : gbm, ridge.

Ce que la régression a appris (poids les plus forts) : carry7 +0.051, brk21 +0.046, vol30 -0.046, mom7 -0.040, spring14 +0.031.

## Évolution (règles inventées par le laboratoire)

42955616 règles explorées depuis le début en 131 passages (jugées sur l'apprentissage seul), 64 présentées à la validation, 2 en service.

Balayage exhaustif : 41413668 combinaisons sur 92490684 essayées (44.8 %).

Présentées à la validation au dernier passage (2026-11-21) :

- mix(a=brk,b=illiq,gate=gpr,hold=7,k=2,la=42,lb=3,sa=1,sb=1,w=0.6) → porte non, déflaté 0.003
- mix(a=riskmom,b=illiq,gate=gpr,hold=3,k=5,la=42,lb=3,sa=1,sb=1,w=0.5) → porte non, déflaté 0.004
- mix(a=illiq,b=riskmom,gate=gpr,hold=3,k=5,la=14,lb=42,sa=1,sb=1,w=0.6) → porte non, déflaté 0.0
- mix(a=illiq,b=mom,gate=geo_news,hold=5,k=5,la=7,lb=28,sa=1,sb=1,w=0.7) → porte non, déflaté 0.003
- mix(a=z,b=illiq,gate=geo_news,hold=5,k=5,la=14,lb=3,sa=1,sb=1,w=0.4) → porte non, déflaté 0.008
- mix(a=illiq,b=brk,gate=fomc,hold=7,k=5,la=21,lb=42,sa=1,sb=1,w=0.6) → porte non, déflaté 0.001

Règles nées ici, en paper trading :

- blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) — née le 2026-11-14, Sharpe déflaté 0.538
- blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) — née le 2026-11-14, Sharpe déflaté 0.475

## Livres de paper trading

| règle | capital $ | jours | rendement % | pire baisse % | Sharpe | ordres | ordres ignorés (< 10 $) | état | test séquentiel | porte backtest |
|---|---|---|---|---|---|---|---|---|---|---|
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 7 | 0.78 | 0.45 | – | 32 | 62 | paper | continue | oui |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 1000 | 7 | 1.16 | 0.56 | – | 52 | 41 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 1000 | 7 | 1.22 | 0.37 | – | 48 | 42 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 1.46 | 0.23 | – | 34 | 73 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 0.74 | 0.29 | – | 24 | 78 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 1.46 | 0.23 | – | 34 | 73 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 0.74 | 0.29 | – | 24 | 78 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 2.93 | 0.47 | – | 34 | 73 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 1.47 | 0.58 | – | 24 | 78 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 2.93 | 0.47 | – | 34 | 73 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 1.47 | 0.58 | – | 24 | 78 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 2.93 | 0.47 | – | 34 | 73 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 1.47 | 0.58 | – | 24 | 78 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 1.46 | 0.23 | – | 34 | 73 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 0.74 | 0.29 | – | 24 | 78 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 1.92 | 0.23 | – | 43 | 64 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 1.17 | 0.29 | – | 30 | 72 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 1.46 | 0.23 | – | 34 | 73 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 1000 | 7 | 0.95 | 0.2 | – | 26 | 65 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 0.74 | 0.29 | – | 24 | 78 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 1.46 | 0.23 | – | 34 | 73 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 0.74 | 0.29 | – | 24 | 78 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 1.46 | 0.23 | – | 34 | 73 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 0.74 | 0.29 | – | 24 | 78 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 1000 | 8 | 3.39 | 0.75 | – | 54 | 75 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 1000 | 8 | 3.31 | 0.47 | – | 44 | 80 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 1000 | 8 | 4.83 | 0.38 | – | 30 | 36 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 54 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 1000 | 8 | 8.34 | 0.38 | – | 28 | 37 | paper | continue | non |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 54 | paper | continue | non |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 1000 | 8 | 2.24 | 0.52 | – | 24 | 90 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 1000 | 8 | -0.69 | 2.02 | – | 23 | 90 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 1000 | 8 | -0.84 | 2.96 | – | 18 | 42 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 50 | 8 | 0.0 | 0.0 | – | 0 | 54 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 1000 | 8 | -0.11 | 2.96 | – | 18 | 42 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 54 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 1000 | 8 | 2.92 | 0.88 | – | 19 | 92 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 50 | 8 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| carry(carry=14,hold=7,k=3) | 1000 | 8 | 4.0 | 1.03 | – | 10 | 46 | paper | continue | non |
| carry(carry=14,hold=7,k=3) | 50 | 8 | 0.0 | 0.0 | – | 0 | 54 | paper | continue | non |
| carry(carry=3,hold=7,k=0) | 1000 | 8 | 3.78 | 0.78 | – | 27 | 86 | paper | continue | oui |
| carry(carry=3,hold=7,k=0) | 50 | 8 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| carry(carry=3,hold=7,k=3) | 1000 | 8 | 0.52 | 2.56 | – | 17 | 42 | paper | continue | non |
| carry(carry=3,hold=7,k=3) | 50 | 8 | 0.0 | 0.0 | – | 0 | 54 | paper | continue | non |
| carry(carry=7,hold=7,k=0) | 1000 | 8 | 2.54 | 0.8 | – | 26 | 88 | paper | continue | oui |
| carry(carry=7,hold=7,k=0) | 50 | 8 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 1000 | 8 | 4.6 | 0.65 | – | 12 | 45 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 50 | 8 | 0.0 | 0.0 | – | 0 | 54 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 1000 | 7 | 0.76 | 1.06 | – | 24 | 66 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 7 | 2.28 | 0.52 | – | 25 | 65 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | oui |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 1000 | 7 | 0.55 | 1.01 | – | 58 | 49 | paper | continue | non |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 1000 | 7 | 1.13 | 1.22 | – | 26 | 65 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 1000 | 7 | -1.99 | 2.51 | – | 83 | 36 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 7 | 0.96 | 0.83 | – | 72 | 42 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 50 | 7 | 0.0 | 0.0 | – | 0 | 84 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 1000 | 8 | 0.44 | 1.24 | – | 42 | 68 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 1000 | 8 | 4.73 | 0.07 | – | 34 | 72 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 50 | 8 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | non |
| premium(hold=1) | 1000 | 8 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| premium(hold=1) | 50 | 8 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 1000 | 8 | -0.5 | 0.5 | – | 8 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 50 | 8 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 1000 | 8 | -0.5 | 0.5 | – | 8 | 0 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 50 | 8 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 1000 | 8 | -0.5 | 0.5 | – | 8 | 0 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 50 | 8 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(hold=1,mom=14) | 1000 | 8 | -0.88 | 1.0 | – | 12 | 1 | paper | continue | non |
| trend(hold=1,mom=14) | 50 | 8 | 0.0 | 0.0 | – | 0 | 7 | paper | continue | non |
| trend(hold=1,mom=28) | 1000 | 8 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=28) | 50 | 8 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=7) | 1000 | 8 | -1.36 | 1.36 | – | 12 | 1 | paper | continue | non |
| trend(hold=1,mom=7) | 50 | 8 | 0.0 | 0.0 | – | 0 | 7 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 1000 | 7 | -5.6 | 10.55 | – | 34 | 176 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 50 | 7 | 0.0 | 0.0 | – | 0 | 210 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 1000 | 7 | -5.94 | 10.88 | – | 32 | 178 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 50 | 7 | 0.0 | 0.0 | – | 0 | 210 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 1000 | 7 | 0.23 | 2.72 | – | 58 | 52 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 50 | 7 | 0.0 | 0.0 | – | 0 | 86 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 1000 | 7 | 5.34 | 5.62 | – | 32 | 178 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 50 | 7 | 0.0 | 0.0 | – | 0 | 210 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 1000 | 7 | 5.34 | 5.62 | – | 32 | 178 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 50 | 7 | 0.0 | 0.0 | – | 0 | 210 | paper | continue | non |
| whales(hold=1,k=0) | 1000 | 7 | -1.42 | 1.42 | – | 42 | 9 | paper | continue | non |
| whales(hold=1,k=0) | 50 | 7 | 0.0 | 0.0 | – | 0 | 36 | paper | continue | non |
| whales(hold=1,k=3) | 1000 | 7 | -2.13 | 2.13 | – | 22 | 4 | paper | continue | non |
| whales(hold=1,k=3) | 50 | 7 | 0.0 | 0.0 | – | 0 | 18 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 1000 | 8 | -3.29 | 4.17 | – | 24 | 88 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 50 | 8 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 1000 | 8 | 4.58 | 0.97 | – | 18 | 93 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 50 | 8 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | non |

## Fiche de score du catalogue (62 règles, historique long)

| règle | porte | Sharpe < 2024 | Sharpe ≥ 2024 | IC 95 % | rendement ≥ 2024 coûts ×2 % | baisse ≥ 2024 % | données propres (≥ 2026-07) % | Sharpe déflaté |
|---|---|---|---|---|---|---|---|---|
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | oui | 1.04 | 1.58 | [0.53, 2.55] | 116.6 | 12.5 | -8.9 | 0.529 |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.1 | 1.59 | [0.46, 2.62] | 95.8 | 18.2 | -8.6 | 0.538 |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | oui | 1.21 | 1.58 | [0.45, 2.63] | 87.4 | 14.8 | -12.7 | 0.53 |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | oui | 1.41 | 1.53 | [0.44, 2.57] | 58.4 | 12.0 | -10.4 | 0.495 |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | oui | 1.03 | 1.42 | [0.43, 2.35] | 80.5 | 10.7 | -6.9 | 0.421 |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | oui | 1.32 | 1.53 | [0.43, 2.6] | 84.2 | 14.9 | -12.0 | 0.491 |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | oui | 1.51 | 1.36 | [0.43, 2.33] | 93.0 | 13.6 | -11.2 | 0.382 |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | oui | 1.0 | 1.45 | [0.4, 2.42] | 105.7 | 13.1 | -9.8 | 0.443 |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | oui | 0.95 | 1.52 | [0.4, 2.47] | 83.2 | 10.2 | -7.0 | 0.488 |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.14 | 1.52 | [0.35, 2.57] | 81.4 | 14.7 | -9.4 | 0.485 |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | oui | 0.82 | 1.5 | [0.35, 2.57] | 77.4 | 11.3 | -2.7 | 0.475 |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | oui | 1.16 | 1.37 | [0.34, 2.39] | 97.4 | 15.7 | -13.8 | 0.386 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.445 |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.445 |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.45 | [0.32, 2.53] | 75.2 | 15.1 | -12.0 | 0.439 |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.41 | [0.31, 2.44] | 95.1 | 17.0 | -15.2 | 0.412 |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | oui | 0.96 | 1.37 | [0.31, 2.35] | 64.6 | 12.6 | -9.7 | 0.388 |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | oui | 1.16 | 1.4 | [0.31, 2.5] | 69.5 | 14.5 | -9.8 | 0.408 |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | oui | 1.08 | 1.4 | [0.3, 2.43] | 56.9 | 16.1 | -6.0 | 0.406 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.378 |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.35 | [0.28, 2.36] | 96.7 | 15.7 | -13.8 | 0.374 |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.378 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | oui | 0.88 | 1.26 | [0.26, 2.33] | 96.4 | 15.9 | -9.8 | 0.32 |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | oui | 1.1 | 1.28 | [0.26, 2.28] | 57.3 | 15.7 | -13.8 | 0.333 |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | oui | 1.18 | 1.28 | [0.26, 2.26] | 50.1 | 14.3 | -9.1 | 0.329 |
| carry(carry=7,hold=7,k=0) | oui | 0.7 | 1.25 | [0.25, 2.18] | 70.6 | 12.6 | 0.7 | 0.31 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | oui | 1.66 | 1.22 | [0.24, 2.22] | 47.1 | 11.2 | -0.9 | 0.298 |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | oui | 1.29 | 1.34 | [0.22, 2.42] | 60.5 | 17.1 | -14.9 | 0.364 |
| carry(carry=3,hold=7,k=0) | oui | 0.63 | 1.23 | [0.2, 2.31] | 61.8 | 14.9 | -12.9 | 0.299 |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | oui | 1.18 | 1.25 | [0.15, 2.26] | 82.8 | 17.1 | -14.5 | 0.315 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | oui | 1.35 | 1.21 | [0.12, 2.24] | 70.2 | 20.9 | -1.4 | 0.288 |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | oui | 1.34 | 1.14 | [0.07, 2.19] | 29.4 | 16.4 | -14.1 | 0.247 |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | oui | 0.21 | 0.99 | [0.07, 2.0] | 54.6 | 13.1 | -0.8 | 0.178 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | oui | 1.1 | 1.14 | [0.04, 2.31] | 119.6 | 29.3 | -8.0 | 0.245 |
| carry(carry=7,hold=7,k=3) | oui | 0.51 | 1.07 | [0.04, 2.06] | 71.8 | 19.6 | -6.1 | 0.214 |
| carry(carry=14,hold=7,k=0) | oui | 0.42 | 1.09 | [0.04, 2.09] | 58.4 | 13.6 | -1.8 | 0.223 |
| whales(hold=1,k=0) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.005 |
| whales(hold=1,k=3) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.005 |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | non | -0.35 | 1.06 | [-0.06, 2.23] | 81.8 | 27.3 | -12.2 | 0.211 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | non | 1.42 | 1.04 | [-0.08, 2.1] | 97.5 | 22.3 | -15.0 | 0.199 |
| carry(carry=14,hold=7,k=3) | non | 0.43 | 0.91 | [-0.08, 1.83] | 70.6 | 21.0 | 0.6 | 0.144 |
| carry(carry=3,hold=7,k=3) | non | 0.92 | 0.88 | [-0.13, 1.92] | 58.4 | 25.5 | -16.8 | 0.125 |
| xsmom(hold=7,k=0,mom=14) | non | 1.12 | 0.8 | [-0.23, 1.88] | 46.1 | 24.9 | -13.5 | 0.108 |
| premium(hold=1) | non | 1.4 | 0.67 | [-0.31, 1.72] | 63.3 | 26.6 | 0.0 | 0.071 |
| ml(hold=7,k=0,model=ridge) | non | 0.8 | 0.67 | [-0.34, 1.7] | 28.6 | 23.5 | -18.2 | 0.072 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | non | 1.31 | 0.73 | [-0.42, 1.82] | 12.8 | 30.9 | -23.0 | 0.083 |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | non | 0.42 | 0.63 | [-0.44, 1.65] | -5.4 | 13.1 | 3.2 | 0.062 |
| ml(hold=7,k=0,model=gbm) | non | -0.09 | 0.58 | [-0.59, 1.67] | 18.2 | 21.0 | -16.1 | 0.054 |
| ts(hold=1,l=14,s=1,sig=spring) | non | -1.07 | 0.15 | [-0.84, 1.24] | -8.9 | 20.9 | 3.4 | 0.009 |
| trend(gate=premium,hold=1,mom=14) | non | 1.27 | 0.31 | [-0.95, 1.61] | 7.1 | 49.2 | 6.4 | 0.02 |
| ts(hold=1,l=21,s=1,sig=brk) | non | 0.67 | 0.21 | [-0.96, 1.27] | -20.3 | 62.9 | 2.7 | 0.013 |
| xsmom(hold=7,k=0,mom=28) | non | 1.47 | -0.07 | [-1.02, 0.9] | -19.8 | 36.0 | -14.7 | 0.003 |
| trend(hold=1,mom=14) | non | 1.4 | 0.17 | [-1.07, 1.44] | -11.2 | 58.0 | 11.9 | 0.011 |
| trend(gate=risk_on,hold=1,mom=14) | non | 1.31 | 0.23 | [-1.09, 1.51] | -3.4 | 53.9 | 6.4 | 0.014 |
| trend(gate=nasdaq,hold=1,mom=14) | non | 1.5 | 0.17 | [-1.1, 1.43] | -9.3 | 55.8 | 8.5 | 0.011 |
| ts(hold=1,l=10,s=-1,sig=z) | non | -0.87 | -0.13 | [-1.1, 0.94] | -58.2 | 61.9 | 1.2 | 0.002 |
| ts(hold=1,l=14,s=1,sig=vwapd) | non | 0.46 | -0.05 | [-1.13, 0.9] | -49.4 | 61.2 | -10.4 | 0.004 |
| trend(hold=1,mom=28) | non | 1.59 | 0.12 | [-1.16, 1.32] | -13.0 | 59.3 | 16.6 | 0.008 |
| ts(hold=1,l=14,s=-1,sig=vwapd) | non | -0.66 | -0.22 | [-1.16, 0.84] | -61.0 | 65.7 | 0.9 | 0.002 |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | non | 0.46 | -0.09 | [-1.17, 0.86] | -53.5 | 39.4 | -1.6 | 0.003 |
| trend(hold=1,mom=7) | non | 1.57 | 0.07 | [-1.24, 1.33] | -22.1 | 63.7 | 16.5 | 0.007 |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | non | -0.62 | -0.53 | [-1.6, 0.56] | -54.1 | 31.9 | -11.5 | 0.0 |

## Journal des décisions (les 40 dernières)

- 2026-11-20 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-20 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-20 — ÉVOLUTION : 355008 règles explorées en 22188 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (38929616 explorées et 58 présentées depuis le début)
- 2026-11-20 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-20 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-20 — ÉVOLUTION : 342688 règles explorées en 21418 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (39272304 explorées et 58 présentées depuis le début)
- 2026-11-20 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-20 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-20 — ÉVOLUTION : 257488 règles explorées en 16093 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (39529792 explorées et 58 présentées depuis le début)
- 2026-11-20 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 503696 règles explorées en 31481 générations, 6 présentées à la validation (0 en attente du prochain examen), 2 règles nées en service (40033488 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 254672 règles explorées en 15917 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (40288160 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 253856 règles explorées en 15866 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (40542016 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 256592 règles explorées en 16037 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (40798608 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 354016 règles explorées en 22126 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (41152624 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 351648 règles explorées en 21978 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (41504272 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 419920 règles explorées en 26245 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (41924192 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 356288 règles explorées en 22268 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (42280480 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 255312 règles explorées en 15957 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (42535792 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-21 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-21 — ÉVOLUTION : 419824 règles explorées en 26239 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (42955616 explorées et 64 présentées depuis le début)
- 2026-11-21 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
