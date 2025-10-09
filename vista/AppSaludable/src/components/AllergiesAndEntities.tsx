import React, { useEffect, useState } from 'react';
import { useAllergiesApi, useEntitiesApi, useNinosApi, useSelfAnthropometryApi } from '../hooks/useApi';
import type { AlergiaResponse, TipoAlergiaResponse } from '../types/api';
import { toast } from 'sonner';

export default function AllergiesAndEntities() {
  const { getSelfChild } = useSelfAnthropometryApi();
  const { getAllergyTypes, addAllergy, getAllergies, removeAllergy } = useAllergiesApi();
  const { searchEntities } = useEntitiesApi();
  const { updateNino } = useNinosApi();
  
  const [allergyTypes, setAllergyTypes] = useState<TipoAlergiaResponse[]>([]);
  const [allergies, setAllergies] = useState<AlergiaResponse[]>([]);
  const [newAllergy, setNewAllergy] = useState<{ ta_codigo: string; severidad: 'LEVE'|'MODERADA'|'SEVERA' }>({ ta_codigo: '', severidad: 'LEVE' });
  const [currentNinoId, setCurrentNinoId] = useState<number | null>(null);
  const [allergyQuery, setAllergyQuery] = useState<string>('');
  const [entityQuery, setEntityQuery] = useState<string>('');
  const [entityResults, setEntityResults] = useState<any[]>([]);
  const [selectedEntity, setSelectedEntity] = useState<any | null>(null);
  const [currentEntity, setCurrentEntity] = useState<any | null>(null); // Entidad ya asociada
  const [loading, setLoading] = useState<boolean>(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const self = await getSelfChild.execute();
      if (!self) {
        console.error('No se pudo cargar el perfil personal');
        return;
      }
      
      setCurrentNinoId(self.nin_id);

      // Cargar alergias
      const als = await getAllergies.execute(self.nin_id);
      setAllergies(als || []);

      // Si hay una entidad asociada, obtener sus detalles
      if (self.ent_id) {
        if (self.ent_nombre || self.ent_codigo) {
          setCurrentEntity({
            ent_id: self.ent_id,
            ent_nombre: self.ent_nombre,
            ent_codigo: self.ent_codigo,
            ent_direccion: self.ent_direccion,
            ent_departamento: self.ent_departamento,
            ent_provincia: self.ent_provincia,
            ent_distrito: self.ent_distrito,
          });
        }
        try {
          // Obtener todas las entidades (sin filtro) para encontrar la específica
          const allEntities = await searchEntities.execute('');
          const currentEntityDetails = allEntities?.find(ent => ent.ent_id === self.ent_id);
          if (currentEntityDetails) {
            setCurrentEntity(currentEntityDetails);
          } else {
            // Si no se encuentra en la búsqueda general, la entidad podría estar inactiva
            console.warn(`Entidad con ID ${self.ent_id} no encontrada en búsqueda activa`);
          }
        } catch (err) {
          console.error('Error al cargar detalles de la entidad:', err);
        }
      } else {
        setCurrentEntity(null);
      }
      
    } catch (err) {
      console.error('Error al cargar datos:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Buscar tipos de alergia
  useEffect(() => {
    if (!allergyQuery) return;
    const handler = setTimeout(async () => {
      const types = await getAllergyTypes.execute(allergyQuery);
      setAllergyTypes(types || []);
    }, 300);
    return () => clearTimeout(handler);
  }, [allergyQuery]);

  // Buscar entidades
  useEffect(() => {
    if (!entityQuery) return;
    const handler = setTimeout(async () => {
      const ents = await searchEntities.execute(entityQuery);
      setEntityResults(ents || []);
    }, 300);
    return () => clearTimeout(handler);
  }, [entityQuery]);

  const handleAddAllergy = async () => {
    if (!currentNinoId || !newAllergy.ta_codigo) return;
    
    const added = await addAllergy.execute(currentNinoId, newAllergy);
    if (added) {
      const als = await getAllergies.execute(currentNinoId);
      setAllergies(als || []);
      setNewAllergy({ ta_codigo: '', severidad: 'LEVE' });
      setAllergyQuery('');
      toast.success('Alergia agregada', {
        description: 'La alergia se registró correctamente.',
      });
    } else {
      toast.error('Error al agregar alergia', {
        description: addAllergy.error || 'No se pudo registrar la alergia.',
      });
    }
  };

  const handleRemoveAllergy = async (allergyId: number) => {
    if (!currentNinoId) return;
    
    const confirmed = window.confirm('¿Estás seguro de que deseas eliminar esta alergia?');
    if (!confirmed) return;
    
    const ok = await removeAllergy.execute(currentNinoId, allergyId);
    if (ok) {
      const als = await getAllergies.execute(currentNinoId);
      setAllergies(als || []);
      toast.success('Alergia eliminada', {
        description: 'La alergia se eliminó correctamente.',
      });
    } else {
      toast.error('Error al eliminar alergia', {
        description: removeAllergy.error || 'No se pudo eliminar la alergia.',
      });
    }
  };

  const handleAssociateEntity = async () => {
    if (!currentNinoId || !selectedEntity) return;
    
    const updated = await updateNino.execute(currentNinoId, { ent_id: selectedEntity.ent_id });
    if (updated) {
      // Actualizar la entidad actual y limpiar selección
      setCurrentEntity(selectedEntity);
      setSelectedEntity(null);
      setEntityQuery('');
      setEntityResults([]);
      
      // Refrescar datos del niño
      const refreshedChild = await getSelfChild.execute();
      if (refreshedChild) {
        // Actualizar entidad actual con los datos frescos
        if (refreshedChild.ent_nombre) {
          setCurrentEntity({
            ent_id: refreshedChild.ent_id || 0,
            ent_nombre: refreshedChild.ent_nombre,
            ent_codigo: refreshedChild.ent_codigo || '',
            ent_distrito: refreshedChild.ent_distrito || '',
            ent_provincia: refreshedChild.ent_provincia || '',
            ent_departamento: refreshedChild.ent_departamento || '',
          });
        }
      }
      
      toast.success('Entidad asociada', {
        description: `Se asoció correctamente con ${selectedEntity.ent_nombre}.`,
      });
    } else {
      toast.error('Error al asociar entidad', {
        description: updateNino.error || 'No se pudo actualizar.',
      });
    }
  };

  const handleRemoveEntity = async () => {
    if (!currentNinoId) return;
    
    const confirmed = window.confirm('¿Estás seguro de que deseas desasociar esta entidad?');
    if (!confirmed) return;
    
    const updated = await updateNino.execute(currentNinoId, { ent_id: null });
    if (updated) {
      setCurrentEntity(null);
      toast.success('Entidad desasociada', {
        description: 'La entidad se desasoció correctamente.',
      });
    } else {
      toast.error('Error al desasociar entidad', {
        description: updateNino.error || 'No se pudo desasociar la entidad.',
      });
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-48">
        <div className="animate-pulse text-gray-500">Cargando alergias y entidades...</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Column: Allergies Section */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center mb-6">
          <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mr-3">
            <span className="text-2xl">🚫</span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Gestión de Alergias</h3>
            <p className="text-sm text-gray-600">Registra y gestiona tus alergias alimentarias, medicamentos y ambientales</p>
          </div>
        </div>
        
        {/* Add Allergy Form */}
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-3">Agregar nueva alergia</h4>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Buscar tipo de alergia</label>
              <input
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
                placeholder="Buscar alergia..."
                value={allergyQuery}
                onChange={(e) => setAllergyQuery(e.target.value)}
              />
              {allergyQuery && allergyTypes.length > 0 && (
                <div className="mt-2 max-h-40 overflow-y-auto border rounded-md bg-white shadow-sm">
                  {allergyTypes.slice(0, 8).map(t => (
                    <button
                      key={t.ta_codigo}
                      className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm border-b border-gray-100 last:border-b-0"
                      onClick={() => {
                        setNewAllergy(prev => ({ ...prev, ta_codigo: t.ta_codigo }));
                        setAllergyQuery(t.ta_nombre);
                      }}
                    >
                      <div className="font-medium text-gray-800">{t.ta_nombre}</div>
                      <div className="text-xs text-gray-500">{t.ta_categoria}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Severidad</label>
                <select
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
                  value={newAllergy.severidad}
                  onChange={(e) => setNewAllergy(prev => ({ ...prev, severidad: e.target.value as any }))}
                >
                  <option value="LEVE">Leve</option>
                  <option value="MODERADA">Moderada</option>
                  <option value="SEVERA">Severa</option>
                </select>
              </div>
              
              <div className="flex items-end">
                <button
                  disabled={!newAllergy.ta_codigo}
                  onClick={handleAddAllergy}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm font-medium transition-colors"
                >
                  Agregar
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Allergies List */}
        <div>
          <h4 className="font-medium text-gray-900 mb-3">Alergias registradas</h4>
          {allergies.length === 0 ? (
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <div className="text-4xl mb-2 opacity-50">🚫</div>
              <div className="text-gray-500 mb-1">Sin alergias registradas</div>
              <div className="text-sm text-gray-400">Las alergias que agregues aparecerán aquí</div>
            </div>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {allergies.map(a => (
                <div key={a.na_id} className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{a.ta_nombre}</div>
                      <div className="text-sm text-gray-500 mt-1">{a.ta_categoria}</div>
                      <span className={`inline-block mt-2 px-2 py-1 rounded-full text-xs font-medium ${
                        a.na_severidad === 'SEVERA' ? 'bg-red-100 text-red-800' :
                        a.na_severidad === 'MODERADA' ? 'bg-orange-100 text-orange-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {a.na_severidad}
                      </span>
                    </div>
                    <button
                      className="ml-2 text-red-600 hover:bg-red-50 p-2 rounded-lg text-sm transition-colors"
                      onClick={() => handleRemoveAllergy(a.na_id)}
                      title="Eliminar alergia"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right Column: Entity Association Section */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center mb-6">
          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
            <span className="text-2xl">🏥</span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Entidad de Atención</h3>
            <p className="text-sm text-gray-600">Asocia tu perfil con un hospital, clínica u otra entidad de salud</p>
          </div>
        </div>
        
        {/* Current Associated Entity */}
        {currentEntity && (
          <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium text-blue-900">Entidad asociada actualmente:</div>
                <div className="text-blue-800 mt-1 font-semibold">{currentEntity.ent_nombre}</div>
                <div className="text-xs text-blue-600 mt-1">{currentEntity.entti_nombre}</div>
                {currentEntity.ent_direccion && (
                  <div className="text-xs text-blue-600">{currentEntity.ent_direccion}</div>
                )}
              </div>
              <button
                onClick={handleRemoveEntity}
                className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                title="Desasociar entidad"
              >
                Desasociar
              </button>
            </div>
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {currentEntity ? 'Cambiar entidad' : 'Buscar entidad'}
            </label>
            <input
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
              placeholder="Buscar hospital, clínica, posta, etc..."
              value={entityQuery}
              onChange={(e) => setEntityQuery(e.target.value)}
            />
            {entityQuery && entityResults.length > 0 && (
              <div className="mt-2 max-h-40 overflow-y-auto border rounded-md bg-white shadow-sm">
                {entityResults.slice(0, 8).map(ent => (
                  <button
                    key={ent.ent_id}
                    className="w-full text-left px-3 py-2 hover:bg-gray-50 text-sm border-b border-gray-100 last:border-b-0"
                    onClick={() => {
                      setSelectedEntity(ent);
                      setEntityQuery(ent.ent_nombre);
                      setEntityResults([]);
                    }}
                  >
                    <div className="font-medium text-gray-800">{ent.ent_nombre}</div>
                    <div className="text-xs text-gray-500">{ent.entti_nombre} • {ent.ent_direccion || 'Sin dirección'}</div>
                  </button>
                ))}
              </div>
            )}
            {entityQuery && entityResults.length === 0 && (
              <div className="mt-2 p-3 text-sm text-gray-500 bg-gray-50 rounded-md">
                No se encontraron entidades. Intenta con otro término de búsqueda.
              </div>
            )}
          </div>
          
          <button
            disabled={!selectedEntity}
            onClick={handleAssociateEntity}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm font-medium transition-colors"
          >
            {currentEntity ? 'Cambiar entidad' : 'Asociar entidad'}
          </button>
        </div>
        
        {selectedEntity && (
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="text-sm font-medium text-blue-900">Entidad seleccionada:</div>
            <div className="text-blue-800 mt-1">{selectedEntity.ent_nombre}</div>
            <div className="text-xs text-blue-600 mt-1">{selectedEntity.entti_nombre}</div>
          </div>
        )}

        {/* Additional Info Section */}
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
              <span className="text-sm">💡</span>
            </div>
            <div>
              <div className="text-sm font-medium text-green-900 mb-1">¿Por qué asociar una entidad?</div>
              <div className="text-xs text-green-700 space-y-1">
                <div>• Facilita el seguimiento médico</div>
                <div>• Permite compartir datos con profesionales</div>
                <div>• Mejora la coordinación de la atención</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
