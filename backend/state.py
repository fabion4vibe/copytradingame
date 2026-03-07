"""
state.py
--------
Singola fonte di verità per l'intera simulazione.
Tutti i moduli backend importano da questo file per leggere e scrivere
lo stato condiviso. Non esiste database: tutto vive in memoria.

Uso tipico negli altri moduli:
    from state import state

    state.current_tick += 1
    state.assets["SIM-A"] = my_asset
    state.platform_pnl += 150.0
"""

from typing import Any, Dict, List
from dataclasses import dataclass, field

# NOTA: nessun import da altri moduli del progetto per evitare dipendenze
# circolari. I tipi Any verranno sostituiti con le classi specifiche dai
# task successivi man mano che i moduli vengono creati.


@dataclass
class SimulationState:
    """
    Stato globale della simulazione, condiviso tra tutti i moduli backend.

    Campi:
        current_tick          — tick corrente della simulazione (avanzato da MarketSimulator)
        assets                — dizionario asset_id → Asset (popolato da TASK_02)
        retail_traders        — dizionario id → RetailTrader (popolato da TASK_03)
        professional_traders  — dizionario id → ProfessionalTrader (popolato da TASK_04)
        copy_relations        — lista di CopyRelation attive e inattive (popolata da TASK_05)
        platform_pnl          — profitto cumulativo della piattaforma (perdite nette retail)
        platform_commissions  — commissioni accumulate (non usate nei task iniziali)
        platform_bonus_paid   — totale bonus pagati ai trader professionisti in fase C
        trade_log             — log globale di tutti i trade eseguiti (retail + professionisti)
    """

    # ── Mercato ───────────────────────────────────────────────────────────
    current_tick: int = 0
    assets: Dict[str, Any] = field(default_factory=dict)          # asset_id → Asset

    # ── Trader ────────────────────────────────────────────────────────────
    retail_traders: Dict[str, Any] = field(default_factory=dict)        # id → RetailTrader
    professional_traders: Dict[str, Any] = field(default_factory=dict)  # id → ProfessionalTrader

    # ── Copy trading ──────────────────────────────────────────────────────
    copy_relations: List[Any] = field(default_factory=list)        # lista CopyRelation

    # ── Economia piattaforma ──────────────────────────────────────────────
    platform_pnl: float = 0.0           # profitto cumulativo (dalle perdite retail)
    platform_commissions: float = 0.0   # commissioni accumulate
    platform_bonus_paid: float = 0.0    # bonus pagati ai professionisti in fase C

    # ── Storico globale ───────────────────────────────────────────────────
    trade_log: List[Any] = field(default_factory=list)             # tutti i trade eseguiti


# ── Singleton ─────────────────────────────────────────────────────────────
# Istanza condivisa importabile direttamente:
#     from state import state
state = SimulationState()


# ── Funzioni helper ───────────────────────────────────────────────────────

def reset_state() -> None:
    """
    Reimposta lo stato globale ai valori iniziali.

    Muta l'istanza esistente invece di ricrearla, in modo che tutti i moduli
    che hanno già importato `state` con `from state import state` continuino
    a puntare all'oggetto corretto dopo il reset.

    Utile per il restart della simulazione tramite l'endpoint /manager/reset.
    """
    state.current_tick = 0
    state.assets.clear()
    state.retail_traders.clear()
    state.professional_traders.clear()
    state.copy_relations.clear()
    state.platform_pnl = 0.0
    state.platform_commissions = 0.0
    state.platform_bonus_paid = 0.0
    state.trade_log.clear()


def _serialize(obj: Any) -> Any:
    """
    Converte ricorsivamente un oggetto in un tipo serializzabile JSON.

    Strategia:
    - Oggetti con metodo `to_dict()` → chiama to_dict() (convenzione dei moduli domain)
    - dict → ricorre sui valori
    - list → ricorre sugli elementi
    - Primitivi (int, float, str, bool, None) → passati as-is
    - Tutto il resto → convertito a stringa come fallback
    """
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    # Fallback: enum, dataclass senza to_dict, ecc.
    return str(obj)


def get_state_snapshot() -> dict:
    """
    Restituisce uno snapshot serializzabile (JSON-compatibile) dello stato corrente.

    Utile per debug, export e ispezione dello stato dalla console.
    Ogni valore viene convertito tramite _serialize(), che chiama to_dict()
    sugli oggetti di dominio quando disponibile.

    Returns:
        dict con tutti i campi di SimulationState in formato JSON-compatibile.
    """
    return {
        "current_tick": state.current_tick,
        "assets": _serialize(state.assets),
        "retail_traders": _serialize(state.retail_traders),
        "professional_traders": _serialize(state.professional_traders),
        "copy_relations": _serialize(state.copy_relations),
        "platform_pnl": state.platform_pnl,
        "platform_commissions": state.platform_commissions,
        "platform_bonus_paid": state.platform_bonus_paid,
        "trade_log": _serialize(state.trade_log),
    }
