"""
manager/router.py
-----------------
Router FastAPI per gli endpoint /api/v1/manager (dashboard gestore).

Nessuna logica di dominio: aggrega dati da recommender, copy_engine e state.
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
    """Restituisce i KPI globali della piattaforma (PlatformOverview)."""
    return strategy_recommender.get_platform_health_report()


@router.get("/pnl")
async def get_platform_pnl():
    """
    Restituisce il dettaglio del PnL della piattaforma.

    Il campo 'history' è vuoto: la piattaforma non traccia lo storico tick per tick.
    Sarà popolato dall'orchestratore (TASK_08) quando disponibile.
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
        "history": [],  # TODO: popolato dall'orchestratore in TASK_08
    }


@router.get("/copy-stats")
async def get_copy_stats():
    """Restituisce le statistiche aggregate del copy trading."""
    return copy_engine.get_copy_stats()


@router.post("/reset")
async def reset_simulation():
    """
    Reimposta la simulazione ai valori iniziali e ri-inizializza i dati di default.

    Dopo il reset:
    - tick = 0, platform_pnl = 0
    - 5 asset di mercato ricreati
    - 3 trader professionisti in fase A
    - 10 trader retail simulati
    """
    reset_state()
    market_simulator.initialize_default_assets()
    professional_engine.create_default_professionals(3)
    retail_engine.create_simulated_retailers(10)
    return {"success": True}
