# TASK_12 — Layer Didattico Trasversale

**File di output**: `frontend/src/didactic/`
**Dipende da**: TASK_10, TASK_11 (slot già predisposti)
**Branch**: `task/12-didactic-layer`
**Milestone**: M3

---

## Obiettivo

Implementare il layer didattico dell'interfaccia: l'insieme di componenti, pannelli e meccanismi che trasformano la piattaforma da uno strumento di simulazione a uno strumento di comprensione. L'utente target non ha background finanziario. Al termine dell'interazione con la piattaforma deve essere in grado di spiegare a voce il modello di business simulato.

---

## Struttura Directory

```
frontend/src/didactic/
├── components/
│   ├── MechanismExplainer.tsx      # Spiegazione inline di un meccanismo specifico
│   ├── PhaseGuide.tsx              # Guida alle tre fasi del trader professionista
│   ├── PhaseExplainer.tsx          # Descrizione della fase corrente (per il gestore)
│   ├── RecommendationExplainer.tsx # Spiega perché l'algoritmo raccomanda un'azione
│   ├── MetricExplainer.tsx         # Spiega cosa significa una metrica della dashboard
│   ├── RetailVsPlatformSnapshot.tsx # Confronto PnL retail vs guadagno piattaforma
│   ├── HowItWorks.tsx              # Pannello laterale "Come funziona la piattaforma"
│   └── ConflictOfInterestBanner.tsx # Banner fisso sul conflitto di interesse
├── content/
│   ├── mechanisms.ts               # Testi esplicativi per MechanismExplainer
│   ├── phases.ts                   # Testi per PhaseGuide e PhaseExplainer
│   ├── metrics.ts                  # Testi per MetricExplainer
│   └── howItWorks.ts               # Contenuto del pannello HowItWorks
└── index.ts                        # Export centralizzato
```

---

## Componenti da Implementare

### `MechanismExplainer.tsx`

Pannello collassabile che spiega un meccanismo specifico in linguaggio semplice.

Props:
```typescript
interface MechanismExplainerProps {
  id: 'portfolio-pnl' | 'copy-trading' | 'platform-profit' | 'phase-cycle' | 'bonus-system'
  defaultOpen?: boolean
}
```

Ogni `id` corrisponde a un testo in `content/mechanisms.ts`. Struttura del testo:

```typescript
// mechanisms.ts
export const mechanisms = {
  'portfolio-pnl': {
    title: 'Cos\'è il PnL?',
    body: `PnL sta per "Profit and Loss" — guadagno o perdita.
           Il tuo PnL mostra quanto hai guadagnato o perso rispetto
           al capitale iniziale. Un PnL negativo significa che il valore
           attuale del tuo portafoglio è inferiore a quello con cui hai iniziato.`,
    keyPoint: 'Il PnL non realizzato cambia ad ogni tick. Diventa reale solo quando vendi.'
  },
  'copy-trading': {
    title: 'Come funziona il copy trading?',
    body: `Quando copi un trader, ogni sua operazione viene replicata
           automaticamente sul tuo portafoglio in proporzione alla
           percentuale di allocazione che hai scelto.
           Se il trader compra, compri anche tu. Se perde, perdi anche tu.`,
    keyPoint: 'Non puoi intervenire sulle singole operazioni copiate. Puoi solo smettere di copiare.'
  },
  'platform-profit': {
    title: 'Come guadagna la piattaforma?',
    body: `In questa simulazione la piattaforma guadagna principalmente
           dalle perdite dei trader retail. Quando un retail perde €100,
           quella somma viene registrata come guadagno della piattaforma.
           Questo crea un incentivo strutturale: la piattaforma è più
           redditizia quando i suoi utenti perdono.`,
    keyPoint: 'Questo è il conflitto di interesse al centro di questo progetto didattico.'
  },
  'phase-cycle': {
    title: 'Le tre fasi del trader professionista',
    body: `I trader professionisti passano attraverso tre fasi controllate dalla piattaforma:
           Fase A (Costruzione reputazione): ottimi risultati, pochi follower.
           Fase B (Attrazione follower): buoni risultati, crescita dei copiatori.
           Fase C (Monetizzazione): operazioni deliberatamente svantaggiose.
           I follower subiscono le perdite. Il trader riceve un bonus.`,
    keyPoint: 'I trader professionisti non sono indipendenti. Sono strumenti della piattaforma.'
  },
  'bonus-system': {
    title: 'Il sistema di bonus',
    body: `In fase C, il trader professionista riceve un bonus fisso per ogni tick,
           indipendentemente dal suo PnL personale. Questo significa che può perdere
           soldi nelle sue operazioni ma essere comunque compensato.
           Il bonus viene pagato dalla piattaforma, che però recupera molto di più
           attraverso le perdite dei retail che lo copiano.`,
    keyPoint: 'Il professionista è incentivato a perdere deliberatamente perché viene comunque pagato.'
  }
}
```

Stile visivo: bordo sinistro colorato (blu per informativo, arancione per allerta, rosso per conflitto di interesse).

---

### `PhaseGuide.tsx`

Componente collassabile che mostra le tre fasi come una timeline visiva. Posizionato sopra la lista professionisti nel CopyTradingPanel retail.

```
[Fase A] ──────► [Fase B] ──────► [Fase C]
Costruisce       Attrae            Monetizza
reputazione      follower          a loro spese

▼ Leggi di più
```

Stato: aperto di default alla prima visita, poi collassato (salvato in React state locale, non storage).

---

### `PhaseExplainer.tsx`

Utilizzato nella dashboard gestore accanto alla card di ogni trader. Mostra una descrizione della fase attuale orientata al gestore.

Props: `{ phase: TraderPhase, followersCount: number, capitalExposed: number }`

Contenuto per fase:

- **REPUTATION_BUILD**: *"Il trader sta costruendo credibilità. Le sue operazioni hanno rendimento atteso positivo. Obiettivo: raggiungere [N] follower per passare alla fase successiva."*
- **FOLLOWER_GROWTH**: *"Il trader è in fase di crescita. Mantiene buone performance per attrarre più capital. [N] follower, €[X] esposti. Soglia fase C: [N] follower e €[X] esposti."*
- **MONETIZATION**: *"Fase attiva. Il trader sta eseguendo operazioni con rendimento atteso negativo. I [N] follower stanno perdendo capitale. Bonus attivo: €[X] per tick."*

---

### `RecommendationExplainer.tsx`

Pannello che si apre cliccando `[Spiega questo]` su una raccomandazione algoritmica.

Props: `{ recommendation: Recommendation }`

Spiega in linguaggio semplice:
- Perché l'algoritmo ha assegnato quel score
- Cosa significa il livello di rischio
- Cosa succederebbe ai retail se la raccomandazione viene applicata
- Qual è il guadagno atteso per la piattaforma e a spese di chi

Deve contenere sempre questa frase (adattata ai dati reali):
> *"Se questa azione viene applicata, i [N] retail che copiano [nome trader] sono esposti a perdite stimate di €[X] nei prossimi [N] tick. La piattaforma registrerebbe un guadagno netto stimato di €[Y]."*

---

### `MetricExplainer.tsx`

Tooltip espanso per le metriche del `PlatformKpiPanel`. Si apre cliccando ⓘ.

Props: `{ metricId: string }`

Metriche da spiegare (in `content/metrics.ts`):

```typescript
export const metrics = {
  'platform-pnl': {
    label: 'PnL Netto Piattaforma',
    explanation: 'Somma delle perdite nette dei trader retail, al netto dei bonus pagati ai professionisti.',
    formula: 'Perdite retail totali − Bonus pagati'
  },
  'total-retail-capital': {
    label: 'Capitale Retail Totale',
    explanation: 'Somma del valore attuale di tutti i portafogli retail (liquidità + posizioni aperte a prezzi correnti).'
  },
  'copy-penetration': {
    label: '% Capitale in Copy Trading',
    explanation: 'Percentuale del capitale retail totale che è attualmente allocata in relazioni di copy attive. Più è alta, più la piattaforma può influenzare i risultati attraverso i trader professionisti.'
  },
  'retail-losing': {
    label: 'Retail in Perdita',
    explanation: 'Numero di trader retail con PnL totale negativo rispetto al capitale iniziale.'
  }
}
```

---

### `RetailVsPlatformSnapshot.tsx`

Pannello nella dashboard retail che mostra il confronto diretto tra il PnL del retail e il guadagno che la piattaforma ha realizzato "su di lui".

```
┌─────────────────────────────────────────────────────────┐
│  📊 Il tuo impatto sulla piattaforma                    │
│                                                         │
│  Il tuo PnL totale:          -€340                     │
│  Guadagno piattaforma su di te: +€340                  │
│                                                         │
│  Delle tue operazioni in copy:                          │
│  - Operazioni copiate: 12                               │
│  - PnL da copy: -€280 (82% della tua perdita totale)   │
│                                                         │
│  ⓘ Come viene calcolato questo?                         │
└─────────────────────────────────────────────────────────┘
```

I dati provengono dalle API già esistenti (`/retail/traders/{id}/pnl` e `/manager/pnl`). Il calcolo "guadagno piattaforma su di te" è una stima: usa la proporzione del capitale retail dell'utente sul totale per stimare la sua quota del PnL piattaforma.

---

### `HowItWorks.tsx`

Pannello laterale (drawer) accessibile dal pulsante `[? Come funziona]` nella dashboard manager. Spiega l'intero modello economico simulato in formato narrativo, diviso in sezioni:

1. **La piattaforma e i suoi attori** — chi sono retail, professionisti e gestore
2. **Il ciclo di vita del trader professionista** — le tre fasi con esempi numerici
3. **Come guadagna la piattaforma** — formula esplicita con numeri di esempio
4. **Il conflitto di interesse** — perché gli incentivi del gestore e del retail sono opposti
5. **Cosa osservare nella simulazione** — suggerimenti su cosa guardare per vedere il meccanismo in azione

Il contenuto è statico (testo in `content/howItWorks.ts`). Non fa chiamate API.

---

### `ConflictOfInterestBanner.tsx`

Banner fisso in cima a entrambe le dashboard (retail e manager). Non è dismissibile. Testo diverso per ruolo:

**Vista Retail:**
```
⚠️ Stai usando una piattaforma didattica simulata.
I trader professionisti che puoi copiare sono controllati dalla piattaforma.
Le loro strategie possono essere modificate per generare perdite nei tuoi confronti.
```

**Vista Manager:**
```
🏢 Stai osservando la piattaforma dal punto di vista del gestore.
Hai il controllo diretto dei trader professionisti e dei loro comportamenti.
Le tue decisioni influenzano direttamente il capitale dei retail.
```

---

## Integrazione con TASK_10 e TASK_11

Sostituisci i placeholder già predisposti:

| Placeholder | Componente finale |
|---|---|
| `<MechanismExplainer id="portfolio-pnl" />` | Implementato qui |
| `<PhaseGuide />` | Implementato qui |
| `<RetailVsPlatformSnapshot />` | Implementato qui |
| `<PhaseExplainer phase={...} />` | Implementato qui |
| `<RecommendationExplainer recommendation={...} />` | Implementato qui |
| `<MetricExplainer metricId="..." />` | Implementato qui |
| `<HowItWorks />` | Implementato qui |
| `<ConflictOfInterestBanner role="retail|manager" />` | Aggiunto in App.tsx |

---

## Vincoli

- Nessun testo didattico deve essere nascosto dietro più di un click.
- Il banner `ConflictOfInterestBanner` non è dismissibile né minimizzabile.
- I testi in `content/` sono separati dai componenti per facilitare revisioni future senza toccare il codice React.
- Nessuna chiamata API aggiuntiva: usa i dati già caricati dalle dashboard.
- Nessun `any` TypeScript.

---

## Criteri di Completamento

- [ ] `MechanismExplainer` con 5 meccanismi implementati
- [ ] `PhaseGuide` con timeline visiva delle 3 fasi
- [ ] `PhaseExplainer` con testo adattivo per fase corrente
- [ ] `RecommendationExplainer` con stima impatto retail
- [ ] `MetricExplainer` con spiegazioni per le 4 metriche principali
- [ ] `RetailVsPlatformSnapshot` con dati live
- [ ] `HowItWorks` drawer con 5 sezioni di contenuto
- [ ] `ConflictOfInterestBanner` non dismissibile in entrambe le viste
- [ ] Tutti i placeholder di TASK_10 e TASK_11 sostituiti
- [ ] Contenuti testuali separati in `content/*.ts`
- [ ] Nessun `any` TypeScript
