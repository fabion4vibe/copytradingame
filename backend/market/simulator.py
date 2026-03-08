"""
simulator.py
------------
Implementa `MarketSimulator`: gestisce tutti gli asset simulati e avanza
i prezzi tick per tick tramite il modello GBM (Geometric Brownian Motion).

Solo questo modulo è autorizzato a modificare `state.current_tick`.
"""

import numpy as np
from typing import List, Optional

from market.asset import Asset
from state import state


# ── Costante temporale ────────────────────────────────────────────────────
# dt = 1 significa che ogni tick corrisponde a un'unità di tempo unitaria.
# Tutte le grandezze (drift, volatilità) sono espresse per tick.
DT: float = 1.0


class MarketSimulator:
    """
    Gestisce la simulazione dei prezzi per tutti gli asset registrati.

    Responsabilità:
    - Inizializzare gli asset di default
    - Avanzare i prezzi di tutti gli asset applicando il GBM discreto
    - Aggiornare state.current_tick (unico modulo autorizzato a farlo)
    - Fornire accesso ai prezzi correnti e alla serie storica

    Modello GBM discreto:
        P(t+1) = P(t) * exp( (μ - σ²/2) * dt  +  σ * √dt * Z )
        dove Z ~ N(0, 1)
    """

    def initialize_default_assets(self) -> None:
        """
        Crea i 5 asset simulati predefiniti e li inserisce in state.assets.

        Asset creati:
            SIM-A: prezzo 100, σ=0.02, μ=+0.001  — stabile, lieve crescita
            SIM-B: prezzo  50, σ=0.04, μ= 0.000  — neutro, alta volatilità
            SIM-C: prezzo 200, σ=0.01, μ=+0.002  — crescita costante, bassa vol
            SIM-D: prezzo  75, σ=0.05, μ=-0.001  — volatile, lieve calo strutturale
            SIM-E: prezzo  30, σ=0.03, μ= 0.000  — neutro, volatilità media

        Ogni asset viene inserito in state.assets con chiave = asset.id.
        price_history viene inizializzato con il solo prezzo iniziale (tick 0).
        """
        default_configs = [
            ("sim-a", "SIM-A", 100.0, 0.02,  0.001),
            ("sim-b", "SIM-B",  50.0, 0.04,  0.000),
            ("sim-c", "SIM-C", 200.0, 0.01,  0.002),
            ("sim-d", "SIM-D",  75.0, 0.05, -0.001),
            ("sim-e", "SIM-E",  30.0, 0.03,  0.000),
        ]

        for asset_id, symbol, price, volatility, drift in default_configs:
            asset = Asset(
                id=asset_id,
                symbol=symbol,
                initial_price=price,
                current_price=price,
                volatility=volatility,
                drift=drift,
                price_history=[price],  # price_history[0] == initial_price
            )
            state.assets[asset_id] = asset

    def step(self, n_ticks: int = 1) -> None:
        """
        Avanza la simulazione di n_ticks applicando il GBM discreto a ogni asset.

        Per ogni tick:
            1. Per ogni asset in state.assets, calcola il nuovo prezzo:
               P(t+1) = P(t) * exp( (μ - σ²/2) * dt  +  σ * √dt * Z )
               con Z ~ N(0,1) campionato indipendentemente per ogni asset e tick.
            2. Aggiorna asset.current_price e appende a asset.price_history.
            3. Incrementa state.current_tick di 1.

        Il prezzo è vincolato a rimanere >= 0.01 (il GBM garantisce positività
        matematicamente, ma il clamp protegge da underflow numerici estremi).

        Args:
            n_ticks: numero di tick da simulare in sequenza. Default = 1.
        """
        for _ in range(n_ticks):
            for asset in state.assets.values():
                mu = asset.drift
                sigma = asset.volatility
                p_t = asset.current_price

                # GBM discreto: drift corretto per la convessità (Itô)
                z = float(np.random.normal(0.0, 1.0))
                exponent = (mu - 0.5 * sigma ** 2) * DT + sigma * np.sqrt(DT) * z
                p_next = p_t * np.exp(exponent)

                # Protezione contro underflow (teoricamente impossibile con GBM)
                p_next = max(p_next, 0.01)

                asset.current_price = p_next
                asset.price_history.append(p_next)

            # Incremento tick dopo aver aggiornato tutti gli asset
            state.current_tick += 1

    def get_price(self, asset_id: str) -> float:
        """
        Restituisce il prezzo corrente di un asset.

        Args:
            asset_id: identificatore dell'asset (es. "sim-a").

        Returns:
            float: prezzo corrente dell'asset.

        Raises:
            KeyError: se asset_id non esiste in state.assets.
        """
        return state.assets[asset_id].current_price

    def get_history(self, asset_id: str, last_n: Optional[int] = None) -> List[float]:
        """
        Restituisce la serie storica dei prezzi di un asset.

        Args:
            asset_id: identificatore dell'asset.
            last_n:   se specificato, restituisce solo gli ultimi N valori.
                      Se None o maggiore della lunghezza totale, restituisce
                      l'intera serie storica.

        Returns:
            List[float]: serie storica (o sottoinsieme finale).

        Raises:
            KeyError: se asset_id non esiste in state.assets.
        """
        history = state.assets[asset_id].price_history
        if last_n is not None and last_n < len(history):
            return history[-last_n:]
        return list(history)

    def add_asset(self, asset: Asset) -> None:
        """
        Aggiunge un asset personalizzato alla simulazione.

        Se price_history è vuoto, lo inizializza con il current_price corrente.
        L'asset viene inserito in state.assets con chiave = asset.id.

        Args:
            asset: istanza di Asset da aggiungere.
        """
        if not asset.price_history:
            asset.price_history = [asset.current_price]
        state.assets[asset.id] = asset


# ── Istanza globale ───────────────────────────────────────────────────────
# Importabile direttamente: from market.simulator import market_simulator
market_simulator = MarketSimulator()
