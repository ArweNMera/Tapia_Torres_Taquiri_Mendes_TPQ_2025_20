import React, { useState, useEffect } from 'react';
import { useNinosApi, useAnthropometryApi } from '../../hooks/useApi';
import CreateChildForm from './CreateChildForm';
import ChildProfileView from './ChildProfileView';
import type { NinoWithAnthropometry, NutritionalStatusResponse } from '../../types/api';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import ConfirmationModal from '../ui/ConfirmationModal';
import ActionConfirmModal from '../ui/ActionConfirmModal';

type ClassificationKey = 'normal' | 'sobrepeso' | 'obesidad' | 'desnutrición' | 'desnutricion' | 'bajo peso' | 'sin_datos';

interface ClassificationTheme {
  badgeBg: string;
  badgeText: string;
  cardBg: string;
  cardBorder: string;
  avatarBg: string;
}

const CLASSIFICATION_THEMES: Record<ClassificationKey, ClassificationTheme> = {
  normal: {
    badgeBg: 'bg-emerald-100',
    badgeText: 'text-emerald-700',
    cardBg: 'bg-emerald-50',
    cardBorder: 'border-emerald-200',
    avatarBg: 'bg-emerald-500',
  },
  sobrepeso: {
    badgeBg: 'bg-amber-100',
    badgeText: 'text-amber-700',
    cardBg: 'bg-white',
    cardBorder: 'border-amber-200',
    avatarBg: 'bg-amber-500',
  },
  obesidad: {
    badgeBg: 'bg-rose-100',
    badgeText: 'text-rose-700',
    cardBg: 'bg-white',
    cardBorder: 'border-rose-200',
    avatarBg: 'bg-rose-500',
  },
  desnutrición: {
    badgeBg: 'bg-orange-100',
    badgeText: 'text-orange-700',
    cardBg: 'bg-white',
    cardBorder: 'border-orange-200',
    avatarBg: 'bg-orange-500',
  },
  desnutricion: {
    badgeBg: 'bg-orange-100',
    badgeText: 'text-orange-700',
    cardBg: 'bg-white',
    cardBorder: 'border-orange-200',
    avatarBg: 'bg-orange-500',
  },
  'bajo peso': {
    badgeBg: 'bg-sky-100',
    badgeText: 'text-sky-700',
    cardBg: 'bg-white',
    cardBorder: 'border-sky-200',
    avatarBg: 'bg-sky-500',
  },
  sin_datos: {
    badgeBg: 'bg-slate-100',
    badgeText: 'text-slate-600',
    cardBg: 'bg-white',
    cardBorder: 'border-slate-200',
    avatarBg: 'bg-emerald-500',
  },
};

const normalizeClassificationKey = (classification?: string): ClassificationKey => {
  if (!classification) {
    return 'sin_datos';
  }

  const normalized = classification.trim().toLowerCase();

  if (normalized in CLASSIFICATION_THEMES) {
    return normalized as ClassificationKey;
  }

  switch (normalized) {
    case 'bajo_peso':
    case 'bajo-peso':
    case 'bajo peso':
      return 'bajo peso';
    case 'desnutricion':
      return 'desnutricion';
    case 'desnutrición':
      return 'desnutrición';
    case 'sobre peso':
      return 'sobrepeso';
    default:
      return 'sin_datos';
  }
};

const getClassificationTheme = (classification?: string): ClassificationTheme => {
  const key = normalizeClassificationKey(classification);
  return CLASSIFICATION_THEMES[key];
};

const getInitials = (fullName: string): string => {
  return fullName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('');
};

const formatClassification = (status?: NutritionalStatusResponse | null) => {
  const classification = status?.classification;
  if (!classification) return 'SIN EVALUACIÓN';
  return classification.toUpperCase();
};

const ChildrenList: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedChildId, setSelectedChildId] = useState<number | null>(null);
  const [hasInitialized, setHasInitialized] = useState(false);
  
  // Estados para modales de confirmación
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    type: 'success' | 'error';
    title: string;
    message?: string;
  }>({
    isOpen: false,
    type: 'success',
    title: '',
    message: '',
  });

  const [deleteConfirmModal, setDeleteConfirmModal] = useState<{
    isOpen: boolean;
    childId: number | null;
    childName: string;
  }>({
    isOpen: false,
    childId: null,
    childName: '',
  });
  
  const { getNinos, deleteNino, updateNino } = useNinosApi();

  useEffect(() => {
    if (!hasInitialized) {
      getNinos.execute();
      setHasInitialized(true);
    }
  }, [hasInitialized]);

  const handleChildCreated = (childId: number) => {
    setIsCreateModalOpen(false);
    setSelectedChildId(childId);
    getNinos.execute();
    
    // Mostrar modal de confirmación después de cerrar el modal de creación
    setTimeout(() => {
      setConfirmModal({
        isOpen: true,
        type: 'success',
        title: 'Niño registrado',
        message: '¡Perfil del niño creado exitosamente! Se ha realizado la evaluación nutricional.',
      });
    }, 300);
  };

  const [editingChild, setEditingChild] = useState<{
    id: number;
    name: string;
    birthDate: string;
  } | null>(null);
  const [editError, setEditError] = useState<string | null>(null);

  const childProfiles: NinoWithAnthropometry[] = Array.isArray(getNinos.data)
    ? getNinos.data
    : [];

  const handleDeleteChild = (childId: number, childName: string) => {
    setDeleteConfirmModal({
      isOpen: true,
      childId,
      childName,
    });
  };

  const confirmDeleteChild = async () => {
    const { childId, childName } = deleteConfirmModal;
    if (!childId) return;

    const deleted = await deleteNino.execute(childId);
    
    setDeleteConfirmModal({ isOpen: false, childId: null, childName: '' });

    if (!deleted) {
      setConfirmModal({
        isOpen: true,
        type: 'error',
        title: 'Error al eliminar',
        message: deleteNino.error || 'No se pudo eliminar al niño.',
      });
      return;
    }

    if (selectedChildId === childId) {
      setSelectedChildId(null);
    }
    await getNinos.execute();
    
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title: 'Niño eliminado',
      message: `${childName} ha sido eliminado correctamente.`,
    });
  };

  const openEditModal = (child: NinoWithAnthropometry['nino']) => {
    setEditError(null);
    setEditingChild({
      id: child.nin_id,
      name: child.nin_nombres,
      birthDate: child.nin_fecha_nac ? child.nin_fecha_nac.split('T')[0] || child.nin_fecha_nac : '',
    });
  };

  const handleEditSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!editingChild) return;

    const trimmedName = editingChild.name.trim();
    if (!trimmedName) {
      setEditError('El nombre es obligatorio.');
      return;
    }

    const originalName = childProfiles.find(c => c.nino.nin_id === editingChild.id)?.nino.nin_nombres;
    const originalBirthDate = childProfiles.find(c => c.nino.nin_id === editingChild.id)?.nino.nin_fecha_nac?.split('T')[0];
    
    const nameChanged = trimmedName !== originalName;
    const dateChanged = editingChild.birthDate !== originalBirthDate;

    const payload: Record<string, unknown> = {
      nin_nombres: trimmedName,
    };

    if (editingChild.birthDate) {
      payload.nin_fecha_nac = editingChild.birthDate;
    }

    const result = await updateNino.execute(editingChild.id, payload);

    if (!result) {
      setEditingChild(null);
      setEditError(null);
      setConfirmModal({
        isOpen: true,
        type: 'error',
        title: 'Error al actualizar',
        message: updateNino.error || 'No se pudo actualizar la información.',
      });
      return;
    }

    setEditingChild(null);
    setEditError(null);
    await getNinos.execute();
    
    // Mensaje personalizado según lo que cambió
    let title = 'Datos actualizados';
    let message = 'La información del niño ha sido actualizada correctamente.';
    
    if (nameChanged && dateChanged) {
      title = 'Nombre y fecha actualizados';
      message = 'El nombre y la fecha de nacimiento han sido actualizados correctamente.';
    } else if (nameChanged) {
      title = 'Nombre actualizado';
      message = 'El nombre del niño ha sido actualizado correctamente.';
    } else if (dateChanged) {
      title = 'Fecha actualizada';
      message = 'La fecha de nacimiento ha sido actualizada correctamente.';
    }
    
    setConfirmModal({
      isOpen: true,
      type: 'success',
      title,
      message,
    });
  };

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'Sin información';

    const parsed = new Date(dateString);
    if (Number.isNaN(parsed.getTime())) {
      return 'Sin información';
    }

    return parsed.toLocaleDateString('es-ES');
  };

  const calculateAge = (birthDate?: string | null) => {
    if (!birthDate) return 'Sin información';

    const birth = new Date(birthDate);
    if (Number.isNaN(birth.getTime())) {
      return 'Sin información';
    }

    const now = new Date();
    const diffTime = Math.abs(now.getTime() - birth.getTime());
    const diffMonths = Math.floor(diffTime / (1000 * 60 * 60 * 24 * 30.44));
    const years = Math.floor(diffMonths / 12);
    const months = diffMonths % 12;
    
    if (years > 0) {
      return `${years} año${years > 1 ? 's' : ''}${months > 0 ? ` y ${months} mes${months > 1 ? 'es' : ''}` : ''}`;
    } else {
      return `${months} mes${months === 1 ? '' : 'es'}`;
    }
  };

  // Si se está mostrando el perfil de un niño específico
  if (selectedChildId) {
    return (
      <ChildProfileView 
        childId={selectedChildId}
        onClose={() => {
          setSelectedChildId(null);
          // Actualizar la lista al regresar del perfil
          getNinos.execute();
        }}
      />
    );
  }

  // Vista principal: lista de niños
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Mis Niños</h2>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:from-emerald-600 hover:to-emerald-700 hover:shadow-xl transform hover:scale-105 transition-all duration-200"
        >
          👶 Agregar niño
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

      {childProfiles.length === 0 && !getNinos.loading && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-4">
            Aún no has registrado ningún niño
          </div>
          <p className="text-gray-400 mb-6">
            Comienza creando el perfil de un niño para hacer seguimiento de su crecimiento y estado nutricional.
          </p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-lg hover:from-emerald-600 hover:to-emerald-700 hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            👶 Registrar primer perfil
          </button>
        </div>
      )}

      {/* Lista de niños */}
      {childProfiles.length > 0 && (
        <>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Mis Niños Registrados</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {childProfiles.map((child) => {
              const { nino, antropometrias, ultimo_estado_nutricional: ultimoEstado } = child;
              const ultimaAntropometria = antropometrias && antropometrias.length > 0
                ? antropometrias[antropometrias.length - 1]
                : null;

              const statusLabel = formatClassification(ultimoEstado);
              const riskLabel = ultimoEstado?.risk_level ? ultimoEstado.risk_level.toUpperCase() : null;
              const theme = getClassificationTheme(ultimoEstado?.classification);
              const lastMeasurementDate = ultimaAntropometria ? formatDate(ultimaAntropometria.ant_fecha) : null;
              const updatedAt = formatDate(nino.actualizado_en);
              const createdAt = formatDate(nino.creado_en);
              const entityLabel = nino.ent_nombre || nino.ent_codigo || null;
              const entityLocation = [
                nino.ent_distrito,
                nino.ent_provincia,
                nino.ent_departamento,
              ].filter(Boolean).join(', ');

              return (
                <div
                  key={nino.nin_id}
                  className={`group rounded-2xl border p-6 shadow-sm transition-all duration-200 cursor-pointer hover:shadow-md ${theme.cardBorder} ${theme.cardBg}`}
                  onClick={() => setSelectedChildId(nino.nin_id)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault();
                      setSelectedChildId(nino.nin_id);
                    }
                  }}
                >
                  <div className="flex h-full gap-4">
                    <div className={`${theme.avatarBg} flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full text-sm font-semibold text-white`}>
                      {getInitials(nino.nin_nombres)}
                    </div>

                    <div className="flex-1 space-y-3">
                      <div className="relative flex flex-col gap-3 text-left">
                        <div className="flex flex-col gap-2 pr-20">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="text-xs font-semibold uppercase tracking-wide text-gray-600">Nombre:</span>
                            <span className="text-lg font-semibold leading-tight text-gray-900">{nino.nin_nombres}</span>
                          </div>
                          {statusLabel && (
                            <span className={`inline-block w-fit rounded-full px-3 py-1 text-[11px] font-semibold tracking-wide ${theme.badgeBg} ${theme.badgeText}`}>
                              {statusLabel}
                            </span>
                          )}
                        </div>

                        <div className="absolute right-0 top-0 flex items-center gap-2">
                          <button
                            type="button"
                            className="inline-flex h-9 items-center justify-center rounded-lg bg-blue-500 px-4 text-sm text-white shadow-sm transition hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300"
                            onClick={(event) => {
                              event.stopPropagation();
                              openEditModal(nino);
                            }}
                            aria-label={`Editar ${nino.nin_nombres}`}
                          >
                            ✏️
                          </button>
                          <button
                            type="button"
                            className="inline-flex h-9 items-center justify-center rounded-lg px-4 text-sm text-white shadow-sm transition hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-300"
                            style={{ backgroundColor: '#dc2626' }}
                            onClick={(event) => {
                              event.stopPropagation();
                              handleDeleteChild(nino.nin_id, nino.nin_nombres);
                            }}
                            aria-label={`Eliminar ${nino.nin_nombres}`}
                          >
                            🗑️
                          </button>
                        </div>
                      </div>

                      <div className="space-y-1 text-left text-sm">
                        <div>
                          <span className="font-semibold text-gray-700">Edad:</span>
                          <span className="ml-1 text-gray-600">{calculateAge(nino.nin_fecha_nac)}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Nacimiento:</span>
                          <span className="ml-1 text-gray-600">{formatDate(nino.nin_fecha_nac)}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Último registro:</span>
                          {ultimaAntropometria ? (
                            <span className="ml-1 text-gray-600">
                              {ultimaAntropometria.ant_peso_kg} kg • {ultimaAntropometria.ant_talla_cm} cm
                              {lastMeasurementDate && lastMeasurementDate !== 'Sin información' && (
                                <span className="text-xs text-gray-500"> ({lastMeasurementDate})</span>
                              )}
                            </span>
                          ) : (
                            <span className="ml-1 italic text-gray-400">Sin mediciones</span>
                          )}
                        </div>
                        <div>
                          <span className="font-semibold text-gray-700">Entidad:</span>
                          {entityLabel ? (
                            <span className="ml-1 text-gray-600">{entityLabel}</span>
                          ) : (
                            <span className="ml-1 italic text-gray-400">No asociada</span>
                          )}
                          {entityLabel && entityLocation && (
                            <span className="block text-xs font-normal leading-snug text-gray-500">{entityLocation}</span>
                          )}
                        </div>
                        {riskLabel && (
                          <div>
                            <span className="font-semibold text-gray-700">Riesgo:</span>
                            <span className="ml-1 text-gray-600">{riskLabel}</span>
                          </div>
                        )}
                      </div>

                      <div className="mt-3 border-t border-gray-100 pt-3 text-left text-xs text-gray-500">
                        <div>
                          <span className="font-semibold text-gray-600">Actualizado:</span>
                          <span className="ml-1 text-gray-500">{updatedAt}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-gray-600">Registrado:</span>
                          <span className="ml-1 text-gray-500">{createdAt}</span>
                        </div>
                      </div>
                    </div>

                    <div className="grid w-full max-w-[220px] grid-cols-2 gap-2 self-start sm:self-center">
                      <button
                        type="button"
                        className="col-span-1 rounded-md px-3 py-2 text-xs font-semibold text-white shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1"
                        style={{ backgroundColor: '#047857' }}
                        onClick={(event) => {
                          event.stopPropagation();
                          setSelectedChildId(nino.nin_id);
                        }}
                      >
                        📊 Análisis
                      </button>
                      <button
                        type="button"
                        className="col-span-1 rounded-md px-3 py-2 text-xs font-semibold text-white shadow-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1"
                        style={{ backgroundColor: '#000000' }}
                        onClick={(event) => {
                          event.stopPropagation();
                          // TODO: abrir modal antropometría
                        }}
                      >
                        📏 Medidas
                      </button>
                      <button
                        type="button"
                        className="col-span-1 rounded-md bg-orange-500 px-3 py-2 text-xs font-semibold text-white shadow-sm transition-all duration-200 hover:bg-orange-600 active:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-400 focus:ring-offset-1"
                        onClick={(event) => {
                          event.stopPropagation();
                          // TODO: abrir modal alergias
                        }}
                      >
                        🧡 Alergias
                      </button>
                      <button
                        type="button"
                        className="col-span-1 rounded-md bg-blue-500 px-3 py-2 text-xs font-semibold text-white shadow-sm transition-all duration-200 hover:bg-blue-600 active:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-1"
                        onClick={(event) => {
                          event.stopPropagation();
                          // TODO: abrir modal entidades
                        }}
                      >
                        🏥 Entidad
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}

      {/* Información adicional */}
      {childProfiles.length > 0 && (
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

      <Dialog open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen}>
        <DialogContent className="w-full sm:w-[90vw] md:w-[80vw] lg:w-[70vw] xl:w-[65vw] max-w-[1000px] my-16 p-0 max-h-[85vh] overflow-y-auto rounded-2xl">
          <DialogHeader className="p-4 pb-2">
            <DialogTitle className="text-base font-bold text-emerald-900">Registrar nuevo niño</DialogTitle>
          </DialogHeader>
          <CreateChildForm
            onSuccess={handleChildCreated}
            onCancel={() => setIsCreateModalOpen(false)}
          />
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(editingChild)} onOpenChange={(open) => {
        if (!open) {
          setEditingChild(null);
          setEditError(null);
        }
      }}>
        <DialogContent className="w-full max-w-[480px] p-0 overflow-hidden rounded-2xl">
          <form onSubmit={handleEditSubmit} className="space-y-4 p-6">
            <DialogHeader className="pb-2">
              <DialogTitle className="text-lg font-semibold text-emerald-900">Editar información</DialogTitle>
            </DialogHeader>

            <div className="space-y-1">
              <label className="text-sm font-semibold text-gray-700" htmlFor="child-name">Nombre</label>
              <input
                id="child-name"
                type="text"
                value={editingChild?.name ?? ''}
                onChange={(event) =>
                  setEditingChild((prev) => prev ? { ...prev, name: event.target.value } : prev)
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
                placeholder="Nombre completo"
                required
              />
            </div>

            <div className="space-y-1">
              <label className="text-sm font-semibold text-gray-700" htmlFor="child-birthdate">Fecha de nacimiento</label>
              <input
                id="child-birthdate"
                type="date"
                value={editingChild?.birthDate ?? ''}
                onChange={(event) =>
                  setEditingChild((prev) => prev ? { ...prev, birthDate: event.target.value } : prev)
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-200"
              />
              <p className="text-xs text-gray-500">La edad se recalcula automáticamente según la fecha.</p>
            </div>

            {editError && (
              <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-xs font-medium text-red-700">
                {editError}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => {
                  setEditingChild(null);
                  setEditError(null);
                }}
                className="rounded-md border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-600 transition hover:bg-gray-100"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-offset-1"
                disabled={updateNino.loading}
              >
                {updateNino.loading ? 'Guardando…' : 'Guardar cambios'}
              </button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Modal de confirmación de eliminación */}
      <ActionConfirmModal
        isOpen={deleteConfirmModal.isOpen}
        onClose={() => setDeleteConfirmModal({ isOpen: false, childId: null, childName: '' })}
        onConfirm={confirmDeleteChild}
        title="¿Eliminar niño?"
        description={`¿Estás seguro de que deseas eliminar a "${deleteConfirmModal.childName}" y todos sus datos asociados? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        isLoading={deleteNino.loading}
      />

      {/* Modal de confirmación de acciones */}
      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        onClose={() => setConfirmModal({ isOpen: false, type: 'success', title: '', message: '' })}
        type={confirmModal.type}
        title={confirmModal.title}
        message={confirmModal.message}
      />
    </div>
  );
};

export default ChildrenList;
