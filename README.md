# Trading Platform Simulator

Piattaforma didattica locale che simula meccanismi di **copy trading** e **conflitti di interesse** in una piattaforma finanziaria. Nessun dato reale, nessun utente reale.

**Demo live:** https://fabion4vibe.github.io/copytradingame/

---

## Indice

- [Requisiti](#requisiti)
- [Avvio in locale](#avvio-in-locale)
- [Verifica che tutto funzioni](#verifica-che-tutto-funzioni)
- [Deploy su GitHub Pages + Render](#deploy-su-github-pages--render)
- [Struttura del progetto](#struttura-del-progetto)

---

## Requisiti

| Strumento | Versione minima |
|---|---|
| Python | 3.11 |
| Node.js | 18 |
| npm | 9 |

---

## Avvio in locale

### 1 — Backend (FastAPI)

```bash
cd backend

# Prima volta: crea virtualenv e installa dipendenze
python -m venv .venv

# Attiva il virtualenv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt

# Avvia il server
uvicorn main:app --reload --port 8000
```

Il backend sarà disponibile su **http://localhost:8000**

### 2 — Frontend (Vite + React)

In un secondo terminale:

```bash
cd frontend

# Prima volta
npm install

npm run dev
```

Il frontend sarà disponibile su **http://localhost:5173**

### Avvio rapido (macOS / Linux)

In alternativa, dalla root del progetto:

```bash
bash start.sh
```

Avvia backend e frontend in parallelo. Premi `Ctrl+C` per fermare entrambi.

---

## Verifica che tutto funzioni

### Backend

Apri nel browser: **http://localhost:8000/docs**

Verifica che siano presenti gli endpoint:
- `GET /api/v1/market/assets` — lista asset di mercato
- `GET /api/v1/retail/traders` — lista trader retail
- `GET /api/v1/professional/traders` — lista professionisti
- `GET /api/v1/manager/overview` — panoramica piattaforma
- `POST /api/v1/orchestrator/tick` — avanza di un tick

Test rapido da terminale (con il backend attivo):

```bash
curl http://localhost:8000/api/v1/market/assets
# Deve restituire un array JSON con gli asset SIM-A...SIM-E
```

### Frontend

Apri **http://localhost:5173** e verifica:

1. **Ruolo Retail** — seleziona un trader dall'elenco, esegui un trade manuale, avanza qualche tick con il controller in alto
2. **Ruolo Manager** — switcha al ruolo Manager, verifica che il grafico PnL si aggiorni, prova a forzare una fase su un trader professionista
3. **Didattica** — il banner arancione in cima deve essere sempre visibile; i tooltip ⓘ sui KPI devono aprirsi al click

---

## Deploy su GitHub Pages + Render

### Architettura di produzione

```
GitHub Pages  ──→  frontend (build statico)
      │
      │ API calls (HTTPS)
      ▼
    Render  ──→  backend (FastAPI su uvicorn)
      │
      │ persistenza opzionale
      ▼
   JSONBin.io  ──→  snapshot stato simulazione
```

---

### Deploy backend su Render

1. Vai su [render.com](https://render.com) → **New → Web Service**
2. Collega il repository GitHub
3. Configura il servizio:

| Campo | Valore |
|---|---|
| Root Directory | `backend` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Instance Type | Free |

4. Aggiungi le variabili d'ambiente (**Environment → Add Environment Variable**):

| Variabile | Valore |
|---|---|
| `JSONBIN_KEY` | Master key da [jsonbin.io](https://jsonbin.io) → Account → API Keys |
| `JSONBIN_BIN_ID` | ID del bin creato su JSONBin (usato per la persistenza dello stato) |

> Se non vuoi la persistenza, ometti entrambe le variabili: la simulazione partirà da zero ad ogni riavvio del servizio.

5. Clicca **Create Web Service** e attendi il primo deploy (~2-3 minuti)
6. Copia l'URL assegnato (es. `https://copytradingame-api.onrender.com`)

**Verifica:** `https://<tuo-url-render>.onrender.com/docs` deve mostrare la Swagger UI.

---

### Deploy frontend su GitHub Pages

Il deploy avviene automaticamente tramite GitHub Actions ad ogni push su `main`.

#### Prima configurazione (una tantum)

**1. Abilita GitHub Pages**

GitHub → repo → **Settings → Pages → Source → GitHub Actions**

**2. Imposta la variabile `VITE_API_URL`**

GitHub → repo → **Settings → Secrets and variables → Actions → Variables → New repository variable**

| Name | Value |
|---|---|
| `VITE_API_URL` | `https://<tuo-url-render>.onrender.com` |

**3. Ri-esegui il workflow**

GitHub → repo → **Actions → Deploy Frontend to GitHub Pages → Run workflow**

Dopo ~30 secondi il frontend è live su:
`https://<tuo-username>.github.io/copytradingame/`

#### Come funziona il workflow

Il file `.github/workflows/deploy-frontend.yml`:
- si attiva ad ogni push su `main`
- esegue `npm ci` + `npm run build` nella cartella `frontend/`
- inietta `VITE_API_URL` come variabile d'ambiente al build time
- pubblica `frontend/dist/` su GitHub Pages

---

### Configurazione JSONBin (persistenza opzionale)

JSONBin.io è un servizio gratuito che salva lo stato della simulazione tra un riavvio e l'altro del backend su Render (il free tier di Render mette in sleep il servizio dopo 15 minuti di inattività).

1. Registrati su [jsonbin.io](https://jsonbin.io)
2. **API Keys** → copia la **Master Key**
3. **Bins → Create a Bin** → inserisci `{}` come contenuto iniziale → salva
4. Copia l'**ID del Bin** dall'URL o dal pannello
5. Imposta `JSONBIN_KEY` e `JSONBIN_BIN_ID` come variabili d'ambiente su Render

Lo stato viene salvato automaticamente ogni 100 tick e ripristinato al riavvio del backend.

---

## Struttura del progetto

```
/
├── backend/
│   ├── main.py              # Entry point FastAPI + lifespan
│   ├── state.py             # Stato globale in memoria (singleton)
│   ├── orchestrator.py      # Coordinamento tick
│   ├── schemas.py           # Modelli Pydantic I/O
│   ├── requirements.txt
│   ├── market/              # Simulatore prezzi GBM (5 asset: SIM-A…SIM-E)
│   ├── traders/             # retail.py, professional.py, copy_engine.py
│   ├── algorithm/           # scorer.py, recommender.py
│   └── manager/             # Router dashboard gestore
├── frontend/
│   └── src/
│       ├── views/
│       │   ├── retail/      # Dashboard trader retail
│       │   └── manager/     # Dashboard gestore piattaforma
│       ├── didactic/        # Layer didattico (spiegazioni, tooltip, guide)
│       ├── api/             # Chiamate API centralizzate
│       └── types/           # Tipi TypeScript condivisi
├── tasks/                   # Task sheet di sviluppo (TASK_01…TASK_13)
├── .github/workflows/       # GitHub Actions (deploy frontend)
├── openapi.yaml             # Contratto API
├── ARCHITECTURE.md
├── TASK_GRAPH.md
└── start.sh                 # Avvio rapido locale (bash)
```
