"""
algorithm/router.py
-------------------
Router FastAPI per gli endpoint /api/v1/algorithm.

Nessuna logica di dominio: chiama scorer e recommender e restituisce i risultati.
"""

from fastapi import APIRouter, HTTPException

from algorithm.scorer import trader_scorer
from algorithm.recommender import strategy_recommender
from schemas import ScenarioRequest

router = APIRouter(prefix="/algorithm", tags=["algorithm"])


@router.get("/recommendations")
async def get_recommendations():
    """Restituisce le raccomandazioni strategiche ordinate per priorità."""
    return strategy_recommender.get_recommendations()


@router.get("/rankings")
async def get_rankings():
    """Restituisce il ranking dei trader professionisti per score di monetizzazione."""
    return trader_scorer.rank_all_traders()


@router.post("/simulate-scenario")
async def simulate_scenario(body: ScenarioRequest):
    """Stima l'effetto di uno scenario su N tick futuri (modello statistico)."""
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
