import { useState } from 'react';
import { professionalApi } from '../../api/professional';
import { algorithmApi } from '../../api/algorithm';
import type { ProfessionalSummary, TraderPhase, ScenarioResult } from '../../types';
import { PhaseExplainer } from '../../didactic/PhaseExplainer';

interface TraderControlPanelProps {
  professionals: ProfessionalSummary[];
  onPhaseChanged: () => void;
}

const PHASE_LABEL: Record<TraderPhase, string> = {
  REPUTATION_BUILD: 'Fase A — Costruzione Reputazione',
  FOLLOWER_GROWTH: 'Fase B — Crescita Follower',
  MONETIZATION: 'Fase C — Monetizzazione',
};

const PHASE_COLOR: Record<TraderPhase, string> = {
  REPUTATION_BUILD: 'text-blue-400',
  FOLLOWER_GROWTH: 'text-yellow-400',
  MONETIZATION: 'text-red-400',
};

const ALL_PHASES: TraderPhase[] = ['REPUTATION_BUILD', 'FOLLOWER_GROWTH', 'MONETIZATION'];

/** Stima il guadagno stimato in 10 tick per il dialog di conferma fase C. */
async function fetchPhaseCEstimate(traderId: string): Promise<ScenarioResult | null> {
  try {
    const res = await algorithmApi.simulateScenario(
      traderId,
      'TRANSITION_TO_MONETIZATION',
      10
    );
    return res.data;
  } catch {
    return null;
  }
}

/** Dialog di conferma per l'attivazione della Fase C — mostra l'impatto completo. */
interface PhaseCDialogProps {
  trader: ProfessionalSummary;
  estimate: ScenarioResult | null;
  loading: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

function PhaseCDialog({ trader, estimate, loading, onConfirm, onCancel }: PhaseCDialogProps) {
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border border-red-700 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
        <h2 className="text-red-400 font-bold text-base flex items-center gap-2">
          <span>⚠️</span>
          <span>Attivazione Fase di Monetizzazione — {trader.name}</span>
        </h2>

        <p className="text-gray-300 text-sm leading-relaxed">
          Stai per attivare la <strong className="text-red-300">Fase C (Monetizzazione)</strong> per
          questo trader. Questa non è una ottimizzazione della strategia: è una scelta deliberata
          di danneggiare i follower a favore del guadagno della piattaforma.
        </p>

        <div className="bg-gray-800 rounded p-3 space-y-1 text-sm">
          <p className="text-gray-400 font-medium mb-2">In questa fase:</p>
          <p className="text-gray-300">• Il trader adotterà operazioni con <strong>rendimento atteso negativo</strong></p>
          <p className="text-gray-300">
            • I <strong className="text-red-300">{trader.followers_count} follower</strong> che lo copiano
            subiranno perdite proporzionali
          </p>
          <p className="text-gray-300">
            • Il trader riceverà un <strong>bonus fisso</strong> per ogni tick,
            indipendentemente dal suo PnL
          </p>
          <p className="text-gray-300">
            • La piattaforma registrerà il differenziale come <strong className="text-green-400">guadagno</strong>
          </p>
        </div>

        <div className="bg-gray-800 rounded p-3 space-y-1 text-sm">
          <div className="flex justify-between text-gray-300">
            <span>Capitale retail attualmente esposto:</span>
            <span className="font-mono text-red-400">
              €{trader.follower_capital_exposed.toFixed(0)}
            </span>
          </div>
          {loading && (
            <p className="text-gray-500 text-xs">Calcolo stima in corso...</p>
          )}
          {!loading && estimate && (
            <>
              <div className="flex justify-between text-gray-300">
                <span>Perdita retail attesa (10 tick):</span>
                <span className="font-mono text-red-400">
                  −€{estimate.expected_retail_loss.toFixed(0)}
                </span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Bonus da pagare al trader:</span>
                <span className="font-mono text-orange-400">
                  −€{estimate.expected_bonus_paid.toFixed(0)}
                </span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>Guadagno netto piattaforma stimato:</span>
                <span className="font-mono text-green-400">
                  +€{estimate.expected_platform_net_gain.toFixed(0)}
                </span>
              </div>
              <div className="flex justify-between text-gray-400 text-xs">
                <span>Intervallo di confidenza:</span>
                <span className="font-mono">
                  [+€{estimate.confidence_interval[0].toFixed(0)} /
                  +€{estimate.confidence_interval[1].toFixed(0)}]
                </span>
              </div>
            </>
          )}
        </div>

        <div className="flex gap-3 pt-2">
          <button
            onClick={onCancel}
            className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 text-sm font-medium rounded transition-colors"
          >
            Annulla
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 py-2 bg-red-800 hover:bg-red-700 text-white text-sm font-bold rounded transition-colors"
          >
            Confermo — Attiva Fase C
          </button>
        </div>
      </div>
    </div>
  );
}

/** Pannello di controllo per ogni trader professionista: cambio fase e strategia. */
export function TraderControlPanel({ professionals, onPhaseChanged }: TraderControlPanelProps) {
  const [pendingPhaseC, setPendingPhaseC] = useState<{
    trader: ProfessionalSummary;
    estimate: ScenarioResult | null;
    loading: boolean;
  } | null>(null);
  const [changingPhase, setChangingPhase] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handlePhaseClick = async (trader: ProfessionalSummary, targetPhase: TraderPhase) => {
    if (targetPhase === trader.phase) return;

    // Fase C richiede dialog di conferma con dati live
    if (targetPhase === 'MONETIZATION') {
      setPendingPhaseC({ trader, estimate: null, loading: true });
      const estimate = await fetchPhaseCEstimate(trader.id);
      setPendingPhaseC({ trader, estimate, loading: false });
      return;
    }

    await executePhaseChange(trader.id, targetPhase);
  };

  const executePhaseChange = async (traderId: string, targetPhase: TraderPhase) => {
    setChangingPhase(traderId);
    setError(null);
    setSuccess(null);
    try {
      await professionalApi.changePhase(traderId, targetPhase);
      const label = PHASE_LABEL[targetPhase];
      setSuccess(`Fase cambiata → ${label}`);
      onPhaseChanged();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? 'Errore durante il cambio di fase.');
    } finally {
      setChangingPhase(null);
    }
  };

  const handleConfirmPhaseC = async () => {
    if (!pendingPhaseC) return;
    const traderId = pendingPhaseC.trader.id;
    setPendingPhaseC(null);
    await executePhaseChange(traderId, 'MONETIZATION');
  };

  return (
    <div className="space-y-4">
      {/* Feedback globale */}
      {error && (
        <p className="text-sm text-red-400 bg-red-950 border border-red-800 rounded p-2">{error}</p>
      )}
      {success && (
        <p className="text-sm text-green-400 bg-green-950 border border-green-800 rounded p-2">{success}</p>
      )}

      {/* Card per ogni trader professionista */}
      {professionals.map((trader) => (
        <div
          key={trader.id}
          className={`rounded-lg border p-4 space-y-3 ${
            trader.phase === 'MONETIZATION'
              ? 'border-red-800 bg-red-950/20'
              : 'border-gray-700 bg-gray-800/50'
          }`}
        >
          {/* Header trader */}
          <div className="flex items-start justify-between">
            <div>
              <p className="text-white font-semibold text-sm">🧑‍💼 {trader.name}</p>
              <p className={`text-xs font-medium ${PHASE_COLOR[trader.phase]}`}>
                {PHASE_LABEL[trader.phase]}
              </p>
            </div>
            <div className="text-right text-xs text-gray-400 space-y-0.5">
              <p>Follower: <span className="text-white">{trader.followers_count}</span></p>
              <p>Capitale esposto: <span className="text-white">€{trader.follower_capital_exposed.toFixed(0)}</span></p>
            </div>
          </div>

          {/* PnL e bonus */}
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="bg-gray-800 rounded p-2 text-center">
              <p className="text-gray-400">PnL Personale</p>
              <p className={`font-mono font-semibold ${trader.pnl_personal >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {trader.pnl_personal >= 0 ? '+' : ''}€{trader.pnl_personal.toFixed(0)}
              </p>
            </div>
            <div className="bg-gray-800 rounded p-2 text-center">
              <p className="text-gray-400">Bonus Ricevuto</p>
              <p className="font-mono font-semibold text-yellow-400">
                +€{trader.bonus_earned.toFixed(0)}
              </p>
            </div>
            <div className="bg-gray-800 rounded p-2 text-center">
              <p className="text-gray-400">Compensazione Tot.</p>
              <p className="font-mono font-semibold text-white">
                +€{trader.total_compensation.toFixed(0)}
              </p>
            </div>
          </div>

          {/* PhaseExplainer — layer didattico TASK_12 */}
          <PhaseExplainer
            phase={trader.phase}
            followersCount={trader.followers_count}
            capitalExposed={trader.follower_capital_exposed}
          />

          {/* Pulsanti cambio fase */}
          <div>
            <p className="text-xs text-gray-500 mb-1">Cambia fase:</p>
            <div className="flex gap-2">
              {ALL_PHASES.map((targetPhase) => {
                const isCurrent = trader.phase === targetPhase;
                const isMonetization = targetPhase === 'MONETIZATION';
                return (
                  <button
                    key={targetPhase}
                    onClick={() => handlePhaseClick(trader, targetPhase)}
                    disabled={isCurrent || changingPhase === trader.id}
                    title={
                      isMonetization
                        ? 'Attivazione Monetizzazione: il trader adotterà strategie con EV negativo. I follower subiranno perdite. La piattaforma riceve il differenziale.'
                        : undefined
                    }
                    className={`flex-1 text-xs py-1.5 rounded font-medium transition-colors ${
                      isCurrent
                        ? 'opacity-40 cursor-not-allowed ' +
                          (isMonetization ? 'bg-red-800 text-white' : 'bg-gray-600 text-gray-300')
                        : isMonetization
                        ? 'bg-red-900 hover:bg-red-800 text-red-200 border border-red-700'
                        : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                    }`}
                  >
                    {targetPhase === 'REPUTATION_BUILD' ? '→ Fase A' :
                     targetPhase === 'FOLLOWER_GROWTH' ? '→ Fase B' :
                     '→ Fase C ⚠️'}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Profilo strategia */}
          <details className="text-xs text-gray-400">
            <summary className="cursor-pointer hover:text-gray-300 transition-colors">
              Parametri strategia corrente
            </summary>
            <div className="mt-2 pl-2 border-l border-gray-700 space-y-0.5 text-gray-400">
              <p>Trader in fase attiva — i parametri variano per fase.</p>
              <p>Trade eseguiti: <span className="text-gray-300">{trader.n_trades}</span></p>
            </div>
          </details>
        </div>
      ))}

      {/* Dialog di conferma Fase C */}
      {pendingPhaseC && (
        <PhaseCDialog
          trader={pendingPhaseC.trader}
          estimate={pendingPhaseC.estimate}
          loading={pendingPhaseC.loading}
          onConfirm={handleConfirmPhaseC}
          onCancel={() => setPendingPhaseC(null)}
        />
      )}
    </div>
  );
}
