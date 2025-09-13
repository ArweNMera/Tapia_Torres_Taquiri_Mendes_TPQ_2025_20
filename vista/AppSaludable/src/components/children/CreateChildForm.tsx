import React, { useState } from 'react';
import { useChildProfileApi, useAllergiesApi } from '../../hooks/useApi';
import type { CreateChildProfileRequest, AlergiaCreate } from '../../types/api';

interface CreateChildFormProps {
  onSuccess?: (childId: number) => void;
  onCancel?: () => void;
}

const CreateChildForm: React.FC<CreateChildFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    // Datos del niño
    nin_nombres: '',
    nin_fecha_nac: '',
    nin_sexo: '' as 'M' | 'F' | '',
    
    // Datos antropométricos
    ant_peso_kg: '',
    ant_talla_cm: '',
    ant_fecha: new Date().toISOString().split('T')[0], // Fecha actual por defecto
  });

  const [selectedAllergies, setSelectedAllergies] = useState<string[]>([]);
  
  const { createChildProfile } = useChildProfileApi();
  const { getAllergyTypes, addAllergy } = useAllergiesApi();

  // Cargar tipos de alergias al montar el componente
  React.useEffect(() => {
    getAllergyTypes.execute();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleAllergyToggle = (allergyCode: string) => {
    setSelectedAllergies(prev => 
      prev.includes(allergyCode)
        ? prev.filter(code => code !== allergyCode)
        : [...prev, allergyCode]
    );
  };

  const calculateAge = (birthDate: string): number => {
    const birth = new Date(birthDate);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - birth.getTime());
    const diffMonths = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 30.44)); // Aproximadamente 30.44 días por mes
    return diffMonths;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.nin_nombres || !formData.nin_fecha_nac || !formData.nin_sexo || 
        !formData.ant_peso_kg || !formData.ant_talla_cm) {
      alert('Por favor, completa todos los campos obligatorios.');
      return;
    }

    // Validar edad (debe ser menor a 19 años)
    const ageInMonths = calculateAge(formData.nin_fecha_nac);
    if (ageInMonths > 228) { // 19 años * 12 meses
      alert('La aplicación está diseñada para niños y adolescentes menores de 19 años.');
      return;
    }

    try {
      const childRequest: CreateChildProfileRequest = {
        nino: {
          nin_nombres: formData.nin_nombres,
          nin_fecha_nac: formData.nin_fecha_nac,
          nin_sexo: formData.nin_sexo as 'M' | 'F',
        },
        antropometria: {
          ant_peso_kg: parseFloat(formData.ant_peso_kg),
          ant_talla_cm: parseFloat(formData.ant_talla_cm),
          ant_fecha: formData.ant_fecha,
        }
      };

      const result = await createChildProfile.execute(childRequest);
      
      if (result) {
        const childId = result.nino.nin_id;
        
        // Agregar alergias seleccionadas
        for (const allergyCode of selectedAllergies) {
          const allergyData: AlergiaCreate = {
            ta_codigo: allergyCode,
            severidad: 'LEVE' // Por defecto, el usuario puede cambiar esto después
          };
          await addAllergy.execute(childId, allergyData);
        }

        alert('¡Perfil del niño creado exitosamente! Se ha realizado la evaluación nutricional.');
        if (onSuccess) {
          onSuccess(childId);
        }
      }
    } catch (error) {
      console.error('Error creating child profile:', error);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Crear Perfil del Niño</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Información básica del niño */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700">Información del Niño</h3>
          
          <div>
            <label htmlFor="nin_nombres" className="block text-sm font-medium text-gray-700 mb-1">
              Nombre completo *
            </label>
            <input
              type="text"
              id="nin_nombres"
              name="nin_nombres"
              value={formData.nin_nombres}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="nin_fecha_nac" className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de nacimiento *
              </label>
              <input
                type="date"
                id="nin_fecha_nac"
                name="nin_fecha_nac"
                value={formData.nin_fecha_nac}
                onChange={handleInputChange}
                max={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label htmlFor="nin_sexo" className="block text-sm font-medium text-gray-700 mb-1">
                Sexo *
              </label>
              <select
                id="nin_sexo"
                name="nin_sexo"
                value={formData.nin_sexo}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Seleccionar...</option>
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
              </select>
            </div>
          </div>
        </div>

        {/* Medidas antropométricas */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700">Medidas Actuales</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label htmlFor="ant_peso_kg" className="block text-sm font-medium text-gray-700 mb-1">
                Peso (kg) *
              </label>
              <input
                type="number"
                id="ant_peso_kg"
                name="ant_peso_kg"
                value={formData.ant_peso_kg}
                onChange={handleInputChange}
                step="0.1"
                min="1"
                max="200"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label htmlFor="ant_talla_cm" className="block text-sm font-medium text-gray-700 mb-1">
                Talla (cm) *
              </label>
              <input
                type="number"
                id="ant_talla_cm"
                name="ant_talla_cm"
                value={formData.ant_talla_cm}
                onChange={handleInputChange}
                step="0.1"
                min="30"
                max="250"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label htmlFor="ant_fecha" className="block text-sm font-medium text-gray-700 mb-1">
                Fecha de medición
              </label>
              <input
                type="date"
                id="ant_fecha"
                name="ant_fecha"
                value={formData.ant_fecha}
                onChange={handleInputChange}
                max={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Alergias */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-700">Alergias (Opcional)</h3>
          
          {getAllergyTypes.loading ? (
            <p className="text-gray-500">Cargando tipos de alergias...</p>
          ) : getAllergyTypes.data && getAllergyTypes.data.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
              {getAllergyTypes.data.map((allergy) => (
                <label key={allergy.ta_codigo} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedAllergies.includes(allergy.ta_codigo)}
                    onChange={() => handleAllergyToggle(allergy.ta_codigo)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">
                    {allergy.ta_nombre} ({allergy.ta_categoria.toLowerCase()})
                  </span>
                </label>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No hay tipos de alergias disponibles</p>
          )}
        </div>

        {/* Mostrar error si existe */}
        {createChildProfile.error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            Error: {createChildProfile.error}
          </div>
        )}

        {/* Botones */}
        <div className="flex space-x-4 pt-6">
          <button
            type="submit"
            disabled={createChildProfile.loading}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createChildProfile.loading ? 'Creando perfil...' : 'Crear Perfil'}
          </button>
          
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Cancelar
            </button>
          )}
        </div>
      </form>
    </div>
  );
};

export default CreateChildForm;
