import React, { useState, useEffect } from 'react';
import { useChildProfileApi, useNutritionalEvaluationApi, useAnthropometryApi } from '../../hooks/useApi';
import type { NinoWithAnthropometry, AnthropometryCreate } from '../../types/api';
import { toast } from 'sonner';

interface ChildProfileViewProps {
  childId: number;
  onClose?: () => void;
}

const ChildProfileView: React.FC<ChildProfileViewProps> = ({ childId, onClose }) => {
  const [showAddMeasurement, setShowAddMeasurement] = useState(false);
  const [newMeasurement, setNewMeasurement] = useState({
    ant_peso_kg: '',
    ant_talla_cm: '',
    ant_fecha: new Date().toISOString().split('T')[0],
  });

  const { getChildWithData } = useChildProfileApi();
  const { evaluateNutritionalStatus } = useNutritionalEvaluationApi();
  const { addAnthropometry } = useAnthropometryApi();

  useEffect(() => {
    getChildWithData.execute(childId);
  }, [childId]);

  const handleAddMeasurement = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newMeasurement.ant_peso_kg || !newMeasurement.ant_talla_cm) {
      toast.error('Campos incompletos', {
        description: 'Por favor, completa peso y talla.',
      });
      return;
    }

    const measurementData: AnthropometryCreate = {
      ant_peso_kg: parseFloat(newMeasurement.ant_peso_kg),
      ant_talla_cm: parseFloat(newMeasurement.ant_talla_cm),
      ant_fecha: newMeasurement.ant_fecha,
    };

    const result = await addAnthropometry.execute(childId, measurementData);

    if (result) {
      // Actualizar la evaluación nutricional
      await evaluateNutritionalStatus.execute(childId);

      // Recargar datos del niño
      await getChildWithData.execute(childId);

      // Limpiar formulario
      setNewMeasurement({
        ant_peso_kg: '',
        ant_talla_cm: '',
        ant_fecha: new Date().toISOString().split('T')[0],
      });
      setShowAddMeasurement(false);

      toast.success('Medición agregada', {
        description: 'Medición agregada y estado nutricional actualizado.',
      });
    } else {
      toast.error('Error al agregar medición', {
        description: addAnthropometry.error || 'No se pudo agregar la medición.',
      });
    }
  };

  const handleEvaluateNutrition = async () => {
    const result = await evaluateNutritionalStatus.execute(childId);
    if (result) {
      await getChildWithData.execute(childId);
      toast.success('Evaluación actualizada', {
        description: 'La evaluación nutricional se actualizó correctamente.',
      });
    } else {
      toast.error('Error al evaluar', {
        description: evaluateNutritionalStatus.error || 'No se pudo actualizar la evaluación.',
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES');
  };

  const getClassificationColor = (classification: string) => {
    switch (classification.toLowerCase()) {
      case 'normal':
      case 'riesgo bajo':
        return 'text-green-600 bg-green-100';
      case 'sobrepeso':
      case 'riesgo moderado':
        return 'text-yellow-600 bg-yellow-100';
      case 'obesidad':
      case 'desnutrición':
      case 'riesgo alto':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (getChildWithData.loading) {
    return <div className="p-6 text-center">Cargando información del niño...</div>;
  }

  if (getChildWithData.error) {
    return (
      <div className="p-6 text-center text-red-600">
        Error: {getChildWithData.error}
      </div>
    );
  }

  if (!getChildWithData.data) {
    return <div className="p-6 text-center">No se encontró información del niño.</div>;
  }

  const childData: NinoWithAnthropometry = getChildWithData.data;
  const { nino, antropometrias, alergias, ultimo_estado_nutricional } = childData;

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Perfil de {nino.nin_nombres}</h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl font-bold"
          >
            ×
          </button>
        )}
      </div>

      {/* Información básica */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Información Básica</h3>
          <p><strong>Nombre:</strong> {nino.nin_nombres}</p>
          <p><strong>Fecha de nacimiento:</strong> {formatDate(nino.nin_fecha_nac)}</p>
          <p><strong>Sexo:</strong> {nino.nin_sexo === 'M' ? 'Masculino' : 'Femenino'}</p>
          <p><strong>Edad:</strong> {nino.edad_meses} meses ({Math.floor(nino.edad_meses / 12)} años y {nino.edad_meses % 12} meses)</p>
        </div>

        {ultimo_estado_nutricional && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Estado Nutricional Actual</h3>
            <p><strong>IMC:</strong> {ultimo_estado_nutricional.imc.toFixed(2)} kg/m²</p>
            {ultimo_estado_nutricional.z_score_imc && (
              <p><strong>Z-Score IMC:</strong> {ultimo_estado_nutricional.z_score_imc.toFixed(2)}</p>
            )}
            {ultimo_estado_nutricional.percentile && (
              <p><strong>Percentil:</strong> {ultimo_estado_nutricional.percentile.toFixed(1)}%</p>
            )}
            <p>
              <strong>Clasificación:</strong>{' '}
              <span className={`px-2 py-1 rounded text-sm ${getClassificationColor(ultimo_estado_nutricional.classification)}`}>
                {ultimo_estado_nutricional.classification}
              </span>
            </p>
            <p>
              <strong>Nivel de riesgo:</strong>{' '}
              <span className={`px-2 py-1 rounded text-sm ${getClassificationColor(ultimo_estado_nutricional.risk_level)}`}>
                {ultimo_estado_nutricional.risk_level}
              </span>
            </p>
          </div>
        )}
      </div>

      {/* Recomendaciones */}
      {ultimo_estado_nutricional && ultimo_estado_nutricional.recommendations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Recomendaciones</h3>
          <div className="bg-blue-50 p-4 rounded-lg space-y-3">
            {ultimo_estado_nutricional.recommendations.map((rec, index) => (
              <div key={index} className="flex gap-3">
                <span className="text-2xl flex-shrink-0">{rec.icono}</span>
                <div className="flex-1">
                  <p className="font-medium text-blue-900">{rec.titulo}</p>
                  <p className="text-sm text-blue-700 mt-1">{rec.descripcion}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Alergias */}
      {alergias.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Alergias</h3>
          <div className="flex flex-wrap gap-2">
            {alergias.map((alergia) => (
              <span
                key={alergia.na_id}
                className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm"
              >
                {alergia.ta_nombre} ({alergia.na_severidad})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Historial antropométrico */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-700">Historial de Mediciones</h3>
          <div className="space-x-2">
            <button
              onClick={() => setShowAddMeasurement(!showAddMeasurement)}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
            >
              {showAddMeasurement ? 'Cancelar' : 'Agregar Medición'}
            </button>
            <button
              onClick={handleEvaluateNutrition}
              disabled={evaluateNutritionalStatus.loading}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm disabled:opacity-50"
            >
              {evaluateNutritionalStatus.loading ? 'Evaluando...' : 'Evaluar Estado'}
            </button>
          </div>
        </div>

        {/* Formulario para agregar medición */}
        {showAddMeasurement && (
          <form onSubmit={handleAddMeasurement} className="bg-gray-50 p-4 rounded-lg mb-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Peso (kg) *
                </label>
                <input
                  type="number"
                  value={newMeasurement.ant_peso_kg}
                  onChange={(e) => setNewMeasurement(prev => ({ ...prev, ant_peso_kg: e.target.value }))}
                  step="0.1"
                  min="1"
                  max="200"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Talla (cm) *
                </label>
                <input
                  type="number"
                  value={newMeasurement.ant_talla_cm}
                  onChange={(e) => setNewMeasurement(prev => ({ ...prev, ant_talla_cm: e.target.value }))}
                  step="0.1"
                  min="30"
                  max="250"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fecha
                </label>
                <input
                  type="date"
                  value={newMeasurement.ant_fecha}
                  onChange={(e) => setNewMeasurement(prev => ({ ...prev, ant_fecha: e.target.value }))}
                  max={new Date().toISOString().split('T')[0]}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div className="mt-4">
              <button
                type="submit"
                disabled={addAnthropometry.loading}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {addAnthropometry.loading ? 'Agregando...' : 'Agregar Medición'}
              </button>
            </div>
          </form>
        )}

        {/* Tabla de mediciones */}
        {antropometrias.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white border border-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Fecha</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Edad (meses)</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Peso (kg)</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Talla (cm)</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">IMC</th>
                  <th className="px-4 py-2 text-left text-sm font-medium text-gray-700">Z-Score IMC</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {antropometrias.map((medicion) => (
                  <tr key={medicion.ant_id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm text-gray-900">{formatDate(medicion.ant_fecha)}</td>
                    <td className="px-4 py-2 text-sm text-gray-900">{medicion.ant_edad_meses || 'N/A'}</td>
                    <td className="px-4 py-2 text-sm text-gray-900">{medicion.ant_peso_kg}</td>
                    <td className="px-4 py-2 text-sm text-gray-900">{medicion.ant_talla_cm}</td>
                    <td className="px-4 py-2 text-sm text-gray-900">{medicion.imc?.toFixed(2) || 'N/A'}</td>
                    <td className="px-4 py-2 text-sm text-gray-900">{medicion.ant_z_imc?.toFixed(2) || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No hay mediciones registradas.</p>
        )}
      </div>

      {/* Errores */}
      {addAnthropometry.error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded mb-4">
          Error agregando medición: {addAnthropometry.error}
        </div>
      )}

      {evaluateNutritionalStatus.error && (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded mb-4">
          Error evaluando estado nutricional: {evaluateNutritionalStatus.error}
        </div>
      )}
    </div>
  );
};

export default ChildProfileView;
