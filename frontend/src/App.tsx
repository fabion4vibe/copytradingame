import { useState } from 'react';
import { RoleSwitcher } from './components/RoleSwitcher';
import { TickController } from './components/TickController';
import { RetailDashboard } from './views/retail/RetailDashboard';
import { ManagerDashboard } from './views/manager/ManagerDashboard';
import { ConflictOfInterestBanner } from './didactic/components/ConflictOfInterestBanner';
import type { AppRole } from './types';

/**
 * Application root.
 *
 * Manages:
 * - The active role ('retail' | 'manager') for routing between views
 * - The current tick, passed as a prop to views to trigger re-fetching
 *   without remounting the entire component (preserves local state, e.g. PnL history)
 */
export default function App() {
  const [role, setRole] = useState<AppRole>('retail');
  const [tick, setTick] = useState(0);

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Fixed header */}
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

          {/* Central controls */}
          <TickController currentTick={tick} onTickAdvanced={setTick} />

          {/* Role switcher */}
          <RoleSwitcher role={role} onChange={setRole} />
        </div>
      </header>

      {/* Vista principale — tick passato come prop, non come key */}
      <main className="max-w-screen-xl mx-auto px-6 py-6 space-y-4">
        {/* Banner conflitto di interesse — non dismissibile (TASK_12) */}
        <ConflictOfInterestBanner role={role} />

        {role === 'retail' ? (
          <RetailDashboard tick={tick} />
        ) : (
          <ManagerDashboard tick={tick} />
        )}
      </main>

      {/* Footer licenza */}
      <footer className="border-t border-gray-800 mt-10 py-4 px-6 text-center text-xs text-gray-600">
        <p>
          &copy; FC —{' '}
          <a
            href="https://github.com/fabion4vibe/copytradingame"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-gray-400 transition-colors"
          >
            github.com/fabion4vibe/copytradingame
          </a>
          {' '}·{' '}
          <a
            href="https://creativecommons.org/licenses/by/4.0/"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-gray-400 transition-colors"
          >
            CC BY 4.0
          </a>
        </p>
      </footer>
    </div>
  );
}
