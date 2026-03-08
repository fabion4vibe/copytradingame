import { useEffect, useState } from 'react';
import { retailApi } from '../../api/retail';
import type { Trade } from '../../types';

interface TradeHistoryPanelProps {
  retailId: string;
  /** Tick corrente — usato per aggiornare la lista dopo ogni operazione. */
  tick: number;
}

type FilterMode = 'all' | 'manual' | 'copy';

const PAGE_SIZE = 20;

/** Pannello con la lista paginata delle operazioni eseguite dal trader retail. */
export function TradeHistoryPanel({ retailId, tick }: TradeHistoryPanelProps) {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [filter, setFilter] = useState<FilterMode>('all');
  const [page, setPage] = useState(0);

  useEffect(() => {
    retailApi.getHistory(retailId).then((r) => setTrades(r.data)).catch(() => {});
  }, [retailId, tick]);

  // Applica il filtro
  const filtered = trades.filter((t) => {
    if (filter === 'manual') return !t.is_copy;
    if (filter === 'copy') return t.is_copy;
    return true;
  });

  // Ordina dal più recente al più vecchio (tick decrescente, poi timestamp)
  const sorted = [...filtered].reverse();

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE);
  const paginated = sorted.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  const handleFilterChange = (f: FilterMode) => {
    setFilter(f);
    setPage(0);
  };

  return (
    <div className="space-y-3">
      {/* Filtri */}
      <div className="flex gap-2 text-xs">
        {(['all', 'manual', 'copy'] as FilterMode[]).map((f) => (
          <button
            key={f}
            onClick={() => handleFilterChange(f)}
            className={`px-3 py-1 rounded transition-colors ${
              filter === f
                ? 'bg-blue-700 text-white'
                : 'bg-gray-800 text-gray-400 hover:text-white'
            }`}
          >
            {f === 'all' ? 'Tutti' : f === 'manual' ? 'Manuali' : 'Copy'}
          </button>
        ))}
        <span className="ml-auto text-gray-500 self-center">
          {filtered.length} operazioni totali
        </span>
      </div>

      {/* Tabella */}
      {paginated.length === 0 ? (
        <p className="text-sm text-gray-500 italic">Nessuna operazione trovata.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead>
              <tr className="text-gray-400 border-b border-gray-700">
                <th className="py-2 pr-3">Tipo</th>
                <th className="py-2 pr-3">Asset</th>
                <th className="py-2 pr-3">Azione</th>
                <th className="py-2 pr-3 text-right">Qty</th>
                <th className="py-2 pr-3 text-right">Prezzo</th>
                <th className="py-2 text-right">PnL</th>
              </tr>
            </thead>
            <tbody>
              {paginated.map((t) => (
                <tr
                  key={t.id}
                  className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors"
                >
                  {/* Badge manuale / copy */}
                  <td className="py-1.5 pr-3">
                    {t.is_copy ? (
                      <span
                        className="bg-purple-900 text-purple-300 px-1.5 py-0.5 rounded text-[10px] font-medium"
                        title={`Copiato da: ${t.copied_from ?? 'sconosciuto'}`}
                      >
                        📋 Copy
                      </span>
                    ) : (
                      <span className="bg-gray-800 text-gray-400 px-1.5 py-0.5 rounded text-[10px]">
                        Manuale
                      </span>
                    )}
                  </td>
                  <td className="py-1.5 pr-3 font-mono text-gray-300">
                    {t.asset_id.toUpperCase()}
                  </td>
                  <td className="py-1.5 pr-3">
                    <span
                      className={
                        t.action === 'BUY' ? 'text-green-400' : 'text-red-400'
                      }
                    >
                      {t.action === 'BUY' ? '▲ BUY' : '▼ SELL'}
                    </span>
                  </td>
                  <td className="py-1.5 pr-3 text-right font-mono text-gray-300">
                    {t.quantity.toFixed(2)}
                  </td>
                  <td className="py-1.5 pr-3 text-right font-mono text-gray-300">
                    €{t.price.toFixed(4)}
                  </td>
                  <td className="py-1.5 text-right font-mono">
                    {t.pnl_realized !== null && t.pnl_realized !== undefined ? (
                      <span
                        className={
                          t.pnl_realized >= 0 ? 'text-green-400' : 'text-red-400'
                        }
                      >
                        {t.pnl_realized >= 0 ? '+' : ''}
                        {t.pnl_realized.toFixed(2)}
                      </span>
                    ) : (
                      <span className="text-gray-600">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Nota didattica per le operazioni copy */}
      {filter !== 'manual' && filtered.some((t) => t.is_copy) && (
        <p className="text-xs text-purple-400 bg-purple-950/40 border border-purple-800 rounded p-2">
          <strong>📋 Copy trade:</strong> queste operazioni sono state eseguite automaticamente
          replicando le mosse di un trader professionista. Il costo (o guadagno) è proporzionale
          alla percentuale di allocazione scelta.
        </p>
      )}

      {/* Paginazione */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between text-xs text-gray-400 pt-1">
          <button
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-2 py-1 bg-gray-800 rounded disabled:opacity-40 hover:bg-gray-700 transition-colors"
          >
            ← Prec
          </button>
          <span>
            Pag. {page + 1} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="px-2 py-1 bg-gray-800 rounded disabled:opacity-40 hover:bg-gray-700 transition-colors"
          >
            Succ →
          </button>
        </div>
      )}
    </div>
  );
}
