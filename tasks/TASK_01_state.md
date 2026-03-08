# TASK_01 — Stato Globale In-Memory

**File di output**: `backend/state.py`
**Dipende da**: nessuno
**Blocca**: tutti gli altri task backend

---

## Obiettivo

Creare il modulo `state.py` che funge da **singola fonte di verità** per l'intera simulazione. Tutti i moduli backend importano da questo file per leggere e scrivere lo stato condiviso. Non esiste database.

---

## Struttura da Implementare

```python
# backend/state.py

from typing import Dict, List
from dataclasses import dataclass, field

# Importerà i tipi dagli altri moduli una volta creati.
# Per ora usa dizionari tipizzati generici (Dict[str, Any]).
# I task successivi sostituiranno i tipi Any con le classi specifiche.
```

Lo stato globale deve essere un **singleton** — un'unica istanza condivisa, accessibile via import.

### Campi dello stato

```python
@dataclass
class SimulationState:
    # Mercato
    current_tick: int = 0
    assets: Dict[str, Any] = field(default_factory=dict)         # asset_id → Asset

    # Trader
    retail_traders: Dict[str, Any] = field(default_factory=dict)       # id → RetailTrader
    professional_traders: Dict[str, Any] = field(default_factory=dict) # id → ProfessionalTrader

    # Copy trading
    copy_relations: List[Any] = field(default_factory=list)      # lista CopyRelation

    # Economia piattaforma
    platform_pnl: float = 0.0          # profitto cumulativo piattaforma
    platform_commissions: float = 0.0  # commissioni accumulate
    platform_bonus_paid: float = 0.0   # bonus pagati ai professionisti

    # Storico
    trade_log: List[Any] = field(default_factory=list)           # tutti i trade eseguiti

# Istanza globale
state = SimulationState()
```

---

## Funzioni Helper da Implementare

```python
def reset_state() -> None:
    """Reimposta lo stato globale ai valori iniziali. Utile per restart della simulazione."""

def get_state_snapshot() -> dict:
    """Restituisce uno snapshot serializzabile dello stato corrente (per debug/export JSON)."""
```

---

## Vincoli

- **Nessun import da altri moduli del progetto** in questo file (evitare dipendenze circolari).
- Usare `Any` come tipo placeholder per le entità non ancora definite. I task successivi aggiorneranno i type hint.
- Il singleton `state` deve essere importabile direttamente: `from state import state`

---

## Esempio di Utilizzo Atteso (da altri moduli)

```python
from state import state

state.current_tick += 1
state.assets["SIM-A"] = my_asset
state.platform_pnl += 150.0
```

---

## Criteri di Completamento

- [ ] `SimulationState` dataclass con tutti i campi
- [ ] Singleton `state` istanziato a livello di modulo
- [ ] `reset_state()` implementata
- [ ] `get_state_snapshot()` implementata e restituisce dict serializzabile
- [ ] Nessuna dipendenza circolare
- [ ] Docstring su ogni classe e funzione pubblica
