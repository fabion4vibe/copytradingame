import type { AppRole } from '../types';

interface RoleSwitcherProps {
  role: AppRole;
  onChange: (role: AppRole) => void;
}

/**
 * Toggle visibile in header per passare tra la vista Retail e quella Gestore.
 * Permette all'utente di esplorare entrambe le prospettive della piattaforma.
 */
export function RoleSwitcher({ role, onChange }: RoleSwitcherProps) {
  return (
    <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-1">
      <button
        onClick={() => onChange('retail')}
        className={`flex items-center gap-1.5 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
          role === 'retail'
            ? 'bg-blue-600 text-white'
            : 'text-gray-400 hover:text-white'
        }`}
      >
        <span>👤</span> Retail
      </button>
      <button
        onClick={() => onChange('manager')}
        className={`flex items-center gap-1.5 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
          role === 'manager'
            ? 'bg-purple-600 text-white'
            : 'text-gray-400 hover:text-white'
        }`}
      >
        <span>🏢</span> Gestore
      </button>
    </div>
  );
}
