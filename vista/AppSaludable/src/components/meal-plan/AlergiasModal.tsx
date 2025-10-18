/**
 * Modal para gestionar alergias alimentarias del niño
 * Reutiliza la lógica de AllergiesAndEntities.tsx
 */
import React, { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { useAllergiesApi } from '../../hooks/useApi';
import type { AlergiaResponse, TipoAlergiaResponse } from '../../types/api';
import { toast } from 'sonner';
import { Loader2, AlertTriangle } from 'lucide-react';

interface AlergiasModalProps {
  open: boolean;
  onClose: () => void;
  ninId: number;
  ninNombre: string;
}

export const AlergiasModal: React.FC<AlergiasModalProps> = ({
  open,
  onClose,
  ninId,
  ninNombre,
}) => {
  const { getAllergyTypes, addAllergy, getAllergies, removeAllergy } = useAllergiesApi();

  const [allergyTypes, setAllergyTypes] = useState<TipoAlergiaResponse[]>([]);
  const [allergies, setAllergies] = useState<AlergiaResponse[]>([]);
  const [newAllergy, setNewAllergy] = useState<{ ta_codigo: string; severidad: 'LEVE'|'MODERADA'|'SEVERA' }>({
    ta_codigo: '',
    severidad: 'LEVE'
  });
  const [allergyQuery, setAllergyQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  const loadAllergies = async () => {
    setLoading(true);
    try {
      const als = await getAllergies.execute(ninId);
      setAllergies(als || []);
    } catch (err) {
      console.error('Error al cargar alergias:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      loadAllergies();
    }
  }, [open, ninId]);

  // Buscar tipos de alergia
  useEffect(() => {
    if (!allergyQuery) {
      setAllergyTypes([]);
      return;
    }
    const handler = setTimeout(async () => {
      const types = await getAllergyTypes.execute(allergyQuery);
      setAllergyTypes(types || []);
    }, 300);
    return () => clearTimeout(handler);
  }, [allergyQuery]);

  const handleAddAllergy = async () => {
    if (!newAllergy.ta_codigo) return;

    const added = await addAllergy.execute(ninId, newAllergy);
    if (added) {
      await loadAllergies();
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
    const confirmed = window.confirm('¿Estás seguro de que deseas eliminar esta alergia?');
    if (!confirmed) return;

    const ok = await removeAllergy.execute(ninId, allergyId);
    if (ok) {
      await loadAllergies();
      toast.success('Alergia eliminada', {
        description: 'La alergia se eliminó correctamente.',
      });
    } else {
      toast.error('Error al eliminar alergia', {
        description: removeAllergy.error || 'No se pudo eliminar la alergia.',
      });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            Alergias de {ninNombre}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {loading ? (
            <div className="flex justify-center items-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
            </div>
          ) : (
            <>
              {/* Add Allergy Form */}
              <div className="p-4 bg-gray-50 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-3">Agregar nueva alergia</h4>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Buscar tipo de alergia
                    </label>
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
                              setAllergyTypes([]);
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
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Severidad
                      </label>
                      <select
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 outline-none"
                        value={newAllergy.severidad}
                        onChange={(e) => setNewAllergy(prev => ({
                          ...prev,
                          severidad: e.target.value as any
                        }))}
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
                <h4 className="font-medium text-gray-900 mb-3">
                  Alergias registradas ({allergies.length})
                </h4>
                {allergies.length === 0 ? (
                  <div className="text-center py-8 bg-gray-50 rounded-lg">
                    <div className="text-4xl mb-2 opacity-50">🚫</div>
                    <div className="text-gray-500 mb-1">Sin alergias registradas</div>
                    <div className="text-sm text-gray-400">
                      Las alergias que agregues aparecerán aquí
                    </div>
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
            </>
          )}

          {/* Botón cerrar */}
          <div className="flex justify-end pt-4 border-t">
            <Button onClick={onClose} variant="outline">
              Cerrar
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
