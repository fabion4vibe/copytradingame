"""
simulator.py
------------
Implements `MarketSimulator`: manages all simulated assets and advances
prices tick by tick using the GBM (Geometric Brownian Motion) model.

Only this module is authorised to modify `state.current_tick`.
"""

import numpy as np
from typing import List, Optional

from market.asset import Asset
from state import state


# ── Time constant ─────────────────────────────────────────────────────────
# dt = 1 means each tick corresponds to one unit of time.
# All quantities (drift, volatility) are expressed per tick.
DT: float = 1.0


class MarketSimulator:
    """
    Manages price simulation for all registered assets.

    Responsibilities:
    - Initialise the default assets
    - Advance prices for all assets applying the discrete GBM
    - Update state.current_tick (only this module is authorised to do so)
    - Provide access to current prices and the price history

    Discrete GBM model:
        P(t+1) = P(t) * exp( (μ - σ²/2) * dt  +  σ * √dt * Z )
        where Z ~ N(0, 1)
    """

    def initialize_default_assets(self) -> None:
        """
        Creates the 5 predefined simulated assets and inserts them into state.assets.

        Assets created:
            SIM-A: price 100, σ=0.02, μ=+0.001  — stable, slight upward drift
            SIM-B: price  50, σ=0.04, μ= 0.000  — neutral, high volatility
            SIM-C: price 200, σ=0.01, μ=+0.002  — steady growth, low volatility
            SIM-D: price  75, σ=0.05, μ=-0.001  — volatile, slight structural decline
            SIM-E: price  30, σ=0.03, μ= 0.000  — neutral, medium volatility

        Each asset is inserted in state.assets with key = asset.id.
        price_history is initialised with only the initial price (tick 0).
        """
        default_configs = [
            ("sim-a", "SIM-A", 100.0, 0.02,  0.001),
            ("sim-b", "SIM-B",  50.0, 0.04,  0.000),
            ("sim-c", "SIM-C", 200.0, 0.01,  0.002),
            ("sim-d", "SIM-D",  75.0, 0.05, -0.001),
            ("sim-e", "SIM-E",  30.0, 0.03,  0.000),
        ]

        for asset_id, symbol, price, volatility, drift in default_configs:
            asset = Asset(
                id=asset_id,
                symbol=symbol,
                initial_price=price,
                current_price=price,
                volatility=volatility,
                drift=drift,
                price_history=[price],  # price_history[0] == initial_price
            )
            state.assets[asset_id] = asset

    def step(self, n_ticks: int = 1) -> None:
        """
        Advances the simulation by n_ticks applying the discrete GBM to every asset.

        For each tick:
            1. For every asset in state.assets, compute the new price:
               P(t+1) = P(t) * exp( (μ - σ²/2) * dt  +  σ * √dt * Z )
               with Z ~ N(0,1) sampled independently per asset and per tick.
            2. Updates asset.current_price and appends to asset.price_history.
            3. Increments state.current_tick by 1.

        Price is clamped to >= 0.01 (GBM guarantees positivity mathematically,
        but the clamp guards against extreme numerical underflow).

        Args:
            n_ticks: number of ticks to simulate in sequence. Default = 1.
        """
        for _ in range(n_ticks):
            for asset in state.assets.values():
                mu = asset.drift
                sigma = asset.volatility
                p_t = asset.current_price

                # Discrete GBM: drift corrected for convexity (Itô)
                z = float(np.random.normal(0.0, 1.0))
                exponent = (mu - 0.5 * sigma ** 2) * DT + sigma * np.sqrt(DT) * z
                p_next = p_t * np.exp(exponent)

                # Guard against underflow (theoretically impossible with GBM)
                p_next = max(p_next, 0.01)

                asset.current_price = p_next
                asset.price_history.append(p_next)

            # Increment tick after all assets have been updated
            state.current_tick += 1

    def get_price(self, asset_id: str) -> float:
        """
        Returns the current price of an asset.

        Args:
            asset_id: asset identifier (e.g. "sim-a").

        Returns:
            float: current price of the asset.

        Raises:
            KeyError: if asset_id does not exist in state.assets.
        """
        return state.assets[asset_id].current_price

    def get_history(self, asset_id: str, last_n: Optional[int] = None) -> List[float]:
        """
        Returns the price history of an asset.

        Args:
            asset_id: asset identifier.
            last_n:   if specified, returns only the last N values.
                      If None or greater than the total length, returns
                      the entire price history.

        Returns:
            List[float]: price series (or final subset).

        Raises:
            KeyError: if asset_id does not exist in state.assets.
        """
        history = state.assets[asset_id].price_history
        if last_n is not None and last_n < len(history):
            return history[-last_n:]
        return list(history)

    def add_asset(self, asset: Asset) -> None:
        """
        Adds a custom asset to the simulation.

        If price_history is empty, initialises it with the current current_price.
        The asset is inserted in state.assets with key = asset.id.

        Args:
            asset: Asset instance to add.
        """
        if not asset.price_history:
            asset.price_history = [asset.current_price]
        state.assets[asset.id] = asset


# ── Global instance ───────────────────────────────────────────────────────
# Importable directly: from market.simulator import market_simulator
market_simulator = MarketSimulator()
