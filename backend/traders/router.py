"""
traders/router.py
-----------------
Router FastAPI per gli endpoint /api/v1/retail e /api/v1/professional.

Contiene due APIRouter distinti (retail_router e professional_router)
montati in main.py con i prefix corretti. Nessuna logica di dominio.
"""

from fastapi import APIRouter, HTTPException
from dataclasses import asdict

from traders.retail import retail_engine
from traders.professional import professional_engine, TraderPhase, StrategyProfile
from traders.copy_engine import copy_engine
from state import state
from schemas import (
    TradeRequest,
    CreateRetailRequest,
    CopyRequest,
    PhaseChangeRequest,
    UpdateStrategyRequest,
)

# ── Router Retail (/api/v1/retail) ─────────────────────────────────────────

retail_router = APIRouter(prefix="/retail", tags=["retail"])


def _trade_to_dict(trade) -> dict:
    """Serializza un Trade in dict JSON-compatibile."""
    return {
        "id": trade.id,
        "trader_id": trade.trader_id,
        "asset_id": trade.asset_id,
        "action": trade.action,
        "quantity": trade.quantity,
        "price": trade.price,
        "timestamp": trade.timestamp,
        "is_copy": trade.is_copy,
        "copied_from": trade.copied_from,
        "pnl_realized": trade.pnl_realized,
    }


def _copy_relation_to_dict(rel) -> dict:
    """Serializza una CopyRelation in dict JSON-compatibile."""
    return {
        "retail_id": rel.retail_id,
        "professional_id": rel.professional_id,
        "allocation_pct": rel.allocation_pct,
        "start_tick": rel.start_tick,
        "active": rel.active,
    }


@retail_router.get("/traders")
async def list_retail_traders():
    """Restituisce il riepilogo di tutti i trader retail."""
    return [
        retail_engine.get_summary(trader_id)
        for trader_id in state.retail_traders
    ]


@retail_router.get("/traders/{trader_id}")
async def get_retail_trader(trader_id: str):
    """Restituisce il dettaglio completo di un trader retail."""
    if trader_id not in state.retail_traders:
        raise HTTPException(status_code=404, detail=f"Retail trader '{trader_id}' non trovato.")
    trader = state.retail_traders[trader_id]
    summary = retail_engine.get_summary(trader_id)
    return {
        **summary,
        "portfolio": dict(trader.portfolio),
        "avg_buy_prices": dict(trader.avg_buy_prices),
        "is_real_user": trader.is_real_user,
    }


@retail_router.post("/traders", status_code=201)
async def create_retail_trader(body: CreateRetailRequest):
    """Crea un nuovo trader retail e lo aggiunge alla simulazione."""
    trader = retail_engine.create_retail_trader(
        name=body.name,
        initial_balance=body.initial_balance,
        is_real_user=body.is_real_user,
    )
    return retail_engine.get_summary(trader.id)


@retail_router.post("/traders/{trader_id}/trade")
async def execute_trade(trader_id: str, body: TradeRequest):
    """Esegue un'operazione manuale (BUY o SELL) per un trader retail."""
    if trader_id not in state.retail_traders:
        raise HTTPException(status_code=404, detail=f"Retail trader '{trader_id}' non trovato.")
    try:
        trade = retail_engine.execute_trade(
            trader_id=trader_id,
            asset_id=body.asset_id,
            action=body.action,
            quantity=body.quantity,
        )
        return _trade_to_dict(trade)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Asset '{body.asset_id}' non trovato.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@retail_router.post("/traders/{trader_id}/copy", status_code=201)
async def start_copy(trader_id: str, body: CopyRequest):
    """Avvia una relazione di copy trading verso un professionista."""
    try:
        relation = copy_engine.start_copy(
            retail_id=trader_id,
            professional_id=body.professional_id,
            allocation_pct=body.allocation_pct,
        )
        return _copy_relation_to_dict(relation)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@retail_router.delete("/traders/{trader_id}/copy/{professional_id}")
async def stop_copy(trader_id: str, professional_id: str):
    """Disattiva la relazione di copy trading tra retail e professionista."""
    try:
        copy_engine.stop_copy(retail_id=trader_id, professional_id=professional_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@retail_router.get("/traders/{trader_id}/history")
async def get_trade_history(trader_id: str):
    """Restituisce lo storico delle operazioni di un trader retail."""
    if trader_id not in state.retail_traders:
        raise HTTPException(status_code=404, detail=f"Retail trader '{trader_id}' non trovato.")
    trader = state.retail_traders[trader_id]
    return [_trade_to_dict(t) for t in trader.trade_history]


@retail_router.get("/traders/{trader_id}/pnl")
async def get_retail_pnl(trader_id: str):
    """Restituisce il PnL e il valore corrente del portafoglio del trader."""
    if trader_id not in state.retail_traders:
        raise HTTPException(status_code=404, detail=f"Retail trader '{trader_id}' non trovato.")
    return {
        "pnl": round(retail_engine.get_total_pnl(trader_id), 4),
        "portfolio_value": round(retail_engine.get_portfolio_value(trader_id), 4),
    }


# ── Router Professional (/api/v1/professional) ─────────────────────────────

professional_router = APIRouter(prefix="/professional", tags=["professional"])


def _strategy_to_dict(strategy) -> dict:
    """Serializza uno StrategyProfile in dict JSON-compatibile."""
    return {
        "expected_value": strategy.expected_value,
        "risk_level": strategy.risk_level,
        "trade_frequency": strategy.trade_frequency,
        "min_followers_for_B": strategy.min_followers_for_B,
        "min_followers_for_C": strategy.min_followers_for_C,
        "target_capital_exposed": strategy.target_capital_exposed,
        "bonus_per_tick_in_C": strategy.bonus_per_tick_in_C,
    }


@professional_router.get("/traders")
async def list_professional_traders():
    """Restituisce il riepilogo di tutti i trader professionisti."""
    return [
        professional_engine.get_summary(trader_id)
        for trader_id in state.professional_traders
    ]


@professional_router.get("/traders/{trader_id}")
async def get_professional_trader(trader_id: str):
    """Restituisce il dettaglio completo di un trader professionista."""
    if trader_id not in state.professional_traders:
        raise HTTPException(status_code=404, detail=f"Professional trader '{trader_id}' non trovato.")
    trader = state.professional_traders[trader_id]
    summary = professional_engine.get_summary(trader_id)
    return {
        **summary,
        "strategy": _strategy_to_dict(trader.strategy),
        "followers": list(trader.followers),
        "last_phase_change_tick": (
            trader.phase_history[-1]["tick"] if trader.phase_history else None
        ),
    }


@professional_router.patch("/traders/{trader_id}/phase")
async def change_phase(trader_id: str, body: PhaseChangeRequest):
    """Cambia la fase FSM di un trader professionista."""
    if trader_id not in state.professional_traders:
        raise HTTPException(status_code=404, detail=f"Professional trader '{trader_id}' non trovato.")
    try:
        new_phase = TraderPhase(body.new_phase)
        professional_engine.transition_phase(trader_id, new_phase)
        return professional_engine.get_summary(trader_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@professional_router.patch("/traders/{trader_id}/strategy")
async def update_strategy(trader_id: str, body: UpdateStrategyRequest):
    """Aggiorna il profilo strategico di un trader professionista (campi opzionali)."""
    if trader_id not in state.professional_traders:
        raise HTTPException(status_code=404, detail=f"Professional trader '{trader_id}' non trovato.")
    trader = state.professional_traders[trader_id]
    s = trader.strategy
    # Aggiorna solo i campi forniti nel body
    updates = body.model_dump(exclude_none=True)
    for field_name, value in updates.items():
        setattr(s, field_name, value)
    return _strategy_to_dict(s)


@professional_router.get("/traders/{trader_id}/history")
async def get_professional_trade_history(trader_id: str):
    """Restituisce lo storico delle operazioni di un trader professionista."""
    if trader_id not in state.professional_traders:
        raise HTTPException(status_code=404, detail=f"Professional trader '{trader_id}' non trovato.")
    trader = state.professional_traders[trader_id]
    return [_trade_to_dict(t) for t in trader.trade_history]


@professional_router.get("/traders/{trader_id}/phase-history")
async def get_phase_history(trader_id: str):
    """Restituisce il log dei cambi di fase di un trader professionista."""
    if trader_id not in state.professional_traders:
        raise HTTPException(status_code=404, detail=f"Professional trader '{trader_id}' non trovato.")
    return state.professional_traders[trader_id].phase_history
