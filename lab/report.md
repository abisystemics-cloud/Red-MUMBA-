# Laboratoire hl-swarm — rapport

Généré le 2026-11-18 04:15 UTC · 30 marchés Hyperliquid, dernier jour clôturé 2026-11-17

Simulation uniquement : aucun ordre réel.

## Champion

**blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5)** depuis le 2026-11-14 (provisoire)

- positions simulées pour 1000 $ : AVAX +42 $, ATOM +42 $, INJ +42 $, AAVE +42 $, ICP +42 $, RUNE +42 $, BTC -42 $, XRP -42 $, NEAR -42 $, SEI -42 $, FIL -42 $, HBAR -42 $
- positions simulées pour 50 $ : aucune (ordres sous le minimum de 10 $)

## Contexte du jour (macro, institutions, géopolitique)

| indicateur | feu | source |
|---|---|---|
| Nasdaq au-dessus de sa moyenne 100 j | rouge | yahoo, 2128 jours |
| Stablecoins en hausse sur 30 j | rouge | DefiLlama, 3277 jours |
| Prime Coinbase positive (7 j) | rouge | Coinbase vs Binance spot, 504 jours |
| Gérants d'actifs CME en hausse (4 sem.) | rouge | CFTC, 449 semaines |
| Risque géopolitique calme | vert | indice GPR, 15295 jours |
| Hors fenêtre de décision de la Fed | vert | calendrier de la Fed (liste jusqu'à fin 2026) |
| Ton de la presse mondiale sur les cryptos en amélioration | rouge | GDELT, 467 jours |
| Presse mondiale : tensions géopolitiques calmes | vert | GDELT, 467 jours |
| Indice Fear & Greed au-dessus de sa moyenne 30 j | rouge | alternative.me, 3209 jours |

## Échanges avec Claude (connecteurs)

Dernière lecture : 2026-11-18 — réponses de Claude du 2026-11-16T23:42Z déjà lues.

- Risque signalé pour le 2026-11-16 : **elevated** — Les tensions Iran–États-Unis dans le Golfe restent vives : après les tirs de drones iraniens des 15–16 novembre contre un radar américain à Bahreïn (interceptés), le Conseil de coopération du Golfe dénonce une « provocation flagrante », des frappes américaines sur la côte sud de l'Iran sont rapportées et un troisième porte-avions américain est arrivé dans la région. Côté crypto, la plateforme de p [source](https://www.thenationalnews.com/news/gulf/2026/11/16/iran-attacks-bahrain-in-blatant-challenge-to-peace-push/) [source](https://www.military.com/iran-targets-us-military-base-in-2nd-bahrain-drone-attack-in-3-days) [source](https://insights.niacouncil.org/p/iran-and-us-exchange-new-strikes) [source](https://www.thenationalnews.com/news/us/2026/11/16/uss-theodore-roosevelt-middle-east-centcom/) [source](https://www.coindesk.com/tech/2026/11/16/lighter-suspends-all-withdrawals-after-usd10-4-million-crypto-exploit)
- Paper trading Keel au 2026-11-16 : +0.60 % en 4 jours, pire baisse 0.70 %. Paper Keel en marche, 4 évaluations (dernière le 16/11 12:00 UTC), 51 ordres exécutés, valeur du compte 1 006,56 $ ; 45 des 96 derniers ordres ignorés car sous le minimum de 10 $, dont 14 sorties (pos
- Gros traders au 2026-11-16 : les plus acheteurs ETC +18, FIL +16, DOT +15 ; les plus vendeurs SOL -38, OP -54, SEI -59
- 2026-11-13 · TIA : Aucune cause précise identifiée par la recherche web pour la baisse de TIA du 13/11 : pas d'annonce ni d'incident trouvé. Le jeton est en tendance baissière depuis début novembre, dans un secteur des blockchains de couche 1 en recul. [source](https://www.coinbase.com/en-fr/price/celestia)
- 2026-11-14 · TIA : Aucune nouvelle propre à Celestia : la baisse du 13/11 accompagne le repli général du marché crypto (bitcoin en forte baisse, sentiment de peur extrême). Le jeton restait en tendance baissière sous toutes ses moyennes mobiles. [source](https://coinmarketcap.com/top-stories/6af75f3f0ada0c77afaf1484/) [source](https://tradersunion.com/news/cryptocurrency-news/show/4240045-celestia-drops-11-63percent-today/)
- 2026-11-15 · APT : Aucun catalyseur propre à Aptos n'a été trouvé (ni annonce, ni incident réseau, ni décision réglementaire). La baisse s'inscrit dans le repli général du marché du 14 novembre, le bitcoin touchant un plus bas de trois mois vers 62 000 $ sur fond de liquidations. [source](https://www.diariobitcoin.com/analisis/aptos-apt-cae-1546-el-14-de-noviembre-de-2026-y-queda-bajo-presion-tecnica/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · INJ : Aucune cause propre à Injective n'a été trouvée : la baisse d'environ 15 % a eu lieu pendant le vote sur la mise à jour Veyra, pourtant bien soutenue par la communauté. Elle suit le repli général du marché crypto du 14 novembre et une pression vendeuse déjà installée depuis plusieurs jours. [source](https://tradersunion.com/news/cryptocurrency-news/show/4250138-injective-slides-15-18percent-today-to/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · UNI : Pas de cause propre à Uniswap : selon CoinMarketCap, la baisse d'environ 15 % vient du repli général du marché (bitcoin sous 68 000 $, inflation américaine plus forte que prévu, dollar et taux en hausse). Elle a été amplifiée par la perte de la zone technique des 6 $ et un positionnement baissier des traders. [source](https://coinmarketcap.com/top-stories/6af7ddf10ada0c77afaf9379/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)

## Machine learning

Dernier entraînement le 2026-11-18 sur l'historique 2020-01 → 2026-10 (62102 exemples). Modèles en service aujourd'hui : gbm, ridge.

Ce que la régression a appris (poids les plus forts) : carry7 +0.051, brk21 +0.046, vol30 -0.046, mom7 -0.040, spring14 +0.031.

## Évolution (règles inventées par le laboratoire)

22447696 règles explorées depuis le début en 72 passages (jugées sur l'apprentissage seul), 46 présentées à la validation, 2 en service.

Balayage exhaustif : 20905742 combinaisons sur 92490684 essayées (22.6 %).

Présentées à la validation au dernier passage (2026-11-18) :

- mix(a=illiq,b=z,gate=geo_news,hold=3,k=5,la=3,lb=28,sa=1,sb=1,w=0.6) → porte non, déflaté 0.005
- mix(a=illiq,b=riskmom,gate=geo_news,hold=3,k=5,la=5,lb=42,sa=1,sb=1,w=0.6) → porte non, déflaté 0.002
- mix(a=z,b=illiq,gate=news_tone,hold=5,k=5,la=21,lb=3,sa=1,sb=1,w=0.3) → porte non, déflaté 0.001
- mix(a=brk,b=illiq,gate=gpr,hold=7,k=5,la=42,lb=21,sa=1,sb=1,w=0.3) → porte non, déflaté 0.0
- mix(a=illiq,b=brk,gate=gpr,hold=7,k=5,la=21,lb=42,sa=1,sb=1,w=0.7) → porte non, déflaté 0.0
- mix(a=mom,b=illiq,gate=geo_news,hold=2,k=5,la=28,lb=10,sa=1,sb=1,w=0.4) → porte non, déflaté 0.002

Règles nées ici, en paper trading :

- blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) — née le 2026-11-14, Sharpe déflaté 0.551
- blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) — née le 2026-11-14, Sharpe déflaté 0.489

## Livres de paper trading

| règle | capital $ | jours | rendement % | pire baisse % | Sharpe | ordres | ordres ignorés (< 10 $) | état | test séquentiel | porte backtest |
|---|---|---|---|---|---|---|---|---|---|---|
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 4 | 0.44 | 0.45 | – | 18 | 33 | paper | continue | oui |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 1000 | 4 | 0.21 | 0.56 | – | 40 | 11 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 1000 | 4 | 0.6 | 0.08 | – | 36 | 12 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 0.98 | 0.23 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.43 | 0.29 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 0.98 | 0.23 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.43 | 0.29 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 1.97 | 0.47 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.85 | 0.58 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 1.97 | 0.47 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.85 | 0.58 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 1.97 | 0.47 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.85 | 0.58 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 0.98 | 0.23 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.43 | 0.29 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 0.98 | 0.23 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.43 | 0.29 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 0.98 | 0.23 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 1000 | 4 | 0.64 | 0.2 | – | 12 | 36 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.43 | 0.29 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 0.98 | 0.23 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.43 | 0.29 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 0.98 | 0.23 | – | 22 | 43 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 0.43 | 0.29 | – | 12 | 48 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 1000 | 5 | 2.18 | 0.36 | – | 42 | 45 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 72 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 1000 | 5 | 2.34 | 0.47 | – | 32 | 50 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 72 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 1000 | 5 | 4.04 | 0.38 | – | 22 | 22 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 36 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 1000 | 5 | 5.61 | 0.38 | – | 20 | 23 | paper | continue | non |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 36 | paper | continue | non |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 1000 | 5 | 1.61 | 0.52 | – | 12 | 60 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 72 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 1000 | 5 | -0.49 | 1.41 | – | 12 | 60 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 72 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 1000 | 5 | -1.29 | 2.23 | – | 6 | 30 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 50 | 5 | 0.0 | 0.0 | – | 0 | 36 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 1000 | 5 | -1.29 | 2.23 | – | 6 | 30 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 36 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 1000 | 5 | 1.38 | 0.88 | – | 12 | 60 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 50 | 5 | 0.0 | 0.0 | – | 0 | 72 | paper | continue | oui |
| carry(carry=14,hold=7,k=3) | 1000 | 5 | 3.36 | 1.03 | – | 6 | 30 | paper | continue | non |
| carry(carry=14,hold=7,k=3) | 50 | 5 | 0.0 | 0.0 | – | 0 | 36 | paper | continue | non |
| carry(carry=3,hold=7,k=0) | 1000 | 5 | 2.25 | 0.78 | – | 12 | 60 | paper | continue | oui |
| carry(carry=3,hold=7,k=0) | 50 | 5 | 0.0 | 0.0 | – | 0 | 72 | paper | continue | oui |
| carry(carry=3,hold=7,k=3) | 1000 | 5 | 1.29 | 2.56 | – | 6 | 30 | paper | continue | non |
| carry(carry=3,hold=7,k=3) | 50 | 5 | 0.0 | 0.0 | – | 0 | 36 | paper | continue | non |
| carry(carry=7,hold=7,k=0) | 1000 | 5 | 1.99 | 0.8 | – | 12 | 60 | paper | continue | oui |
| carry(carry=7,hold=7,k=0) | 50 | 5 | 0.0 | 0.0 | – | 0 | 72 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 1000 | 5 | 5.28 | 0.36 | – | 6 | 30 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 50 | 5 | 0.0 | 0.0 | – | 0 | 36 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 1000 | 4 | 0.04 | 1.06 | – | 12 | 36 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 4 | -0.1 | 0.52 | – | 12 | 36 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | oui |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 1000 | 4 | 0.25 | 0.85 | – | 36 | 24 | paper | continue | non |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 1000 | 4 | -0.73 | 1.22 | – | 12 | 36 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 1000 | 4 | -1.87 | 1.87 | – | 48 | 18 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 4 | 0.91 | 0.83 | – | 44 | 20 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 50 | 4 | 0.0 | 0.0 | – | 0 | 48 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 1000 | 5 | -1.23 | 1.24 | – | 29 | 39 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 1000 | 5 | 3.0 | 0.07 | – | 22 | 43 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 50 | 5 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | non |
| premium(hold=1) | 1000 | 5 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| premium(hold=1) | 50 | 5 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 1000 | 5 | -0.4 | 0.4 | – | 7 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 50 | 5 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 1000 | 5 | -0.4 | 0.4 | – | 7 | 0 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 50 | 5 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 1000 | 5 | -0.4 | 0.4 | – | 7 | 0 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 50 | 5 | 0.0 | 0.0 | – | 0 | 4 | paper | continue | non |
| trend(hold=1,mom=14) | 1000 | 5 | -0.68 | 0.8 | – | 11 | 1 | paper | continue | non |
| trend(hold=1,mom=14) | 50 | 5 | 0.0 | 0.0 | – | 0 | 7 | paper | continue | non |
| trend(hold=1,mom=28) | 1000 | 5 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=28) | 50 | 5 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=7) | 1000 | 5 | -1.36 | 1.36 | – | 12 | 1 | paper | continue | non |
| trend(hold=1,mom=7) | 50 | 5 | 0.0 | 0.0 | – | 0 | 7 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 1000 | 4 | 5.54 | 1.07 | – | 33 | 87 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 50 | 4 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 1000 | 4 | 5.55 | 1.07 | – | 32 | 88 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 50 | 4 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 1000 | 4 | 3.03 | 1.05 | – | 36 | 43 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 50 | 4 | 0.0 | 0.0 | – | 0 | 69 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 1000 | 4 | -5.62 | 5.62 | – | 32 | 88 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 50 | 4 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 1000 | 4 | -5.62 | 5.62 | – | 32 | 88 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 50 | 4 | 0.0 | 0.0 | – | 0 | 120 | paper | continue | non |
| whales(hold=1,k=0) | 1000 | 4 | -0.98 | 0.98 | – | 24 | 0 | paper | continue | non |
| whales(hold=1,k=0) | 50 | 4 | 0.0 | 0.0 | – | 0 | 12 | paper | continue | non |
| whales(hold=1,k=3) | 1000 | 4 | -1.95 | 1.95 | – | 12 | 0 | paper | continue | non |
| whales(hold=1,k=3) | 50 | 4 | 0.0 | 0.0 | – | 0 | 6 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 1000 | 5 | -2.44 | 2.74 | – | 12 | 60 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 50 | 5 | 0.0 | 0.0 | – | 0 | 72 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 1000 | 5 | 2.81 | 0.97 | – | 12 | 60 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 50 | 5 | 0.0 | 0.0 | – | 0 | 72 | paper | continue | non |

## Fiche de score du catalogue (62 règles, historique long)

| règle | porte | Sharpe < 2024 | Sharpe ≥ 2024 | IC 95 % | rendement ≥ 2024 coûts ×2 % | baisse ≥ 2024 % | données propres (≥ 2026-07) % | Sharpe déflaté |
|---|---|---|---|---|---|---|---|---|
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | oui | 1.04 | 1.58 | [0.53, 2.55] | 116.6 | 12.5 | -8.9 | 0.542 |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.1 | 1.59 | [0.46, 2.62] | 95.8 | 18.2 | -8.6 | 0.551 |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | oui | 1.21 | 1.58 | [0.45, 2.63] | 87.4 | 14.8 | -12.7 | 0.543 |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | oui | 1.41 | 1.53 | [0.44, 2.57] | 58.4 | 12.0 | -10.4 | 0.508 |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | oui | 1.03 | 1.42 | [0.43, 2.35] | 80.5 | 10.7 | -6.9 | 0.434 |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | oui | 1.32 | 1.53 | [0.43, 2.6] | 84.2 | 14.9 | -12.0 | 0.504 |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | oui | 1.51 | 1.36 | [0.43, 2.33] | 93.0 | 13.6 | -11.2 | 0.394 |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | oui | 1.0 | 1.45 | [0.4, 2.42] | 105.7 | 13.1 | -9.8 | 0.456 |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | oui | 0.95 | 1.52 | [0.4, 2.47] | 83.2 | 10.2 | -7.0 | 0.501 |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.14 | 1.52 | [0.35, 2.57] | 81.4 | 14.7 | -9.4 | 0.498 |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | oui | 0.82 | 1.5 | [0.35, 2.57] | 77.4 | 11.3 | -2.7 | 0.489 |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | oui | 1.16 | 1.37 | [0.34, 2.39] | 97.4 | 15.7 | -13.8 | 0.399 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.458 |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.458 |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.458 |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.45 | [0.32, 2.53] | 75.2 | 15.1 | -12.0 | 0.452 |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.41 | [0.31, 2.44] | 95.1 | 17.0 | -15.2 | 0.424 |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | oui | 0.96 | 1.37 | [0.31, 2.35] | 64.6 | 12.6 | -9.7 | 0.401 |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | oui | 1.16 | 1.4 | [0.31, 2.5] | 69.5 | 14.5 | -9.8 | 0.421 |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | oui | 1.08 | 1.4 | [0.3, 2.43] | 56.9 | 16.1 | -6.0 | 0.419 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.39 |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.39 |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.35 | [0.28, 2.36] | 96.7 | 15.7 | -13.8 | 0.387 |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.39 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | oui | 0.88 | 1.26 | [0.26, 2.33] | 96.4 | 15.9 | -9.8 | 0.332 |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | oui | 1.18 | 1.28 | [0.26, 2.26] | 50.1 | 14.3 | -9.1 | 0.341 |
| carry(carry=7,hold=7,k=0) | oui | 0.7 | 1.25 | [0.25, 2.18] | 70.6 | 12.6 | 0.7 | 0.322 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | oui | 1.66 | 1.22 | [0.24, 2.22] | 47.1 | 11.2 | -0.9 | 0.309 |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | oui | 1.29 | 1.34 | [0.22, 2.42] | 60.5 | 17.1 | -14.9 | 0.377 |
| carry(carry=3,hold=7,k=0) | oui | 0.63 | 1.23 | [0.2, 2.31] | 61.8 | 14.9 | -12.9 | 0.31 |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | oui | 1.18 | 1.25 | [0.15, 2.26] | 82.8 | 17.1 | -14.5 | 0.326 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | oui | 1.35 | 1.21 | [0.12, 2.24] | 70.2 | 20.9 | -1.4 | 0.299 |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | oui | 0.21 | 0.99 | [0.07, 2.0] | 54.6 | 13.1 | -0.8 | 0.187 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | oui | 1.1 | 1.14 | [0.04, 2.31] | 119.6 | 29.3 | -8.0 | 0.256 |
| carry(carry=7,hold=7,k=3) | oui | 0.51 | 1.07 | [0.04, 2.06] | 71.8 | 19.6 | -6.1 | 0.224 |
| carry(carry=14,hold=7,k=0) | oui | 0.42 | 1.09 | [0.04, 2.09] | 58.4 | 13.6 | -1.8 | 0.233 |
| whales(hold=1,k=0) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.005 |
| whales(hold=1,k=3) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.005 |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | non | -0.35 | 1.06 | [-0.06, 2.23] | 81.8 | 27.3 | -12.2 | 0.22 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | non | 1.42 | 1.04 | [-0.08, 2.1] | 97.5 | 22.3 | -15.0 | 0.209 |
| carry(carry=14,hold=7,k=3) | non | 0.43 | 0.91 | [-0.08, 1.83] | 70.6 | 21.0 | 0.6 | 0.152 |
| carry(carry=3,hold=7,k=3) | non | 0.92 | 0.88 | [-0.13, 1.92] | 58.4 | 25.5 | -16.8 | 0.132 |
| xsmom(hold=7,k=0,mom=14) | non | 1.12 | 0.8 | [-0.23, 1.88] | 46.1 | 24.9 | -13.5 | 0.115 |
| premium(hold=1) | non | 1.4 | 0.67 | [-0.31, 1.72] | 63.3 | 26.6 | 0.0 | 0.075 |
| ml(hold=7,k=0,model=ridge) | non | 0.8 | 0.67 | [-0.34, 1.7] | 28.0 | 23.5 | -18.2 | 0.075 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | non | 1.31 | 0.73 | [-0.42, 1.82] | 12.8 | 30.9 | -23.0 | 0.089 |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | non | 0.42 | 0.63 | [-0.44, 1.65] | -5.4 | 13.1 | 3.2 | 0.066 |
| ml(hold=7,k=0,model=gbm) | non | -0.36 | 0.52 | [-0.62, 1.59] | 14.3 | 21.0 | -17.3 | 0.046 |
| ts(hold=1,l=14,s=1,sig=spring) | non | -1.07 | 0.15 | [-0.84, 1.24] | -8.9 | 20.9 | 3.4 | 0.01 |
| trend(gate=premium,hold=1,mom=14) | non | 1.27 | 0.31 | [-0.95, 1.61] | 7.1 | 49.2 | 6.4 | 0.022 |
| ts(hold=1,l=21,s=1,sig=brk) | non | 0.67 | 0.21 | [-0.96, 1.27] | -20.3 | 62.9 | 2.7 | 0.014 |
| xsmom(hold=7,k=0,mom=28) | non | 1.47 | -0.07 | [-1.02, 0.9] | -19.8 | 36.0 | -14.7 | 0.004 |
| trend(hold=1,mom=14) | non | 1.4 | 0.17 | [-1.07, 1.44] | -11.2 | 58.0 | 11.9 | 0.012 |
| trend(gate=risk_on,hold=1,mom=14) | non | 1.31 | 0.23 | [-1.09, 1.51] | -3.4 | 53.9 | 6.4 | 0.016 |
| trend(gate=nasdaq,hold=1,mom=14) | non | 1.5 | 0.17 | [-1.1, 1.43] | -9.3 | 55.8 | 8.5 | 0.012 |
| ts(hold=1,l=10,s=-1,sig=z) | non | -0.87 | -0.13 | [-1.1, 0.94] | -58.2 | 61.9 | 1.2 | 0.003 |
| ts(hold=1,l=14,s=1,sig=vwapd) | non | 0.46 | -0.05 | [-1.13, 0.9] | -49.4 | 61.2 | -10.4 | 0.004 |
| trend(hold=1,mom=28) | non | 1.59 | 0.12 | [-1.16, 1.32] | -13.0 | 59.3 | 16.6 | 0.009 |
| ts(hold=1,l=14,s=-1,sig=vwapd) | non | -0.66 | -0.22 | [-1.16, 0.84] | -61.0 | 65.7 | 0.9 | 0.002 |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | non | 0.46 | -0.09 | [-1.17, 0.86] | -53.5 | 39.4 | -1.6 | 0.003 |
| trend(hold=1,mom=7) | non | 1.57 | 0.07 | [-1.24, 1.33] | -22.1 | 63.7 | 16.5 | 0.007 |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | non | -0.62 | -0.53 | [-1.6, 0.56] | -54.1 | 31.9 | -11.5 | 0.0 |

## Journal des décisions (les 40 dernières)

- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 350288 règles explorées en 21893 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (18425232 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 369936 règles explorées en 23121 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (18795168 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 520096 règles explorées en 32506 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (19315264 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 351440 règles explorées en 21965 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (19666704 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 247680 règles explorées en 15480 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (19914384 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 498768 règles explorées en 31173 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (20413152 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 254720 règles explorées en 15920 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (20667872 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 247760 règles explorées en 15485 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (20915632 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 412112 règles explorées en 25757 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (21327744 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-17 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-17 — ÉVOLUTION : 356432 règles explorées en 22277 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (21684176 explorées et 40 présentées depuis le début)
- 2026-11-17 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-18 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-18 — ÉVOLUTION : 253472 règles explorées en 15842 générations, 6 présentées à la validation (0 en attente du prochain examen), 2 règles nées en service (21937648 explorées et 46 présentées depuis le début)
- 2026-11-18 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-18 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-18 — ÉVOLUTION : 253664 règles explorées en 15854 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (22191312 explorées et 46 présentées depuis le début)
- 2026-11-18 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-18 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-18 — ÉVOLUTION : 256384 règles explorées en 16024 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (22447696 explorées et 46 présentées depuis le début)
- 2026-11-18 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
