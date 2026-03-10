"""
scorer.py
---------
Computes a monetisation score for each professional trader,
representing the priority for transitioning to phase C.

The score is purely analytical: it does not execute trades or modify state.
It is used by recommender.py to generate suggestions for the platform manager.

Typical usage:
    from algorithm.scorer import trader_scorer
    score = trader_scorer.compute_score(trader_id)
    ranking = trader_scorer.rank_all_traders()
"""

from typing import Dict, List, Optional

from state import state
from traders.professional import TraderPhase

# Default weights for score calculation
DEFAULT_WEIGHTS: Dict[str, float] = {
    "w1": 0.35,   # follower count
    "w2": 0.35,   # exposed follower capital
    "w3": 0.15,   # performance (inverted: lower trader earnings → higher readiness for C)
    "w4": 0.15,   # phase urgency
}

# Urgency value associated with each phase
_PHASE_URGENCY: Dict[TraderPhase, float] = {
    TraderPhase.REPUTATION_BUILD: 0.0,
    TraderPhase.FOLLOWER_GROWTH:  0.5,
    TraderPhase.MONETIZATION:     1.0,
}


class TraderScorer:
    """
    Computes and ranks monetisation scores for professional traders.

    The score measures how ready (or high-priority) a trader is for the
    transition to phase C, based on followers, exposed capital, performance,
    and current phase.
    """

    def _get_weights(self, weights: Optional[Dict[str, float]]) -> Dict[str, float]:
        """
        Returns the provided weights, or the defaults if None.

        Args:
            weights: optional weight dictionary with keys w1–w4.

        Returns:
            Weight dictionary to use in the score calculation.
        """
        if weights is None:
            return DEFAULT_WEIGHTS
        return {**DEFAULT_WEIGHTS, **weights}

    def compute_score(
        self, trader_id: str, weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Computes the monetisation score for a professional trader.

        Formula:
            score = w1 * norm_followers
                  + w2 * norm_capital_exposed
                  + w3 * (1 - norm_pnl_personal)
                  + w4 * phase_urgency

        Normalisations [0,1] are relative to the maximum across all professionals.
        If there is only one trader, norm_* = 1.0 for positive values, 0.0 otherwise.

        phase_urgency:
            REPUTATION_BUILD → 0.0
            FOLLOWER_GROWTH  → 0.5
            MONETIZATION     → 1.0

        Args:
            trader_id: ProfessionalTrader id.
            weights:   optional weights (dict with keys w1–w4).
                       If None, DEFAULT_WEIGHTS are used.

        Returns:
            float in [0.0, 1.0]: monetisation priority score.

        Raises:
            KeyError: if trader_id does not exist in state.professional_traders.
        """
        w = self._get_weights(weights)
        traders = list(state.professional_traders.values())

        if not traders:
            return 0.0

        # Raw values for normalisation
        all_followers = [len(t.followers) for t in traders]
        all_capital   = [t.follower_capital_exposed for t in traders]
        all_pnl       = [t.pnl_personal for t in traders]

        max_followers = max(all_followers) if max(all_followers) > 0 else 1.0
        max_capital   = max(all_capital)   if max(all_capital)   > 0 else 1.0

        # For PnL we use the maximum absolute value to normalise on a common scale
        pnl_range = max(abs(p) for p in all_pnl) if any(p != 0 for p in all_pnl) else 1.0

        trader = state.professional_traders[trader_id]

        norm_followers = len(trader.followers) / max_followers
        norm_capital   = trader.follower_capital_exposed / max_capital

        # Normalise PnL to [0,1]: a very positive PnL → high norm → (1 - norm) low
        # The w3 component rewards traders who performed less well (candidates for phase C)
        norm_pnl = (trader.pnl_personal + pnl_range) / (2 * pnl_range)
        norm_pnl = max(0.0, min(1.0, norm_pnl))

        phase_urgency = _PHASE_URGENCY[trader.phase]

        score = (
            w["w1"] * norm_followers
            + w["w2"] * norm_capital
            + w["w3"] * (1.0 - norm_pnl)
            + w["w4"] * phase_urgency
        )
        return round(max(0.0, min(1.0, score)), 4)

    def rank_all_traders(
        self, weights: Optional[Dict[str, float]] = None
    ) -> List[dict]:
        """
        Computes and ranks all professional traders by descending score.

        Args:
            weights: optional weights for score calculation.

        Returns:
            List of dicts sorted by descending score, each containing:
            trader_id, name, phase, score, followers,
            capital_exposed, pnl_personal.
        """
        results = []
        for trader_id, trader in state.professional_traders.items():
            score = self.compute_score(trader_id, weights)
            results.append({
                "trader_id": trader_id,
                "name": trader.name,
                "phase": trader.phase.value,
                "score": score,
                "followers": len(trader.followers),
                "capital_exposed": round(trader.follower_capital_exposed, 2),
                "pnl_personal": round(trader.pnl_personal, 4),
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def check_transition_conditions(self, trader_id: str) -> dict:
        """
        Checks whether the automatic transition conditions are satisfied
        for the given trader.

        Transition A→B requires: followers >= strategy.min_followers_for_B
        Transition B→C requires: followers >= strategy.min_followers_for_C
                             AND capital_exposed >= strategy.target_capital_exposed

        Args:
            trader_id: ProfessionalTrader id.

        Returns:
            dict with:
            - can_transition_to_B:     bool
            - can_transition_to_C:     bool
            - followers_needed_for_B:  int (0 if already satisfied)
            - followers_needed_for_C:  int (0 if already satisfied)
            - capital_needed_for_C:    float (0.0 if already satisfied)
            - current_phase:           str

        Raises:
            KeyError: if trader_id does not exist in state.professional_traders.
        """
        trader = state.professional_traders[trader_id]
        s = trader.strategy
        n_followers = len(trader.followers)
        capital = trader.follower_capital_exposed

        followers_needed_B = max(0, s.min_followers_for_B - n_followers)
        followers_needed_C = max(0, s.min_followers_for_C - n_followers)
        capital_needed_C   = max(0.0, s.target_capital_exposed - capital)

        can_to_B = (
            trader.phase == TraderPhase.REPUTATION_BUILD
            and followers_needed_B == 0
        )
        can_to_C = (
            trader.phase == TraderPhase.FOLLOWER_GROWTH
            and followers_needed_C == 0
            and capital_needed_C == 0.0
        )

        return {
            "can_transition_to_B": can_to_B,
            "can_transition_to_C": can_to_C,
            "followers_needed_for_B": followers_needed_B,
            "followers_needed_for_C": followers_needed_C,
            "capital_needed_for_C": round(capital_needed_C, 2),
            "current_phase": trader.phase.value,
        }


# ── Global instance ────────────────────────────────────────────────────────
# Importable directly: from algorithm.scorer import trader_scorer
trader_scorer = TraderScorer()
