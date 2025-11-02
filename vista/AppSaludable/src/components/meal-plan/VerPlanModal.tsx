import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { useToast } from '../ui/use-toast';
import { Loader2, Calendar, Sparkles, RefreshCw, FileDown } from 'lucide-react';
import {
  obtenerDetalleMenu,
  generarPlanCompletoConLLM,
  obtenerDetalleReceta,
  descargarPlanPdf
} from '../../services/mealPlanApi';

interface VerPlanModalProps {
  open: boolean;
  onClose: (recargar?: boolean) => void;
  ninId: number;
  ninNombre: string;
  menId?: number;
}

interface Comida {
  rec_id: number;
  rec_nombre: string;
  mei_kcal: number;
  ingredientes?: any[];
}

interface Dia {
  dia_idx: number;
  dia_nombre: string;
  fecha: string;
  desayuno?: Comida;
  almuerzo?: Comida;
  cena?: Comida;
  total_dia: number;
}

export const VerPlanModal: React.FC<VerPlanModalProps> = ({
  open,
  onClose,
  ninId,
  ninNombre,
  menId,
}) => {
  const { toast } = useToast();
  const [cargando, setCargando] = useState(false);
  const [generando, setGenerando] = useState(false);
  const [plan, setPlan] = useState<any>(null);
  const [progreso, setProgreso] = useState<string[]>([]);
  const [planGenerado, setPlanGenerado] = useState(false);

  useEffect(() => {
    if (open && menId) {
      cargarPlan();
      setPlanGenerado(false);
      setDiaSeleccionado(0); // Reset día seleccionado al abrir
    }
  }, [open, menId, ninId]); // Agregar ninId como dependencia

  // Resetear estado cuando cambia el niño
  useEffect(() => {
    if (open) {
      setPlan(null); // Limpiar plan anterior
      setDiaSeleccionado(0); // Resetear día
    }
  }, [ninId, open]);

  const cargarPlan = async () => {
    if (!menId) return;

    setCargando(true);
    try {
      const data = await obtenerDetalleMenu(menId);
      if (data.dias && Array.isArray(data.dias)) {
        data.dias = data.dias.map((dia: any) => {
          const transformed: any = {
            dia_idx: dia.dia_idx,
            dia_nombre: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][dia.dia_idx] || `Día ${dia.dia_idx + 1}`,
            fecha: data.men_inicio,
            total_dia: 0
          };

          const fechaInicio = new Date(data.men_inicio);
          fechaInicio.setDate(fechaInicio.getDate() + dia.dia_idx);
          transformed.fecha = fechaInicio.toISOString().split('T')[0];

          if (dia.items && Array.isArray(dia.items)) {
            dia.items.forEach((item: any) => {
              const comida = {
                rec_id: item.rec_id,
                rec_nombre: item.rec_nombre,
                mei_kcal: item.mei_kcal,
                rec_instrucciones: item.rec_instrucciones || '',
                ingredientes: []
              };

              transformed.total_dia += item.mei_kcal;

              if (item.mei_comida === 'DESAYUNO') {
                transformed.desayuno = comida;
              } else if (item.mei_comida === 'ALMUERZO') {
                transformed.almuerzo = comida;
              } else if (item.mei_comida === 'CENA') {
                transformed.cena = comida;
              }
            });
          }

          return transformed;
        });
      }

      setPlan(data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo cargar el plan de comidas',
        variant: 'destructive',
      });
    } finally {
      setCargando(false);
    }
  };

  const handleGenerarNuevo = async () => {
    setGenerando(true);
    setProgreso([]);

    try {
      const hoy = new Date();
      const diaSemana = hoy.getDay();
      const diasHastaLunes = diaSemana === 0 ? 1 : diaSemana === 1 ? 0 : 8 - diaSemana;
      const proximoLunes = new Date(hoy);
      proximoLunes.setDate(hoy.getDate() + diasHastaLunes);
      const fechaInicio = proximoLunes.toISOString().split('T')[0];

      setProgreso((prev) => [...prev, '🔍 Obteniendo perfil nutricional...']);
      await new Promise((resolve) => setTimeout(resolve, 500));

      setProgreso((prev) => [...prev, '🍽️ Consultando preferencias...']);
      await new Promise((resolve) => setTimeout(resolve, 500));

      setProgreso((prev) => [...prev, '⚠️ Verificando alergias...']);
      await new Promise((resolve) => setTimeout(resolve, 500));

      setProgreso((prev) => [...prev, '🤖 Generando plan con IA...']);

      const resultado = await generarPlanCompletoConLLM(ninId, fechaInicio);

      setProgreso((prev) => [...prev, '✅ Plan generado exitosamente']);

      // Recargar el plan inmediatamente
      if (resultado.men_id) {
        setProgreso((prev) => [...prev, '📥 Cargando plan generado...']);
        const data = await obtenerDetalleMenu(resultado.men_id);

        // Transformar datos igual que en cargarPlan
        if (data.dias && Array.isArray(data.dias)) {
          data.dias = data.dias.map((dia: any) => {
            const transformed: any = {
              dia_idx: dia.dia_idx,
              dia_nombre: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'][dia.dia_idx] || `Día ${dia.dia_idx + 1}`,
              fecha: data.men_inicio,
              total_dia: 0
            };

            const fechaInicio = new Date(data.men_inicio);
            fechaInicio.setDate(fechaInicio.getDate() + dia.dia_idx);
            transformed.fecha = fechaInicio.toISOString().split('T')[0];

            if (dia.items && Array.isArray(dia.items)) {
              dia.items.forEach((item: any) => {
                const comida = {
                  rec_id: item.rec_id,
                  rec_nombre: item.rec_nombre,
                  mei_kcal: item.mei_kcal,
                  rec_instrucciones: item.rec_instrucciones || '',
                  ingredientes: []
                };

                transformed.total_dia += item.mei_kcal;

                if (item.mei_comida === 'DESAYUNO') {
                  transformed.desayuno = comida;
                } else if (item.mei_comida === 'ALMUERZO') {
                  transformed.almuerzo = comida;
                } else if (item.mei_comida === 'CENA') {
                  transformed.cena = comida;
                }
              });
            }

            return transformed;
          });
        }

        setPlan(data);
        setPlanGenerado(true);
        setDiaSeleccionado(0); // Resetear a lunes
        setProgreso((prev) => [...prev, '🎉 Plan listo para visualizar']);

        console.log('✅ Plan generado y cargado:', data);
      }

      toast({
        title: 'Plan generado',
        description: `Nuevo plan de comidas para ${ninNombre}`,
      });
    } catch (error: any) {
      setProgreso((prev) => [...prev, `❌ Error: ${error.message}`]);
      toast({
        title: 'Error',
        description: error.message || 'No se pudo generar el plan',
        variant: 'destructive',
      });
    } finally {
      setGenerando(false);
    }
  };

  const [diaSeleccionado, setDiaSeleccionado] = useState(0);
  const [recetaDetalle, setRecetaDetalle] = useState<any | null>(null);
  const [cargandoReceta, setCargandoReceta] = useState(false);
  const [descargandoPdf, setDescargandoPdf] = useState(false);

  const cargarDetalleReceta = async (comida: Comida) => {
    setCargandoReceta(true);
    try {
      const detalle = await obtenerDetalleReceta(comida.rec_id);
      setRecetaDetalle({
        ...comida,
        ...detalle
      });
    } catch (error: any) {
      toast({
        title: 'Error',
        description: 'No se pudo cargar el detalle de la receta',
        variant: 'destructive',
      });
    } finally {
      setCargandoReceta(false);
    }
  };

  const descargarPlanPdfHandler = async () => {
    if (!menId || !plan) return;

    setDescargandoPdf(true);
    try {
      // Usar el servicio de API que maneja automáticamente la autenticación
      const blob = await descargarPlanPdf(ninId, menId);

      // Crear URL temporal y descargar
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `plan_comidas_${ninNombre.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      toast({
        title: '✅ PDF descargado',
        description: 'El plan de comidas se ha descargado correctamente',
      });
    } catch (error: any) {
      console.error('❌ Error descargando PDF:', error);
      toast({
        title: 'Error',
        description: error.message || 'No se pudo descargar el PDF',
        variant: 'destructive',
      });
    } finally {
      setDescargandoPdf(false);
    }
  };

  const ComidaRow: React.FC<{ comida?: Comida; tipo: string; icono: string }> = ({ comida, tipo, icono }) => {
    if (!comida) {
      return (
        <div className="bg-gray-50 rounded-lg p-4 border border-dashed border-gray-300">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">{icono}</span>
              <div>
                <h3 className="font-semibold text-gray-400">{tipo}</h3>
                <p className="text-sm text-gray-400">Sin receta asignada</p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-lg p-4 border border-gray-200 hover:shadow-lg transition-shadow">
        <div className="flex items-start justify-between gap-4">
          {/* Info principal */}
          <div className="flex items-start gap-3 flex-1">
            <span className="text-3xl">{icono}</span>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h3 className="font-semibold text-gray-900">{tipo}</h3>
                <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                  {comida.ingredientes?.length || 0} ingredientes
                </span>
              </div>
              <h4 className="text-lg font-bold text-gray-800 mb-2">{comida.rec_nombre}</h4>

              {/* Info nutricional */}
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <span className="text-orange-600 font-bold text-xl">{comida.mei_kcal}</span>
                  <span className="text-gray-600">kcal</span>
                </div>
                {comida.ingredientes && comida.ingredientes.length > 0 && (
                  <div className="text-gray-600">
                    {comida.ingredientes.slice(0, 3).map((ing: any, idx: number) => (
                      <span key={idx}>
                        {ing.ali_nombre}
                        {idx < Math.min(2, comida.ingredientes!.length - 1) ? ', ' : ''}
                      </span>
                    ))}
                    {comida.ingredientes.length > 3 && ` +${comida.ingredientes.length - 3} más`}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Botón ver más */}
          <Button
            size="sm"
            variant="outline"
            onClick={() => setRecetaDetalle(comida)}
            className="shrink-0"
          >
            Ver Receta
          </Button>
        </div>
      </div>
    );
  };

  // Debug: ver qué datos llegan
  useEffect(() => {
    if (plan) {
      console.log('📊 Plan cargado:', plan);
      console.log('📅 Días:', plan.dias);
    }
  }, [plan]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-green-600" />
            Plan de Comidas - {ninNombre}
          </DialogTitle>
        </DialogHeader>

        {cargando ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : generando ? (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">Generando plan...</h3>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {progreso.map((mensaje, index) => (
                  <div key={index} className="flex items-start gap-2 text-sm text-blue-800">
                    {mensaje.startsWith('✅') ? (
                      <span className="text-green-600">✅</span>
                    ) : mensaje.startsWith('❌') ? (
                      <span className="text-red-600">❌</span>
                    ) : (
                      <Loader2 className="w-4 h-4 animate-spin mt-0.5" />
                    )}
                    <span>{mensaje.replace(/^[🔍🍽️⚠️🤖✅❌]\s*/, '')}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : plan ? (
          <div className="space-y-4">
            {/* Header del plan */}
            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-3 border border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-600">Período</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {new Date(plan.men_inicio).toLocaleDateString('es-PE')} - {new Date(plan.men_fin).toLocaleDateString('es-PE')}
                  </p>
                </div>
                {plan.men_kcal_total && (
                  <div className="text-right">
                    <p className="text-xs text-gray-600">Total Semanal</p>
                    <p className="text-lg font-bold text-green-600">{plan.men_kcal_total} kcal</p>
                  </div>
                )}
              </div>
            </div>

            {/* Botones de días */}
            {plan.dias && plan.dias.length > 0 && (
              <div className="flex gap-2 flex-wrap justify-center">
                {plan.dias.map((dia: Dia) => (
                  <Button
                    key={dia.dia_idx}
                    onClick={() => setDiaSeleccionado(dia.dia_idx)}
                    variant={diaSeleccionado === dia.dia_idx ? 'default' : 'outline'}
                    className={`${diaSeleccionado === dia.dia_idx
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : ''
                      }`}
                  >
                    {dia.dia_nombre}
                  </Button>
                ))}
              </div>
            )}

            {/* Comidas del día seleccionado */}
            {plan.dias && plan.dias.length > 0 ? (
              (() => {
                const diaActual = plan.dias[diaSeleccionado];
                if (!diaActual) return null;

                return (
                  <div className="space-y-4">
                    {/* Header del día */}
                    <div className="bg-gradient-to-r from-green-100 to-blue-100 rounded-lg p-2 border border-green-200">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-bold text-gray-900">{diaActual.dia_nombre}</h3>
                        <div className="text-right">
                          <p className="text-xs text-gray-600">Total</p>
                          <p className="text-lg font-bold text-green-600">{diaActual.total_dia} kcal</p>
                        </div>
                      </div>
                    </div>

                    {/* Grid de 3 comidas */}
                    <div className="grid grid-cols-3 gap-3">
                      {/* DESAYUNO */}
                      <div>
                        <h2 className="text-sm font-bold text-gray-700 mb-2 flex items-center gap-1">
                          <span>🌅</span>
                          Desayuno
                        </h2>
                        {diaActual.desayuno ? (
                          <div className="bg-white rounded-lg p-3 border border-gray-200 hover:shadow-md transition-shadow">
                            <h4 className="text-sm font-bold text-gray-900 mb-2 line-clamp-2">
                              {diaActual.desayuno.rec_nombre}
                            </h4>
                            <div className="flex items-center gap-1 mb-2">
                              <span className="text-orange-600 font-bold text-xl">{diaActual.desayuno.mei_kcal}</span>
                              <span className="text-gray-600 text-xs">kcal</span>
                            </div>
                            <Button
                              size="sm"
                              onClick={() => cargarDetalleReceta(diaActual.desayuno!)}
                              className="w-full bg-green-600 hover:bg-green-700 h-8 text-xs"
                              disabled={cargandoReceta}
                            >
                              Ver Receta
                            </Button>
                          </div>
                        ) : (
                          <div className="bg-gray-50 rounded-lg p-3 border border-dashed border-gray-300 text-center">
                            <p className="text-xs text-gray-500">Sin receta</p>
                          </div>
                        )}
                      </div>

                      {/* ALMUERZO */}
                      <div>
                        <h2 className="text-sm font-bold text-gray-700 mb-2 flex items-center gap-1">
                          <span>🍽️</span>
                          Almuerzo
                        </h2>
                        {diaActual.almuerzo ? (
                          <div className="bg-white rounded-lg p-3 border border-gray-200 hover:shadow-md transition-shadow">
                            <h4 className="text-sm font-bold text-gray-900 mb-2 line-clamp-2">
                              {diaActual.almuerzo.rec_nombre}
                            </h4>
                            <div className="flex items-center gap-1 mb-2">
                              <span className="text-orange-600 font-bold text-xl">{diaActual.almuerzo.mei_kcal}</span>
                              <span className="text-gray-600 text-xs">kcal</span>
                            </div>
                            <Button
                              size="sm"
                              onClick={() => cargarDetalleReceta(diaActual.almuerzo!)}
                              className="w-full bg-green-600 hover:bg-green-700 h-8 text-xs"
                              disabled={cargandoReceta}
                            >
                              Ver Receta
                            </Button>
                          </div>
                        ) : (
                          <div className="bg-gray-50 rounded-lg p-3 border border-dashed border-gray-300 text-center">
                            <p className="text-xs text-gray-500">Sin receta</p>
                          </div>
                        )}
                      </div>

                      {/* CENA */}
                      <div>
                        <h2 className="text-sm font-bold text-gray-700 mb-2 flex items-center gap-1">
                          <span>🌙</span>
                          Cena
                        </h2>
                        {diaActual.cena ? (
                          <div className="bg-white rounded-lg p-3 border border-gray-200 hover:shadow-md transition-shadow">
                            <h4 className="text-sm font-bold text-gray-900 mb-2 line-clamp-2">
                              {diaActual.cena.rec_nombre}
                            </h4>
                            <div className="flex items-center gap-1 mb-2">
                              <span className="text-orange-600 font-bold text-xl">{diaActual.cena.mei_kcal}</span>
                              <span className="text-gray-600 text-xs">kcal</span>
                            </div>
                            <Button
                              size="sm"
                              onClick={() => cargarDetalleReceta(diaActual.cena!)}
                              className="w-full bg-green-600 hover:bg-green-700 h-8 text-xs"
                              disabled={cargandoReceta}
                            >
                              Ver Receta
                            </Button>
                          </div>
                        ) : (
                          <div className="bg-gray-50 rounded-lg p-3 border border-dashed border-gray-300 text-center">
                            <p className="text-xs text-gray-500">Sin receta</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })()
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                <p>No hay días en el plan</p>
              </div>
            )}

            {/* Resumen */}
            {plan.resumen && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-900 mb-2">Resumen</h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Calorías promedio/día</p>
                    <p className="font-semibold text-gray-900">{plan.resumen.calorias_promedio_dia} kcal</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Preferencias respetadas</p>
                    <p className="font-semibold text-gray-900">
                      {plan.resumen.preferencias_respetadas}/{plan.resumen.preferencias_totales}
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Match</p>
                    <p className="font-semibold text-gray-900">{(plan.resumen.porcentaje_match * 100).toFixed(0)}%</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No hay plan de comidas
            </h3>
            <p className="text-gray-600 mb-4">
              Genera un plan personalizado para {ninNombre}
            </p>
            <Button
              onClick={handleGenerarNuevo}
              className="bg-green-600 hover:bg-green-700"
            >
              <Sparkles className="w-4 h-4 mr-2" />
              Generar Plan
            </Button>
          </div>
        )}

        {/* Botones footer */}
        <div className="flex justify-center items-center gap-4 pt-4 border-t">
          {plan && !generando && (
            <>
              <Button
                onClick={descargarPlanPdfHandler}
                disabled={descargandoPdf}
                style={{
                  backgroundColor: '#2563eb',
                  color: 'white',
                  borderColor: '#2563eb'
                }}
                className="hover:opacity-90"
              >
                {descargandoPdf ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <FileDown className="w-4 h-4 mr-2" />
                )}
                Descargar PDF
              </Button>
              <Button
                onClick={handleGenerarNuevo}
                style={{
                  backgroundColor: '#16a34a',
                  color: 'white',
                  borderColor: '#16a34a'
                }}
                className="hover:opacity-90"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Generar Nuevo
              </Button>
            </>
          )}
          <Button onClick={() => onClose(planGenerado)} variant="outline">
            Cerrar
          </Button>
        </div>
      </DialogContent>

      {/* Modal de detalle de receta */}
      {recetaDetalle && (
        <Dialog open={!!recetaDetalle} onOpenChange={() => setRecetaDetalle(null)}>
          <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-xl">{recetaDetalle.rec_nombre}</DialogTitle>
            </DialogHeader>

            <div className="space-y-4">
              {/* Info nutricional completa */}
              <div className="bg-gradient-to-r from-orange-50 to-red-50 rounded-lg p-4 border border-orange-200">
                <h3 className="font-semibold text-orange-900 mb-3">Información Nutricional</h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <p className="text-xs text-gray-600">Calorías</p>
                    <p className="text-2xl font-bold text-orange-600">
                      {recetaDetalle.nutrientes?.kcal || recetaDetalle.mei_kcal || 0}
                    </p>
                    <p className="text-xs text-gray-500">kcal</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-600">Proteínas</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {recetaDetalle.nutrientes?.proteina_g || 0}
                    </p>
                    <p className="text-xs text-gray-500">g</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-600">Carbohidratos</p>
                    <p className="text-2xl font-bold text-green-600">
                      {recetaDetalle.nutrientes?.carbohidratos_g || 0}
                    </p>
                    <p className="text-xs text-gray-500">g</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-600">Grasas</p>
                    <p className="text-2xl font-bold text-yellow-600">
                      {recetaDetalle.nutrientes?.grasa_g || 0}
                    </p>
                    <p className="text-xs text-gray-500">g</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-600">Fibra</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {recetaDetalle.nutrientes?.fibra_g || 0}
                    </p>
                    <p className="text-xs text-gray-500">g</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-600">Hierro</p>
                    <p className="text-2xl font-bold text-red-600">
                      {recetaDetalle.nutrientes?.hierro_mg || 0}
                    </p>
                    <p className="text-xs text-gray-500">mg</p>
                  </div>
                </div>
              </div>

              {/* Ingredientes */}
              {recetaDetalle.ingredientes && recetaDetalle.ingredientes.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <span>🥗</span>
                    Ingredientes ({recetaDetalle.ingredientes.length})
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-4 space-y-2 max-h-60 overflow-y-auto">
                    {recetaDetalle.ingredientes.map((ing: any, idx: number) => (
                      <div key={idx} className="flex items-center justify-between text-sm border-b border-gray-200 pb-2 last:border-0">
                        <span className="text-gray-900 font-medium">{ing.ali_nombre}</span>
                        <span className="text-gray-600">
                          {ing.cantidad} {ing.unidad}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Procedimiento */}
              {recetaDetalle.rec_instrucciones && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <span>👨‍🍳</span>
                    Procedimiento
                  </h3>
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <p className="text-sm text-gray-800 whitespace-pre-line">
                      {recetaDetalle.rec_instrucciones}
                    </p>
                  </div>
                </div>
              )}

              <div className="flex justify-end pt-4 border-t">
                <Button
                  onClick={() => setRecetaDetalle(null)}
                  className="bg-green-600 hover:bg-green-700"
                >
                  Cerrar
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </Dialog>
  );
};
