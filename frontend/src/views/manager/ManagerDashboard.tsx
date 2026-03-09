import { useEffect, useState } from 'react';
import { managerApi } from '../../api/manager';
import { professionalApi } from '../../api/professional';
import type { PlatformOverview, PlatformPnL, CopyStats, ProfessionalSummary } from '../../types';
import { PlatformKpiPanel } from './PlatformKpiPanel';
import { TraderControlPanel } from './TraderControlPanel';
import { AlgorithmPanel } from './AlgorithmPanel';
import { CopyFlowPanel } from './CopyFlowPanel';
import { PlatformPnLChart } from './PlatformPnLChart';
import { HowItWorks } from '../../didactic/HowItWorks';
import { LoadingSpinner } from '../../components/LoadingSpinner';

interface ManagerDashboardProps {
  /** Tick corrente — ricevuto da App per aggiornare i pannelli senza rimontare il componente. */
  tick: number;
}

/** Dashboard principale del gestore della piattaforma. */
export function ManagerDashboard({ tick }: ManagerDashboardProps) {
  const [overview, setOverview] = useState<PlatformOverview | null>(null);
  const [pnlData, setPnlData] = useState<PlatformPnL | null>(null);
  const [copyStats, setCopyStats] = useState<CopyStats | null>(null);
  const [professionals, setProfessionals] = useState<ProfessionalSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [howItWorksOpen, setHowItWorksOpen] = useState(false);

  const loadData = async () => {
    try {
      const [overviewRes, pnlRes, copyRes, prosRes] = await Promise.all([
        managerApi.getOverview(),
        managerApi.getPnl(),
        managerApi.getCopyStats(),
        professionalApi.listTraders(),
      ]);
      setOverview(overviewRes.data);
      setPnlData(pnlRes.data);
      setCopyStats(copyRes.data);
      setProfessionals(prosRes.data);
    } catch {
      // se un'API fallisce, i dati precedenti restano visibili
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [tick]);

  if (loading && !overview) {
    return <LoadingSpinner message="Caricamento dashboard gestore..." />;
  }

  if (!overview) {
    return (
      <div className="text-center text-gray-500 text-sm py-10">
        Impossibile caricare i dati della piattaforma.
      </div>
    );
  }

  return (
    <div className="space-y-5">

      {/* Header con pulsante "Come funziona" */}
      <div className="flex items-center justify-between">
        <h1 className="text-base font-bold text-white">Dashboard Gestore</h1>
        <button
          onClick={() => setHowItWorksOpen(true)}
          className="text-xs px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-600 text-gray-300 rounded transition-colors"
        >
          ? Come funziona la piattaforma
        </button>
      </div>

      {/* Banner KPI */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
        <PlatformKpiPanel overview={overview} />
      </div>

      {/* Griglia centrale: controllo trader | algoritmo */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">
            Controllo Trader Professionisti
          </h2>
          <TraderControlPanel
            professionals={professionals}
            onPhaseChanged={loadData}
          />
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">
            Motore Algoritmico
          </h2>
          <AlgorithmPanel tick={tick} onActionApplied={loadData} />
        </div>
      </div>

      {/* Fila inferiore: flusso copy | grafico PnL */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">
            Flusso Copy Trading
          </h2>
          {copyStats ? (
            <CopyFlowPanel copyStats={copyStats} professionals={professionals} />
          ) : (
            <p className="text-sm text-gray-500 italic">Caricamento...</p>
          )}
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">
            Evoluzione PnL Piattaforma
          </h2>
          {pnlData ? (
            <PlatformPnLChart pnlData={pnlData} />
          ) : (
            <p className="text-sm text-gray-500 italic">Caricamento...</p>
          )}
        </div>
      </div>

      {/* Pannello "Come funziona" — placeholder TASK_12 */}
      <HowItWorks open={howItWorksOpen} onClose={() => setHowItWorksOpen(false)} />
    </div>
  );
}
