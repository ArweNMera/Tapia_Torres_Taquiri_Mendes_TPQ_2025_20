import React from 'react';
import { Bell, Search, Calendar, TrendingUp, Apple, Droplets, Zap, Clock } from 'lucide-react';
import { NutritionCard } from '../NutritionCard';
import { RecipeCard } from '../RecipeCard';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Progress } from '../ui/progress';
import { useAuth } from '../../contexts/AuthContext';

interface DashboardScreenProps {
  onRecipeClick?: (recipeId: string) => void;
}

export function DashboardScreen({ onRecipeClick }: DashboardScreenProps) {
  const { user } = useAuth();
  const defaultAvatarUrl = 'https://images.unsplash.com/photo-1494790108755-2616b612b577?w=150';
  const avatarSrc = user?.avatar_url && user.avatar_url.trim().length > 0
    ? user.avatar_url.trim()
    : defaultAvatarUrl;
  const avatarKey = user?.avatar_url && user.avatar_url.trim().length > 0
    ? user.avatar_url.trim()
    : 'dashboard-default-avatar';
  
  const todayMeals = [
    {
      id: '1',
      title: 'Puré de calabaza con pollo',
      image: 'https://images.unsplash.com/photo-1583506955278-b24cb3b0c9b5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2xvcmZ1bCUyMHZlZ2V0YWJsZXMlMjBmcnVpdHMlMjBraWRzJTIwbWVhbHxlbnwxfHx8fDE3NTcyMjA0NTB8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      cookTime: '20 min',
      servings: 2,
      rating: 4.8,
      difficulty: 'Fácil' as const,
      calories: 180
    },
    {
      id: '2',
      title: 'Smoothie de frutas y avena',
      image: 'https://images.unsplash.com/photo-1744028982670-67ca067bedfa?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb29raW5nJTIwcmVjaXBlJTIwaGVhbHRoeSUyMGluZ3JlZGllbnRzfGVufDF8fHx8MTc1NzIyMDQ1MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      cookTime: '5 min',
      servings: 1,
      rating: 4.9,
      difficulty: 'Fácil' as const,
      calories: 220
    }
  ];

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Desktop Grid Layout */}
      <div className="lg:grid lg:grid-cols-12 lg:gap-6 lg:space-y-0 space-y-6">
        {/* Left Column - Main Content */}
        <div className="lg:col-span-8 space-y-6">
          {/* Header - Mobile Only */}
          <div className="lg:hidden flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Avatar className="w-12 h-12">
                <AvatarImage key={avatarKey} src={avatarSrc} />
                <AvatarFallback>
                  {user?.usr_nombre?.charAt(0) || ''}{user?.usr_apellido?.charAt(0) || ''}
                </AvatarFallback>
              </Avatar>
              <div>
                <h1 className="text-xl font-semibold text-gray-800">¡Hola, {user?.usr_nombre}!</h1>
                <p className="text-sm text-gray-600">Bienvenido de vuelta</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="icon" className="relative">
                <Bell size={20} />
                <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
              </Button>
              <Button variant="ghost" size="icon">
                <Search size={20} />
              </Button>
            </div>
          </div>

          {/* Desktop Welcome */}
          <div className="hidden lg:block">
            <h1 className="text-2xl font-semibold text-gray-800 mb-2">¡Buen día, {user?.usr_nombre}!</h1>
            <p className="text-gray-600">Aquí tienes el resumen nutricional de Sofía para hoy</p>
          </div>

          {/* Daily Progress */}
          <Card className="p-4 lg:p-6 bg-gradient-to-r from-green-100 to-green-50">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold text-gray-800">Progreso de Hoy</h2>
              <Calendar size={20} className="text-green-600" />
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Calorías consumidas</span>
                  <span>680 / 1200 kcal</span>
                </div>
                <Progress value={56} className="h-2" />
              </div>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <p className="text-sm text-gray-600">Proteínas</p>
                  <p className="font-semibold text-green-600">85%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Carbohidratos</p>
                  <p className="font-semibold text-orange-600">72%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Grasas</p>
                  <p className="font-semibold text-yellow-600">45%</p>
                </div>
              </div>
            </div>
          </Card>

          {/* Nutrition Metrics */}
          <div>
            <h2 className="font-semibold text-gray-800 mb-3">Métricas Nutricionales</h2>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
              <NutritionCard
                title="Peso actual"
                value="12.5 kg"
                subtitle="+200g esta semana"
                icon={<TrendingUp size={24} />}
                color="green"
              />
              <NutritionCard
                title="IMC infantil"
                value="Normal"
                subtitle="Percentil 57.7"
                icon={<Apple size={24} />}
                color="blue"
              />
              <NutritionCard
                title="Hidratación"
                value="750 ml"
                subtitle="Meta: 1000ml"
                icon={<Droplets size={24} />}
                color="blue"
              />
              <NutritionCard
                title="Energía"
                value="Activa"
                subtitle="2h de juego"
                icon={<Zap size={24} />}
                color="yellow"
              />
            </div>
          </div>

          {/* Today's Meals */}
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold text-gray-800">Comidas de Hoy</h2>
              <Button variant="ghost" className="text-green-600 text-sm">
                Ver plan completo
              </Button>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
              {todayMeals.map((meal) => (
                <RecipeCard
                  title={meal.title}
                  image={meal.image}
                  cookTime={meal.cookTime}
                  servings={meal.servings}
                  rating={meal.rating}
                  difficulty={meal.difficulty as 'Fácil'}
                  calories={meal.calories}
                  onClick={() => onRecipeClick?.(meal.id)}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Right Column - Sidebar Content (Desktop Only) */}
        <div className="hidden lg:block lg:col-span-4 space-y-6">

          {/* Quick Actions - Desktop Sidebar */}
          <Card className="p-4">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
              <Zap size={18} className="mr-2 text-orange-600" />
              Acciones Rápidas
            </h3>
            <div className="space-y-3">
              <Button className="w-full bg-primary/10 text-primary hover:bg-primary/20 border border-primary/20 justify-start">
                🍽️ Mi Plan de Comidas
              </Button>
              <Button className="w-full bg-orange-100 text-orange-800 hover:bg-orange-200 border border-orange-200 justify-start">
                📱 Consultar nutricionista
              </Button>
              <Button className="w-full bg-green-100 text-green-800 hover:bg-green-200 border border-green-200 justify-start">
                📊 Ver progreso semanal
              </Button>
              <Button className="w-full bg-blue-100 text-blue-800 hover:bg-blue-200 border border-blue-200 justify-start">
                📱 Escanear producto
              </Button>
            </div>
          </Card>

          {/* Health Tips - Desktop Sidebar */}
          <Card className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200">
            <h3 className="font-semibold text-gray-800 mb-2 flex items-center">
              💡 Consejo del día
            </h3>
            <p className="text-sm text-gray-700 mb-3">
              Las frutas de temporada aportan vitaminas esenciales. Incluye manzanas y peras en la merienda de Sofía para fortalecer su sistema inmune.
            </p>
            <Button size="sm" variant="outline" className="w-full">
              Ver más consejos
            </Button>
          </Card>

          {/* Weekly Summary - Desktop Sidebar */}
          <Card className="p-4">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
              <Calendar size={18} className="mr-2 text-purple-600" />
              Resumen Semanal
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Recetas probadas</span>
                <span className="font-semibold text-gray-800">8</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Días con meta completa</span>
                <span className="font-semibold text-green-600">5/7</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Peso promedio</span>
                <span className="font-semibold text-gray-800">12.4 kg</span>
              </div>
            </div>
          </Card>

          {/* Upcoming Meals - Desktop Sidebar */}
          <Card className="p-4">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
              <Clock size={18} className="mr-2 text-blue-600" />
              Próximas Comidas
            </h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800">Merienda</p>
                  <p className="text-xs text-gray-500">15:30 - Compota de manzana</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800">Cena</p>
                  <p className="text-xs text-gray-500">19:00 - Sopa de verduras</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Mobile-only Quick Actions and Health Tips */}
      <div className="lg:hidden space-y-6">
        <Card className="p-4">
          <h3 className="font-semibold text-gray-800 mb-3">Acciones Rápidas</h3>
          <div className="grid grid-cols-2 gap-3">
            <Button className="bg-orange-100 text-orange-800 hover:bg-orange-200 border border-orange-200">
              📱 Consultar nutricionista
            </Button>
            <Button className="bg-green-100 text-green-800 hover:bg-green-200 border border-green-200">
              📊 Ver progreso semanal
            </Button>
          </div>
        </Card>

        <Card className="p-4 bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200">
          <h3 className="font-semibold text-gray-800 mb-2">💡 Consejo del día</h3>
          <p className="text-sm text-gray-700">
            Las frutas de temporada aportan vitaminas esenciales. Incluye manzanas y peras en la merienda de Sofía para fortalecer su sistema inmune.
          </p>
        </Card>
      </div>
    </div>
  );
}
