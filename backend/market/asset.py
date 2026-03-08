"""
asset.py
--------
Definisce la struttura dati `Asset` che rappresenta un singolo strumento
finanziario simulato. Ogni asset mantiene il proprio storico dei prezzi e
i parametri del modello GBM (drift e volatilità).
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List


@dataclass
class Asset:
    """
    Rappresenta un asset finanziario simulato.

    Attributi:
        id            — identificatore univoco (es. "sim-a")
        symbol        — simbolo leggibile (es. "SIM-A")
        initial_price — prezzo al tick 0, usato come riferimento per il rendimento
        current_price — prezzo corrente, aggiornato ad ogni tick dal MarketSimulator
        volatility    — σ (sigma): deviazione standard del rendimento per tick
        drift         — μ (mu): rendimento atteso per tick (può essere negativo)
        price_history — serie storica completa; price_history[0] == initial_price
    """

    id: str
    symbol: str
    initial_price: float
    current_price: float
    volatility: float
    drift: float
    price_history: List[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        """
        Serializza l'asset in un dizionario JSON-compatibile.

        Non include price_history per default (può essere grande);
        usa get_history() sul simulator per la serie storica completa.

        Returns:
            dict con i campi principali dell'asset, compatibile con lo schema
            Asset definito in openapi.yaml.
        """
        return {
            "id": self.id,
            "symbol": self.symbol,
            "initial_price": self.initial_price,
            "current_price": self.current_price,
            "volatility": self.volatility,
            "drift": self.drift,
            "current_return": self.current_return(),
        }

    def current_return(self) -> float:
        """
        Rendimento percentuale (in forma decimale) dall'inizio della simulazione.

        Formula: (current_price - initial_price) / initial_price

        Returns:
            float: es. 0.05 significa +5%, -0.12 significa -12%.
                   Restituisce 0.0 se initial_price è zero (caso degenere).
        """
        if self.initial_price == 0.0:
            return 0.0
        return (self.current_price - self.initial_price) / self.initial_price

    def volatility_realized(self) -> float:
        """
        Volatilità realizzata: deviazione standard dei rendimenti logaritmici storici.

        Calcolata come std dei log-return: ln(P[t] / P[t-1])

        Returns:
            float: volatilità realizzata. Restituisce 0.0 se in price_history
                   ci sono meno di 2 osservazioni (impossibile calcolare i ritorni).
        """
        if len(self.price_history) < 2:
            return 0.0

        prices = np.array(self.price_history, dtype=float)
        # Filtra prezzi <= 0 per evitare log di valori non positivi
        prices = prices[prices > 0]
        if len(prices) < 2:
            return 0.0

        log_returns = np.log(prices[1:] / prices[:-1])
        return float(np.std(log_returns))
