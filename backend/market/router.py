"""
market/router.py
----------------
FastAPI router for the /api/v1/market endpoints.

No domain logic: calls market_simulator and returns the results.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query

from market.simulator import market_simulator
from state import state
from schemas import TickRequest
from orchestrator import orchestrator

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/assets")
async def list_assets():
    """Returns all assets with their current prices."""
    return [asset.to_dict() for asset in state.assets.values()]


@router.get("/assets/{asset_id}")
async def get_asset(asset_id: str):
    """Returns the detail of a single asset."""
    if asset_id not in state.assets:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' non trovato.")
    return state.assets[asset_id].to_dict()


@router.get("/assets/{asset_id}/history")
async def get_asset_history(
    asset_id: str,
    last_n: Optional[int] = Query(default=None, ge=1),
):
    """Returns the price history of an asset."""
    if asset_id not in state.assets:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' non trovato.")
    history = market_simulator.get_history(asset_id, last_n)
    return {"history": history, "ticks": len(history)}


@router.post("/tick")
async def advance_tick(body: TickRequest):
    """
    Executes N complete ticks via the orchestrator.

    Each tick includes: price update, professional strategies,
    copy trade propagation and follower exposure recalculation.
    """
    summaries = orchestrator.run_n_ticks(body.n_ticks)
    return {"tick": state.current_tick, "summaries": summaries}


@router.get("/status")
async def get_market_status():
    """Returns the current state of the market simulation."""
    return {
        "tick": state.current_tick,
        "n_assets": len(state.assets),
        "running": True,
    }
