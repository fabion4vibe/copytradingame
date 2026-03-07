# TASK_04 — Professional Trader + FSM

**File di output**: `backend/traders/professional.py`
**Dipende da**: TASK_01, TASK_02
**Blocca**: TASK_05, TASK_06

---

## Obiettivo

Implementare il modulo `ProfessionalTrader` con la **macchina a stati finiti (FSM)** che controlla il comportamento del trader nelle tre fasi del ciclo di vita. Questo è il nucleo didattico del progetto: mostrare come un trader apparentemente indipendente sia in realtà controllato dalla piattaforma.

---

## Struttura Dati

### Enum `TraderPhase`

```python
from enum import Enum

class TraderPhase(str, Enum):
    REPUTATION_BUILD = "REPUTATION_BUILD"   # Fase A: costruzione reputazione
    FOLLOWER_GROWTH  = "FOLLOWER_GROWTH"    # Fase B: attrazione follower
    MONETIZATION     = "MONETIZATION"       # Fase C: estrazione valore
```

### Dataclass `StrategyProfile`

Parametri che definiscono il comportamento del trader per fase.

```python
@dataclass
class StrategyProfile:
    # Parametri operativi
    expected_value: float        # EV atteso per trade (pos. in A/B, neg. in C)
    risk_level: float            # 0.0–1.0: influenza volatilità delle operazioni
    trade_frequency: float       # probabilità di eseguire un trade per tick (0.0–1.0)

    # Soglie transizione automatica (usate dal motore algoritmico)
    min_followers_for_B: int     # follower minimi per passare ad A→B
    min_followers_for_C: int     # follower minimi per passare a B→C
    target_capital_exposed: float  # capitale retail esposto target per attivare C

    # Compensazione
    bonus_per_tick_in_C: float   # bonus ricevuto dal professionista per ogni tick in fase C
```

### Dataclass `ProfessionalTrader`

```python
@dataclass
class ProfessionalTrader:
    id: str
    name: str
    phase: TraderPhase
    strategy: StrategyProfile

    # Stato economico
    balance: float
    portfolio: Dict[str, float]
    avg_buy_prices: Dict[str, float]
    pnl_personal: float = 0.0       # PnL da trading effettivo
    bonus_earned: float = 0.0       # bonus accumulati dalla piattaforma

    # Follower
    followers: List[str] = field(default_factory=list)  # retail_trader_id
    follower_capital_exposed: float = 0.0  # capitale retail totale esposto su di lui

    # Storico
    trade_history: List[Any] = field(default_factory=list)  # importa Trade da retail.py
    phase_history: List[dict] = field(default_factory=list) # log dei cambi di fase

    initial_balance: float = 50000.0
```

---

## Classe `ProfessionalTraderEngine`

### Metodi da implementare

```python
def create_professional_trader(
    name: str,
    initial_phase: TraderPhase = TraderPhase.REPUTATION_BUILD,
    strategy: StrategyProfile = None   # se None, usa profilo default per fase A
) -> ProfessionalTrader:
    """
    Crea un nuovo ProfessionalTrader, lo aggiunge a state.professional_traders.
    Se strategy è None, usa DEFAULT_STRATEGY_A (vedi sotto).
    """

def execute_strategy(trader_id: str) -> Optional[Trade]:
    """
    Esegue la strategia del professionista per il tick corrente.

    Logica:
    1. Estrai random() < strategy.trade_frequency → se False, non fare nulla
    2. Scegli un asset casuale tra quelli in state.assets
    3. Calcola l'azione in base alla fase:
       - REPUTATION_BUILD / FOLLOWER_GROWTH:
           Sceglie BUY/SELL con probabilità che favorisce EV positivo
           (es. compra su asset con drift positivo, vende su negativo)
       - MONETIZATION:
           Sceglie azioni con EV negativo (es. compra asset volatile in calo)
           Aumenta la frequenza e la dimensione delle posizioni
    4. Esegui il trade (chiama logica analoga a RetailTraderEngine.execute_trade)
    5. Se fase MONETIZATION, accumula strategy.bonus_per_tick_in_C in bonus_earned
    6. Aggiorna state.platform_pnl del bonus (la piattaforma "paga" il bonus)

    Restituisce il Trade eseguito o None se nessun trade questo tick.
    """

def transition_phase(trader_id: str, new_phase: TraderPhase) -> None:
    """
    Cambia la fase del trader e aggiorna la strategy di conseguenza.
    Registra il cambio in phase_history con tick corrente e fase precedente.

    Profili strategia per fase:
    - REPUTATION_BUILD → DEFAULT_STRATEGY_A
    - FOLLOWER_GROWTH  → DEFAULT_STRATEGY_B
    - MONETIZATION     → DEFAULT_STRATEGY_C
    """

def update_follower_capital(trader_id: str) -> None:
    """
    Ricalcola follower_capital_exposed sommando il portfolio_value
    di tutti i RetailTrader che copiano questo professionista.
    """

def get_summary(trader_id: str) -> dict:
    """
    Restituisce: id, name, phase, followers_count, follower_capital_exposed,
    pnl_personal, bonus_earned, total_compensation (pnl + bonus),
    n_trades, last_phase_change_tick
    """

def create_default_professionals(n: int = 3) -> List[ProfessionalTrader]:
    """
    Crea N trader professionisti con nomi casuali, tutti in fase REPUTATION_BUILD.
    """
```

---

## Profili Strategia Predefiniti

```python
DEFAULT_STRATEGY_A = StrategyProfile(
    expected_value=+0.015,      # EV positivo: in media +1.5% per trade
    risk_level=0.2,
    trade_frequency=0.4,        # 40% di probabilità di tradare per tick
    min_followers_for_B=5,
    min_followers_for_C=15,
    target_capital_exposed=50000.0,
    bonus_per_tick_in_C=0.0     # nessun bonus in fase A
)

DEFAULT_STRATEGY_B = StrategyProfile(
    expected_value=+0.008,      # EV ancora positivo, ma più conservativo
    risk_level=0.3,
    trade_frequency=0.6,
    min_followers_for_B=5,
    min_followers_for_C=15,
    target_capital_exposed=50000.0,
    bonus_per_tick_in_C=0.0
)

DEFAULT_STRATEGY_C = StrategyProfile(
    expected_value=-0.020,      # EV negativo: in media -2% per trade
    risk_level=0.7,
    trade_frequency=0.8,        # alta frequenza per massimizzare il danno
    min_followers_for_B=5,
    min_followers_for_C=15,
    target_capital_exposed=50000.0,
    bonus_per_tick_in_C=200.0   # bonus fisso per tick in fase C
)
```

---

## Nota Didattica (Non Omettere)

Ogni transizione di fase deve essere loggata in `phase_history` con un commento esplicativo:

```python
# Esempio di entry in phase_history
{
    "tick": 42,
    "from_phase": "FOLLOWER_GROWTH",
    "to_phase": "MONETIZATION",
    "followers_at_transition": 18,
    "capital_exposed_at_transition": 62000.0,
    "note": "Soglia follower e capitale raggiunti. Attivazione fase di monetizzazione."
}
```

---

## Criteri di Completamento

- [ ] `TraderPhase` enum con 3 valori
- [ ] `StrategyProfile` con tutti i campi
- [ ] `ProfessionalTrader` con tutti i campi
- [ ] 3 profili strategia predefiniti (A, B, C)
- [ ] `execute_strategy()` genera trade coerenti con la fase
- [ ] `transition_phase()` aggiorna strategia e logga in `phase_history`
- [ ] `update_follower_capital()` corretto
- [ ] `create_default_professionals(3)` funzionante
- [ ] Nota didattica nel log delle transizioni
- [ ] Docstring su tutto il pubblico
