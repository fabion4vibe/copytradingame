# TASK_06 — Motore Algoritmico di Controllo

**File di output**: `backend/algorithm/scorer.py`, `backend/algorithm/recommender.py`
**Dipende da**: TASK_03, TASK_04, TASK_05
**Blocca**: TASK_07

---

## Obiettivo

Implementare il motore che analizza lo stato della simulazione e produce **raccomandazioni strategiche** per il gestore. Il motore non agisce autonomamente: fornisce supporto decisionale. Il gestore può accettare o ignorare i suggerimenti.

---

## File 1: `backend/algorithm/scorer.py`

### Classe `TraderScorer`

Calcola uno score per ogni trader professionista che rappresenta la **priorità di transizione alla fase C** (monetizzazione).

```python
def compute_score(trader_id: str, weights: dict = None) -> float:
    """
    Calcola lo score di monetizzazione per un trader professionista.
    
    Formula:
        score = w1 * norm_followers
              + w2 * norm_capital_exposed
              + w3 * (1 - norm_pnl_personal)   # più il trader ha perso, meno è utile tenerlo in A/B
              + w4 * phase_urgency
    
    Dove:
        norm_* = normalizzazione [0,1] rispetto al massimo tra tutti i professionisti
        
        phase_urgency:
            REPUTATION_BUILD → 0.0
            FOLLOWER_GROWTH  → 0.5
            MONETIZATION     → 1.0  (già in C, score alto ma non azionabile)
    
    Pesi di default:
        w1 = 0.35  (follower count)
        w2 = 0.35  (capitale esposto)
        w3 = 0.15  (performance)
        w4 = 0.15  (urgenza di fase)
    
    Se weights è fornito, usa quelli (stesso formato dict).
    """

def rank_all_traders(weights: dict = None) -> List[dict]:
    """
    Calcola e ordina tutti i trader per score decrescente.
    
    Restituisce lista di:
    {
        "trader_id": str,
        "name": str,
        "phase": str,
        "score": float,
        "followers": int,
        "capital_exposed": float,
        "pnl_personal": float
    }
    """

def check_transition_conditions(trader_id: str) -> dict:
    """
    Verifica se le condizioni di transizione automatica sono soddisfatte.
    
    Restituisce:
    {
        "can_transition_to_B": bool,
        "can_transition_to_C": bool,
        "followers_needed_for_B": int,   # quanti ne mancano (0 se già ok)
        "followers_needed_for_C": int,
        "capital_needed_for_C": float,
        "current_phase": str
    }
    """
```

---

## File 2: `backend/algorithm/recommender.py`

### Classe `StrategyRecommender`

Genera raccomandazioni complete per il gestore.

```python
def get_recommendations(weights: dict = None) -> List[dict]:
    """
    Analizza tutti i trader e produce una lista di raccomandazioni ordinate per priorità.
    
    Una raccomandazione ha questa struttura:
    {
        "trader_id": str,
        "trader_name": str,
        "current_phase": str,
        "suggested_action": str,       # vedi azioni possibili sotto
        "reason": str,                 # spiegazione leggibile
        "expected_platform_gain": float,
        "risk_level": str,             # "LOW" | "MEDIUM" | "HIGH"
        "confidence": float,           # 0.0–1.0
        "score": float
    }
    
    Azioni possibili:
    - "MAINTAIN_CURRENT_PHASE"
    - "TRANSITION_TO_FOLLOWER_GROWTH"
    - "TRANSITION_TO_MONETIZATION"
    - "INCREASE_TRADE_FREQUENCY"
    - "REDUCE_RISK_LEVEL"
    - "AWAIT_MORE_FOLLOWERS"
    """

def simulate_scenario(trader_id: str, scenario: str, n_ticks: int = 10) -> dict:
    """
    Stima l'effetto di un'azione su N tick futuri (simulazione statistica, non determinististica).
    
    Scenari supportati:
    - "TRANSITION_TO_MONETIZATION": stima perdita attesa retail e guadagno piattaforma
    - "MAINTAIN_CURRENT_PHASE": stima evoluzione con strategia corrente
    
    Usa il modello:
        expected_retail_loss = follower_capital * |EV_C| * trade_frequency * n_ticks
        expected_platform_gain = expected_retail_loss - bonus_paid
    
    Restituisce:
    {
        "scenario": str,
        "trader_id": str,
        "n_ticks": int,
        "expected_retail_loss": float,
        "expected_bonus_paid": float,
        "expected_platform_net_gain": float,
        "confidence_interval": [float, float]   # ±1σ
    }
    """

def get_platform_health_report() -> dict:
    """
    Panoramica sintetica dello stato della piattaforma.
    
    Restituisce:
    {
        "current_tick": int,
        "platform_pnl": float,
        "platform_commissions": float,
        "platform_bonus_paid": float,
        "platform_net": float,                  # pnl + commissions - bonus
        "total_retail_capital": float,
        "total_capital_in_copy": float,
        "copy_penetration_pct": float,          # % capitale retail in copy
        "n_professionals_in_monetization": int,
        "n_retail_losing": int,                 # retail con PnL totale negativo
        "avg_retail_pnl": float
    }
    """
```

---

## Note di Implementazione

- Tutti i calcoli sono su dati già presenti in `state`. Non eseguire trade reali.
- `expected_platform_gain` nelle raccomandazioni è sempre una stima, non un dato reale. Marcalo chiaramente nella docstring.
- Il `confidence` di una raccomandazione è più alto quando: il trader ha molti follower, il capitale esposto è alto, la fase B è avanzata.

---

## Criteri di Completamento

- [ ] `compute_score()` con formula corretta e pesi configurabili
- [ ] `rank_all_traders()` ordinato per score decrescente
- [ ] `check_transition_conditions()` corretto per ogni trader
- [ ] `get_recommendations()` con almeno 2 tipi di azione distinte
- [ ] `simulate_scenario()` per MONETIZATION e MAINTAIN
- [ ] `get_platform_health_report()` con tutti i campi
- [ ] Docstring su tutto il pubblico
