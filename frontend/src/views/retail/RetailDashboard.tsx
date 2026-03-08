import { useEffect, useState } from 'react';
import { RetailSelector } from './RetailSelector';
import { PortfolioPanel } from './PortfolioPanel';
import { TradePanel } from './TradePanel';
import { CopyTradingPanel } from './CopyTradingPanel';
import { TradeHistoryPanel } from './TradeHistoryPanel';
import { RetailVsPlatformSnapshot } from '../../didactic/RetailVsPlatformSnapshot';
import { retailApi } from '../../api/retail';
import type { RetailSummary } from '../../types';

interface RetailDashboardProps {
  /** Tick corrente — ricevuto da App per aggiornare i pannelli senza rimontare il componente. */
  tick: number;
}

/** Dashboard principale del trader retail: portfolio, trading manuale, copy trading e storico. */
export function RetailDashboard({ tick }: RetailDashboardProps) {
  const [traders, setTraders] = useState<RetailSummary[]>([]);
  const [selectedRetailId, setSelectedRetailId] = useState('');
  const [currentSummary, setCurrentSummary] = useState<RetailSummary | null>(null);

  // Carica la lista di tutti i trader retail
  useEffect(() => {
    retailApi.listTraders().then((r) => {
      setTraders(r.data);
      if (r.data.length > 0 && !selectedRetailId) {
        setSelectedRetailId(r.data[0].id);
      }
    }).catch(() => {});
  }, [tick]);

  // Aggiorna il summary del trader selezionato per il pannello didattico
  useEffect(() => {
    if (!selectedRetailId) return;
    const found = traders.find((t) => t.id === selectedRetailId);
    if (found) setCurrentSummary(found);
  }, [selectedRetailId, traders]);

  // Callback condiviso per ricaricare la lista dopo trade / copy
  const handleRefresh = () => {
    retailApi.listTraders().then((r) => setTraders(r.data)).catch(() => {});
  };

  return (
    <div className="space-y-6">

      {/* Selettore trader */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
        <h2 className="text-sm font-semibold text-gray-300 mb-3">Trader Retail</h2>
        <RetailSelector
          traders={traders}
          selectedId={selectedRetailId}
          onChange={(id) => {
            setSelectedRetailId(id);
            setCurrentSummary(null);
          }}
        />
      </div>

      {selectedRetailId ? (
        <>
          {/* Griglia principale: portfolio + trade panel */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <h2 className="text-sm font-semibold text-gray-300 mb-3">Portfolio</h2>
              <PortfolioPanel
                retailId={selectedRetailId}
                tick={tick}
              />
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <h2 className="text-sm font-semibold text-gray-300 mb-3">Esegui Trade</h2>
              <TradePanel
                retailId={selectedRetailId}
                onTradeExecuted={handleRefresh}
              />
            </div>
          </div>

          {/* Copy Trading */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <h2 className="text-sm font-semibold text-gray-300 mb-3">Copy Trading</h2>
            <CopyTradingPanel
              retailId={selectedRetailId}
              onCopyChanged={handleRefresh}
            />
          </div>

          {/* Storico operazioni */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <h2 className="text-sm font-semibold text-gray-300 mb-3">
              Storico Operazioni
            </h2>
            <TradeHistoryPanel retailId={selectedRetailId} tick={tick} />
          </div>

          {/* Snapshot didattico: retail vs piattaforma — layer didattico TASK_12 */}
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
            <RetailVsPlatformSnapshot
              retailId={selectedRetailId}
              retailPnl={currentSummary?.total_pnl ?? 0}
            />
          </div>
        </>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 text-center text-gray-500 text-sm">
          Seleziona un trader retail per visualizzare la dashboard.
        </div>
      )}
    </div>
  );
}
