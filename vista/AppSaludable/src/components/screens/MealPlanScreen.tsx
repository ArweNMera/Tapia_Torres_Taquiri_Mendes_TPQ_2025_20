import { useState } from 'react';
import { Calendar, Clock, Plus, Utensils, Apple, Coffee, Sun, Moon, Settings, RefreshCw, BookOpen } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import { motion } from 'motion/react';
import { MealPreferencesSetup } from './MealPreferencesSetup';
import { RecipeDetailModal } from '../RecipeDetailModal';

interface MealPlanScreenProps {
  onRecipeClick?: (recipeId: string) => void;
}

interface Meal {
  id: string;
  name: string;
  time: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  image: string;
  difficulty: 'Fácil' | 'Intermedio' | 'Avanzado';
  duration: number;
  ingredients: number;
}

const weeklyPlan = {
  Monday: {
    breakfast: {
      id: '1',
      name: 'Avena con Frutas',
      time: '08:00',
      calories: 320,
      protein: 12,
      carbs: 45,
      fats: 8,
      image: 'https://images.unsplash.com/photo-1517884061854-4ddc25fb5e0b?w=400',
      difficulty: 'Fácil' as const,
      duration: 10,
      ingredients: 5
    },
    lunch: {
      id: '2',
      name: 'Pollo al Vapor con Quinoa',
      time: '13:00',
      calories: 450,
      protein: 35,
      carbs: 40,
      fats: 12,
      image: 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400',
      difficulty: 'Intermedio' as const,
      duration: 25,
      ingredients: 8
    },
    dinner: {
      id: '3',
      name: 'Salmón con Vegetales',
      time: '19:00',
      calories: 380,
      protein: 28,
      carbs: 15,
      fats: 22,
      image: 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400',
      difficulty: 'Intermedio' as const,
      duration: 20,
      ingredients: 6
    },
    snack: {
      id: '4',
      name: 'Yogurt con Almendras',
      time: '16:00',
      calories: 180,
      protein: 8,
      carbs: 12,
      fats: 12,
      image: 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400',
      difficulty: 'Fácil' as const,
      duration: 5,
      ingredients: 3
    }
  }
};

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const dayNames = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'];

export function MealPlanScreen({ onRecipeClick }: MealPlanScreenProps) {
  const [selectedDay, setSelectedDay] = useState('Monday');
  const [viewMode, setViewMode] = useState<'day' | 'week'>('day');
  const [showSetup, setShowSetup] = useState(false);
  const [hasCompletedSetup, setHasCompletedSetup] = useState(false);
  const [selectedRecipe, setSelectedRecipe] = useState<string | null>(null);
  const [userPreferences, setUserPreferences] = useState<any>(null);

  const getMealIcon = (mealType: string) => {
    switch (mealType) {
      case 'breakfast': return <Coffee size={20} className="text-accent-dark" />;
      case 'lunch': return <Sun size={20} className="text-secondary" />;
      case 'dinner': return <Moon size={20} className="text-primary" />;
      case 'snack': return <Apple size={20} className="text-success" />;
      default: return <Utensils size={20} />;
    }
  };

  const getMealTitle = (mealType: string) => {
    switch (mealType) {
      case 'breakfast': return 'Desayuno';
      case 'lunch': return 'Almuerzo';
      case 'dinner': return 'Cena';
      case 'snack': return 'Snack';
      default: return 'Comida';
    }
  };

  const handleSetupComplete = (preferences: any) => {
    setUserPreferences(preferences);
    setHasCompletedSetup(true);
    setShowSetup(false);
  };

  const handleSetupSkip = () => {
    setHasCompletedSetup(true);
    setShowSetup(false);
  };

  const handleRecipeDetailClick = (mealId: string) => {
    setSelectedRecipe(mealId);
    onRecipeClick?.(mealId);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'F��cil': return 'bg-success text-white';
      case 'Intermedio': return 'bg-warning text-white';
      case 'Avanzado': return 'bg-destructive text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const renderMealCard = (meal: Meal, mealType: string) => (
    <Card className="p-4 hover:shadow-md transition-all duration-200 border-l-4 border-l-primary">
      <div className="flex items-start space-x-4">
        <div className="w-16 h-16 rounded-lg overflow-hidden bg-muted flex-shrink-0">
          <img
            src={meal.image}
            alt={meal.name}
            className="w-full h-full object-cover"
          />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              {getMealIcon(mealType)}
              <span className="text-sm font-medium text-muted-foreground">
                {getMealTitle(mealType)}
              </span>
            </div>
            <span className="text-sm text-muted-foreground">{meal.time}</span>
          </div>

          <h3 className="font-semibold text-gray-900 mb-2 truncate">{meal.name}</h3>

          <div className="flex items-center space-x-3 mb-3">
            <Badge className={`text-xs px-2 py-1 ${getDifficultyColor(meal.difficulty)}`}>
              {meal.difficulty}
            </Badge>
            <span className="text-xs text-muted-foreground flex items-center">
              <Clock size={12} className="mr-1" />
              {meal.duration}min
            </span>
            <span className="text-xs text-muted-foreground">
              {meal.ingredients} ingredientes
            </span>
          </div>

          <div className="grid grid-cols-4 gap-2 text-center mb-3">
            <div>
              <p className="text-xs text-muted-foreground">Calorías</p>
              <p className="font-semibold text-sm">{meal.calories}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Proteína</p>
              <p className="font-semibold text-sm text-chart-1">{meal.protein}g</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Carbos</p>
              <p className="font-semibold text-sm text-chart-2">{meal.carbs}g</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Grasas</p>
              <p className="font-semibold text-sm text-chart-3">{meal.fats}g</p>
            </div>
          </div>

          {/* Botón para ver receta */}
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={() => handleRecipeDetailClick(meal.id)}
          >
            <BookOpen size={14} className="mr-2" />
            Ver Receta Completa
          </Button>
        </div>
      </div>
    </Card>
  );

  const renderDayView = () => {
    const dayPlan = weeklyPlan[selectedDay as keyof typeof weeklyPlan] || weeklyPlan.Monday;
    const totalCalories = Object.values(dayPlan).reduce((sum, meal) => sum + meal.calories, 0);
    const totalProtein = Object.values(dayPlan).reduce((sum, meal) => sum + meal.protein, 0);

    return (
      <div className="space-y-6">
        {/* Resumen del día */}
        <Card className="p-6 bg-gradient-to-r from-primary/5 to-secondary/5 border-primary/20">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">
              {dayNames[days.indexOf(selectedDay)]}
            </h2>
            <Badge className="bg-primary text-white px-3 py-1">
              {totalCalories} kcal totales
            </Badge>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-3 bg-white rounded-lg">
              <p className="text-sm text-muted-foreground">Meta calórica</p>
              <p className="text-lg font-semibold text-primary">1,800</p>
            </div>
            <div className="p-3 bg-white rounded-lg">
              <p className="text-sm text-muted-foreground">Consumidas</p>
              <p className="text-lg font-semibold text-secondary">{totalCalories}</p>
            </div>
            <div className="p-3 bg-white rounded-lg">
              <p className="text-sm text-muted-foreground">Proteína</p>
              <p className="text-lg font-semibold text-chart-1">{totalProtein}g</p>
            </div>
            <div className="p-3 bg-white rounded-lg">
              <p className="text-sm text-muted-foreground">Comidas</p>
              <p className="text-lg font-semibold text-accent-dark">4</p>
            </div>
          </div>
        </Card>

        {/* Comidas del día */}
        <div className="space-y-4">
          {renderMealCard(dayPlan.breakfast, 'breakfast')}
          {renderMealCard(dayPlan.snack, 'snack')}
          {renderMealCard(dayPlan.lunch, 'lunch')}
          {renderMealCard(dayPlan.dinner, 'dinner')}
        </div>

        {/* Botón para agregar comida */}
        <Card className="p-6 border-dashed border-2 border-muted-foreground/30 hover:border-primary/50 transition-colors">
          <Button
            variant="ghost"
            className="w-full h-16 text-muted-foreground hover:text-primary"
            onClick={() => console.log('Agregar comida personalizada')}
          >
            <Plus size={24} className="mr-2" />
            Agregar comida personalizada
          </Button>
        </Card>
      </div>
    );
  };

  // Si no ha completado la configuración inicial, mostrar el setup
  if (showSetup || !hasCompletedSetup) {
    return (
      <MealPreferencesSetup
        onComplete={handleSetupComplete}
        onSkip={handleSetupSkip}
      />
    );
  }

  return (
    <>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Mi Plan de Comidas</h1>
            <p className="text-muted-foreground mt-1">
              {userPreferences ? 'Plan personalizado basado en tus preferencias' : 'Planificación personalizada para toda la semana'}
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSetup(true)}
            >
              <Settings size={16} className="mr-2" />
              Ajustar
            </Button>
            <Button
              variant={viewMode === 'day' ? 'default' : 'outline'}
              onClick={() => setViewMode('day')}
              size="sm"
            >
              Día
            </Button>
            <Button
              variant={viewMode === 'week' ? 'default' : 'outline'}
              onClick={() => setViewMode('week')}
              size="sm"
            >
              Semana
            </Button>
          </div>
        </div>

        {/* Recomendación personalizada */}
        {userPreferences && (
          <Alert>
            <RefreshCw size={16} />
            <AlertDescription>
              ¡Plan actualizado! Hemos generado recomendaciones basadas en tus preferencias:
              <strong> {userPreferences.goals?.slice(0, 2).join(', ')}</strong>
              {userPreferences.goals?.length > 2 && ` y ${userPreferences.goals.length - 2} objetivos más`}.
            </AlertDescription>
          </Alert>
        )}

        {/* Navegación de días */}
        <div className="flex space-x-2 overflow-x-auto pb-2">
          {days.map((day, index) => (
            <Button
              key={day}
              variant={selectedDay === day ? 'default' : 'outline'}
              onClick={() => setSelectedDay(day)}
              className="flex-shrink-0"
              size="sm"
            >
              <Calendar size={16} className="mr-1" />
              {dayNames[index]}
            </Button>
          ))}
        </div>

        {/* Vista del contenido */}
        <motion.div
          key={selectedDay}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {viewMode === 'day' ? renderDayView() : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Vista semanal en desarrollo...</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* Modal de detalle de receta */}
      <RecipeDetailModal
        isOpen={!!selectedRecipe}
        onClose={() => setSelectedRecipe(null)}
        onAddToPlan={() => {
          // Lógica para agregar al plan
          setSelectedRecipe(null);
        }}
        onSave={() => {
          // Lógica para guardar receta
        }}
        onShare={() => {
          // Lógica para compartir receta
        }}
      />
    </>
  );
}
