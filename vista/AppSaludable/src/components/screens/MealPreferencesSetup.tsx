import { useState } from 'react';
import { Check, Plus, X, Clock, Users, AlertCircle } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Alert, AlertDescription } from '../ui/alert';
import { motion, AnimatePresence } from 'motion/react';

interface MealItem {
  id: string;
  name: string;
  frequency: 'daily' | 'weekly' | 'occasionally';
  category: string;
}

interface MealPreferencesSetupProps {
  onComplete: (preferences: UserMealPreferences) => void;
  onSkip: () => void;
}

interface UserMealPreferences {
  currentMeals: {
    breakfast: MealItem[];
    lunch: MealItem[];
    dinner: MealItem[];
    snacks: MealItem[];
  };
  dietaryRestrictions: string[];
  allergies: string[];
  familySize: number;
  cookingTime: string;
  experience: string;
  goals: string[];
}

const commonFoods = {
  breakfast: [
    { name: 'Avena', category: 'Cereales' },
    { name: 'Huevos', category: 'Proteínas' },
    { name: 'Pan tostado', category: 'Cereales' },
    { name: 'Frutas', category: 'Frutas' },
    { name: 'Yogurt', category: 'Lácteos' },
    { name: 'Cereal', category: 'Cereales' }
  ],
  lunch: [
    { name: 'Arroz', category: 'Cereales' },
    { name: 'Pollo', category: 'Proteínas' },
    { name: 'Verduras', category: 'Verduras' },
    { name: 'Pasta', category: 'Cereales' },
    { name: 'Legumbres', category: 'Proteínas' },
    { name: 'Pescado', category: 'Proteínas' }
  ],
  dinner: [
    { name: 'Sopa', category: 'Líquidos' },
    { name: 'Ensalada', category: 'Verduras' },
    { name: 'Carne', category: 'Proteínas' },
    { name: 'Verduras cocidas', category: 'Verduras' },
    { name: 'Quinoa', category: 'Cereales' },
    { name: 'Tofu', category: 'Proteínas' }
  ],
  snacks: [
    { name: 'Frutas', category: 'Frutas' },
    { name: 'Frutos secos', category: 'Proteínas' },
    { name: 'Galletas', category: 'Cereales' },
    { name: 'Yogurt', category: 'Lácteos' },
    { name: 'Verduras crudas', category: 'Verduras' }
  ]
};

const allergies = [
  'Gluten', 'Lácteos', 'Huevos', 'Frutos secos', 'Mariscos',
  'Soja', 'Pescado', 'Ajonjolí', 'Ninguna'
];

const goals = [
  'Alimentación más balanceada',
  'Aumentar consumo de verduras',
  'Reducir azúcar procesada',
  'Más variedad en comidas',
  'Comidas más rápidas',
  'Alimentación económica'
];

export function MealPreferencesSetup({ onComplete, onSkip }: MealPreferencesSetupProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [preferences, setPreferences] = useState<UserMealPreferences>({
    currentMeals: {
      breakfast: [],
      lunch: [],
      dinner: [],
      snacks: []
    },
    dietaryRestrictions: [],
    allergies: [],
    familySize: 2,
    cookingTime: '30-45',
    experience: 'intermedio',
    goals: []
  });

  const [currentMealType, setCurrentMealType] = useState<'breakfast' | 'lunch' | 'dinner' | 'snacks'>('breakfast');
  const [customFoodInput, setCustomFoodInput] = useState('');

  const totalSteps = 4;

  const getMealTypeLabel = (type: string) => {
    switch (type) {
      case 'breakfast': return 'Desayuno';
      case 'lunch': return 'Almuerzo';
      case 'dinner': return 'Cena';
      case 'snacks': return 'Snacks';
      default: return type;
    }
  };

  const addMealItem = (mealType: keyof typeof preferences.currentMeals, item: MealItem) => {
    setPreferences(prev => ({
      ...prev,
      currentMeals: {
        ...prev.currentMeals,
        [mealType]: [...prev.currentMeals[mealType], item]
      }
    }));
  };

  const removeMealItem = (mealType: keyof typeof preferences.currentMeals, itemId: string) => {
    setPreferences(prev => ({
      ...prev,
      currentMeals: {
        ...prev.currentMeals,
        [mealType]: prev.currentMeals[mealType].filter(item => item.id !== itemId)
      }
    }));
  };

  const addCustomFood = () => {
    if (customFoodInput.trim()) {
      const newItem: MealItem = {
        id: Date.now().toString(),
        name: customFoodInput.trim(),
        frequency: 'daily',
        category: 'Personalizado'
      };
      addMealItem(currentMealType, newItem);
      setCustomFoodInput('');
    }
  };

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete(preferences);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStep1 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">¿Qué sueles comer actualmente?</h2>
        <p className="text-muted-foreground">
          Cuéntanos tus comidas habituales para generar recomendaciones personalizadas
        </p>
      </div>

      {/* Selector de tipo de comida */}
      <div className="flex space-x-2 mb-6">
        {(['breakfast', 'lunch', 'dinner', 'snacks'] as const).map((type) => (
          <Button
            key={type}
            variant={currentMealType === type ? 'default' : 'outline'}
            onClick={() => setCurrentMealType(type)}
            className="flex-1"
            size="sm"
          >
            {getMealTypeLabel(type)}
          </Button>
        ))}
      </div>

      {/* Comidas seleccionadas para el tipo actual */}
      <Card className="p-4 min-h-[120px]">
        <h3 className="font-semibold mb-3">{getMealTypeLabel(currentMealType)} actual:</h3>

        <div className="flex flex-wrap gap-2 mb-4">
          <AnimatePresence>
            {preferences.currentMeals[currentMealType].map((item) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
              >
                <Badge className="flex items-center space-x-2 bg-primary text-white">
                  <span>{item.name}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-4 w-4 p-0 hover:bg-white/20"
                    onClick={() => removeMealItem(currentMealType, item.id)}
                  >
                    <X size={12} />
                  </Button>
                </Badge>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {preferences.currentMeals[currentMealType].length === 0 && (
          <p className="text-muted-foreground text-sm italic">
            Selecciona los alimentos que sueles comer en {getMealTypeLabel(currentMealType).toLowerCase()}
          </p>
        )}
      </Card>

      {/* Opciones comunes */}
      <div>
        <h4 className="font-medium mb-3">Opciones comunes:</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {commonFoods[currentMealType].map((food, index) => (
            <Button
              key={index}
              variant="outline"
              size="sm"
              onClick={() => {
                const newItem: MealItem = {
                  id: Date.now().toString() + index,
                  name: food.name,
                  frequency: 'daily',
                  category: food.category
                };
                addMealItem(currentMealType, newItem);
              }}
              className="justify-start"
              disabled={preferences.currentMeals[currentMealType].some(item => item.name === food.name)}
            >
              <Plus size={14} className="mr-2" />
              {food.name}
            </Button>
          ))}
        </div>
      </div>

      {/* Agregar comida personalizada */}
      <div className="flex space-x-2">
        <Input
          placeholder="¿Otra comida que no aparece?"
          value={customFoodInput}
          onChange={(e) => setCustomFoodInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addCustomFood()}
        />
        <Button onClick={addCustomFood} disabled={!customFoodInput.trim()}>
          <Plus size={16} />
        </Button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">Restricciones y Alergias</h2>
        <p className="text-muted-foreground">
          Para generar un plan seguro y adecuado para ti
        </p>
      </div>

      <Card className="p-6">
        <h3 className="font-semibold mb-4 flex items-center">
          <AlertCircle size={20} className="mr-2 text-warning" />
          Alergias Alimentarias
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {allergies.map((allergy) => (
            <Button
              key={allergy}
              variant={preferences.allergies.includes(allergy) ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                setPreferences(prev => ({
                  ...prev,
                  allergies: prev.allergies.includes(allergy)
                    ? prev.allergies.filter(a => a !== allergy)
                    : [...prev.allergies, allergy]
                }));
              }}
              className="justify-start"
            >
              {preferences.allergies.includes(allergy) && <Check size={14} className="mr-2" />}
              {allergy}
            </Button>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="font-semibold mb-4">Preferencias Dietéticas</h3>

        <div className="space-y-3">
          <Textarea
            placeholder="Ej: vegetariano, bajo en sodio, sin azúcar añadida, etc."
            value={preferences.dietaryRestrictions.join(', ')}
            onChange={(e) => {
              const restrictions = e.target.value.split(',').map(r => r.trim()).filter(r => r);
              setPreferences(prev => ({ ...prev, dietaryRestrictions: restrictions }));
            }}
            rows={3}
          />
          <p className="text-sm text-muted-foreground">
            Separa múltiples restricciones con comas
          </p>
        </div>
      </Card>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">Información de Cocina</h2>
        <p className="text-muted-foreground">
          Para ajustar las recetas a tu estilo de vida
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="font-semibold mb-4 flex items-center">
            <Users size={20} className="mr-2 text-primary" />
            Tamaño de Familia
          </h3>
          <Select
            value={preferences.familySize.toString()}
            onValueChange={(value) => setPreferences(prev => ({ ...prev, familySize: parseInt(value) }))}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1 persona</SelectItem>
              <SelectItem value="2">2 personas</SelectItem>
              <SelectItem value="3">3 personas</SelectItem>
              <SelectItem value="4">4 personas</SelectItem>
              <SelectItem value="5">5+ personas</SelectItem>
            </SelectContent>
          </Select>
        </Card>

        <Card className="p-6">
          <h3 className="font-semibold mb-4 flex items-center">
            <Clock size={20} className="mr-2 text-secondary" />
            Tiempo para Cocinar
          </h3>
          <Select
            value={preferences.cookingTime}
            onValueChange={(value) => setPreferences(prev => ({ ...prev, cookingTime: value }))}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="15">Menos de 15 min</SelectItem>
              <SelectItem value="15-30">15-30 minutos</SelectItem>
              <SelectItem value="30-45">30-45 minutos</SelectItem>
              <SelectItem value="45+">Más de 45 minutos</SelectItem>
            </SelectContent>
          </Select>
        </Card>
      </div>

      <Card className="p-6">
        <h3 className="font-semibold mb-4">Experiencia en Cocina</h3>
        <div className="grid grid-cols-3 gap-2">
          {[
            { value: 'principiante', label: 'Principiante' },
            { value: 'intermedio', label: 'Intermedio' },
            { value: 'avanzado', label: 'Avanzado' }
          ].map((level) => (
            <Button
              key={level.value}
              variant={preferences.experience === level.value ? 'default' : 'outline'}
              onClick={() => setPreferences(prev => ({ ...prev, experience: level.value }))}
            >
              {level.label}
            </Button>
          ))}
        </div>
      </Card>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold mb-2">Objetivos Nutricionales</h2>
        <p className="text-muted-foreground">
          ¿Qué te gustaría mejorar en tu alimentación?
        </p>
      </div>

      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {goals.map((goal) => (
            <Button
              key={goal}
              variant={preferences.goals.includes(goal) ? 'default' : 'outline'}
              size="sm"
              onClick={() => {
                setPreferences(prev => ({
                  ...prev,
                  goals: prev.goals.includes(goal)
                    ? prev.goals.filter(g => g !== goal)
                    : [...prev.goals, goal]
                }));
              }}
              className="justify-start h-auto p-4"
            >
              {preferences.goals.includes(goal) && <Check size={16} className="mr-2" />}
              <span className="text-left">{goal}</span>
            </Button>
          ))}
        </div>
      </Card>

      <Alert>
        <AlertCircle size={16} />
        <AlertDescription>
          Basándonos en tu información, generaremos un plan personalizado con recetas
          adaptadas a tus necesidades y preferencias.
        </AlertDescription>
      </Alert>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 to-secondary/5 p-4">
      <div className="max-w-2xl mx-auto">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-muted-foreground mb-2">
            <span>Paso {currentStep} de {totalSteps}</span>
            <span>{Math.round((currentStep / totalSteps) * 100)}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / totalSteps) * 100}%` }}
            />
          </div>
        </div>

        {/* Content */}
        <Card className="p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {currentStep === 1 && renderStep1()}
              {currentStep === 2 && renderStep2()}
              {currentStep === 3 && renderStep3()}
              {currentStep === 4 && renderStep4()}
            </motion.div>
          </AnimatePresence>
        </Card>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <div className="flex space-x-3">
            {currentStep > 1 && (
              <Button variant="outline" onClick={handleBack}>
                Anterior
              </Button>
            )}
            <Button variant="ghost" onClick={onSkip} className="text-muted-foreground">
              Omitir configuración
            </Button>
          </div>

          <Button
            onClick={handleNext}
            className="bg-primary hover:bg-primary-dark"
          >
            {currentStep === totalSteps ? 'Generar Mi Plan' : 'Siguiente'}
          </Button>
        </div>
      </div>
    </div>
  );
}
