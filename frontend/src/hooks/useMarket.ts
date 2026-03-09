import { useState, useEffect, useCallback } from 'react';
import { marketApi } from '../api/market';
import type { Asset, MarketStatus } from '../types';

interface UseMarketReturn {
  assets: Asset[];
  status: MarketStatus | null;
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

/**
 * Hook per accedere ai dati di mercato correnti.
 * Si aggiorna ogni volta che cambia `tick` (passato come dipendenza).
 *
 * @param tick - Tick corrente (passato da App per triggerare il re-fetch).
 */
export function useMarket(tick: number): UseMarketReturn {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [status, setStatus] = useState<MarketStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    try {
      setError(null);
      const [assetsRes, statusRes] = await Promise.all([
        marketApi.getAssets(),
        marketApi.getStatus(),
      ]);
      setAssets(assetsRes.data);
      setStatus(statusRes.data);
    } catch {
      setError('Impossibile connettersi al backend. Assicurati che il server sia in esecuzione.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetch();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick]);

  return { assets, status, loading, error, refresh: fetch };
}
