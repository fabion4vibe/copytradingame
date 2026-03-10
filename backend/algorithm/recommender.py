"""
recommender.py
--------------
Generates strategic recommendations for the platform manager.

The engine does not act autonomously: it analyses the current state and produces
suggestions that the manager can accept or ignore from the dashboard.

All "expected_*" values are statistical estimates, not deterministic forecasts.

Typical usage:
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
    Analyses the simulation state and produces recommendations for the platform manager.

    Recommendations are sorted by descending score (highest priority first).
    Platform gain estimates are approximations based on expected EV and trade frequency:
    they do not account for market variance.
    """

    def get_recommendations(
        self, weights: Optional[Dict[str, float]] = None
    ) -> List[dict]:
        """
        Analyses all traders and produces a sorted list of recommendations.

        suggested_action is determined by:
        - Transition conditions met → suggest transition
        - Trader in phase A/B with high score but insufficient followers → AWAIT
        - Trader in phase C → suggest MAINTAIN or REDUCE_RISK if score drops
        - Trader in A with low frequency → INCREASE_TRADE_FREQUENCY

        NOTE: expected_platform_gain is a statistical estimate (EV * capital * freq),
        not an observed value. Use only as a priority indicator.

        Args:
            weights: optional weights for score calculation.

        Returns:
            List of recommendations sorted by descending score. Each entry:
            - trader_id, trader_name, current_phase
            - suggested_action: string identifying the suggested action
            - reason:           human-readable explanation (in Italian for UI display)
            - expected_platform_gain: estimated platform gain (if applicable)
            - risk_level:       "LOW" | "MEDIUM" | "HIGH"
            - confidence:       0.0–1.0
            - score:            priority score computed by TraderScorer
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
        Determines the recommended action for a single trader.

        Returns a tuple (action, reason, risk_level, confidence, expected_gain).

        Args:
            trader:     ProfessionalTrader instance.
            conditions: output of check_transition_conditions().
            score:      score computed by TraderScorer.

        Returns:
            Tuple (action: str, reason: str, risk: str, confidence: float, gain: float).
        """
        phase = trader.phase
        n_followers = len(trader.followers)
        capital = trader.follower_capital_exposed

        # Estimate platform gain if the trader transitions to phase C
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
        Estimates the platform's net gain if a trader transitions to phase C.

        Formula:
            expected_retail_loss = capital * |EV_C| * trade_frequency * n_ticks
            expected_platform_net = expected_retail_loss - (bonus_per_tick * n_ticks)

        Args:
            capital:   current exposed follower capital.
            strategy:  StrategyProfile for phase C (DEFAULT_STRATEGY_C).
            n_ticks:   time horizon of the estimate.

        Returns:
            float: expected net platform gain (may be negative).
        """
        expected_retail_loss = capital * abs(strategy.expected_value) * strategy.trade_frequency * n_ticks
        bonus_cost = strategy.bonus_per_tick_in_C * n_ticks
        return expected_retail_loss - bonus_cost

    def simulate_scenario(
        self, trader_id: str, scenario: str, n_ticks: int = 10
    ) -> dict:
        """
        Estimates the effect of a scenario over N future ticks (statistical model, not deterministic).

        Supported scenarios:
        - "TRANSITION_TO_MONETIZATION": uses phase C parameters (DEFAULT_STRATEGY_C)
          to estimate expected retail loss and net platform gain.
        - "MAINTAIN_CURRENT_PHASE": uses the trader's current strategy.

        Shared formula:
            expected_retail_loss = follower_capital * |EV| * trade_frequency * n_ticks
            expected_bonus_paid  = bonus_per_tick_in_C * n_ticks
            expected_platform_net = expected_retail_loss - expected_bonus_paid

        confidence_interval is ±1σ computed assuming variance proportional
        to EV and the square root of the number of ticks (CLT approximation).

        NOTE: "expected_*" values are statistical estimates based on expected EV.
        They do not account for market variance or actual trader behaviour.
        Use only as indicative decision support.

        Args:
            trader_id: ProfessionalTrader id.
            scenario:  "TRANSITION_TO_MONETIZATION" or "MAINTAIN_CURRENT_PHASE".
            n_ticks:   time horizon (default 10).

        Returns:
            dict with scenario, trader_id, n_ticks, expected_retail_loss,
            expected_bonus_paid, expected_platform_net_gain, confidence_interval.

        Raises:
            KeyError:   if trader_id does not exist.
            ValueError: if scenario is not supported.
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

        # ±1σ: approximation based on process variance (CLT)
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
        Concise overview of the platform's economic state.

        Computes:
        - platform_net: pnl + commissions - bonus_paid
        - total_retail_capital: sum of portfolio_value across all retail traders
        - total_capital_in_copy: retail capital actually in copy (from copy_engine)
        - copy_penetration_pct: % of retail capital in copy
        - n_professionals_in_monetization: professional traders in phase C
        - n_retail_losing: retail traders with negative total PnL
        - avg_retail_pnl: average total PnL across all retail traders

        Returns:
            dict with all fields described above.
        """
        # Retail capital
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

        # Professionals in phase C
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


# ── Global instance ────────────────────────────────────────────────────────
# Importable directly: from algorithm.recommender import strategy_recommender
strategy_recommender = StrategyRecommender()
