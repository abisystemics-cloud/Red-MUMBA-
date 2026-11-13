"""Sizing (Kelly fractionnel) et stops dynamiques fondés sur la variance.

Kelly : f* = p − (1 − p) / b, avec p = taux de gain et b = gain moyen / perte
moyenne. Les deux sont estimés sur les trades réalisés, rétrécis (shrinkage
bayésien) vers des priors tant que l'échantillon est petit — sinon trois trades
gagnants feraient exploser la taille.

Stop : k × σ_réalisée × √horizon, borné par [min_stop_bps, max_stop_bps].
La taille est ensuite celle qui fait perdre exactement `risque_usd` au stop.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

from core.events import RiskLevel


@dataclass
class TradeStats:
    prior_win_rate: float
    prior_payoff: float
    prior_weight: int = 20
    window: int = 200
    returns: deque = field(default_factory=lambda: deque(maxlen=200))

    def add(self, r: float) -> None:
        self.returns.append(r)

    @property
    def n(self) -> int:
        return len(self.returns)

    def win_rate(self) -> float:
        wins = sum(1 for r in self.returns if r > 0)
        return (wins + self.prior_win_rate * self.prior_weight) / (self.n + self.prior_weight)

    def payoff(self) -> float:
        wins = [r for r in self.returns if r > 0]
        losses = [-r for r in self.returns if r < 0]
        if not wins or not losses:
            return self.prior_payoff
        emp = (sum(wins) / len(wins)) / (sum(losses) / len(losses))
        w = min(len(wins), len(losses))
        return (emp * w + self.prior_payoff * self.prior_weight) / (w + self.prior_weight)

    def variance(self) -> float:
        if self.n < 2:
            return float("nan")
        m = sum(self.returns) / self.n
        return sum((r - m) ** 2 for r in self.returns) / (self.n - 1)


def kelly_fraction(p: float, b: float) -> float:
    if b <= 0:
        return 0.0
    return max(0.0, p - (1 - p) / b)


def stop_distance_bps(vol_bps_per_sqrt_s: float, cfg, horizon_s: float | None = None) -> float:
    horizon_s = horizon_s if horizon_s is not None else getattr(cfg, "stop_horizon_s", 60.0)
    raw = cfg.stop_vol_mult * vol_bps_per_sqrt_s * math.sqrt(horizon_s)
    if not math.isfinite(raw):
        raw = cfg.max_stop_bps
    return float(min(cfg.max_stop_bps, max(cfg.min_stop_bps, raw)))


@dataclass
class SizeDecision:
    qty: float
    notional: float
    stop_bps: float
    stop_px: float
    tp_px: float
    risk_usd: float
    kelly_raw: float
    kelly_used: float
    reason: str = ""


def size_position(*, equity: float, px: float, is_long: bool, vol_bps: float,
                  stats: TradeStats, cfg, level: RiskLevel, sz_decimals: int = 4) -> SizeDecision:
    p, b = stats.win_rate(), stats.payoff()
    k_raw = kelly_fraction(p, b)
    if getattr(cfg, "sizing", "kelly") == "fixed":
        k_used = cfg.max_risk_per_trade_pct / 100
    else:
        k_used = min(k_raw * cfg.kelly_fraction, cfg.max_risk_per_trade_pct / 100)
    if level == RiskLevel.CAUTION:
        k_used *= 0.5
    stop_bps = stop_distance_bps(vol_bps, cfg)
    risk_usd = equity * k_used
    if level == RiskLevel.HALT or k_used <= 0 or px <= 0:
        return SizeDecision(0, 0, stop_bps, 0, 0, 0, k_raw, k_used, "no edge or halted")
    notional = risk_usd / (stop_bps / 1e4)
    notional = min(notional, cfg.max_position_notional_usd, equity * cfg.max_leverage)
    step = 10 ** -sz_decimals
    qty = math.floor(notional / px / step) * step
    sign = 1 if is_long else -1
    stop_px = px * (1 - sign * stop_bps / 1e4)
    tp_px = px * (1 + sign * stop_bps * cfg.take_profit_r / 1e4)
    return SizeDecision(round(qty, sz_decimals), qty * px, stop_bps, stop_px, tp_px,
                        risk_usd, k_raw, k_used)


@dataclass
class CircuitBreaker:
    """Limite de perte journalière + série de pertes consécutives."""
    daily_loss_limit_pct: float
    max_consecutive_losses: int
    day: int = -1
    day_start_equity: float = 0.0
    consecutive_losses: int = 0
    tripped_reason: str = ""

    def on_equity(self, equity: float, now_ms: int) -> None:
        d = now_ms // 86_400_000
        if d != self.day:
            self.day, self.day_start_equity = d, equity
            self.consecutive_losses = 0
            self.tripped_reason = ""
        if self.day_start_equity > 0:
            dd = (equity / self.day_start_equity - 1) * 100
            if dd <= -self.daily_loss_limit_pct:
                self.tripped_reason = f"daily loss {dd:.2f}% <= -{self.daily_loss_limit_pct}%"

    def on_trade_closed(self, pnl: float) -> None:
        self.consecutive_losses = self.consecutive_losses + 1 if pnl < 0 else 0
        if self.consecutive_losses >= self.max_consecutive_losses:
            self.tripped_reason = f"{self.consecutive_losses} consecutive losses"

    @property
    def tripped(self) -> bool:
        return bool(self.tripped_reason)


def round_px(px: float, sz_decimals: int, is_perp: bool = True) -> float:
    """Règles de tick Hyperliquid : ≤ 5 chiffres significatifs et
    ≤ (6 − szDecimals) décimales pour un perp."""
    if px <= 0:
        return px
    max_dec = (6 if is_perp else 8) - sz_decimals
    sig = float(f"{px:.5g}")
    return round(sig, max(0, max_dec))
