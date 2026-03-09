import { useEffect, useRef } from 'react';

/**
 * Hook generico per eseguire una funzione a intervallo regolare.
 *
 * @param fn          - Funzione da eseguire ad ogni intervallo.
 * @param intervalMs  - Intervallo in millisecondi.
 * @param enabled     - Se false, il polling è sospeso.
 */
export function usePolling(
  fn: () => void,
  intervalMs: number,
  enabled: boolean
): void {
  // Manteniamo sempre il ref aggiornato all'ultima versione di fn
  // per evitare stale closures senza ricreare l'intervallo.
  const fnRef = useRef(fn);
  fnRef.current = fn;

  useEffect(() => {
    if (!enabled) return;
    const id = setInterval(() => fnRef.current(), intervalMs);
    return () => clearInterval(id);
  }, [intervalMs, enabled]);
}
