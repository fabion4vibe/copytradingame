# TASK_02 — Simulatore di Mercato

**File di output**: `backend/market/asset.py`, `backend/market/simulator.py`
**Dipende da**: TASK_01 (state.py)
**Blocca**: TASK_03, TASK_04

---

## Obiettivo

Implementare il simulatore di prezzi stocastico basato su **Geometric Brownian Motion (GBM)** semplificato. Il simulatore genera serie temporali di prezzi per N asset in memoria, avanzando di un tick per volta.

---

## File 1: `backend/market/asset.py`

### Classe `Asset`

```python
@dataclass
class Asset:
    id: str
    symbol: str           # es. "SIM-A"
    initial_price: float
    current_price: float
    volatility: float     # σ (sigma) — deviazione standard del rendimento per tick
    drift: float          # μ (mu) — rendimento atteso per tick (può essere negativo)
    price_history: List[float]  # serie storica, un valore per tick
```

**Metodi da implementare**:

```python
def to_dict(self) -> dict:
    """Serializza l'asset in dizionario JSON-compatibile."""

def current_return(self) -> float:
    """Rendimento percentuale dall'inizio della simulazione."""

def volatility_realized(self) -> float:
    """Volatilità realizzata (std dei rendimenti logaritmici storici).
    Restituisce 0.0 se meno di 2 tick disponibili."""
```

---

## File 2: `backend/market/simulator.py`

### Classe `MarketSimulator`

Gestisce tutti gli asset e avanza i prezzi tick per tick.

**Metodo di inizializzazione**:

```python
def initialize_default_assets(self) -> None:
    """
    Crea 5 asset simulati con parametri predefiniti e li inserisce in state.assets.
    
    Asset predefiniti:
    - SIM-A: prezzo 100, volatilità 0.02, drift 0.001   (stabile, lieve crescita)
    - SIM-B: prezzo 50,  volatilità 0.04, drift 0.000   (neutro, alta vol)
    - SIM-C: prezzo 200, volatilità 0.01, drift 0.002   (crescita costante)
    - SIM-D: prezzo 75,  volatilità 0.05, drift -0.001  (volatile, lieve calo)
    - SIM-E: prezzo 30,  volatilità 0.03, drift 0.000   (neutro)
    """
```

**Metodo di avanzamento tick**:

```python
def step(self, n_ticks: int = 1) -> None:
    """
    Avanza la simulazione di n_ticks.
    
    Per ogni tick e per ogni asset, applica GBM discreto:
    
        P(t+1) = P(t) * exp((μ - σ²/2) * dt + σ * √dt * Z)
    
    dove:
        dt = 1 (un'unità di tempo per tick)
        Z  ~ N(0, 1) (variabile casuale normale standard)
    
    Aggiorna:
    - asset.current_price
    - asset.price_history (append del nuovo prezzo)
    - state.current_tick += n_ticks
    """
```

**Altri metodi**:

```python
def get_price(self, asset_id: str) -> float:
    """Restituisce il prezzo corrente di un asset."""

def get_history(self, asset_id: str, last_n: int = None) -> List[float]:
    """Restituisce la serie storica. Se last_n specificato, solo gli ultimi N valori."""

def add_asset(self, asset: Asset) -> None:
    """Aggiunge un asset alla simulazione e a state.assets."""
```

---

## Modello Matematico (GBM Discreto)

```
P(t+1) = P(t) * exp( (μ - σ²/2) * Δt  +  σ * √Δt * Z )

dove:
  μ     = drift (rendimento atteso per unità di tempo)
  σ     = volatilità (deviazione standard)
  Δt    = 1 (tick unitario)
  Z     ~ N(0,1)
```

Usa `numpy.random.normal(0, 1)` per generare Z. Importa `numpy as np`.

---

## Vincoli

- I prezzi non possono diventare negativi (il GBM lo garantisce matematicamente, ma aggiungere un `max(price, 0.01)` per sicurezza).
- Non alterare `state.current_tick` da nessun'altra parte: solo `MarketSimulator.step()` lo fa.
- `price_history[0]` è sempre `initial_price`.

---

## Criteri di Completamento

- [ ] Classe `Asset` con tutti i campi e metodi
- [ ] `MarketSimulator.initialize_default_assets()` crea 5 asset in `state.assets`
- [ ] `MarketSimulator.step(n)` applica GBM correttamente
- [ ] I prezzi rimangono positivi
- [ ] `get_history()` funziona con e senza `last_n`
- [ ] Docstring su tutto il pubblico
