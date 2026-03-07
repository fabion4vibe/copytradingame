# TASK_08 — Orchestratore Tick

**File di output**: `backend/orchestrator.py`
**Dipende da**: TASK_07 (tutti i moduli e router funzionanti)
**Blocca**: nessuno (ultimo modulo backend)

---

## Obiettivo

Implementare l'orchestratore che coordina l'avanzamento della simulazione per ogni tick. Gestisce sia l'avanzamento **manuale** (chiamato dall'endpoint POST /market/tick) sia l'avanzamento **automatico** (loop in background opzionale).

---

## Classe `TickOrchestrator`

```python
class TickOrchestrator:
    """
    Coordina l'esecuzione di un tick completo della simulazione.
    
    Ordine di esecuzione per ogni tick:
    1. market.step(1)                          → aggiorna prezzi
    2. Per ogni professional_trader:
         professional_engine.execute_strategy()  → genera trade
         Se trade eseguito:
             copy_engine.propagate_trade(trade)   → propaga ai follower
    3. Per ogni professional_trader:
         professional_engine.update_follower_capital()  → ricalcola esposizione
    4. algorithm_engine.update_scores()          → aggiorna ranking interni
    5. [opzionale] state.snapshot()              → salva JSON se abilitato
    """
```

### Metodi da implementare

```python
def run_tick(self) -> dict:
    """
    Esegue un singolo tick completo seguendo l'ordine sopra.
    
    Restituisce un tick summary:
    {
        "tick": int,
        "prices": {asset_id: current_price},
        "trades_executed": int,          # trade totali (professionisti + copie)
        "platform_pnl_delta": float,     # variazione PnL piattaforma in questo tick
        "professionals_summary": [
            {"id": str, "phase": str, "trade_executed": bool}
        ]
    }
    """

def run_n_ticks(self, n: int) -> List[dict]:
    """
    Esegue N tick consecutivi.
    Restituisce lista di tick summary (uno per tick).
    """

def start_auto_tick(self, interval_seconds: float = 2.0) -> None:
    """
    Avvia un loop in background (threading.Thread o asyncio.Task) 
    che esegue run_tick() ogni interval_seconds.
    
    Se già in esecuzione, non ne avvia un secondo.
    """

def stop_auto_tick(self) -> None:
    """
    Ferma il loop automatico.
    """

def is_auto_running(self) -> bool:
    """Restituisce True se il loop automatico è attivo."""

def get_tick_log(self, last_n: int = 10) -> List[dict]:
    """
    Restituisce i summary degli ultimi N tick eseguiti.
    Il log è mantenuto in memoria (lista circolare, max 1000 tick).
    """
```

---

## Integrazione con l'API

Il router `/market` deve usare l'orchestratore per POST /tick:

```python
# In backend/market/router.py (aggiornamento post TASK_07)

@router.post("/tick")
async def advance_tick(body: TickRequest):
    summaries = orchestrator.run_n_ticks(body.n_ticks)
    return {
        "tick": state.current_tick,
        "summaries": summaries
    }
```

---

## Snapshot JSON (Opzionale)

Se la variabile d'ambiente `SAVE_SNAPSHOTS=true` è impostata, dopo ogni tick salva lo stato in `data/snapshot_{tick}.json`.

Usa `state.get_state_snapshot()` (definita in TASK_01).

---

## Vincoli

- L'auto-tick non deve interferire con le chiamate manuali all'API (usare lock se necessario).
- Se un professional non ha abbastanza balance per eseguire il suo trade, la strategia viene saltata silenziosamente.
- Il tick log non cresce indefinitamente: max 1000 entry (deque con maxlen).

---

## Criteri di Completamento

- [ ] `run_tick()` esegue i 4 step nell'ordine corretto
- [ ] `run_n_ticks(n)` restituisce lista di summary
- [ ] `start_auto_tick()` e `stop_auto_tick()` funzionanti
- [ ] `get_tick_log()` con deque a dimensione fissa
- [ ] Integrazione con router `/market/tick`
- [ ] Nessuna race condition su auto-tick vs manual tick
- [ ] Docstring su tutto il pubblico
