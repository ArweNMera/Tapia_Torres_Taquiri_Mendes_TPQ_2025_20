import React, { useEffect, useState } from 'react';
import ConfirmationModal from './ui/ConfirmationModal';
import { useSelfAnthropometryApi } from '../hooks/useApi';
import type { AnthropometryCreate, AnthropometryResponse, NutritionalStatusResponse } from '../types/api';

export default function AnthropometryManagement() {
  const { getSelfChild, addSelfAnthropometry, getSelfAnthropometryHistory, getSelfNutritionalStatus } = useSelfAnthropometryApi();
  
  const [form, setForm] = useState<AnthropometryCreate>({ 
    ant_peso_kg: 0, 
    ant_talla_cm: 0, 
    ant_fecha: new Date().toISOString().slice(0,10) 
  });
  const [history, setHistory] = useState<AnthropometryResponse[]>([]);
  const [status, setStatus] = useState<NutritionalStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentNinoId, setCurrentNinoId] = useState<number | null>(null);
  const [showSuccess, setShowSuccess] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [confirmModal, setConfirmModal] = useState<{ isOpen: boolean; type: 'success' | 'error'; title: string; message?: string }>({ isOpen: false, type: 'success', title: '', message: '' });

  const loadData = async () => {
    setLoading(true);
    try {
      const self = await getSelfChild.execute();
      if (!self) {
        setError(getSelfChild.error || 'Error al cargar perfil personal');
        return;
      }
      
      setCurrentNinoId(self.nin_id);
      
      // Cargar datos en paralelo
      const [hist, stat] = await Promise.all([
        getSelfAnthropometryHistory.execute(),
        getSelfNutritionalStatus.execute()
      ]);
      
      setHistory(hist || []);
      setStatus(stat || null);
      
    } catch (err) {
      setError('Error al cargar datos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setForm(prev => ({ 
      ...prev, 
      [name]: name === 'ant_peso_kg' || name === 'ant_talla_cm' ? Number(value) : value 
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    if (form.ant_peso_kg <= 0 || form.ant_talla_cm <= 0) {
      setError('Peso y talla deben ser mayores a 0');
      return;
    }
    
    const normalized = {
      ...form,
      ant_talla_cm: form.ant_talla_cm <= 3 ? Number((form.ant_talla_cm * 100).toFixed(1)) : form.ant_talla_cm,
    };
    
    const saved = await addSelfAnthropometry.execute(normalized);
    if (!saved) {
      setError(addSelfAnthropometry.error || 'Error al guardar medida');
      setConfirmModal({ isOpen: true, type: 'error', title: 'Error al guardar', message: addSelfAnthropometry.error || 'No se pudo guardar la medida.' });
      return;
    }
    
    setShowSuccess(true);
    setConfirmModal({ isOpen: true, type: 'success', title: 'Datos actualizados', message: 'La medida ha sido registrada correctamente.' });
    
    // Recargar datos
    await loadData();
    
    // Reset form
    setForm(prev => ({ ...prev, ant_peso_kg: 0, ant_talla_cm: 0 }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-48">
        <div className="animate-pulse text-gray-500">Cargando datos antropométricos...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Success Message */}
      {showSuccess && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-green-500 mr-3"></div>
              <span className="text-green-800 font-medium">Medida guardada correctamente</span>
            </div>
            <button 
              onClick={() => setShowSuccess(false)}
              className="text-green-600 hover:text-green-800"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Form */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center mb-4">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3">
              <span className="text-2xl">📏</span>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Registrar nueva medida</h3>
              <p className="text-sm text-gray-600">Registra tu peso y talla actual</p>
            </div>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
              <input 
                type="date" 
                name="ant_fecha" 
                value={form.ant_fecha || ''} 
                onChange={handleChange}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none" 
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Peso (kg)</label>
                <input 
                  type="number" 
                  step="0.1" 
                  name="ant_peso_kg" 
                  value={form.ant_peso_kg || ''} 
                  onChange={handleChange}
                  placeholder="Ej: 65.5"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Talla (cm)</label>
                <input 
                  type="number" 
                  step="0.1" 
                  name="ant_talla_cm" 
                  value={form.ant_talla_cm || ''} 
                  onChange={handleChange}
                  placeholder="Ej: 170"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none" 
                />
              </div>
            </div>
            
            <button 
              type="submit" 
              className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 font-medium transition-colors"
            >
              Guardar medida
            </button>
          </form>

          {error && (
            <div className="mt-4 p-3 rounded-lg border border-red-200 bg-red-50 text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Right Column: Current Status */}
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center mb-4">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <span className="text-2xl">📊</span>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-gray-900">Última evaluación</h4>
              <p className="text-sm text-gray-600">Estado nutricional actual</p>
            </div>
          </div>
          
          {status ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-600">IMC</div>
                  <div className="text-2xl font-bold text-gray-900">{status.imc.toFixed(2)}</div>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="text-sm text-gray-600">Clasificación</div>
                  <div className="text-lg font-semibold text-gray-900">{status.classification}</div>
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-sm text-gray-600 mb-1">Nivel de riesgo</div>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                  status.risk_level === 'CRITICO' ? 'bg-red-100 text-red-800' :
                  status.risk_level === 'ALTO' ? 'bg-orange-100 text-orange-800' :
                  status.risk_level === 'MODERADO' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {status.risk_level}
                </span>
              </div>
              
              {status.recommendations && status.recommendations.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="text-sm font-medium text-blue-900 mb-2">Recomendaciones:</div>
                  <ul className="grid grid-cols-1 md:grid-cols-2 gap-x-4 gap-y-1 list-disc list-inside text-sm text-blue-800">
                    {status.recommendations.map((r, i) => (<li key={i} className="break-words">{r}</li>))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-6xl mb-4 opacity-50">📊</div>
              <div className="text-gray-500 mb-2">Aún no hay evaluación</div>
              <div className="text-sm text-gray-400">Registra una medida para calcular tu estado nutricional</div>
            </div>
          )}
        </div>
      </div>

      {/* History Section */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center mb-4">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-3">
            <span className="text-2xl">📈</span>
          </div>
          <div>
            <h4 className="text-lg font-semibold text-gray-900">Historial de medidas</h4>
            <p className="text-sm text-gray-600">Seguimiento de tu evolución antropométrica</p>
          </div>
        </div>
        
        {history.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4 opacity-50">📈</div>
            <div className="text-gray-500 mb-2">Sin registros</div>
            <div className="text-sm text-gray-400">Tus medidas aparecerán aquí una vez que las registres</div>
          </div>
        ) : (
          <div className="overflow-hidden rounded-lg border">
            <div className="max-h-80 overflow-y-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Peso (kg)</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Talla (cm)</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">IMC</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {history.map((h) => (
                    <tr key={h.ant_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(h.ant_fecha).toLocaleDateString('es-ES')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {h.ant_peso_kg} kg
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {h.ant_talla_cm} cm
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {(h.imc ?? (h.ant_peso_kg / Math.pow(h.ant_talla_cm/100,2))).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Modal de confirmación (éxito/error) */}
      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ isOpen: false, type: 'success', title: '', message: '' })}
        type={confirmModal.type}
        title={confirmModal.title}
        message={confirmModal.message}
      />
    </div>
  );
}
