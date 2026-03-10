"""
main.py
-------
FastAPI application entry point — Trading Platform Simulator.

Configures CORS, mounts all routers and initialises the state on startup.
Run with: uvicorn main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from market.router import router as market_router
from traders.router import retail_router, professional_router
from algorithm.router import router as algorithm_router
from manager.router import router as manager_router

from market.asset import Asset
from market.simulator import market_simulator
from traders.copy_engine import CopyRelation
from traders.professional import ProfessionalTrader, professional_engine
from traders.retail import RetailTrader, Trade, retail_engine
from state import SimulationState, state


def _restore_state_from_snapshot(snapshot: dict) -> None:
    """
    Restores the global state from a snapshot dictionary.

    The dictionary format is the one produced by state.get_state_snapshot().
    Fields missing from the snapshot are ignored (default value unchanged).

    Args:
        snapshot: snapshot dictionary produced by SimulationState.get_state_snapshot().
    """
    state.current_tick         = snapshot.get("current_tick", 0)
    state.platform_pnl         = snapshot.get("platform_pnl", 0.0)
    state.platform_commissions = snapshot.get("platform_commissions", 0.0)
    state.platform_bonus_paid  = snapshot.get("platform_bonus_paid", 0.0)

    for asset_id, asset_data in snapshot.get("assets", {}).items():
        state.assets[asset_id] = Asset.from_dict(asset_data)

    for trader_id, trader_data in snapshot.get("retail_traders", {}).items():
        state.retail_traders[trader_id] = RetailTrader.from_dict(trader_data)

    for trader_id, trader_data in snapshot.get("professional_traders", {}).items():
        state.professional_traders[trader_id] = ProfessionalTrader.from_dict(trader_data)

    state.copy_relations = [
        CopyRelation.from_dict(cr) for cr in snapshot.get("copy_relations", [])
    ]

    # Last 500 trades (snapshot is already truncated, but from_dict is idempotent)
    state.trade_log = [Trade.from_dict(t) for t in snapshot.get("trade_log", [])]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application lifecycle.

    First attempts to restore state from JSONBin (production on Render).
    If unavailable or failing, initialises from scratch (local + first boot).
    """
    snapshot = SimulationState.load_from_remote()

    if snapshot:
        _restore_state_from_snapshot(snapshot)
    else:
        market_simulator.initialize_default_assets()
        professional_engine.create_default_professionals(3)
        retail_engine.create_simulated_retailers(10)

    yield
    # Shutdown: no resources to release (state is in-memory)


app = FastAPI(
    title="Trading Platform Simulator",
    description=(
        "Local educational platform simulating trading mechanics, "
        "copy trading and conflicts of interest."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",          # local development
        "https://fabion4vibe.github.io",  # GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Router ─────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(market_router,       prefix=API_PREFIX)
app.include_router(retail_router,       prefix=API_PREFIX)
app.include_router(professional_router, prefix=API_PREFIX)
app.include_router(algorithm_router,    prefix=API_PREFIX)
app.include_router(manager_router,      prefix=API_PREFIX)


# ── Health check ───────────────────────────────────────────────────────────

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint. Returns application status and current tick."""
    return {"status": "ok", "tick": state.current_tick}
