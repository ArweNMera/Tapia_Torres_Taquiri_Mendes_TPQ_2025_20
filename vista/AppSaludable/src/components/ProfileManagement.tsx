import React, { useState } from 'react';
import UserProfileForm from './UserProfileForm';
import { ChildrenList } from './children';

interface ProfileSection {
  id: 'personal' | 'children' | 'anthropometry';
  title: string;
  icon: string;
  description: string;
}

const ProfileManagement: React.FC = () => {
  const [activeSection, setActiveSection] = useState<ProfileSection['id']>('personal');

  const sections: ProfileSection[] = [
    {
      id: 'personal',
      title: 'Información Personal',
      icon: '👤',
      description: 'Gestiona tu información personal y configuración de cuenta'
    },
    {
      id: 'children',
      title: 'Mis Niños',
      icon: '👶',
      description: 'Gestiona los perfiles de tus niños y sus datos antropométricos'
    },
    {
      id: 'anthropometry',
      title: 'Datos Antropométricos',
      icon: '📏',
      description: 'Agrega y actualiza medidas antropométricas de tus niños'
    }
  ];

  const renderSectionContent = () => {
    switch (activeSection) {
      case 'personal':
        return <UserProfileForm />;
      case 'children':
        return (
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">Gestión de Niños</h2>
              <p className="text-gray-600 mt-1">
                Administra los perfiles de tus niños y sus datos antropométricos
              </p>
            </div>
            <div className="p-6">
              <ChildrenList />
            </div>
          </div>
        );
      case 'anthropometry':
        return (
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">Datos Antropométricos</h2>
              <p className="text-gray-600 mt-1">
                Agrega nuevas medidas antropométricas para seguimiento nutricional
              </p>
            </div>
            <div className="p-6">
              <div className="text-center py-8">
                <div className="text-6xl mb-4">📏</div>
                <h3 className="text-lg font-medium text-gray-800 mb-2">
                  Gestión de Medidas Antropométricas
                </h3>
                <p className="text-gray-600 mb-6">
                  Selecciona un niño desde la sección "Mis Niños" para agregar nuevas medidas o ver su historial completo.
                </p>
                <button
                  onClick={() => setActiveSection('children')}
                  className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Ver Mis Niños
                </button>
              </div>
            </div>
          </div>
        );
      default:
        return <UserProfileForm />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Mi Perfil</h1>
          <p className="text-gray-600 mt-2">
            Gestiona tu información personal y los datos de tus niños
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {sections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`${
                    activeSection === section.id
                      ? 'border-blue-500 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-6 border-b-2 font-medium text-sm rounded-t-lg transition-all duration-200 flex items-center space-x-2`}
                >
                  <span className="text-lg">{section.icon}</span>
                  <span>{section.title}</span>
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Section Description */}
        <div className="mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">
                {sections.find(s => s.id === activeSection)?.icon}
              </span>
              <div>
                <h2 className="text-lg font-medium text-blue-900">
                  {sections.find(s => s.id === activeSection)?.title}
                </h2>
                <p className="text-blue-700 text-sm">
                  {sections.find(s => s.id === activeSection)?.description}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="transition-all duration-300">
          {renderSectionContent()}
        </div>
      </div>
    </div>
  );
};

export default ProfileManagement;
