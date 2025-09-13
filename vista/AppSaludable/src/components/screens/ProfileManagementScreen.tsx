import React, { useEffect, useMemo, useState } from 'react';
import UserProfileForm from '../UserProfileForm';
import { ChildrenList } from '../children';
import { useUserApi } from '../../hooks/useApi';
import { useNinosApi } from '../../hooks/useApi';

interface ProfileSection {
  id: 'personal' | 'children' | 'anthropometry';
  title: string;
  icon: string;
  description: string;
}

export function ProfileManagementScreen() {
  const [activeSection, setActiveSection] = useState<ProfileSection['id']>('personal');
  const { getProfile } = useUserApi();
  const { getNinos } = useNinosApi();

  useEffect(() => {
    if (!getProfile.data) getProfile.execute();
    getNinos.execute();
  }, []);

  const ageYears = useMemo(() => {
    const dob = getProfile.data?.fecha_nac;
    if (!dob) return null;
    return Math.floor((Date.now() - new Date(dob).getTime()) / (1000 * 60 * 60 * 24 * 365.25));
  }, [getProfile.data?.fecha_nac]);

  const isSelfManaged = typeof ageYears === 'number' ? ageYears >= 13 : null;

  const sections: ProfileSection[] = useMemo(() => {
    const base: ProfileSection[] = [
      {
        id: 'personal',
        title: 'Información Personal',
        icon: '👤',
        description: 'Gestiona tu información personal y configuración de cuenta',
      },
    ];
    if (Array.isArray(getNinos.data) && getNinos.data.length > 0) {
      base.push({
        id: 'children',
        title: 'Mis Niños',
        icon: '👶',
        description: 'Gestiona los perfiles de tus niños y sus datos antropométricos',
      });
    }
    // Removido: pestaña de "Datos Clínicos" ya que está disponible en el sidebar
    return base;
  }, [getNinos.data]);  // Reajustar sección activa si cambia el conjunto de pestañas
  useEffect(() => {
    if (!sections.find(s => s.id === activeSection)) {
      setActiveSection('personal');
    }
  }, [sections, activeSection]);

  const handleSaved = () => {
    // reconsultar para recalcular edad/autogestión y pestañas
    getProfile.execute();
  };

  const renderSectionContent = () => {
    switch (activeSection) {
      case 'personal':
        return <UserProfileForm onSaved={handleSaved} />;
      case 'children':
        return (
          <div className="bg-white rounded-lg shadow-md">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-800">Gestión de Niños</h2>
              <p className="text-gray-600 mt-1">Administra los perfiles de tus niños y sus datos antropométricos</p>
            </div>
            <div className="p-6">
              <ChildrenList />
            </div>
          </div>
        );
      default:
        return <UserProfileForm onSaved={handleSaved} />;
    }
  };

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Navigation Tabs */}
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
