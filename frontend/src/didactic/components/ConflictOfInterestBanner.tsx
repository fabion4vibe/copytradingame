import type { AppRole } from '../../types';

interface ConflictOfInterestBannerProps {
  role: AppRole;
}

const CONTENT: Record<AppRole, { icon: string; text: string; className: string }> = {
  retail: {
    icon: '⚠️',
    text: 'Stai usando una piattaforma didattica simulata. I trader professionisti che puoi copiare sono controllati dalla piattaforma. Le loro strategie possono essere modificate per generare perdite nei tuoi confronti.',
    className: 'bg-orange-950 border-orange-700 text-orange-200',
  },
  manager: {
    icon: '🏢',
    text: 'Stai osservando la piattaforma dal punto di vista del gestore. Hai il controllo diretto dei trader professionisti e dei loro comportamenti. Le tue decisioni influenzano direttamente il capitale dei retail.',
    className: 'bg-blue-950 border-blue-800 text-blue-200',
  },
};

/**
 * Banner fisso in cima alla dashboard — non dismissibile.
 * Esplicita il conflitto di interesse dal punto di vista del ruolo attivo.
 */
export function ConflictOfInterestBanner({ role }: ConflictOfInterestBannerProps) {
  const { icon, text, className } = CONTENT[role];

  return (
    <div className={`border rounded-lg px-4 py-2.5 text-xs leading-relaxed ${className}`}>
      <span className="mr-2">{icon}</span>
      {text}
    </div>
  );
}
