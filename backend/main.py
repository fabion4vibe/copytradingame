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

from market.simulator import market_simulator
from traders.professional import professional_engine
from traders.retail import retail_engine
from state import state


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestisce il ciclo di vita dell'applicazione.

    All'avvio inizializza la simulazione con dati di default:
    - 5 asset di mercato (SIM-A … SIM-E)
    - 3 trader professionisti in fase REPUTATION_BUILD
    - 10 trader retail simulati con bilanci casuali
    """
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
    allow_origins=["http://localhost:5173"],
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
