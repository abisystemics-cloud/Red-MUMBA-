# CLAUDE.md — contexte pour toute session Claude sur ce dépôt

## Le projet
hl-swarm (projet « Red MUMBA ») : bot de trading autonome à 7 agents pour les perps Hyperliquid.
Le propriétaire ne veut écrire aucune ligne de code : Claude code, teste, pousse et explique en français.
Lire d'abord `README.md` (architecture, backtest, go/no-go) et `SUPERVISION.md` (règles d'intervention).

## État (mis à jour le 12/11/2026)
- Code complet sur `main` : 7 agents, exécution maker, signaux funding / liquidations / positionnement Coinversa,
  canal de supervision (branche `control`), backtest historique (workflow `backtest`).
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
```
