# TASK_10 — Dashboard Retail

**File di output**: `frontend/src/views/retail/`
**Dipende da**: TASK_09
**Parallelo a**: TASK_11

---

## Obiettivo

Implementare la dashboard del trader retail: visione del proprio portafoglio, storico operazioni, gestione copy trading e possibilità di fare trading manuale.

---

## File da Creare

```
frontend/src/views/retail/
├── RetailDashboard.tsx       # Layout principale della vista retail
├── PortfolioPanel.tsx        # Portafoglio e bilancio corrente
├── TradePanel.tsx            # Form per trade manuali
├── CopyTradingPanel.tsx      # Gestione copy: chi copio, start/stop
├── TradeHistoryPanel.tsx     # Storico operazioni
└── RetailSelector.tsx        # Dropdown per scegliere quale retail visualizzare
```

---

## `RetailDashboard.tsx`

Layout a griglia:

```
┌─────────────────────────────────────────────────┐
│  RetailSelector: [ Mario Rossi ▼ ]              │
├──────────────────┬──────────────────────────────┤
│  PortfolioPanel  │  TradePanel                  │
│                  │                              │
├──────────────────┴──────────────────────────────┤
│  CopyTradingPanel                               │
├─────────────────────────────────────────────────┤
│  TradeHistoryPanel                              │
└─────────────────────────────────────────────────┘
```

---

## `PortfolioPanel.tsx`

Mostra:
- **Bilancio disponibile** (cash)
- **Valore portafoglio** (posizioni aperte a prezzi correnti)
- **PnL totale** con colore verde/rosso
- **Posizioni aperte**: tabella con asset, quantità, prezzo medio, valore corrente, PnL non realizzato
- **Grafico**: PnL nel tempo (recharts LineChart, polling ogni tick)

---

## `TradePanel.tsx`

Form per trade manuale:
```
Asset: [ SIM-A ▼ ]
Azione: [ BUY ] [ SELL ]
Quantità: [ _______ ]
Prezzo corrente: 105.30
Totale stimato: 1053.00
[ Esegui Trade ]
```

- Chiama `retailApi.executeTrade(retailId, { asset_id, action, quantity })`
- Mostra errori inline (es. "Balance insufficiente")
- Aggiorna PortfolioPanel dopo esecuzione

---

## `CopyTradingPanel.tsx`

Due sezioni:

**Trader disponibili da copiare**:
Tabella con professionisti disponibili (da `professionalApi.getAll()`):
| Nome | Fase | Follower | PnL Personale | Azione |
|------|------|----------|---------------|--------|
| Alpha | 🟡 FOLLOWER_GROWTH | 12 | +8.2% | [Copia] |

- La fase MONETIZATION è mostrata in **rosso** con badge "⚠ Fase C"
- Il pulsante [Copia] apre un mini-form per scegliere `allocation_pct`

**Trader che sto copiando**:
Lista delle copy relation attive con pulsante [Stop Copy]

---

## `TradeHistoryPanel.tsx`

Tabella paginata (20 per pagina):

| Tick | Asset | Azione | Quantità | Prezzo | PnL Realizzato | Copiato da |
|------|-------|--------|----------|--------|----------------|------------|

- Trade copiati marcati con badge "📋 Copy"
- PnL realizzato colorato verde/rosso
- Filtrabile per: tutto / solo manuali / solo copiati

---

## `RetailSelector.tsx`

Dropdown che elenca tutti i retail disponibili in `state`.
Al cambio selezione, ricarica tutti i pannelli con i dati del nuovo retail.
Il retail "reale" (is_real_user=true) è marcato con badge "👤 Tu".

---

## Nota Didattica — CopyTradingPanel

Quando un professionista è in fase MONETIZATION, mostra un **callout esplicativo**:

```
⚠️ Questo trader è in Fase C (Monetizzazione).
In questa fase la piattaforma ha attivato una strategia non ottimale.
Le operazioni vengono replicate sul tuo portafoglio.
Il trader professionista riceve un bonus indipendentemente dal suo PnL personale.
```

Questo callout è intenzionale e fa parte della natura didattica del progetto.

---

## Layer Didattico Retail (Requisiti da TASK_12)

Questi elementi vengono definiti nel dettaglio in TASK_12 ma devono essere **predisposti** già in questo task come slot vuoti o placeholder, pronti per essere riempiti da TASK_12.

### Slot da predisporre in ogni pannello

**PortfolioPanel** — riserva uno spazio `<MechanismExplainer id="portfolio-pnl" />` sotto il PnL totale. Sarà popolato da TASK_12 con una spiegazione di cosa significa il PnL e come viene calcolato.

**CopyTradingPanel** — prima della lista dei professionisti disponibili, riserva `<PhaseGuide />`: un componente che spiega le tre fasi del ciclo di vita del trader. Deve essere collassabile (aperto di default la prima volta, poi ricordato).

**CopyTradingPanel** — nella card di ogni professionista in fase C, il callout già descritto sopra non è opzionale: è **visibile sempre**, non dietro un tooltip.

**TradeHistoryPanel** — per ogni riga con `is_copy: true`, mostra una nota inline: *"Operazione copiata automaticamente — eseguita perché stai seguendo [nome trader]."*

### Confronto affiancato (nuovo elemento)

Aggiungi in fondo alla dashboard retail un pannello `<RetailVsPlatformSnapshot />` (placeholder):
```
Il tuo PnL: -€340     |     Guadagno piattaforma su di te: +€340
```
Questo pannello sarà implementato in TASK_12 ma lo spazio e il nome del componente devono esistere già qui.

---

## Vincoli

- Aggiornamento dati: ogni volta che il tick avanza (polling su `/market/status`), rieseguire le chiamate ai pannelli.
- Nessun `any` TypeScript.
- Non duplicare la logica di fetch: usare gli hook in `src/hooks/`.

---

## Criteri di Completamento

- [ ] `RetailDashboard.tsx` con layout a griglia
- [ ] `PortfolioPanel.tsx` con posizioni e PnL
- [ ] `TradePanel.tsx` con form funzionante e gestione errori
- [ ] `CopyTradingPanel.tsx` con lista professionisti e copy attive
- [ ] Callout fase C sempre visibile (non tooltip, non collassabile)
- [ ] `TradeHistoryPanel.tsx` con filtri, paginazione e note inline su trade copiati
- [ ] `RetailSelector.tsx` funzionante
- [ ] Aggiornamento automatico a ogni tick
- [ ] Placeholder `<MechanismExplainer />` in PortfolioPanel
- [ ] Placeholder `<PhaseGuide />` in CopyTradingPanel
- [ ] Placeholder `<RetailVsPlatformSnapshot />` in fondo alla dashboard
