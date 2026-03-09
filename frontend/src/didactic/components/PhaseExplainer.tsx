import type { TraderPhase } from '../../types';
import { phaseInfo } from '../content/phases';

interface PhaseExplainerProps {
  phase: TraderPhase;
  followersCount: number;
  capitalExposed: number;
}

/**
 * Pannello descrittivo della fase corrente per la dashboard gestore.
 * Spiega in linguaggio diretto cosa sta facendo il trader e quale impatto ha sui follower.
 */
export function PhaseExplainer({ phase, followersCount, capitalExposed }: PhaseExplainerProps) {
  const info = phaseInfo[phase];

  const dynamicText: Record<TraderPhase, string> = {
    REPUTATION_BUILD:
      `Il trader sta costruendo credibilità con operazioni a rendimento atteso positivo. `
      + `Ha ${followersCount} follower per un totale di €${capitalExposed.toFixed(0)} esposti. `
      + `Obiettivo: raggiungere un numero sufficiente di follower per passare alla fase successiva.`,
    FOLLOWER_GROWTH:
      `Il trader è in fase di crescita. Mantiene buone performance per attrarre più capitale. `
      + `${followersCount} follower attivi, €${capitalExposed.toFixed(0)} esposti. `
      + `Più follower si aggiungono ora, maggiore sarà l'impatto in Fase C.`,
    MONETIZATION:
      `⚠️ Fase attiva. Il trader sta eseguendo operazioni con rendimento atteso negativo. `
      + `I ${followersCount} follower che lo copiano stanno perdendo capitale. `
      + `Capitale retail a rischio: €${capitalExposed.toFixed(0)}. Bonus fisso attivo per ogni tick.`,
  };

  const bgClass =
    phase === 'REPUTATION_BUILD'
      ? 'bg-blue-950/30 border-blue-800'
      : phase === 'FOLLOWER_GROWTH'
      ? 'bg-yellow-950/30 border-yellow-800'
      : 'bg-red-950/30 border-red-800';

  return (
    <div className={`rounded border px-3 py-2 text-xs ${bgClass}`}>
      <p className={`font-semibold mb-1 ${info.colorClass}`}>
        {info.emoji} {info.label}
      </p>
      <p className="text-gray-300 leading-relaxed">{dynamicText[phase]}</p>
    </div>
  );
}
