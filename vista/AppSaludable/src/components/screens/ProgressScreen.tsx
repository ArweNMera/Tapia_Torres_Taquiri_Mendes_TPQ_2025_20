import { useState } from 'react';
import { TrendingUp, Calendar, Award, Target } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Progress } from '../ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

export function ProgressScreen() {
  const [selectedPeriod, setSelectedPeriod] = useState('week');

  const weightData = [
    { date: 'Ene', weight: 11.8 },
    { date: 'Feb', weight: 12.0 },
    { date: 'Mar', weight: 12.1 },
    { date: 'Abr', weight: 12.3 },
    { date: 'May', weight: 12.5 },
  ];

  const nutritionData = [
    { day: 'Lun', proteinas: 85, carbohidratos: 72, grasas: 45 },
    { day: 'Mar', proteinas: 90, carbohidratos: 78, grasas: 52 },
    { day: 'Mié', proteinas: 78, carbohidratos: 68, grasas: 48 },
    { day: 'Jue', proteinas: 92, carbohidratos: 82, grasas: 55 },
    { day: 'Vie', proteinas: 88, carbohidratos: 75, grasas: 50 },
    { day: 'Sáb', proteinas: 85, carbohidratos: 70, grasas: 47 },
    { day: 'Dom', proteinas: 80, carbohidratos: 65, grasas: 42 },
  ];

  const achievements = [
    {
      title: 'Primera Semana Completa',
      description: 'Completó su primera semana de alimentación saludable',
      date: '2024-01-15',
      icon: '🏆',
      earned: true
    },
    {
      title: 'Explorador de Sabores',
      description: 'Probó 10 recetas diferentes',
      date: '2024-01-22',
      icon: '🌟',
      earned: true
    },
    {
      title: 'Peso Ideal',
      description: 'Mantiene un peso saludable por 30 días',
      date: null,
      icon: '⚖️',
      earned: false
    },
    {
      title: 'Nutrición Perfecta',
      description: 'Cumplió con todos los macronutrientes por 7 días',
      date: null,
      icon: '💪',
      earned: false
    }
  ];

  return (
    <div className="p-4 lg:p-6 space-y-6 lg:max-w-6xl lg:mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-800 mb-2">Progreso Nutricional</h1>
        <p className="text-gray-600">Seguimiento del desarrollo saludable de Sofía</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-3">
        <Card className="p-4 bg-gradient-to-br from-green-100 to-green-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Peso actual</p>
              <p className="text-xl font-semibold text-gray-800">12.5 kg</p>
              <p className="text-xs text-green-600 flex items-center mt-1">
                <TrendingUp size={12} className="mr-1" />
                +200g esta semana
              </p>
            </div>
            <div className="w-12 h-12 bg-green-200 rounded-full flex items-center justify-center">
              <span className="text-xl">📈</span>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-br from-blue-100 to-blue-50">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">IMC</p>
              <p className="text-xl font-semibold text-gray-800">Normal</p>
              <p className="text-xs text-blue-600 flex items-center mt-1">
                <Target size={12} className="mr-1" />
                Percentil 65
              </p>
            </div>
            <div className="w-12 h-12 bg-blue-200 rounded-full flex items-center justify-center">
              <span className="text-xl">💙</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Period Selector */}
      <div className="flex justify-center">
        <div className="flex bg-gray-100 rounded-lg p-1">
          {[
            { id: 'week', label: 'Semana' },
            { id: 'month', label: 'Mes' },
            { id: 'year', label: 'Año' }
          ].map((period) => (
            <button
              key={period.id}
              onClick={() => setSelectedPeriod(period.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                selectedPeriod === period.id
                  ? 'bg-white text-gray-800 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              {period.label}
            </button>
          ))}
        </div>
      </div>

      {/* Charts */}
      <Tabs defaultValue="weight" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="weight">Peso y Crecimiento</TabsTrigger>
          <TabsTrigger value="nutrition">Nutrición Semanal</TabsTrigger>
        </TabsList>

        <TabsContent value="weight" className="space-y-4">
          <Card className="p-4 lg:p-6">
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
              <TrendingUp size={20} className="mr-2 text-green-600" />
              Evolución del Peso
            </h3>
            <div className="h-48 lg:h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={weightData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis domain={['dataMin - 0.5', 'dataMax + 0.5']} />
                  <Tooltip formatter={(value) => [`${value} kg`, 'Peso']} />
                  <Line
                    type="monotone"
                    dataKey="weight"
                    stroke="#16a34a"
                    strokeWidth={3}
                    dot={{ fill: '#16a34a', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="font-semibold text-gray-800 mb-4">Metas de Crecimiento</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Peso ideal para la edad</span>
                  <span className="text-green-600">92%</span>
                </div>
                <Progress value={92} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Altura esperada</span>
                  <span className="text-blue-600">88%</span>
                </div>
                <Progress value={88} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Desarrollo motor</span>
                  <span className="text-purple-600">95%</span>
                </div>
                <Progress value={95} className="h-2" />
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="nutrition" className="space-y-4">
          <Card className="p-4 lg:p-6">
            <h3 className="font-semibold text-gray-800 mb-4">Macronutrientes (% de meta diaria)</h3>
            <div className="h-48 lg:h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={nutritionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="proteinas" fill="#16a34a" name="Proteínas" />
                  <Bar dataKey="carbohidratos" fill="#ea580c" name="Carbohidratos" />
                  <Bar dataKey="grasas" fill="#eab308" name="Grasas" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <div className="grid grid-cols-3 gap-3">
            <Card className="p-3 text-center bg-green-50">
              <div className="text-green-600 mb-1">💪</div>
              <p className="text-xs text-gray-600">Proteínas</p>
              <p className="text-lg font-semibold text-gray-800">86%</p>
              <p className="text-xs text-green-600">Promedio semanal</p>
            </Card>
            <Card className="p-3 text-center bg-orange-50">
              <div className="text-orange-600 mb-1">🍞</div>
              <p className="text-xs text-gray-600">Carbohidratos</p>
              <p className="text-lg font-semibold text-gray-800">73%</p>
              <p className="text-xs text-orange-600">Promedio semanal</p>
            </Card>
            <Card className="p-3 text-center bg-yellow-50">
              <div className="text-yellow-600 mb-1">🥑</div>
              <p className="text-xs text-gray-600">Grasas</p>
              <p className="text-lg font-semibold text-gray-800">48%</p>
              <p className="text-xs text-yellow-600">Promedio semanal</p>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Achievements */}
      <Card className="p-4">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
          <Award size={20} className="mr-2 text-yellow-600" />
          Logros Nutricionales
        </h3>
        <div className="space-y-3">
          {achievements.map((achievement, index) => (
            <div
              key={index}
              className={`flex items-center p-3 rounded-lg border ${
                achievement.earned
                  ? 'bg-yellow-50 border-yellow-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className={`text-2xl mr-3 ${!achievement.earned && 'grayscale opacity-50'}`}>
                {achievement.icon}
              </div>
              <div className="flex-1">
                <h4 className={`font-medium ${
                  achievement.earned ? 'text-gray-800' : 'text-gray-500'
                }`}>
                  {achievement.title}
                </h4>
                <p className={`text-sm ${
                  achievement.earned ? 'text-gray-600' : 'text-gray-400'
                }`}>
                  {achievement.description}
                </p>
                {achievement.earned && achievement.date && (
                  <p className="text-xs text-yellow-600 mt-1">
                    Obtenido el {new Date(achievement.date).toLocaleDateString('es-ES')}
                  </p>
                )}
              </div>
              {achievement.earned && (
                <div className="text-yellow-600">
                  <Award size={20} />
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Export Progress */}
      <Card className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
        <div className="text-center">
          <h3 className="font-semibold text-gray-800 mb-2">📊 Reporte de Progreso</h3>
          <p className="text-sm text-gray-600 mb-3">
            Genera un reporte completo para compartir con el pediatra
          </p>
          <div className="flex gap-2">
            <Button className="flex-1 bg-purple-600 hover:bg-purple-700 text-white text-sm">
              Descargar PDF
            </Button>
            <Button variant="outline" className="flex-1 text-sm">
              Enviar por Email
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
