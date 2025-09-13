import React, { useState, useEffect } from 'react';
import { useNinosApi } from '../../hooks/useApi';
import CreateChildForm from './CreateChildForm';
import ChildProfileView from './ChildProfileView';
import type { NinoResponse } from '../../types/api';

const ChildrenList: React.FC = () => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedChildId, setSelectedChildId] = useState<number | null>(null);
  
  const { getNinos } = useNinosApi();

  useEffect(() => {
    getNinos.execute();
  }, []);

  const handleChildCreated = (childId: number) => {
    setShowCreateForm(false);
    setSelectedChildId(childId);
    // Recargar la lista de niños
    getNinos.execute();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES');
  };

  const calculateAge = (birthDate: string) => {
    const birth = new Date(birthDate);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - birth.getTime());
    const diffMonths = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 30.44));
    const years = Math.floor(diffMonths / 12);
    const months = diffMonths % 12;
    
    if (years > 0) {
      return `${years} años${months > 0 ? ` y ${months} meses` : ''}`;
    } else {
      return `${months} meses`;
    }
  };

  // Si se está mostrando el formulario de crear niño
  if (showCreateForm) {
    return (
      <CreateChildForm 
        onSuccess={handleChildCreated}
        onCancel={() => setShowCreateForm(false)}
      />
    );
  }

  // Si se está mostrando el perfil de un niño específico
  if (selectedChildId) {
    return (
      <ChildProfileView 
        childId={selectedChildId}
        onClose={() => setSelectedChildId(null)}
      />
    );
  }

  // Vista principal: lista de niños
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Mis Niños</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Agregar Niño
        </button>
      </div>

      {getNinos.loading && (
        <div className="text-center py-8">
          <div className="text-gray-600">Cargando niños...</div>
        </div>
      )}

      {getNinos.error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
          Error: {getNinos.error}
        </div>
      )}

      {getNinos.data && getNinos.data.length === 0 && !getNinos.loading && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-4">
            Aún no has registrado ningún niño
          </div>
          <p className="text-gray-400 mb-6">
            Comienza creando el perfil de un niño para hacer seguimiento de su crecimiento y estado nutricional.
          </p>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
          >
            Crear Primer Perfil
          </button>
        </div>
      )}

      {getNinos.data && getNinos.data.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {getNinos.data.map((nino: NinoResponse) => (
            <div
              key={nino.nin_id}
              className="bg-white rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedChildId(nino.nin_id)}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">
                    {nino.nin_nombres}
                  </h3>
                  <span className={`w-3 h-3 rounded-full ${nino.nin_sexo === 'M' ? 'bg-blue-500' : 'bg-pink-500'}`}></span>
                </div>
                
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>Sexo:</span>
                    <span className="font-medium">
                      {nino.nin_sexo === 'M' ? 'Masculino' : 'Femenino'}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span>Edad:</span>
                    <span className="font-medium">
                      {calculateAge(nino.nin_fecha_nac)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span>Nacimiento:</span>
                    <span className="font-medium">
                      {formatDate(nino.nin_fecha_nac)}
                    </span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span>Registrado:</span>
                    <span className="font-medium">
                      {formatDate(nino.creado_en)}
                    </span>
                  </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedChildId(nino.nin_id);
                    }}
                    className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 transition-colors text-sm"
                  >
                    Ver Perfil Completo
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Información adicional */}
      {getNinos.data && getNinos.data.length > 0 && (
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-800 mb-2">💡 Consejos:</h4>
          <ul className="text-blue-700 text-sm space-y-1">
            <li>• Haz clic en cualquier tarjeta para ver el perfil completo del niño</li>
            <li>• Puedes agregar nuevas mediciones antropométricas en el perfil</li>
            <li>• El sistema evaluará automáticamente el estado nutricional con cada nueva medición</li>
            <li>• Las recomendaciones se actualizan según las normas de la OMS</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default ChildrenList;
