import { useEffect, useState } from 'react';
import { retailApi } from '../../api/retail';
import type { Trade } from '../../types';

interface RetailVsPlatformSnapshotProps {
  retailId: string;
  retailPnl: number;
}

/**
 * Confronto diretto tra il PnL del retail e il guadagno che la piattaforma
 * ha realizzato attraverso di lui. Spiega la relazione causale tra la perdita
 * dell'utente e il profitto della piattaforma.
 */
export function RetailVsPlatformSnapshot({ retailId, retailPnl }: RetailVsPlatformSnapshotProps) {
  const [trades, setTrades] = useState<Trade[]>([]);

  useEffect(() => {
    if (!retailId) return;
    retailApi.getHistory(retailId).then((r) => setTrades(r.data)).catch(() => {});
  }, [retailId, retailPnl]);

  const copyTrades = trades.filter((t) => t.is_copy);
  const copyPnl = copyTrades.reduce((acc, t) => acc + (t.pnl_realized ?? 0), 0);

  // Il guadagno della piattaforma "su questo retail" è approssimativamente
  // uguale alla perdita realizzata dal retail (relazione 1:1)
  const platformGainFromThisRetail = -retailPnl;
  const copyPct =
    retailPnl < 0 && copyPnl < 0
      ? Math.abs(copyPnl / retailPnl) * 100
      : 0;

  const hasPnl = retailPnl !== 0;

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
        <span>📊</span>
        <span>Il tuo impatto sulla piattaforma</span>
      </h3>

      {!hasPnl ? (
        <p className="text-xs text-gray-500 italic">
          Nessuna operazione eseguita ancora. Avanza qualche tick o esegui un trade.
        </p>
      ) : (
        <div className="space-y-3">
          {/* Confronto PnL */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-800 rounded p-3 text-center">
              <p className="text-xs text-gray-400 mb-1">Il tuo PnL totale</p>
              <p className={`text-lg font-mono font-bold ${
                retailPnl >= 0 ? 'text-green-400' : 'text-red-400'
              }`}>
                {retailPnl >= 0 ? '+' : ''}€{retailPnl.toFixed(2)}
              </p>
            </div>
            <div className="bg-gray-800 rounded p-3 text-center border border-green-900">
              <p className="text-xs text-gray-400 mb-1">Guadagno piattaforma su di te</p>
              <p className={`text-lg font-mono font-bold ${
                platformGainFromThisRetail > 0 ? 'text-green-400' : 'text-gray-400'
              }`}>
                {platformGainFromThisRetail > 0 ? '+' : ''}€{platformGainFromThisRetail.toFixed(2)}
              </p>
            </div>
          </div>

          {/* Nota esplicativa relazione */}
          {retailPnl < 0 && (
            <div className="bg-orange-950/30 border border-orange-800 rounded p-2 text-xs text-orange-300">
              ⚠️ La tua perdita di <strong>€{Math.abs(retailPnl).toFixed(2)}</strong> corrisponde
              approssimativamente al guadagno della piattaforma su di te.
              In questo modello, ogni euro che perdi è un euro che la piattaforma guadagna.
            </div>
          )}

          {/* Analisi copy trades */}
          {copyTrades.length > 0 && (
            <div className="bg-gray-800 rounded p-3 space-y-1 text-xs">
              <p className="text-gray-400 font-medium">Delle tue operazioni in copy:</p>
              <div className="flex justify-between text-gray-300">
                <span>Operazioni copiate eseguite:</span>
                <span className="font-mono">{copyTrades.length}</span>
              </div>
              <div className="flex justify-between text-gray-300">
                <span>PnL da operazioni copy:</span>
                <span className={`font-mono ${copyPnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {copyPnl >= 0 ? '+' : ''}€{copyPnl.toFixed(2)}
                  {copyPct > 0 && (
                    <span className="text-gray-500 ml-1">
                      ({copyPct.toFixed(0)}% della perdita totale)
                    </span>
                  )}
                </span>
              </div>
            </div>
          )}

          {/* Spiegazione didattica */}
          <button
            className="text-xs text-gray-500 hover:text-gray-300 underline underline-offset-2 transition-colors"
            onClick={() => {
              const el = document.getElementById('retail-vs-platform-explainer');
              if (el) el.classList.toggle('hidden');
            }}
          >
            ⓘ Come viene calcolato questo?
          </button>
          <div id="retail-vs-platform-explainer" className="hidden text-xs text-gray-400 bg-gray-800/50 rounded p-2 leading-relaxed">
            Il "guadagno piattaforma su di te" è stimato come il valore opposto del tuo PnL.
            Nel modello simulato, ogni perdita retail viene registrata direttamente come
            guadagno della piattaforma. Il calcolo reale distribuisce le perdite tra tutti
            i retail attivi, ma questa visualizzazione usa la tua perdita come proxy diretto.
          </div>
        </div>
      )}
    </div>
  );
}
