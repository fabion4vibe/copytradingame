/** Testi per PhaseGuide e PhaseExplainer. */

import type { TraderPhase } from '../../types';

export interface PhaseInfo {
  label: string;
  shortLabel: string;
  emoji: string;
  tagline: string;
  description: string;
  /** Dal punto di vista del gestore */
  managerView: string;
  colorClass: string;
}

export const phaseInfo: Record<TraderPhase, PhaseInfo> = {
  REPUTATION_BUILD: {
    label: 'Fase A — Costruzione Reputazione',
    shortLabel: 'Fase A',
    emoji: '🔵',
    tagline: 'Costruisce credibilità',
    description:
      'Il trader adotta strategie con rendimento atteso positivo. Le sue performance sembrano eccellenti. '
      + 'L\'obiettivo è costruire fiducia e attrarre i primi follower.',
    managerView:
      'Il trader sta costruendo credibilità. Le sue operazioni hanno rendimento atteso positivo. '
      + 'L\'obiettivo è raggiungere un numero sufficiente di follower per passare alla fase successiva.',
    colorClass: 'text-blue-400',
  },
  FOLLOWER_GROWTH: {
    label: 'Fase B — Crescita Follower',
    shortLabel: 'Fase B',
    emoji: '🟡',
    tagline: 'Attrae follower',
    description:
      'Il trader mantiene buone performance per attrarre più copiatori. '
      + 'Più capitale retail viene esposto attraverso il copy trading.',
    managerView:
      'Il trader è in fase di crescita. Mantiene buone performance per attrarre più capitale. '
      + 'Più follower significa più capitale esposto e maggiore impatto nella fase successiva.',
    colorClass: 'text-yellow-400',
  },
  MONETIZATION: {
    label: 'Fase C — Monetizzazione',
    shortLabel: 'Fase C',
    emoji: '🔴',
    tagline: 'Monetizza a spese dei follower',
    description:
      'Il trader adotta operazioni con rendimento atteso negativo. '
      + 'I follower che lo copiano subiscono perdite proporzionali. '
      + 'Il trader riceve un bonus fisso per ogni tick indipendentemente dal suo PnL.',
    managerView:
      'Fase attiva. Il trader sta eseguendo operazioni con rendimento atteso negativo. '
      + 'I follower stanno perdendo capitale. Il bonus per tick è attivo.',
    colorClass: 'text-red-400',
  },
};

export const phaseTimelineSteps = [
  {
    phase: 'REPUTATION_BUILD' as TraderPhase,
    step: 1,
    title: 'Fase A',
    subtitle: 'Costruisce reputazione',
    detail: 'Operazioni positive → follower in crescita',
  },
  {
    phase: 'FOLLOWER_GROWTH' as TraderPhase,
    step: 2,
    title: 'Fase B',
    subtitle: 'Attrae follower',
    detail: 'Performance buone → più capitale esposto',
  },
  {
    phase: 'MONETIZATION' as TraderPhase,
    step: 3,
    title: 'Fase C',
    subtitle: 'Monetizza a loro spese',
    detail: 'Operazioni negative → follower perdono',
  },
];
