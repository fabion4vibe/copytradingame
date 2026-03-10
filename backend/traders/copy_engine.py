"""
copy_engine.py
--------------
Implements the copy trading engine: propagates the professional trader's operations
to all active retail followers.

This is the module where phase C losses are transferred to followers
and the platform profit is updated.

DIDACTIC NOTE — Central conflict-of-interest mechanism:
    The platform profits from the net losses of retail traders.
    When a professional is in phase C (negative EV), their operations are
    replicated to followers via propagate_trade(). Each net loss suffered by
    a retail trader translates into a platform gain recorded in state.platform_pnl.
    The professional receives a separate bonus (see professional.py).
    The platform profits on both fronts.

Typical usage:
    from traders.copy_engine import copy_engine, CopyRelation
    relation = copy_engine.start_copy(retail_id, professional_id, allocation_pct=0.4)
    copy_trades = copy_engine.propagate_trade(professional_trade)
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

from state import state
from traders.retail import Trade, retail_engine
from traders.professional import professional_engine

logger = logging.getLogger(__name__)


# ── CopyRelation dataclass ─────────────────────────────────────────────────

@dataclass
class CopyRelation:
    """
    Represents a copy trading relationship between a retail and a professional trader.

    Fields:
        retail_id:       id of the follower RetailTrader
        professional_id: id of the copied ProfessionalTrader
        allocation_pct:  fraction of the retail portfolio allocated to copy (0.0–1.0]
        start_tick:      tick at which the relationship was activated
        active:          False if the relationship was deactivated with stop_copy()
    """

    retail_id: str
    professional_id: str
    allocation_pct: float
    start_tick: int
    active: bool = True

    def to_dict(self) -> dict:
        """Serializes the copy trading relationship to a JSON-compatible dictionary."""
        return {
            "retail_id": self.retail_id,
            "professional_id": self.professional_id,
            "allocation_pct": self.allocation_pct,
            "start_tick": self.start_tick,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CopyRelation":
        """Reconstructs a CopyRelation from a snapshot dictionary."""
        return cls(
            retail_id=data["retail_id"],
            professional_id=data["professional_id"],
            allocation_pct=data["allocation_pct"],
            start_tick=data["start_tick"],
            active=data.get("active", True),
        )


# ── Engine ─────────────────────────────────────────────────────────────────

class CopyEngine:
    """
    Manages copy trading relationships and trade propagation.

    It is the only module authorised to update state.platform_pnl with
    the net losses of retail followers.
    """

    def start_copy(
        self,
        retail_id: str,
        professional_id: str,
        allocation_pct: float = 0.5,
    ) -> CopyRelation:
        """
        Starts a copy trading relationship between a retail and a professional trader.

        Validations:
        - The retail trader exists in state.retail_traders
        - The professional exists in state.professional_traders
        - No active CopyRelation already exists between these two
        - allocation_pct is in range (0.0, 1.0]

        Actions:
        - Creates CopyRelation and appends it to state.copy_relations
        - Adds professional_id to retail.copied_traders
        - Adds retail_id to professional.followers
        - Updates the professional's follower_capital_exposed

        Args:
            retail_id:       id of the RetailTrader who wants to copy.
            professional_id: id of the ProfessionalTrader to copy.
            allocation_pct:  fraction of retail balance to allocate (default 0.5).

        Returns:
            The newly created CopyRelation.

        Raises:
            ValueError: if any validation fails, with a descriptive message.
        """
        if retail_id not in state.retail_traders:
            raise ValueError(f"Retail trader '{retail_id}' non trovato.")
        if professional_id not in state.professional_traders:
            raise ValueError(f"Professional trader '{professional_id}' non trovato.")
        if not (0.0 < allocation_pct <= 1.0):
            raise ValueError(
                f"allocation_pct deve essere in (0.0, 1.0], ricevuto {allocation_pct}."
            )

        # Controlla relazione attiva già esistente
        for rel in state.copy_relations:
            if (rel.retail_id == retail_id
                    and rel.professional_id == professional_id
                    and rel.active):
                raise ValueError(
                    f"Esiste già una relazione attiva tra retail '{retail_id}' "
                    f"e professional '{professional_id}'."
                )

        relation = CopyRelation(
            retail_id=retail_id,
            professional_id=professional_id,
            allocation_pct=allocation_pct,
            start_tick=state.current_tick,
        )
        state.copy_relations.append(relation)

        retail = state.retail_traders[retail_id]
        if professional_id not in retail.copied_traders:
            retail.copied_traders.append(professional_id)

        professional = state.professional_traders[professional_id]
        if retail_id not in professional.followers:
            professional.followers.append(retail_id)

        professional_engine.update_follower_capital(professional_id)
        return relation

    def stop_copy(self, retail_id: str, professional_id: str) -> None:
        """
        Deactivates the copy trading relationship between a retail and a professional.

        Actions:
        - Sets CopyRelation.active = False
        - Removes professional_id from retail.copied_traders
        - Removes retail_id from professional.followers
        - Updates the professional's follower_capital_exposed

        Args:
            retail_id:       RetailTrader id.
            professional_id: ProfessionalTrader id.

        Raises:
            ValueError: if no active relationship exists between the two.
        """
        found = False
        for rel in state.copy_relations:
            if (rel.retail_id == retail_id
                    and rel.professional_id == professional_id
                    and rel.active):
                rel.active = False
                found = True
                break

        if not found:
            raise ValueError(
                f"Nessuna relazione attiva trovata tra retail '{retail_id}' "
                f"e professional '{professional_id}'."
            )

        retail = state.retail_traders.get(retail_id)
        if retail and professional_id in retail.copied_traders:
            retail.copied_traders.remove(professional_id)

        professional = state.professional_traders.get(professional_id)
        if professional and retail_id in professional.followers:
            professional.followers.remove(retail_id)
            professional_engine.update_follower_capital(professional_id)

    def propagate_trade(self, professional_trade: Trade) -> List[Trade]:
        """
        Replicates the professional's trade to all active retail followers.

        For each active CopyRelation with professional_id == trade.trader_id:

            BUY:  qty_to_copy = (retail.balance * allocation_pct) / current_price
            SELL: qty_to_copy = retail.portfolio.get(asset_id, 0) * allocation_pct

        If qty <= 0 or the trade fails due to insufficient balance/portfolio,
        the trade is silently skipped.

        state.platform_pnl update (central didactic mechanism):
            After each copied trade, the retail's PnL delta is computed.
            If negative (the retail lost), the platform records the gain:
                state.platform_pnl += abs(delta_pnl)
            The platform does not record gains when the retail profits.

        Args:
            professional_trade: the Trade executed by the professional to replicate.

        Returns:
            List of Trades executed on retail followers.
        """
        professional_id = professional_trade.trader_id
        asset_id = professional_trade.asset_id
        action = professional_trade.action
        current_price = state.assets[asset_id].current_price

        copy_trades: List[Trade] = []

        for rel in state.copy_relations:
            if rel.professional_id != professional_id or not rel.active:
                continue

            retail_id = rel.retail_id
            if retail_id not in state.retail_traders:
                continue

            retail = state.retail_traders[retail_id]

            # Calcola quantità da copiare in base all'azione
            if action == "BUY":
                capital_to_use = retail.balance * rel.allocation_pct
                qty = capital_to_use / current_price if current_price > 0 else 0.0
            else:  # SELL
                held = retail.portfolio.get(asset_id, 0.0)
                qty = held * rel.allocation_pct

            if qty <= 1e-9:
                logger.info(
                    "INFO: copied trade skipped — zero quantity — "
                    "retail=%s, asset=%s, action=%s",
                    retail_id, asset_id, action,
                )
                continue

            # Portfolio value snapshot before the trade
            pv_before = retail_engine.get_portfolio_value(retail_id)

            try:
                trade = retail_engine.execute_trade(
                    trader_id=retail_id,
                    asset_id=asset_id,
                    action=action,
                    quantity=qty,
                    is_copy=True,
                    copied_from=professional_id,
                )
                copy_trades.append(trade)
            except ValueError:
                # Insufficient balance or portfolio: skip silently
                logger.info(
                    "INFO: copied trade skipped — insufficient balance — "
                    "retail=%s, asset=%s, action=%s, qty=%.4f",
                    retail_id, asset_id, action, qty,
                )
                continue

            # platform_pnl update — the platform profits from retail losses
            # DIDACTIC NOTE: this is the conflict-of-interest mechanism.
            # Every time a follower loses, the platform records an equivalent gain.
            # In phase C, the professional intentionally generates losses for followers,
            # and the platform collects on both fronts:
            # from retail losses (here) and from the professional's bonus (in professional.py).
            pv_after = retail_engine.get_portfolio_value(retail_id)
            delta_pnl = pv_after - pv_before
            if delta_pnl < 0:
                state.platform_pnl += abs(delta_pnl)

        return copy_trades

    def get_active_relations(
        self, professional_id: Optional[str] = None
    ) -> List[CopyRelation]:
        """
        Returns active CopyRelations, optionally filtered by professional.

        Args:
            professional_id: if specified, filters for that professional.
                             If None, returns all active relationships.

        Returns:
            List of active CopyRelations.
        """
        return [
            rel for rel in state.copy_relations
            if rel.active and (
                professional_id is None or rel.professional_id == professional_id
            )
        ]

    def get_copy_stats(self) -> dict:
        """
        Returns aggregate copy trading statistics.

        Returns:
            dict with:
            - total_active_relations: total number of active relationships
            - total_capital_in_copy:  total retail capital committed to copy
            - by_professional:        for each professional with active followers:
                                      followers, capital_exposed, phase
        """
        active = self.get_active_relations()
        total_capital = 0.0
        by_professional: dict = {}

        for rel in active:
            retail = state.retail_traders.get(rel.retail_id)
            pro = state.professional_traders.get(rel.professional_id)
            if retail is None or pro is None:
                continue

            capital = retail_engine.get_portfolio_value(rel.retail_id) * rel.allocation_pct
            total_capital += capital

            if rel.professional_id not in by_professional:
                by_professional[rel.professional_id] = {
                    "followers": 0,
                    "capital_exposed": 0.0,
                    "phase": pro.phase.value,
                }
            by_professional[rel.professional_id]["followers"] += 1
            by_professional[rel.professional_id]["capital_exposed"] += capital

        # Round capital_exposed for readability
        for stats in by_professional.values():
            stats["capital_exposed"] = round(stats["capital_exposed"], 2)

        return {
            "total_active_relations": len(active),
            "total_capital_in_copy": round(total_capital, 2),
            "by_professional": by_professional,
        }


# ── Global instance ────────────────────────────────────────────────────────
# Importable directly: from traders.copy_engine import copy_engine
copy_engine = CopyEngine()
