import { useState, useEffect } from 'react';
import { X, TrendingUp, AlertTriangle, Brain, Calendar } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { toast } from 'sonner';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { apiService } from '../../services/api';

interface Child {
  nin_id: number;
  nin_nombres: string;
  nin_apellidos: string;
}

interface PrediccionModalProps {
  open: boolean;
  onClose: () => void;
  child: Child;
}

interface Prediccion {
  clasificacion: string;
  probabilidad: number;
  score_riesgo: number;
  prob_normal: number;
  prob_riesgo: number;
  prob_moderado: number;
  prob_severo: number;
  probabilidades_por_clase?: Record<string, number>;
  features_importantes?: Array<[string, number]>;
  creado_en?: string;
  pml_id?: number;
  guardado?: boolean;
}

export function PrediccionModal({ open, onClose, child }: PrediccionModalProps) {
  const [mesesProyeccion, setMesesProyeccion] = useState(1);
  const [prediccion, setPrediccion] = useState<Prediccion | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingUltima, setLoadingUltima] = useState(false);

  // Cargar última predicción al abrir el modal
  useEffect(() => {
    if (open) {
      cargarUltimaPrediccion();
    }
  }, [open]);

  const cargarUltimaPrediccion = async () => {
    try {
      setLoadingUltima(true);
      const response = await apiService.obtenerUltimaPrediccion(child.nin_id);
      if (response.success && response.data) {
        setPrediccion(response.data);
      }
    } catch (error) {
      console.log('No hay predicciones previas');
    } finally {
      setLoadingUltima(false);
    }
  };

  const handleGenerarPrediccion = async () => {
    try {
      setLoading(true);

      const response = await apiService.generarPrediccion(child.nin_id, mesesProyeccion);

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Error al generar predicción');
      }

      setPrediccion(response.data);
      toast.success('Predicción generada exitosamente');

    } catch (error: any) {
      console.error('Error generando predicción:', error);
      toast.error(error.response?.data?.detail || 'Error al generar predicción');
    } finally {
      setLoading(false);
    }
  };

  const getClasificacionColor = (clasificacion: string) => {
    const lower = clasificacion.toLowerCase();
    if (lower.includes('severa') || lower.includes('obesidad')) return 'bg-red-500';
    if (lower.includes('moderada') || lower.includes('sobrepeso')) return 'bg-orange-500';
    if (lower.includes('riesgo')) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getRiesgoNivel = (score: number) => {
    if (score < 0.3) return { nivel: 'BAJO', color: 'text-green-600', bgColor: 'bg-green-100' };
    if (score < 0.6) return { nivel: 'MODERADO', color: 'text-yellow-600', bgColor: 'bg-yellow-100' };
    return { nivel: 'ALTO', color: 'text-red-600', bgColor: 'bg-red-100' };
  };

  const formatFeatureName = (name: string) => {
    const mapping: Record<string, string> = {
      'age_months': 'Edad (meses)',
      'sex_numeric': 'Sexo',
      'BMI': 'IMC',
      'weight_kg': 'Peso (kg)',
      'height_cm': 'Talla (cm)',
      'bmi_velocity': 'Vel. IMC',
      'weight_velocity': 'Vel. Peso',
      'height_velocity': 'Vel. Talla',
      'adherence_score': 'Adherencia',
      'allergy_count': 'Alergias',
      'altitude_m': 'Altitud'
    };
    return mapping[name] || name;
  };

  // Preparar datos para gráfico
  const chartData = prediccion ? [
    { name: 'Normal', value: prediccion.prob_normal * 100, color: '#22c55e' },
    { name: 'Riesgo', value: prediccion.prob_riesgo * 100, color: '#eab308' },
    { name: 'Moderado', value: prediccion.prob_moderado * 100, color: '#f97316' },
    { name: 'Severo', value: prediccion.prob_severo * 100, color: '#ef4444' }
  ] : [];

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto" style={{ maxWidth: '70vw', width: '850px' }}>
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span className="flex items-center space-x-2">
              <Brain className="text-primary" />
              <span>Predicción Nutricional - {child.nin_nombres}</span>
            </span>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X size={20} />
            </Button>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Selector de meses */}
          <div className="space-y-3">
            <Label className="flex items-center space-x-2">
              <Calendar size={16} />
              <span>Proyectar a:</span>
            </Label>
            <div className="flex space-x-2">
              {[1, 2, 3, 4, 5, 6].map((mes) => (
                <Button
                  key={mes}
                  variant={mesesProyeccion === mes ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setMesesProyeccion(mes)}
                  disabled={loading}
                >
                  {mes} {mes === 1 ? 'mes' : 'meses'}
                </Button>
              ))}
            </div>
          </div>

          {/* Botón generar */}
          <Button
            onClick={handleGenerarPrediccion}
            disabled={loading}
            className="w-full"
            size="lg"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generando predicción...
              </>
            ) : (
              <>
                <TrendingUp size={20} className="mr-2" />
                Generar Predicción
              </>
            )}
          </Button>

          {/* Resultados */}
          {prediccion && (
            <div className="space-y-6 pt-4 border-t">
              {/* Clasificación principal */}
              <div style={{ backgroundColor: 'rgba(0,0,0,0.05)', borderRadius: '8px', padding: '24px' }} className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Clasificación Predicha</p>
                    <Badge className={`${getClasificacionColor(prediccion.clasificacion)} text-white text-lg px-4 py-2`}>
                      {prediccion.clasificacion.replace(/_/g, ' ')}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground mb-2">Confianza</p>
                    <p className="text-3xl font-bold">{(prediccion.probabilidad * 100).toFixed(1)}%</p>
                  </div>
                </div>

                {/* Score de riesgo */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <Label className="flex items-center space-x-2">
                      <AlertTriangle size={16} />
                      <span>Score de Riesgo</span>
                    </Label>
                    <Badge className={`${getRiesgoNivel(prediccion.score_riesgo).bgColor} ${getRiesgoNivel(prediccion.score_riesgo).color}`}>
                      {getRiesgoNivel(prediccion.score_riesgo).nivel}
                    </Badge>
                  </div>
                  <Progress value={prediccion.score_riesgo * 100} className="h-3" />
                  <p className="text-sm text-muted-foreground mt-1">
                    {(prediccion.score_riesgo * 100).toFixed(1)}% de probabilidad de riesgo
                  </p>
                </div>
              </div>

              {/* Gráfico de probabilidades */}
              <div className="space-y-3">
                <Label>Distribución de Probabilidades</Label>
                <div style={{ height: '300px', backgroundColor: 'rgba(0,0,0,0.03)', borderRadius: '8px', padding: '16px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip formatter={(value: number) => `${value.toFixed(1)}%`} />
                      <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Features importantes */}
              {prediccion.features_importantes && prediccion.features_importantes.length > 0 && (
                <div className="space-y-3">
                  <Label>Factores Más Influyentes</Label>
                  <div className="space-y-2">
                    {prediccion.features_importantes.slice(0, 5).map(([name, importance], index) => {
                      const maxImportance = Math.max(...(prediccion.features_importantes?.map(f => f[1]) || [1]));
                      return (
                      <div key={name} className="flex items-center space-x-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <p className="font-medium">{formatFeatureName(name)}</p>
                          <Progress value={(importance / maxImportance) * 100} className="h-2 mt-1" />
                        </div>
                        <span className="text-sm text-muted-foreground">{importance.toFixed(2)}</span>
                      </div>
                    );
                    })}
                  </div>
                </div>
              )}

              {/* Recomendaciones */}
              <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '16px' }}>
                <h4 className="font-medium mb-2 flex items-center space-x-2">
                  <AlertTriangle className="text-blue-600" size={16} />
                  <span>Recomendaciones</span>
                </h4>
                <ul className="text-sm space-y-1 text-blue-900">
                  {prediccion.score_riesgo > 0.6 && (
                    <>
                      <li>• Programar consulta con nutricionista</li>
                      <li>• Monitorear adherencia al plan nutricional</li>
                      <li>• Realizar seguimiento antropométrico mensual</li>
                    </>
                  )}
                  {prediccion.score_riesgo > 0.3 && prediccion.score_riesgo <= 0.6 && (
                    <>
                      <li>• Reforzar adherencia al plan nutricional</li>
                      <li>• Seguimiento antropométrico cada 2 meses</li>
                      <li>• Evaluar posibles ajustes al plan</li>
                    </>
                  )}
                  {prediccion.score_riesgo <= 0.3 && (
                    <>
                      <li>• Mantener plan nutricional actual</li>
                      <li>• Seguimiento antropométrico trimestral</li>
                      <li>• Continuar con buenos hábitos alimenticios</li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          )}
        </div>

        {/* Acciones */}
        <div className="flex justify-between items-center pt-4 border-t">
          <div className="text-sm text-muted-foreground">
            {loadingUltima && "Cargando última predicción..."}
            {prediccion && !loading && (
              <span>
                Última predicción: {new Date(prediccion.creado_en || Date.now()).toLocaleDateString()}
              </span>
            )}
          </div>
          <div className="flex space-x-3">
            <Button variant="outline" onClick={onClose}>
              Cerrar
            </Button>
            {prediccion && (
              <Button onClick={() => window.print()}>
                Imprimir Reporte
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
