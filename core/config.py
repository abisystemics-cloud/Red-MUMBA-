"""Configuration typée + rechargement à chaud atomique.

Le ConfigStore surveille `config.yaml` (polling mtime, sans dépendance externe).
Quand le fichier change, il est revalidé ; si la validation échoue, l'ancienne
configuration reste active. Seule la section `strategy` est appliquée à chaud :
un changement ailleurs est journalisé et nécessite un redémarrage.
"""
from __future__ import annotations

import asyncio
import copy
import logging
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

import yaml
from pydantic import BaseModel, Field, field_validator

log = logging.getLogger("core.config")


class Market(BaseModel):
    coin: str
    binance: Optional[str] = None
    bybit: Optional[str] = None


class Runtime(BaseModel):
    network: str = "testnet"
    dry_run: bool = True
    log_level: str = "INFO"
    health_port: int = 8080
    config_poll_seconds: float = 2.0

    @field_validator("network")
    @classmethod
    def _net(cls, v: str) -> str:
        if v not in ("testnet", "mainnet"):
            raise ValueError("network must be testnet|mainnet")
        return v


class HLData(BaseModel):
    ws_url_mainnet: str
    ws_url_testnet: str
    api_url_mainnet: str
    api_url_testnet: str
    book_levels: int = 20
    n_sig_figs: Optional[int] = None


class Liquidations(BaseModel):
    provider: str = "disabled"
    poll_seconds: int = 60
    coinglass_base_url: str = "https://open-api-v4.coinglass.com"
    coinglass_heatmap_path: str = "/api/futures/liquidation/heatmap/model1"
    firecrawl_url: str = ""


class DataCfg(BaseModel):
    hyperliquid: HLData
    binance_ws: str
    bybit_ws: str
    liquidations: Liquidations = Liquidations()
    record_market_data: bool = True
    recordings_dir: str = "data/recordings"
    max_staleness_ms: int = 2500


class ScheduledEvent(BaseModel):
    name: str
    at: str


class MacroCfg(BaseModel):
    enabled: bool = True
    poll_seconds: int = 300
    blackout_minutes_before: int = 10
    blackout_minutes_after: int = 20
    scheduled_events: list[ScheduledEvent] = Field(default_factory=list)
    btc_1m_move_halt_pct: float = 2.5
    cex_divergence_halt_bps: float = 80
    llm_model: str = "sonar"
    llm_halt_threshold: float = 0.8
    llm_caution_threshold: float = 0.5


class Weights(BaseModel):
    obi: float = 0.35
    cvd: float = 0.30
    premium: float = 0.25
    poc: float = 0.10


class StrategyCfg(BaseModel):
    obi_depth: int = 10
    obi_decay: float = 0.15
    cvd_window_s: int = 60
    vpvr_window_s: int = 900
    vpvr_bucket_bps: float = 5
    zscore_window: int = 300
    spoof_size_mult: float = 8.0
    spoof_max_life_s: float = 3.0
    weights: Weights = Weights()
    entry_threshold: float = 1.6
    exit_threshold: float = 0.4
    persistence_ticks: int = 3
    max_spread_bps: float = 4.0
    max_hold_s: int = 600
    cooldown_s: int = 30


class RiskCfg(BaseModel):
    kelly_fraction: float = 0.25
    max_risk_per_trade_pct: float = 0.5
    max_position_notional_usd: float = 5000
    max_leverage: float = 3
    stop_vol_mult: float = 2.5
    take_profit_r: float = 2.0
    min_stop_bps: float = 8
    max_stop_bps: float = 150
    daily_loss_limit_pct: float = 3.0
    max_consecutive_losses: int = 5
    slippage_bps: float = 3
    prior_win_rate: float = 0.52
    prior_payoff: float = 1.2
    flatten_on_halt: bool = True
    paper_equity_usd: float = 10000

    @field_validator("kelly_fraction")
    @classmethod
    def _kelly(cls, v: float) -> float:
        if not 0 < v <= 1:
            raise ValueError("kelly_fraction must be in (0, 1]")
        return v


class TelemetryCfg(BaseModel):
    posthog_host: str = "https://eu.i.posthog.com"
    flush_interval_s: float = 1.0
    batch_size: int = 500
    distinct_id: str = "hl-swarm"
    local_log_dir: str = "data/telemetry"


class ResearchCfg(BaseModel):
    enabled: bool = True
    check_interval_s: int = 3600
    lookback_hours: int = 24
    min_trades_for_eval: int = 20
    degrade_sharpe_below: float = 0.5
    degrade_winrate_below: float = 0.45
    max_drawdown_pct: float = 10.0
    n_trials: int = 60
    oos_fraction: float = 0.3
    max_param_change_pct: float = 30
    auto_deploy: bool = True
    bounds: dict[str, list[float]] = Field(default_factory=dict)


class AppConfig(BaseModel):
    version: int = 1
    runtime: Runtime
    markets: list[Market]
    data: DataCfg
    macro: MacroCfg = MacroCfg()
    strategy: StrategyCfg = StrategyCfg()
    risk: RiskCfg = RiskCfg()
    telemetry: TelemetryCfg = TelemetryCfg()
    research: ResearchCfg = ResearchCfg()

    # --- helpers ------------------------------------------------------------
    @property
    def is_mainnet(self) -> bool:
        return self.runtime.network == "mainnet"

    def hl_ws_url(self) -> str:
        override = os.getenv("HL_BOOK_WS_URL")
        if override:
            return override
        h = self.data.hyperliquid
        return h.ws_url_mainnet if self.is_mainnet else h.ws_url_testnet

    def hl_api_url(self) -> str:
        h = self.data.hyperliquid
        return h.api_url_mainnet if self.is_mainnet else h.api_url_testnet

    def live_trading_armed(self) -> bool:
        """Triple verrou : mainnet + dry_run=false + confirmation explicite."""
        return (
            self.is_mainnet
            and not self.runtime.dry_run
            and os.getenv("LIVE_TRADING_CONFIRM") == "I_UNDERSTAND_THE_RISKS"
        )


def load_config(path: str | Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    return AppConfig.model_validate(raw)


Listener = Callable[[AppConfig, AppConfig], Awaitable[None] | None]


class ConfigStore:
    """Détient la config courante et la recharge à chaud."""

    HOT_SECTIONS = ("strategy",)

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._cfg = load_config(self.path)
        self._mtime = self.path.stat().st_mtime
        self._listeners: list[Listener] = []
        self.reload_count = 0

    @property
    def current(self) -> AppConfig:
        return self._cfg

    def subscribe(self, fn: Listener) -> None:
        self._listeners.append(fn)

    async def watch(self, stop: asyncio.Event) -> None:
        poll = self._cfg.runtime.config_poll_seconds
        while not stop.is_set():
            try:
                await asyncio.wait_for(stop.wait(), timeout=poll)
            except asyncio.TimeoutError:
                pass
            await self.check_reload()

    async def check_reload(self) -> bool:
        try:
            mtime = self.path.stat().st_mtime
        except FileNotFoundError:
            return False
        if mtime == self._mtime:
            return False
        self._mtime = mtime
        try:
            new_cfg = load_config(self.path)
        except Exception as exc:  # noqa: BLE001
            log.error("config reload rejected (invalid): %s", exc)
            return False
        old = self._cfg
        cold_changed = [
            k for k in AppConfig.model_fields
            if k not in self.HOT_SECTIONS and getattr(old, k) != getattr(new_cfg, k)
        ]
        if cold_changed:
            log.warning("non-hot sections changed %s: restart needed to apply them", cold_changed)
            merged = old.model_copy(update={"strategy": new_cfg.strategy})
        else:
            merged = new_cfg
        self._cfg = merged
        self.reload_count += 1
        log.info("config hot-reloaded (#%d) strategy=%s", self.reload_count, merged.strategy.model_dump())
        for fn in self._listeners:
            res = fn(old, merged)
            if asyncio.iscoroutine(res):
                await res
        return True


def atomic_update_strategy(path: str | Path, new_strategy: dict[str, Any],
                           history_dir: str | Path | None = None) -> Path:
    """Réécrit uniquement la section `strategy` de config.yaml, de façon atomique.

    Le fichier précédent est archivé (audit/rollback). Écriture via fichier
    temporaire + os.replace : le ConfigStore ne voit jamais un fichier partiel.
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    candidate = copy.deepcopy(raw)
    candidate["strategy"] = new_strategy
    AppConfig.model_validate(candidate)  # refuse d'écrire une config invalide

    hist = Path(history_dir) if history_dir else path.parent / "config_history"
    hist.mkdir(parents=True, exist_ok=True)
    backup = hist / f"config.{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.yaml"
    shutil.copy2(path, backup)

    text = path.read_text(encoding="utf-8")
    new_text = _replace_top_level_block(text, "strategy", new_strategy)
    # contrôle final : le texte produit doit redonner exactement `candidate`
    if yaml.safe_load(new_text) != candidate:
        new_text = yaml.safe_dump(candidate, sort_keys=False, allow_unicode=True)

    fd, tmp = tempfile.mkstemp(prefix=".config.", suffix=".yaml", dir=str(path.parent))
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    os.replace(tmp, path)
    return backup


def _replace_top_level_block(text: str, key: str, value: dict[str, Any]) -> str:
    """Remplace le bloc YAML `key:` de premier niveau en conservant les
    commentaires du reste du fichier."""
    lines = text.splitlines(keepends=True)
    start = next((i for i, ln in enumerate(lines) if ln.startswith(f"{key}:")), None)
    if start is None:
        return text + "\n" + yaml.safe_dump({key: value}, sort_keys=False)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        if ln.strip() and not ln[0].isspace() and not ln.lstrip().startswith("#"):
            end = j
            break
    # garder les commentaires/lignes vides qui précèdent la section suivante
    while end - 1 > start and (not lines[end - 1].strip() or lines[end - 1].lstrip().startswith("#")) \
            and not lines[end - 1][:1].isspace():
        end -= 1
    header = f"{key}:                       # ← section rechargée à chaud (réécrite par l'agent R&D)\n"
    body = yaml.safe_dump(value, sort_keys=False, allow_unicode=True, default_flow_style=False)
    body = "".join("  " + ln if ln.strip() else ln for ln in body.splitlines(keepends=True))
    return "".join(lines[:start]) + header + body + "\n" + "".join(lines[end:]).lstrip("\n")
