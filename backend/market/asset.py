"""
asset.py
--------
Defines the `Asset` data structure representing a single simulated financial
instrument. Each asset maintains its own price history and the GBM model
parameters (drift and volatility).
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List


@dataclass
class Asset:
    """
    Represents a simulated financial asset.

    Attributes:
        id            — unique identifier (e.g. "sim-a")
        symbol        — human-readable symbol (e.g. "SIM-A")
        initial_price — price at tick 0, used as the return reference
        current_price — current price, updated every tick by MarketSimulator
        volatility    — σ (sigma): standard deviation of return per tick
        drift         — μ (mu): expected return per tick (can be negative)
        price_history — complete price series; price_history[0] == initial_price
    """

    id: str
    symbol: str
    initial_price: float
    current_price: float
    volatility: float
    drift: float
    price_history: List[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        """
        Serializes the asset to a JSON-compatible dictionary.

        Does not include price_history by default (can be large);
        use get_history() on the simulator for the full price series.

        Returns:
            dict with the main asset fields, compatible with the Asset
            schema defined in openapi.yaml.
        """
        return {
            "id": self.id,
            "symbol": self.symbol,
            "initial_price": self.initial_price,
            "current_price": self.current_price,
            "volatility": self.volatility,
            "drift": self.drift,
            "current_return": self.current_return(),
        }

    def current_return(self) -> float:
        """
        Percentage return (in decimal form) since the start of the simulation.

        Formula: (current_price - initial_price) / initial_price

        Returns:
            float: e.g. 0.05 means +5%, -0.12 means -12%.
                   Returns 0.0 if initial_price is zero (degenerate case).
        """
        if self.initial_price == 0.0:
            return 0.0
        return (self.current_price - self.initial_price) / self.initial_price

    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        """
        Reconstructs an Asset from a snapshot dictionary.

        Initialises price_history with only the current_price (price_history
        is not included in the snapshot to keep the payload size small).

        Args:
            data: dictionary produced by to_dict().

        Returns:
            Restored Asset instance.
        """
        asset = cls(
            id=data["id"],
            symbol=data["symbol"],
            initial_price=data["initial_price"],
            current_price=data["current_price"],
            volatility=data["volatility"],
            drift=data["drift"],
        )
        asset.price_history = [data["current_price"]]
        return asset

    def volatility_realized(self) -> float:
        """
        Realized volatility: standard deviation of historical log-returns.

        Computed as the std of log-returns: ln(P[t] / P[t-1])

        Returns:
            float: realized volatility. Returns 0.0 if price_history has
                   fewer than 2 observations (returns cannot be computed).
        """
        if len(self.price_history) < 2:
            return 0.0

        prices = np.array(self.price_history, dtype=float)
        # Filter prices <= 0 to avoid log of non-positive values
        prices = prices[prices > 0]
        if len(prices) < 2:
            return 0.0

        log_returns = np.log(prices[1:] / prices[:-1])
        return float(np.std(log_returns))
