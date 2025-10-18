import React, { useState } from 'react';
import ProfileManagementScreen from './ProfileManagementScreen';
import { SettingsScreen } from './SettingsScreen';
import { AdminUsersPage } from '../../pages/AdminUsersPage';
import { useAuth } from '../../contexts/AuthContext';

type Section = 'gestion' | 'config' | 'admin';

export default function ProfileHubScreen() {
  const { user } = useAuth();
  const isAdmin = user?.rol_nombre === 'Administrador';
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
          {isAdmin && (
            <button
              onClick={() => setSection('admin')}
              className={`whitespace-nowrap py-3 px-4 border-b-2 font-medium text-sm rounded-t-md transition-all ${
                section === 'admin'
                  ? 'border-red-600 text-red-700 bg-red-50'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🛡️ Administración
            </button>
          )}
        </nav>
      </div>

      {/* Content */}
      <div>
        {section === 'gestion' && <ProfileManagementScreen />}
        {section === 'config' && <SettingsScreen />}
        {section === 'admin' && isAdmin && <AdminUsersPage />}
      </div>
    </div>
  );
}
