"""Messages échangés entre agents (dataclasses légères, slots pour la latence)."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np


def now_ms() -> int:
    return time.time_ns() // 1_000_000


def mono_ns() -> int:
    return time.perf_counter_ns()


class Topic(str, Enum):
    BOOK = "book"                 # BookSnapshot
    TRADE = "trade"               # Trade (batch)
    ASSET_CTX = "asset_ctx"       # AssetCtx
    EXT_QUOTE = "ext_quote"       # ExternalQuote (Binance / Bybit)
    LIQ_MAP = "liq_map"           # LiquidationMap
    WHALES = "whales"             # WhaleBias
    FEATURES = "features"         # FeatureVector
    SIGNAL = "signal"             # Signal (brut, agent Quant)
    VALIDATED = "validated"       # Signal validé
    RISK_STATE = "risk_state"     # MacroState (kill switch)
    ORDER = "order"               # OrderEvent
    FILL = "fill"                 # FillEvent
    POSITION = "position"         # PositionUpdate
    TELEMETRY = "telemetry"       # dict libre
    CONTROL = "control"           # ControlCommand (canal de supervision)
    HEALTH = "health"


@dataclass(slots=True)
class BookSnapshot:
    coin: str
    exch_ts: int                  # horodatage exchange (ms)
    recv_ts: int                  # horodatage réception (ms)
    bids: np.ndarray              # shape (n, 2) [px, sz], meilleur en premier
    asks: np.ndarray
    recv_ns: int = field(default_factory=mono_ns)

    @property
    def best_bid(self) -> float:
        return float(self.bids[0, 0]) if len(self.bids) else float("nan")

    @property
    def best_ask(self) -> float:
        return float(self.asks[0, 0]) if len(self.asks) else float("nan")

    @property
    def mid(self) -> float:
        return (self.best_bid + self.best_ask) / 2

    @property
    def spread_bps(self) -> float:
        m = self.mid
        return (self.best_ask - self.best_bid) / m * 1e4 if m > 0 else float("inf")


@dataclass(slots=True)
class Trade:
    coin: str
    ts: int
    px: float
    sz: float
    is_buy: bool                  # True = agresseur acheteur
    tid: Optional[int] = None


@dataclass(slots=True)
class AssetCtx:
    coin: str
    ts: int
    open_interest: float
    funding: float
    mark_px: float
    oracle_px: float
    day_ntl_vlm: float = 0.0
    premium: float = 0.0


@dataclass(slots=True)
class ExternalQuote:
    venue: str                    # binance | bybit
    coin: str
    ts: int
    bid: float
    ask: float

    @property
    def mid(self) -> float:
        return (self.bid + self.ask) / 2


@dataclass(slots=True)
class LiquidationMap:
    coin: str
    ts: int
    # niveaux de prix où se concentrent les liquidations estimées [(px, usd)]
    clusters: list[tuple[float, float]]
    source: str


@dataclass(slots=True)
class WhaleBias:
    coin: str
    ts: int
    bias: float                   # [-1, 1] : notionnel net long/short des adresses suivies
    n_wallets: int
    gross_usd: float


@dataclass(slots=True)
class FeatureVector:
    coin: str
    ts: int
    mid: float
    spread_bps: float
    obi: float
    obi_z: float
    cvd: float
    cvd_slope_z: float
    poc: float
    poc_dist_bps: float
    premium_bps: float
    premium_z: float
    spoof_bid: float              # score de spoofing côté bid [0..1]
    spoof_ask: float
    realized_vol_bps: float       # volatilité réalisée par sqrt(seconde)
    oi_change_pct: float
    funding: float
    book_age_ms: int
    ext_age_ms: int
    liq_magnet_bps: float = float("nan")
    source_recv_ns: int = 0
    funding_z: float = 0.0        # z-score du funding (positif = longs qui paient cher)
    whale_bias: float = 0.0


class Side(str, Enum):
    LONG = "long"
    SHORT = "short"
    FLAT = "flat"


@dataclass(slots=True)
class Signal:
    coin: str
    ts: int
    side: Side
    score: float
    features: FeatureVector
    reason: str = ""
    validated: bool = False
    rejections: list[str] = field(default_factory=list)


class RiskLevel(str, Enum):
    NORMAL = "normal"
    CAUTION = "caution"           # taille / 2
    HALT = "halt"                 # aucun nouveau trade (+ flatten optionnel)


@dataclass(slots=True)
class MacroState:
    ts: int
    level: RiskLevel
    reasons: list[str]
    llm_risk_score: Optional[float] = None
    until_ts: Optional[int] = None


@dataclass(slots=True)
class OrderEvent:
    coin: str
    ts: int
    side: Side
    size: float
    limit_px: float
    kind: str                     # entry | exit | stop | tp | flatten
    client_id: str
    status: str                   # sent | accepted | rejected | filled | cancelled
    latency_ms: float = 0.0
    info: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FillEvent:
    coin: str
    ts: int
    side: Side
    size: float
    px: float
    fee: float
    expected_px: float
    slippage_bps: float
    closed_pnl: float
    kind: str
    dry_run: bool


@dataclass(slots=True)
class ControlCommand:
    id: str
    cmd: str
    args: dict[str, Any]
    reason: str
    issued_by: str
