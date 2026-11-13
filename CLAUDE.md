# CLAUDE.md — contexte pour toute session Claude sur ce dépôt

## Le projet
hl-swarm (projet « Red MUMBA ») : bot de trading autonome à 7 agents pour les perps Hyperliquid.
Le propriétaire ne veut écrire aucune ligne de code : Claude code, teste, pousse et explique en français.
Lire d'abord `README.md` (architecture, backtest, go/no-go) et `SUPERVISION.md` (règles d'intervention).

## État (mis à jour le 12/11/2026)
- Code complet sur `main` : 7 agents, exécution maker, signaux funding / liquidations / positionnement Coinversa,
  canal de supervision (branche `control`), backtest historique (workflow `backtest`),
  interface web temps réel (`ui/index.html`, `core/web.py`, `UI_PASSWORD`) et mode `python main.py --demo`.
- AWS : utilisateur IAM `hl-swarm-backtest` (lecture seule archive Hyperliquid) créé ; compte AWS en Free plan
  (6 mois). Archive S3 disponible jusqu'au 11/11/2026 ; Coinversa depuis le 01/09/2026.
- Capital disponible du propriétaire : ~50 $ ; horizon de décision : 5 mois. Production prévue sur Render.
- **Rien n'est déployé.** Aucun test contre les vraies API n'a encore tourné.
- Étape en cours : le propriétaire ajoute les secrets GitHub `COINVERSA_API_KEY`, `AWS_ACCESS_KEY_ID`,
  `AWS_SECRET_ACCESS_KEY`. Ensuite : `python scripts/request_backtest.py --from 2026-09-01 --to 2026-10-31`,
  puis `--fetch <id> --wait-s 1800`, et lui expliquer le verdict.
- Suite si GO : workflow `integration-testnet`, déploiement (AWS ou Render), 2 semaines de paper trading,
  puis tâche planifiée de supervision via PostHog (projet « Default project », id 337957, hôte UE).

## Règles non négociables
- `config.yaml` versionné reste **testnet + dry_run** (la CI le vérifie). Le passage en réel se fait
  uniquement sur le serveur, par l'humain, avec `LIVE_TRADING_CONFIRM`.
- Jamais de secret dans le dépôt ni dans la conversation : secrets GitHub / variables du serveur uniquement.
- Le superviseur ne peut que réduire le risque (liste blanche de `agents/control_agent.py`). Ne jamais valider
  soi-même une proposition de l'agent R&D, ni conclure GO à la place des critères.
- Aucun LLM dans le chemin critique du trading.
- Avant chaque push : `ruff check .` et `pytest -q` au vert. Commits en anglais, explications à l'humain en français.

## Commandes utiles
```bash
pytest -q                                              # tests hors réseau
python scripts/backtest.py --from A --to B             # backtest local (après import_history.py)
python scripts/request_backtest.py --from A --to B     # backtest distant (GitHub Actions)
python scripts/supervise.py ping --reason "..."        # commande de supervision (branche control)
python main.py --go-live                               # rapport go/no-go
python main.py --demo                                  # démo + interface http://localhost:8080 (mdp: demo)
```

## Backtest results log
- bt-20261112T225821 (2026-09-01→11-11, BTC+ETH, maker): 1 trade. Invalid measure — Kelly sizing hit 0 after 3 losses and never recovered (still true in live; fix before any real money).
- bt-20261112T233005 sweep: same lock-out, 1–15 trades per setting, uninformative.
- bt-20261113T055142 sweep (fixed sizing, CVD/POC from Binance aggTrades flow, maker+taker, 16 settings): NO-GO. Every setting loses on both train and validation (48–5400 trades). Best (entry 1.2, persistence 6, maker): −0.9 % train / −0.9 % validation, PF 0.66–0.70, fees ≈ all of the loss → no gross edge above costs. Taker strictly worse. Current strategy (short-horizon microstructure) should not trade real money.
- bt-20261113T151423 bar research (scripts/bar_research.py, Binance 15m klines 2020-01→2026-10, BTC/ETH/SOL, train ≤2023-12, validation 2024-01→2026-10, taker costs, 0.5 % risk/trade): all 5 families NO-GO under the pre-registered rule. VWAP rotation (Trader Dale) and Wyckoff spring lose heavily on both periods; VWAP trend ≈ flat; Binance funding fade wins on train, loses on validation. Only TSMOM 6h (L=28 bars ≈ 7 days) is close: train Sharpe 1.55 / validation 0.74 (threshold 0.8), PF 1.37, +7.25 % at tiny exposure, still positive with 2× costs. Not a GO; candidate for robustness checks (neighbouring L, per-year/per-coin, vs buy-and-hold) and forward paper trading only.
- bt-20261113T153448 robustness (scripts/tsmom_robustness.py, pre-registered A–D): TSMOM 6h L=28 long-only PASSES all four. Neighbours L=20/24/32/36 all positive on validation (Sharpe 0.69–0.85); each coin positive alone (BTC/ETH/SOL Sharpe 0.51/0.62/0.75); 6 of 7 calendar years positive (2022 −2.9 %); beta ≈ 0.04 vs equal-weight buy-and-hold, alpha +1.5 %/yr at 0.5 % risk (t ≈ 1.0, not significant alone). Long/short version similar (beta ≈ 0). Validation at 2 % risk/trade: +28 %, DD 13 %; at 4 %: +53 %, DD 25 % (Jan 2024→Oct 2026). Buy-and-hold same period: +32 %, DD 64 %. Not a live GO: next is forward paper trading.
