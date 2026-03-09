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

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List

# NOTA: nessun import da altri moduli del progetto per evitare dipendenze
# circolari. I tipi Any verranno sostituiti con le classi specifiche dai
# task successivi man mano che i moduli vengono creati.

# ── Configurazione JSONBin.io ──────────────────────────────────────────────
# Le variabili d'ambiente sono None in locale: i metodi di persistenza
# diventano no-op automaticamente.
JSONBIN_BASE_URL = "https://api.jsonbin.io/v3/b"
JSONBIN_KEY = os.environ.get("JSONBIN_KEY")        # None in locale
JSONBIN_BIN_ID = os.environ.get("JSONBIN_BIN_ID")  # None in locale


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

    def get_state_snapshot(self) -> dict:
        """
        Restituisce uno snapshot completo dello stato, serializzabile in JSON.
        Usato sia per debug/export che per la persistenza remota (JSONBin).

        Il trade_log viene troncato agli ultimi 500 elementi per contenere
        le dimensioni del payload JSON entro limiti ragionevoli per JSONBin free tier.
        """
        return {
            "current_tick":         self.current_tick,
            "platform_pnl":         self.platform_pnl,
            "platform_commissions": self.platform_commissions,
            "platform_bonus_paid":  self.platform_bonus_paid,
            "assets": {
                asset_id: asset.to_dict()
                for asset_id, asset in self.assets.items()
            },
            "retail_traders": {
                trader_id: trader.to_dict()
                for trader_id, trader in self.retail_traders.items()
            },
            "professional_traders": {
                trader_id: trader.to_dict()
                for trader_id, trader in self.professional_traders.items()
            },
            "copy_relations": [cr.to_dict() for cr in self.copy_relations],
            "trade_log": [t.to_dict() for t in self.trade_log[-500:]],
        }

    def save_to_remote(self) -> None:
        """
        Persiste lo stato corrente su JSONBin.io via HTTP PUT.

        Non fa nulla se JSONBIN_KEY o JSONBIN_BIN_ID non sono configurati
        (comportamento atteso in ambiente locale).

        Non solleva eccezioni: se il salvataggio fallisce (timeout, rete,
        rate limit), il tick continua normalmente. Il prossimo salvataggio
        programmato riproverà.
        """
        if not JSONBIN_KEY or not JSONBIN_BIN_ID:
            return

        url = f"{JSONBIN_BASE_URL}/{JSONBIN_BIN_ID}"
        payload = json.dumps(self.get_state_snapshot()).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "X-Master-Key": JSONBIN_KEY,
        }
        req = urllib.request.Request(
            url, data=payload, headers=headers, method="PUT"
        )
        try:
            urllib.request.urlopen(req, timeout=3)
        except (urllib.error.URLError, TimeoutError):
            pass  # DIDACTIC: il fallimento del salvataggio non blocca la simulazione

    @classmethod
    def load_from_remote(cls) -> "dict | None":
        """
        Carica l'ultimo snapshot salvato da JSONBin.io.

        Restituisce il dizionario dello snapshot se disponibile,
        None in tutti gli altri casi (locale, rete assente, bin vuoto,
        risposta malformata).
        """
        if not JSONBIN_KEY or not JSONBIN_BIN_ID:
            return None

        url = f"{JSONBIN_BASE_URL}/{JSONBIN_BIN_ID}/latest"
        headers = {"X-Master-Key": JSONBIN_KEY}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("record")  # JSONBin wrappa il contenuto in "record"
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
            return None


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
    Wrapper module-level per state.get_state_snapshot().

    Mantenuto per compatibilità con i moduli che importano questa funzione
    direttamente (es. orchestrator.py).

    Returns:
        dict con tutti i campi di SimulationState in formato JSON-compatibile.
    """
    return state.get_state_snapshot()
