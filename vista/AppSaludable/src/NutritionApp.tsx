import React from 'react';
import Dashboard from './components/Dashboard';
import { AuthProvider } from './contexts/AuthContext';

/**
 * Ejemplo de integración del Dashboard de Seguimiento Nutricional
 * 
 * Este componente muestra cómo integrar el sistema completo de seguimiento
 * nutricional que incluye:
 * - Gestión de niños
 * - Evaluación nutricional WHO
 * - Sistema de alergias
 * - Historial antropométrico
 */
const NutritionApp: React.FC = () => {
  return (
    <AuthProvider>
      <div className="App">
        <Dashboard />
      </div>
    </AuthProvider>
  );
};

export default NutritionApp;
