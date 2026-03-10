"""
algorithm/router.py
-------------------
FastAPI router for the /api/v1/algorithm endpoints.

No domain logic: delegates to scorer and recommender and returns the results.
"""

from fastapi import APIRouter, HTTPException

from algorithm.scorer import trader_scorer
from algorithm.recommender import strategy_recommender
from schemas import ScenarioRequest

router = APIRouter(prefix="/algorithm", tags=["algorithm"])


@router.get("/recommendations")
async def get_recommendations():
    """Returns strategic recommendations sorted by priority."""
    return strategy_recommender.get_recommendations()


@router.get("/rankings")
async def get_rankings():
    """Returns the professional trader ranking by monetisation score."""
    return trader_scorer.rank_all_traders()


@router.post("/simulate-scenario")
async def simulate_scenario(body: ScenarioRequest):
    """Estimates the effect of a scenario over N future ticks (statistical model)."""
    try:
        return strategy_recommender.simulate_scenario(
            trader_id=body.trader_id,
            scenario=body.scenario,
            n_ticks=body.n_ticks,
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Trader '{body.trader_id}' non trovato.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
