"""
market package
--------------
Simulatore di mercato basato su GBM (Geometric Brownian Motion).

Esporta:
    Asset            — struttura dati di un asset simulato
    MarketSimulator  — motore di simulazione prezzi
    market_simulator — istanza globale condivisa
"""

from market.asset import Asset
from market.simulator import MarketSimulator, market_simulator

__all__ = ["Asset", "MarketSimulator", "market_simulator"]
