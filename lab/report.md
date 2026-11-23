# Laboratoire hl-swarm — rapport

Généré le 2026-11-23 07:31 UTC · 30 marchés Hyperliquid, dernier jour clôturé 2026-11-22

Simulation uniquement : aucun ordre réel.

## Champion

**blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5)** depuis le 2026-11-14 (provisoire)

- positions simulées pour 1000 $ : AVAX +42 $, ATOM +42 $, XLM +42 $, TRX +42 $, ICP +42 $, RUNE +42 $, BTC -42 $, ETH -42 $, DOT -42 $, ARB -42 $, UNI -42 $, HBAR -42 $
- positions simulées pour 50 $ : aucune (ordres sous le minimum de 10 $)

## Contexte du jour (macro, institutions, géopolitique)

| indicateur | feu | source |
|---|---|---|
| Nasdaq au-dessus de sa moyenne 100 j | rouge | yahoo, 2131 jours |
| Stablecoins en hausse sur 30 j | rouge | DefiLlama, 3282 jours |
| Prime Coinbase positive (7 j) | rouge | Coinbase vs Binance spot, 509 jours |
| Gérants d'actifs CME en hausse (4 sem.) | rouge | CFTC, 450 semaines |
| Risque géopolitique calme | vert | indice GPR, 15295 jours |
| Hors fenêtre de décision de la Fed | vert | calendrier de la Fed (liste jusqu'à fin 2026) |
| Ton de la presse mondiale sur les cryptos en amélioration | indisponible | indisponible (RuntimeError) |
| Presse mondiale : tensions géopolitiques calmes | vert | GDELT, 469 jours |
| Indice Fear & Greed au-dessus de sa moyenne 30 j | rouge | alternative.me, 3214 jours |

## Échanges avec Claude (connecteurs)

Dernière lecture : 2026-11-23 — réponses de Claude du 2026-11-22T23:41Z déjà lues.

- Risque signalé pour le 2026-11-22 : **none** — Aucun événement grave daté des dernières 24 heures n'a été trouvé (piratage ou faillite d'exchange, panne d'Hyperliquid, décrochage de stablecoin, choc réglementaire, escalade militaire). Les résultats de recherche ne contenaient que des articles anciens ou sans date fiable. 
- Paper trading Keel au 2026-11-22 : +1.08 % en 10 jours, pire baisse 1.14 %. Paper Keel (1 000 $ simulés) en cours depuis le 13/11 ; 10 évaluations ; P&L net -23,2 $ après frais mais rendement total +1,08 % selon Keel ; 57 % des ordres des 7 derniers jours refusés car < 10 $ ;
- Gros traders au 2026-11-22 : les plus acheteurs DOT +24, FIL +22, BCH +19 ; les plus vendeurs SEI -55, LTC -61, TIA -65
- 2026-11-13 · TIA : Aucune cause précise identifiée par la recherche web pour la baisse de TIA du 13/11 : pas d'annonce ni d'incident trouvé. Le jeton est en tendance baissière depuis début novembre, dans un secteur des blockchains de couche 1 en recul. [source](https://www.coinbase.com/en-fr/price/celestia)
- 2026-11-14 · TIA : Aucune nouvelle propre à Celestia : la baisse du 13/11 accompagne le repli général du marché crypto (bitcoin en forte baisse, sentiment de peur extrême). Le jeton restait en tendance baissière sous toutes ses moyennes mobiles. [source](https://coinmarketcap.com/top-stories/6af75f3f0ada0c77afaf1484/) [source](https://tradersunion.com/news/cryptocurrency-news/show/4240045-celestia-drops-11-63percent-today/)
- 2026-11-15 · APT : Aucun catalyseur propre à Aptos n'a été trouvé (ni annonce, ni incident réseau, ni décision réglementaire). La baisse s'inscrit dans le repli général du marché du 14 novembre, le bitcoin touchant un plus bas de trois mois vers 62 000 $ sur fond de liquidations. [source](https://www.diariobitcoin.com/analisis/aptos-apt-cae-1546-el-14-de-noviembre-de-2026-y-queda-bajo-presion-tecnica/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · INJ : Aucune cause propre à Injective n'a été trouvée : la baisse d'environ 15 % a eu lieu pendant le vote sur la mise à jour Veyra, pourtant bien soutenue par la communauté. Elle suit le repli général du marché crypto du 14 novembre et une pression vendeuse déjà installée depuis plusieurs jours. [source](https://tradersunion.com/news/cryptocurrency-news/show/4250138-injective-slides-15-18percent-today-to/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · UNI : Pas de cause propre à Uniswap : selon CoinMarketCap, la baisse d'environ 15 % vient du repli général du marché (bitcoin sous 68 000 $, inflation américaine plus forte que prévu, dollar et taux en hausse). Elle a été amplifiée par la perte de la zone technique des 6 $ et un positionnement baissier des traders. [source](https://coinmarketcap.com/top-stories/6af7ddf10ada0c77afaf9379/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)

## Machine learning

Dernier entraînement le 2026-11-23 sur l'historique 2020-01 → 2026-10 (62102 exemples). Modèles en service aujourd'hui : gbm, ridge.

Ce que la régression a appris (poids les plus forts) : carry7 +0.051, brk21 +0.046, vol30 -0.046, mom7 -0.040, spring14 +0.031.

## Évolution (règles inventées par le laboratoire)

55649696 règles explorées depuis le début en 169 passages (jugées sur l'apprentissage seul), 76 présentées à la validation, 2 en service.

Balayage exhaustif : 54107753 combinaisons sur 92490684 essayées (58.5 %).

Présentées à la validation au dernier passage (2026-11-23) :

- mix(a=brk,b=illiq,gate=geo_news,hold=7,k=5,la=42,lb=14,sa=1,sb=1,w=0.4) → porte non, déflaté 0.0
- mix(a=z,b=illiq,gate=geo_news,hold=3,k=5,la=28,lb=3,sa=1,sb=1,w=0.4) → porte non, déflaté 0.004
- mix(a=illiq,b=mom,gate=cot,hold=5,k=5,la=2,lb=28,sa=1,sb=1,w=0.7) → porte non, déflaté 0.001
- mix(a=illiq,b=brk,gate=news_tone,hold=14,k=5,la=42,lb=28,sa=1,sb=1,w=0.6) → porte non, déflaté 0.0
- mix(a=illiq,b=riskmom,gate=geo_news,hold=2,k=5,la=7,lb=42,sa=1,sb=1,w=0.6) → porte non, déflaté 0.001
- mix(a=mom,b=illiq,hold=2,k=5,la=28,lb=10,sa=1,sb=1,w=0.4) → porte non, déflaté 0.002

Règles nées ici, en paper trading :

- blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) — née le 2026-11-14, Sharpe déflaté 0.525
- blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) — née le 2026-11-14, Sharpe déflaté 0.463

## Livres de paper trading

| règle | capital $ | jours | rendement % | pire baisse % | Sharpe | ordres | ordres ignorés (< 10 $) | état | test séquentiel | porte backtest |
|---|---|---|---|---|---|---|---|---|---|---|
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 9 | 0.11 | 0.66 | – | 40 | 82 | paper | continue | oui |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 1000 | 9 | -0.31 | 1.45 | – | 58 | 62 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 1000 | 9 | 0.09 | 1.28 | – | 48 | 66 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 0.72 | 0.73 | – | 40 | 94 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.18 | 0.64 | – | 24 | 102 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 0.72 | 0.73 | – | 40 | 94 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.18 | 0.64 | – | 24 | 102 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 1.44 | 1.45 | – | 40 | 94 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.34 | 1.28 | – | 24 | 102 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 1.44 | 1.45 | – | 40 | 94 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.34 | 1.28 | – | 24 | 102 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 1.44 | 1.45 | – | 40 | 94 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.34 | 1.28 | – | 24 | 102 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 0.72 | 0.73 | – | 40 | 94 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.18 | 0.64 | – | 24 | 102 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 0.42 | 1.48 | – | 60 | 74 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.01 | 1.28 | – | 42 | 84 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 0.72 | 0.73 | – | 40 | 94 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 1000 | 9 | 0.65 | 0.3 | – | 26 | 89 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.18 | 0.64 | – | 24 | 102 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 0.72 | 0.73 | – | 40 | 94 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.18 | 0.64 | – | 24 | 102 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 0.72 | 0.73 | – | 40 | 94 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 0.18 | 0.64 | – | 24 | 102 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 1000 | 10 | 2.63 | 0.75 | – | 60 | 96 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 132 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 1000 | 10 | 1.81 | 1.45 | – | 50 | 101 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 132 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 1000 | 10 | 4.3 | 0.51 | – | 40 | 43 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 66 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 1000 | 10 | 6.65 | 1.56 | – | 36 | 45 | paper | continue | non |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 66 | paper | continue | non |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 1000 | 10 | 1.1 | 1.28 | – | 24 | 114 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 132 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 1000 | 10 | -1.68 | 2.34 | – | 23 | 114 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 132 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 1000 | 10 | -1.0 | 2.96 | – | 18 | 54 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 50 | 10 | 0.0 | 0.0 | – | 0 | 66 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 1000 | 10 | -0.44 | 2.96 | – | 18 | 54 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 66 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 1000 | 10 | 1.97 | 0.98 | – | 19 | 116 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 50 | 10 | 0.0 | 0.0 | – | 0 | 132 | paper | continue | oui |
| carry(carry=14,hold=7,k=3) | 1000 | 10 | 3.25 | 1.57 | – | 10 | 58 | paper | continue | non |
| carry(carry=14,hold=7,k=3) | 50 | 10 | 0.0 | 0.0 | – | 0 | 66 | paper | continue | non |
| carry(carry=3,hold=7,k=0) | 1000 | 10 | 3.08 | 0.82 | – | 27 | 110 | paper | continue | oui |
| carry(carry=3,hold=7,k=0) | 50 | 10 | 0.0 | 0.0 | – | 0 | 132 | paper | continue | oui |
| carry(carry=3,hold=7,k=3) | 1000 | 10 | 0.49 | 2.56 | – | 17 | 54 | paper | continue | non |
| carry(carry=3,hold=7,k=3) | 50 | 10 | 0.0 | 0.0 | – | 0 | 66 | paper | continue | non |
| carry(carry=7,hold=7,k=0) | 1000 | 10 | 2.21 | 0.8 | – | 26 | 112 | paper | continue | oui |
| carry(carry=7,hold=7,k=0) | 50 | 10 | 0.0 | 0.0 | – | 0 | 132 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 1000 | 10 | 4.78 | 0.79 | – | 12 | 57 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 50 | 10 | 0.0 | 0.0 | – | 0 | 66 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 1000 | 9 | 0.42 | 1.06 | – | 24 | 90 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 9 | 2.14 | 0.52 | – | 25 | 89 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | oui |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 1000 | 9 | -0.32 | 1.01 | – | 72 | 66 | paper | continue | non |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 1000 | 9 | 1.15 | 1.22 | – | 26 | 89 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 1000 | 9 | -2.95 | 2.95 | – | 104 | 48 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 9 | 1.3 | 0.83 | – | 102 | 51 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 50 | 9 | 0.0 | 0.0 | – | 0 | 108 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 1000 | 10 | 1.31 | 1.24 | – | 46 | 90 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 1000 | 10 | 5.02 | 0.49 | – | 34 | 96 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 50 | 10 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | non |
| premium(hold=1) | 1000 | 10 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| premium(hold=1) | 50 | 10 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 1000 | 10 | -0.5 | 0.5 | – | 8 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 50 | 10 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 1000 | 10 | -0.5 | 0.5 | – | 8 | 0 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 50 | 10 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 1000 | 10 | -0.5 | 0.5 | – | 8 | 0 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 50 | 10 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(hold=1,mom=14) | 1000 | 10 | -0.88 | 1.0 | – | 12 | 1 | paper | continue | non |
| trend(hold=1,mom=14) | 50 | 10 | 0.0 | 0.0 | – | 0 | 7 | paper | continue | non |
| trend(hold=1,mom=28) | 1000 | 10 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=28) | 50 | 10 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=7) | 1000 | 10 | -1.36 | 1.36 | – | 17 | 1 | paper | continue | non |
| trend(hold=1,mom=7) | 50 | 10 | 0.0 | 0.0 | – | 0 | 10 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 1000 | 9 | -4.23 | 10.55 | – | 34 | 236 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 50 | 9 | 0.0 | 0.0 | – | 0 | 270 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 1000 | 9 | -4.57 | 10.88 | – | 32 | 238 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 50 | 9 | 0.0 | 0.0 | – | 0 | 270 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 1000 | 9 | 1.21 | 2.82 | – | 77 | 90 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 50 | 9 | 0.0 | 0.0 | – | 0 | 143 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 1000 | 9 | 3.81 | 5.62 | – | 32 | 238 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 50 | 9 | 0.0 | 0.0 | – | 0 | 270 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 1000 | 9 | 3.81 | 5.62 | – | 32 | 238 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 50 | 9 | 0.0 | 0.0 | – | 0 | 270 | paper | continue | non |
| whales(hold=1,k=0) | 1000 | 9 | -1.51 | 1.51 | – | 58 | 19 | paper | continue | non |
| whales(hold=1,k=0) | 50 | 9 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | non |
| whales(hold=1,k=3) | 1000 | 9 | -1.9 | 2.38 | – | 30 | 9 | paper | continue | non |
| whales(hold=1,k=3) | 50 | 9 | 0.0 | 0.0 | – | 0 | 24 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 1000 | 10 | -4.37 | 5.0 | – | 24 | 112 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 50 | 10 | 0.0 | 0.0 | – | 0 | 132 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 1000 | 10 | 4.4 | 0.97 | – | 18 | 117 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 50 | 10 | 0.0 | 0.0 | – | 0 | 132 | paper | continue | non |

## Fiche de score du catalogue (62 règles, historique long)

| règle | porte | Sharpe < 2024 | Sharpe ≥ 2024 | IC 95 % | rendement ≥ 2024 coûts ×2 % | baisse ≥ 2024 % | données propres (≥ 2026-07) % | Sharpe déflaté |
|---|---|---|---|---|---|---|---|---|
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | oui | 1.04 | 1.58 | [0.53, 2.55] | 116.6 | 12.5 | -8.9 | 0.516 |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.1 | 1.59 | [0.46, 2.62] | 95.8 | 18.2 | -8.6 | 0.525 |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | oui | 1.21 | 1.58 | [0.45, 2.63] | 87.4 | 14.8 | -12.7 | 0.517 |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | oui | 1.41 | 1.53 | [0.44, 2.57] | 58.4 | 12.0 | -10.4 | 0.482 |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | oui | 1.03 | 1.42 | [0.43, 2.35] | 80.5 | 10.7 | -6.9 | 0.409 |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | oui | 1.32 | 1.53 | [0.43, 2.6] | 84.2 | 14.9 | -12.0 | 0.478 |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | oui | 1.51 | 1.36 | [0.43, 2.33] | 93.0 | 13.6 | -11.2 | 0.37 |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | oui | 1.0 | 1.45 | [0.4, 2.42] | 105.7 | 13.1 | -9.8 | 0.431 |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | oui | 0.95 | 1.52 | [0.4, 2.47] | 83.2 | 10.2 | -7.0 | 0.475 |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.14 | 1.52 | [0.35, 2.57] | 81.4 | 14.7 | -9.4 | 0.472 |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | oui | 0.82 | 1.5 | [0.35, 2.57] | 77.4 | 11.3 | -2.7 | 0.463 |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | oui | 1.16 | 1.37 | [0.34, 2.39] | 97.4 | 15.7 | -13.8 | 0.375 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.433 |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.433 |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.45 | [0.32, 2.53] | 75.2 | 15.1 | -12.0 | 0.427 |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.41 | [0.31, 2.44] | 95.1 | 17.0 | -15.2 | 0.399 |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | oui | 0.96 | 1.37 | [0.31, 2.35] | 64.6 | 12.6 | -9.7 | 0.376 |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | oui | 1.16 | 1.4 | [0.31, 2.5] | 69.5 | 14.5 | -9.8 | 0.396 |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | oui | 1.08 | 1.4 | [0.3, 2.43] | 56.9 | 16.1 | -6.0 | 0.394 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.366 |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.35 | [0.28, 2.36] | 96.7 | 15.7 | -13.8 | 0.363 |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.366 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | oui | 0.88 | 1.26 | [0.26, 2.33] | 96.4 | 15.9 | -9.8 | 0.309 |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | oui | 1.1 | 1.28 | [0.26, 2.28] | 57.3 | 15.7 | -13.8 | 0.322 |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | oui | 1.18 | 1.28 | [0.26, 2.26] | 50.1 | 14.3 | -9.1 | 0.318 |
| carry(carry=7,hold=7,k=0) | oui | 0.7 | 1.25 | [0.25, 2.18] | 70.6 | 12.6 | 0.7 | 0.299 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | oui | 1.66 | 1.22 | [0.24, 2.22] | 47.1 | 11.2 | -0.9 | 0.287 |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | oui | 1.29 | 1.34 | [0.22, 2.42] | 60.5 | 17.1 | -14.9 | 0.353 |
| carry(carry=3,hold=7,k=0) | oui | 0.63 | 1.23 | [0.2, 2.31] | 61.8 | 14.9 | -12.9 | 0.288 |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | oui | 1.18 | 1.25 | [0.15, 2.26] | 82.8 | 17.1 | -14.5 | 0.304 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | oui | 1.35 | 1.21 | [0.12, 2.24] | 70.2 | 20.9 | -1.4 | 0.277 |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | oui | 1.34 | 1.14 | [0.07, 2.19] | 29.4 | 16.4 | -14.1 | 0.237 |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | oui | 0.21 | 0.99 | [0.07, 2.0] | 54.6 | 13.1 | -0.8 | 0.17 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | oui | 1.1 | 1.14 | [0.04, 2.31] | 119.6 | 29.3 | -8.0 | 0.236 |
| carry(carry=7,hold=7,k=3) | oui | 0.51 | 1.07 | [0.04, 2.06] | 71.8 | 19.6 | -6.1 | 0.205 |
| carry(carry=14,hold=7,k=0) | oui | 0.42 | 1.09 | [0.04, 2.09] | 58.4 | 13.6 | -1.8 | 0.214 |
| whales(hold=1,k=0) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.004 |
| whales(hold=1,k=3) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.004 |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | non | -0.35 | 1.06 | [-0.06, 2.23] | 81.8 | 27.3 | -12.2 | 0.202 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | non | 1.42 | 1.04 | [-0.08, 2.1] | 97.5 | 22.3 | -15.0 | 0.191 |
| carry(carry=14,hold=7,k=3) | non | 0.43 | 0.91 | [-0.08, 1.83] | 70.6 | 21.0 | 0.6 | 0.137 |
| carry(carry=3,hold=7,k=3) | non | 0.92 | 0.88 | [-0.13, 1.92] | 58.4 | 25.5 | -16.8 | 0.119 |
| xsmom(hold=7,k=0,mom=14) | non | 1.12 | 0.8 | [-0.23, 1.88] | 46.1 | 24.9 | -13.5 | 0.103 |
| premium(hold=1) | non | 1.4 | 0.67 | [-0.31, 1.72] | 63.3 | 26.6 | 0.0 | 0.067 |
| ml(hold=7,k=0,model=ridge) | non | 0.8 | 0.67 | [-0.34, 1.7] | 28.6 | 23.5 | -18.2 | 0.068 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | non | 1.31 | 0.73 | [-0.42, 1.82] | 12.8 | 30.9 | -23.0 | 0.079 |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | non | 0.42 | 0.63 | [-0.44, 1.65] | -5.4 | 13.1 | 3.2 | 0.058 |
| ml(hold=7,k=0,model=gbm) | non | -0.09 | 0.58 | [-0.59, 1.67] | 18.2 | 21.0 | -16.1 | 0.051 |
| ts(hold=1,l=14,s=1,sig=spring) | non | -1.07 | 0.15 | [-0.84, 1.24] | -8.9 | 20.9 | 3.4 | 0.009 |
| trend(gate=premium,hold=1,mom=14) | non | 1.27 | 0.31 | [-0.95, 1.61] | 7.1 | 49.2 | 6.4 | 0.019 |
| ts(hold=1,l=21,s=1,sig=brk) | non | 0.67 | 0.21 | [-0.96, 1.27] | -20.3 | 62.9 | 2.7 | 0.012 |
| xsmom(hold=7,k=0,mom=28) | non | 1.47 | -0.07 | [-1.02, 0.9] | -19.8 | 36.0 | -14.7 | 0.003 |
| trend(hold=1,mom=14) | non | 1.4 | 0.17 | [-1.07, 1.44] | -11.2 | 58.0 | 11.9 | 0.01 |
| trend(gate=risk_on,hold=1,mom=14) | non | 1.31 | 0.23 | [-1.09, 1.51] | -3.4 | 53.9 | 6.4 | 0.013 |
| trend(gate=nasdaq,hold=1,mom=14) | non | 1.5 | 0.17 | [-1.1, 1.43] | -9.3 | 55.8 | 8.5 | 0.01 |
| ts(hold=1,l=10,s=-1,sig=z) | non | -0.87 | -0.13 | [-1.1, 0.94] | -58.2 | 61.9 | 1.2 | 0.002 |
| ts(hold=1,l=14,s=1,sig=vwapd) | non | 0.46 | -0.05 | [-1.13, 0.9] | -49.4 | 61.2 | -10.4 | 0.003 |
| trend(hold=1,mom=28) | non | 1.59 | 0.12 | [-1.16, 1.32] | -13.0 | 59.3 | 16.6 | 0.008 |
| ts(hold=1,l=14,s=-1,sig=vwapd) | non | -0.66 | -0.22 | [-1.16, 0.84] | -61.0 | 65.7 | 0.9 | 0.001 |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | non | 0.46 | -0.09 | [-1.17, 0.86] | -53.5 | 39.4 | -1.6 | 0.003 |
| trend(hold=1,mom=7) | non | 1.57 | 0.07 | [-1.24, 1.33] | -22.1 | 63.7 | 16.5 | 0.006 |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | non | -0.62 | -0.53 | [-1.6, 0.56] | -54.1 | 31.9 | -11.5 | 0.0 |

## Journal des décisions (les 40 dernières)

- 2026-11-22 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-22 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-22 — ÉVOLUTION : 271344 règles explorées en 16959 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (51804592 explorées et 70 présentées depuis le début)
- 2026-11-22 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-22 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-22 — ÉVOLUTION : 318944 règles explorées en 19934 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (52123536 explorées et 70 présentées depuis le début)
- 2026-11-22 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-22 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-22 — ÉVOLUTION : 418752 règles explorées en 26172 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (52542288 explorées et 70 présentées depuis le début)
- 2026-11-22 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-22 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-22 — ÉVOLUTION : 255952 règles explorées en 15997 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (52798240 explorées et 70 présentées depuis le début)
- 2026-11-22 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-22 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-22 — ÉVOLUTION : 508848 règles explorées en 31803 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (53307088 explorées et 70 présentées depuis le début)
- 2026-11-22 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-22 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-22 — ÉVOLUTION : 254704 règles explorées en 15919 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (53561792 explorées et 70 présentées depuis le début)
- 2026-11-22 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-22 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-22 — ÉVOLUTION : 319104 règles explorées en 19944 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (53880896 explorées et 70 présentées depuis le début)
- 2026-11-22 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-23 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-23 — ÉVOLUTION : 257456 règles explorées en 16091 générations, 6 présentées à la validation (0 en attente du prochain examen), 2 règles nées en service (54138352 explorées et 76 présentées depuis le début)
- 2026-11-23 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-23 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-23 — ÉVOLUTION : 256496 règles explorées en 16031 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (54394848 explorées et 76 présentées depuis le début)
- 2026-11-23 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-23 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-23 — ÉVOLUTION : 258544 règles explorées en 16159 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (54653392 explorées et 76 présentées depuis le début)
- 2026-11-23 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-23 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-23 — ÉVOLUTION : 318560 règles explorées en 19910 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (54971952 explorées et 76 présentées depuis le début)
- 2026-11-23 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-23 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-23 — ÉVOLUTION : 320176 règles explorées en 20011 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (55292128 explorées et 76 présentées depuis le début)
- 2026-11-23 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-23 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-23 — ÉVOLUTION : 357568 règles explorées en 22348 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (55649696 explorées et 76 présentées depuis le début)
- 2026-11-23 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
