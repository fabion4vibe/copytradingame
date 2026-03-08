import type { PlatformOverview } from '../../types';
import { MetricExplainer } from '../../didactic/MetricExplainer';

interface PlatformKpiPanelProps {
  overview: PlatformOverview;
}

interface KpiCardProps {
  label: string;
  value: string;
  metricId: string;
  highlight?: 'positive' | 'negative' | 'warning' | 'neutral';
}

/** Singola card KPI con icona ⓘ per il MetricExplainer (placeholder TASK_12). */
function KpiCard({ label, value, metricId, highlight = 'neutral' }: KpiCardProps) {
  const valueColor =
    highlight === 'positive'
      ? 'text-green-400'
      : highlight === 'negative'
      ? 'text-red-400'
      : highlight === 'warning'
      ? 'text-yellow-400'
      : 'text-white';

  return (
    <div className="bg-gray-800 rounded-lg px-4 py-3 flex-1 min-w-[140px]">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-gray-400">{label}</span>
        {/* Slot MetricExplainer — implementazione in TASK_12 */}
        <MetricExplainer metricId={metricId} />
      </div>
      <p className={`text-lg font-mono font-semibold ${valueColor}`}>{value}</p>
    </div>
  );
}

/** Banner orizzontale con le 4 metriche chiave della piattaforma. */
export function PlatformKpiPanel({ overview }: PlatformKpiPanelProps) {
  const {
    platform_net,
    total_retail_capital,
    copy_penetration_pct,
    n_retail_losing,
    total_capital_in_copy,
  } = overview;

  // Stima del totale retail per la card "Retail in Perdita" come denominatore
  // La vista mostra il conteggio assoluto perché n_retail_traders non è esposto nell'overview
  const copyPct = (copy_penetration_pct * 100).toFixed(1);
  const capitalInCopy = total_capital_in_copy.toFixed(0);

  return (
    <div className="flex flex-wrap gap-3">
      <KpiCard
        label="PnL Netto Piattaforma"
        value={`${platform_net >= 0 ? '+' : ''}€${platform_net.toFixed(0)}`}
        metricId="platform-net-pnl"
        highlight={platform_net >= 0 ? 'positive' : 'negative'}
      />
      <KpiCard
        label="Capitale Retail Totale"
        value={`€${total_retail_capital.toFixed(0)}`}
        metricId="total-retail-capital"
        highlight="neutral"
      />
      <KpiCard
        label="Capitale in Copy"
        value={`€${capitalInCopy} (${copyPct}%)`}
        metricId="copy-penetration"
        highlight={copy_penetration_pct > 0.5 ? 'warning' : 'neutral'}
      />
      <div
        className={`bg-gray-800 rounded-lg px-4 py-3 flex-1 min-w-[140px] ${
          n_retail_losing > 0 ? 'border border-red-800' : ''
        }`}
      >
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-gray-400">Retail in Perdita</span>
          <MetricExplainer metricId="retail-losing-count" />
        </div>
        <p className="text-lg font-mono font-semibold text-red-400">
          {n_retail_losing}
          <span className="text-sm text-gray-500 ml-1">trader</span>
        </p>
      </div>
    </div>
  );
}
