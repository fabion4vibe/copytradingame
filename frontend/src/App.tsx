import { useState } from 'react';
import { RoleSwitcher } from './components/RoleSwitcher';
import { TickController } from './components/TickController';
import { RetailDashboard } from './views/retail/RetailDashboard';
import { ManagerDashboard } from './views/manager/ManagerDashboard';
import type { AppRole } from './types';

/**
 * Root dell'applicazione.
 *
 * Gestisce:
 * - Il ruolo attivo ('retail' | 'manager') per il routing tra le viste
 * - Il tick corrente, passato come prop alle viste per triggerare il re-fetch
 *   senza rimontare l'intero componente (preserva lo stato locale, es. PnL history)
 */
export default function App() {
  const [role, setRole] = useState<AppRole>('retail');
  const [tick, setTick] = useState(0);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header fisso */}
      <header className="sticky top-0 z-50 bg-gray-900 border-b border-gray-800 px-6 py-3">
        <div className="max-w-screen-xl mx-auto flex items-center justify-between gap-4">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <span className="text-lg font-bold text-white tracking-tight">
              Trading Platform Simulator
            </span>
            <span className="hidden sm:inline text-xs text-gray-500 border border-gray-700 rounded px-2 py-0.5">
              didattico
            </span>
          </div>

          {/* Controlli centrali */}
          <TickController currentTick={tick} onTickAdvanced={setTick} />

          {/* Role switcher */}
          <RoleSwitcher role={role} onChange={setRole} />
        </div>
      </header>

      {/* Vista principale — tick passato come prop, non come key */}
      <main className="max-w-screen-xl mx-auto px-6 py-6">
        {role === 'retail' ? (
          <RetailDashboard tick={tick} />
        ) : (
          <ManagerDashboard tick={tick} />
        )}
      </main>
    </div>
  );
}
