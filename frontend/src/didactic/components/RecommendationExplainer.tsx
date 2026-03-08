import { useState } from 'react';
import type { Recommendation } from '../../types';

interface RecommendationExplainerProps {
  recommendation: Recommendation;
}

const RISK_EXPLANATION: Record<string, string> = {
  LOW: 'Rischio contenuto — impatto limitato sui retail in caso di applicazione.',
  MEDIUM: 'Rischio moderato — perdite significative per i follower se attivato.',
  HIGH: 'Rischio elevato — impatto diretto e immediato sul capitale dei retail.',
};

/**
 * Pannello toggle "[Spiega questo]" che spiega in linguaggio semplice
 * perché l'algoritmo ha generato una specifica raccomandazione.
 */
export function RecommendationExplainer({ recommendation: rec }: RecommendationExplainerProps) {
  const [open, setOpen] = useState(false);

  const isMonetization = rec.suggested_action === 'TRANSITION_TO_MONETIZATION';

  return (
    <div>
      <button
        onClick={() => setOpen((o) => !o)}
        className="text-xs text-blue-400 hover:text-blue-300 underline underline-offset-2 transition-colors"
      >
        {open ? '▲ Chiudi spiegazione' : '[Spiega questo]'}
      </button>

      {open && (
        <div className="mt-2 bg-gray-900 border border-gray-700 rounded-lg p-3 space-y-3 text-xs">

          {/* Perché questo score */}
          <div>
            <p className="text-gray-400 font-medium mb-1">Perché questo score ({rec.score.toFixed(2)})?</p>
            <p className="text-gray-300 leading-relaxed">
              L'algoritmo assegna uno score a ogni trader basandosi sul numero di follower,
              il capitale esposto attraverso il copy trading, la fase corrente e la distanza
              dalla soglia di monetizzazione. Score più alti indicano che il trader ha
              accumulato sufficiente fiducia da parte dei follower per massimizzare l'impatto
              di una transizione.
            </p>
          </div>

          {/* Livello di rischio */}
          <div>
            <p className="text-gray-400 font-medium mb-1">
              Livello di rischio: <span className={
                rec.risk_level === 'HIGH' ? 'text-red-400' :
                rec.risk_level === 'MEDIUM' ? 'text-yellow-400' :
                'text-green-400'
              }>{rec.risk_level}</span>
            </p>
            <p className="text-gray-300">{RISK_EXPLANATION[rec.risk_level] ?? ''}</p>
          </div>

          {/* Impatto retail — frase mandatoria */}
          <div className="bg-red-950/30 border border-red-800 rounded p-2">
            <p className="text-red-300 leading-relaxed">
              Se questa azione viene applicata, i{' '}
              <strong>{rec.trader_name}</strong> è copiato da follower con capitale esposto.
              Applicando <strong>{isMonetization ? 'Fase C' : 'questa azione'}</strong>,
              il capitale dei retail che lo copiano è esposto a perdite stimate di{' '}
              <strong>€{(rec.expected_platform_gain * 1.2).toFixed(0)}</strong> nei tick successivi.
              La piattaforma registrerebbe un guadagno netto stimato di{' '}
              <strong className="text-green-400">€{rec.expected_platform_gain.toFixed(0)}</strong>.
            </p>
          </div>

          {/* A spese di chi */}
          {isMonetization && (
            <div>
              <p className="text-gray-400 font-medium mb-1">A spese di chi?</p>
              <p className="text-gray-300 leading-relaxed">
                Tutti i retail che hanno avviato una relazione di copy con{' '}
                <strong>{rec.trader_name}</strong> subiranno perdite proporzionali
                alla loro percentuale di allocazione. Non riceveranno alcun avviso
                automatico dalla piattaforma.
              </p>
            </div>
          )}

          {/* Confidenza algoritmo */}
          <p className="text-gray-500">
            Confidenza algoritmo: {(rec.confidence * 100).toFixed(0)}% — basata su
            simulazione Monte Carlo con distribuzione GBM dei prezzi.
          </p>
        </div>
      )}
    </div>
  );
}
