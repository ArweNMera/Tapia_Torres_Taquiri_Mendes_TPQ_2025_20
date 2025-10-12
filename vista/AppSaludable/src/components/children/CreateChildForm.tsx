import React, { useState } from 'react';
import { useChildProfileApi, useAllergiesApi } from '../../hooks/useApi';
import type { CreateChildProfileRequest, AlergiaCreate } from '../../types/api';
import { toast } from 'sonner';

interface CreateChildFormProps {
  onSuccess?: (childId: number) => void;
  onCancel?: () => void;
}

const CreateChildForm: React.FC<CreateChildFormProps> = ({ onSuccess, onCancel }) => {
  const [formData, setFormData] = useState({
    // Datos del niño
    nin_nombres: '',
    nin_apellidos: '',
    nin_fecha_nac: '',
    nin_sexo: '' as 'M' | 'F' | '',

    // Datos antropométricos
    ant_peso_kg: '',
    ant_talla_cm: '',
    ant_fecha: new Date().toISOString().split('T')[0], // Fecha actual por defecto
  });

  const [selectedAllergies, setSelectedAllergies] = useState<string[]>([]);
  const [allergySearchTerm, setAllergySearchTerm] = useState('');

  const { createChildProfile } = useChildProfileApi();
  const { getAllergyTypes, addAllergy } = useAllergiesApi();

  React.useEffect(() => {
    const handler = setTimeout(() => {
      const query = allergySearchTerm.trim();
      if (query.length >= 2) {
        getAllergyTypes.execute(query);
      }
    }, 300);
    return () => clearTimeout(handler);
  }, [allergySearchTerm]);

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

    if (!formData.nin_nombres || !formData.nin_apellidos || !formData.nin_fecha_nac || !formData.nin_sexo ||
        !formData.ant_peso_kg || !formData.ant_talla_cm) {
      toast.error('Campos incompletos', {
        description: 'Por favor, completa todos los campos obligatorios.',
      });
      return;
    }

    const fullName = `${formData.nin_nombres.trim()} ${formData.nin_apellidos.trim()}`.replace(/\s+/g, ' ').trim();
    if (!fullName) {
      toast.error('Datos inválidos', {
        description: 'Debes ingresar nombres y apellidos válidos.',
      });
      return;
    }

    // Validar edad (debe ser menor a 19 años)
    const ageInMonths = calculateAge(formData.nin_fecha_nac);
    if (ageInMonths > 228) { // 19 años * 12 meses
      toast.error('Edad no válida', {
        description: 'La aplicación está diseñada para niños y adolescentes menores de 19 años.',
      });
      return;
    }

    try {
      const childRequest: CreateChildProfileRequest = {
        nino: {
          nin_nombres: fullName,
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

        toast.success('¡Niño registrado!', {
          description: 'Perfil creado exitosamente con evaluación nutricional.',
        });

        // Ejecutar callback de éxito inmediatamente
        if (onSuccess) {
          onSuccess(childId);
        }
      } else {
        toast.error('Error al registrar', {
          description: createChildProfile.error || 'No se pudo crear el perfil del niño.',
        });
      }
    } catch (error) {
      console.error('Error creating child profile:', error);
      toast.error('Error inesperado', {
        description: 'Hubo un error al crear el perfil. Intenta nuevamente.',
      });
    }
  };

  return (
    <div className="p-8 pb-10">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Información básica del niño */}
        <div className="space-y-3">
          <h3 className="text-base md:text-lg font-bold text-gray-900">Información del Niño</h3>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="nin_nombres" className="block text-sm font-semibold text-gray-700 mb-1">
                Nombres *
                </label>
                <input
                  type="text"
                  id="nin_nombres"
                  name="nin_nombres"
                  value={formData.nin_nombres}
                  onChange={handleInputChange}
                  className="w-full rounded border border-emerald-300 px-3 py-3 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  required
                />
              </div>
              <div>
                <label htmlFor="nin_apellidos" className="block text-sm font-semibold text-gray-700 mb-1">
                  Apellidos *
                </label>
                <input
                  type="text"
                  id="nin_apellidos"
                  name="nin_apellidos"
                  value={formData.nin_apellidos}
                  onChange={handleInputChange}
                  className="w-full rounded border border-emerald-300 px-3 py-3 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="nin_fecha_nac" className="block text-sm font-semibold text-gray-700 mb-1">
                Fecha de nacimiento *
                </label>
                <input
                  type="date"
                  id="nin_fecha_nac"
                  name="nin_fecha_nac"
                  value={formData.nin_fecha_nac}
                  onChange={handleInputChange}
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full rounded border border-emerald-300 px-3 py-3 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  required
                />
              </div>
              <div>
                <label htmlFor="nin_sexo" className="block text-sm font-semibold text-gray-700 mb-1">
                  Sexo *
                </label>
                <select
                  id="nin_sexo"
                  name="nin_sexo"
                  value={formData.nin_sexo}
                  onChange={handleInputChange}
                  className="w-full px-3 py-3 text-sm md:text-base border border-emerald-300 rounded focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  required
                >
                  <option value="">Seleccionar...</option>
                  <option value="M">Masculino</option>
                  <option value="F">Femenino</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Medidas antropométricas */}
        <div className="space-y-3">
          <h3 className="text-base md:text-lg font-bold text-gray-900">Medidas Actuales</h3>

          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="ant_peso_kg" className="block text-sm font-semibold text-gray-700 mb-1">
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
                  className="w-full px-3 py-3 text-sm md:text-base border border-emerald-300 rounded focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  required
                />
              </div>

              <div>
                <label htmlFor="ant_talla_cm" className="block text-sm font-semibold text-gray-700 mb-1">
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
                  className="w-full px-3 py-3 text-sm md:text-base border border-emerald-300 rounded focus:outline-none focus:ring-2 focus:ring-emerald-400"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="ant_fecha" className="block text-sm font-semibold text-gray-700 mb-1">
                Fecha de medición
              </label>
              <input
                type="date"
                id="ant_fecha"
                name="ant_fecha"
                value={formData.ant_fecha}
                onChange={handleInputChange}
                max={new Date().toISOString().split('T')[0]}
                className="w-full px-3 py-3 text-sm md:text-base border border-emerald-300 rounded focus:outline-none focus:ring-2 focus:ring-emerald-400"
              />
            </div>
          </div>
        </div>

        {/* Alergias mejoradas con buscador */}
        <div className="space-y-3">
          <h3 className="text-base md:text-lg font-bold text-gray-900">Alergias (Opcional)</h3>
          <div className="space-y-3">
            <div className="relative">
              <input
                type="text"
                value={allergySearchTerm}
                onChange={(event) => setAllergySearchTerm(event.target.value)}
                placeholder="Buscar alergia por nombre o código..."
                className="w-full rounded-lg border border-emerald-300 px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 pl-10"
              />
              <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-emerald-500">
                🔍
              </div>
            </div>

            {/* Solo mostrar resultados si hay término de búsqueda de al menos 2 caracteres */}
            {allergySearchTerm.trim() && allergySearchTerm.trim().length >= 2 && (
              <>
                {getAllergyTypes.loading ? (
                  <div className="text-center py-4">
                    <p className="text-sm text-gray-500">🔍 Buscando alergias...</p>
                  </div>
                ) : getAllergyTypes.data && getAllergyTypes.data.length > 0 ? (
                  <div className="border border-emerald-200 rounded-lg max-h-40 overflow-y-auto">
                    <div className="space-y-1 p-2">
                      {getAllergyTypes.data.map((allergy) => (
                        <label
                          key={allergy.ta_codigo}
                          className="flex items-center space-x-3 p-2 hover:bg-emerald-50 rounded-md cursor-pointer transition-colors"
                        >
                          <input
                            type="checkbox"
                            checked={selectedAllergies.includes(allergy.ta_codigo)}
                            onChange={() => handleAllergyToggle(allergy.ta_codigo)}
                            className="rounded border-emerald-300 text-emerald-600 focus:ring-emerald-400 h-4 w-4"
                          />
                          <div className="flex-1">
                            <span className="font-medium text-gray-800 text-sm">{allergy.ta_nombre}</span>
                            <span className="ml-2 text-xs text-emerald-600 bg-emerald-100 px-2 py-1 rounded">
                              {allergy.ta_codigo}
                            </span>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4 border border-gray-200 rounded-lg bg-gray-50">
                    <p className="text-sm text-gray-500">❌ No se encontraron alergias para "{allergySearchTerm}"</p>
                  </div>
                )}
              </>
            )}

            {/* Mostrar alergias seleccionadas */}
            {selectedAllergies.length > 0 && (
              <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3">
                <h4 className="text-sm font-semibold text-emerald-800 mb-2">Alergias seleccionadas:</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedAllergies.map((allergyCode) => {
                    const allergy = getAllergyTypes.data?.find(a => a.ta_codigo === allergyCode);
                    return (
                      <span
                        key={allergyCode}
                        className="inline-flex items-center gap-1 bg-emerald-100 text-emerald-800 text-xs px-2 py-1 rounded-full"
                      >
                        {allergy?.ta_nombre || allergyCode}
                        <button
                          type="button"
                          onClick={() => handleAllergyToggle(allergyCode)}
                          className="ml-1 text-emerald-600 hover:text-emerald-800"
                        >
                          ✕
                        </button>
                      </span>
                    );
                  })}
                </div>
              </div>
            )}



            {allergySearchTerm.trim() && allergySearchTerm.trim().length < 2 && (
              <div className="text-center py-4 border border-dashed border-gray-300 rounded-lg bg-gray-50">
                <p className="text-sm text-gray-500">⌨️ Escribe al menos 2 caracteres para buscar</p>
              </div>
            )}
          </div>
        </div>

        {/* Error */}
        {createChildProfile.error && (
          <div className="p-2 bg-red-100 border border-red-400 text-red-700 rounded text-xs">
            Error: {createChildProfile.error}
          </div>
        )}

        {/* Botones mejorados */}
        <div className="flex flex-wrap items-center justify-end gap-3 pt-6 border-t border-gray-200">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm md:text-base font-semibold text-gray-700 shadow-sm transition-all hover:bg-gray-50 hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-300"
            >
              Cancelar
            </button>
          )}
          <button
            type="submit"
            disabled={createChildProfile.loading}
            className="rounded-lg bg-gradient-to-r from-emerald-400 to-emerald-500 px-6 py-3 text-sm md:text-base font-semibold text-white shadow-lg transition-all hover:from-emerald-500 hover:to-emerald-600 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-emerald-400 disabled:cursor-not-allowed disabled:opacity-50 disabled:transform-none"
          >
            {createChildProfile.loading ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin">⏳</span>
                Guardando...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                💾 Guardar
              </span>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateChildForm;
