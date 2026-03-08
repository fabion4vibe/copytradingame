import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import type { PlatformPnL } from '../../types';

interface PlatformPnLChartProps {
  pnlData: PlatformPnL;
}

/** Grafico a tre linee: PnL lordo (commissioni da retail), bonus pagati, PnL netto piattaforma. */
export function PlatformPnLChart({ pnlData }: PlatformPnLChartProps) {
  const history = pnlData.history;

  if (history.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-500 text-sm italic">
        Nessun dato disponibile — avvia la simulazione.
      </div>
    );
  }

  // Aggiunge la metrica bonus_paid se disponibile (la calcoliamo come pnl - net)
  const chartData = history.map((entry) => ({
    tick: entry.tick,
    pnl_lordo: parseFloat(entry.pnl.toFixed(2)),
    pnl_netto: parseFloat(entry.net.toFixed(2)),
    bonus_pagati: parseFloat((entry.pnl - entry.net).toFixed(2)),
  }));

  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-500">
        <span className="text-green-400">■</span> PnL netto &nbsp;
        <span className="text-blue-400">■</span> Commissioni (perdite retail) &nbsp;
        <span className="text-red-400">■</span> Bonus pagati ai trader
      </p>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="tick"
            tick={{ fill: '#9ca3af', fontSize: 11 }}
            label={{ value: 'Tick', position: 'insideBottomRight', offset: -4, fill: '#6b7280', fontSize: 10 }}
          />
          <YAxis
            tick={{ fill: '#9ca3af', fontSize: 11 }}
            tickFormatter={(v: number) => `€${v.toFixed(0)}`}
            width={60}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 4 }}
            labelStyle={{ color: '#9ca3af', fontSize: 11 }}
            itemStyle={{ fontSize: 11 }}
            formatter={(value: number, name: string) => {
              const labels: Record<string, string> = {
                pnl_netto: 'PnL Netto',
                pnl_lordo: 'Commissioni (perdite retail)',
                bonus_pagati: 'Bonus pagati',
              };
              return [`€${value.toFixed(2)}`, labels[name] ?? name];
            }}
          />
          <Legend
            formatter={(value) => {
              const labels: Record<string, string> = {
                pnl_netto: 'PnL Netto',
                pnl_lordo: 'Commissioni',
                bonus_pagati: 'Bonus Pagati',
              };
              return <span style={{ fontSize: 11, color: '#9ca3af' }}>{labels[value] ?? value}</span>;
            }}
          />
          <Line
            type="monotone"
            dataKey="pnl_lordo"
            stroke="#60a5fa"
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="bonus_pagati"
            stroke="#f87171"
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="pnl_netto"
            stroke="#34d399"
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
