# TASK_GRAPH.md
# Ordine di Esecuzione Task — Trading Platform Simulator

---

## Grafo delle Dipendenze

```
TASK_01_state
    │
    ├──► TASK_02_market_simulator
    │         │
    │         ├──► TASK_03_retail_trader
    │         │         │
    │         │         └──► TASK_05_copy_engine ◄──┐
    │         │                    │                 │
    │         └──► TASK_04_professional_trader ──────┘
    │                    │
    │                    └──► TASK_06_algorithm_engine
    │
    └──► TASK_07_api_routers (dipende da 02+03+04+05+06)
              │
              └──► TASK_08_orchestrator
                        │
                        └──► TASK_09_frontend_setup
                                  │
                                  ├──► TASK_10_frontend_retail ──────┐
                                  └──► TASK_11_frontend_manager ─────┤
                                                                      │
                                                              TASK_12_didactic_layer
```

---

## Tabella Esecuzione

| Ordine | Task ID | Nome | Branch | Dipende da | Output |
|--------|---------|------|--------|------------|--------|
| 1 | TASK_01 | Stato Globale | `task/01-state` | — | `backend/state.py` |
| 2 | TASK_02 | Simulatore di Mercato | `task/02-market-simulator` | TASK_01 | `backend/market/` |
| 3 | TASK_03 | Retail Trader | `task/03-retail-trader` | TASK_01, TASK_02 | `backend/traders/retail.py` |
| 4 | TASK_04 | Professional Trader + FSM | `task/04-professional-trader` | TASK_01, TASK_02 | `backend/traders/professional.py` |
| 5 | TASK_05 | Copy Engine | `task/05-copy-engine` | TASK_03, TASK_04 | `backend/traders/copy_engine.py` |
| 6 | TASK_06 | Algorithm Engine | `task/06-algorithm-engine` | TASK_03, TASK_04, TASK_05 | `backend/algorithm/` |
| 7 | TASK_07 | API Routers + main.py | `task/07-api-routers` | TASK_02–06 | `backend/*/router.py`, `backend/main.py` |
| 8 | TASK_08 | Orchestratore Tick | `task/08-orchestrator` | TASK_07 | `backend/orchestrator.py` |
| 9 | TASK_09 | Frontend Setup | `task/09-frontend-setup` | TASK_07 | `frontend/` scaffold + `src/api/` |
| 10 | TASK_10 | Dashboard Retail | `task/10-frontend-retail` | TASK_09 | `frontend/src/views/retail/` |
| 11 | TASK_11 | Dashboard Gestore | `task/11-frontend-manager` | TASK_09 | `frontend/src/views/manager/` |
| 12 | TASK_12 | Layer Didattico | `task/12-didactic-layer` | TASK_10, TASK_11 | `frontend/src/didactic/` |

---

## Regole di Precedenza

- **Non iniziare un task** prima che tutti i task da cui dipende siano marcati come ✅ completati.
- I task 03 e 04 possono essere eseguiti **in parallelo** (nessuna dipendenza reciproca), ognuno sul proprio branch.
- I task 10 e 11 possono essere eseguiti **in parallelo**, ognuno sul proprio branch.
- TASK_12 inizia solo dopo che **sia TASK_10 che TASK_11** sono completati e mergiati su `develop`.
- Ogni branch viene creato da `develop` e mergiato su `develop` al completamento (vedere `CLAUDE.md` sezione Workflow Git).

---

## Milestone

| Milestone | Task inclusi | Branch sorgente | Tag |
|-----------|-------------|-----------------|-----|
| **M1 — Backend Core** | TASK_01–05 | `develop` | `v0.1.0` |
| **M2 — Backend Completo** | TASK_06–08 | `develop` | `v0.2.0` |
| **M3 — MVP Completo** | TASK_09–12 | `develop` | `v1.0.0` |

Il merge su `main` avviene **solo** al completamento di ogni milestone. Vedere `CLAUDE.md` per la procedura esatta.

---

## Stato di Avanzamento

Aggiorna questa sezione man mano che i task vengono completati.

| Task | Branch | Stato | Note |
|------|--------|-------|------|
| TASK_01 | `task/01-state` | ✅ Completato | Merged direttamente su develop |
| TASK_02 | `task/02-market-simulator` | ✅ Completato | |
| TASK_03 | `task/03-retail-trader` | ✅ Completato | |
| TASK_04 | `task/04-professional-trader` | ✅ Completato | |
| TASK_05 | `task/05-copy-engine` | ✅ Completato | |
| TASK_06 | `task/06-algorithm-engine` | ✅ Completato | |
| TASK_07 | `task/07-api-routers` | ✅ Completato | |
| TASK_08 | `task/08-orchestrator` | ✅ Completato | |
| TASK_09 | `task/09-frontend-setup` | ⬜ Non iniziato | |
| TASK_10 | `task/10-frontend-retail` | ⬜ Non iniziato | |
| TASK_11 | `task/11-frontend-manager` | ⬜ Non iniziato | |
| TASK_12 | `task/12-didactic-layer` | ⬜ Non iniziato | |

Legend: ⬜ Non iniziato | 🔄 In corso | ✅ Completato | ❌ Bloccato
