# TASK_07 — API Routers + main.py

**File di output**: `backend/main.py`, `backend/market/router.py`, `backend/traders/router.py`, `backend/algorithm/router.py`, `backend/manager/router.py`
**Dipende da**: TASK_02, TASK_03, TASK_04, TASK_05, TASK_06
**Blocca**: TASK_08, TASK_09

---

## Obiettivo

Creare tutti gli endpoint REST che espongono la logica dei moduli al frontend. Il contratto formale è in `openapi.yaml`. Questo task implementa solo i router: nessuna logica di dominio qui.

---

## Regola Fondamentale

I router **non contengono logica di dominio**. Chiamano i moduli e restituiscono i risultati. Struttura tipo:

```python
@router.post("/traders/{trader_id}/trade")
async def execute_trade(trader_id: str, body: TradeRequest):
    try:
        trade = retail_engine.execute_trade(trader_id, body.asset_id, body.action, body.quantity)
        return trade_to_dict(trade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## `backend/main.py`

```python
# Entry point FastAPI
# Deve:
# 1. Creare l'app FastAPI con titolo "Trading Platform Simulator"
# 2. Configurare CORS per permettere richieste da localhost:5173
# 3. Montare tutti i router con i prefix corretti
# 4. Definire un endpoint GET /health che restituisce {"status": "ok", "tick": current_tick}
# 5. All'avvio (lifespan o startup event): inizializzare lo stato con dati di default
#    - market.initialize_default_assets()
#    - create_default_professionals(3)
#    - create_simulated_retailers(10)
```

---

## Router: `/api/v1/market`

| Metodo | Path | Handler | Risposta |
|--------|------|---------|----------|
| GET | `/assets` | Lista tutti gli asset | `List[AssetDict]` |
| GET | `/assets/{asset_id}` | Dettaglio asset | `AssetDict` |
| GET | `/assets/{asset_id}/history` | Serie storica | `{"history": [float], "ticks": int}` |
| POST | `/tick` | Avanza N tick | `{"tick": int, "prices": dict}` |
| GET | `/status` | Stato simulazione | `{"tick": int, "n_assets": int, "running": bool}` |

**Body POST /tick**:
```json
{ "n_ticks": 1 }
```

---

## Router: `/api/v1/retail`

| Metodo | Path | Handler | Risposta |
|--------|------|---------|----------|
| GET | `/traders` | Lista retail | `List[RetailSummary]` |
| GET | `/traders/{id}` | Dettaglio retail | `RetailDetail` |
| POST | `/traders` | Crea nuovo retail | `RetailSummary` |
| POST | `/traders/{id}/trade` | Esegui trade | `TradeDict` |
| POST | `/traders/{id}/copy` | Avvia copy | `CopyRelationDict` |
| DELETE | `/traders/{id}/copy/{pro_id}` | Ferma copy | `{"success": true}` |
| GET | `/traders/{id}/history` | Storico trade | `List[TradeDict]` |
| GET | `/traders/{id}/pnl` | PnL corrente | `{"pnl": float, "portfolio_value": float}` |

**Body POST /traders**:
```json
{ "name": "string", "initial_balance": 10000.0, "is_real_user": false }
```

**Body POST /traders/{id}/trade**:
```json
{ "asset_id": "string", "action": "BUY|SELL", "quantity": 10.0 }
```

**Body POST /traders/{id}/copy**:
```json
{ "professional_id": "string", "allocation_pct": 0.5 }
```

---

## Router: `/api/v1/professional`

| Metodo | Path | Handler | Risposta |
|--------|------|---------|----------|
| GET | `/traders` | Lista professionisti | `List[ProfessionalSummary]` |
| GET | `/traders/{id}` | Dettaglio + fase + follower | `ProfessionalDetail` |
| PATCH | `/traders/{id}/phase` | Cambia fase | `ProfessionalSummary` |
| PATCH | `/traders/{id}/strategy` | Aggiorna strategia | `StrategyDict` |
| GET | `/traders/{id}/history` | Storico trade | `List[TradeDict]` |
| GET | `/traders/{id}/phase-history` | Log cambi fase | `List[PhaseHistoryEntry]` |

**Body PATCH /phase**:
```json
{ "new_phase": "REPUTATION_BUILD|FOLLOWER_GROWTH|MONETIZATION" }
```

---

## Router: `/api/v1/algorithm`

| Metodo | Path | Handler | Risposta |
|--------|------|---------|----------|
| GET | `/recommendations` | Lista raccomandazioni | `List[Recommendation]` |
| GET | `/rankings` | Ranking trader per score | `List[TraderRanking]` |
| POST | `/simulate-scenario` | Stima scenario | `ScenarioResult` |

**Body POST /simulate-scenario**:
```json
{ "trader_id": "string", "scenario": "TRANSITION_TO_MONETIZATION", "n_ticks": 10 }
```

---

## Router: `/api/v1/manager`

| Metodo | Path | Handler | Risposta |
|--------|------|---------|----------|
| GET | `/overview` | KPI globali | `PlatformOverview` |
| GET | `/pnl` | Dettaglio PnL piattaforma | `PlatformPnL` |
| GET | `/copy-stats` | Statistiche copy trading | `CopyStats` |
| POST | `/reset` | Reimposta simulazione | `{"success": true}` |

---

## Modelli Pydantic di Input/Output

Definisci in `backend/schemas.py` (file separato, importato da tutti i router):

```python
# Input
class TickRequest(BaseModel):
    n_ticks: int = 1

class TradeRequest(BaseModel):
    asset_id: str
    action: Literal["BUY", "SELL"]
    quantity: float

class CreateRetailRequest(BaseModel):
    name: str
    initial_balance: float = 10000.0
    is_real_user: bool = False

class CopyRequest(BaseModel):
    professional_id: str
    allocation_pct: float = 0.5

class PhaseChangeRequest(BaseModel):
    new_phase: Literal["REPUTATION_BUILD", "FOLLOWER_GROWTH", "MONETIZATION"]

class ScenarioRequest(BaseModel):
    trader_id: str
    scenario: str
    n_ticks: int = 10
```

---

## Criteri di Completamento

- [ ] `main.py` con CORS, router montati, startup event
- [ ] Tutti gli endpoint di `/market` implementati
- [ ] Tutti gli endpoint di `/retail` implementati
- [ ] Tutti gli endpoint di `/professional` implementati
- [ ] Tutti gli endpoint di `/algorithm` implementati
- [ ] Tutti gli endpoint di `/manager` implementati
- [ ] `schemas.py` con tutti i modelli Pydantic
- [ ] Errori restituiti come `HTTPException` con status code appropriato (400, 404)
- [ ] Nessuna logica di dominio nei router
