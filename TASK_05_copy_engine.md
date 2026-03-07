# TASK_05 — Copy Engine

**File di output**: `backend/traders/copy_engine.py`
**Dipende da**: TASK_03 (RetailTrader), TASK_04 (ProfessionalTrader)
**Blocca**: TASK_06, TASK_07

---

## Obiettivo

Implementare il motore di copy trading: la propagazione delle operazioni del trader professionista a tutti i retail che lo stanno copiando. Questo modulo è il punto in cui le perdite della fase C vengono trasferite ai follower e il profitto della piattaforma viene aggiornato.

---

## Dataclass `CopyRelation`

*(definita in questo file, importata dagli altri)*

```python
@dataclass
class CopyRelation:
    retail_id: str
    professional_id: str
    allocation_pct: float    # % del portafoglio retail allocata (0.0–1.0)
    start_tick: int
    active: bool = True
```

---

## Classe `CopyEngine`

### Metodi da implementare

```python
def start_copy(
    retail_id: str,
    professional_id: str,
    allocation_pct: float = 0.5
) -> CopyRelation:
    """
    Avvia una relazione di copy trading.
    
    Validazioni:
    - Il retail esiste in state.retail_traders
    - Il professional esiste in state.professional_traders
    - Non esiste già una CopyRelation attiva tra questi due
    - allocation_pct in range (0.0, 1.0]
    
    Azioni:
    - Crea CopyRelation e la aggiunge a state.copy_relations
    - Aggiunge professional_id a retail.copied_traders
    - Aggiunge retail_id a professional.followers
    - Chiama professional_engine.update_follower_capital(professional_id)
    
    Lancia ValueError con messaggio descrittivo in caso di errore.
    """

def stop_copy(retail_id: str, professional_id: str) -> None:
    """
    Disattiva la relazione di copy.
    
    Azioni:
    - Imposta CopyRelation.active = False
    - Rimuove professional_id da retail.copied_traders
    - Rimuove retail_id da professional.followers
    - Aggiorna follower_capital del professional
    """

def propagate_trade(professional_trade: Trade) -> List[Trade]:
    """
    Replica il trade del professionista a tutti i retail follower attivi.
    
    Per ogni CopyRelation attiva con professional_id == trade.trader_id:
    
        capital_to_use = retail.balance * copy_relation.allocation_pct
        qty_to_copy = capital_to_use / current_price   (per BUY)
                    = retail.portfolio[asset_id] * allocation_pct  (per SELL)
        
        Se qty > 0:
            esegui il trade sul retail (chiama RetailTraderEngine.execute_trade)
            segna il trade come is_copy=True, copied_from=professional_id
    
    Aggiorna state.platform_pnl con le perdite nette dei retail:
        platform_gain += max(0, -retail_pnl_delta)
        # La piattaforma guadagna dalle perdite dei retail, non dai guadagni
    
    Restituisce lista di Trade eseguiti sui retail.
    """

def get_active_relations(professional_id: str = None) -> List[CopyRelation]:
    """
    Restituisce le CopyRelation attive.
    Se professional_id specificato, filtra per quel professionista.
    """

def get_copy_stats() -> dict:
    """
    Restituisce statistiche aggregate del copy trading:
    {
        "total_active_relations": int,
        "total_capital_in_copy": float,
        "by_professional": {
            professional_id: {
                "followers": int,
                "capital_exposed": float,
                "phase": str
            }
        }
    }
    """
```

---

## Meccanismo di Propagazione — Dettaglio

```
[Professional esegue BUY su SIM-A, qty=100, price=105]
    │
    ▼
propagate_trade(trade) chiamato
    │
    ├── CopyRelation(retail_id="R1", allocation_pct=0.3, active=True)
    │       capital_to_use = R1.balance * 0.3 = 3000
    │       qty_to_copy = 3000 / 105 = 28.57
    │       → execute_trade(R1, "SIM-A", "BUY", 28.57)
    │       → Trade registrato con is_copy=True
    │
    └── CopyRelation(retail_id="R2", allocation_pct=0.5, active=True)
            capital_to_use = R2.balance * 0.5 = 4000
            qty_to_copy = 4000 / 105 = 38.09
            → execute_trade(R2, "SIM-A", "BUY", 38.09)
```

---

## Aggiornamento PnL Piattaforma

```python
# Dopo ogni propagazione, calcola il delta PnL di ogni retail
# La piattaforma cattura le perdite nette aggregate

# NOTA DIDATTICA: questo è il meccanismo fondamentale
# La piattaforma guadagna quando i retail perdono.
# Quando il professional è in fase C (EV negativo), le perdite
# si propagano ai follower, e la piattaforma registra il guadagno.

delta_retail_pnl = portfolio_value_dopo - portfolio_value_prima
if delta_retail_pnl < 0:
    state.platform_pnl += abs(delta_retail_pnl)
```

---

## Vincoli

- Se un retail non ha abbastanza balance per copiare un BUY, il trade viene saltato silenziosamente (no eccezione, ma logga un `# INFO: trade copiato saltato per balance insufficiente`).
- Se un retail non ha la posizione per copiare un SELL, idem.
- Non modificare i trade già eseguiti dal professionista.

---

## Criteri di Completamento

- [ ] `CopyRelation` dataclass completa
- [ ] `start_copy()` con tutte le validazioni
- [ ] `stop_copy()` che aggiorna correttamente tutti i riferimenti
- [ ] `propagate_trade()` replica correttamente BUY e SELL
- [ ] `propagate_trade()` aggiorna `state.platform_pnl`
- [ ] Trade copiati marcati con `is_copy=True`
- [ ] Commento didattico sul meccanismo di PnL piattaforma
- [ ] Docstring su tutto il pubblico
