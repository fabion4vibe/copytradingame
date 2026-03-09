"""
orchestrator.py
---------------
Coordina l'avanzamento della simulazione tick per tick.

Ogni tick completo esegue in ordine:
  1. market.step(1)                         → aggiorna prezzi
  2. Per ogni professionista:
       execute_strategy()                    → genera trade
       Se trade eseguito → propagate_trade() → propaga ai follower
  3. Per ogni professionista:
       update_follower_capital()             → ricalcola esposizione retail
  4. Snapshot JSON opzionale (SAVE_SNAPSHOTS=true)

Supporta sia tick manuali (via API) sia un loop automatico in background.
Il lock garantisce che auto-tick e tick manuali non si sovrappongano.

Uso tipico:
    from orchestrator import orchestrator
    summary = orchestrator.run_tick()
    orchestrator.start_auto_tick(interval_seconds=2.0)
    orchestrator.stop_auto_tick()
"""

import json
import logging
import os
import threading
from collections import deque
from pathlib import Path
from typing import List

from market.simulator import market_simulator
from traders.professional import professional_engine
from traders.copy_engine import copy_engine
from state import state, get_state_snapshot

logger = logging.getLogger(__name__)


class TickOrchestrator:
    """
    Coordina l'esecuzione di un tick completo della simulazione.

    Garantisce l'ordine di esecuzione corretto tra i moduli e previene
    race condition tra tick manuali e il loop automatico tramite un Lock.

    Attributi interni:
        _tick_log:    deque con gli ultimi 1000 tick summary
        _lock:        threading.Lock condiviso tra tick manuali e auto-tick
        _auto_thread: Thread del loop automatico (None se non attivo)
        _stop_event:  Event per segnalare l'arresto del loop automatico
    """

    def __init__(self) -> None:
        self._tick_log: deque = deque(maxlen=1000)
        self._lock = threading.Lock()
        self._auto_thread: threading.Thread = None
        self._stop_event = threading.Event()

    def run_tick(self) -> dict:
        """
        Esegue un singolo tick completo seguendo l'ordine definito.

        Passi:
        1. Avanza i prezzi di mercato (market_simulator.step)
        2. Ogni professionista esegue la propria strategia
        3. I trade dei professionisti vengono propagati ai follower
        4. Il capitale esposto di ogni professionista viene ricalcolato
        5. (Opzionale) Salva snapshot JSON se SAVE_SNAPSHOTS=true

        Thread-safe: acquisisce il lock prima di eseguire qualsiasi step.

        Returns:
            dict con tick, prices, trades_executed, platform_pnl_delta,
            professionals_summary.
        """
        with self._lock:
            pnl_before = state.platform_pnl
            trades_executed = 0

            # Step 1: avanza i prezzi di mercato
            market_simulator.step(1)

            # Step 2 + 3: ogni professionista esegue strategia e propaga ai follower
            professionals_summary = []
            for trader_id in list(state.professional_traders.keys()):
                trade = professional_engine.execute_strategy(trader_id)
                trade_done = trade is not None

                if trade_done:
                    trades_executed += 1
                    copy_trades = copy_engine.propagate_trade(trade)
                    trades_executed += len(copy_trades)

                professionals_summary.append({
                    "id": trader_id,
                    "phase": state.professional_traders[trader_id].phase.value,
                    "trade_executed": trade_done,
                })

            # Step 4: ricalcola il capitale follower esposto per ogni professionista
            for trader_id in state.professional_traders:
                professional_engine.update_follower_capital(trader_id)

            summary = {
                "tick": state.current_tick,
                "prices": {
                    asset_id: round(asset.current_price, 4)
                    for asset_id, asset in state.assets.items()
                },
                "trades_executed": trades_executed,
                "platform_pnl_delta": round(state.platform_pnl - pnl_before, 4),
                "professionals_summary": professionals_summary,
            }

            self._tick_log.append(summary)

            # Step 5: snapshot opzionale (file locale)
            if os.environ.get("SAVE_SNAPSHOTS", "").lower() == "true":
                self._save_snapshot()

            # Salvataggio remoto ogni 100 tick.
            # In locale JSONBIN_KEY non è configurato, save_to_remote() non fa nulla.
            # In produzione salva lo snapshot su JSONBin per sopravvivere ai riavvii di Render.
            if state.current_tick % 100 == 0:
                state.save_to_remote()

            return summary

    def run_n_ticks(self, n: int) -> List[dict]:
        """
        Esegue N tick consecutivi.

        Args:
            n: numero di tick da eseguire (>= 1).

        Returns:
            Lista di tick summary, uno per tick.
        """
        return [self.run_tick() for _ in range(n)]

    def start_auto_tick(self, interval_seconds: float = 2.0) -> None:
        """
        Avvia un loop in background che esegue run_tick() ogni interval_seconds.

        Se il loop è già in esecuzione non ne avvia un secondo.
        Il thread è daemon: si chiude automaticamente all'uscita del processo.

        Args:
            interval_seconds: intervallo tra tick automatici (default 2.0 s).
        """
        if self._auto_thread is not None and self._auto_thread.is_alive():
            logger.info("Auto-tick già in esecuzione — ignorato.")
            return

        self._stop_event.clear()

        def _loop() -> None:
            logger.info("Auto-tick avviato (intervallo %.1f s).", interval_seconds)
            while not self._stop_event.is_set():
                try:
                    self.run_tick()
                except Exception as exc:
                    logger.error("Errore durante auto-tick: %s", exc)
                self._stop_event.wait(timeout=interval_seconds)
            logger.info("Auto-tick fermato.")

        self._auto_thread = threading.Thread(target=_loop, daemon=True, name="auto-tick")
        self._auto_thread.start()

    def stop_auto_tick(self) -> None:
        """
        Ferma il loop automatico.

        Segnala l'evento di stop e attende la terminazione del thread (max 5 s).
        """
        self._stop_event.set()
        if self._auto_thread is not None:
            self._auto_thread.join(timeout=5.0)
            self._auto_thread = None

    def is_auto_running(self) -> bool:
        """
        Restituisce True se il loop automatico è attivo.

        Returns:
            bool: True se il thread è vivo e il segnale di stop non è stato inviato.
        """
        return (
            self._auto_thread is not None
            and self._auto_thread.is_alive()
            and not self._stop_event.is_set()
        )

    def get_tick_log(self, last_n: int = 10) -> List[dict]:
        """
        Restituisce i summary degli ultimi N tick eseguiti.

        Il log è mantenuto in memoria come deque con maxlen=1000: i tick
        più vecchi vengono scartati automaticamente quando il limite è raggiunto.

        Args:
            last_n: numero di tick più recenti da restituire (default 10).

        Returns:
            Lista di tick summary ordinata dal più vecchio al più recente.
        """
        log_list = list(self._tick_log)
        return log_list[-last_n:] if last_n < len(log_list) else log_list

    def _save_snapshot(self) -> None:
        """
        Salva lo stato corrente in data/snapshot_{tick}.json.

        Chiamato internamente da run_tick() se SAVE_SNAPSHOTS=true.
        La directory data/ viene creata se non esiste.
        """
        try:
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            snapshot_path = data_dir / f"snapshot_{state.current_tick}.json"
            with open(snapshot_path, "w", encoding="utf-8") as f:
                json.dump(get_state_snapshot(), f, indent=2, default=str)
        except Exception as exc:
            logger.error("Errore durante il salvataggio dello snapshot: %s", exc)


# ── Istanza globale ────────────────────────────────────────────────────────
# Importabile direttamente: from orchestrator import orchestrator
orchestrator = TickOrchestrator()
