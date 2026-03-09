"""
retail.py
---------
Implementa il modulo RetailTrader: utenti che fanno trading manuale o tramite copy.

La dataclass Trade è definita qui ed è condivisa con professional.py.

Uso tipico:
    from traders.retail import RetailTraderEngine, Trade
    engine = RetailTraderEngine()
    trader = engine.create_retail_trader("Alice")
    trade  = engine.execute_trade(trader.id, "sim-a", "BUY", 5.0)
"""

import random
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from state import state


# ── Nomi casuali per i trader simulati ────────────────────────────────────
_SIMULATED_NAMES = [
    "Alice", "Bruno", "Carla", "Davide", "Elena",
    "Fabio", "Giulia", "Hamid", "Irene", "Luca",
    "Marco", "Nadia", "Omar", "Paola", "Quin",
    "Rosa", "Stefano", "Tina", "Ugo", "Vera",
]


# ── Dataclass Trade (condivisa tra retail e professionisti) ────────────────

@dataclass
class Trade:
    """
    Rappresenta una singola operazione di acquisto o vendita eseguita da un trader.

    Campi:
        id            — UUID univoco del trade
        trader_id     — id del trader che ha eseguito l'operazione
        asset_id      — id dell'asset scambiato
        action        — "BUY" o "SELL"
        quantity      — quantità scambiata
        price         — prezzo al momento del trade
        timestamp     — tick della simulazione in cui è avvenuto il trade
        is_copy       — True se il trade è stato generato dal copy engine
        copied_from   — professional_trader_id sorgente, se is_copy=True
        pnl_realized  — PnL realizzato (valorizzato solo su SELL)
    """

    id: str
    trader_id: str
    asset_id: str
    action: str                   # "BUY" | "SELL"
    quantity: float
    price: float
    timestamp: int
    is_copy: bool = False
    copied_from: Optional[str] = None
    pnl_realized: float = 0.0

    def to_dict(self) -> dict:
        """Serializza il trade in un dizionario JSON-compatibile."""
        return {
            "id": self.id,
            "trader_id": self.trader_id,
            "asset_id": self.asset_id,
            "action": self.action,
            "quantity": self.quantity,
            "price": self.price,
            "timestamp": self.timestamp,
            "is_copy": self.is_copy,
            "copied_from": self.copied_from,
            "pnl_realized": self.pnl_realized,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Trade":
        """Ricostruisce un Trade da un dizionario snapshot."""
        return cls(
            id=data["id"],
            trader_id=data["trader_id"],
            asset_id=data["asset_id"],
            action=data["action"],
            quantity=data["quantity"],
            price=data["price"],
            timestamp=data["timestamp"],
            is_copy=data.get("is_copy", False),
            copied_from=data.get("copied_from"),
            pnl_realized=data.get("pnl_realized", 0.0),
        )


# ── Dataclass RetailTrader ─────────────────────────────────────────────────

@dataclass
class RetailTrader:
    """
    Rappresenta un trader retail: utente che opera manualmente o tramite copy.

    Campi:
        id              — UUID univoco
        name            — nome visualizzato
        is_real_user    — True solo per l'utente umano che usa la dashboard
        balance         — liquidità disponibile (diminuisce su BUY, aumenta su SELL)
        portfolio       — asset_id → quantità posseduta
        avg_buy_prices  — asset_id → prezzo medio di carico (media ponderata)
        trade_history   — lista di Trade eseguiti da questo trader
        copied_traders  — lista di professional_trader_id copiati
        initial_balance — bilancio iniziale, usato per calcolare il PnL totale
    """

    id: str
    name: str
    is_real_user: bool
    balance: float
    portfolio: Dict[str, float] = field(default_factory=dict)
    avg_buy_prices: Dict[str, float] = field(default_factory=dict)
    trade_history: List[Trade] = field(default_factory=list)
    copied_traders: List[str] = field(default_factory=list)
    initial_balance: float = 10000.0

    def to_dict(self) -> dict:
        """Serializza il retail trader in un dizionario JSON-compatibile."""
        return {
            "id": self.id,
            "name": self.name,
            "is_real_user": self.is_real_user,
            "balance": self.balance,
            "portfolio": dict(self.portfolio),
            "avg_buy_prices": dict(self.avg_buy_prices),
            "trade_history": [t.to_dict() for t in self.trade_history],
            "copied_traders": list(self.copied_traders),
            "initial_balance": self.initial_balance,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RetailTrader":
        """Ricostruisce un RetailTrader da un dizionario snapshot."""
        trader = cls(
            id=data["id"],
            name=data["name"],
            is_real_user=data["is_real_user"],
            balance=data["balance"],
            portfolio=data.get("portfolio", {}),
            avg_buy_prices=data.get("avg_buy_prices", {}),
            copied_traders=data.get("copied_traders", []),
            initial_balance=data.get("initial_balance", 10000.0),
        )
        trader.trade_history = [Trade.from_dict(t) for t in data.get("trade_history", [])]
        return trader


# ── Engine ─────────────────────────────────────────────────────────────────

class RetailTraderEngine:
    """
    Gestisce le operazioni dei trader retail: creazione, esecuzione trade e calcoli.

    Non modifica state.platform_pnl — quella responsabilità appartiene al copy engine.
    """

    def create_retail_trader(
        self,
        name: str,
        initial_balance: float = 10000.0,
        is_real_user: bool = False,
    ) -> RetailTrader:
        """
        Crea un nuovo RetailTrader, lo aggiunge a state.retail_traders e lo restituisce.

        Args:
            name:            nome del trader.
            initial_balance: bilancio iniziale in valuta simulata.
            is_real_user:    True se corrisponde all'utente umano della dashboard.

        Returns:
            Il RetailTrader appena creato.
        """
        trader = RetailTrader(
            id=str(uuid.uuid4()),
            name=name,
            is_real_user=is_real_user,
            balance=initial_balance,
            initial_balance=initial_balance,
        )
        state.retail_traders[trader.id] = trader
        return trader

    def execute_trade(
        self,
        trader_id: str,
        asset_id: str,
        action: str,
        quantity: float,
        is_copy: bool = False,
        copied_from: Optional[str] = None,
    ) -> Trade:
        """
        Esegue un'operazione di acquisto o vendita per un retail trader.

        BUY:
            - Verifica che trader.balance >= quantity * current_price
            - Aggiorna portfolio e avg_buy_prices (media ponderata)
            - Scala il balance del costo totale
            - Registra il Trade in trade_history e state.trade_log

        SELL:
            - Verifica che portfolio[asset_id] >= quantity
            - Calcola pnl_realized = (current_price - avg_buy_price) * quantity
            - Aggiorna balance e portfolio
            - Rimuove la chiave da portfolio/avg_buy_prices se vendita completa
            - Registra il Trade in trade_history e state.trade_log

        Args:
            trader_id:   id del RetailTrader.
            asset_id:    id dell'asset da scambiare.
            action:      "BUY" o "SELL".
            quantity:    quantità dell'asset.
            is_copy:     True se generato dal copy engine.
            copied_from: professional_trader_id sorgente (se is_copy=True).

        Returns:
            Il Trade appena eseguito.

        Raises:
            KeyError:   se trader_id o asset_id non esistono.
            ValueError: se il balance è insufficiente (BUY) o il portafoglio è
                        insufficiente (SELL), con messaggio descrittivo.
        """
        trader = state.retail_traders[trader_id]
        current_price = state.assets[asset_id].current_price
        pnl_realized = 0.0

        if action == "BUY":
            cost = quantity * current_price
            if trader.balance < cost:
                raise ValueError(
                    f"Balance insufficiente per {trader.name}: "
                    f"richiesto {cost:.2f}, disponibile {trader.balance:.2f}."
                )
            # Aggiorna media ponderata del prezzo di carico
            old_qty = trader.portfolio.get(asset_id, 0.0)
            old_avg = trader.avg_buy_prices.get(asset_id, 0.0)
            new_qty = old_qty + quantity
            trader.avg_buy_prices[asset_id] = (
                (old_avg * old_qty + current_price * quantity) / new_qty
            )
            trader.portfolio[asset_id] = new_qty
            trader.balance -= cost

        elif action == "SELL":
            held = trader.portfolio.get(asset_id, 0.0)
            if held < quantity:
                raise ValueError(
                    f"Portafoglio insufficiente per {trader.name}: "
                    f"richiesto {quantity:.4f} di {asset_id}, posseduto {held:.4f}."
                )
            avg_buy = trader.avg_buy_prices.get(asset_id, 0.0)
            pnl_realized = (current_price - avg_buy) * quantity
            trader.balance += quantity * current_price
            remaining = held - quantity
            if remaining < 1e-9:
                # Vendita completa: rimuovi le chiavi per pulizia
                trader.portfolio.pop(asset_id, None)
                trader.avg_buy_prices.pop(asset_id, None)
            else:
                trader.portfolio[asset_id] = remaining
                # avg_buy_price rimane invariato su vendita parziale

        else:
            raise ValueError(f"Azione non valida: '{action}'. Usa 'BUY' o 'SELL'.")

        trade = Trade(
            id=str(uuid.uuid4()),
            trader_id=trader_id,
            asset_id=asset_id,
            action=action,
            quantity=quantity,
            price=current_price,
            timestamp=state.current_tick,
            is_copy=is_copy,
            copied_from=copied_from,
            pnl_realized=pnl_realized,
        )
        trader.trade_history.append(trade)
        state.trade_log.append(trade)
        return trade

    def get_portfolio_value(self, trader_id: str) -> float:
        """
        Calcola il valore totale del portafoglio del trader.

        Valore = balance + Σ(portfolio[asset_id] * current_price[asset_id])

        Args:
            trader_id: id del RetailTrader.

        Returns:
            float: valore totale in valuta simulata.
        """
        trader = state.retail_traders[trader_id]
        holdings_value = sum(
            qty * state.assets[asset_id].current_price
            for asset_id, qty in trader.portfolio.items()
            if asset_id in state.assets
        )
        return trader.balance + holdings_value

    def get_total_pnl(self, trader_id: str) -> float:
        """
        Calcola il PnL totale del trader rispetto al bilancio iniziale.

        PnL totale = portfolio_value_corrente - initial_balance

        Args:
            trader_id: id del RetailTrader.

        Returns:
            float: PnL totale (positivo = guadagno, negativo = perdita).
        """
        return self.get_portfolio_value(trader_id) - state.retail_traders[trader_id].initial_balance

    def get_summary(self, trader_id: str) -> dict:
        """
        Restituisce un dizionario riepilogativo del trader retail.

        Campi restituiti:
            id, name, balance, portfolio_value, total_pnl,
            n_trades, copied_traders

        Args:
            trader_id: id del RetailTrader.

        Returns:
            dict con i dati del trader.
        """
        trader = state.retail_traders[trader_id]
        portfolio_value = self.get_portfolio_value(trader_id)
        return {
            "id": trader.id,
            "name": trader.name,
            "balance": round(trader.balance, 4),
            "portfolio_value": round(portfolio_value, 4),
            "total_pnl": round(portfolio_value - trader.initial_balance, 4),
            "n_trades": len(trader.trade_history),
            "copied_traders": list(trader.copied_traders),
        }

    def create_simulated_retailers(self, n: int = 10) -> List[RetailTrader]:
        """
        Crea N retail trader simulati con nomi e bilanci casuali.

        Ogni trader ha un bilancio iniziale casuale tra 5000 e 20000.
        Utili per popolare la simulazione senza un utente reale.

        Args:
            n: numero di trader simulati da creare.

        Returns:
            Lista dei RetailTrader creati.
        """
        traders = []
        name_pool = list(_SIMULATED_NAMES)
        random.shuffle(name_pool)

        for i in range(n):
            # Ricicla i nomi se n > len(_SIMULATED_NAMES)
            name = name_pool[i % len(name_pool)]
            if i >= len(name_pool):
                name = f"{name}_{i}"
            balance = round(random.uniform(5000.0, 20000.0), 2)
            trader = self.create_retail_trader(
                name=name,
                initial_balance=balance,
                is_real_user=False,
            )
            traders.append(trader)

        return traders


# ── Istanza globale ────────────────────────────────────────────────────────
# Importabile direttamente: from traders.retail import retail_engine
retail_engine = RetailTraderEngine()
