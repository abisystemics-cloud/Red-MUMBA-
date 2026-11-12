"""Modèle de signal + politique d'entrée/sortie — partagés live/backtest."""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from core.events import FeatureVector, Side


def composite_score(f: FeatureVector, cfg) -> float:
    """Score directionnel : >0 haussier, <0 baissier (unités ~ z-score)."""
    w = cfg.weights
    # Un OBI haussier alors que le bid est "spoofé" est suspect : on l'atténue.
    obi = f.obi_z * (1 - f.spoof_bid) if f.obi_z > 0 else f.obi_z * (1 - f.spoof_ask)
    # HL en retard sur les CEX (premium négatif) → rattrapage haussier attendu.
    prem = -f.premium_z
    # Retour vers le POC (aimant de liquidité), borné.
    poc = -max(-3.0, min(3.0, f.poc_dist_bps / 20.0)) if math.isfinite(f.poc_dist_bps) else 0.0
    # Funding extrême = foule trop positionnée d'un côté → biais contrarien.
    funding = -max(-3.0, min(3.0, f.funding_z))
    # Cluster de liquidations proche = aimant (les stops déclenchés poussent le prix).
    liq = 0.0
    if math.isfinite(f.liq_magnet_bps) and abs(f.liq_magnet_bps) <= cfg.liq_max_dist_bps:
        liq = max(-3.0, min(3.0, f.liq_magnet_bps / 50.0))
    # Biais net des adresses suivies, ramené à l'échelle d'un z-score.
    whale = 3.0 * max(-1.0, min(1.0, f.whale_bias))
    return (w.obi * obi + w.cvd * f.cvd_slope_z + w.premium * prem + w.poc * poc
            + w.funding * funding + w.liq * liq + w.whale * whale)


class SignalModel:
    """Transforme les features en intention (LONG/SHORT/FLAT) avec persistance."""

    def __init__(self, cfg):
        self.cfg = cfg
        self._streak_side = Side.FLAT
        self._streak = 0

    def apply_config(self, cfg) -> None:
        self.cfg = cfg

    def update(self, f: FeatureVector) -> tuple[Side, float]:
        cfg = self.cfg
        s = composite_score(f, cfg)
        if s >= cfg.entry_threshold:
            cand = Side.LONG
        elif s <= -cfg.entry_threshold:
            cand = Side.SHORT
        else:
            cand = Side.FLAT
        if cand == self._streak_side:
            self._streak += 1
        else:
            self._streak_side, self._streak = cand, 1
        if cand != Side.FLAT and self._streak >= cfg.persistence_ticks:
            return cand, s
        return Side.FLAT, s


class Action(str, Enum):
    HOLD = "hold"
    ENTER_LONG = "enter_long"
    ENTER_SHORT = "enter_short"
    EXIT = "exit"


@dataclass
class PositionView:
    side: Side = Side.FLAT
    entry_ts: int = 0
    last_exit_ts: int = 0


def decide(signal_side: Side, score: float, pos: PositionView, now_ms: int, cfg) -> Action:
    """Politique unique d'entrée/sortie (stops/TP gérés séparément par le risque)."""
    if pos.side == Side.FLAT:
        if now_ms - pos.last_exit_ts < cfg.cooldown_s * 1000:
            return Action.HOLD
        if signal_side == Side.LONG:
            return Action.ENTER_LONG
        if signal_side == Side.SHORT:
            return Action.ENTER_SHORT
        return Action.HOLD
    held_s = (now_ms - pos.entry_ts) / 1000
    if held_s >= cfg.max_hold_s:
        return Action.EXIT
    direction = 1 if pos.side == Side.LONG else -1
    if score * direction < cfg.exit_threshold - cfg.entry_threshold:
        return Action.EXIT  # le signal s'est retourné franchement
    if signal_side not in (Side.FLAT, pos.side):
        return Action.EXIT
    if abs(score) < cfg.exit_threshold and held_s > 5:
        return Action.EXIT  # l'avantage s'est dissipé
    return Action.HOLD
