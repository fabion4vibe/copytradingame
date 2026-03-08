"""
professional.py
---------------
Implementa ProfessionalTrader con la macchina a stati finiti (FSM) che controlla
il comportamento del trader nelle tre fasi del ciclo di vita.

Nucleo didattico del progetto: mostra come un trader apparentemente indipendente
sia in realtà controllato dalla piattaforma tramite incentivi e transizioni di fase.

Uso tipico:
    from traders.professional import ProfessionalTraderEngine, TraderPhase
    engine = ProfessionalTraderEngine()
    trader = engine.create_professional_trader("Marco")
    trade  = engine.execute_strategy(trader.id)
"""

import random
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from state import state
from traders.retail import Trade, retail_engine


# ── Enum TraderPhase ───────────────────────────────────────────────────────

class TraderPhase(str, Enum):
    """
    Fasi del ciclo di vita di un trader professionista.

    REPUTATION_BUILD — Fase A: il trader opera con EV positivo per costruire
                       uno storico attraente e raccogliere i primi follower.
    FOLLOWER_GROWTH  — Fase B: il trader mantiene buone performance per attrarre
                       più follower e aumentare il capitale retail esposto.
    MONETIZATION     — Fase C: la piattaforma attiva la monetizzazione. Il trader
                       inizia a operare con EV negativo, danneggiando i follower,
                       mentre riceve un bonus fisso per ogni tick in questa fase.
    """

    REPUTATION_BUILD = "REPUTATION_BUILD"
    FOLLOWER_GROWTH  = "FOLLOWER_GROWTH"
    MONETIZATION     = "MONETIZATION"


# ── Dataclass StrategyProfile ──────────────────────────────────────────────

@dataclass
class StrategyProfile:
    """
    Parametri operativi che definiscono il comportamento del trader per fase.

    Campi:
        expected_value          — EV atteso per trade (positivo in A/B, negativo in C)
        risk_level              — 0.0–1.0: influenza la dimensione delle posizioni
        trade_frequency         — probabilità di eseguire un trade per tick (0.0–1.0)
        min_followers_for_B     — soglia follower per transizione automatica A→B
        min_followers_for_C     — soglia follower per transizione automatica B→C
        target_capital_exposed  — capitale retail esposto target per attivare la fase C
        bonus_per_tick_in_C     — bonus fisso pagato dalla piattaforma per ogni tick in C
    """

    expected_value: float
    risk_level: float
    trade_frequency: float
    min_followers_for_B: int
    min_followers_for_C: int
    target_capital_exposed: float
    bonus_per_tick_in_C: float


# ── Profili strategia predefiniti ─────────────────────────────────────────

DEFAULT_STRATEGY_A = StrategyProfile(
    expected_value=+0.015,       # EV positivo: in media +1.5% per trade
    risk_level=0.2,
    trade_frequency=0.4,         # 40% di probabilità di tradare per tick
    min_followers_for_B=5,
    min_followers_for_C=15,
    target_capital_exposed=50000.0,
    bonus_per_tick_in_C=0.0,     # nessun bonus in fase A
)

DEFAULT_STRATEGY_B = StrategyProfile(
    expected_value=+0.008,       # EV ancora positivo, più conservativo
    risk_level=0.3,
    trade_frequency=0.6,
    min_followers_for_B=5,
    min_followers_for_C=15,
    target_capital_exposed=50000.0,
    bonus_per_tick_in_C=0.0,
)

DEFAULT_STRATEGY_C = StrategyProfile(
    expected_value=-0.020,       # EV negativo: in media -2% per trade
    risk_level=0.7,
    trade_frequency=0.8,         # alta frequenza per massimizzare il danno ai follower
    min_followers_for_B=5,
    min_followers_for_C=15,
    target_capital_exposed=50000.0,
    bonus_per_tick_in_C=200.0,   # bonus fisso per tick in fase C
)

# Mappa fase → profilo predefinito (usata da transition_phase)
_DEFAULT_STRATEGY_BY_PHASE = {
    TraderPhase.REPUTATION_BUILD: DEFAULT_STRATEGY_A,
    TraderPhase.FOLLOWER_GROWTH:  DEFAULT_STRATEGY_B,
    TraderPhase.MONETIZATION:     DEFAULT_STRATEGY_C,
}

# Nomi casuali per i trader simulati
_PRO_NAMES = [
    "Maverick", "Oracle", "Falcon", "Titan", "Apex",
    "Vector", "Cipher", "Nexus", "Zenith", "Phantom",
]


# ── Dataclass ProfessionalTrader ───────────────────────────────────────────

@dataclass
class ProfessionalTrader:
    """
    Rappresenta un trader professionista controllato dalla FSM della piattaforma.

    Campi:
        id                      — UUID univoco
        name                    — nome visualizzato
        phase                   — fase corrente della FSM
        strategy                — profilo strategico attivo per questa fase
        balance                 — liquidità disponibile
        portfolio               — asset_id → quantità posseduta
        avg_buy_prices          — asset_id → prezzo medio di carico
        pnl_personal            — PnL accumulato dal trading effettivo
        bonus_earned            — bonus totali ricevuti dalla piattaforma (fase C)
        followers               — lista di retail_trader_id che copiano questo trader
        follower_capital_exposed — somma del valore di portafoglio dei follower
        trade_history           — lista di Trade eseguiti
        phase_history           — log dei cambi di fase con dettagli didattici
        initial_balance         — bilancio iniziale per calcolo PnL
    """

    id: str
    name: str
    phase: TraderPhase
    strategy: StrategyProfile
    balance: float
    portfolio: Dict[str, float] = field(default_factory=dict)
    avg_buy_prices: Dict[str, float] = field(default_factory=dict)
    pnl_personal: float = 0.0
    bonus_earned: float = 0.0
    followers: List[str] = field(default_factory=list)
    follower_capital_exposed: float = 0.0
    trade_history: List[Any] = field(default_factory=list)
    phase_history: List[dict] = field(default_factory=list)
    initial_balance: float = 50000.0


# ── Engine ─────────────────────────────────────────────────────────────────

class ProfessionalTraderEngine:
    """
    Gestisce la creazione, l'esecuzione della strategia e le transizioni di fase
    dei trader professionisti.

    La FSM (macchina a stati finiti) è il meccanismo centrale: la piattaforma
    controlla quando e come il trader cambia comportamento, indipendentemente
    dalla volontà del trader stesso.
    """

    def create_professional_trader(
        self,
        name: str,
        initial_phase: TraderPhase = TraderPhase.REPUTATION_BUILD,
        strategy: Optional[StrategyProfile] = None,
    ) -> ProfessionalTrader:
        """
        Crea un nuovo ProfessionalTrader, lo aggiunge a state.professional_traders.

        Args:
            name:          nome del trader.
            initial_phase: fase iniziale della FSM (default: REPUTATION_BUILD).
            strategy:      profilo strategico. Se None, usa il profilo predefinito
                           per la fase iniziale.

        Returns:
            Il ProfessionalTrader appena creato.
        """
        if strategy is None:
            strategy = _DEFAULT_STRATEGY_BY_PHASE[initial_phase]

        trader = ProfessionalTrader(
            id=str(uuid.uuid4()),
            name=name,
            phase=initial_phase,
            strategy=strategy,
            balance=50000.0,
            initial_balance=50000.0,
        )
        state.professional_traders[trader.id] = trader
        return trader

    def execute_strategy(self, trader_id: str) -> Optional[Trade]:
        """
        Esegue la strategia del professionista per il tick corrente.

        Logica:
        1. Estrae random() — se >= trade_frequency, nessun trade questo tick.
        2. Sceglie un asset casuale tra quelli in state.assets.
        3. Determina l'azione in base alla fase:
           - REPUTATION_BUILD / FOLLOWER_GROWTH:
               Compra asset con drift >= 0 (trend positivo), vende asset con
               drift < 0 (trend negativo). EV atteso positivo.
           - MONETIZATION:
               Inverte la logica: compra asset in calo, vende asset in crescita.
               EV atteso negativo, massimizzando le perdite dei follower che copiano.
        4. Calcola la quantità in base a risk_level e balance/portfolio disponibili.
        5. Esegue il trade aggiornando balance, portfolio e avg_buy_prices.
        6. Se in MONETIZATION, accredita bonus_per_tick_in_C al trader e aggiorna
           state.platform_bonus_paid e state.platform_pnl.

        Args:
            trader_id: id del ProfessionalTrader.

        Returns:
            Il Trade eseguito, oppure None se nessun trade questo tick.
        """
        trader = state.professional_traders[trader_id]

        # 1. Probabilità di trade per questo tick
        if random.random() >= trader.strategy.trade_frequency:
            return None

        # 2. Asset casuale
        if not state.assets:
            return None
        asset_id = random.choice(list(state.assets.keys()))
        asset = state.assets[asset_id]
        current_price = asset.current_price

        # 3. Azione preferita in base alla fase e al drift dell'asset
        in_monetization = (trader.phase == TraderPhase.MONETIZATION)
        if not in_monetization:
            # A/B: EV positivo → segui il trend
            prefer_buy = (asset.drift >= 0)
        else:
            # C: EV negativo → vai contro il trend (compra ciò che scende)
            prefer_buy = (asset.drift < 0)

        # 4. Calcola quantità e verifica fattibilità
        trade = self._try_execute(trader, asset_id, current_price, prefer_buy)
        if trade is None:
            return None

        # 5. Se in MONETIZATION, accumula bonus della piattaforma
        if in_monetization:
            bonus = trader.strategy.bonus_per_tick_in_C
            if bonus > 0:
                trader.bonus_earned += bonus
                state.platform_bonus_paid += bonus
                state.platform_pnl -= bonus   # il bonus è un costo per la piattaforma

        return trade

    def _try_execute(
        self,
        trader: ProfessionalTrader,
        asset_id: str,
        current_price: float,
        prefer_buy: bool,
    ) -> Optional[Trade]:
        """
        Tenta di eseguire un trade per il professionista.

        Prova prima l'azione preferita; se non fattibile, prova quella opposta.
        Restituisce None se nessuna delle due è eseguibile.

        Args:
            trader:        istanza ProfessionalTrader.
            asset_id:      id dell'asset.
            current_price: prezzo corrente dell'asset.
            prefer_buy:    True se l'azione preferita è BUY.

        Returns:
            Trade eseguito, o None.
        """
        for action in (("BUY" if prefer_buy else "SELL"),
                       ("SELL" if prefer_buy else "BUY")):
            trade = self._execute_action(trader, asset_id, current_price, action)
            if trade is not None:
                return trade
        return None

    def _execute_action(
        self,
        trader: ProfessionalTrader,
        asset_id: str,
        current_price: float,
        action: str,
    ) -> Optional[Trade]:
        """
        Esegue concretamente un BUY o SELL sul portafoglio del professionista.

        Logica analoga a RetailTraderEngine.execute_trade, ma opera sui campi
        del ProfessionalTrader. Non chiama execute_trade di retail per evitare
        l'accoppiamento tra tipi diversi di trader.

        Args:
            trader:        istanza ProfessionalTrader da aggiornare.
            asset_id:      id dell'asset.
            current_price: prezzo corrente.
            action:        "BUY" o "SELL".

        Returns:
            Trade registrato, oppure None se non è possibile eseguire l'azione.
        """
        pnl_realized = 0.0

        if action == "BUY":
            # Quantità proporzionale al risk_level e al balance disponibile
            max_spend = trader.strategy.risk_level * 0.25 * trader.balance
            quantity = max_spend / current_price if current_price > 0 else 0.0
            if quantity < 1e-6 or trader.balance < quantity * current_price:
                return None

            old_qty = trader.portfolio.get(asset_id, 0.0)
            old_avg = trader.avg_buy_prices.get(asset_id, 0.0)
            new_qty = old_qty + quantity
            trader.avg_buy_prices[asset_id] = (
                (old_avg * old_qty + current_price * quantity) / new_qty
            )
            trader.portfolio[asset_id] = new_qty
            trader.balance -= quantity * current_price

        else:  # SELL
            held = trader.portfolio.get(asset_id, 0.0)
            if held < 1e-6:
                return None

            # Vendi una frazione del posseduto proporzionale al risk_level
            quantity = trader.strategy.risk_level * held
            avg_buy = trader.avg_buy_prices.get(asset_id, 0.0)
            pnl_realized = (current_price - avg_buy) * quantity
            trader.balance += quantity * current_price
            trader.pnl_personal += pnl_realized

            remaining = held - quantity
            if remaining < 1e-9:
                trader.portfolio.pop(asset_id, None)
                trader.avg_buy_prices.pop(asset_id, None)
            else:
                trader.portfolio[asset_id] = remaining

        trade = Trade(
            id=str(uuid.uuid4()),
            trader_id=trader.id,
            asset_id=asset_id,
            action=action,
            quantity=quantity,
            price=current_price,
            timestamp=state.current_tick,
            pnl_realized=pnl_realized,
        )
        trader.trade_history.append(trade)
        state.trade_log.append(trade)
        return trade

    def transition_phase(self, trader_id: str, new_phase: TraderPhase) -> None:
        """
        Cambia la fase del trader e aggiorna la strategia di conseguenza.

        La transizione viene registrata in phase_history con tutti i dettagli
        necessari per la visualizzazione didattica nell'interfaccia.

        Args:
            trader_id:  id del ProfessionalTrader.
            new_phase:  nuova fase della FSM.
        """
        trader = state.professional_traders[trader_id]
        old_phase = trader.phase

        # Note esplicative per ogni transizione (uso didattico)
        _transition_notes = {
            (TraderPhase.REPUTATION_BUILD, TraderPhase.FOLLOWER_GROWTH):
                "Soglia follower raggiunta. Il trader passa a raccogliere più capitale.",
            (TraderPhase.FOLLOWER_GROWTH, TraderPhase.MONETIZATION):
                "Soglia follower e capitale raggiunti. Attivazione fase di monetizzazione.",
            (TraderPhase.MONETIZATION, TraderPhase.REPUTATION_BUILD):
                "Reset del ciclo. Il trader riparte dalla costruzione della reputazione.",
        }
        note = _transition_notes.get(
            (old_phase, new_phase),
            f"Transizione manuale da {old_phase.value} a {new_phase.value}.",
        )

        # Log della transizione — dati usati dalla dashboard didattica
        phase_entry = {
            "tick": state.current_tick,
            "from_phase": old_phase.value,
            "to_phase": new_phase.value,
            "followers_at_transition": len(trader.followers),
            "capital_exposed_at_transition": round(trader.follower_capital_exposed, 2),
            "note": note,
        }
        trader.phase_history.append(phase_entry)

        # Aggiorna fase e strategia
        trader.phase = new_phase
        trader.strategy = _DEFAULT_STRATEGY_BY_PHASE[new_phase]

    def update_follower_capital(self, trader_id: str) -> None:
        """
        Ricalcola follower_capital_exposed sommando il valore di portafoglio
        di tutti i RetailTrader che copiano questo professionista.

        Deve essere chiamato ad ogni tick dall'orchestratore per mantenere
        aggiornato il dato usato dalla FSM per le transizioni automatiche.

        Args:
            trader_id: id del ProfessionalTrader.
        """
        trader = state.professional_traders[trader_id]
        total = 0.0
        for retail_id in trader.followers:
            if retail_id in state.retail_traders:
                total += retail_engine.get_portfolio_value(retail_id)
        trader.follower_capital_exposed = total

    def get_summary(self, trader_id: str) -> dict:
        """
        Restituisce un dizionario riepilogativo del trader professionista.

        Campi restituiti:
            id, name, phase, followers_count, follower_capital_exposed,
            pnl_personal, bonus_earned, total_compensation,
            n_trades, last_phase_change_tick

        Args:
            trader_id: id del ProfessionalTrader.

        Returns:
            dict con i dati del trader.
        """
        trader = state.professional_traders[trader_id]
        last_tick = (
            trader.phase_history[-1]["tick"]
            if trader.phase_history else None
        )
        return {
            "id": trader.id,
            "name": trader.name,
            "phase": trader.phase.value,
            "followers_count": len(trader.followers),
            "follower_capital_exposed": round(trader.follower_capital_exposed, 2),
            "pnl_personal": round(trader.pnl_personal, 4),
            "bonus_earned": round(trader.bonus_earned, 4),
            "total_compensation": round(trader.pnl_personal + trader.bonus_earned, 4),
            "n_trades": len(trader.trade_history),
            "last_phase_change_tick": last_tick,
        }

    def create_default_professionals(self, n: int = 3) -> List[ProfessionalTrader]:
        """
        Crea N trader professionisti con nomi casuali, tutti in fase REPUTATION_BUILD.

        Args:
            n: numero di trader da creare.

        Returns:
            Lista dei ProfessionalTrader creati.
        """
        name_pool = list(_PRO_NAMES)
        random.shuffle(name_pool)
        traders = []
        for i in range(n):
            name = name_pool[i % len(name_pool)]
            if i >= len(name_pool):
                name = f"{name}_{i}"
            trader = self.create_professional_trader(name=name)
            traders.append(trader)
        return traders


# ── Istanza globale ────────────────────────────────────────────────────────
# Importabile direttamente: from traders.professional import professional_engine
professional_engine = ProfessionalTraderEngine()
