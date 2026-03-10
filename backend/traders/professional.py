"""
professional.py
---------------
Implements ProfessionalTrader with the finite state machine (FSM) that controls
the trader's behaviour across the three lifecycle phases.

Educational core of the project: shows how an apparently independent trader is
in reality controlled by the platform through incentives and phase transitions.

Typical usage:
    from traders.professional import ProfessionalTraderEngine, TraderPhase
    engine = ProfessionalTraderEngine()
    trader = engine.create_professional_trader("Marco")
    trade  = engine.execute_strategy(trader.id)
"""

import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from state import state
from traders.retail import Trade, retail_engine


# ── TraderPhase enum ──────────────────────────────────────────────────────

class TraderPhase(str, Enum):
    """
    Lifecycle phases of a professional trader.

    REPUTATION_BUILD — Phase A: the trader operates with positive EV to build
                       an attractive track record and attract early followers.
    FOLLOWER_GROWTH  — Phase B: the trader maintains good performance to attract
                       more followers and increase exposed retail capital.
    MONETIZATION     — Phase C: the platform activates monetisation. The trader
                       starts operating with negative EV, harming followers,
                       while receiving a fixed bonus for each tick in this phase.
    """

    REPUTATION_BUILD = "REPUTATION_BUILD"
    FOLLOWER_GROWTH  = "FOLLOWER_GROWTH"
    MONETIZATION     = "MONETIZATION"


# ── StrategyProfile dataclass ─────────────────────────────────────────────

@dataclass
class StrategyProfile:
    """
    Operational parameters defining the trader's behaviour per phase.

    Fields:
        expected_value          — expected EV per trade (positive in A/B, negative in C)
        risk_level              — 0.0–1.0: influences position sizing
        trade_frequency         — probability of executing a trade per tick (0.0–1.0)
        min_followers_for_B     — follower threshold for automatic A→B transition
        min_followers_for_C     — follower threshold for automatic B→C transition
        target_capital_exposed  — target exposed retail capital to activate phase C
        bonus_per_tick_in_C     — fixed bonus paid by the platform per tick in phase C
    """

    expected_value: float
    risk_level: float
    trade_frequency: float
    min_followers_for_B: int
    min_followers_for_C: int
    target_capital_exposed: float
    bonus_per_tick_in_C: float

    def to_dict(self) -> dict:
        """Serializes the strategy profile to a JSON-compatible dictionary."""
        return {
            "expected_value": self.expected_value,
            "risk_level": self.risk_level,
            "trade_frequency": self.trade_frequency,
            "min_followers_for_B": self.min_followers_for_B,
            "min_followers_for_C": self.min_followers_for_C,
            "target_capital_exposed": self.target_capital_exposed,
            "bonus_per_tick_in_C": self.bonus_per_tick_in_C,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StrategyProfile":
        """Reconstructs a StrategyProfile from a snapshot dictionary."""
        return cls(
            expected_value=data["expected_value"],
            risk_level=data["risk_level"],
            trade_frequency=data["trade_frequency"],
            min_followers_for_B=data["min_followers_for_B"],
            min_followers_for_C=data["min_followers_for_C"],
            target_capital_exposed=data["target_capital_exposed"],
            bonus_per_tick_in_C=data["bonus_per_tick_in_C"],
        )


# ── Default strategy profiles ─────────────────────────────────────────────

DEFAULT_STRATEGY_A = StrategyProfile(
    expected_value=+0.015,       # positive EV: on average +1.5% per trade
    risk_level=0.2,
    trade_frequency=0.4,         # 40% probability of trading per tick
    min_followers_for_B=5,
    min_followers_for_C=15,
    target_capital_exposed=50000.0,
    bonus_per_tick_in_C=0.0,     # no bonus in phase A
)

DEFAULT_STRATEGY_B = StrategyProfile(
    expected_value=+0.008,       # still positive EV, more conservative
    risk_level=0.3,
    trade_frequency=0.6,
    min_followers_for_B=5,
    min_followers_for_C=15,
    target_capital_exposed=50000.0,
    bonus_per_tick_in_C=0.0,
)

DEFAULT_STRATEGY_C = StrategyProfile(
    expected_value=-0.020,       # negative EV: on average -2% per trade
    risk_level=0.7,
    trade_frequency=0.8,         # high frequency to maximise follower losses
    min_followers_for_B=5,
    min_followers_for_C=15,
    target_capital_exposed=50000.0,
    bonus_per_tick_in_C=200.0,   # fixed bonus per tick in phase C
)

# Phase → default profile map (used by transition_phase)
_DEFAULT_STRATEGY_BY_PHASE = {
    TraderPhase.REPUTATION_BUILD: DEFAULT_STRATEGY_A,
    TraderPhase.FOLLOWER_GROWTH:  DEFAULT_STRATEGY_B,
    TraderPhase.MONETIZATION:     DEFAULT_STRATEGY_C,
}

# Random names for simulated traders
_PRO_NAMES = [
    "Maverick", "Oracle", "Falcon", "Titan", "Apex",
    "Vector", "Cipher", "Nexus", "Zenith", "Phantom",
]


# ── ProfessionalTrader dataclass ──────────────────────────────────────────

@dataclass
class ProfessionalTrader:
    """
    Represents a professional trader controlled by the platform's FSM.

    Fields:
        id                      — unique UUID
        name                    — display name
        phase                   — current FSM phase
        strategy                — active strategy profile for this phase
        balance                 — available cash
        portfolio               — asset_id → quantity held
        avg_buy_prices          — asset_id → weighted average entry price
        pnl_personal            — PnL accumulated from actual trading
        bonus_earned            — total bonuses received from the platform (phase C)
        followers               — list of retail_trader_ids copying this trader
        follower_capital_exposed — sum of followers' portfolio values
        trade_history           — list of executed Trades
        phase_history           — log of phase changes with didactic details
        initial_balance         — starting balance for PnL calculation
    """

    id: str
    name: str
    phase: TraderPhase
    strategy: StrategyProfile
    balance: float
    portfolio: Dict[str, float] = field(default_factory=dict)
    avg_buy_prices: Dict[str, float] = field(default_factory=dict)
    pnl_personal: float = 0.0
    bonus_earned: float = 0.0
    followers: List[str] = field(default_factory=list)
    follower_capital_exposed: float = 0.0
    trade_history: List[Any] = field(default_factory=list)
    phase_history: List[dict] = field(default_factory=list)
    initial_balance: float = 50000.0

    def to_dict(self) -> dict:
        """Serializes the professional trader to a JSON-compatible dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "phase": self.phase.value,
            "strategy": self.strategy.to_dict(),
            "balance": self.balance,
            "portfolio": dict(self.portfolio),
            "avg_buy_prices": dict(self.avg_buy_prices),
            "pnl_personal": self.pnl_personal,
            "bonus_earned": self.bonus_earned,
            "followers": list(self.followers),
            "follower_capital_exposed": self.follower_capital_exposed,
            "trade_history": [t.to_dict() for t in self.trade_history],
            "phase_history": list(self.phase_history),
            "initial_balance": self.initial_balance,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ProfessionalTrader":
        """Reconstructs a ProfessionalTrader from a snapshot dictionary."""
        trader = cls(
            id=data["id"],
            name=data["name"],
            phase=TraderPhase(data["phase"]),
            strategy=StrategyProfile.from_dict(data["strategy"]),
            balance=data["balance"],
            portfolio=data.get("portfolio", {}),
            avg_buy_prices=data.get("avg_buy_prices", {}),
            pnl_personal=data.get("pnl_personal", 0.0),
            bonus_earned=data.get("bonus_earned", 0.0),
            followers=data.get("followers", []),
            follower_capital_exposed=data.get("follower_capital_exposed", 0.0),
            phase_history=data.get("phase_history", []),
            initial_balance=data.get("initial_balance", 50000.0),
        )
        trader.trade_history = [Trade.from_dict(t) for t in data.get("trade_history", [])]
        return trader


# ── Engine ─────────────────────────────────────────────────────────────────

class ProfessionalTraderEngine:
    """
    Manages creation, strategy execution and phase transitions for professional traders.

    The FSM (finite state machine) is the central mechanism: the platform controls
    when and how the trader changes behaviour, independently of the trader's own will.
    """

    def create_professional_trader(
        self,
        name: str,
        initial_phase: TraderPhase = TraderPhase.REPUTATION_BUILD,
        strategy: Optional[StrategyProfile] = None,
    ) -> ProfessionalTrader:
        """
        Creates a new ProfessionalTrader and adds it to state.professional_traders.

        Args:
            name:          trader name.
            initial_phase: initial FSM phase (default: REPUTATION_BUILD).
            strategy:      strategy profile. If None, uses the default profile
                           for the initial phase.

        Returns:
            The newly created ProfessionalTrader.
        """
        if strategy is None:
            strategy = _DEFAULT_STRATEGY_BY_PHASE[initial_phase]

        trader = ProfessionalTrader(
            id=str(uuid.uuid4()),
            name=name,
            phase=initial_phase,
            strategy=strategy,
            balance=50000.0,
            initial_balance=50000.0,
        )
        state.professional_traders[trader.id] = trader
        return trader

    def execute_strategy(self, trader_id: str) -> Optional[Trade]:
        """
        Executes the professional's strategy for the current tick.

        Logic:
        1. Draws random() — if >= trade_frequency, no trade this tick.
        2. Picks a random asset from state.assets.
        3. Determines the action based on the phase:
           - REPUTATION_BUILD / FOLLOWER_GROWTH:
               Buys assets with drift >= 0 (positive trend), sells assets with
               drift < 0 (negative trend). Expected positive EV.
           - MONETIZATION:
               Inverts the logic: buys falling assets, sells rising assets.
               Expected negative EV, maximising losses for copying followers.
        4. Computes the quantity based on risk_level and available balance/portfolio.
        5. Executes the trade, updating balance, portfolio and avg_buy_prices.
        6. If in MONETIZATION, credits bonus_per_tick_in_C to the trader and updates
           state.platform_bonus_paid and state.platform_pnl.

        Args:
            trader_id: ProfessionalTrader id.

        Returns:
            The executed Trade, or None if no trade this tick.
        """
        trader = state.professional_traders[trader_id]

        # 1. Trade probability for this tick
        if random.random() >= trader.strategy.trade_frequency:
            return None

        # 2. Random asset
        if not state.assets:
            return None
        asset_id = random.choice(list(state.assets.keys()))
        asset = state.assets[asset_id]
        current_price = asset.current_price

        # 3. Preferred action based on phase and asset drift
        in_monetization = (trader.phase == TraderPhase.MONETIZATION)
        if not in_monetization:
            # A/B: positive EV → follow the trend
            prefer_buy = (asset.drift >= 0)
        else:
            # C: negative EV → go against the trend (buy what falls)
            prefer_buy = (asset.drift < 0)

        # 4. Compute quantity and check feasibility
        trade = self._try_execute(trader, asset_id, current_price, prefer_buy)
        if trade is None:
            return None

        # 5. If in MONETIZATION, accumulate platform bonus
        if in_monetization:
            bonus = trader.strategy.bonus_per_tick_in_C
            if bonus > 0:
                trader.bonus_earned += bonus
                state.platform_bonus_paid += bonus
                state.platform_pnl -= bonus   # the bonus is a cost for the platform

        return trade

    def _try_execute(
        self,
        trader: ProfessionalTrader,
        asset_id: str,
        current_price: float,
        prefer_buy: bool,
    ) -> Optional[Trade]:
        """
        Attempts to execute a trade for the professional.

        Tries the preferred action first; if not feasible, tries the opposite.
        Returns None if neither can be executed.

        Args:
            trader:        ProfessionalTrader instance.
            asset_id:      asset id.
            current_price: current price of the asset.
            prefer_buy:    True if the preferred action is BUY.

        Returns:
            Executed Trade, or None.
        """
        for action in (("BUY" if prefer_buy else "SELL"),
                       ("SELL" if prefer_buy else "BUY")):
            trade = self._execute_action(trader, asset_id, current_price, action)
            if trade is not None:
                return trade
        return None

    def _execute_action(
        self,
        trader: ProfessionalTrader,
        asset_id: str,
        current_price: float,
        action: str,
    ) -> Optional[Trade]:
        """
        Concretely executes a BUY or SELL on the professional's portfolio.

        Logic analogous to RetailTraderEngine.execute_trade, but operates on
        ProfessionalTrader fields. Does not call retail execute_trade to avoid
        coupling between different trader types.

        Args:
            trader:        ProfessionalTrader instance to update.
            asset_id:      asset id.
            current_price: current price.
            action:        "BUY" or "SELL".

        Returns:
            Recorded Trade, or None if the action cannot be executed.
        """
        pnl_realized = 0.0

        if action == "BUY":
            # Quantity proportional to risk_level and available balance
            max_spend = trader.strategy.risk_level * 0.25 * trader.balance
            quantity = max_spend / current_price if current_price > 0 else 0.0
            if quantity < 1e-6 or trader.balance < quantity * current_price:
                return None

            old_qty = trader.portfolio.get(asset_id, 0.0)
            old_avg = trader.avg_buy_prices.get(asset_id, 0.0)
            new_qty = old_qty + quantity
            trader.avg_buy_prices[asset_id] = (
                (old_avg * old_qty + current_price * quantity) / new_qty
            )
            trader.portfolio[asset_id] = new_qty
            trader.balance -= quantity * current_price

        else:  # SELL
            held = trader.portfolio.get(asset_id, 0.0)
            if held < 1e-6:
                return None

            # Sell a fraction of the held quantity proportional to risk_level
            quantity = trader.strategy.risk_level * held
            avg_buy = trader.avg_buy_prices.get(asset_id, 0.0)
            pnl_realized = (current_price - avg_buy) * quantity
            trader.balance += quantity * current_price
            trader.pnl_personal += pnl_realized

            remaining = held - quantity
            if remaining < 1e-9:
                trader.portfolio.pop(asset_id, None)
                trader.avg_buy_prices.pop(asset_id, None)
            else:
                trader.portfolio[asset_id] = remaining

        trade = Trade(
            id=str(uuid.uuid4()),
            trader_id=trader.id,
            asset_id=asset_id,
            action=action,
            quantity=quantity,
            price=current_price,
            timestamp=state.current_tick,
            pnl_realized=pnl_realized,
        )
        trader.trade_history.append(trade)
        state.trade_log.append(trade)
        return trade

    def transition_phase(self, trader_id: str, new_phase: TraderPhase) -> None:
        """
        Changes the trader's phase and updates the strategy accordingly.

        The transition is recorded in phase_history with all details
        needed for the didactic display in the interface.

        Args:
            trader_id:  ProfessionalTrader id.
            new_phase:  new FSM phase.
        """
        trader = state.professional_traders[trader_id]
        old_phase = trader.phase

        # Explanatory notes for each transition (didactic use) — kept in Italian for UI display
        _transition_notes = {
            (TraderPhase.REPUTATION_BUILD, TraderPhase.FOLLOWER_GROWTH):
                "Soglia follower raggiunta. Il trader passa a raccogliere più capitale.",
            (TraderPhase.FOLLOWER_GROWTH, TraderPhase.MONETIZATION):
                "Soglia follower e capitale raggiunti. Attivazione fase di monetizzazione.",
            (TraderPhase.MONETIZATION, TraderPhase.REPUTATION_BUILD):
                "Reset del ciclo. Il trader riparte dalla costruzione della reputazione.",
        }
        note = _transition_notes.get(
            (old_phase, new_phase),
            f"Transizione manuale da {old_phase.value} a {new_phase.value}.",
        )

        # Transition log entry — data used by the didactic dashboard
        phase_entry = {
            "tick": state.current_tick,
            "from_phase": old_phase.value,
            "to_phase": new_phase.value,
            "followers_at_transition": len(trader.followers),
            "capital_exposed_at_transition": round(trader.follower_capital_exposed, 2),
            "note": note,
        }
        trader.phase_history.append(phase_entry)

        # Update phase and strategy
        trader.phase = new_phase
        trader.strategy = _DEFAULT_STRATEGY_BY_PHASE[new_phase]

    def update_follower_capital(self, trader_id: str) -> None:
        """
        Recalculates follower_capital_exposed by summing the portfolio value
        of all RetailTraders copying this professional.

        Must be called every tick by the orchestrator to keep the value
        used by the FSM for automatic transitions up to date.

        Args:
            trader_id: ProfessionalTrader id.
        """
        trader = state.professional_traders[trader_id]
        total = 0.0
        for retail_id in trader.followers:
            if retail_id in state.retail_traders:
                total += retail_engine.get_portfolio_value(retail_id)
        trader.follower_capital_exposed = total

    def get_summary(self, trader_id: str) -> dict:
        """
        Returns a summary dictionary for the professional trader.

        Returned fields:
            id, name, phase, followers_count, follower_capital_exposed,
            pnl_personal, bonus_earned, total_compensation,
            n_trades, last_phase_change_tick

        Args:
            trader_id: ProfessionalTrader id.

        Returns:
            dict with trader data.
        """
        trader = state.professional_traders[trader_id]
        last_tick = (
            trader.phase_history[-1]["tick"]
            if trader.phase_history else None
        )
        return {
            "id": trader.id,
            "name": trader.name,
            "phase": trader.phase.value,
            "followers_count": len(trader.followers),
            "follower_capital_exposed": round(trader.follower_capital_exposed, 2),
            "pnl_personal": round(trader.pnl_personal, 4),
            "bonus_earned": round(trader.bonus_earned, 4),
            "total_compensation": round(trader.pnl_personal + trader.bonus_earned, 4),
            "n_trades": len(trader.trade_history),
            "last_phase_change_tick": last_tick,
        }

    def create_default_professionals(self, n: int = 3) -> List[ProfessionalTrader]:
        """
        Creates N professional traders with random names, all in REPUTATION_BUILD phase.

        Args:
            n: number of traders to create.

        Returns:
            List of created ProfessionalTraders.
        """
        name_pool = list(_PRO_NAMES)
        random.shuffle(name_pool)
        traders = []
        for i in range(n):
            name = name_pool[i % len(name_pool)]
            if i >= len(name_pool):
                name = f"{name}_{i}"
            trader = self.create_professional_trader(name=name)
            traders.append(trader)
        return traders


# ── Global instance ────────────────────────────────────────────────────────
# Importable directly: from traders.professional import professional_engine
professional_engine = ProfessionalTraderEngine()
