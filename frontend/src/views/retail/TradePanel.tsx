import { useEffect, useState } from 'react';
import { marketApi } from '../../api/market';
import { retailApi } from '../../api/retail';
import type { Asset } from '../../types';

interface TradePanelProps {
  retailId: string;
  onTradeExecuted: () => void;
}

/** Form per eseguire operazioni manuali di acquisto e vendita. */
export function TradePanel({ retailId, onTradeExecuted }: TradePanelProps) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [selectedAssetId, setSelectedAssetId] = useState('');
  const [action, setAction] = useState<'BUY' | 'SELL'>('BUY');
  const [quantity, setQuantity] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    marketApi.getAssets().then((res) => {
      setAssets(res.data);
      if (res.data.length > 0 && !selectedAssetId) {
        setSelectedAssetId(res.data[0].id);
      }
    }).catch(() => {});
  }, []);

  const currentAsset = assets.find((a) => a.id === selectedAssetId);
  const qty = parseFloat(quantity) || 0;
  const estimatedTotal = currentAsset ? qty * currentAsset.current_price : 0;

  const handleSubmit = async () => {
    if (!selectedAssetId || qty <= 0) {
      setError('Inserisci una quantità valida maggiore di zero.');
      return;
    }
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      await retailApi.executeTrade(retailId, selectedAssetId, action, qty);
      setSuccess(`${action} di ${qty} ${selectedAssetId.toUpperCase()} eseguito con successo.`);
      setQuantity('');
      onTradeExecuted();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? 'Errore durante l\'esecuzione del trade.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Asset */}
      <div>
        <label className="block text-xs text-gray-400 mb-1">Asset</label>
        <select
          value={selectedAssetId}
          onChange={(e) => setSelectedAssetId(e.target.value)}
          className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded px-3 py-2 focus:outline-none focus:border-blue-500"
        >
          {assets.map((a) => (
            <option key={a.id} value={a.id}>{a.symbol}</option>
          ))}
        </select>
      </div>

      {/* Azione */}
      <div>
        <label className="block text-xs text-gray-400 mb-1">Azione</label>
        <div className="flex gap-2">
          {(['BUY', 'SELL'] as const).map((a) => (
            <button
              key={a}
              onClick={() => setAction(a)}
              className={`flex-1 py-2 rounded text-sm font-medium transition-colors ${
                action === a
                  ? a === 'BUY' ? 'bg-green-700 text-white' : 'bg-red-700 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {a === 'BUY' ? '▲ Acquista' : '▼ Vendi'}
            </button>
          ))}
        </div>
      </div>

      {/* Quantità */}
      <div>
        <label className="block text-xs text-gray-400 mb-1">Quantità</label>
        <input
          type="number"
          min="0"
          step="0.01"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          placeholder="es. 10.00"
          className="w-full bg-gray-800 border border-gray-700 text-white text-sm rounded px-3 py-2 focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Info prezzo */}
      {currentAsset && (
        <div className="bg-gray-800/50 rounded p-3 text-sm space-y-1">
          <div className="flex justify-between text-gray-400">
            <span>Prezzo corrente</span>
            <span className="text-white font-mono">€{currentAsset.current_price.toFixed(4)}</span>
          </div>
          <div className="flex justify-between text-gray-400">
            <span>Totale stimato</span>
            <span className="text-white font-mono">€{estimatedTotal.toFixed(2)}</span>
          </div>
        </div>
      )}

      {/* Feedback */}
      {error && (
        <p className="text-sm text-red-400 bg-red-950 border border-red-800 rounded p-2">{error}</p>
      )}
      {success && (
        <p className="text-sm text-green-400 bg-green-950 border border-green-800 rounded p-2">{success}</p>
      )}

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={submitting || qty <= 0}
        className="w-full py-2 bg-blue-700 hover:bg-blue-600 disabled:opacity-40 text-white font-medium text-sm rounded transition-colors"
      >
        {submitting ? 'Esecuzione...' : 'Esegui Trade'}
      </button>
    </div>
  );
}
