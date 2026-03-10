import { useEffect, useState } from 'react';
import { retailApi } from '../../api/retail';
import { marketApi } from '../../api/market';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import { ErrorMessage } from '../../components/ErrorMessage';
import { MechanismExplainer } from '../../didactic/MechanismExplainer';
import type { RetailDetail, Asset } from '../../types';

interface PortfolioPanelProps {
  retailId: string;
  tick: number;
}

const fmt = (v: number) =>
  `€${Math.abs(v).toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const pnlColor = (v: number) =>
  v > 0 ? 'text-green-400' : v < 0 ? 'text-red-400' : 'text-gray-400';
const pnlSign = (v: number) => (v >= 0 ? '+' : '-');

/** Mostra bilancio, valore portafoglio, PnL totale e posizioni aperte. */
export function PortfolioPanel({ retailId, tick }: PortfolioPanelProps) {
  const [trader, setTrader] = useState<RetailDetail | null>(null);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    Promise.all([retailApi.getTrader(retailId), marketApi.getAssets()])
      .then(([tRes, aRes]) => {
        if (!cancelled) { setTrader(tRes.data); setAssets(aRes.data); }
      })
      .catch(() => { if (!cancelled) setError('Errore nel caricamento portafoglio.'); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [retailId, tick]);

  if (loading) return <LoadingSpinner message="Caricamento portafoglio..." />;
  if (error || !trader) return <ErrorMessage message={error ?? 'Dati non disponibili.'} />;

  const assetMap = Object.fromEntries(assets.map((a) => [a.id, a]));
  const portfolioValue = trader.balance + Object.entries(trader.portfolio).reduce((sum, [assetId, qty]) => {
    const price = assetMap[assetId]?.current_price ?? 0;
    return sum + qty * price;
  }, 0);
  // Usa i valori calcolati dall'API
  const pnl = trader.total_pnl;

  return (
    <div className="space-y-4">
      {/* Riepilogo finanziario */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-gray-800 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Liquidità</p>
          <p className="text-lg font-bold text-white">{fmt(trader.balance)}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">Valore portafoglio</p>
          <p className="text-lg font-bold text-white">{fmt(trader.portfolio_value)}</p>
        </div>
        <div className="bg-gray-800 rounded-lg p-3">
          <p className="text-xs text-gray-400 mb-1">PnL totale</p>
          <p className={`text-lg font-bold ${pnlColor(pnl)}`}>
            {pnlSign(pnl)}{fmt(pnl)}
          </p>
        </div>
      </div>

      {/* Slot didattico TASK_12 */}
      <MechanismExplainer id="portfolio-pnl" />

      {/* Posizioni aperte */}
      {Object.keys(trader.portfolio).length === 0 ? (
        <p className="text-sm text-gray-500 italic">Nessuna posizione aperta.</p>
      ) : (
        <div>
          <p className="text-xs text-gray-400 mb-2 uppercase tracking-wide">Posizioni aperte</p>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 border-b border-gray-800">
                <th className="text-left pb-1">Asset</th>
                <th className="text-right pb-1">Qtà</th>
                <th className="text-right pb-1">Prezzo medio</th>
                <th className="text-right pb-1">Prezzo attuale</th>
                <th className="text-right pb-1">PnL non realizz.</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(trader.portfolio).map(([assetId, qty]) => {
                const avgBuy = trader.avg_buy_prices[assetId] ?? 0;
                const currentPrice = assetMap[assetId]?.current_price ?? 0;
                const unrealizedPnl = (currentPrice - avgBuy) * qty;
                return (
                  <tr key={assetId} className="border-b border-gray-800/50">
                    <td className="py-1.5 font-mono text-blue-300">{assetId.toUpperCase()}</td>
                    <td className="py-1.5 text-right text-gray-300">{qty.toFixed(4)}</td>
                    <td className="py-1.5 text-right text-gray-300">{fmt(avgBuy)}</td>
                    <td className="py-1.5 text-right text-gray-300">{fmt(currentPrice)}</td>
                    <td className={`py-1.5 text-right font-medium ${pnlColor(unrealizedPnl)}`}>
                      {pnlSign(unrealizedPnl)}{fmt(unrealizedPnl)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
