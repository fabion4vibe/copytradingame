"""
manager/router.py
-----------------
FastAPI router for the /api/v1/manager endpoints (manager dashboard).

No domain logic: aggregates data from recommender, copy_engine and state.
"""

from fastapi import APIRouter

from algorithm.recommender import strategy_recommender
from traders.copy_engine import copy_engine
from market.simulator import market_simulator
from traders.professional import professional_engine
from traders.retail import retail_engine
from state import state, reset_state

router = APIRouter(prefix="/manager", tags=["manager"])


@router.get("/overview")
async def get_overview():
    """Returns the global platform KPIs (PlatformOverview)."""
    return strategy_recommender.get_platform_health_report()


@router.get("/pnl")
async def get_platform_pnl():
    """
    Returns the detailed platform PnL breakdown.

    The 'history' field is empty: the platform does not track tick-by-tick history.
    It will be populated by the orchestrator (TASK_08) when available.
    """
    net = round(
        state.platform_pnl + state.platform_commissions - state.platform_bonus_paid,
        2,
    )
    return {
        "pnl": round(state.platform_pnl, 2),
        "commissions": round(state.platform_commissions, 2),
        "bonus_paid": round(state.platform_bonus_paid, 2),
        "net": net,
        "history": [],  # TODO: populated by the orchestrator in TASK_08
    }


@router.get("/copy-stats")
async def get_copy_stats():
    """Returns aggregate copy trading statistics."""
    return copy_engine.get_copy_stats()


@router.post("/reset")
async def reset_simulation():
    """
    Resets the simulation to its initial values and reinitialises default data.

    After reset:
    - tick = 0, platform_pnl = 0
    - 5 market assets recreated
    - 3 professional traders in phase A
    - 10 simulated retail traders
    """
    reset_state()
    market_simulator.initialize_default_assets()
    professional_engine.create_default_professionals(3)
    retail_engine.create_simulated_retailers(10)
    return {"success": True}
