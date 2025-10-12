import React, { useState } from 'react';
import { ChildrenList } from './children';
import SelfAnthropometry from './SelfAnthropometry';
import ProfileManagement from './ProfileManagement';

type DashboardView = 'children' | 'nutrition' | 'reports' | 'profile';

const Dashboard: React.FC = () => {
  const [currentView, setCurrentView] = useState<DashboardView>('children');

  const navigationItems = [
    { id: 'children' as const, label: 'Mis Niños', icon: '👶' },
    { id: 'nutrition' as const, label: 'Datos Clínicos', icon: '📏' },
    { id: 'reports' as const, label: 'Reportes', icon: '📊' },
    { id: 'profile' as const, label: 'Mi Perfil', icon: '👤' },
  ];

  const renderContent = () => {
    switch (currentView) {
      case 'children':
        return <ChildrenList />;
      case 'nutrition':
        return (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Datos Clínicos</h2>
            <SelfAnthropometry />
          </div>
        );
      case 'reports':
        return (
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Reportes</h2>
            <p className="text-gray-600">Funcionalidad en desarrollo...</p>
          </div>
        );
      case 'profile':
        return <ProfileManagement />;
      default:
        return <ChildrenList />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-gray-900">App Saludable</h1>
              <span className="ml-2 text-sm text-gray-500">Sistema de Seguimiento Nutricional</span>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">👋 Bienvenido</span>
              <button className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Sidebar + Main Content */}
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="flex gap-6">
          <aside className="w-64 bg-white border rounded-lg p-4 h-fit">
            <nav className="space-y-1">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                  className={`w-full flex items-center px-3 py-2 rounded-md text-sm font-medium text-left transition-colors ${
                    currentView === item.id
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <span className="mr-2">{item.icon}</span>
                  {item.label}
                </button>
              ))}
            </nav>
          </aside>
          <main className="flex-1">
            {renderContent()}
          </main>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center text-sm text-gray-600">
            <p>© 2025 App Saludable - Sistema de Seguimiento Nutricional Infantil</p>
            <p>Basado en estándares WHO 2006/2007</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
