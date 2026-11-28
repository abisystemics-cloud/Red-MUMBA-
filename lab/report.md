# Laboratoire hl-swarm — rapport

Généré le 2026-11-28 05:36 UTC · 30 marchés Hyperliquid, dernier jour clôturé 2026-11-27

Simulation uniquement : aucun ordre réel.

## Champion

**blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5)** depuis le 2026-11-14 (provisoire)

- positions simulées pour 1000 $ : ADA +42 $, SEI +42 $, BCH +42 $, XLM +42 $, TRX +42 $, RUNE +42 $, DOGE -42 $, APT -42 $, TIA -42 $, UNI -42 $, FIL -42 $, ICP -42 $
- positions simulées pour 50 $ : aucune (ordres sous le minimum de 10 $)

## Contexte du jour (macro, institutions, géopolitique)

| indicateur | feu | source |
|---|---|---|
| Nasdaq au-dessus de sa moyenne 100 j | rouge | fred, 2136 jours |
| Stablecoins en hausse sur 30 j | rouge | DefiLlama, 3287 jours |
| Prime Coinbase positive (7 j) | rouge | Coinbase vs Binance spot, 514 jours |
| Gérants d'actifs CME en hausse (4 sem.) | rouge | CFTC, 450 semaines |
| Risque géopolitique calme | vert | indice GPR, 15302 jours |
| Hors fenêtre de décision de la Fed | vert | calendrier de la Fed (liste jusqu'à fin 2026) |
| Ton de la presse mondiale sur les cryptos en amélioration | rouge | GDELT, 469 jours |
| Presse mondiale : tensions géopolitiques calmes | vert | GDELT, 469 jours |
| Indice Fear & Greed au-dessus de sa moyenne 30 j | rouge | alternative.me, 3219 jours |

## Échanges avec Claude (connecteurs)

Dernière lecture : 2026-11-28 — réponses de Claude du 2026-11-27T23:41Z déjà lues.

- Risque signalé pour le 2026-11-27 : **none** — Aucun événement grave dans les dernières 24 heures : BTC stable autour de 61 000 $ (+1,3 %), seuls incidents mineurs (accès à des coordonnées de clients chez Zodia Custody sans transaction non autorisée, retrait de Monero par KuCoin). Pas de panne d'Hyperliquid, de décrochage de stablecoin ni de choc réglementaire majeur relevés ; la levée des dernières suspensions de retrait de Binance après le p [source](https://thecryptodesk.substack.com/p/the-crypto-desk-friday-27-november)
- Paper trading Keel au 2026-11-27 : -0.46 % en 15 jours, pire baisse 1.69 %. Paper run actif depuis le 13/11 (15 évaluations, Sharpe -0,99, 165 trades, frais 3,5 $). 52 % des ordres des 7 derniers jours refusés sous le minimum de 10 $ ; critères de graduation Keel : âge 14/21 
- Gros traders au 2026-11-25 : les plus acheteurs ADA +25, DOT +19, ARB +17 ; les plus vendeurs TIA -62, HBAR -70, LTC -75
- 2026-11-14 · TIA : Aucune nouvelle propre à Celestia : la baisse du 13/11 accompagne le repli général du marché crypto (bitcoin en forte baisse, sentiment de peur extrême). Le jeton restait en tendance baissière sous toutes ses moyennes mobiles. [source](https://coinmarketcap.com/top-stories/6af75f3f0ada0c77afaf1484/) [source](https://tradersunion.com/news/cryptocurrency-news/show/4240045-celestia-drops-11-63percent-today/)
- 2026-11-15 · APT : Aucun catalyseur propre à Aptos n'a été trouvé (ni annonce, ni incident réseau, ni décision réglementaire). La baisse s'inscrit dans le repli général du marché du 14 novembre, le bitcoin touchant un plus bas de trois mois vers 62 000 $ sur fond de liquidations. [source](https://www.diariobitcoin.com/analisis/aptos-apt-cae-1546-el-14-de-noviembre-de-2026-y-queda-bajo-presion-tecnica/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · INJ : Aucune cause propre à Injective n'a été trouvée : la baisse d'environ 15 % a eu lieu pendant le vote sur la mise à jour Veyra, pourtant bien soutenue par la communauté. Elle suit le repli général du marché crypto du 14 novembre et une pression vendeuse déjà installée depuis plusieurs jours. [source](https://tradersunion.com/news/cryptocurrency-news/show/4250138-injective-slides-15-18percent-today-to/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-15 · UNI : Pas de cause propre à Uniswap : selon CoinMarketCap, la baisse d'environ 15 % vient du repli général du marché (bitcoin sous 68 000 $, inflation américaine plus forte que prévu, dollar et taux en hausse). Elle a été amplifiée par la perte de la zone technique des 6 $ et un positionnement baissier des traders. [source](https://coinmarketcap.com/top-stories/6af7ddf10ada0c77afaf9379/) [source](https://www.coindesk.com/markets/2026/11/14/bitcoin-drifts-back-to-usd65-000-deep-value-zone-says-analyst)
- 2026-11-27 · SEI : Hausse d'environ 16-20 % sur la journée du 26/11, attribuée par la presse crypto à la mise en service de la version v6.8 du réseau Sei (24/11) et à l'arrivée annoncée du stablecoin PYUSD0 de PayPal sur Sei le 27/11. Les articles sont de l'agrégation de presse, cause non confirmée officiellement. [source](https://coinmarketcap.com/cmc-ai/sei/latest-updates/) [source](https://www.coingabbar.com/en/sei-network-v6-8-goes-live-giga-upgrade-moves-closer) [source](https://www.tradingview.com/news/coinmarketcal:e996cdca7094b:0-sei-paypal-s-pyusd0-stablecoin-goes-live-27-nov-2026/)

## Machine learning

Dernier entraînement le 2026-11-28 sur l'historique 2020-01 → 2026-10 (62102 exemples). Modèles en service aujourd'hui : gbm, ridge.

Ce que la régression a appris (poids les plus forts) : carry7 +0.051, brk21 +0.046, vol30 -0.046, mom7 -0.040, spring14 +0.031.

## Évolution (règles inventées par le laboratoire)

88464768 règles explorées depuis le début en 265 passages (jugées sur l'apprentissage seul), 106 présentées à la validation, 2 en service.

Balayage exhaustif : 86922849 combinaisons sur 92490684 essayées (94.0 %).

Présentées à la validation au dernier passage (2026-11-28) :

- mix(a=illiq,b=brk,gate=gpr,hold=7,k=5,la=14,lb=42,sa=1,sb=1,w=0.6) → porte non, déflaté 0.0
- mix(a=brk,b=illiq,hold=7,k=5,la=42,lb=14,sa=1,sb=1,w=0.4) → porte non, déflaté 0.0
- mix(a=illiq,b=riskmom,gate=geo_news,hold=3,k=5,la=3,lb=42,sa=1,sb=1,w=0.5) → porte non, déflaté 0.004
- mix(a=riskmom,b=illiq,gate=geo_news,hold=3,k=5,la=42,lb=3,sa=1,sb=1,w=0.5) → porte non, déflaté 0.004
- mix(a=illiq,b=mom,hold=5,k=5,la=3,lb=28,sa=1,sb=1,w=0.7) → porte non, déflaté 0.001
- mix(a=z,b=illiq,gate=fng,hold=5,k=5,la=21,lb=3,sa=1,sb=1,w=0.4) → porte non, déflaté 0.009

Règles nées ici, en paper trading :

- blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) — née le 2026-11-14, Sharpe déflaté 0.499
- blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) — née le 2026-11-14, Sharpe déflaté 0.437

## Livres de paper trading

| règle | capital $ | jours | rendement % | pire baisse % | Sharpe | ordres | ordres ignorés (< 10 $) | état | test séquentiel | porte backtest |
|---|---|---|---|---|---|---|---|---|---|---|
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | 0.22 | 0.96 | 0.77 | 65 | 129 | paper | continue | oui |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 1000 | 14 | -0.51 | 2.0 | -0.87 | 83 | 109 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 1000 | 14 | 0.31 | 1.34 | 0.69 | 63 | 118 | paper | continue | oui |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 0.63 | 1.0 | 1.98 | 65 | 141 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 0.29 | 0.67 | 1.03 | 39 | 154 | paper | continue | oui |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 0.63 | 1.0 | 1.98 | 65 | 141 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 0.29 | 0.67 | 1.03 | 39 | 154 | paper | continue | oui |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 1.24 | 2.0 | 1.98 | 65 | 141 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 0.56 | 1.34 | 1.02 | 39 | 154 | paper | continue | oui |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 1.24 | 2.0 | 1.98 | 65 | 141 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 0.56 | 1.34 | 1.02 | 39 | 154 | paper | continue | oui |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 1.24 | 2.0 | 1.98 | 65 | 141 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 0.56 | 1.34 | 1.02 | 39 | 154 | paper | continue | oui |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 0.63 | 1.0 | 1.98 | 65 | 141 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 0.29 | 0.67 | 1.03 | 39 | 154 | paper | continue | oui |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | -0.39 | 2.27 | -0.74 | 104 | 102 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | -0.18 | 1.34 | -0.39 | 73 | 120 | paper | continue | oui |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 0.63 | 1.0 | 1.98 | 65 | 141 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 1000 | 14 | 0.71 | 0.65 | 3.34 | 42 | 141 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 0.29 | 0.67 | 1.03 | 39 | 154 | paper | continue | oui |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 0.63 | 1.0 | 1.98 | 65 | 141 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 0.29 | 0.67 | 1.03 | 39 | 154 | paper | continue | oui |
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 0.63 | 1.0 | 1.98 | 65 | 141 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 0.29 | 0.67 | 1.03 | 39 | 154 | paper | continue | oui |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 1000 | 15 | 3.19 | 0.81 | 5.81 | 86 | 143 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 192 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 1000 | 15 | 1.61 | 2.0 | 2.55 | 75 | 148 | paper | continue | oui |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 192 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 1000 | 15 | 5.33 | 1.39 | 8.92 | 62 | 62 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 1000 | 15 | 7.6 | 1.56 | 8.63 | 52 | 67 | paper | continue | non |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | non |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 1000 | 15 | 1.31 | 1.34 | 2.26 | 39 | 166 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 192 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 1000 | 15 | -1.91 | 2.34 | -2.95 | 35 | 167 | paper | continue | oui |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 192 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 1000 | 15 | -0.3 | 2.96 | -0.38 | 28 | 79 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | 50 | 15 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | non |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 1000 | 15 | 0.94 | 2.96 | 1.45 | 26 | 80 | paper | continue | oui |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 1000 | 15 | 2.68 | 0.98 | 5.48 | 29 | 171 | paper | continue | oui |
| carry(carry=14,hold=7,k=0) | 50 | 15 | 0.0 | 0.0 | – | 0 | 192 | paper | continue | oui |
| carry(carry=14,hold=7,k=3) | 1000 | 15 | 6.51 | 1.57 | 8.71 | 18 | 84 | paper | continue | non |
| carry(carry=14,hold=7,k=3) | 50 | 15 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | non |
| carry(carry=3,hold=7,k=0) | 1000 | 15 | 4.11 | 0.84 | 7.29 | 39 | 163 | paper | continue | oui |
| carry(carry=3,hold=7,k=0) | 50 | 15 | 0.0 | 0.0 | – | 0 | 192 | paper | continue | oui |
| carry(carry=3,hold=7,k=3) | 1000 | 15 | -1.31 | 3.06 | -1.5 | 27 | 79 | paper | continue | non |
| carry(carry=3,hold=7,k=3) | 50 | 15 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | non |
| carry(carry=7,hold=7,k=0) | 1000 | 15 | 2.98 | 0.8 | 6.49 | 40 | 164 | paper | continue | oui |
| carry(carry=7,hold=7,k=0) | 50 | 15 | 0.0 | 0.0 | – | 0 | 192 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 1000 | 15 | 6.39 | 0.79 | 9.1 | 22 | 82 | paper | continue | oui |
| carry(carry=7,hold=7,k=3) | 50 | 15 | 0.0 | 0.0 | – | 0 | 96 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 1000 | 14 | 0.7 | 1.06 | 1.56 | 43 | 140 | paper | continue | oui |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 14 | 1.62 | 1.3 | 4.51 | 39 | 142 | paper | continue | oui |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | oui |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 1000 | 14 | 1.84 | 1.01 | 3.79 | 95 | 114 | paper | continue | non |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 1000 | 14 | 0.6 | 1.74 | 1.16 | 38 | 143 | paper | continue | non |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 1000 | 14 | -3.07 | 3.22 | -6.72 | 161 | 78 | paper | continue | non |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 1000 | 14 | 3.46 | 0.83 | 6.56 | 137 | 93 | paper | continue | non |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | 50 | 14 | 0.0 | 0.0 | – | 0 | 168 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 1000 | 15 | -0.36 | 1.85 | -0.71 | 65 | 140 | paper | continue | non |
| ml(hold=7,k=0,model=gbm) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 1000 | 15 | 1.82 | 4.23 | 2.42 | 54 | 145 | paper | continue | non |
| ml(hold=7,k=0,model=ridge) | 50 | 15 | 0.0 | 0.0 | – | 0 | 180 | paper | continue | non |
| premium(hold=1) | 1000 | 15 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| premium(hold=1) | 50 | 15 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 1000 | 15 | -0.5 | 0.5 | -8.53 | 9 | 0 | paper | continue | non |
| trend(gate=nasdaq,hold=1,mom=14) | 50 | 15 | 0.0 | 0.0 | – | 0 | 5 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 1000 | 15 | -0.5 | 0.5 | -8.53 | 9 | 0 | paper | continue | non |
| trend(gate=premium,hold=1,mom=14) | 50 | 15 | 0.0 | 0.0 | – | 0 | 5 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 1000 | 15 | -0.5 | 0.5 | -8.53 | 9 | 0 | paper | continue | non |
| trend(gate=risk_on,hold=1,mom=14) | 50 | 15 | 0.0 | 0.0 | – | 0 | 5 | paper | continue | non |
| trend(hold=1,mom=14) | 1000 | 15 | -0.88 | 1.0 | -7.12 | 13 | 1 | paper | continue | non |
| trend(hold=1,mom=14) | 50 | 15 | 0.0 | 0.0 | – | 0 | 8 | paper | continue | non |
| trend(hold=1,mom=28) | 1000 | 15 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=28) | 50 | 15 | 0.0 | 0.0 | – | 0 | 0 | paper | continue | non |
| trend(hold=1,mom=7) | 1000 | 15 | -1.47 | 1.59 | -8.39 | 47 | 10 | paper | continue | non |
| trend(hold=1,mom=7) | 50 | 15 | 0.0 | 0.0 | – | 0 | 45 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 1000 | 14 | -1.69 | 10.55 | -0.65 | 62 | 358 | paper | continue | non |
| ts(hold=1,l=10,s=-1,sig=z) | 50 | 14 | 0.0 | 0.0 | – | 0 | 420 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 1000 | 14 | -2.45 | 10.88 | -1.0 | 45 | 375 | paper | continue | non |
| ts(hold=1,l=14,s=-1,sig=vwapd) | 50 | 14 | 0.0 | 0.0 | – | 0 | 420 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 1000 | 14 | 1.08 | 2.82 | 1.17 | 112 | 130 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=spring) | 50 | 14 | 0.0 | 0.0 | – | 0 | 189 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 1000 | 14 | 1.26 | 5.62 | 0.87 | 45 | 375 | paper | continue | non |
| ts(hold=1,l=14,s=1,sig=vwapd) | 50 | 14 | 0.0 | 0.0 | – | 0 | 420 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 1000 | 14 | 1.07 | 5.62 | 0.77 | 34 | 386 | paper | continue | non |
| ts(hold=1,l=21,s=1,sig=brk) | 50 | 14 | 0.0 | 0.0 | – | 0 | 420 | paper | continue | non |
| whales(hold=1,k=0) | 1000 | 14 | -3.53 | 3.53 | -8.69 | 82 | 19 | paper | continue | non |
| whales(hold=1,k=0) | 50 | 14 | 0.0 | 0.0 | – | 0 | 60 | paper | continue | non |
| whales(hold=1,k=3) | 1000 | 14 | -2.35 | 2.38 | -6.06 | 42 | 9 | paper | continue | non |
| whales(hold=1,k=3) | 50 | 14 | 0.0 | 0.0 | – | 0 | 30 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 1000 | 15 | -5.09 | 5.38 | -7.31 | 35 | 166 | paper | continue | non |
| xsmom(hold=7,k=0,mom=14) | 50 | 15 | 0.0 | 0.0 | – | 0 | 192 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 1000 | 15 | 3.98 | 1.06 | 6.3 | 26 | 173 | paper | continue | non |
| xsmom(hold=7,k=0,mom=28) | 50 | 15 | 0.0 | 0.0 | – | 0 | 192 | paper | continue | non |

## Fiche de score du catalogue (62 règles, historique long)

| règle | porte | Sharpe < 2024 | Sharpe ≥ 2024 | IC 95 % | rendement ≥ 2024 coûts ×2 % | baisse ≥ 2024 % | données propres (≥ 2026-07) % | Sharpe déflaté |
|---|---|---|---|---|---|---|---|---|
| blend(carry=7,gate=risk_on,hold=7,k=0,mom=14,w=0.5) | oui | 1.04 | 1.58 | [0.53, 2.55] | 116.6 | 12.5 | -8.9 | 0.49 |
| blend(carry=10,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.1 | 1.59 | [0.46, 2.62] | 95.8 | 18.2 | -8.6 | 0.499 |
| blend(carry=7,gate=nasdaq,hold=1,k=0,mom=14,w=0.7) | oui | 1.21 | 1.58 | [0.45, 2.63] | 87.4 | 14.8 | -12.7 | 0.49 |
| blend(carry=7,gate=fng,hold=1,k=0,mom=14,w=0.7) | oui | 1.41 | 1.53 | [0.44, 2.57] | 58.4 | 12.0 | -10.4 | 0.456 |
| blend(carry=7,gate=cot,hold=7,k=0,mom=14,w=0.5) | oui | 1.03 | 1.42 | [0.43, 2.35] | 80.5 | 10.7 | -6.9 | 0.384 |
| blend(carry=7,gate=gpr,hold=1,k=0,mom=14,w=0.7) | oui | 1.32 | 1.53 | [0.43, 2.6] | 84.2 | 14.9 | -12.0 | 0.452 |
| mix(a=brk,b=carry,hold=7,k=0,la=21,lb=7,sa=1,sb=1,w=0.5) | oui | 1.51 | 1.36 | [0.43, 2.33] | 93.0 | 13.6 | -11.2 | 0.346 |
| blend(carry=7,gate=stable,hold=7,k=0,mom=14,w=0.5) | oui | 1.0 | 1.45 | [0.4, 2.42] | 105.3 | 13.1 | -9.8 | 0.405 |
| blend(carry=7,gate=premium,hold=7,k=0,mom=14,w=0.5) | oui | 0.95 | 1.52 | [0.4, 2.47] | 83.2 | 10.2 | -7.0 | 0.449 |
| blend(carry=7,gate=risk_on,hold=1,k=0,mom=14,w=0.7) | oui | 1.14 | 1.52 | [0.35, 2.57] | 81.4 | 14.7 | -9.4 | 0.446 |
| blend(carry=7,gate=premium,hold=5,k=0,mom=10,w=0.5) | oui | 0.82 | 1.5 | [0.35, 2.57] | 77.4 | 11.3 | -2.7 | 0.437 |
| blend(carry=7,gate=gpr,hold=7,k=0,mom=14,w=0.5) | oui | 1.16 | 1.37 | [0.34, 2.39] | 97.4 | 15.7 | -13.8 | 0.35 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.407 |
| blend(carry=7,gate=claude_risk,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.46 | [0.33, 2.54] | 76.4 | 15.1 | -12.0 | 0.407 |
| blend(carry=7,gate=geo_news,hold=1,k=0,mom=14,w=0.7) | oui | 1.28 | 1.45 | [0.32, 2.53] | 75.2 | 15.1 | -12.0 | 0.401 |
| blend(carry=7,gate=nasdaq,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.41 | [0.31, 2.44] | 95.1 | 17.0 | -15.2 | 0.374 |
| blend(carry=7,gate=fng,hold=7,k=0,mom=14,w=0.5) | oui | 0.96 | 1.37 | [0.31, 2.35] | 64.6 | 12.6 | -9.7 | 0.352 |
| blend(carry=7,gate=stable,hold=1,k=0,mom=14,w=0.7) | oui | 1.16 | 1.4 | [0.31, 2.5] | 69.3 | 14.5 | -9.8 | 0.369 |
| blend(carry=7,gate=premium,hold=1,k=0,mom=14,w=0.7) | oui | 1.08 | 1.4 | [0.3, 2.43] | 56.9 | 16.1 | -6.0 | 0.368 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.342 |
| blend(carry=7,gate=geo_news,hold=7,k=0,mom=14,w=0.5) | oui | 1.14 | 1.35 | [0.28, 2.36] | 96.7 | 15.7 | -13.8 | 0.339 |
| blend(carry=7,gate=claude_risk,hold=7,k=0,mom=14,w=0.5) | oui | 1.15 | 1.35 | [0.28, 2.36] | 97.7 | 15.7 | -13.8 | 0.342 |
| blend(carry=7,hold=7,k=0,mom=14,w=0.7) | oui | 0.88 | 1.26 | [0.26, 2.33] | 96.4 | 15.9 | -9.8 | 0.287 |
| blend(carry=7,gate=news_tone,hold=7,k=0,mom=14,w=0.5) | oui | 1.1 | 1.28 | [0.26, 2.28] | 57.3 | 15.7 | -13.8 | 0.299 |
| blend(carry=7,gate=cot,hold=1,k=0,mom=14,w=0.7) | oui | 1.18 | 1.28 | [0.26, 2.26] | 50.1 | 14.3 | -9.1 | 0.294 |
| carry(carry=7,hold=7,k=0) | oui | 0.7 | 1.25 | [0.25, 2.18] | 70.6 | 12.6 | 0.7 | 0.276 |
| blend(carry=7,hold=1,k=0,mom=14,w=0.5) | oui | 1.66 | 1.22 | [0.24, 2.22] | 47.1 | 11.2 | -0.9 | 0.266 |
| blend(carry=7,gate=fomc,hold=1,k=0,mom=14,w=0.7) | oui | 1.29 | 1.34 | [0.22, 2.42] | 60.5 | 17.1 | -14.9 | 0.328 |
| carry(carry=3,hold=7,k=0) | oui | 0.63 | 1.23 | [0.2, 2.31] | 61.8 | 14.9 | -12.9 | 0.266 |
| blend(carry=7,gate=fomc,hold=7,k=0,mom=14,w=0.5) | oui | 1.18 | 1.25 | [0.15, 2.26] | 82.8 | 17.1 | -14.5 | 0.282 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.5) | oui | 1.35 | 1.21 | [0.12, 2.24] | 70.2 | 20.9 | -1.4 | 0.255 |
| blend(carry=7,gate=news_tone,hold=1,k=0,mom=14,w=0.7) | oui | 1.34 | 1.14 | [0.07, 2.19] | 29.4 | 16.4 | -14.1 | 0.217 |
| mix(a=maxret,b=carry,hold=7,k=0,la=14,lb=7,sa=-1,sb=1,w=0.5) | oui | 0.21 | 0.99 | [0.07, 2.0] | 54.6 | 13.1 | -0.8 | 0.154 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.7) | oui | 1.1 | 1.14 | [0.04, 2.31] | 119.6 | 29.3 | -8.0 | 0.216 |
| carry(carry=7,hold=7,k=3) | oui | 0.51 | 1.07 | [0.04, 2.06] | 71.8 | 19.6 | -6.1 | 0.187 |
| carry(carry=14,hold=7,k=0) | oui | 0.42 | 1.09 | [0.04, 2.09] | 58.4 | 13.6 | -1.8 | 0.195 |
| whales(hold=1,k=0) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.004 |
| whales(hold=1,k=3) | non | 0.0 | 0.0 | [0.0, 0.0] | 0.0 | 0.0 | 0.0 | 0.004 |
| mix(a=vol,b=mom,hold=7,k=0,la=28,lb=14,sa=-1,sb=1,w=0.5) | non | -0.35 | 1.06 | [-0.06, 2.23] | 81.8 | 27.3 | -12.2 | 0.184 |
| blend(carry=7,hold=7,k=3,mom=14,w=0.5) | non | 1.42 | 1.04 | [-0.08, 2.1] | 97.5 | 22.3 | -15.0 | 0.173 |
| carry(carry=14,hold=7,k=3) | non | 0.43 | 0.91 | [-0.08, 1.83] | 70.6 | 21.0 | 0.6 | 0.123 |
| carry(carry=3,hold=7,k=3) | non | 0.92 | 0.88 | [-0.13, 1.92] | 58.4 | 25.5 | -16.8 | 0.106 |
| xsmom(hold=7,k=0,mom=14) | non | 1.12 | 0.8 | [-0.23, 1.88] | 46.1 | 24.9 | -13.5 | 0.092 |
| premium(hold=1) | non | 1.4 | 0.67 | [-0.31, 1.72] | 63.3 | 26.6 | 0.0 | 0.058 |
| ml(hold=7,k=0,model=ridge) | non | 0.8 | 0.67 | [-0.34, 1.7] | 28.6 | 23.5 | -18.2 | 0.06 |
| blend(carry=7,hold=1,k=3,mom=14,w=0.7) | non | 1.31 | 0.73 | [-0.42, 1.82] | 12.8 | 30.9 | -23.0 | 0.069 |
| mix(a=spring,b=carry,hold=1,k=0,la=14,lb=7,sa=1,sb=1,w=0.5) | non | 0.42 | 0.63 | [-0.44, 1.65] | -5.4 | 13.1 | 3.2 | 0.051 |
| ml(hold=7,k=0,model=gbm) | non | -0.09 | 0.59 | [-0.62, 1.68] | 18.4 | 22.1 | -18.8 | 0.045 |
| ts(hold=1,l=14,s=1,sig=spring) | non | -1.07 | 0.15 | [-0.84, 1.24] | -8.9 | 20.9 | 3.4 | 0.007 |
| trend(gate=premium,hold=1,mom=14) | non | 1.27 | 0.31 | [-0.95, 1.61] | 7.1 | 49.2 | 6.4 | 0.016 |
| ts(hold=1,l=21,s=1,sig=brk) | non | 0.67 | 0.21 | [-0.96, 1.27] | -20.3 | 62.9 | 2.7 | 0.01 |
| xsmom(hold=7,k=0,mom=28) | non | 1.47 | -0.07 | [-1.02, 0.9] | -19.8 | 36.0 | -14.7 | 0.002 |
| trend(hold=1,mom=14) | non | 1.4 | 0.17 | [-1.07, 1.44] | -11.2 | 58.0 | 11.9 | 0.008 |
| trend(gate=risk_on,hold=1,mom=14) | non | 1.31 | 0.23 | [-1.09, 1.51] | -3.4 | 53.9 | 6.4 | 0.011 |
| trend(gate=nasdaq,hold=1,mom=14) | non | 1.5 | 0.17 | [-1.1, 1.43] | -9.3 | 55.8 | 8.5 | 0.009 |
| ts(hold=1,l=10,s=-1,sig=z) | non | -0.87 | -0.13 | [-1.1, 0.94] | -58.2 | 61.9 | 1.2 | 0.002 |
| ts(hold=1,l=14,s=1,sig=vwapd) | non | 0.46 | -0.05 | [-1.13, 0.9] | -49.4 | 61.2 | -10.4 | 0.003 |
| trend(hold=1,mom=28) | non | 1.59 | 0.12 | [-1.16, 1.32] | -13.0 | 59.3 | 16.6 | 0.006 |
| ts(hold=1,l=14,s=-1,sig=vwapd) | non | -0.66 | -0.22 | [-1.16, 0.84] | -61.0 | 65.7 | 0.9 | 0.001 |
| mix(a=vsurge,b=mom,hold=1,k=0,la=7,lb=14,sa=1,sb=1,w=0.5) | non | 0.46 | -0.09 | [-1.17, 0.86] | -53.5 | 39.4 | -1.6 | 0.002 |
| trend(hold=1,mom=7) | non | 1.57 | 0.07 | [-1.24, 1.33] | -22.1 | 63.7 | 16.5 | 0.005 |
| mix(a=z,b=carry,hold=1,k=0,la=10,lb=7,sa=-1,sb=1,w=0.5) | non | -0.62 | -0.53 | [-1.6, 0.56] | -54.1 | 31.9 | -11.5 | 0.0 |

## Journal des décisions (les 40 dernières)

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
- 2026-11-27 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-27 — ÉVOLUTION : 497056 règles explorées en 31066 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (86878816 explorées et 100 présentées depuis le début)
- 2026-11-27 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-28 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-28 — ÉVOLUTION : 343968 règles explorées en 21498 générations, 6 présentées à la validation (0 en attente du prochain examen), 2 règles nées en service (87222784 explorées et 106 présentées depuis le début)
- 2026-11-28 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-28 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-28 — ÉVOLUTION : 261008 règles explorées en 16313 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (87483792 explorées et 106 présentées depuis le début)
- 2026-11-28 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-28 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-28 — ÉVOLUTION : 372752 règles explorées en 23297 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (87856544 explorées et 106 présentées depuis le début)
- 2026-11-28 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-28 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-28 — ÉVOLUTION : 255312 règles explorées en 15957 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (88111856 explorées et 106 présentées depuis le début)
- 2026-11-28 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
- 2026-11-28 — modèles ML ré-entraînés sur 62102 exemples
- 2026-11-28 — ÉVOLUTION : 352912 règles explorées en 22057 générations, 0 présentées à la validation (40 en attente du prochain examen), 2 règles nées en service (88464768 explorées et 106 présentées depuis le début)
- 2026-11-28 — fiche de score recalculée sur 2020-01 → 2026-10 : 36 règles sur 62 passent la porte
