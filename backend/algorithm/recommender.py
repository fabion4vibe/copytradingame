"""
recommender.py
--------------
Genera raccomandazioni strategiche per il gestore della piattaforma.

Il motore non agisce autonomamente: analizza lo stato corrente e produce
suggerimenti che il gestore può accettare o ignorare dalla dashboard.

Tutti i valori "expected_*" sono stime statistiche, non previsioni deterministiche.

Uso tipico:
    from algorithm.recommender import strategy_recommender
    recs  = strategy_recommender.get_recommendations()
    sim   = strategy_recommender.simulate_scenario(trader_id, "TRANSITION_TO_MONETIZATION")
    report = strategy_recommender.get_platform_health_report()
"""

import math
from typing import Dict, List, Optional

from state import state
from traders.professional import TraderPhase, DEFAULT_STRATEGY_C
from traders.retail import retail_engine
from traders.copy_engine import copy_engine
from algorithm.scorer import trader_scorer


class StrategyRecommender:
    """
    Analizza lo stato della simulazione e produce raccomandazioni per il gestore.

    Le raccomandazioni sono ordinate per score decrescente (priorità alta prima).
    Le stime di guadagno piattaforma sono approssimazioni basate su EV atteso
    e frequenza di trade: non tengono conto della varianza del mercato.
    """

    def get_recommendations(
        self, weights: Optional[Dict[str, float]] = None
    ) -> List[dict]:
        """
        Analizza tutti i trader e produce una lista di raccomandazioni ordinate.

        La suggested_action è determinata da:
        - Condizioni di transizione soddisfatte → suggerisci transizione
        - Trader in fase A/B con score alto ma senza follower sufficienti → AWAIT
        - Trader in fase C → suggerisci MAINTAIN o REDUCE_RISK se score scende
        - Trader in A con frequenza bassa → INCREASE_TRADE_FREQUENCY

        NOTA: expected_platform_gain è una stima statistica (EV * capital * freq),
        non un dato osservato. Usare solo come indicazione di priorità.

        Args:
            weights: pesi opzionali per il calcolo degli score.

        Returns:
            Lista di raccomandazioni ordinate per score decrescente. Ogni entry:
            - trader_id, trader_name, current_phase
            - suggested_action: stringa che identifica l'azione suggerita
            - reason:           spiegazione leggibile in italiano
            - expected_platform_gain: stima guadagno piattaforma (se applicabile)
            - risk_level:       "LOW" | "MEDIUM" | "HIGH"
            - confidence:       0.0–1.0
            - score:            score di priorità calcolato dal TraderScorer
        """
        ranking = trader_scorer.rank_all_traders(weights)
        recommendations = []

        for entry in ranking:
            trader_id = entry["trader_id"]
            trader = state.professional_traders[trader_id]
            conditions = trader_scorer.check_transition_conditions(trader_id)
            score = entry["score"]

            action, reason, risk, confidence, expected_gain = self._determine_action(
                trader, conditions, score
            )

            recommendations.append({
                "trader_id": trader_id,
                "trader_name": trader.name,
                "current_phase": trader.phase.value,
                "suggested_action": action,
                "reason": reason,
                "expected_platform_gain": round(expected_gain, 2),
                "risk_level": risk,
                "confidence": round(confidence, 3),
                "score": score,
            })

        return recommendations

    def _determine_action(
        self,
        trader,
        conditions: dict,
        score: float,
    ):
        """
        Determina l'azione raccomandata per un singolo trader.

        Restituisce una tupla (action, reason, risk_level, confidence, expected_gain).

        Args:
            trader:     istanza ProfessionalTrader.
            conditions: output di check_transition_conditions().
            score:      score calcolato dal TraderScorer.

        Returns:
            Tupla (action: str, reason: str, risk: str, confidence: float, gain: float).
        """
        phase = trader.phase
        n_followers = len(trader.followers)
        capital = trader.follower_capital_exposed

        # Stima guadagno piattaforma se si transiziona a C
        estimated_gain_if_C = self._estimate_monetization_gain(
            capital, DEFAULT_STRATEGY_C, n_ticks=10
        )

        if phase == TraderPhase.MONETIZATION:
            if score > 0.6:
                return (
                    "MAINTAIN_CURRENT_PHASE",
                    f"{trader.name} è in fase C con score alto ({score:.2f}). "
                    "Mantenere la strategia corrente per massimizzare il rendimento.",
                    "HIGH",
                    min(0.9, score),
                    0.0,
                )
            else:
                return (
                    "REDUCE_RISK_LEVEL",
                    f"{trader.name} è in fase C ma lo score scende ({score:.2f}). "
                    "Ridurre il risk_level per preservare i follower rimanenti.",
                    "MEDIUM",
                    0.6,
                    0.0,
                )

        if phase == TraderPhase.FOLLOWER_GROWTH:
            if conditions["can_transition_to_C"]:
                confidence = min(0.95, 0.6 + 0.01 * n_followers + capital / 200000)
                return (
                    "TRANSITION_TO_MONETIZATION",
                    f"{trader.name} ha {n_followers} follower e {capital:.0f} di capitale esposto. "
                    "Le soglie sono raggiunte: avviare la monetizzazione.",
                    "HIGH",
                    confidence,
                    estimated_gain_if_C,
                )
            else:
                missing_f = conditions["followers_needed_for_C"]
                missing_c = conditions["capital_needed_for_C"]
                return (
                    "AWAIT_MORE_FOLLOWERS",
                    f"{trader.name} è in fase B ma mancano ancora "
                    f"{missing_f} follower e {missing_c:.0f} di capitale per attivare C.",
                    "LOW",
                    max(0.4, score),
                    0.0,
                )

        # REPUTATION_BUILD
        if conditions["can_transition_to_B"]:
            return (
                "TRANSITION_TO_FOLLOWER_GROWTH",
                f"{trader.name} ha raggiunto la soglia follower per la fase B "
                f"({n_followers} follower). Passare a FOLLOWER_GROWTH per attrarre capitale.",
                "MEDIUM",
                min(0.85, 0.5 + score * 0.4),
                0.0,
            )

        if trader.strategy.trade_frequency < 0.5 and n_followers < trader.strategy.min_followers_for_B:
            return (
                "INCREASE_TRADE_FREQUENCY",
                f"{trader.name} è in fase A con bassa frequenza di trade ({trader.strategy.trade_frequency:.0%}). "
                "Aumentare la visibilità per attrarre i primi follower.",
                "LOW",
                0.55,
                0.0,
            )

        return (
            "MAINTAIN_CURRENT_PHASE",
            f"{trader.name} è in fase A. Continuare a costruire la reputazione "
            f"({n_followers}/{trader.strategy.min_followers_for_B} follower per passare a B).",
            "LOW",
            max(0.4, score * 0.6),
            0.0,
        )

    def _estimate_monetization_gain(
        self, capital: float, strategy, n_ticks: int
    ) -> float:
        """
        Stima il guadagno netto della piattaforma se un trader transiziona a C.

        Formula:
            expected_retail_loss = capital * |EV_C| * trade_frequency * n_ticks
            expected_platform_net = expected_retail_loss - (bonus_per_tick * n_ticks)

        Args:
            capital:   capitale follower esposto corrente.
            strategy:  StrategyProfile della fase C (DEFAULT_STRATEGY_C).
            n_ticks:   orizzonte temporale della stima.

        Returns:
            float: guadagno netto atteso della piattaforma (può essere negativo).
        """
        expected_retail_loss = capital * abs(strategy.expected_value) * strategy.trade_frequency * n_ticks
        bonus_cost = strategy.bonus_per_tick_in_C * n_ticks
        return expected_retail_loss - bonus_cost

    def simulate_scenario(
        self, trader_id: str, scenario: str, n_ticks: int = 10
    ) -> dict:
        """
        Stima l'effetto di uno scenario su N tick futuri (modello statistico, non deterministico).

        Scenari supportati:
        - "TRANSITION_TO_MONETIZATION": usa i parametri della fase C (DEFAULT_STRATEGY_C)
          per stimare perdita retail attesa e guadagno netto piattaforma.
        - "MAINTAIN_CURRENT_PHASE": usa la strategia attuale del trader.

        Formula condivisa:
            expected_retail_loss = follower_capital * |EV| * trade_frequency * n_ticks
            expected_bonus_paid  = bonus_per_tick_in_C * n_ticks
            expected_platform_net = expected_retail_loss - expected_bonus_paid

        La confidence_interval è ±1σ calcolata assumendo varianza proporzionale
        all'EV e alla radice del numero di tick (approssimazione CLT).

        NOTA: i valori "expected_*" sono stime statistiche basate su EV atteso.
        Non tengono conto della varianza del mercato né del comportamento effettivo
        dei trader. Usare solo come supporto decisionale indicativo.

        Args:
            trader_id: id del ProfessionalTrader.
            scenario:  "TRANSITION_TO_MONETIZATION" o "MAINTAIN_CURRENT_PHASE".
            n_ticks:   orizzonte temporale (default 10).

        Returns:
            dict con scenario, trader_id, n_ticks, expected_retail_loss,
            expected_bonus_paid, expected_platform_net_gain, confidence_interval.

        Raises:
            KeyError:   se trader_id non esiste.
            ValueError: se scenario non è supportato.
        """
        trader = state.professional_traders[trader_id]
        capital = trader.follower_capital_exposed

        if scenario == "TRANSITION_TO_MONETIZATION":
            strategy = DEFAULT_STRATEGY_C
        elif scenario == "MAINTAIN_CURRENT_PHASE":
            strategy = trader.strategy
        else:
            raise ValueError(
                f"Scenario '{scenario}' non supportato. "
                "Usa 'TRANSITION_TO_MONETIZATION' o 'MAINTAIN_CURRENT_PHASE'."
            )

        ev = abs(strategy.expected_value)
        freq = strategy.trade_frequency
        bonus_per_tick = strategy.bonus_per_tick_in_C

        expected_retail_loss = capital * ev * freq * n_ticks
        expected_bonus_paid  = bonus_per_tick * n_ticks
        expected_platform_net = expected_retail_loss - expected_bonus_paid

        # ±1σ: approssimazione basata su varianza del processo (CLT)
        # σ_per_tick ≈ capital * risk_level * sqrt(freq)
        sigma_per_tick = capital * strategy.risk_level * math.sqrt(freq)
        sigma_total    = sigma_per_tick * math.sqrt(n_ticks)

        return {
            "scenario": scenario,
            "trader_id": trader_id,
            "n_ticks": n_ticks,
            "expected_retail_loss": round(expected_retail_loss, 2),
            "expected_bonus_paid": round(expected_bonus_paid, 2),
            "expected_platform_net_gain": round(expected_platform_net, 2),
            "confidence_interval": [
                round(expected_platform_net - sigma_total, 2),
                round(expected_platform_net + sigma_total, 2),
            ],
        }

    def get_platform_health_report(self) -> dict:
        """
        Panoramica sintetica dello stato economico della piattaforma.

        Calcola:
        - platform_net: pnl + commissions - bonus_paid
        - total_retail_capital: somma del portfolio_value di tutti i retail
        - total_capital_in_copy: capitale retail effettivamente in copy (da copy_engine)
        - copy_penetration_pct: % del capitale retail in copy
        - n_professionals_in_monetization: trader professionisti in fase C
        - n_retail_losing: retail con PnL totale negativo
        - avg_retail_pnl: media del PnL totale tra tutti i retail

        Returns:
            dict con tutti i campi descritti sopra.
        """
        # Capitale retail
        retail_pnls = []
        total_retail_capital = 0.0
        for retail_id in state.retail_traders:
            pv = retail_engine.get_portfolio_value(retail_id)
            total_retail_capital += pv
            pnl = retail_engine.get_total_pnl(retail_id)
            retail_pnls.append(pnl)

        n_retail_losing = sum(1 for p in retail_pnls if p < 0)
        avg_retail_pnl  = (sum(retail_pnls) / len(retail_pnls)) if retail_pnls else 0.0

        # Copy stats
        copy_stats = copy_engine.get_copy_stats()
        total_capital_in_copy = copy_stats["total_capital_in_copy"]
        copy_penetration = (
            (total_capital_in_copy / total_retail_capital * 100)
            if total_retail_capital > 0 else 0.0
        )

        # Professionisti in fase C
        n_in_monetization = sum(
            1 for t in state.professional_traders.values()
            if t.phase == TraderPhase.MONETIZATION
        )

        return {
            "current_tick": state.current_tick,
            "platform_pnl": round(state.platform_pnl, 2),
            "platform_commissions": round(state.platform_commissions, 2),
            "platform_bonus_paid": round(state.platform_bonus_paid, 2),
            "platform_net": round(
                state.platform_pnl + state.platform_commissions - state.platform_bonus_paid, 2
            ),
            "total_retail_capital": round(total_retail_capital, 2),
            "total_capital_in_copy": round(total_capital_in_copy, 2),
            "copy_penetration_pct": round(copy_penetration, 2),
            "n_professionals_in_monetization": n_in_monetization,
            "n_retail_losing": n_retail_losing,
            "avg_retail_pnl": round(avg_retail_pnl, 4),
        }


# ── Istanza globale ────────────────────────────────────────────────────────
# Importabile direttamente: from algorithm.recommender import strategy_recommender
strategy_recommender = StrategyRecommender()
