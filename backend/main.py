"""
main.py
-------
Entry point dell'applicazione FastAPI — Trading Platform Simulator.

Configura CORS, monta tutti i router e inizializza lo stato al avvio.
Avviare con: uvicorn main:app --reload --port 8000
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
    Ripristina lo stato globale da un dizionario snapshot.

    Il formato del dizionario è quello prodotto da state.get_state_snapshot().
    Campi mancanti nello snapshot vengono ignorati (default invariato).

    Args:
        snapshot: dizionario snapshot prodotto da SimulationState.get_state_snapshot().
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

    # Ultimi 500 trade (il snapshot è già troncato, ma dal_dict è idempotente)
    state.trade_log = [Trade.from_dict(t) for t in snapshot.get("trade_log", [])]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestisce il ciclo di vita dell'applicazione.

    Tenta prima il ripristino da JSONBin (produzione su Render).
    Se non disponibile o fallisce, inizializza da zero (locale + primo avvio).
    """
    snapshot = SimulationState.load_from_remote()

    if snapshot:
        _restore_state_from_snapshot(snapshot)
    else:
        market_simulator.initialize_default_assets()
        professional_engine.create_default_professionals(3)
        retail_engine.create_simulated_retailers(10)

    yield
    # Shutdown: nessuna risorsa da liberare (stato in memoria)


app = FastAPI(
    title="Trading Platform Simulator",
    description=(
        "Piattaforma didattica locale che simula meccanismi di trading, "
        "copy trading e conflitti di interesse."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",          # sviluppo locale
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
    """Endpoint di health check. Restituisce lo stato dell'applicazione e il tick corrente."""
    return {"status": "ok", "tick": state.current_tick}
