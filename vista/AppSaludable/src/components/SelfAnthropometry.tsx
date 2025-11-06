import React, { useEffect, useMemo, useState } from 'react';
import AnthropometryManagement from './AnthropometryManagement';
import AllergiesAndEntities from './AllergiesAndEntities';
import {
  useNinosApi,
  useChildProfileApi,
  useAnthropometryApi,
  useNutritionalEvaluationApi,
  useAllergiesApi,
  useEntitiesApi
} from '../hooks/useApi';
import type { NinoWithAnthropometry, TipoAlergiaResponse } from '../types/api';
import CreateChildForm from './children/CreateChildForm';
import {
  BarChart2,
  Building2,
  HeartPulse,
  MessageCircle,
  Pill,
  PlusCircle,
  Sparkles,
  Trash2
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from './ui/dialog';
import { toast } from 'sonner';

interface ClinicalSection {
  id: 'anthropometry' | 'allergies-entities';
  title: string;
  icon: string;
  description: string;
}

const CLINICAL_SECTIONS: ClinicalSection[] = [
  {
    id: 'anthropometry',
    title: 'Antropometría',
    icon: '📏',
    description: 'Registro de medidas, historial y evaluación nutricional',
  },
  {
    id: 'allergies-entities',
    title: 'Alergias y Entidades',
    icon: '🏥',
    description: 'Gestión de alergias y asociación con entidades de salud',
  },
];

const SEVERITY_OPTIONS: Array<{ value: 'LEVE' | 'MODERADA' | 'SEVERA'; label: string }> = [
  { value: 'LEVE', label: 'Leve' },
  { value: 'MODERADA', label: 'Moderada' },
  { value: 'SEVERA', label: 'Severa' },
];

type ChildModalType = 'analysis' | 'measure' | 'allergies' | 'entity';

const CARD_CONTAINER = 'rounded-2xl border border-gray-200 bg-white shadow-sm';
const PRIMARY_BUTTON =
  'inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-5 py-3 text-sm font-semibold text-primary-foreground shadow-sm transition-colors duration-200 hover:bg-primary-dark focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-60';
const INPUT_STYLES =
  'w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none';
const LABEL_STYLES = 'mb-1 block text-xs font-medium text-slate-600';

export default function SelfAnthropometry() {
  const [activeSection, setActiveSection] = useState<ClinicalSection['id']>('anthropometry');
  const [childFlow, setChildFlow] = useState<'unknown' | 'yes' | 'no'>('unknown');
  const [isCreateChildModalOpen, setIsCreateChildModalOpen] = useState(false);
  const [selectedChildId, setSelectedChildId] = useState<number | null>(null);
  const [activeChildModal, setActiveChildModal] = useState<ChildModalType | null>(null);
  const [isFlowConfirmOpen, setIsFlowConfirmOpen] = useState(false);

  const { getNinos, updateNino, deleteNino } = useNinosApi();
  const { getChildWithData } = useChildProfileApi();
  const { addAnthropometry } = useAnthropometryApi();
  const { evaluateNutritionalStatus } = useNutritionalEvaluationApi();
  const { addAllergy, removeAllergy, getAllergyTypes } = useAllergiesApi();
  const { searchEntities } = useEntitiesApi();

  const [measurementForm, setMeasurementForm] = useState({
    ant_peso_kg: '',
    ant_talla_cm: '',
    ant_fecha: new Date().toISOString().split('T')[0],
  });
  const [addingMeasurement, setAddingMeasurement] = useState(false);
  const [evaluatingStatus, setEvaluatingStatus] = useState(false);
  const [newAllergy, setNewAllergy] = useState<{ ta_codigo: string; severidad: 'LEVE' | 'MODERADA' | 'SEVERA' }>({
    ta_codigo: '',
    severidad: 'LEVE',
  });
  const [allergySearch, setAllergySearch] = useState('');
  const [allergyOptions, setAllergyOptions] = useState<TipoAlergiaResponse[]>([]);
  const [addingAllergy, setAddingAllergy] = useState(false);
  const [removingAllergyId, setRemovingAllergyId] = useState<number | null>(null);
  const [entityQuery, setEntityQuery] = useState('');
  const [entityResults, setEntityResults] = useState<any[]>([]);
  const [selectedEntityResult, setSelectedEntityResult] = useState<any | null>(null);
  const [currentEntity, setCurrentEntity] = useState<any | null>(null);
  const [updatingEntity, setUpdatingEntity] = useState(false);
  const [editingChild, setEditingChild] = useState<{
    id: number;
    name: string;
    birthDate: string;
  } | null>(null);
  const [editError, setEditError] = useState<string | null>(null);



  const fetchChildDetail = getChildWithData.execute;
  const fetchAllergyCatalog = getAllergyTypes.execute;
  const fetchEntities = searchEntities.execute;

  useEffect(() => {
    // OPTIMIZACIÓN: Defer la carga de niños para no bloquear render inicial
    const timeoutId = setTimeout(() => {
      getNinos.execute();
    }, 0);
    return () => clearTimeout(timeoutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (Array.isArray(getNinos.data) && getNinos.data.length > 0) {
      setChildFlow('yes');
    }
  }, [getNinos.data]);

  useEffect(() => {
    if (childFlow !== 'yes') {
      setIsCreateChildModalOpen(false);
      setIsFlowConfirmOpen(false);
    }
  }, [childFlow]);

  const children = useMemo<NinoWithAnthropometry[]>(() => {
    if (!Array.isArray(getNinos.data)) {
      return [];
    }
    return getNinos.data;
  }, [getNinos.data]);

  const selectedChildInfo = getChildWithData.data?.nino;

  const selectedChildEntity = useMemo(() => {
    if (!selectedChildInfo || !selectedChildInfo.ent_id) {
      return null;
    }
    return {
      ent_id: selectedChildInfo.ent_id,
      ent_nombre: selectedChildInfo.ent_nombre,
      ent_codigo: selectedChildInfo.ent_codigo,
      ent_direccion: selectedChildInfo.ent_direccion,
      ent_departamento: selectedChildInfo.ent_departamento,
      ent_provincia: selectedChildInfo.ent_provincia,
      ent_distrito: selectedChildInfo.ent_distrito,
    };
  }, [
    selectedChildInfo?.ent_id,
    selectedChildInfo?.ent_nombre,
    selectedChildInfo?.ent_codigo,
    selectedChildInfo?.ent_direccion,
    selectedChildInfo?.ent_departamento,
    selectedChildInfo?.ent_provincia,
    selectedChildInfo?.ent_distrito,
  ]);

  useEffect(() => {
    if (childFlow === 'yes' && !isCreateChildModalOpen && children.length > 0 && !selectedChildId) {
      setSelectedChildId(children[0].nino.nin_id);
    }
  }, [childFlow, isCreateChildModalOpen, children, selectedChildId]);

  useEffect(() => {
    if (!selectedChildId) {
      return;
    }
    // OPTIMIZACIÓN: Usar requestIdleCallback para cargar datos sin bloquear UI
    const timeoutId = setTimeout(() => {
      fetchChildDetail(selectedChildId);
    }, 0); // Defer para siguiente tick

    return () => clearTimeout(timeoutId);
  }, [selectedChildId, fetchChildDetail]);

  useEffect(() => {
    setMeasurementForm({
      ant_peso_kg: '',
      ant_talla_cm: '',
      ant_fecha: new Date().toISOString().split('T')[0],
    });
    setNewAllergy({ ta_codigo: '', severidad: 'LEVE' });
    setAllergySearch('');
    setAllergyOptions([]);
    setEntityQuery('');
    setEntityResults([]);
    setSelectedEntityResult(null);
  }, [selectedChildId]);

  useEffect(() => {
    if (!allergySearch.trim()) {
      setAllergyOptions([]);
      return;
    }
    // OPTIMIZACIÓN: Aumentar debounce a 500ms para reducir llamadas API
    const handler = setTimeout(async () => {
      const options = await fetchAllergyCatalog(allergySearch.trim());
      setAllergyOptions(options || []);
    }, 500);
    return () => clearTimeout(handler);
  }, [allergySearch, fetchAllergyCatalog]);

  useEffect(() => {
    if (!entityQuery.trim()) {
      setEntityResults([]);
      return;
    }
    // OPTIMIZACIÓN: Aumentar debounce a 500ms para reducir llamadas API
    const handler = setTimeout(async () => {
      const results = await fetchEntities(entityQuery.trim());
      setEntityResults(results || []);
    }, 500);
    return () => clearTimeout(handler);
  }, [entityQuery, fetchEntities]);

  useEffect(() => {
    if (!selectedChildId || !selectedChildEntity) {
      setCurrentEntity(null);
      return;
    }
    setCurrentEntity(selectedChildEntity);
  }, [selectedChildId, selectedChildEntity]);

  const handleSelectFlow = (flow: 'yes' | 'no') => {
    if (flow === 'no') {
      setChildFlow('no');
      setSelectedChildId(null);
      setIsCreateChildModalOpen(false);
      setIsFlowConfirmOpen(false);
      return;
    }

    if (childFlow !== 'yes') {
      setChildFlow('yes');
    }

    setIsFlowConfirmOpen(true);
  };

  const handleStartChildRegistration = () => {
    setIsFlowConfirmOpen(false);
    setIsCreateChildModalOpen(true);
  };

  const handleSelectChild = (childId: number) => {
    setSelectedChildId(childId);
    setIsCreateChildModalOpen(false);
  };

  const handleOpenChildModal = async (modal: ChildModalType, childId: number) => {
    if (selectedChildId !== childId) {
      handleSelectChild(childId);
    }
    setActiveChildModal(modal);

    // Si es el modal de medidas, pre-llenar con las últimas mediciones
    if (modal === 'measure') {
      // Cargar datos del niño si no están ya cargados
      const childData = await fetchChildDetail(childId);

      if (childData?.antropometrias && childData.antropometrias.length > 0) {
        const latestMeasurement = childData.antropometrias[0];
        setMeasurementForm({
          ant_peso_kg: String(latestMeasurement.ant_peso_kg),
          ant_talla_cm: String(latestMeasurement.ant_talla_cm),
          ant_fecha: new Date().toISOString().split('T')[0], // Fecha actual para el nuevo registro
        });
      }
    }
  };

  const handleCloseChildModal = () => {
    setActiveChildModal(null);
    setAllergySearch('');
    setAllergyOptions([]);
    setNewAllergy({ ta_codigo: '', severidad: 'LEVE' });
    setEntityQuery('');
    setEntityResults([]);
    setSelectedEntityResult(null);
    setMeasurementForm({
      ant_peso_kg: '',
      ant_talla_cm: '',
      ant_fecha: new Date().toISOString().split('T')[0],
    });
  };

  const handleChildCreated = (childId: number) => {
    setIsCreateChildModalOpen(false);
    setSelectedChildId(childId);
    getNinos.execute().then(() => {
      fetchChildDetail(childId);
    });
  };

  const handleMeasurementSubmit = async (event: React.FormEvent): Promise<boolean> => {
    event.preventDefault();
    if (!selectedChildId || !measurementForm.ant_peso_kg || !measurementForm.ant_talla_cm) {
      toast.error('Campos incompletos', {
        description: 'Por favor, completa peso y talla.',
      });
      return false;
    }

    setAddingMeasurement(true);
    let success = false;
    try {
      const result = await addAnthropometry.execute(selectedChildId, {
        ant_peso_kg: parseFloat(measurementForm.ant_peso_kg),
        ant_talla_cm: parseFloat(measurementForm.ant_talla_cm),
        ant_fecha: measurementForm.ant_fecha,
      });

      if (result) {
        await evaluateNutritionalStatus.execute(selectedChildId);
        await fetchChildDetail(selectedChildId);
        await getNinos.execute();
        setMeasurementForm({
          ant_peso_kg: '',
          ant_talla_cm: '',
          ant_fecha: new Date().toISOString().split('T')[0],
        });
        success = true;

        toast.success('Medición agregada', {
          description: 'Medición agregada y estado nutricional actualizado.',
        });
      } else {
        toast.error('Error al agregar medición', {
          description: addAnthropometry.error || 'No se pudo agregar la medición.',
        });
      }
    } finally {
      setAddingMeasurement(false);
    }
    return success;
  };

  const handleEvaluateStatus = async () => {
    if (!selectedChildId) {
      return;
    }
    setEvaluatingStatus(true);
    try {
      const result = await evaluateNutritionalStatus.execute(selectedChildId);
      if (result) {
        await fetchChildDetail(selectedChildId);
        await getNinos.execute();

        toast.success('Evaluación actualizada', {
          description: 'La evaluación nutricional se actualizó correctamente.',
        });
      } else {
        toast.error('Error al evaluar', {
          description: evaluateNutritionalStatus.error || 'No se pudo actualizar la evaluación.',
        });
      }
    } finally {
      setEvaluatingStatus(false);
    }
  };

  const handleAddAllergyClick = async (): Promise<boolean> => {
    if (!selectedChildId || !newAllergy.ta_codigo) {
      toast.error('Datos incompletos', {
        description: 'Selecciona una alergia antes de continuar.',
      });
      return false;
    }

    setAddingAllergy(true);
    let success = false;
    try {
      const result = await addAllergy.execute(selectedChildId, { ta_codigo: newAllergy.ta_codigo, severidad: newAllergy.severidad });
      if (result) {
        await fetchChildDetail(selectedChildId);
        await getNinos.execute();
        setNewAllergy({ ta_codigo: '', severidad: 'LEVE' });
        setAllergySearch('');
        setAllergyOptions([]);
        setActiveChildModal(null);
        success = true;

        toast.success('Alergia agregada', {
          description: 'Se agregó la alergia correctamente.',
        });
      } else {
        toast.error('Error al agregar alergia', {
          description: addAllergy.error || 'No se pudo agregar la alergia.',
        });
      }
    } finally {
      setAddingAllergy(false);
    }
    return success;
  };

  const handleRemoveAllergyClick = async (allergyId: number, allergyName: string) => {
    if (!selectedChildId) {
      return;
    }

    const confirmed = window.confirm(`¿Estás seguro de que deseas eliminar la alergia: ${allergyName}?`);
    if (!confirmed) return;

    setRemovingAllergyId(allergyId);
    try {
      const result = await removeAllergy.execute(selectedChildId, allergyId);
      if (result) {
        await fetchChildDetail(selectedChildId);
        await getNinos.execute();

        toast.success('Alergia eliminada', {
          description: `Se eliminó la alergia: ${allergyName}`,
        });
      } else {
        toast.error('Error al eliminar alergia', {
          description: removeAllergy.error || 'No se pudo eliminar la alergia.',
        });
      }
    } finally {
      setRemovingAllergyId(null);
    }
  };

  const handleAssignEntity = async (): Promise<boolean> => {
    if (!selectedChildId || !selectedEntityResult) {
      toast.error('Datos incompletos', {
        description: 'Selecciona una entidad antes de continuar.',
      });
      return false;
    }
    setUpdatingEntity(true);
    let success = false;
    try {
      const result = await updateNino.execute(selectedChildId, { ent_id: selectedEntityResult.ent_id });
      if (result) {
        await fetchChildDetail(selectedChildId);
        setCurrentEntity(selectedEntityResult);
        setEntityQuery('');
        setEntityResults([]);
        setSelectedEntityResult(null);
        await getNinos.execute();
        success = true;

        toast.success('Entidad asociada', {
          description: `Se asoció correctamente con ${selectedEntityResult.ent_nombre}.`,
        });
      } else {
        toast.error('Error al asociar entidad', {
          description: updateNino.error || 'No se pudo asociar la entidad.',
        });
      }
    } finally {
      setUpdatingEntity(false);
    }
    return success;
  };

  const handleClearEntity = async () => {
    if (!selectedChildId) {
      return;
    }

    const confirmed = window.confirm('¿Estás seguro de que deseas desasociar esta entidad?');
    if (!confirmed) return;

    setUpdatingEntity(true);
    try {
      const result = await updateNino.execute(selectedChildId, { ent_id: null });
      if (result) {
        await fetchChildDetail(selectedChildId);
        setCurrentEntity(null);
        setEntityQuery('');
        setEntityResults([]);
        setSelectedEntityResult(null);
        await getNinos.execute();

        toast.success('Entidad desasociada', {
          description: 'La entidad se desasoció correctamente.',
        });
      } else {
        toast.error('Error al desasociar entidad', {
          description: updateNino.error || 'No se pudo desasociar la entidad.',
        });
      }
    } finally {
      setUpdatingEntity(false);
    }
  };

  const handleDeleteChild = async (childId: number, childName: string) => {
    const confirmed = window.confirm(`¿Estás seguro de que deseas eliminar a "${childName}" y todos sus datos asociados? Esta acción no se puede deshacer.`);
    if (!confirmed) return;

    const result = await deleteNino.execute(childId);
    if (!result) {
      toast.error('Error al eliminar', {
        description: deleteNino.error || 'No se pudo eliminar al niño.',
      });
      return;
    }

    if (selectedChildId === childId) {
      setSelectedChildId(null);
      setActiveChildModal(null);
    }

    const updated = await getNinos.execute();
    if (!updated || updated.length === 0) {
      setChildFlow('no');
    }
    if (childId === getChildWithData.data?.nino.nin_id) {
      getChildWithData.reset();
    }

    toast.success('Niño eliminado', {
      description: `${childName} ha sido eliminado correctamente.`,
    });
  };

  const openEditChildModal = (child: NinoWithAnthropometry['nino']) => {
    setEditError(null);
    setEditingChild({
      id: child.nin_id,
      name: child.nin_nombres,
      birthDate: child.nin_fecha_nac ? child.nin_fecha_nac.split('T')[0] || child.nin_fecha_nac : '',
    });
  };

  const handleEditChildSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!editingChild) return;

    const trimmedName = editingChild.name.trim();
    if (!trimmedName) {
      setEditError('El nombre es obligatorio.');
      toast.error('Nombre requerido', {
        description: 'El nombre es obligatorio.',
      });
      return;
    }

    const payload: Record<string, unknown> = { nin_nombres: trimmedName };
    if (editingChild.birthDate) {
      payload.nin_fecha_nac = editingChild.birthDate;
    }

    const result = await updateNino.execute(editingChild.id, payload);
    if (!result) {
      setEditError(updateNino.error || 'No se pudo actualizar la información.');
      toast.error('Error al actualizar', {
        description: updateNino.error || 'No se pudo actualizar la información.',
      });
      return;
    }

    setEditingChild(null);
    setEditError(null);
    await getNinos.execute();
    if (selectedChildId === editingChild.id) {
      await fetchChildDetail(editingChild.id);
    }

    toast.success('Información actualizada', {
      description: 'Los datos del niño se actualizaron correctamente.',
    });
  };

  const formatDate = (iso: string | null | undefined) => {
    if (!iso) return '—';
    try {
      return new Date(iso).toLocaleDateString('es-ES');
    } catch {
      return iso;
    }
  };

  const describeAge = (birthDate: string | null | undefined) => {
    if (!birthDate) {
      return 'Sin datos';
    }
    const birth = new Date(birthDate);
    if (Number.isNaN(birth.getTime())) {
      return 'Sin datos';
    }
    const now = new Date();
    const diffMonths = Math.max(0, Math.floor((now.getTime() - birth.getTime()) / (1000 * 60 * 60 * 24 * 30.44)));
    const years = Math.floor(diffMonths / 12);
    const months = diffMonths % 12;
    if (years > 0) {
      return `${years} año${years > 1 ? 's' : ''}${months ? ` y ${months} mes${months > 1 ? 'es' : ''}` : ''}`;
    }
    return `${months} mes${months === 1 ? '' : 'es'}`;
  };

  const getInitials = (name: string | null | undefined) => {
    if (!name) return 'NI';
    const parts = name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() || '');
    return parts.join('') || 'NI';
  };

  const childDetail = (getChildWithData.data as NinoWithAnthropometry | null) || null;

  const renderChildModalContent = () => {
    if (!activeChildModal) {
      return null;
    }

    const titles: Record<ChildModalType, string> = {
      analysis: 'Análisis nutricional',
      measure: 'Actualizar medidas',
      allergies: 'Gestión de alergias',
      entity: 'Entidad de seguimiento',
    } as const;

    const descriptions: Record<ChildModalType, string> = {
      analysis: 'Recomendaciones y estado actual del menor seleccionado.',
      measure: 'Registra o actualiza las mediciones antropométricas.',
      allergies: 'Consulta y ajusta las alergias registradas.',
      entity: 'Consulta o cambia la entidad asociada.',
    } as const;

    if (getChildWithData.loading) {
      return (
        <>
          <DialogHeader className="text-left">
            <DialogTitle>{titles[activeChildModal]}</DialogTitle>
            <DialogDescription>{descriptions[activeChildModal]}</DialogDescription>
          </DialogHeader>
          <div className="py-10 text-center text-sm text-slate-500">Cargando información…</div>
        </>
      );
    }

    if (!childDetail) {
      return (
        <>
          <DialogHeader className="text-left">
            <DialogTitle>{titles[activeChildModal]}</DialogTitle>
            <DialogDescription>{descriptions[activeChildModal]}</DialogDescription>
          </DialogHeader>
          <div className="py-10 text-center text-sm text-slate-500">
            No se encontró información del niño seleccionado.
          </div>
        </>
      );
    }

    const info = childDetail.nino;
    const latestAnthropometry = childDetail.antropometrias?.[0] ?? null;
    const nutritionalStatus = childDetail.ultimo_estado_nutricional || null;

    if (activeChildModal === 'analysis') {
      return (
        <>
          <DialogHeader className="text-left">
            <DialogTitle>{titles.analysis}</DialogTitle>
            <DialogDescription>
              Reporte actualizado para {info.nin_nombres}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-5">
            <section className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h4 className="text-sm font-semibold text-slate-900">Medición más reciente</h4>
              {latestAnthropometry ? (
                <dl className="mt-3 grid grid-cols-2 gap-3 text-sm text-slate-700">
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-slate-500">Fecha</dt>
                    <dd>{formatDate(latestAnthropometry.ant_fecha)}</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-slate-500">Peso</dt>
                    <dd>{latestAnthropometry.ant_peso_kg} kg</dd>
                  </div>
                  <div>
                    <dt className="text-xs uppercase tracking-wide text-slate-500">Talla</dt>
                    <dd>{latestAnthropometry.ant_talla_cm} cm</dd>
                  </div>
                  {latestAnthropometry.imc && (
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-slate-500">IMC</dt>
                      <dd>{Number(latestAnthropometry.imc).toFixed(2)}</dd>
                    </div>
                  )}
                </dl>
              ) : (
                <p className="mt-3 text-sm text-slate-600">Aún no se han registrado mediciones.</p>
              )}
            </section>

            <section className="rounded-xl border border-slate-200 bg-white p-4">
              <h4 className="text-sm font-semibold text-slate-900">Estado nutricional</h4>
              {nutritionalStatus ? (
                <div className="mt-3 space-y-2 text-sm text-slate-700">
                  <div className="flex justify-between">
                    <span>Diagnóstico</span>
                    <span className="font-semibold">{nutritionalStatus.classification}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>IMC</span>
                    <span className="font-semibold">{nutritionalStatus.imc.toFixed(2)}</span>
                  </div>
                  {nutritionalStatus.percentile !== undefined && (
                    <div className="flex justify-between">
                      <span>Percentil</span>
                      <span className="font-semibold">{nutritionalStatus.percentile.toFixed(1)}%</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span>Nivel de riesgo</span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-semibold ${nutritionalStatus.risk_level === 'ALTO'
                        ? 'bg-red-100 text-red-700'
                        : nutritionalStatus.risk_level === 'MODERADO'
                          ? 'bg-yellow-100 text-yellow-700'
                          : 'bg-emerald-100 text-emerald-700'
                        }`}
                    >
                      {nutritionalStatus.risk_level}
                    </span>
                  </div>
                  {nutritionalStatus.recommendations?.length ? (
                    <div className="pt-2">
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-2">Recomendaciones</p>
                      <div className="mt-2 space-y-3">
                        {nutritionalStatus.recommendations.map((rec, index) => (
                          <div key={index} className="flex gap-2">
                            <span className="text-lg flex-shrink-0">{rec.icono}</span>
                            <div className="flex-1">
                              <p className="font-medium text-sm text-slate-900">{rec.titulo}</p>
                              <p className="text-xs text-slate-600 mt-0.5">{rec.descripcion}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </div>
              ) : (
                <p className="mt-3 text-sm text-slate-600">
                  Necesitas registrar una medición para generar el análisis.
                </p>
              )}
            </section>

            {childDetail.antropometrias?.length ? (
              <section className="overflow-hidden rounded-xl border border-slate-200">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                  <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                    <tr>
                      <th className="px-4 py-2 text-left">Fecha</th>
                      <th className="px-4 py-2 text-right">Peso (kg)</th>
                      <th className="px-4 py-2 text-right">Talla (cm)</th>
                      <th className="px-4 py-2 text-right">IMC</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 bg-white">
                    {childDetail.antropometrias.slice(0, 6).map((record) => (
                      <tr key={record.ant_id}>
                        <td className="px-4 py-2">{formatDate(record.ant_fecha)}</td>
                        <td className="px-4 py-2 text-right">{record.ant_peso_kg}</td>
                        <td className="px-4 py-2 text-right">{record.ant_talla_cm}</td>
                        <td className="px-4 py-2 text-right">{record.imc ? Number(record.imc).toFixed(2) : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </section>
            ) : null}
          </div>
          <DialogFooter className="sm:justify-end">
            <button
              type="button"
              onClick={handleCloseChildModal}
              className="inline-flex items-center justify-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100"
            >
              Cerrar
            </button>
            <button
              type="button"
              onClick={handleEvaluateStatus}
              disabled={evaluatingStatus}
              className={PRIMARY_BUTTON}
            >
              {evaluatingStatus ? 'Actualizando…' : 'Actualizar estado'}
            </button>
          </DialogFooter>
        </>
      );
    }

    if (activeChildModal === 'measure') {
      return (
        <>
          <DialogHeader className="text-left">
            <DialogTitle>{titles.measure}</DialogTitle>
            <DialogDescription>
              Ingresa nuevas mediciones para {info.nin_nombres}
            </DialogDescription>
          </DialogHeader>
          <form
            className="space-y-4"
            onSubmit={async (event) => {
              const success = await handleMeasurementSubmit(event);
              if (success) {
                setActiveChildModal(null);
              }
            }}
          >
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className={LABEL_STYLES}>Peso (kg)</label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="200"
                  value={measurementForm.ant_peso_kg}
                  onChange={(e) => setMeasurementForm((prev) => ({ ...prev, ant_peso_kg: e.target.value }))}
                  className={INPUT_STYLES}
                  required
                />
              </div>
              <div>
                <label className={LABEL_STYLES}>Talla (cm)</label>
                <input
                  type="number"
                  step="0.1"
                  min="30"
                  max="250"
                  value={measurementForm.ant_talla_cm}
                  onChange={(e) => setMeasurementForm((prev) => ({ ...prev, ant_talla_cm: e.target.value }))}
                  className={INPUT_STYLES}
                  required
                />
              </div>
            </div>
            <div>
              <label className={LABEL_STYLES}>Fecha</label>
              <input
                type="date"
                value={measurementForm.ant_fecha}
                onChange={(e) => setMeasurementForm((prev) => ({ ...prev, ant_fecha: e.target.value }))}
                className={INPUT_STYLES}
                required
              />
            </div>
            <DialogFooter className="sm:justify-end">
              <button
                type="button"
                onClick={handleCloseChildModal}
                className="inline-flex items-center justify-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={addingMeasurement}
                className={PRIMARY_BUTTON}
              >
                <HeartPulse className="h-4 w-4" /> {addingMeasurement ? 'Guardando…' : 'Guardar medida'}
              </button>
            </DialogFooter>
          </form>
        </>
      );
    }

    if (activeChildModal === 'allergies') {
      return (
        <>
          <DialogHeader className="text-left">
            <DialogTitle>{titles.allergies}</DialogTitle>
            <DialogDescription>
              Alergias registradas para {info.nin_nombres}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h4 className="text-sm font-semibold text-slate-900">Listado actual</h4>
              <div className="mt-3 flex flex-wrap gap-2">
                {childDetail.alergias?.length ? (
                  childDetail.alergias.map((alergia) => (
                    <span
                      key={alergia.na_id}
                      className="inline-flex items-center gap-2 rounded-full border border-amber-200 bg-white px-3 py-1 text-xs text-amber-700"
                    >
                      <span className="font-semibold text-amber-900">{alergia.ta_nombre}</span>
                      <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-semibold uppercase">
                        {alergia.na_severidad}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveAllergyClick(alergia.na_id, alergia.ta_nombre)}
                        disabled={removingAllergyId === alergia.na_id}
                        className="text-amber-600 hover:text-red-600"
                        aria-label="Eliminar alergia"
                      >
                        {removingAllergyId === alergia.na_id ? '…' : '×'}
                      </button>
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-500">No hay alergias registradas.</span>
                )}
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <label className={LABEL_STYLES}>Buscar alergia</label>
                <input
                  value={allergySearch}
                  onChange={(e) => {
                    setAllergySearch(e.target.value);
                    setNewAllergy((prev) => ({ ...prev, ta_codigo: '' }));
                  }}
                  placeholder="Nombre o código"
                  className={INPUT_STYLES}
                />
                {allergySearch && allergyOptions.length > 0 && (
                  <div className="mt-2 max-h-48 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-sm">
                    {allergyOptions.slice(0, 8).map((option) => (
                      <button
                        key={option.ta_codigo}
                        type="button"
                        onClick={() => {
                          setAllergySearch(option.ta_nombre);
                          setNewAllergy((prev) => ({ ...prev, ta_codigo: option.ta_codigo }));
                          setAllergyOptions([]);
                        }}
                        className="w-full border-b border-slate-100 px-3 py-2 text-left text-sm hover:bg-primary/10 last:border-b-0"
                      >
                        <div className="font-medium text-slate-900">{option.ta_nombre}</div>
                        <div className="text-xs text-slate-500">{option.ta_categoria}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={LABEL_STYLES}>Código</label>
                  <input
                    value={newAllergy.ta_codigo}
                    onChange={(e) => setNewAllergy((prev) => ({ ...prev, ta_codigo: e.target.value }))}
                    className={INPUT_STYLES}
                    placeholder="Ej: LC01"
                  />
                </div>
                <div>
                  <label className={LABEL_STYLES}>Severidad</label>
                  <select
                    value={newAllergy.severidad}
                    onChange={(e) => setNewAllergy((prev) => ({ ...prev, severidad: e.target.value as any }))}
                    className={INPUT_STYLES}
                  >
                    {SEVERITY_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <DialogFooter className="sm:justify-end">
                <button
                  type="button"
                  onClick={handleCloseChildModal}
                  className="inline-flex items-center justify-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100"
                >
                  Cerrar
                </button>
                <button
                  type="button"
                  onClick={handleAddAllergyClick}
                  disabled={addingAllergy || !newAllergy.ta_codigo}
                  className={PRIMARY_BUTTON}
                >
                  <Pill className="h-4 w-4" /> {addingAllergy ? 'Guardando…' : 'Agregar alergia'}
                </button>
              </DialogFooter>
            </div>
          </div>
        </>
      );
    }

    if (activeChildModal === 'entity') {
      return (
        <>
          <DialogHeader className="text-left">
            <DialogTitle>{titles.entity}</DialogTitle>
            <DialogDescription>
              Administración de entidad para {info.nin_nombres}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <h4 className="text-sm font-semibold text-slate-900">Entidad actual</h4>
              {currentEntity ? (
                <div className="mt-3 space-y-1 text-sm text-slate-700">
                  <p className="font-semibold text-slate-900">{currentEntity.ent_nombre}</p>
                  <p className="text-xs text-slate-500">
                    {[currentEntity.ent_distrito, currentEntity.ent_provincia, currentEntity.ent_departamento]
                      .filter(Boolean)
                      .join(', ') || 'Sin ubicación especificada'}
                  </p>
                  <button
                    type="button"
                    onClick={handleClearEntity}
                    disabled={updatingEntity}
                    className="mt-2 inline-flex items-center gap-1 rounded-full bg-red-50 px-3 py-1 text-xs font-semibold text-red-700 hover:bg-red-100"
                  >
                    {updatingEntity ? 'Quitando…' : 'Desasociar entidad'}
                  </button>
                </div>
              ) : (
                <p className="mt-3 text-sm text-slate-600">No hay una entidad asociada actualmente.</p>
              )}
            </div>

            <div className="space-y-3">
              <div>
                <label className={LABEL_STYLES}>Buscar entidad</label>
                <input
                  value={entityQuery}
                  onChange={(e) => {
                    setEntityQuery(e.target.value);
                    setSelectedEntityResult(null);
                  }}
                  placeholder="Nombre o código"
                  className={INPUT_STYLES}
                />
                {entityQuery && entityResults.length > 0 && (
                  <div className="mt-2 max-h-48 overflow-y-auto rounded-lg border border-slate-200 bg-white shadow-sm">
                    {entityResults.map((entity: any) => (
                      <button
                        key={entity.ent_id}
                        type="button"
                        onClick={() => {
                          setSelectedEntityResult(entity);
                          setEntityQuery(entity.ent_nombre);
                          setEntityResults([]);
                        }}
                        className="w-full border-b border-slate-100 px-3 py-2 text-left text-sm hover:bg-primary/10 last:border-b-0"
                      >
                        <div className="font-medium text-slate-900">{entity.ent_nombre}</div>
                        <div className="text-xs text-slate-500">
                          {[entity.ent_distrito, entity.ent_provincia].filter(Boolean).join(', ') || 'Sin ubicación'}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <DialogFooter className="sm:justify-end">
                <button
                  type="button"
                  onClick={handleCloseChildModal}
                  className="inline-flex items-center justify-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100"
                >
                  Cerrar
                </button>
                <button
                  type="button"
                  disabled={updatingEntity || !selectedEntityResult}
                  onClick={async () => {
                    const saved = await handleAssignEntity();
                    if (saved) {
                      setActiveChildModal(null);
                    }
                  }}
                  className={PRIMARY_BUTTON}
                >
                  {updatingEntity ? 'Asociando…' : 'Guardar cambios'}
                </button>
              </DialogFooter>
            </div>
          </div>
        </>
      );
    }

    return null;
  };

  const renderFamilyPrompt = () => (
    <section className={`${CARD_CONTAINER} px-6 py-6`}>
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-start gap-4">
          <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
            <MessageCircle className="h-6 w-6" />
          </span>
          <div className="space-y-2">
            <h2 className="text-xl font-semibold text-slate-900">¿Tienes hijos o menores a tu cargo?</h2>
            <p className="text-sm text-slate-600">
              Activa la gestión familiar para registrar sus datos clínicos y seguir su crecimiento paso a paso. Puedes cambiar esta opción cuando lo necesites.
            </p>
          </div>
        </div>
        <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
          <button
            type="button"
            onClick={() => handleSelectFlow('yes')}
            className={`${PRIMARY_BUTTON} flex-1 sm:flex-none ${childFlow === 'yes'
              ? 'ring-2 ring-offset-2 ring-offset-white ring-primary'
              : ''
              }`}
          >
            ✨ Sí, quiero registrarlos
          </button>
          <button
            type="button"
            onClick={() => handleSelectFlow('no')}
            className={`${PRIMARY_BUTTON} flex-1 sm:flex-none ${childFlow === 'no'
              ? 'ring-2 ring-offset-2 ring-offset-white ring-primary'
              : ''
              }`}
          >
            👤 No tengo hijos
          </button>
        </div>
      </div>
    </section>
  );

  const renderChildrenSection = () => {
    if (childFlow === 'no') {
      return (
        <section className={`${CARD_CONTAINER} p-6`}>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-slate-900">Sin menores registrados</h3>
              <p className="max-w-2xl text-sm text-slate-600">
                Cuando quieras comenzar el seguimiento de tus hijos o menores a cargo, activa la gestión familiar y regístralos aquí mismo.
              </p>
            </div>
            <button
              type="button"
              onClick={() => handleSelectFlow('yes')}
              className={`${PRIMARY_BUTTON} w-full md:w-auto`}
            >
              <Sparkles className="h-4 w-4" /> Registrar hijos ahora
            </button>
          </div>
        </section>
      );
    }

    if (childFlow !== 'yes') {
      return (
        <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-6 text-center text-sm text-slate-600">
          Selecciona una de las opciones anteriores para habilitar la gestión de niños.
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <div className={`${CARD_CONTAINER} p-4`}>
          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="space-y-1">
              <h3 className="text-lg font-semibold text-slate-900">Mis niños registrados</h3>
              <p className="text-sm text-slate-600">Selecciona un niño para ver y actualizar su información clínica.</p>
            </div>
            <button
              type="button"
              onClick={() => handleSelectFlow('yes')}
              className={`${PRIMARY_BUTTON} w-full md:w-auto`}
            >
              <PlusCircle className="h-4 w-4" /> Registrar nuevo niño
            </button>
          </div>
        </div>

        <div className={`${CARD_CONTAINER} p-4`}>
          {children.length === 0 && !isCreateChildModalOpen ? (
            <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-600">
              No has registrado niños todavía.
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {children.map((child) => {
                const info = child.nino;
                const latestMeasurement = child.antropometrias?.[0] ?? null;
                const isActive = selectedChildId === info.nin_id;
                const childName = info.nin_nombres?.trim() || 'Sin nombre asignado';
                const ageLabel = describeAge(info.nin_fecha_nac);
                const statusClasses = child.ultimo_estado_nutricional
                  ? child.ultimo_estado_nutricional.risk_level === 'ALTO'
                    ? 'bg-red-100 text-red-700'
                    : child.ultimo_estado_nutricional.risk_level === 'MODERADO'
                      ? 'bg-amber-100 text-amber-700'
                      : 'bg-emerald-100 text-emerald-700'
                  : '';
                const entityName = info.ent_nombre || info.ent_codigo || null;
                const entityLocation = [
                  info.ent_distrito,
                  info.ent_provincia,
                  info.ent_departamento,
                ]
                  .filter(Boolean)
                  .join(', ');
                const formattedMeasurementDate = latestMeasurement?.ant_fecha
                  ? formatDate(latestMeasurement.ant_fecha)
                  : null;
                return (
                  <div
                    key={info.nin_id}
                    role="button"
                    tabIndex={0}
                    onClick={() => handleSelectChild(info.nin_id)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        handleSelectChild(info.nin_id);
                      }
                    }}
                    className={`group w-full rounded-2xl border px-4 py-4 text-left transition-shadow ${isActive
                      ? 'border-primary bg-primary/10 shadow-md'
                      : 'border-gray-200 bg-white hover:border-primary/60 hover:shadow'
                      } cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary/30`}
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-stretch md:justify-between">
                      <div className="flex flex-1 items-start gap-3 text-left">
                        <span
                          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${isActive ? 'bg-primary text-white' : 'bg-primary/10 text-primary'
                            }`}
                        >
                          {getInitials(childName)}
                        </span>
                        <div className="flex-1 space-y-3">
                          <div className="relative flex flex-col gap-3">
                            <div className="flex flex-col gap-2 pr-24">
                              <div className="flex flex-wrap items-center gap-2">
                                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">Nombre:</span>
                                <span className={`text-lg font-semibold leading-tight ${isActive ? 'text-primary' : 'text-slate-900'}`}>
                                  {childName}
                                </span>
                              </div>
                              {child.ultimo_estado_nutricional && (
                                <span className={`inline-block w-fit rounded-full px-3 py-1 text-[11px] font-semibold ${statusClasses}`}>
                                  {child.ultimo_estado_nutricional.classification}
                                </span>
                              )}
                            </div>

                            <div className="absolute right-0 top-0 flex items-center gap-2">
                              <button
                                type="button"
                                onClick={(event) => {
                                  event.stopPropagation();
                                  openEditChildModal(info);
                                }}
                                className="inline-flex h-9 items-center justify-center rounded-lg bg-blue-500 px-4 text-sm text-white shadow-sm transition hover:bg-blue-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-300"
                                aria-label={`Editar ${childName}`}
                              >
                                ✏️
                              </button>
                              <button
                                type="button"
                                onClick={(event) => {
                                  event.stopPropagation();
                                  handleDeleteChild(info.nin_id, childName);
                                }}
                                className="inline-flex h-9 items-center justify-center rounded-lg px-4 text-sm text-white shadow-sm transition hover:bg-red-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-300"
                                style={{ backgroundColor: '#dc2626' }}
                                aria-label={`Eliminar ${childName}`}
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </div>

                          <div className="space-y-1 text-xs text-slate-500 sm:text-sm">
                            <div>
                              <span className="font-semibold text-slate-600">Edad:</span>
                              <span className="ml-1 text-slate-600">{ageLabel}</span>
                            </div>
                            <div>
                              <span className="font-semibold text-slate-600">Nacimiento:</span>
                              <span className="ml-1 text-slate-600">{formatDate(info.nin_fecha_nac)}</span>
                            </div>
                            <div>
                              <span className="font-semibold text-slate-600">Último registro:</span>
                              {latestMeasurement ? (
                                <span className="ml-1 text-slate-600">
                                  {latestMeasurement.ant_peso_kg} kg · {latestMeasurement.ant_talla_cm} cm
                                  {formattedMeasurementDate && formattedMeasurementDate !== '—' && (
                                    <span className="text-[11px] text-slate-400"> ({formattedMeasurementDate})</span>
                                  )}
                                </span>
                              ) : (
                                <span className="ml-1 italic text-slate-400">Sin mediciones</span>
                              )}
                            </div>
                            <div>
                              <span className="font-semibold text-slate-600">Entidad:</span>
                              {entityName ? (
                                <span className="ml-1 text-slate-600">{entityName}</span>
                              ) : (
                                <span className="ml-1 italic text-slate-400">No asociada</span>
                              )}
                              {entityName && entityLocation && (
                                <span className="block text-[11px] text-slate-400">{entityLocation}</span>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="grid w-full max-w-[240px] grid-cols-2 gap-2 self-center md:w-56">
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            handleOpenChildModal('analysis', info.nin_id);
                          }}
                          className="col-span-1 inline-flex items-center justify-center gap-1 rounded-md px-3 py-2 text-xs font-semibold text-white shadow-sm transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-400"
                          style={{ backgroundColor: '#047857' }}
                        >
                          <BarChart2 className="h-3.5 w-3.5" /> Análisis
                        </button>
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            handleOpenChildModal('measure', info.nin_id);
                          }}
                          className="col-span-1 inline-flex items-center justify-center gap-1 rounded-md px-3 py-2 text-xs font-semibold text-white shadow-sm transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gray-600"
                          style={{ backgroundColor: '#000000' }}
                        >
                          <HeartPulse className="h-3.5 w-3.5" /> Medidas
                        </button>
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            handleOpenChildModal('allergies', info.nin_id);
                          }}
                          className="col-span-1 inline-flex items-center justify-center gap-1 rounded-md bg-orange-500 px-3 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-orange-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-orange-400"
                        >
                          <Pill className="h-3.5 w-3.5" /> Alergias
                        </button>
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            handleOpenChildModal('entity', info.nin_id);
                          }}
                          className="col-span-1 inline-flex items-center justify-center gap-1 rounded-md bg-blue-500 px-3 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-blue-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-400"
                        >
                          <Building2 className="h-3.5 w-3.5" /> Entidad
                        </button>
                      </div>
                    </div>
                    <div className="mt-3 flex flex-col gap-1 text-[11px] text-slate-500 sm:flex-row sm:items-center sm:justify-between">
                      <span><span className="font-semibold text-slate-600">Actualizado:</span> {formatDate(info.actualizado_en)}</span>
                      <span className="sm:text-right"><span className="font-semibold text-slate-600">Registrado:</span> {formatDate(info.creado_en)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    );
  };
  const renderPersonalSection = () => (
    <section className={`${CARD_CONTAINER} p-6`}>
      <div className="mb-4 space-y-1">
        <h2 className="text-lg font-semibold text-slate-900">Tus datos clínicos</h2>
        <p className="text-sm text-slate-600">Registra tus propias medidas y obtén recomendaciones personalizadas.</p>
      </div>

      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="flex bg-white">
            {CLINICAL_SECTIONS.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`flex-1 border-b-2 px-6 py-4 text-sm font-medium transition-colors duration-200 ${activeSection === section.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-slate-500 hover:border-primary hover:text-primary'
                  }`}
              >
                <span className="mr-2 text-xl">{section.icon}</span>
                <span>{section.title}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="border-b border-gray-200 bg-gray-50 p-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{CLINICAL_SECTIONS.find(s => s.id === activeSection)?.icon}</span>
            <div>
              <h2 className="text-lg font-medium text-slate-900">{CLINICAL_SECTIONS.find(s => s.id === activeSection)?.title}</h2>
              <p className="text-sm text-slate-600">{CLINICAL_SECTIONS.find(s => s.id === activeSection)?.description}</p>
            </div>
          </div>
        </div>

        <div className="p-6">
          {activeSection === 'anthropometry' ? <AnthropometryManagement /> : <AllergiesAndEntities />}
        </div>
      </div>
    </section>
  );

  return (
    <>
      <div className="space-y-6">
        {renderFamilyPrompt()}
        {renderChildrenSection()}
        {childFlow === 'no' && renderPersonalSection()}
      </div>

      <Dialog open={Boolean(activeChildModal)} onOpenChange={(open) => {
        if (!open) {
          handleCloseChildModal();
        }
      }}>
        <DialogContent className="w-full max-w-2xl">
          {renderChildModalContent()}
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(editingChild)} onOpenChange={(open) => {
        if (!open) {
          setEditingChild(null);
          setEditError(null);
        }
      }}>
        <DialogContent className="w-full max-w-[480px] p-0 overflow-hidden rounded-2xl">
          <form onSubmit={handleEditChildSubmit} className="space-y-4 p-6">
            <DialogHeader className="pb-2 text-left">
              <DialogTitle className="text-lg font-semibold text-emerald-900">Editar información del niño</DialogTitle>
              <DialogDescription className="text-sm text-slate-600">
                Ajusta el nombre o la fecha de nacimiento para corregir la edad.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-700" htmlFor="edit-child-name">Nombre</label>
              <input
                id="edit-child-name"
                type="text"
                value={editingChild?.name ?? ''}
                onChange={(event) =>
                  setEditingChild((prev) => prev ? { ...prev, name: event.target.value } : prev)
                }
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
                required
              />
            </div>

            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-700" htmlFor="edit-child-date">Fecha de nacimiento</label>
              <input
                id="edit-child-date"
                type="date"
                value={editingChild?.birthDate ?? ''}
                onChange={(event) =>
                  setEditingChild((prev) => prev ? { ...prev, birthDate: event.target.value } : prev)
                }
                className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
              <p className="text-xs text-slate-500">Deja vacío si no deseas modificar la fecha actual.</p>
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
                className="rounded-md border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-400"
                disabled={updateNino.loading}
              >
                {updateNino.loading ? 'Guardando…' : 'Guardar cambios'}
              </button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={isFlowConfirmOpen} onOpenChange={setIsFlowConfirmOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader className="text-left">
            <DialogTitle className="text-lg font-semibold text-slate-900">Gestionar niños</DialogTitle>
            <DialogDescription className="text-slate-600">
              {children.length > 0
                ? 'Registra un nuevo niño para llevar control de su información clínica.'
                : 'Aún no tienes niños registrados. Comienza agregando su información clínica para activar la gestión familiar.'}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="sm:justify-end">
            <button
              type="button"
              onClick={() => setIsFlowConfirmOpen(false)}
              className="inline-flex items-center justify-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-300"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleStartChildRegistration}
              className={PRIMARY_BUTTON}
            >
              Registrar niño
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isCreateChildModalOpen} onOpenChange={setIsCreateChildModalOpen}>
        <DialogContent className="w-full sm:w-[88vw] md:w-[68vw] lg:w-[56vw] max-w-[920px] my-20 max-h-[78vh] overflow-y-auto border-none p-0 rounded-3xl">
          <div className="flex flex-col gap-5 p-6">
            <DialogHeader className="text-left">
              <DialogTitle className="text-xl font-semibold text-slate-900">Registrar nuevo niño</DialogTitle>
            </DialogHeader>
            <CreateChildForm
              onSuccess={(childId) => {
                handleChildCreated(childId);
              }}
              onCancel={() => setIsCreateChildModalOpen(false)}
            />
          </div>
        </DialogContent>
      </Dialog>

    </>
  );
}
