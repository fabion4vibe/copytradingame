"""
schemas.py
----------
Modelli Pydantic per tutti i body di input delle API REST.

Importato da tutti i router. Non contiene logica di dominio.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class TickRequest(BaseModel):
    """Body per POST /market/tick."""
    n_ticks: int = Field(default=1, ge=1, description="Numero di tick da avanzare.")


class TradeRequest(BaseModel):
    """Body per POST /retail/traders/{id}/trade."""
    asset_id: str
    action: Literal["BUY", "SELL"]
    quantity: float = Field(gt=0)


class CreateRetailRequest(BaseModel):
    """Body per POST /retail/traders."""
    name: str
    initial_balance: float = Field(default=10000.0, gt=0)
    is_real_user: bool = False


class CopyRequest(BaseModel):
    """Body per POST /retail/traders/{id}/copy."""
    professional_id: str
    allocation_pct: float = Field(default=0.5, gt=0.0, le=1.0)


class PhaseChangeRequest(BaseModel):
    """Body per PATCH /professional/traders/{id}/phase."""
    new_phase: Literal["REPUTATION_BUILD", "FOLLOWER_GROWTH", "MONETIZATION"]


class UpdateStrategyRequest(BaseModel):
    """Body per PATCH /professional/traders/{id}/strategy. Tutti i campi opzionali."""
    expected_value: Optional[float] = None
    risk_level: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    trade_frequency: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    min_followers_for_B: Optional[int] = Field(default=None, ge=0)
    min_followers_for_C: Optional[int] = Field(default=None, ge=0)
    target_capital_exposed: Optional[float] = Field(default=None, ge=0.0)
    bonus_per_tick_in_C: Optional[float] = Field(default=None, ge=0.0)


class ScenarioRequest(BaseModel):
    """Body per POST /algorithm/simulate-scenario."""
    trader_id: str
    scenario: Literal["TRANSITION_TO_MONETIZATION", "MAINTAIN_CURRENT_PHASE"]
    n_ticks: int = Field(default=10, ge=1)
