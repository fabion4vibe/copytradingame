# CLAUDE.md
# Istruzioni Operative per Claude Code — Trading Platform Simulator

---

## Ruolo

Sei un agente di sviluppo software incaricato di costruire **Trading Platform Simulator**, una piattaforma didattica locale che simula meccanismi di trading, copy trading e conflitti di interesse in una piattaforma finanziaria.

Il progetto è **esclusivamente didattico**. Non ci sono dati reali, nessun utente reale esposto, nessuna infrastruttura di produzione.

---

## Regole Operative Assolute

1. **Leggi sempre il task sheet prima di scrivere codice.** Ogni modulo ha un file `tasks/TASK_XX_*.md` che definisce esattamente cosa implementare.
2. **Rispetta il contratto API.** Tutti gli endpoint sono definiti in `openapi.yaml`. Non aggiungere endpoint non previsti senza segnalarlo.
3. **Rispetta l'ordine del TASK_GRAPH.md.** Le dipendenze tra moduli sono esplicite. Non anticipare moduli che dipendono da altri non ancora completati.
4. **Stato globale in memoria tramite `state.py`.** Nessun database. Nessuna scrittura su file se non esplicitamente richiesta nel task.
5. **Un file, una responsabilità.** Non mettere logica di dominio nei router. I router chiamano i moduli, non implementano logica.
6. **Nessuna libreria non prevista** senza approvazione. Le dipendenze approvate sono elencate sotto.
7. **Ogni funzione pubblica ha una docstring.** Il progetto è didattico: il codice deve essere leggibile e spiegabile.
8. **Scrivi i test solo se il task lo richiede esplicitamente.** Altrimenti non generarli.
9. **Segnala ambiguità prima di procedere.** Se un task è ambiguo su un punto non critico, fai un'assunzione ragionevole e documentala con un commento `# ASSUMPTION:`.
10. **Non refactorare moduli già completati** a meno che un task successivo lo richieda esplicitamente.

---

## Stack Tecnologico Approvato

### Backend
```
python >= 3.11
fastapi
uvicorn[standard]
numpy
pydantic >= 2.0
```

### Frontend
```
react 18
vite
typescript
recharts
axios
tailwindcss
```

Nessuna altra dipendenza senza approvazione esplicita.

---

## Struttura Directory Attesa

```
/
├── CLAUDE.md               ← questo file
├── PROJECT_SPEC.md
├── ARCHITECTURE.md
├── TASK_GRAPH.md
├── openapi.yaml
├── tasks/
│   ├── TASK_01_state.md
│   ├── TASK_02_market_simulator.md
│   ├── TASK_03_retail_trader.md
│   ├── TASK_04_professional_trader.md
│   ├── TASK_05_copy_engine.md
│   ├── TASK_06_algorithm_engine.md
│   ├── TASK_07_api_routers.md
│   ├── TASK_08_orchestrator.md
│   ├── TASK_09_frontend_setup.md
│   ├── TASK_10_frontend_retail.md
│   └── TASK_11_frontend_manager.md
├── backend/
│   ├── main.py
│   ├── state.py
│   ├── market/
│   ├── traders/
│   ├── algorithm/
│   ├── manager/
│   └── orchestrator.py
├── frontend/
│   └── src/
└── start.sh
```

---

## Convenzioni di Codice

### Python
- Classi in `PascalCase`, funzioni e variabili in `snake_case`
- Modelli Pydantic per tutti i tipi di input/output API
- Nessun `print()` nei moduli di dominio — usa `logging` se necessario
- Eccezioni esplicite con messaggi descrittivi

### TypeScript / React
- Componenti in `PascalCase`, file `.tsx`
- Tipi espliciti, niente `any`
- Chiamate API centralizzate in `src/api/`
- Nessun fetch diretto nei componenti

---

## Come Procedere per Ogni Task

```
1. Crea il branch: git checkout -b task/XX-<nome> develop
2. Leggi tasks/TASK_XX_*.md
3. Verifica le dipendenze indicate nel task (moduli già completati)
4. Implementa esattamente quanto richiesto, né più né meno
5. Verifica che gli endpoint generati corrispondano a openapi.yaml
6. Aggiungi docstring a ogni funzione/classe pubblica
7. Segnala con commento # TODO: qualsiasi cosa rimasta intenzionalmente incompleta
8. Esegui la procedura Git post-task (vedi sezione Workflow Git)
```

---

## Comportamento Atteso in Caso di Conflitto

| Situazione | Comportamento |
|---|---|
| Task vs ARCHITECTURE.md | Il task sheet ha priorità |
| Task vs openapi.yaml (endpoint) | openapi.yaml ha priorità |
| Ambiguità nel task | Assunzione ragionevole + commento `# ASSUMPTION:` |
| Dipendenza mancante | Blocca e segnala prima di procedere |
| Funzionalità non specificata | Non implementarla, segnalala come `# TODO:` |

---

## Finalità Didattica — Priorità di Progetto

Il destinatario principale di questo progetto **non è lo sviluppatore che legge il codice**, ma **l'utente che usa la piattaforma**. Un utente che non sa nulla di trading, copy trading o conflitti di interesse, e che deve capire questi meccanismi interagendoci direttamente.

### Cosa significa concretamente

L'interfaccia è il prodotto didattico. Il codice è il mezzo, non il fine.

Ogni volta che implementi un componente frontend, chiediti: **un utente senza background finanziario capisce cosa sta vedendo e perché è importante?** Se la risposta è no, il componente è incompleto indipendentemente dalla correttezza tecnica.

### Meccanismi da rendere visibili all'utente

| Meccanismo | Deve essere visibile come |
|---|---|
| Il trader professionista è controllato dalla piattaforma | Badge di fase, log dei cambi di fase con spiegazione |
| La fase C danneggia deliberatamente i follower | Warning esplicito prima di avviare copy, alert durante la fase C |
| La piattaforma guadagna dalle perdite retail | Grafico affiancato: perdita retail vs guadagno piattaforma |
| Il professionista viene compensato anche se perde | Colonna "Bonus" visibile accanto al PnL personale |
| L'effetto gregge amplifica il rischio | Indicatore visivo del capitale esposto aggregato |

### Regola per il layer didattico

Il task TASK_12 definisce il layer didattico trasversale (pannelli informativi, tooltip, guide inline, comparatori). **TASK_12 ha priorità su qualsiasi scelta estetica** nei componenti frontend. Se un componente di TASK_10 o TASK_11 deve essere modificato per integrare il layer didattico, fallo senza esitazione.

### Su commenti e docstring

Le docstring restano obbligatorie, ma il loro scopo primario è la manutenibilità del codice, non la didattica. La didattica vive nell'UI, non nei commenti.

---

## Workflow Git

### Configurazione Iniziale

Il repository remoto sarà indicato dall'utente. Prima di iniziare qualsiasi task:

```bash
git remote -v
git checkout develop && git pull origin develop
```

Se `origin` non è configurato: **blocca e chiedi l'URL all'utente.**
Se `develop` non esiste: `git checkout -b develop && git push -u origin develop`

---

### Struttura Branch

```
main
  └─ develop
       ├─ task/01-state
       ├─ task/02-market-simulator
       ├─ task/03-retail-trader
       ├─ task/04-professional-trader
       ├─ task/05-copy-engine
       ├─ task/06-algorithm-engine
       ├─ task/07-api-routers
       ├─ task/08-orchestrator
       ├─ task/09-frontend-setup
       ├─ task/10-frontend-retail
       ├─ task/11-frontend-manager
       └─ task/12-didactic-layer
```

Ogni task ha il suo branch, creato da `develop` e mergiato su `develop` al completamento. Mai lavorare direttamente su `main` o `develop`.

---

### Procedura per Ogni Task

```bash
# INIZIO
git checkout develop && git pull origin develop
git checkout -b task/XX-<nome>

# ... sviluppo ...

# FINE
git add <file_prodotti>
git commit -m "feat(<scope>): <descrizione>"
git push origin task/XX-<nome>

# Merge su develop
git checkout develop
git merge task/XX-<nome> --no-ff -m "feat: merge task/XX-<nome> into develop"

# Log avanzamento
git add TASK_GRAPH.md
git commit -m "chore: mark TASK_XX as complete in TASK_GRAPH"
git push origin develop
```

---

### Formato Commit (Conventional Commits)

```
<tipo>(<scope>): <descrizione in inglese>
```

Tipi: `feat` / `fix` / `refactor` / `chore` / `docs`
Scope: `state` / `market` / `retail` / `professional` / `copy` / `algorithm` / `api` / `orchestrator` / `frontend` / `didactic`

---

### Milestone → Merge su Main

| Milestone | Task | Tag |
|-----------|------|-----|
| M1 — Backend Core | TASK_01–05 | `v0.1.0` |
| M2 — Backend Completo | TASK_06–08 | `v0.2.0` |
| M3 — MVP Completo | TASK_09–12 | `v1.0.0` |

```bash
git checkout develop && git pull origin develop
git checkout main && git pull origin main
git merge develop --no-ff -m "chore: merge develop into main — Milestone MX (vX.X.0)"
git tag -a vX.X.0 -m "Milestone MX: <descrizione>"
git push origin main && git push origin --tags
git checkout develop
```

---

### Setup Iniziale Repository (Solo Prima Volta)

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.venv/
venv/
node_modules/
dist/
.vite/
data/snapshot_*.json
.env
.env.local
.DS_Store
Thumbs.db
EOF

git add .gitignore CLAUDE.md PROJECT_SPEC.md ARCHITECTURE.md TASK_GRAPH.md openapi.yaml tasks/
git commit -m "chore: initial project setup"
git push origin develop
```

---

### Gestione Errori

| Situazione | Azione |
|---|---|
| push rigettato | `git pull --rebase origin develop` poi ripush |
| Conflitto su TASK_GRAPH.md | Mantieni versione con più task completati |
| origin non configurato | Blocca, chiedi URL all'utente |
| Commit accidentale su main | Segnala, non forzare push senza istruzioni |
