import { useState } from 'react';
import { marketApi } from '../api/market';
import { usePolling } from '../hooks/usePolling';

interface TickControllerProps {
  currentTick: number;
  onTickAdvanced: (newTick: number) => void;
}

/**
 * Pannello di controllo per l'avanzamento della simulazione.
 * Permette tick manuali (+1, +10) e tick automatico (polling ogni 2s).
 *
 * Posizionato nell'header in modo da essere sempre visibile
 * indipendentemente dalla vista attiva (retail o gestore).
 */
export function TickController({ currentTick, onTickAdvanced }: TickControllerProps) {
  const [autoRunning, setAutoRunning] = useState(false);
  const [loading, setLoading] = useState(false);

  const advance = async (n: number) => {
    if (loading) return;
    try {
      setLoading(true);
      const res = await marketApi.advanceTick(n);
      onTickAdvanced(res.data.tick);
    } catch {
      // Errore già loggato dall'interceptor axios
    } finally {
      setLoading(false);
    }
  };

  // Auto-tick: chiama advance(1) ogni 2 secondi se autoRunning è true
  usePolling(() => { void advance(1); }, 2000, autoRunning);

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm font-mono text-gray-300">
        Tick: <span className="text-white font-bold">{currentTick}</span>
      </span>

      <div className="flex items-center gap-1">
        <button
          onClick={() => advance(1)}
          disabled={loading || autoRunning}
          className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 disabled:opacity-40 text-white rounded transition-colors"
        >
          +1
        </button>
        <button
          onClick={() => advance(10)}
          disabled={loading || autoRunning}
          className="px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 disabled:opacity-40 text-white rounded transition-colors"
        >
          +10
        </button>

        {!autoRunning ? (
          <button
            onClick={() => setAutoRunning(true)}
            disabled={loading}
            className="px-3 py-1 text-xs bg-green-700 hover:bg-green-600 disabled:opacity-40 text-white rounded transition-colors"
          >
            ▶ Auto
          </button>
        ) : (
          <button
            onClick={() => setAutoRunning(false)}
            className="px-3 py-1 text-xs bg-red-700 hover:bg-red-600 text-white rounded transition-colors"
          >
            ⏹ Stop
          </button>
        )}
      </div>

      {loading && (
        <span className="text-xs text-gray-500 animate-pulse">avanzamento...</span>
      )}
    </div>
  );
}
