"""
orchestrator.py
---------------
Coordinates the simulation tick-by-tick advancement.

Each full tick executes in order:
  1. market.step(1)                         → updates prices
  2. For each professional:
       execute_strategy()                    → generates trade
       If trade executed → propagate_trade() → propagates to followers
  3. For each professional:
       update_follower_capital()             → recalculates retail exposure
  4. Optional JSON snapshot (SAVE_SNAPSHOTS=true)

Supports both manual ticks (via API) and an automatic background loop.
The lock ensures that auto-tick and manual ticks do not overlap.

Typical usage:
    from orchestrator import orchestrator
    summary = orchestrator.run_tick()
    orchestrator.start_auto_tick(interval_seconds=2.0)
    orchestrator.stop_auto_tick()
"""

import json
import logging
import os
import threading
from collections import deque
from pathlib import Path
from typing import List

from market.simulator import market_simulator
from traders.professional import professional_engine
from traders.copy_engine import copy_engine
from state import state, get_state_snapshot

logger = logging.getLogger(__name__)


class TickOrchestrator:
    """
    Coordinates the execution of a complete simulation tick.

    Guarantees the correct execution order between modules and prevents
    race conditions between manual ticks and the automatic loop via a Lock.

    Internal attributes:
        _tick_log:    deque holding the last 1000 tick summaries
        _lock:        threading.Lock shared between manual ticks and auto-tick
        _auto_thread: Thread for the automatic loop (None if not running)
        _stop_event:  Event used to signal the automatic loop to stop
    """

    def __init__(self) -> None:
        self._tick_log: deque = deque(maxlen=1000)
        self._lock = threading.Lock()
        self._auto_thread: threading.Thread = None
        self._stop_event = threading.Event()

    def run_tick(self) -> dict:
        """
        Executes a single complete tick following the defined order.

        Steps:
        1. Advances market prices (market_simulator.step)
        2. Each professional executes their own strategy
        3. Professional trades are propagated to followers
        4. The exposed capital of each professional is recalculated
        5. (Optional) Saves JSON snapshot if SAVE_SNAPSHOTS=true

        Thread-safe: acquires the lock before executing any step.

        Returns:
            dict with tick, prices, trades_executed, platform_pnl_delta,
            professionals_summary.
        """
        with self._lock:
            pnl_before = state.platform_pnl
            trades_executed = 0

            # Step 1: advance market prices
            market_simulator.step(1)

            # Step 2 + 3: each professional executes strategy and propagates to followers
            professionals_summary = []
            for trader_id in list(state.professional_traders.keys()):
                trade = professional_engine.execute_strategy(trader_id)
                trade_done = trade is not None

                if trade_done:
                    trades_executed += 1
                    copy_trades = copy_engine.propagate_trade(trade)
                    trades_executed += len(copy_trades)

                professionals_summary.append({
                    "id": trader_id,
                    "phase": state.professional_traders[trader_id].phase.value,
                    "trade_executed": trade_done,
                })

            # Step 4: recalculate exposed follower capital for each professional
            for trader_id in state.professional_traders:
                professional_engine.update_follower_capital(trader_id)

            summary = {
                "tick": state.current_tick,
                "prices": {
                    asset_id: round(asset.current_price, 4)
                    for asset_id, asset in state.assets.items()
                },
                "trades_executed": trades_executed,
                "platform_pnl_delta": round(state.platform_pnl - pnl_before, 4),
                "professionals_summary": professionals_summary,
            }

            self._tick_log.append(summary)

            # Step 5: optional snapshot (local file)
            if os.environ.get("SAVE_SNAPSHOTS", "").lower() == "true":
                self._save_snapshot()

            # Remote save every 100 ticks.
            # Locally JSONBIN_KEY is not configured, save_to_remote() is a no-op.
            # In production saves the snapshot to JSONBin to survive Render restarts.
            if state.current_tick % 100 == 0:
                state.save_to_remote()

            return summary

    def run_n_ticks(self, n: int) -> List[dict]:
        """
        Executes N consecutive ticks.

        Args:
            n: number of ticks to execute (>= 1).

        Returns:
            List of tick summaries, one per tick.
        """
        return [self.run_tick() for _ in range(n)]

    def start_auto_tick(self, interval_seconds: float = 2.0) -> None:
        """
        Starts a background loop that executes run_tick() every interval_seconds.

        If the loop is already running, a second one is not started.
        The thread is a daemon: it closes automatically when the process exits.

        Args:
            interval_seconds: interval between automatic ticks (default 2.0 s).
        """
        if self._auto_thread is not None and self._auto_thread.is_alive():
            logger.info("Auto-tick already running — ignored.")
            return

        self._stop_event.clear()

        def _loop() -> None:
            logger.info("Auto-tick started (interval %.1f s).", interval_seconds)
            while not self._stop_event.is_set():
                try:
                    self.run_tick()
                except Exception as exc:
                    logger.error("Error during auto-tick: %s", exc)
                self._stop_event.wait(timeout=interval_seconds)
            logger.info("Auto-tick stopped.")

        self._auto_thread = threading.Thread(target=_loop, daemon=True, name="auto-tick")
        self._auto_thread.start()

    def stop_auto_tick(self) -> None:
        """
        Stops the automatic loop.

        Signals the stop event and waits for the thread to terminate (max 5 s).
        """
        self._stop_event.set()
        if self._auto_thread is not None:
            self._auto_thread.join(timeout=5.0)
            self._auto_thread = None

    def is_auto_running(self) -> bool:
        """
        Returns True if the automatic loop is active.

        Returns:
            bool: True if the thread is alive and the stop signal has not been sent.
        """
        return (
            self._auto_thread is not None
            and self._auto_thread.is_alive()
            and not self._stop_event.is_set()
        )

    def get_tick_log(self, last_n: int = 10) -> List[dict]:
        """
        Returns summaries of the last N executed ticks.

        The log is kept in memory as a deque with maxlen=1000: older ticks
        are automatically discarded when the limit is reached.

        Args:
            last_n: number of most recent ticks to return (default 10).

        Returns:
            List of tick summaries ordered from oldest to most recent.
        """
        log_list = list(self._tick_log)
        return log_list[-last_n:] if last_n < len(log_list) else log_list

    def _save_snapshot(self) -> None:
        """
        Saves the current state to data/snapshot_{tick}.json.

        Called internally by run_tick() if SAVE_SNAPSHOTS=true.
        The data/ directory is created if it does not exist.
        """
        try:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            snapshot_path = data_dir / f"snapshot_{state.current_tick}.json"
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(get_state_snapshot(), f, indent=2, default=str)
        except Exception as exc:
            logger.error("Error saving snapshot: %s", exc)


# ── Global instance ────────────────────────────────────────────────────────
# Importable directly: from orchestrator import orchestrator
orchestrator = TickOrchestrator()
