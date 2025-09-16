import React, { useState } from 'react';
import AnthropometryManagement from './AnthropometryManagement';
import AllergiesAndEntities from './AllergiesAndEntities';

interface ClinicalSection {
  id: 'anthropometry' | 'allergies-entities';
  title: string;
  icon: string;
  description: string;
}

export default function SelfAnthropometry() {
  const [activeSection, setActiveSection] = useState<ClinicalSection['id']>('anthropometry');

  const sections: ClinicalSection[] = [
    {
      id: 'anthropometry',
      title: 'Antropometría',
      icon: '📏',
      description: 'Registro de medidas, historial y evaluación nutricional',
    },
    {
      id: 'allergies-entities',
      title: 'Alergias y Entidades',
      icon: '🏥',
      description: 'Gestión de alergias y asociación con entidades de salud',
    },
  ];

  const renderSectionContent = () => {
    switch (activeSection) {
      case 'anthropometry':
        return <AnthropometryManagement />;
      case 'allergies-entities':
        return <AllergiesAndEntities />;
      default:
        return <AnthropometryManagement />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg border">
        <div className="border-b border-gray-200">
          <nav className="flex">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`${
                  activeSection === section.id 
                    ? 'border-green-500 text-green-600 bg-green-50' 
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } flex-1 py-4 px-6 border-b-2 font-medium text-sm transition-all duration-200 flex items-center justify-center space-x-2`}
              >
                <span className="text-xl">{section.icon}</span>
                <span>{section.title}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Section Description */}
        <div className="p-4 bg-green-50 border-b border-green-200">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{sections.find(s => s.id === activeSection)?.icon}</span>
            <div>
              <h2 className="text-lg font-medium text-green-900">{sections.find(s => s.id === activeSection)?.title}</h2>
              <p className="text-green-700 text-sm">{sections.find(s => s.id === activeSection)?.description}</p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {renderSectionContent()}
        </div>
      </div>
    </div>
  );
}
