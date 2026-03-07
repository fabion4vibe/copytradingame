# TASK_09 — Frontend Setup + API Client

**File di output**: `frontend/` (scaffold completo), `frontend/src/api/`
**Dipende da**: TASK_07 (API funzionante)
**Blocca**: TASK_10, TASK_11

---

## Obiettivo

Creare lo scaffold del progetto React + TypeScript, configurare il router e il role switcher, e implementare il layer API client centralizzato. Nessuna logica di business qui: solo infrastruttura frontend.

---

## Setup Progetto

Usa Vite con template React + TypeScript:
```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install recharts axios tailwindcss @types/node
```

---

## Struttura Directory Frontend

```
frontend/src/
├── main.tsx                  # Entry point React
├── App.tsx                   # Router + RoleSwitcher
├── api/
│   ├── client.ts             # Istanza axios configurata
│   ├── market.ts             # Chiamate /market
│   ├── retail.ts             # Chiamate /retail
│   ├── professional.ts       # Chiamate /professional
│   ├── algorithm.ts          # Chiamate /algorithm
│   └── manager.ts            # Chiamate /manager
├── types/
│   └── index.ts              # Tutti i tipi TypeScript
├── views/
│   ├── retail/               # TASK_10
│   └── manager/              # TASK_11
├── components/
│   ├── RoleSwitcher.tsx      # Switch Retail ↔ Gestore
│   ├── TickController.tsx    # Controllo avanzamento tick
│   ├── PriceChart.tsx        # Grafico prezzi (recharts)
│   ├── LoadingSpinner.tsx
│   └── ErrorMessage.tsx
└── hooks/
    ├── useMarket.ts          # Hook per dati mercato
    └── usePolling.ts         # Hook per polling automatico
```

---

## `frontend/src/api/client.ts`

```typescript
import axios from 'axios';

const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
});

// Interceptor per errori globali
client.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data?.detail || error.message);
    return Promise.reject(error);
  }
);

export default client;
```

---

## `frontend/src/api/market.ts`

```typescript
export const marketApi = {
  getAssets: () => client.get('/market/assets'),
  getAsset: (id: string) => client.get(`/market/assets/${id}`),
  getHistory: (id: string, lastN?: number) => 
    client.get(`/market/assets/${id}/history`, { params: { last_n: lastN } }),
  advanceTick: (nTicks = 1) => client.post('/market/tick', { n_ticks: nTicks }),
  getStatus: () => client.get('/market/status'),
};
```

Implementa pattern analogo per `retail.ts`, `professional.ts`, `algorithm.ts`, `manager.ts`.

---

## `frontend/src/types/index.ts`

Definisci tutti i tipi TypeScript corrispondenti agli oggetti JSON del backend:

```typescript
export type TraderPhase = 'REPUTATION_BUILD' | 'FOLLOWER_GROWTH' | 'MONETIZATION';

export interface Asset {
  id: string;
  symbol: string;
  current_price: number;
  initial_price: number;
  volatility: number;
  drift: number;
}

export interface RetailSummary {
  id: string;
  name: string;
  balance: number;
  portfolio_value: number;
  total_pnl: number;
  n_trades: number;
  copied_traders: string[];
}

export interface ProfessionalSummary {
  id: string;
  name: string;
  phase: TraderPhase;
  followers_count: number;
  follower_capital_exposed: number;
  pnl_personal: number;
  bonus_earned: number;
  total_compensation: number;
}

export interface Trade {
  id: string;
  trader_id: string;
  asset_id: string;
  action: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  timestamp: number;
  is_copy: boolean;
  copied_from: string | null;
  pnl_realized: number;
}

export interface Recommendation {
  trader_id: string;
  trader_name: string;
  current_phase: TraderPhase;
  suggested_action: string;
  reason: string;
  expected_platform_gain: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence: number;
  score: number;
}

export interface PlatformOverview {
  current_tick: number;
  platform_pnl: number;
  platform_net: number;
  total_retail_capital: number;
  copy_penetration_pct: number;
  n_professionals_in_monetization: number;
  n_retail_losing: number;
  avg_retail_pnl: number;
}
```

---

## `frontend/src/App.tsx`

```typescript
// Gestisce:
// 1. Stato globale: ruolo corrente ('retail' | 'manager')
// 2. RoleSwitcher visibile in ogni vista
// 3. TickController visibile in ogni vista
// 4. Routing tra RetailDashboard e ManagerDashboard
```

---

## `frontend/src/components/RoleSwitcher.tsx`

Pulsante toggle visibile in alto in ogni pagina:

```
[ 👤 Retail ] [ 🏢 Gestore ]
```

Al click, cambia la vista renderizzata senza ricaricare la pagina.

---

## `frontend/src/components/TickController.tsx`

Pannello fisso in basso o in header:

```
Tick: 42  [ +1 Tick ] [ +10 Tick ] [ ▶ Auto ] [ ⏹ Stop ]
```

- `+1 Tick`: chiama `marketApi.advanceTick(1)`
- `+10 Tick`: chiama `marketApi.advanceTick(10)`
- `▶ Auto`: polling ogni 2s che chiama `advanceTick(1)` automaticamente
- `⏹ Stop`: ferma il polling

---

## `frontend/src/hooks/usePolling.ts`

```typescript
// Hook generico per polling a intervallo regolare
// usePolling(fn, intervalMs, enabled)
// Chiama fn() ogni intervalMs millisecondi se enabled === true
// Chiama clearInterval al cleanup
```

---

## Vincoli

- Nessun `any` in TypeScript.
- Nessuna chiamata fetch diretta nei componenti: tutto passa per `src/api/`.
- Tailwind per tutti gli stili.

---

## Criteri di Completamento

- [ ] Progetto Vite funzionante con `npm run dev`
- [ ] `client.ts` con axios e interceptor
- [ ] Tutti i file `api/*.ts` con le funzioni necessarie
- [ ] `types/index.ts` con tutti i tipi
- [ ] `App.tsx` con role switcher funzionante
- [ ] `RoleSwitcher.tsx` funzionante
- [ ] `TickController.tsx` funzionante (manuale + auto)
- [ ] `usePolling.ts` hook generico
- [ ] `PriceChart.tsx` con recharts LineChart base
