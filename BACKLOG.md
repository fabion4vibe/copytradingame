# BACKLOG — Trading Platform Simulator

Idee, miglioramenti e funzionalità future da validare prima di implementare.
Non sono impegni: sono spunti da discutere.

Formato: ogni voce ha una **priorità indicativa** (🔴 alta / 🟡 media / 🟢 bassa),
una **categoria** e una breve descrizione del valore atteso.

---

## Come usare questo file

- Aggiungi idee liberamente, senza filtri
- Prima di implementare qualcosa, spostalo in un `TASK_XX_*.md` formale
- Segna le voci scartate con ~~strikethrough~~ + motivazione, non cancellarle

---

## Funzionalità

| # | Priorità | Voce | Note |
|---|---|---|---|
| B-01 | 🟡 | Modalità replay: riesecuzione step-by-step di una simulazione salvata | Utile per la didattica — mostra l'evoluzione tick per tick |
| B-02 | 🟡 | Export CSV dello storico trade e PnL | Permette analisi esterne (Excel, Python) |
| B-03 | 🟢 | Modalità "turbo": avanza N tick in un colpo solo con barra di progresso | Accelera le demo |
| B-04 | 🔴 | Scenario preconfigurato "truffa classica": 3 fasi forzate in sequenza rapida | Rende immediatamente visibile il ciclo A→B→C senza aspettare |
| B-05 | 🟢 | Grafico storico delle fasi del trader professionista (timeline visiva) | Già c'è `phase_history` nel backend — manca solo il frontend |
| B-06 | 🟡 | Confronto affiancato tra due trader retail (chi copia vs chi non copia) | Rende tangibile l'effetto del copy in Fase C |
| B-07 | 🟢 | Notifica/toast quando un trader entra in Fase C durante la simulazione | Feedback in tempo reale senza dover guardare il pannello manager |

---

## Didattica

| # | Priorità | Voce | Note |
|---|---|---|---|
| B-08 | 🔴 | Quiz finale: domande sul meccanismo appena simulato | Verifica comprensione — 3-5 domande a risposta multipla |
| B-09 | 🟡 | Glossario flottante: definizioni di "copy trading", "fase C", "conflitto di interesse", ecc. | Accessibile da un pulsante fisso, non intrusivo |
| B-10 | 🟢 | Modalità guidata (tutorial): sequenza obbligata di azioni con tooltip esplicativi | Per utenti che non sanno da dove partire |
| B-11 | 🟡 | Indicatore visivo "quanto stai perdendo per colpa della piattaforma" in tempo reale | Rende visceralmente chiaro il conflitto di interesse |

---

## Tecnico / Infrastruttura

| # | Priorità | Voce | Note |
|---|---|---|---|
| B-12 | 🟡 | Render keep-alive: ping periodico per evitare il sleep del free tier | Senza JSONBin lo stato si perde ad ogni sleep |
| B-13 | 🟢 | Aggiungere `pytest` con test smoke sui moduli backend critici (orchestrator, copy_engine) | Attualmente nessun test automatico |
| B-14 | 🟢 | Docker Compose per avvio locale con un solo comando | Elimina la dipendenza da Python/Node installati localmente |
| B-15 | 🟡 | Variabile `SIMULATION_SEED` per rendere la simulazione riproducibile | Utile per demo e per il replay (B-01) |

---

## Internazionalizzazione (i18n)

Questa sezione è pianificata in due fasi operative:

**Fase 1 — TASK_14** *(già formalizzato in `tasks/TASK_14_technical_english.md`)*
Tutto il codice e la documentazione tecnica passa all'inglese.
Il criterio è: *se lo legge uno sviluppatore → inglese; se lo legge l'utente finale → rimane in italiano per ora*.

**Fase 2 — TASK_15** *(da formalizzare)*
Internazionalizzazione dell'interfaccia utente con supporto per tre lingue:

| Locale | Codice | Note |
|---|---|---|
| Italiano | `it` | Lingua di partenza — le stringhe attuali diventano il file base |
| Inglese | `en` | Prima traduzione |
| Sardo | `sc` | Terza lingua — richiederà revisione madrelingua |

| # | Priorità | Voce | Note |
|---|---|---|---|
| B-16 | 🔴 | TASK_14: traduzione tecnica → English | Formalizzato, pronto per esecuzione |
| B-17 | 🔴 | TASK_15: setup react-i18next + lingua `it` (estrazione stringhe UI) | Prerequisito per qualsiasi altra lingua |
| B-18 | 🟡 | TASK_16: aggiunta lingua `en` (traduzione inglese UI) | Dopo TASK_15 |
| B-19 | 🟡 | TASK_17: aggiunta lingua `sc` (traduzione sarda UI) | Richiede madrelingua o revisore |
| B-20 | 🟢 | Language switcher nell'header, persistito in localStorage | UX per cambio lingua in-app |
| B-21 | 🟢 | Traduzione dei contenuti didattici (mechanisms.ts, phases.ts, howItWorks.ts) | I file di contenuto hanno molte stringhe lunghe — gestirle separatamente dal resto della UI |
| B-22 | 🟢 | Traduzione `openapi.yaml` — descrizioni endpoint in inglese | Bassa priorità, utile solo per sviluppatori |

### Decisioni architetturali da prendere prima di TASK_15

- **Libreria**: `react-i18next` (standard de facto) o alternativa?
- **Formato file**: `.json` (semplice) o `.po`/`.pot` (standard gettext, tool professionali)?
- **Namespace**: un file unico per lingua o suddiviso per componente/vista?
- **Fallback**: se una stringa sarda manca → cade su italiano o inglese?
- **Codice locale sardo**: `sc` (ISO 639-1 non ufficiale) o `srd` (ISO 639-3)?

---

## Scartato / In attesa

| # | Voce | Motivo |
|---|---|---|
| — | — | — |

---

*Ultimo aggiornamento: 2026-03-10*
