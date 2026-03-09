import { useState } from 'react';
import { metrics } from '../content/metrics';

interface MetricExplainerProps {
  metricId: string;
}

/**
 * Icona ⓘ che apre un tooltip espanso con la spiegazione della metrica.
 * Usato accanto alle card KPI nella dashboard manager.
 */
export function MetricExplainer({ metricId }: MetricExplainerProps) {
  const [open, setOpen] = useState(false);
  const content = metrics[metricId];

  if (!content) return null;

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setOpen((o) => !o)}
        className="text-gray-500 hover:text-blue-400 transition-colors text-xs leading-none"
        title={`Spiega: ${content.label}`}
      >
        ⓘ
      </button>

      {open && (
        <>
          {/* Overlay per chiudere cliccando fuori */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
          />
          {/* Tooltip */}
          <div className="absolute right-0 top-5 z-20 w-64 bg-gray-800 border border-gray-600 rounded-lg p-3 shadow-xl text-xs space-y-2">
            <div className="flex items-start justify-between gap-2">
              <p className="font-semibold text-white">{content.label}</p>
              <button
                onClick={() => setOpen(false)}
                className="text-gray-500 hover:text-white transition-colors shrink-0"
              >
                ✕
              </button>
            </div>
            <p className="text-gray-300 leading-relaxed">{content.explanation}</p>
            {content.formula && (
              <div className="bg-gray-900 rounded px-2 py-1 font-mono text-blue-300 text-[10px]">
                {content.formula}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
