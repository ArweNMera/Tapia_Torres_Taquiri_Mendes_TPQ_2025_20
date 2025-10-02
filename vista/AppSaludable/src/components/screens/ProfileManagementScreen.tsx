import React, { useMemo, useState } from 'react';
import UserProfileForm from '../UserProfileForm';
import { useUserApi } from '../../hooks/useApi';

interface ProfileSection {
  id: 'personal';
  title: string;
  icon: string;
  description: string;
}

export function ProfileManagementScreen() {
  const [activeSection, setActiveSection] = useState<ProfileSection['id']>('personal');

  const sections: ProfileSection[] = useMemo(() => {
    return [
      {
        id: 'personal',
        title: 'Información Personal',
        icon: '👤',
        description: 'Gestiona tu información personal y configuración de cuenta',
      },
    ];
  }, []);

  const handleSaved = () => {
    // Perfil guardado correctamente
  };

  const renderSectionContent = () => {
    return <UserProfileForm onSaved={handleSaved} />;
  };

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Navigation Tabs (solo si hay más de una sección) */}
      {sections.length > 1 && (
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`${activeSection === section.id ? 'border-green-500 text-green-600 bg-green-50' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm rounded-t-lg transition-all duration-200 flex items-center space-x-2`}
                >
                  <span className="text-lg">{section.icon}</span>
                  <span>{section.title}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>
      )}

      {/* Section Description */}
      <div className="mb-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{sections.find(s => s.id === activeSection)?.icon}</span>
            <div>
              <h2 className="text-lg font-medium text-green-900">{sections.find(s => s.id === activeSection)?.title}</h2>
              <p className="text-green-700 text-sm">{sections.find(s => s.id === activeSection)?.description}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="transition-all duration-300">{renderSectionContent()}</div>
    </div>
  );
}

export default ProfileManagementScreen;
