"""
state.py
--------
Single source of truth for the entire simulation.
All backend modules import from this file to read and write
the shared state. No database: everything lives in memory.

Typical usage in other modules:
    from state import state

    state.current_tick += 1
    state.assets["SIM-A"] = my_asset
    state.platform_pnl += 150.0
"""

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List

# NOTE: no imports from other project modules to avoid circular dependencies.
# Any types will be replaced with specific classes by subsequent tasks
# as the modules are created.

# ── JSONBin.io configuration ───────────────────────────────────────────────
# Environment variables are None locally: persistence methods
# become no-ops automatically.
JSONBIN_BASE_URL = "https://api.jsonbin.io/v3/b"
JSONBIN_KEY = os.environ.get("JSONBIN_KEY")        # None in locale
JSONBIN_BIN_ID = os.environ.get("JSONBIN_BIN_ID")  # None in locale


@dataclass
class SimulationState:
    """
    Global simulation state, shared across all backend modules.

    Fields:
        current_tick          — current simulation tick (advanced by MarketSimulator)
        assets                — dict asset_id → Asset (populated by TASK_02)
        retail_traders        — dict id → RetailTrader (populated by TASK_03)
        professional_traders  — dict id → ProfessionalTrader (populated by TASK_04)
        copy_relations        — list of active and inactive CopyRelations (populated by TASK_05)
        platform_pnl          — cumulative platform profit (net retail losses)
        platform_commissions  — accumulated commissions (not used in initial tasks)
        platform_bonus_paid   — total bonuses paid to professional traders in phase C
        trade_log             — global log of all trades executed (retail + professionals)
    """

    # ── Market ────────────────────────────────────────────────────────────
    current_tick: int = 0
    assets: Dict[str, Any] = field(default_factory=dict)          # asset_id → Asset

    # ── Traders ───────────────────────────────────────────────────────────
    retail_traders: Dict[str, Any] = field(default_factory=dict)        # id → RetailTrader
    professional_traders: Dict[str, Any] = field(default_factory=dict)  # id → ProfessionalTrader

    # ── Copy trading ──────────────────────────────────────────────────────
    copy_relations: List[Any] = field(default_factory=list)        # list of CopyRelation

    # ── Platform economics ────────────────────────────────────────────────
    platform_pnl: float = 0.0           # cumulative profit (from retail losses)
    platform_commissions: float = 0.0   # accumulated commissions
    platform_bonus_paid: float = 0.0    # bonuses paid to professionals in phase C

    # ── Global history ────────────────────────────────────────────────────
    trade_log: List[Any] = field(default_factory=list)             # all trades executed

    def get_state_snapshot(self) -> dict:
        """
        Returns a complete snapshot of the state, serializable to JSON.
        Used both for debug/export and for remote persistence (JSONBin).

        The trade_log is truncated to the last 500 entries to keep
        the JSON payload size within reasonable limits for the JSONBin free tier.
        """
        return {
            "current_tick":         self.current_tick,
            "platform_pnl":         self.platform_pnl,
            "platform_commissions": self.platform_commissions,
            "platform_bonus_paid":  self.platform_bonus_paid,
            "assets": {
                asset_id: asset.to_dict()
                for asset_id, asset in self.assets.items()
            },
            "retail_traders": {
                trader_id: trader.to_dict()
                for trader_id, trader in self.retail_traders.items()
            },
            "professional_traders": {
                trader_id: trader.to_dict()
                for trader_id, trader in self.professional_traders.items()
            },
            "copy_relations": [cr.to_dict() for cr in self.copy_relations],
            "trade_log": [t.to_dict() for t in self.trade_log[-500:]],
        }

    def save_to_remote(self) -> None:
        """
        Persists the current state to JSONBin.io via HTTP PUT.

        Does nothing if JSONBIN_KEY or JSONBIN_BIN_ID are not configured
        (expected behaviour in local environment).

        Does not raise exceptions: if saving fails (timeout, network,
        rate limit), the tick continues normally. The next scheduled
        save will retry.
        """
        if not JSONBIN_KEY or not JSONBIN_BIN_ID:
            return

        url = f"{JSONBIN_BASE_URL}/{JSONBIN_BIN_ID}"
        payload = json.dumps(self.get_state_snapshot()).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "X-Master-Key": JSONBIN_KEY,
        }
        req = urllib.request.Request(
            url, data=payload, headers=headers, method="PUT"
        )
        try:
            urllib.request.urlopen(req, timeout=3)
        except (urllib.error.URLError, TimeoutError):
            pass  # DIDACTIC: save failure does not block the simulation tick

    @classmethod
    def load_from_remote(cls) -> "dict | None":
        """
        Loads the latest snapshot saved on JSONBin.io.

        Returns the snapshot dictionary if available,
        None in all other cases (local env, no network, empty bin,
        malformed response).
        """
        if not JSONBIN_KEY or not JSONBIN_BIN_ID:
            return None

        url = f"{JSONBIN_BASE_URL}/{JSONBIN_BIN_ID}/latest"
        headers = {"X-Master-Key": JSONBIN_KEY}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("record")  # JSONBin wraps the content under the "record" key
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
            return None


# ── Singleton ─────────────────────────────────────────────────────────────
# Shared instance, importable directly:
#     from state import state
state = SimulationState()


# ── Helper functions ──────────────────────────────────────────────────────

def reset_state() -> None:
    """
    Resets the global state to its initial values.

    Mutates the existing instance instead of recreating it, so that all modules
    that already imported `state` with `from state import state` continue
    to point to the correct object after the reset.

    Useful for restarting the simulation via the /manager/reset endpoint.
    """
    state.current_tick = 0
    state.assets.clear()
    state.retail_traders.clear()
    state.professional_traders.clear()
    state.copy_relations.clear()
    state.platform_pnl = 0.0
    state.platform_commissions = 0.0
    state.platform_bonus_paid = 0.0
    state.trade_log.clear()


def _serialize(obj: Any) -> Any:
    """
    Recursively converts an object to a JSON-serializable type.

    Strategy:
    - Objects with a `to_dict()` method → calls to_dict() (domain module convention)
    - dict → recurses over values
    - list → recurses over elements
    - Primitives (int, float, str, bool, None) → passed as-is
    - Everything else → converted to string as fallback
    """
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    # Fallback: enum, dataclass without to_dict, etc.
    return str(obj)


def get_state_snapshot() -> dict:
    """
    Module-level wrapper for state.get_state_snapshot().

    Kept for compatibility with modules that import this function
    directly (e.g. orchestrator.py).

    Returns:
        dict with all SimulationState fields in JSON-compatible format.
    """
    return state.get_state_snapshot()
