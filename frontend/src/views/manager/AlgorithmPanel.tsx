import { useEffect, useState } from 'react';
import { algorithmApi } from '../../api/algorithm';
import { professionalApi } from '../../api/professional';
import type {
  Recommendation,
  ProfessionalSummary,
  RiskLevel,
  ScenarioResult,
} from '../../types';
import { RecommendationExplainer } from '../../didactic/RecommendationExplainer';

interface AlgorithmPanelProps {
  tick: number;
  onActionApplied: () => void;
}

const RISK_BADGE: Record<RiskLevel, { label: string; className: string }> = {
  LOW: { label: 'Basso', className: 'bg-green-900 text-green-300' },
  MEDIUM: { label: 'Medio', className: 'bg-yellow-900 text-yellow-300' },
  HIGH: { label: 'Alto', className: 'bg-red-900 text-red-300' },
};

type ScenarioType = 'TRANSITION_TO_MONETIZATION' | 'MAINTAIN_CURRENT_PHASE';

/** Pannello con raccomandazioni algoritmiche e form di simulazione scenari. */
export function AlgorithmPanel({ tick, onActionApplied }: AlgorithmPanelProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [professionals, setProfessionals] = useState<ProfessionalSummary[]>([]);
  const [applying, setApplying] = useState<string | null>(null);
  const [ignored, setIgnored] = useState<Set<string>>(new Set());

  // Simulazione scenario
  const [scenarioTraderId, setScenarioTraderId] = useState('');
  const [scenarioType, setScenarioType] = useState<ScenarioType>('TRANSITION_TO_MONETIZATION');
  const [scenarioTicks, setScenarioTicks] = useState('10');
  const [simulating, setSimulating] = useState(false);
  const [scenarioResult, setScenarioResult] = useState<ScenarioResult | null>(null);
  const [scenarioError, setScenarioError] = useState<string | null>(null);

  useEffect(() => {
    algorithmApi.getRecommendations().then((r) => setRecommendations(r.data)).catch(() => {});
    professionalApi.listTraders().then((r) => {
      setProfessionals(r.data);
      if (r.data.length > 0 && !scenarioTraderId) {
        setScenarioTraderId(r.data[0].id);
      }
    }).catch(() => {});
  }, [tick]);

  const handleApply = async (rec: Recommendation) => {
    setApplying(rec.trader_id);
    try {
      // La raccomandazione suggerisce TRANSITION_TO_MONETIZATION → usa changePhase
      if (rec.suggested_action === 'TRANSITION_TO_MONETIZATION') {
        await professionalApi.changePhase(rec.trader_id, 'MONETIZATION');
      }
      // Segna come applicata (simile a ignorata ma con feedback diverso)
      setIgnored((prev) => new Set(prev).add(rec.trader_id + '_applied'));
      onActionApplied();
    } catch {
      // fallthrough — mostra solo che non è riuscita
    } finally {
      setApplying(null);
    }
  };

  const handleIgnore = (rec: Recommendation) => {
    setIgnored((prev) => new Set(prev).add(rec.trader_id));
  };

  const handleSimulate = async () => {
    if (!scenarioTraderId) return;
    const n = parseInt(scenarioTicks);
    if (isNaN(n) || n <= 0) return;
    setSimulating(true);
    setScenarioResult(null);
    setScenarioError(null);
    try {
      const res = await algorithmApi.simulateScenario(scenarioTraderId, scenarioType, n);
      setScenarioResult(res.data);
    } catch {
      setScenarioError('Errore durante la simulazione.');
    } finally {
      setSimulating(false);
    }
  };

  const visibleRecs = recommendations.filter(
    (r) => !ignored.has(r.trader_id) && !ignored.has(r.trader_id + '_applied')
  );

  return (
    <div className="space-y-5">

      {/* Sezione 1: Raccomandazioni algoritmiche */}
      <div>
        <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">
          Raccomandazioni algoritmiche
        </h3>

        {visibleRecs.length === 0 ? (
          <p className="text-sm text-gray-500 italic">
            {recommendations.length > 0
              ? 'Tutte le raccomandazioni sono state gestite.'
              : 'Nessuna raccomandazione disponibile in questo momento.'}
          </p>
        ) : (
          <div className="space-y-3">
            {visibleRecs.map((rec) => {
              const risk = RISK_BADGE[rec.risk_level];
              const isMonetization = rec.suggested_action === 'TRANSITION_TO_MONETIZATION';
              return (
                <div
                  key={rec.trader_id}
                  className={`rounded-lg border p-3 space-y-2 ${
                    isMonetization
                      ? 'border-red-800 bg-red-950/20'
                      : 'border-gray-700 bg-gray-800/50'
                  }`}
                >
                  {/* Header raccomandazione */}
                  <div className="flex items-start gap-2">
                    <span
                      className={`text-xs px-1.5 py-0.5 rounded font-medium ${risk.className}`}
                    >
                      {risk.label.toUpperCase()}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-white text-sm font-medium">{rec.trader_name}</p>
                      <p className="text-gray-400 text-xs">
                        Azione suggerita:{' '}
                        <strong className={isMonetization ? 'text-red-400' : 'text-yellow-400'}>
                          {isMonetization
                            ? 'Attiva perdite per i follower (Fase C)'
                            : rec.suggested_action}
                        </strong>
                      </p>
                    </div>
                  </div>

                  {/* Dettagli */}
                  <p className="text-xs text-gray-400">{rec.reason}</p>
                  <div className="flex gap-4 text-xs text-gray-400">
                    <span>
                      Guadagno stimato piattaforma:{' '}
                      <strong className="text-green-400">
                        +€{rec.expected_platform_gain.toFixed(0)}
                      </strong>
                    </span>
                    <span>
                      Score: <strong className="text-white">{rec.score.toFixed(2)}</strong>
                    </span>
                    <span>
                      Confidenza: <strong className="text-white">{(rec.confidence * 100).toFixed(0)}%</strong>
                    </span>
                  </div>

                  {/* Slot RecommendationExplainer — implementazione in TASK_12 */}
                  <RecommendationExplainer traderId={rec.trader_id} action={rec.suggested_action} />

                  {/* Azioni */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApply(rec)}
                      disabled={applying === rec.trader_id}
                      className={`text-xs px-3 py-1 rounded font-medium transition-colors ${
                        isMonetization
                          ? 'bg-red-800 hover:bg-red-700 text-red-200'
                          : 'bg-blue-800 hover:bg-blue-700 text-blue-200'
                      } disabled:opacity-40`}
                    >
                      {applying === rec.trader_id ? 'Applicazione...' : 'Applica'}
                    </button>
                    <button
                      onClick={() => handleIgnore(rec)}
                      className="text-xs px-3 py-1 rounded bg-gray-700 hover:bg-gray-600 text-gray-400 transition-colors"
                    >
                      Ignora
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Sezione 2: Simulazione scenario */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-3">
          Simulazione scenario
        </h3>

        <div className="space-y-3">
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
            {/* Selezione trader */}
            <div>
              <label className="block text-xs text-gray-400 mb-1">Trader</label>
              <select
                value={scenarioTraderId}
                onChange={(e) => setScenarioTraderId(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded px-2 py-1.5 focus:outline-none focus:border-blue-500"
              >
                {professionals.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            {/* Tipo scenario */}
            <div>
              <label className="block text-xs text-gray-400 mb-1">Scenario</label>
              <select
                value={scenarioType}
                onChange={(e) => setScenarioType(e.target.value as ScenarioType)}
                className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded px-2 py-1.5 focus:outline-none focus:border-blue-500"
              >
                <option value="TRANSITION_TO_MONETIZATION">Attiva perdite follower (Fase C)</option>
                <option value="MAINTAIN_CURRENT_PHASE">Mantieni fase corrente</option>
              </select>
            </div>

            {/* N tick */}
            <div>
              <label className="block text-xs text-gray-400 mb-1">N tick da simulare</label>
              <input
                type="number"
                min="1"
                max="100"
                value={scenarioTicks}
                onChange={(e) => setScenarioTicks(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded px-2 py-1.5 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <button
            onClick={handleSimulate}
            disabled={simulating || !scenarioTraderId}
            className="px-4 py-1.5 bg-gray-700 hover:bg-gray-600 disabled:opacity-40 text-white text-sm rounded transition-colors"
          >
            {simulating ? 'Simulazione in corso...' : 'Simula'}
          </button>

          {scenarioError && (
            <p className="text-xs text-red-400">{scenarioError}</p>
          )}

          {scenarioResult && (
            <div className="bg-gray-800 rounded p-3 space-y-1 text-xs">
              <p className="text-gray-400 font-medium mb-2">
                Risultato simulazione — {scenarioResult.n_ticks} tick
              </p>
              <div className="flex justify-between text-gray-300">
                <span>Perdita retail attesa:</span>
                <span className="font-mono text-red-400">
                  −€{scenarioResult.expected_retail_loss.toFixed(0)}
                </span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Bonus da pagare:</span>
                <span className="font-mono text-orange-400">
                  −€{scenarioResult.expected_bonus_paid.toFixed(0)}
                </span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Guadagno netto piattaforma:</span>
                <span className="font-mono text-green-400">
                  +€{scenarioResult.expected_platform_net_gain.toFixed(0)}
                </span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Intervallo di confidenza:</span>
                <span className="font-mono">
                  [+€{scenarioResult.confidence_interval[0].toFixed(0)} /
                  +€{scenarioResult.confidence_interval[1].toFixed(0)}]
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
