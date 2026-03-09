import { useState } from 'react';
import { howItWorksSections } from '../content/howItWorks';

interface HowItWorksProps {
  open: boolean;
  onClose: () => void;
}

/**
 * Pannello laterale (drawer) con spiegazione completa del modello economico
 * simulato dalla piattaforma. 5 sezioni narrative, contenuto statico.
 */
export function HowItWorks({ open, onClose }: HowItWorksProps) {
  const [activeSection, setActiveSection] = useState<string | null>(null);

  if (!open) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black/60 z-40"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed right-0 top-0 h-full w-full max-w-lg bg-gray-900 border-l border-gray-700 z-50 flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-700 shrink-0">
          <h2 className="text-white font-bold text-base flex items-center gap-2">
            <span>📖</span>
            <span>Come funziona la piattaforma</span>
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors text-lg leading-none"
          >
            ✕
          </button>
        </div>

        {/* Intro */}
        <div className="px-5 py-3 bg-blue-950/30 border-b border-blue-900 text-xs text-blue-300 shrink-0">
          Questa piattaforma simula un sistema di copy trading con un conflitto di interesse
          strutturale incorporato. Leggere questa guida prima di interagire con la simulazione
          aiuta a riconoscere i meccanismi in azione.
        </div>

        {/* Sezioni scrollabili */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3">
          {howItWorksSections.map((section) => {
            const isActive = activeSection === section.id;
            return (
              <div
                key={section.id}
                className="border border-gray-700 rounded-lg overflow-hidden"
              >
                <button
                  onClick={() => setActiveSection(isActive ? null : section.id)}
                  className="w-full flex items-center justify-between px-4 py-3 text-left bg-gray-800 hover:bg-gray-750 transition-colors"
                >
                  <span className="text-sm font-semibold text-white">{section.title}</span>
                  <span className="text-gray-500 text-xs ml-2 shrink-0">
                    {isActive ? '▲' : '▼'}
                  </span>
                </button>

                {isActive && (
                  <div className="px-4 py-3 bg-gray-800/50 space-y-2">
                    {section.content.map((paragraph, idx) => (
                      <p key={idx} className="text-xs text-gray-300 leading-relaxed">
                        {paragraph}
                      </p>
                    ))}
                    {section.highlight && (
                      <div className="mt-3 bg-yellow-950/40 border border-yellow-800 rounded p-2">
                        <p className="text-xs text-yellow-300 font-medium">
                          💡 {section.highlight}
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-gray-700 text-xs text-gray-500 shrink-0">
          Questo è un progetto didattico. Nessun dato reale. Nessun utente reale esposto.
        </div>
      </div>
    </>
  );
}
