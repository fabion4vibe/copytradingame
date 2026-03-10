import { useEffect, useState } from 'react';
import { professionalApi } from '../../api/professional';
import { retailApi } from '../../api/retail';
import type { ProfessionalSummary, RetailDetail } from '../../types';
import { PhaseGuide } from '../../didactic/PhaseGuide';

interface CopyTradingPanelProps {
  retailId: string;
  onCopyChanged: () => void;
}

/** Mappa le fasi del trader a badge colorati per l'UI. */
const PHASE_BADGE: Record<string, { label: string; className: string }> = {
  REPUTATION_BUILD: { label: 'Fase A', className: 'bg-blue-700 text-blue-100' },
  FOLLOWER_GROWTH: { label: 'Fase B', className: 'bg-yellow-700 text-yellow-100' },
  MONETIZATION: { label: 'Fase C', className: 'bg-red-700 text-red-100' },
};

/** Pannello per gestire il copy trading: visualizza i trader disponibili e le relazioni attive. */
export function CopyTradingPanel({ retailId, onCopyChanged }: CopyTradingPanelProps) {
  const [professionals, setProfessionals] = useState<ProfessionalSummary[]>([]);
  const [retailDetail, setRetailDetail] = useState<RetailDetail | null>(null);
  const [selectedTraderId, setSelectedTraderId] = useState<string | null>(null);
  const [allocationPct, setAllocationPct] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [stopping, setStopping] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const load = () => {
    professionalApi.listTraders().then((r) => setProfessionals(r.data)).catch(() => {});
    retailApi.getTrader(retailId).then((r) => setRetailDetail(r.data)).catch(() => {});
  };

  useEffect(() => {
    load();
  }, [retailId]);

  const copiedIds = new Set(retailDetail?.copied_traders ?? []);

  const handleStartCopy = async () => {
    if (!selectedTraderId) return;
    const pct = parseFloat(allocationPct);
    if (isNaN(pct) || pct <= 0 || pct > 100) {
      setError('Inserisci una percentuale di allocazione valida (1–100).');
      return;
    }
    setSubmitting(true);
    setError(null);
    setSuccess(null);
    try {
      // Il backend si aspetta una frazione 0-1; l'utente inserisce una percentuale 1-100
      await retailApi.startCopy(retailId, selectedTraderId, pct / 100);
      setSuccess(`Copy avviato su ${selectedTraderId} con ${pct}% del capitale.`);
      setSelectedTraderId(null);
      setAllocationPct('');
      load();
      onCopyChanged();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? 'Errore durante l\'avvio del copy trading.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleStopCopy = async (traderId: string) => {
    setStopping(traderId);
    setError(null);
    setSuccess(null);
    try {
      await retailApi.stopCopy(retailId, traderId);
      setSuccess(`Copy interrotto per ${traderId}.`);
      load();
      onCopyChanged();
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? 'Errore durante l\'interruzione del copy.');
    } finally {
      setStopping(null);
    }
  };

  const phaseCTraders = professionals.filter((p) => p.phase === 'MONETIZATION');

  return (
    <div className="space-y-5">

      {/* Guida alle fasi — placeholder didattico */}
      <PhaseGuide />

      {/* Avviso Fase C — sempre visibile quando ci sono trader in monetizzazione */}
      {phaseCTraders.length > 0 && (
        <div className="bg-red-950 border border-red-700 rounded p-3 space-y-2">
          <p className="text-red-400 font-semibold text-sm flex items-center gap-2">
            <span>⚠️</span>
            <span>Trader in Fase C (Monetizzazione) rilevati</span>
          </p>
          <p className="text-red-300 text-xs leading-relaxed">
            I trader in Fase C adottano deliberatamente strategie ad alto rischio che
            tendono a danneggiare i follower. La piattaforma <strong>guadagna</strong> quando
            i follower perdono. Copiare un trader in Fase C espone il tuo capitale a
            perdite significative e prevedibili.
          </p>
          <ul className="text-red-300 text-xs space-y-0.5">
            {phaseCTraders.map((p) => (
              <li key={p.id} className="flex items-center gap-1">
                <span>•</span>
                <span className="font-mono">{p.name}</span>
                <span className="text-red-500">
                  — capitale follower esposto: €{p.follower_capital_exposed.toFixed(0)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Lista relazioni di copy attive */}
      <div>
        <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-2">Copy attivi</h3>
        {copiedIds.size === 0 ? (
          <p className="text-sm text-gray-500 italic">Nessun copy trading attivo.</p>
        ) : (
          <div className="space-y-2">
            {professionals
              .filter((p) => copiedIds.has(p.id))
              .map((p) => {
                const badge = PHASE_BADGE[p.phase];
                return (
                  <div
                    key={p.id}
                    className="flex items-center justify-between bg-gray-800 rounded px-3 py-2"
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded ${badge.className}`}
                      >
                        {badge.label}
                      </span>
                      <span className="text-sm text-white">{p.name}</span>
                      {p.phase === 'MONETIZATION' && (
                        <span className="text-xs text-red-400">⚠️ Fase rischiosa</span>
                      )}
                    </div>
                    <button
                      onClick={() => handleStopCopy(p.id)}
                      disabled={stopping === p.id}
                      className="text-xs bg-red-900 hover:bg-red-800 disabled:opacity-40 text-red-300 px-2 py-1 rounded transition-colors"
                    >
                      {stopping === p.id ? 'Interruzione...' : 'Stop Copy'}
                    </button>
                  </div>
                );
              })}
          </div>
        )}
      </div>

      {/* Tabella trader disponibili */}
      <div>
        <h3 className="text-xs text-gray-400 uppercase tracking-wider mb-2">
          Trader disponibili
        </h3>
        <div className="space-y-2">
          {professionals.map((p) => {
            const badge = PHASE_BADGE[p.phase];
            const isCopied = copiedIds.has(p.id);
            const isSelected = selectedTraderId === p.id;

            return (
              <div key={p.id} className="bg-gray-800 rounded overflow-hidden">
                {/* Riga principale */}
                <div className="flex items-center gap-3 px-3 py-2">
                  <span
                    className={`text-xs font-medium px-2 py-0.5 rounded shrink-0 ${badge.className}`}
                  >
                    {badge.label}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-white font-medium truncate">{p.name}</p>
                    <p className="text-xs text-gray-400">
                      Follower: {p.followers_count} · Capitale esposto: €{p.follower_capital_exposed.toFixed(0)} · PnL: €{p.pnl_personal.toFixed(2)}
                    </p>
                  </div>
                  {isCopied ? (
                    <span className="text-xs text-green-400 shrink-0">✓ Copiato</span>
                  ) : (
                    <button
                      onClick={() =>
                        setSelectedTraderId(isSelected ? null : p.id)
                      }
                      className={`text-xs px-3 py-1 rounded shrink-0 transition-colors ${
                        isSelected
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                      }`}
                    >
                      {isSelected ? 'Annulla' : 'Copia'}
                    </button>
                  )}
                </div>

                {/* Form allocazione — espanso solo per il trader selezionato */}
                {isSelected && !isCopied && (
                  <div className="border-t border-gray-700 px-3 py-3 bg-gray-800/80 space-y-2">
                    <label className="block text-xs text-gray-400">
                      Percentuale del capitale da allocare (1–100%)
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        min="1"
                        max="100"
                        step="1"
                        value={allocationPct}
                        onChange={(e) => setAllocationPct(e.target.value)}
                        placeholder="es. 20"
                        className="flex-1 bg-gray-900 border border-gray-600 text-white text-sm rounded px-3 py-1.5 focus:outline-none focus:border-blue-500"
                      />
                      <button
                        onClick={handleStartCopy}
                        disabled={submitting}
                        className="px-4 py-1.5 bg-blue-700 hover:bg-blue-600 disabled:opacity-40 text-white text-sm font-medium rounded transition-colors"
                      >
                        {submitting ? 'Avvio...' : 'Avvia Copy'}
                      </button>
                    </div>
                    <p className="text-xs text-gray-500">
                      Questa percentuale del tuo saldo verrà replicata proporzionalmente
                      per ogni trade eseguito dal trader selezionato.
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Feedback */}
      {error && (
        <p className="text-sm text-red-400 bg-red-950 border border-red-800 rounded p-2">{error}</p>
      )}
      {success && (
        <p className="text-sm text-green-400 bg-green-950 border border-green-800 rounded p-2">{success}</p>
      )}
    </div>
  );
}
