"""Le bot pose ses questions à Claude, Claude répond avec ses connecteurs.

Le bot n'a pas accès aux connecteurs du compte Claude (Coinversa, Keel, Bigdata.com,
recherche web…). Il écrit donc chaque jour ses DEMANDES dans `requests.json` (branche
`lab-state`) ; une tâche programmée Claude les lit, interroge les connecteurs et
dépose les RÉPONSES dans `answers.json` (branche `claude-answers`). Au passage suivant
le bot les relit ici.

Garde-fous :
- le bot ne peut demander que des INFORMATIONS, d'un type figurant dans REQUEST_TYPES ;
- chaque réponse est validée comme une donnée non fiable (types, bornes, longueurs) ;
  ce qui ne respecte pas le format est ignoré ;
- une réponse de plus de 36 h n'est pas utilisée ;
- Claude ne décide d'aucun trade : ses réponses alimentent (1) le rapport, (2) un feu
  « claude_risk » qui ne peut que DIVISER l'exposition par deux, (3) une famille de
  règles « whales » qui concourt en simulation comme les autres.
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np

DAY_MS = 86_400_000
MAX_AGE_H = 36
KEEL_DEPLOYMENT = "dep_01m7b0gq4cxdfqe8capdvfdfkm"
REQUEST_TYPES = {
    "smart_money": {
        "question": "Pour chacun de ces marchés Hyperliquid, quel est le biais net (de -100 à +100, en % du notionnel) des "
                    "traders les plus rentables (tiers de PnL les plus hauts) en ce moment ?",
        "answer_schema": {"bias": {"<COIN>": "nombre entre -100 et 100"}, "as_of": "date ISO", "source": "texte court"}},
    "risk_check": {
        "question": "Y a-t-il eu dans les dernières 24 heures un événement grave pour les marchés crypto ou pour Hyperliquid "
                    "(piratage ou faillite d'un exchange, panne ou exploit d'Hyperliquid, décrochage d'un stablecoin, choc "
                    "réglementaire, escalade militaire majeure) ?",
        "answer_schema": {"level": "none | elevated | severe", "summary": "2 phrases maximum", "sources": ["URL"]}},
    "keel_status": {
        "question": "Où en est le paper trading Keel (rendement, pire baisse, nombre de jours) ?",
        "answer_schema": {"return_pct": "nombre", "max_dd_pct": "nombre", "days": "entier", "note": "texte court"}},
    "explain_move": {
        "question": "Ce marché a bougé de plus de 12 % hier. Quelle en est la cause la plus probable ?",
        "answer_schema": {"summary": "2 phrases maximum", "sources": ["URL"]}},
}


def _iso(ms: float) -> str:
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d")


def build_requests(state: dict, panel: dict) -> dict:
    """Les demandes du jour : trois permanentes + une par gros mouvement (3 au plus)."""
    coins = list(panel["coins"])
    reqs = [{"id": "smart_money", "type": "smart_money", "coins": coins},
            {"id": "risk_check", "type": "risk_check"},
            {"id": "keel_status", "type": "keel_status", "deployment": KEEL_DEPLOYMENT}]
    last = np.nan_to_num(panel["R"][-1])
    big = sorted(((abs(float(r)), c, float(r)) for c, r in zip(coins, last, strict=True) if abs(r) > 0.12), reverse=True)[:3]
    reqs += [{"id": f"move_{c}", "type": "explain_move", "coin": c, "move_pct": round(r * 100, 1), "day": _iso(panel["days"][-1])}
             for _, c, r in big]
    for r in reqs:
        r["question"] = REQUEST_TYPES[r["type"]]["question"]
        r["answer_schema"] = REQUEST_TYPES[r["type"]]["answer_schema"]
    champ = (state.get("champion") or {}).get("name")
    return {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "last_closed_day": _iso(panel["days"][-1]),
            "from": "hl-swarm lab (programme, pas un humain)", "champion": champ, "requests": reqs}


def _text(v, n: int = 400) -> str:
    return " ".join(str(v).replace("|", "/").split())[:n]


def _urls(v) -> list[str]:
    return [u[:300] for u in v if isinstance(u, str) and u.startswith("https://")][:5] if isinstance(v, list) else []


def ingest(state: dict, answers: dict | None, panel: dict, now_ms: float) -> list[str]:
    """Valide les réponses et les range dans l'état, datées du dernier jour clôturé. → journal."""
    mem = state.setdefault("claude", {"risk": {}, "smart_money": {}, "notes": []})
    if not isinstance(answers, dict) or not isinstance(answers.get("answers"), dict):
        return ["aucune réponse de Claude à lire"]
    try:
        at = datetime.strptime(str(answers.get("answered_at", ""))[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return ["réponses de Claude sans date valide : ignorées"]
    age_h = (now_ms / 1000 - at.timestamp()) / 3600
    stamp = at.strftime("%Y-%m-%dT%H:%MZ")
    if stamp == mem.get("last_answer"):
        return [f"réponses de Claude du {stamp} déjà lues"]
    if not 0 <= age_h <= MAX_AGE_H:
        return [f"réponses de Claude trop anciennes ({age_h:.0f} h) : ignorées"]
    day, ans, used = _iso(panel["days"][-1]), answers["answers"], []
    sm = ans.get("smart_money")
    if isinstance(sm, dict) and isinstance(sm.get("bias"), dict):
        bias = {c: max(-100.0, min(100.0, float(v))) for c, v in sm["bias"].items()
                if c in panel["coins"] and isinstance(v, (int, float)) and np.isfinite(v)}
        if len(bias) >= 10:
            mem["smart_money"][day] = bias
            used.append(f"gros traders ({len(bias)} marchés)")
    rk = ans.get("risk_check")
    if isinstance(rk, dict) and rk.get("level") in ("none", "elevated", "severe"):
        mem["risk"][day] = rk["level"]
        mem["risk_note"] = {"day": day, "level": rk["level"], "summary": _text(rk.get("summary", "")), "sources": _urls(rk.get("sources"))}
        used.append(f"risque {rk['level']}")
    ks = ans.get("keel_status")
    if isinstance(ks, dict) and all(isinstance(ks.get(k), (int, float)) for k in ("return_pct", "max_dd_pct", "days")):
        mem["keel"] = {"day": day, "return_pct": float(ks["return_pct"]), "max_dd_pct": float(ks["max_dd_pct"]),
                       "days": int(ks["days"]), "note": _text(ks.get("note", ""), 200)}
        used.append("Keel")
    for key, a in ans.items():
        if key.startswith("move_") and key[5:] in panel["coins"] and isinstance(a, dict) and a.get("summary"):
            mem["notes"].append({"day": day, "coin": key[5:], "summary": _text(a["summary"]), "sources": _urls(a.get("sources"))})
            used.append(f"mouvement {key[5:]}")
    mem["notes"] = mem["notes"][-20:]
    for k in ("risk", "smart_money"):
        mem[k] = dict(sorted(mem[k].items())[-120:])
    mem["last_answer"] = stamp
    return [f"réponses de Claude du {stamp} lues : " + (", ".join(used) or "rien d'exploitable")]


def wire(state: dict, panel: dict) -> None:
    """Branche les réponses mémorisées sur le panel : feu `claude_risk` et signal `smart_money`."""
    mem = state.get("claude") or {}
    days = [_iso(d) for d in panel["days"]]
    risk = mem.get("risk", {})
    panel.setdefault("ctx", {})["claude_risk"] = np.array([risk.get(d, "none") == "none" for d in days])
    sig = np.full(panel["C"].shape, np.nan)
    for i, d in enumerate(days):
        row = mem.get("smart_money", {}).get(d)
        if row:
            sig[i] = [row.get(c, np.nan) for c in panel["coins"]]
    panel.setdefault("ext", {})["smart_money"] = sig
