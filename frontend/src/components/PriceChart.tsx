import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface PriceChartProps {
  symbol: string;
  history: number[];
  color?: string;
}

/**
 * Grafico lineare del prezzo di un asset nel tempo.
 * Usa Recharts ResponsiveContainer per adattarsi al contenitore padre.
 *
 * @param symbol  - Simbolo dell'asset (es. "SIM-A"), mostrato nel tooltip.
 * @param history - Array di prezzi storici (uno per tick).
 * @param color   - Colore della linea (default: #60a5fa = blue-400).
 */
export function PriceChart({ symbol, history, color = '#60a5fa' }: PriceChartProps) {
  const data = history.map((price, i) => ({ tick: i, price: parseFloat(price.toFixed(4)) }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data} margin={{ top: 4, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey="tick"
          tick={{ fontSize: 10, fill: '#9ca3af' }}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fontSize: 10, fill: '#9ca3af' }}
          width={55}
          tickFormatter={(v: number) => v.toFixed(2)}
        />
        <Tooltip
          contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 6 }}
          labelStyle={{ color: '#9ca3af', fontSize: 11 }}
          itemStyle={{ color: color, fontSize: 12 }}
          formatter={(value) => [(value as number).toFixed(4), symbol] as [string, string]}
          labelFormatter={(label) => `Tick ${label}`}
        />
        <Line
          type="monotone"
          dataKey="price"
          stroke={color}
          strokeWidth={1.5}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
