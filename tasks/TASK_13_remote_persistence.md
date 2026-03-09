# TASK_13 — Persistenza Stato Remota (JSONBin.io)

**File di output**: modifiche a `backend/state.py`, `backend/orchestrator.py`, `backend/main.py`
**Branch**: `task/13-remote-persistence`
**Dipende da**: TASK_08 (orchestrator completo e funzionante)
**Milestone**: post-M2, pre-deploy

---

## Obiettivo

Il backend gira su Render free tier, che termina il processo dopo 15 minuti di inattività.
Al riavvio, lo stato in memoria viene perso. Questo task aggiunge la persistenza remota
tramite JSONBin.io: ogni 100 tick lo stato viene salvato su un bin remoto, e al riavvio
viene ripristinato automaticamente.

Il codice deve funzionare **senza modifiche** sia in locale (dove le env var non esistono)
sia in produzione (dove le env var sono configurate su Render).

---

## Prerequisiti Manuali (A Carico dell'Utente, Non dell'Agente)

Prima che questo task venga eseguito, l'utente deve:

1. Creare un account su https://jsonbin.io
2. Ottenere la **Master Key** dalla dashboard → API Keys
3. Creare un bin vuoto una volta sola:
   ```bash
   curl -X POST https://api.jsonbin.io/v3/b \
     -H "Content-Type: application/json" \
     -H "X-Master-Key: TUA_MASTER_KEY" \
     -d '{"current_tick": 0}'
   ```
4. Salvare il `bin_id` dalla risposta (campo `metadata.id`)
5. Su Render → Environment Variables, aggiungere:
   ```
   JSONBIN_KEY=TUA_MASTER_KEY
   JSONBIN_BIN_ID=TUO_BIN_ID
   ```

L'agente non gestisce queste operazioni. Assume che le variabili d'ambiente siano
già configurate su Render quando il codice viene deployato.

---

## Modifica 1 — `backend/state.py`

Aggiungi in cima al file, dopo gli import esistenti:

```python
import os
import json
import urllib.request
import urllib.error
```

Aggiungi queste costanti a livello di modulo (fuori dalla classe):

```python
JSONBIN_BASE_URL = "https://api.jsonbin.io/v3/b"
JSONBIN_KEY = os.environ.get("JSONBIN_KEY")        # None in locale
JSONBIN_BIN_ID = os.environ.get("JSONBIN_BIN_ID")  # None in locale
```

Aggiungi questi due metodi alla classe `SimulationState`:

```python
def save_to_remote(self) -> None:
    """
    Persiste lo stato corrente su JSONBin.io via HTTP PUT.

    Non fa nulla se JSONBIN_KEY o JSONBIN_BIN_ID non sono configurati
    (comportamento atteso in ambiente locale).

    Non solleva eccezioni: se il salvataggio fallisce (timeout, rete,
    rate limit), il tick continua normalmente. Il prossimo salvataggio
    programmato riproverà.
    """
    if not JSONBIN_KEY or not JSONBIN_BIN_ID:
        return

    url = f"{JSONBIN_BASE_URL}/{JSONBIN_BIN_ID}"
    payload = json.dumps(self.get_state_snapshot()).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": JSONBIN_KEY,
    }
    req = urllib.request.Request(
        url, data=payload, headers=headers, method="PUT"
    )
    try:
        urllib.request.urlopen(req, timeout=3)
    except (urllib.error.URLError, TimeoutError):
        pass  # # DIDACTIC: il fallimento del salvataggio non blocca la simulazione

@classmethod
def load_from_remote(cls) -> dict | None:
    """
    Carica l'ultimo snapshot salvato da JSONBin.io.

    Restituisce il dizionario dello snapshot se disponibile,
    None in tutti gli altri casi (locale, rete assente, bin vuoto,
    risposta malformata).
    """
    if not JSONBIN_KEY or not JSONBIN_BIN_ID:
        return None

    url = f"{JSONBIN_BASE_URL}/{JSONBIN_BIN_ID}/latest"
    headers = {"X-Master-Key": JSONBIN_KEY}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("record")  # JSONBin wrappa il contenuto in "record"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return None
```

---

## Modifica 2 — `backend/orchestrator.py`

Nella classe `TickOrchestrator`, nel metodo `run_tick()`, aggiungi il salvataggio
condizionale **come ultima operazione prima del return**:

```python
def run_tick(self) -> dict:
    """..docstring esistente.."""

    # — step 1: aggiorna prezzi
    # — step 2: esegui strategie professionisti
    # — step 3: propaga copy
    # — step 4: aggiorna follower capital
    # ... logica esistente invariata ...

    # Salvataggio remoto ogni 100 tick.
    # In locale JSONBIN_KEY non è configurato, save_to_remote() non fa nulla.
    # In produzione salva lo snapshot su JSONBin per sopravvivere ai riavvii di Render.
    if state.current_tick % 100 == 0:
        state.save_to_remote()

    return summary
```

Non modificare nient'altro in questo file.

---

## Modifica 3 — `backend/main.py`

Sostituisci lo startup event esistente con questa versione:

```python
@app.on_event("startup")
async def startup() -> None:
    """
    Inizializza lo stato della simulazione.

    Tenta prima il ripristino da JSONBin (produzione).
    Se non disponibile o fallisce, inizializza da zero (locale + primo avvio).
    """
    snapshot = SimulationState.load_from_remote()

    if snapshot:
        _restore_state_from_snapshot(snapshot)
    else:
        market.initialize_default_assets()
        create_default_professionals(3)
        create_simulated_retailers(10)


def _restore_state_from_snapshot(snapshot: dict) -> None:
    """
    Ripristina lo stato globale da un dizionario snapshot.

    Il formato del dizionario è quello prodotto da state.get_state_snapshot().
    Campi mancanti nello snapshot vengono ignorati (default invariato).
    """
    state.current_tick            = snapshot.get("current_tick", 0)
    state.platform_pnl            = snapshot.get("platform_pnl", 0.0)
    state.platform_commissions    = snapshot.get("platform_commissions", 0.0)
    state.platform_bonus_paid     = snapshot.get("platform_bonus_paid", 0.0)

    # Ripristina asset
    for asset_id, asset_data in snapshot.get("assets", {}).items():
        state.assets[asset_id] = asset_from_dict(asset_data)

    # Ripristina retail traders
    for trader_id, trader_data in snapshot.get("retail_traders", {}).items():
        state.retail_traders[trader_id] = retail_trader_from_dict(trader_data)

    # Ripristina professional traders
    for trader_id, trader_data in snapshot.get("professional_traders", {}).items():
        state.professional_traders[trader_id] = professional_trader_from_dict(trader_data)

    # Ripristina copy relations
    state.copy_relations = [
        copy_relation_from_dict(cr)
        for cr in snapshot.get("copy_relations", [])
    ]

    # Ripristina trade log (ultimi 500 trade per contenere le dimensioni del JSON)
    state.trade_log = [
        trade_from_dict(t)
        for t in snapshot.get("trade_log", [])
    ]
```

Le funzioni `asset_from_dict`, `retail_trader_from_dict`, `professional_trader_from_dict`,
`copy_relation_from_dict`, `trade_from_dict` sono i costruttori inversi delle rispettive
classi. Implementale nello stesso file o nei moduli di appartenenza (es. `market/asset.py`,
`traders/retail.py` ecc.) come metodi di classe `from_dict(cls, data: dict)`.

---

## Aggiornamento `get_state_snapshot()` in `state.py`

Verifica che `get_state_snapshot()` (definita in TASK_01) restituisca un dizionario
**completamente serializzabile in JSON**, includendo tutti i campi necessari al ripristino:

```python
def get_state_snapshot(self) -> dict:
    """
    Restituisce uno snapshot completo dello stato, serializzabile in JSON.
    Usato sia per debug/export che per la persistenza remota (JSONBin).

    Il trade_log viene troncato agli ultimi 500 elementi per contenere
    le dimensioni del payload JSON entro limiti ragionevoli per JSONBin free tier.
    """
    return {
        "current_tick":           self.current_tick,
        "platform_pnl":           self.platform_pnl,
        "platform_commissions":   self.platform_commissions,
        "platform_bonus_paid":    self.platform_bonus_paid,
        "assets": {
            asset_id: asset.to_dict()
            for asset_id, asset in self.assets.items()
        },
        "retail_traders": {
            trader_id: trader.to_dict()
            for trader_id, trader in self.retail_traders.items()
        },
        "professional_traders": {
            trader_id: trader.to_dict()
            for trader_id, trader in self.professional_traders.items()
        },
        "copy_relations": [
            cr.to_dict() for cr in self.copy_relations
        ],
        "trade_log": [
            t.to_dict() for t in self.trade_log[-500:]  # ultimi 500
        ],
    }
```

Verifica che tutte le classi coinvolte (`Asset`, `RetailTrader`, `ProfessionalTrader`,
`CopyRelation`, `Trade`) abbiano un metodo `to_dict()` che restituisce un dizionario
con soli tipi primitivi (str, int, float, bool, list, dict). Se manca, aggiungilo.

---

## Comportamento Atteso

| Situazione | Comportamento |
|---|---|
| Locale, env var assenti | `save_to_remote()` e `load_from_remote()` non fanno nulla |
| Produzione, ogni 100 tick | Snapshot salvato su JSONBin silenziosamente |
| Render va in sleep e si risveglia | Startup carica da JSONBin, simulazione riprende dal tick salvato |
| JSONBin non raggiungibile al tick | Tick avanza normalmente, salvataggio saltato |
| JSONBin non raggiungibile allo startup | Inizializzazione da zero, come primo avvio |
| Snapshot corrotto o parziale | `load_from_remote()` restituisce None, inizializzazione da zero |

---

## Stima Utilizzo JSONBin Free Tier

- Free tier: 10.000 richieste/mese
- Salvataggio ogni 100 tick
- Auto-tick ogni 2 secondi → 1 tick ogni 2s → 1 salvataggio ogni 200s → ~13.000/mese con uso continuo H24
- **Per uso didattico discontinuo** (qualche ora al giorno): ~500–1.000 richieste/mese, ampiamente nel free tier

Se l'auto-tick viene usato intensivamente, aumentare l'intervallo a `% 200` o `% 500`.

---

## File da NON Modificare

- Tutti i task sheets (`tasks/`)
- `openapi.yaml`
- `TASK_GRAPH.md` (aggiornalo solo marcando questo task come completato)
- Qualsiasi file frontend

---

## Criteri di Completamento

- [ ] `save_to_remote()` aggiunta a `SimulationState`, silenziosa in locale
- [ ] `load_from_remote()` aggiunta a `SimulationState`, restituisce None in locale
- [ ] `get_state_snapshot()` restituisce dizionario completamente serializzabile con tutti i campi
- [ ] Tutti i modelli hanno `to_dict()` e `from_dict()` compatibili
- [ ] `run_tick()` chiama `save_to_remote()` ogni 100 tick
- [ ] Startup event tenta ripristino remoto prima dell'inizializzazione da zero
- [ ] `_restore_state_from_snapshot()` ripristina correttamente tutti i campi
- [ ] Nessuna eccezione non gestita in caso di rete assente o JSONBin irraggiungibile
- [ ] Il comportamento in locale è identico a prima di questo task
