# TASK_11 — Dashboard Gestore

**File di output**: `frontend/src/views/manager/`
**Dipende da**: TASK_09
**Parallelo a**: TASK_10

---

## Obiettivo

Implementare la dashboard del gestore della piattaforma: visione aggregata del sistema, controllo diretto dei trader professionisti, pannello algoritmico e monitoraggio del profitto della piattaforma.

---

## File da Creare

```
frontend/src/views/manager/
├── ManagerDashboard.tsx       # Layout principale vista gestore
├── PlatformKpiPanel.tsx       # KPI globali in tempo reale
├── TraderControlPanel.tsx     # Controllo trader professionisti
├── AlgorithmPanel.tsx         # Raccomandazioni e simulazione scenari
├── CopyFlowPanel.tsx          # Flusso copy trading aggregato
└── PlatformPnLChart.tsx       # Grafico evoluzione PnL piattaforma
```

---

## `ManagerDashboard.tsx`

Layout:

```
┌─────────────────────────────────────────────────┐
│  PlatformKpiPanel (banner orizzontale)          │
├──────────────────────┬──────────────────────────┤
│  TraderControlPanel  │  AlgorithmPanel          │
│                      │                          │
├──────────────────────┴──────────────────────────┤
│  CopyFlowPanel          │  PlatformPnLChart     │
└─────────────────────────────────────────────────┘
```

---

## `PlatformKpiPanel.tsx`

Banner con card metriche:

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ PnL Netto    │ │ Capital      │ │ % in Copy    │ │ Retail in    │
│ Piattaforma  │ │ Retail Tot.  │ │ Trading      │ │ Perdita      │
│ +€12,340     │ │ €145,200     │ │ 68%          │ │ 7/10         │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

- Aggiornamento ogni tick
- PnL in verde/rosso
- Card "Retail in Perdita" con sfondo rosso se > 50%

---

## `TraderControlPanel.tsx`

Una card per ogni trader professionista:

```
┌─────────────────────────────────────────────────┐
│ 🧑‍💼 Alpha Trader                               │
│ Fase: 🟡 FOLLOWER_GROWTH                        │
│ Follower: 14  |  Capitale esposto: €32,100      │
│ PnL personale: +€840  |  Bonus: €0             │
│                                                 │
│ [ → Fase A ] [ → Fase B ] [ → Fase C ⚠ ]       │
│                                                 │
│ Strategia:                                      │
│   EV: +0.008  Risk: 0.3  Freq: 0.6             │
└─────────────────────────────────────────────────┘
```

- Pulsanti cambio fase chiamano `professionalApi.changePhase()`
- Il pulsante "→ Fase C" ha colore rosso con tooltip:
  ```
  "Attivazione Monetizzazione: il trader adotterà strategie con EV negativo.
   I follower subiranno perdite. La piattaforma riceve il differenziale."
  ```
- Dopo il cambio fase, aggiorna la card in tempo reale

---

## `AlgorithmPanel.tsx`

Due sezioni:

**Raccomandazioni algoritmiche**:
Lista di raccomandazioni da `algorithmApi.getRecommendations()`:

```
🔴 ALTA PRIORITÀ — Alpha Trader
   Azione suggerita: TRANSITION_TO_MONETIZATION
   Motivo: 14 follower attivi, €32,100 esposti. Score: 0.87
   Guadagno atteso piattaforma: +€4,200
   Rischio: ALTO  |  Confidenza: 84%
   [ Applica ] [ Ignora ]
```

- "Applica" esegue la transizione automaticamente
- Badge colorati per livello rischio (verde/giallo/rosso)

**Simulazione scenario**:
Form per simulare l'effetto di una transizione:
```
Trader: [ Alpha ▼ ]  Scenario: [ TRANSITION_TO_MONETIZATION ▼ ]  N tick: [ 10 ]
[ Simula ]

Risultato:
  Perdita retail attesa: -€3,800
  Bonus da pagare: -€2,000
  Guadagno netto piattaforma: +€1,800
  Intervallo confidenza: [+€1,200 / +€2,400]
```

---

## `CopyFlowPanel.tsx`

Tabella aggregata del copy trading:

| Trader | Fase | Follower | Capitale Esposto | % Cap. Piattaforma |
|--------|------|----------|------------------|--------------------|
| Alpha  | 🟡 B | 14 | €32,100 | 22% |
| Beta   | 🔴 C | 8  | €18,400 | 13% |

- Barra di progresso per "Capitale Esposto" relativo al totale
- Fase C evidenziata in rosso

---

## `PlatformPnLChart.tsx`

Grafico a linea (recharts) con:
- Asse X: tick
- Asse Y: PnL cumulativo piattaforma
- Linea verde per PnL netto
- Linea blu per commissioni
- Linea rossa per bonus pagati
- Legenda esplicativa

---

## Layer Didattico Manager (Requisiti da TASK_12)

Questi elementi vengono definiti in dettaglio in TASK_12 ma devono essere **predisposti** già in questo task come slot o placeholder.

### Slot da predisporre

**TraderControlPanel** — sopra i pulsanti di cambio fase, riserva `<PhaseExplainer phase={currentPhase} />`: un componente che spiega cosa sta facendo il trader in questa fase, in linguaggio non tecnico. Implementazione in TASK_12.

**TraderControlPanel** — il pulsante "→ Fase C" deve includere già ora un **dialog di conferma** con testo esplicativo completo (non solo "Sei sicuro?"):
```
Stai per attivare la Fase di Monetizzazione per [nome trader].

In questa fase:
• Il trader adotterà operazioni con rendimento atteso negativo
• I [N] follower che lo copiano subiranno perdite proporzionali
• Il trader riceverà un bonus fisso per ogni tick indipendentemente dal suo PnL
• La piattaforma registrerà il differenziale come guadagno

Capitale retail attualmente esposto: €XX.XXX
Guadagno piattaforma stimato (10 tick): €X.XXX

[ Annulla ]  [ Confermo — Attiva Fase C ]
```

**AlgorithmPanel** — ogni raccomandazione deve avere un link `[Spiega questo]` che apre `<RecommendationExplainer />`. Slot da predisporre, implementazione in TASK_12.

**PlatformKpiPanel** — aggiungi un'icona ⓘ accanto a ogni metrica. Al click apre `<MetricExplainer metricId="..." />`. Slot da predisporre, implementazione in TASK_12.

### Pannello "Come funziona la piattaforma" (nuovo elemento)

Aggiungi un pulsante fisso `[? Come funziona]` nell'header della dashboard manager. Apre un pannello laterale `<HowItWorks />` (placeholder). Sarà implementato in TASK_12 con la spiegazione completa del modello economico.

---

## Nota sul Tono della Dashboard Gestore

La dashboard del gestore non deve essere neutrale. Deve rendere **esplicito il conflitto di interesse** in ogni elemento. Non usare linguaggio eufemistico:

| Non scrivere | Scrivi invece |
|---|---|
| "Ottimizza la strategia" | "Attiva perdite per i follower" |
| "Fase avanzata" | "Fase di monetizzazione (Fase C)" |
| "Aggiorna parametri" | "Aumenta l'esposizione al rischio dei retail" |

Questo è il punto centrale del progetto didattico. Il gestore deve vedere esattamente cosa sta facendo.

---

## Criteri di Completamento

- [ ] `ManagerDashboard.tsx` con layout completo
- [ ] `PlatformKpiPanel.tsx` con 4 card metriche e icone ⓘ placeholder
- [ ] `TraderControlPanel.tsx` con card per ogni trader e pulsanti fase
- [ ] Dialog di conferma fase C con testo esplicativo completo e dati live
- [ ] `AlgorithmPanel.tsx` con raccomandazioni, link `[Spiega questo]` placeholder, e simulazione
- [ ] `CopyFlowPanel.tsx` con tabella aggregata
- [ ] `PlatformPnLChart.tsx` con 3 linee
- [ ] Pulsante `[? Come funziona]` con slot `<HowItWorks />`
- [ ] Placeholder `<PhaseExplainer />` in TraderControlPanel
- [ ] Placeholder `<RecommendationExplainer />` in AlgorithmPanel
- [ ] Linguaggio non eufemistico in tutta la dashboard
- [ ] Aggiornamento automatico a ogni tick
