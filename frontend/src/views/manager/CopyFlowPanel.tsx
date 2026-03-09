import type { CopyStats, ProfessionalSummary, TraderPhase } from '../../types';

interface CopyFlowPanelProps {
  copyStats: CopyStats;
  professionals: ProfessionalSummary[];
}

const PHASE_LABEL: Record<TraderPhase, string> = {
  REPUTATION_BUILD: '🔵 Fase A',
  FOLLOWER_GROWTH: '🟡 Fase B',
  MONETIZATION: '🔴 Fase C',
};

const PHASE_ROW_CLASS: Record<TraderPhase, string> = {
  REPUTATION_BUILD: '',
  FOLLOWER_GROWTH: '',
  MONETIZATION: 'bg-red-950/30 border-l-2 border-red-700',
};

/** Tabella aggregata del flusso copy trading con barra di esposizione relativa. */
export function CopyFlowPanel({ copyStats, professionals }: CopyFlowPanelProps) {
  const { total_capital_in_copy, by_professional } = copyStats;

  // Ordina: Fase C prima, poi per capitale esposto decrescente
  const rows = professionals
    .filter((p) => by_professional[p.id] !== undefined)
    .map((p) => {
      const stats = by_professional[p.id];
      return {
        id: p.id,
        name: p.name,
        phase: p.phase,
        followers: stats.followers,
        capital_exposed: stats.capital_exposed,
        pct_of_total: total_capital_in_copy > 0
          ? (stats.capital_exposed / total_capital_in_copy) * 100
          : 0,
      };
    })
    .sort((a, b) => {
      if (a.phase === 'MONETIZATION' && b.phase !== 'MONETIZATION') return -1;
      if (b.phase === 'MONETIZATION' && a.phase !== 'MONETIZATION') return 1;
      return b.capital_exposed - a.capital_exposed;
    });

  if (rows.length === 0) {
    return (
      <p className="text-sm text-gray-500 italic">
        Nessuna relazione di copy trading attiva.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex justify-between text-xs text-gray-400">
        <span>
          Relazioni attive: <strong className="text-white">{copyStats.total_active_relations}</strong>
        </span>
        <span>
          Capitale totale in copy:{' '}
          <strong className="text-white">€{total_capital_in_copy.toFixed(0)}</strong>
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs text-left">
          <thead>
            <tr className="text-gray-400 border-b border-gray-700">
              <th className="py-2 pr-3">Trader</th>
              <th className="py-2 pr-3">Fase</th>
              <th className="py-2 pr-3 text-right">Follower</th>
              <th className="py-2 pr-3 text-right">Capitale Esposto</th>
              <th className="py-2">% del Totale</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.id}
                className={`border-b border-gray-800 ${PHASE_ROW_CLASS[row.phase]}`}
              >
                <td className="py-2 pr-3 text-white font-medium">{row.name}</td>
                <td className="py-2 pr-3">
                  <span className={row.phase === 'MONETIZATION' ? 'text-red-400 font-semibold' : 'text-gray-300'}>
                    {PHASE_LABEL[row.phase]}
                  </span>
                </td>
                <td className="py-2 pr-3 text-right font-mono text-gray-300">
                  {row.followers}
                </td>
                <td className="py-2 pr-3 text-right font-mono text-gray-300">
                  €{row.capital_exposed.toFixed(0)}
                </td>
                <td className="py-2 min-w-[100px]">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-gray-700 rounded overflow-hidden">
                      <div
                        className={`h-full rounded ${
                          row.phase === 'MONETIZATION' ? 'bg-red-600' : 'bg-blue-600'
                        }`}
                        style={{ width: `${Math.min(100, row.pct_of_total)}%` }}
                      />
                    </div>
                    <span className="text-gray-400 w-8 text-right">
                      {row.pct_of_total.toFixed(0)}%
                    </span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {rows.some((r) => r.phase === 'MONETIZATION') && (
        <p className="text-xs text-red-400 bg-red-950/40 border border-red-800 rounded p-2">
          🔴 I trader in <strong>Fase C</strong> stanno attivamente perdendo capitale
          per i follower. Il capitale esposto su questi trader genera perdite retail
          che si convertono in guadagno per la piattaforma.
        </p>
      )}
    </div>
  );
}
