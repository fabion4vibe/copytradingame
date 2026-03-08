import { useState } from 'react';
import { mechanisms } from '../content/mechanisms';
import type { MechanismId } from '../content/mechanisms';

interface MechanismExplainerProps {
  id: MechanismId;
  defaultOpen?: boolean;
}

const BORDER_COLOR: Record<string, string> = {
  blue: 'border-blue-600 bg-blue-950/30',
  orange: 'border-orange-500 bg-orange-950/30',
  red: 'border-red-700 bg-red-950/30',
};

const KEY_POINT_COLOR: Record<string, string> = {
  blue: 'text-blue-300',
  orange: 'text-orange-300',
  red: 'text-red-300',
};

/**
 * Pannello collassabile che spiega un meccanismo in linguaggio semplice.
 * Il bordo sinistro colorato segnala visivamente il tipo di contenuto.
 */
export function MechanismExplainer({ id, defaultOpen = false }: MechanismExplainerProps) {
  const [open, setOpen] = useState(defaultOpen);
  const content = mechanisms[id];

  if (!content) return null;

  const borderClass = BORDER_COLOR[content.color] ?? BORDER_COLOR.blue;
  const keyClass = KEY_POINT_COLOR[content.color] ?? KEY_POINT_COLOR.blue;

  return (
    <div className={`border-l-4 rounded-r pl-3 py-2 pr-3 text-xs ${borderClass}`}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 w-full text-left text-gray-300 hover:text-white transition-colors"
      >
        <span className="text-gray-500">{open ? '▼' : '▶'}</span>
        <span className="font-medium">ⓘ {content.title}</span>
      </button>

      {open && (
        <div className="mt-2 space-y-2">
          <p className="text-gray-300 leading-relaxed">{content.body}</p>
          <p className={`font-semibold ${keyClass}`}>
            💡 {content.keyPoint}
          </p>
        </div>
      )}
    </div>
  );
}
