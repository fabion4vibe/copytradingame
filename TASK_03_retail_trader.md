# TASK_03 — Retail Trader

**File di output**: `backend/traders/retail.py`
**Dipende da**: TASK_01, TASK_02
**Blocca**: TASK_05

---

## Obiettivo

Implementare il modulo `RetailTrader`: utenti che fanno trading manuale o tramite copy. Ogni retail ha un portafoglio, un bilancio, uno storico operazioni e una lista di trader professionisti copiati.

---

## Struttura Dati

### Dataclass `Trade`
*(condivisa tra retail e professionisti — definiscila qui, importata dagli altri)*

```python
@dataclass
class Trade:
    id: str                    # UUID generato
    trader_id: str
    asset_id: str
    action: str                # "BUY" | "SELL"
    quantity: float
    price: float               # prezzo al momento del trade
    timestamp: int             # tick corrente
    is_copy: bool = False
    copied_from: str = None    # professional_trader_id se is_copy=True
    pnl_realized: float = 0.0  # PnL realizzato (solo su SELL)
```

### Dataclass `RetailTrader`

```python
@dataclass
class RetailTrader:
    id: str
    name: str
    is_real_user: bool         # True solo per l'utente umano
    balance: float             # liquidità disponibile
    portfolio: Dict[str, float]        # asset_id → quantità posseduta
    avg_buy_prices: Dict[str, float]   # asset_id → prezzo medio di carico
    trade_history: List[Trade] = field(default_factory=list)
    copied_traders: List[str] = field(default_factory=list)  # professional_trader_id
    initial_balance: float = 10000.0   # per calcolo PnL totale
```

---

## Classe `RetailTraderEngine`

Gestisce le operazioni dei trader retail.

### Metodi da implementare

```python
def create_retail_trader(
    name: str,
    initial_balance: float = 10000.0,
    is_real_user: bool = False
) -> RetailTrader:
    """
    Crea un nuovo RetailTrader, lo aggiunge a state.retail_traders e lo restituisce.
    Genera un UUID come id.
    """

def execute_trade(
    trader_id: str,
    asset_id: str,
    action: str,           # "BUY" | "SELL"
    quantity: float
) -> Trade:
    """
    Esegue un'operazione manuale per un retail trader.
    
    BUY:
      - Verifica che trader.balance >= quantity * current_price
      - Aggiorna portfolio e avg_buy_prices
      - Scala il balance
      - Aggiunge il Trade a trade_history e state.trade_log
    
    SELL:
      - Verifica che portfolio[asset_id] >= quantity
      - Calcola pnl_realized = (current_price - avg_buy_price) * quantity
      - Aggiorna balance e portfolio
      - Aggiunge il Trade
    
    Lancia ValueError con messaggio descrittivo in caso di errore.
    """

def get_portfolio_value(trader_id: str) -> float:
    """
    Calcola il valore totale del portafoglio:
    balance + Σ(portfolio[asset_id] * current_price[asset_id])
    """

def get_total_pnl(trader_id: str) -> float:
    """
    PnL totale = portfolio_value_corrente - initial_balance
    """

def get_summary(trader_id: str) -> dict:
    """
    Restituisce un dizionario con:
    - id, name, balance, portfolio_value, total_pnl, n_trades, copied_traders
    """

def create_simulated_retailers(n: int = 10) -> List[RetailTrader]:
    """
    Crea N retail simulati con nomi casuali e bilancio casuale tra 5000 e 20000.
    Utili per popolare la simulazione senza utente reale.
    """
```

---

## Vincoli

- Il prezzo usato nei trade è sempre `state.assets[asset_id].current_price`.
- Non modificare `state.platform_pnl` da questo modulo. Lo fa il copy engine.
- `avg_buy_prices` va aggiornato con media ponderata su BUY multipli:
  ```
  new_avg = (old_avg * old_qty + price * new_qty) / (old_qty + new_qty)
  ```
- Su SELL completo (qty = tutto il posseduto), rimuovi la chiave da `portfolio` e `avg_buy_prices`.

---

## Criteri di Completamento

- [ ] Dataclass `Trade` con tutti i campi
- [ ] Dataclass `RetailTrader` con tutti i campi
- [ ] `create_retail_trader()` aggiunge a `state.retail_traders`
- [ ] `execute_trade()` BUY funzionante con verifica balance
- [ ] `execute_trade()` SELL funzionante con calcolo PnL
- [ ] `get_portfolio_value()` e `get_total_pnl()` corretti
- [ ] `create_simulated_retailers(n)` funzionante
- [ ] Docstring su tutto il pubblico
