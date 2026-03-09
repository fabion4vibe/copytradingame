import type { RetailSummary } from '../../types';

interface RetailSelectorProps {
  traders: RetailSummary[];
  selectedId: string;
  onChange: (id: string) => void;
}

/** Dropdown per scegliere quale trader retail visualizzare nei pannelli. */
export function RetailSelector({ traders, selectedId, onChange }: RetailSelectorProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-400">Visualizzi:</span>
      <select
        value={selectedId}
        onChange={(e) => onChange(e.target.value)}
        className="bg-gray-800 border border-gray-700 text-white text-sm rounded px-3 py-1.5 focus:outline-none focus:border-blue-500"
      >
        {traders.map((t) => (
          <option key={t.id} value={t.id}>
            {t.name}{t.copied_traders.length > 0 ? ' 📋' : ''}
          </option>
        ))}
      </select>
    </div>
  );
}
