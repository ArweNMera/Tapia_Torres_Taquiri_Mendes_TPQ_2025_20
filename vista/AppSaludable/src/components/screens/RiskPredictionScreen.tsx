import { useState } from 'react';
import { AlertTriangle, TrendingUp, Heart, Shield, Activity, Brain, Target, Calendar } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import { Alert, AlertDescription } from '../ui/alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { motion } from 'motion/react';

interface RiskAssessment {
  id: string;
  type: 'malnutrition' | 'obesity' | 'deficiency';
  level: 'low' | 'medium' | 'high';
  percentage: number;
  description: string;
  recommendations: string[];
  timeframe: string;
}

interface NutritionalMetric {
  name: string;
  current: number;
  recommended: number;
  unit: string;
  status: 'optimal' | 'warning' | 'critical';
  trend: 'up' | 'down' | 'stable';
}

const riskAssessments: RiskAssessment[] = [
  {
    id: '1',
    type: 'malnutrition',
    level: 'low',
    percentage: 15,
    description: 'Riesgo bajo de desnutrición basado en el patrón alimentario actual',
    recommendations: [
      'Mantener la variedad actual de alimentos',
      'Incrementar ligeramente las porciones de proteína',
      'Continuar con el seguimiento mensual'
    ],
    timeframe: '3 meses'
  },
  {
    id: '2',
    type: 'deficiency',
    level: 'medium',
    percentage: 35,
    description: 'Riesgo moderado de deficiencia de hierro y vitamina D',
    recommendations: [
      'Incluir más alimentos ricos en hierro (carnes rojas, espinacas)',
      'Aumentar exposición solar diaria (15-20 min)',
      'Considerar suplementación bajo supervisión médica'
    ],
    timeframe: '6 semanas'
  }
];

const nutritionalMetrics: NutritionalMetric[] = [
  { name: 'Proteína', current: 45, recommended: 50, unit: 'g/día', status: 'warning', trend: 'up' },
  { name: 'Hierro', current: 8, recommended: 12, unit: 'mg/día', status: 'critical', trend: 'down' },
  { name: 'Calcio', current: 950, recommended: 1000, unit: 'mg/día', status: 'optimal', trend: 'stable' },
  { name: 'Vitamina D', current: 15, recommended: 25, unit: 'mcg/día', status: 'warning', trend: 'up' },
  { name: 'Fibra', current: 20, recommended: 25, unit: 'g/día', status: 'warning', trend: 'up' },
  { name: 'Vitamina C', current: 85, recommended: 75, unit: 'mg/día', status: 'optimal', trend: 'stable' }
];

const growthData = [
  { month: 'Ene', weight: 18.5, height: 95, recommended_weight: 19.0 },
  { month: 'Feb', weight: 18.8, height: 96, recommended_weight: 19.2 },
  { month: 'Mar', weight: 19.0, height: 97, recommended_weight: 19.4 },
  { month: 'Abr', weight: 19.2, height: 98, recommended_weight: 19.6 },
  { month: 'May', weight: 19.3, height: 99, recommended_weight: 19.8 },
  { month: 'Jun', weight: 19.4, height: 100, recommended_weight: 20.0 }
];

const comparisonData = [
  { category: 'Proteínas', value: 85, recommended: 100 },
  { category: 'Carbohidratos', value: 92, recommended: 100 },
  { category: 'Grasas', value: 78, recommended: 100 },
  { category: 'Vitaminas', value: 65, recommended: 100 },
  { category: 'Minerales', value: 70, recommended: 100 }
];

export function RiskPredictionScreen() {
  const [selectedPeriod, setSelectedPeriod] = useState<'1m' | '3m' | '6m'>('3m');
  const [activeTab, setActiveTab] = useState<'overview' | 'detailed' | 'comparison'>('overview');

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-success text-white';
      case 'medium': return 'bg-warning text-white';
      case 'high': return 'bg-destructive text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getRiskIcon = (type: string) => {
    switch (type) {
      case 'malnutrition': return <AlertTriangle size={20} />;
      case 'obesity': return <TrendingUp size={20} />;
      case 'deficiency': return <Activity size={20} />;
      default: return <Shield size={20} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'optimal': return 'text-success';
      case 'warning': return 'text-warning';
      case 'critical': return 'text-destructive';
      default: return 'text-muted-foreground';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      case 'stable': return '➡️';
      default: return '➡️';
    }
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Evaluación de Riesgos */}
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-6">
          <Brain className="text-primary" size={24} />
          <h3 className="text-lg font-semibold">Evaluación de Riesgos con IA</h3>
        </div>

        <div className="space-y-4">
          {riskAssessments.map((assessment) => (
            <motion.div
              key={assessment.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${getRiskColor(assessment.level)}`}>
                    {getRiskIcon(assessment.type)}
                  </div>
                  <div>
                    <h4 className="font-medium">
                      {assessment.type === 'malnutrition' ? 'Desnutrición' :
                       assessment.type === 'obesity' ? 'Obesidad' : 'Deficiencias Nutricionales'}
                    </h4>
                    <Badge className={`mt-1 ${getRiskColor(assessment.level)}`}>
                      Riesgo {assessment.level === 'low' ? 'Bajo' : 
                               assessment.level === 'medium' ? 'Moderado' : 'Alto'}: {assessment.percentage}%
                    </Badge>
                  </div>
                </div>
                <div className="text-right text-sm text-muted-foreground">
                  Plazo: {assessment.timeframe}
                </div>
              </div>

              <p className="text-sm text-muted-foreground mb-4">{assessment.description}</p>

              <div className="bg-muted rounded-lg p-3">
                <p className="font-medium text-sm mb-2">Recomendaciones:</p>
                <ul className="space-y-1">
                  {assessment.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm flex items-start">
                      <span className="text-primary mr-2">•</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Métricas Nutricionales Clave */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-6">Estado Nutricional Actual</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {nutritionalMetrics.map((metric, index) => (
            <motion.div
              key={metric.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 border rounded-lg"
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">{metric.name}</h4>
                <span className="text-lg">{getTrendIcon(metric.trend)}</span>
              </div>
              
              <div className="flex items-baseline space-x-2 mb-2">
                <span className={`text-lg font-bold ${getStatusColor(metric.status)}`}>
                  {metric.current}
                </span>
                <span className="text-sm text-muted-foreground">/ {metric.recommended} {metric.unit}</span>
              </div>

              <Progress 
                value={(metric.current / metric.recommended) * 100} 
                className="h-2"
              />
              
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>0</span>
                <span>{metric.recommended}</span>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Alertas y Recomendaciones Urgentes */}
      <div className="space-y-3">
        <Alert>
          <AlertTriangle size={16} />
          <AlertDescription>
            <strong>Atención:</strong> Los niveles de hierro están por debajo del rango recomendado. 
            Se sugiere incluir más alimentos ricos en hierro en la dieta diaria.
          </AlertDescription>
        </Alert>

        <Alert>
          <Heart size={16} />
          <AlertDescription>
            <strong>Buen progreso:</strong> Los niveles de calcio y vitamina C están en rangos óptimos. 
            ¡Continúa con la alimentación actual!
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );

  const renderDetailed = () => (
    <div className="space-y-6">
      {/* Gráfico de Crecimiento */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-6">Tendencia de Crecimiento vs. Recomendaciones OMS</h3>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={growthData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="weight" 
                stroke="#16a34a" 
                strokeWidth={3}
                name="Peso Actual (kg)"
              />
              <Line 
                type="monotone" 
                dataKey="recommended_weight" 
                stroke="#f97316" 
                strokeDasharray="5 5"
                name="Peso Recomendado (kg)"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-center space-x-6 mt-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-0.5 bg-primary"></div>
            <span>Peso Actual</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-0.5 bg-secondary border-dashed"></div>
            <span>Peso Recomendado OMS</span>
          </div>
        </div>
      </Card>

      {/* Análisis Predictivo */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-6">Predicciones a 6 Meses</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h4 className="font-medium">Escenario Actual</h4>
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm mb-2">Manteniendo la dieta actual:</p>
              <ul className="text-sm space-y-1 text-muted-foreground">
                <li>• Peso estimado: 21.2 kg</li>
                <li>• Altura estimada: 106 cm</li>
                <li>• IMC proyectado: 18.9</li>
                <li>• Estado: Normal-bajo</li>
              </ul>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="font-medium">Escenario Optimizado</h4>
            <div className="p-4 bg-success/10 rounded-lg">
              <p className="text-sm mb-2">Siguiendo recomendaciones:</p>
              <ul className="text-sm space-y-1 text-success">
                <li>• Peso estimado: 22.1 kg</li>
                <li>• Altura estimada: 107 cm</li>
                <li>• IMC proyectado: 19.3</li>
                <li>• Estado: Óptimo</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );

  const renderComparison = () => (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-6">Comparación con Estándares MINSA/OMS</h3>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={comparisonData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="category" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#16a34a" name="Tu Progreso %" />
            <Bar dataKey="recommended" fill="#e2e8f0" name="Estándar Recomendado %" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 bg-primary/5 rounded-lg">
          <h4 className="font-medium mb-2">Puntos Fuertes</h4>
          <ul className="text-sm space-y-1">
            <li className="flex items-center space-x-2">
              <span className="text-success">✓</span>
              <span>Carbohidratos en rango óptimo</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="text-success">✓</span>
              <span>Proteínas cerca del objetivo</span>
            </li>
          </ul>
        </div>

        <div className="p-4 bg-warning/5 rounded-lg">
          <h4 className="font-medium mb-2">Áreas de Mejora</h4>
          <ul className="text-sm space-y-1">
            <li className="flex items-center space-x-2">
              <span className="text-warning">⚠</span>
              <span>Incrementar vitaminas y minerales</span>
            </li>
            <li className="flex items-center space-x-2">
              <span className="text-warning">⚠</span>
              <span>Mejorar balance de grasas saludables</span>
            </li>
          </ul>
        </div>
      </div>
    </Card>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Predicción de Riesgos</h1>
          <p className="text-muted-foreground mt-1">
            Análisis predictivo basado en inteligencia artificial
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant={selectedPeriod === '1m' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedPeriod('1m')}
          >
            1M
          </Button>
          <Button
            variant={selectedPeriod === '3m' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedPeriod('3m')}
          >
            3M
          </Button>
          <Button
            variant={selectedPeriod === '6m' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedPeriod('6m')}
          >
            6M
          </Button>
        </div>
      </div>

      {/* Navegación de tabs */}
      <div className="flex space-x-2 border-b">
        <Button
          variant={activeTab === 'overview' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('overview')}
          className="rounded-b-none"
        >
          <Shield size={16} className="mr-2" />
          Resumen
        </Button>
        <Button
          variant={activeTab === 'detailed' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('detailed')}
          className="rounded-b-none"
        >
          <TrendingUp size={16} className="mr-2" />
          Análisis Detallado
        </Button>
        <Button
          variant={activeTab === 'comparison' ? 'default' : 'ghost'}
          onClick={() => setActiveTab('comparison')}
          className="rounded-b-none"
        >
          <Target size={16} className="mr-2" />
          Comparación
        </Button>
      </div>

      {/* Contenido de las tabs */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'detailed' && renderDetailed()}
        {activeTab === 'comparison' && renderComparison()}
      </motion.div>

      {/* Acciones rápidas */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button className="flex-1 bg-primary hover:bg-primary-dark">
          <Calendar size={16} className="mr-2" />
          Programar Consulta Médica
        </Button>
        <Button variant="outline" className="flex-1">
          <Target size={16} className="mr-2" />
          Generar Plan Personalizado
        </Button>
      </div>
    </div>
  );
}