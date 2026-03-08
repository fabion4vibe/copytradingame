"""
scorer.py
---------
Calcola uno score di monetizzazione per ogni trader professionista,
rappresentando la priorità di transizione alla fase C.

Lo score è puramente analitico: non esegue trade né modifica lo stato.
È usato da recommender.py per generare suggerimenti al gestore.

Uso tipico:
    from algorithm.scorer import trader_scorer
    score = trader_scorer.compute_score(trader_id)
    ranking = trader_scorer.rank_all_traders()
"""

from typing import Dict, List, Optional

from state import state
from traders.professional import TraderPhase

# Pesi di default per il calcolo dello score
DEFAULT_WEIGHTS: Dict[str, float] = {
    "w1": 0.35,   # follower count
    "w2": 0.35,   # capitale esposto
    "w3": 0.15,   # performance (inversa: meno il trader guadagna, più è "pronto")
    "w4": 0.15,   # urgenza di fase
}

# Urgenza associata a ogni fase
_PHASE_URGENCY: Dict[TraderPhase, float] = {
    TraderPhase.REPUTATION_BUILD: 0.0,
    TraderPhase.FOLLOWER_GROWTH:  0.5,
    TraderPhase.MONETIZATION:     1.0,
}


class TraderScorer:
    """
    Calcola e ordina gli score di monetizzazione per i trader professionisti.

    Lo score misura quanto un trader è pronto (o prioritario) per la transizione
    alla fase C, basandosi su follower, capitale esposto, performance e fase corrente.
    """

    def _get_weights(self, weights: Optional[Dict[str, float]]) -> Dict[str, float]:
        """
        Restituisce i pesi forniti o quelli di default se None.

        Args:
            weights: dizionario pesi opzionale con chiavi w1–w4.

        Returns:
            Dizionario pesi da usare nel calcolo.
        """
        if weights is None:
            return DEFAULT_WEIGHTS
        return {**DEFAULT_WEIGHTS, **weights}

    def compute_score(
        self, trader_id: str, weights: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calcola lo score di monetizzazione per un trader professionista.

        Formula:
            score = w1 * norm_followers
                  + w2 * norm_capital_exposed
                  + w3 * (1 - norm_pnl_personal)
                  + w4 * phase_urgency

        Le normalizzazioni [0,1] sono relative al massimo tra tutti i professionisti.
        Se c'è un solo trader, norm_* = 1.0 per i valori positivi, 0.0 altrimenti.

        phase_urgency:
            REPUTATION_BUILD → 0.0
            FOLLOWER_GROWTH  → 0.5
            MONETIZATION     → 1.0

        Args:
            trader_id: id del ProfessionalTrader.
            weights:   pesi opzionali (dict con chiavi w1–w4).
                       Se None, usa DEFAULT_WEIGHTS.

        Returns:
            float in [0.0, 1.0]: score di priorità alla monetizzazione.

        Raises:
            KeyError: se trader_id non esiste in state.professional_traders.
        """
        w = self._get_weights(weights)
        traders = list(state.professional_traders.values())

        if not traders:
            return 0.0

        # Valori grezzi per normalizzazione
        all_followers = [len(t.followers) for t in traders]
        all_capital   = [t.follower_capital_exposed for t in traders]
        all_pnl       = [t.pnl_personal for t in traders]

        max_followers = max(all_followers) if max(all_followers) > 0 else 1.0
        max_capital   = max(all_capital)   if max(all_capital)   > 0 else 1.0

        # Per il PnL usiamo il massimo valore assoluto per normalizzare su scala comune
        pnl_range = max(abs(p) for p in all_pnl) if any(p != 0 for p in all_pnl) else 1.0

        trader = state.professional_traders[trader_id]

        norm_followers = len(trader.followers) / max_followers
        norm_capital   = trader.follower_capital_exposed / max_capital

        # Normalizza il PnL in [0,1]: un PnL molto positivo → norm alta → (1 - norm) bassa
        # Il componente w3 premia i trader che hanno performato meno (candidati alla C)
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
        Calcola e ordina tutti i trader professionisti per score decrescente.

        Args:
            weights: pesi opzionali per il calcolo dello score.

        Returns:
            Lista di dict ordinata per score decrescente, ognuno con:
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
        Verifica se le condizioni di transizione automatica sono soddisfatte
        per il trader indicato.

        La transizione A→B richiede: followers >= strategy.min_followers_for_B
        La transizione B→C richiede: followers >= strategy.min_followers_for_C
                                 AND capital_exposed >= strategy.target_capital_exposed

        Args:
            trader_id: id del ProfessionalTrader.

        Returns:
            dict con:
            - can_transition_to_B:     bool
            - can_transition_to_C:     bool
            - followers_needed_for_B:  int (0 se già soddisfatto)
            - followers_needed_for_C:  int (0 se già soddisfatto)
            - capital_needed_for_C:    float (0.0 se già soddisfatto)
            - current_phase:           str

        Raises:
            KeyError: se trader_id non esiste in state.professional_traders.
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


# ── Istanza globale ────────────────────────────────────────────────────────
# Importabile direttamente: from algorithm.scorer import trader_scorer
trader_scorer = TraderScorer()
