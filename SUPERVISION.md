# Supervision de hl-swarm

Ce guide décrit comment un superviseur (toi ou Claude) suit le bot et intervient. Le bot reste autonome : le superviseur observe, réduit le risque si besoin et prévient l'humain. Il ne pilote pas les trades.

## Le canal

```
 superviseur ──commit──▶ branche GitHub `control` (control/commands.json) ──lecture 30 s──▶ bot
 superviseur ◀──HogQL── PostHog ◀── command_ack · command_applied · status_snapshot ◀── bot
                                   └─ alerte Telegram à chaque commande appliquée ─▶ humain
```

- **Envoyer une commande :** `python scripts/supervise.py <commande> --reason "..."`. Chaque commande est un commit : l'historique de la branche `control` sert de journal d'audit.
- **Lire la réponse :** dans PostHog, les événements `hlswarm_command_ack`, `hlswarm_command_applied` et `hlswarm_status_snapshot`.
- **Côté serveur :** il faut `CONTROL_GITHUB_REPO` et `CONTROL_GITHUB_TOKEN`. Le jeton GitHub est *fine-grained*, limité à ce dépôt, avec la permission Contents en **lecture seule**.

## Commandes autorisées (liste blanche)

| Commande | Effet | Quand l'utiliser |
|---|---|---|
| `ping` | Le bot renvoie un `status_snapshot` immédiat | Contrôle de routine, test du canal |
| `pause` | HALT : plus aucune nouvelle entrée | Anomalie non comprise, marché désordonné |
| `resume` | Lève la pause du superviseur | La cause de la pause est résolue |
| `flatten` | Ferme toutes les positions immédiatement | Danger avéré (flux faux, exchange instable) |
| `set_risk_scale --scale x` | Taille × x, avec x ∈ [0, 1] | Drawdown qui se creuse, régime inhabituel |
| `disable_coin --coin X` / `enable_coin` | Coupe ou rouvre un marché | Problème propre à un marché |
| `go_live_report` | Rapport go/no-go immédiat | Bilan à la demande |
| `research_run` | Cycle R&D forcé | Après un changement de régime de marché |

**Impossible par construction :** augmenter le risque au-delà de `config.yaml`, passer en réel, toucher aux fonds ou modifier la stratégie. La stratégie ne change que par une proposition de l'agent R&D validée par l'humain.

## Backtests à la demande

Le superviseur peut lancer un backtest distant et lire le résultat, sans accès au serveur :

```bash
python scripts/request_backtest.py --from 2026-09-01 --to 2026-10-31      # affiche l'id
python scripts/request_backtest.py --fetch <id> --wait-s 1800             # récupère le rapport
```

Exemple d'usage : avant de résumer une proposition de l'agent R&D, la faire backtester sur une période plus longue que ses 24 h de données.

## Routine de surveillance

À chaque passage, lancer ces requêtes HogQL. Le filtre `network` est à remplacer par `mainnet` en réel.

```sql
-- 1. Dernier état connu (vivant ? en pause ? positions ? erreurs ?)
SELECT timestamp, properties.role, properties.status FROM events
WHERE event = 'hlswarm_status_snapshot' ORDER BY timestamp DESC LIMIT 2

-- 2. Incidents des dernières 24 h
SELECT timestamp, event, properties.feed, properties.level, properties.reason, properties.error
FROM events WHERE event IN ('hlswarm_feed_down','hlswarm_risk_level','hlswarm_breaker')
  AND timestamp > now() - INTERVAL 24 HOUR ORDER BY timestamp DESC

-- 3. Performance des dernières 24 h
SELECT count() AS trades, sum(toFloat(properties.pnl)) AS pnl,
       avg(toFloat(properties.slippage_bps)) AS slip_bps,
       countIf(toFloat(properties.pnl) > 0) / count() AS win_rate
FROM events WHERE event = 'hlswarm_trade_closed' AND timestamp > now() - INTERVAL 24 HOUR

-- 4. Ordres refusés (surtout stops / TP)
SELECT timestamp, properties.coin, properties.kind, properties.error FROM events
WHERE event = 'hlswarm_order' AND properties.status = 'rejected'
  AND timestamp > now() - INTERVAL 24 HOUR ORDER BY timestamp DESC LIMIT 50
```

## Règles d'intervention

| Constat | Action du superviseur |
|---|---|
| Aucun `status_snapshot` depuis plus de 15 min | `ping`. Toujours rien 5 min plus tard → prévenir l'humain (bot ou serveur à l'arrêt) |
| Stop ou TP refusé sur une position ouverte | `flatten` + prévenir l'humain |
| `feed_down` Hyperliquid de plus de 5 min avec des positions ouvertes | `flatten` |
| Drawdown du jour au-delà de −2 % (avant le disjoncteur à −3 %) | `set_risk_scale --scale 0.5` |
| Plus de 3 pertes d'affilée sur un même marché | `disable_coin` sur ce marché, puis prévenir l'humain |
| Slippage moyen > 5 bps sur 24 h | Prévenir l'humain (exécution dégradée) |
| Proposition de l'agent R&D en attente | Résumer la proposition à l'humain ; ne jamais la valider soi-même |
| Rapport go/no-go | Le transmettre tel quel ; ne jamais conclure GO à la place des critères |

**Toujours :** une commande = une raison écrite (`--reason`), et chaque action est signalée à l'humain. Dans le doute, la pause est préférable au flatten, et prévenir est préférable à agir.
