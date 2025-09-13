import React, { useState } from 'react';
import ProfileManagementScreen from './ProfileManagementScreen';
import { SettingsScreen } from './SettingsScreen';

type Section = 'gestion' | 'config';

export default function ProfileHubScreen() {
  const [section, setSection] = useState<Section>('gestion');

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-6">
          <button
            onClick={() => setSection('gestion')}
            className={`whitespace-nowrap py-3 px-4 border-b-2 font-medium text-sm rounded-t-md transition-all ${
              section === 'gestion'
                ? 'border-green-600 text-green-700 bg-green-50'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Gestión del Perfil
          </button>
          <button
            onClick={() => setSection('config')}
            className={`whitespace-nowrap py-3 px-4 border-b-2 font-medium text-sm rounded-t-md transition-all ${
              section === 'config'
                ? 'border-green-600 text-green-700 bg-green-50'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Configuración
          </button>
        </nav>
      </div>

      {/* Content */}
      <div>
        {section === 'gestion' ? (
          <ProfileManagementScreen />
        ) : (
          <SettingsScreen />
        )}
      </div>
    </div>
  );
}

