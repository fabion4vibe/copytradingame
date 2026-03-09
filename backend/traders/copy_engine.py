"""
copy_engine.py
--------------
Implementa il motore di copy trading: propaga le operazioni del trader
professionista a tutti i retail follower attivi.

Questo è il modulo in cui le perdite della fase C si trasferiscono ai follower
e il profitto della piattaforma viene aggiornato.

NOTA DIDATTICA — Meccanismo centrale del conflitto di interessi:
    La piattaforma guadagna dalle perdite nette dei retail.
    Quando un professionista è in fase C (EV negativo), le sue operazioni
    vengono replicate ai follower tramite propagate_trade(). Ogni perdita
    netta subita da un retail si traduce in un guadagno per la piattaforma,
    registrato in state.platform_pnl. Il professionista riceve un bonus
    separato (vedi professional.py). La piattaforma guadagna su entrambi i fronti.

Uso tipico:
    from traders.copy_engine import copy_engine, CopyRelation
    relation = copy_engine.start_copy(retail_id, professional_id, allocation_pct=0.4)
    copy_trades = copy_engine.propagate_trade(professional_trade)
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

from state import state
from traders.retail import Trade, retail_engine
from traders.professional import professional_engine

logger = logging.getLogger(__name__)


# ── Dataclass CopyRelation ─────────────────────────────────────────────────

@dataclass
class CopyRelation:
    """
    Rappresenta una relazione di copy trading tra un retail e un professionista.

    Campi:
        retail_id:       id del RetailTrader follower
        professional_id: id del ProfessionalTrader copiato
        allocation_pct:  frazione del portafoglio retail allocata al copy (0.0–1.0]
        start_tick:      tick in cui la relazione è stata attivata
        active:          False se la relazione è stata disattivata con stop_copy()
    """

    retail_id: str
    professional_id: str
    allocation_pct: float
    start_tick: int
    active: bool = True

    def to_dict(self) -> dict:
        """Serializza la relazione di copy trading in un dizionario JSON-compatibile."""
        return {
            "retail_id": self.retail_id,
            "professional_id": self.professional_id,
            "allocation_pct": self.allocation_pct,
            "start_tick": self.start_tick,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CopyRelation":
        """Ricostruisce una CopyRelation da un dizionario snapshot."""
        return cls(
            retail_id=data["retail_id"],
            professional_id=data["professional_id"],
            allocation_pct=data["allocation_pct"],
            start_tick=data["start_tick"],
            active=data.get("active", True),
        )


# ── Engine ─────────────────────────────────────────────────────────────────

class CopyEngine:
    """
    Gestisce le relazioni di copy trading e la propagazione dei trade.

    È l'unico modulo autorizzato ad aggiornare state.platform_pnl con le
    perdite nette dei retail follower.
    """

    def start_copy(
        self,
        retail_id: str,
        professional_id: str,
        allocation_pct: float = 0.5,
    ) -> CopyRelation:
        """
        Avvia una relazione di copy trading tra un retail e un professionista.

        Validazioni:
        - Il retail esiste in state.retail_traders
        - Il professional esiste in state.professional_traders
        - Non esiste già una CopyRelation attiva tra questi due
        - allocation_pct è in range (0.0, 1.0]

        Azioni:
        - Crea CopyRelation e la aggiunge a state.copy_relations
        - Aggiunge professional_id a retail.copied_traders
        - Aggiunge retail_id a professional.followers
        - Aggiorna follower_capital_exposed del professionista

        Args:
            retail_id:       id del RetailTrader che vuole copiare.
            professional_id: id del ProfessionalTrader da copiare.
            allocation_pct:  frazione del balance retail da allocare (default 0.5).

        Returns:
            La CopyRelation appena creata.

        Raises:
            ValueError: se una validazione fallisce, con messaggio descrittivo.
        """
        if retail_id not in state.retail_traders:
            raise ValueError(f"Retail trader '{retail_id}' non trovato.")
        if professional_id not in state.professional_traders:
            raise ValueError(f"Professional trader '{professional_id}' non trovato.")
        if not (0.0 < allocation_pct <= 1.0):
            raise ValueError(
                f"allocation_pct deve essere in (0.0, 1.0], ricevuto {allocation_pct}."
            )

        # Controlla relazione attiva già esistente
        for rel in state.copy_relations:
            if (rel.retail_id == retail_id
                    and rel.professional_id == professional_id
                    and rel.active):
                raise ValueError(
                    f"Esiste già una relazione attiva tra retail '{retail_id}' "
                    f"e professional '{professional_id}'."
                )

        relation = CopyRelation(
            retail_id=retail_id,
            professional_id=professional_id,
            allocation_pct=allocation_pct,
            start_tick=state.current_tick,
        )
        state.copy_relations.append(relation)

        retail = state.retail_traders[retail_id]
        if professional_id not in retail.copied_traders:
            retail.copied_traders.append(professional_id)

        professional = state.professional_traders[professional_id]
        if retail_id not in professional.followers:
            professional.followers.append(retail_id)

        professional_engine.update_follower_capital(professional_id)
        return relation

    def stop_copy(self, retail_id: str, professional_id: str) -> None:
        """
        Disattiva la relazione di copy trading tra un retail e un professionista.

        Azioni:
        - Imposta CopyRelation.active = False
        - Rimuove professional_id da retail.copied_traders
        - Rimuove retail_id da professional.followers
        - Aggiorna follower_capital_exposed del professionista

        Args:
            retail_id:       id del RetailTrader.
            professional_id: id del ProfessionalTrader.

        Raises:
            ValueError: se non esiste una relazione attiva tra i due.
        """
        found = False
        for rel in state.copy_relations:
            if (rel.retail_id == retail_id
                    and rel.professional_id == professional_id
                    and rel.active):
                rel.active = False
                found = True
                break

        if not found:
            raise ValueError(
                f"Nessuna relazione attiva trovata tra retail '{retail_id}' "
                f"e professional '{professional_id}'."
            )

        retail = state.retail_traders.get(retail_id)
        if retail and professional_id in retail.copied_traders:
            retail.copied_traders.remove(professional_id)

        professional = state.professional_traders.get(professional_id)
        if professional and retail_id in professional.followers:
            professional.followers.remove(retail_id)
            professional_engine.update_follower_capital(professional_id)

    def propagate_trade(self, professional_trade: Trade) -> List[Trade]:
        """
        Replica il trade del professionista a tutti i retail follower attivi.

        Per ogni CopyRelation attiva con professional_id == trade.trader_id:

            BUY:  qty_to_copy = (retail.balance * allocation_pct) / current_price
            SELL: qty_to_copy = retail.portfolio.get(asset_id, 0) * allocation_pct

        Se qty <= 0 o il trade fallisce per balance/portfolio insufficienti,
        il trade viene saltato silenziosamente.

        Aggiornamento state.platform_pnl (meccanismo didattico centrale):
            Dopo ogni trade copiato, il delta PnL del retail viene calcolato.
            Se negativo (il retail ha perso), la piattaforma registra il guadagno:
                state.platform_pnl += abs(delta_pnl)
            La piattaforma non registra guadagni quando il retail guadagna.

        Args:
            professional_trade: il Trade eseguito dal professionista da replicare.

        Returns:
            Lista dei Trade eseguiti sui retail follower.
        """
        professional_id = professional_trade.trader_id
        asset_id = professional_trade.asset_id
        action = professional_trade.action
        current_price = state.assets[asset_id].current_price

        copy_trades: List[Trade] = []

        for rel in state.copy_relations:
            if rel.professional_id != professional_id or not rel.active:
                continue

            retail_id = rel.retail_id
            if retail_id not in state.retail_traders:
                continue

            retail = state.retail_traders[retail_id]

            # Calcola quantità da copiare in base all'azione
            if action == "BUY":
                capital_to_use = retail.balance * rel.allocation_pct
                qty = capital_to_use / current_price if current_price > 0 else 0.0
            else:  # SELL
                held = retail.portfolio.get(asset_id, 0.0)
                qty = held * rel.allocation_pct

            if qty <= 1e-9:
                logger.info(
                    "INFO: trade copiato saltato per quantità zero — "
                    "retail=%s, asset=%s, action=%s",
                    retail_id, asset_id, action,
                )
                continue

            # Snapshot del valore portafoglio prima del trade
            pv_before = retail_engine.get_portfolio_value(retail_id)

            try:
                trade = retail_engine.execute_trade(
                    trader_id=retail_id,
                    asset_id=asset_id,
                    action=action,
                    quantity=qty,
                    is_copy=True,
                    copied_from=professional_id,
                )
                copy_trades.append(trade)
            except ValueError:
                # Balance o portafoglio insufficiente: salta silenziosamente
                logger.info(
                    "INFO: trade copiato saltato per balance insufficiente — "
                    "retail=%s, asset=%s, action=%s, qty=%.4f",
                    retail_id, asset_id, action, qty,
                )
                continue

            # Aggiornamento platform_pnl — la piattaforma guadagna dalle perdite retail
            # NOTA DIDATTICA: questo è il meccanismo del conflitto di interessi.
            # Ogni volta che un follower perde, la piattaforma registra un guadagno
            # equivalente. In fase C, il professionista genera intenzionalmente
            # perdite per i follower, e la piattaforma incassa su entrambi i fronti:
            # dalle perdite retail (qui) e dal bonus al professionista (in professional.py).
            pv_after = retail_engine.get_portfolio_value(retail_id)
            delta_pnl = pv_after - pv_before
            if delta_pnl < 0:
                state.platform_pnl += abs(delta_pnl)

        return copy_trades

    def get_active_relations(
        self, professional_id: Optional[str] = None
    ) -> List[CopyRelation]:
        """
        Restituisce le CopyRelation attive, opzionalmente filtrate per professionista.

        Args:
            professional_id: se specificato, filtra per quel professionista.
                             Se None, restituisce tutte le relazioni attive.

        Returns:
            Lista di CopyRelation attive.
        """
        return [
            rel for rel in state.copy_relations
            if rel.active and (
                professional_id is None or rel.professional_id == professional_id
            )
        ]

    def get_copy_stats(self) -> dict:
        """
        Restituisce statistiche aggregate del copy trading.

        Returns:
            dict con:
            - total_active_relations: numero totale di relazioni attive
            - total_capital_in_copy:  capitale retail totale impegnato in copy
            - by_professional:        per ogni professionista con follower attivi:
                                      followers, capital_exposed, phase
        """
        active = self.get_active_relations()
        total_capital = 0.0
        by_professional: dict = {}

        for rel in active:
            retail = state.retail_traders.get(rel.retail_id)
            pro = state.professional_traders.get(rel.professional_id)
            if retail is None or pro is None:
                continue

            capital = retail_engine.get_portfolio_value(rel.retail_id) * rel.allocation_pct
            total_capital += capital

            if rel.professional_id not in by_professional:
                by_professional[rel.professional_id] = {
                    "followers": 0,
                    "capital_exposed": 0.0,
                    "phase": pro.phase.value,
                }
            by_professional[rel.professional_id]["followers"] += 1
            by_professional[rel.professional_id]["capital_exposed"] += capital

        # Arrotonda capital_exposed per leggibilità
        for stats in by_professional.values():
            stats["capital_exposed"] = round(stats["capital_exposed"], 2)

        return {
            "total_active_relations": len(active),
            "total_capital_in_copy": round(total_capital, 2),
            "by_professional": by_professional,
        }


# ── Istanza globale ────────────────────────────────────────────────────────
# Importabile direttamente: from traders.copy_engine import copy_engine
copy_engine = CopyEngine()
