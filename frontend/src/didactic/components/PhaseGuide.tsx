import { useState } from 'react';
import { phaseTimelineSteps } from '../content/phases';

/**
 * Timeline visiva delle tre fasi del trader professionista.
 * Collassabile, aperta di default alla prima visualizzazione.
 */
export function PhaseGuide() {
  const [open, setOpen] = useState(true);

  return (
    <div className="bg-gray-800/60 border border-gray-700 rounded-lg text-xs">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center justify-between w-full px-3 py-2.5 text-gray-300 hover:text-white transition-colors"
      >
        <span className="font-medium flex items-center gap-2">
          <span>📘</span>
          <span>Come funzionano i trader professionisti?</span>
        </span>
        <span className="text-gray-500 text-[10px]">{open ? '▲ chiudi' : '▼ leggi di più'}</span>
      </button>

      {open && (
        <div className="px-3 pb-3 space-y-3">
          {/* Timeline */}
          <div className="flex items-start gap-2 mt-1">
            {phaseTimelineSteps.map((step, idx) => (
              <div key={step.phase} className="flex items-start gap-2 flex-1">
                <div
                  className={`flex-1 rounded p-2 text-center ${
                    step.phase === 'REPUTATION_BUILD'
                      ? 'bg-blue-950 border border-blue-800'
                      : step.phase === 'FOLLOWER_GROWTH'
                      ? 'bg-yellow-950 border border-yellow-800'
                      : 'bg-red-950 border border-red-800'
                  }`}
                >
                  <p className={`font-bold ${
                    step.phase === 'REPUTATION_BUILD' ? 'text-blue-400' :
                    step.phase === 'FOLLOWER_GROWTH' ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {step.title}
                  </p>
                  <p className="text-gray-300 mt-0.5">{step.subtitle}</p>
                  <p className="text-gray-500 mt-1 text-[10px]">{step.detail}</p>
                </div>
                {idx < phaseTimelineSteps.length - 1 && (
                  <div className="text-gray-600 mt-4 shrink-0">→</div>
                )}
              </div>
            ))}
          </div>

          <p className="text-gray-400 leading-relaxed">
            I trader professionisti <strong className="text-white">non sono indipendenti</strong>.
            La piattaforma controlla la loro fase e quindi il loro comportamento.
            In Fase C, le loro operazioni sono progettate per farti perdere —
            mentre loro vengono comunque pagati con un bonus fisso.
          </p>
        </div>
      )}
    </div>
  );
}
