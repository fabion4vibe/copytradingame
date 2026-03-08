"""
market/router.py
----------------
Router FastAPI per gli endpoint /api/v1/market.

Nessuna logica di dominio: chiama market_simulator e restituisce i risultati.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from market.simulator import market_simulator
from state import state
from schemas import TickRequest

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/assets")
async def list_assets():
    """Restituisce tutti gli asset con i prezzi correnti."""
    return [asset.to_dict() for asset in state.assets.values()]


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str):
    """Restituisce il dettaglio di un singolo asset."""
    if asset_id not in state.assets:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' non trovato.")
    return state.assets[asset_id].to_dict()


@router.get("/assets/{asset_id}/history")
async def get_asset_history(
    asset_id: str,
    last_n: Optional[int] = Query(default=None, ge=1),
):
    """Restituisce la serie storica dei prezzi di un asset."""
    if asset_id not in state.assets:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' non trovato.")
    history = market_simulator.get_history(asset_id, last_n)
    return {"history": history, "ticks": len(history)}


@router.post("/tick")
async def advance_tick(body: TickRequest):
    """
    Avanza la simulazione di mercato di N tick.

    Restituisce un TickSummary per ogni tick eseguito con prezzi aggiornati.
    trades_executed e platform_pnl_delta sono 0 finché l'orchestratore
    (TASK_08) non gestisce il tick completo.
    """
    summaries = []
    for _ in range(body.n_ticks):
        pnl_before = state.platform_pnl
        market_simulator.step(1)
        summaries.append({
            "tick": state.current_tick,
            "prices": {
                asset_id: asset.current_price
                for asset_id, asset in state.assets.items()
            },
            "trades_executed": 0,
            "platform_pnl_delta": round(state.platform_pnl - pnl_before, 4),
        })
    return {"tick": state.current_tick, "summaries": summaries}


@router.get("/status")
async def get_market_status():
    """Restituisce lo stato corrente della simulazione di mercato."""
    return {
        "tick": state.current_tick,
        "n_assets": len(state.assets),
        "running": True,
    }
