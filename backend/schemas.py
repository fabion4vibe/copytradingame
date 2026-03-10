"""
schemas.py
----------
Pydantic models for all REST API input bodies.

Imported by all routers. Contains no domain logic.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class TickRequest(BaseModel):
    """Request body for POST /market/tick."""
    n_ticks: int = Field(default=1, ge=1, description="Number of ticks to advance.")


class TradeRequest(BaseModel):
    """Request body for POST /retail/traders/{id}/trade."""
    asset_id: str
    action: Literal["BUY", "SELL"]
    quantity: float = Field(gt=0)


class CreateRetailRequest(BaseModel):
    """Request body for POST /retail/traders."""
    name: str
    initial_balance: float = Field(default=10000.0, gt=0)
    is_real_user: bool = False


class CopyRequest(BaseModel):
    """Request body for POST /retail/traders/{id}/copy."""
    professional_id: str
    allocation_pct: float = Field(default=0.5, gt=0.0, le=1.0)


class PhaseChangeRequest(BaseModel):
    """Request body for PATCH /professional/traders/{id}/phase."""
    new_phase: Literal["REPUTATION_BUILD", "FOLLOWER_GROWTH", "MONETIZATION"]


class UpdateStrategyRequest(BaseModel):
    """Request body for PATCH /professional/traders/{id}/strategy. All fields optional."""
    expected_value: Optional[float] = None
    risk_level: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    trade_frequency: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    min_followers_for_B: Optional[int] = Field(default=None, ge=0)
    min_followers_for_C: Optional[int] = Field(default=None, ge=0)
    target_capital_exposed: Optional[float] = Field(default=None, ge=0.0)
    bonus_per_tick_in_C: Optional[float] = Field(default=None, ge=0.0)


class ScenarioRequest(BaseModel):
    """Request body for POST /algorithm/simulate-scenario."""
    trader_id: str
    scenario: Literal["TRANSITION_TO_MONETIZATION", "MAINTAIN_CURRENT_PHASE"]
    n_ticks: int = Field(default=10, ge=1)
