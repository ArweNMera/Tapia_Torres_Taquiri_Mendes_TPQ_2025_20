import { X, Clock, Users, ChefHat, Heart, Share2, Bookmark, AlertCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Separator } from './ui/separator';
import { Progress } from './ui/progress';
import { Alert, AlertDescription } from './ui/alert';
import { motion } from 'motion/react';

interface Recipe {
  id: string;
  name: string;
  image: string;
  description: string;
  prepTime: number;
  cookTime: number;
  servings: number;
  difficulty: 'Fácil' | 'Intermedio' | 'Avanzado';
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  fiber: number;
  ingredients: {
    id: string;
    name: string;
    amount: string;
    unit: string;
    category: string;
  }[];
  instructions: {
    step: number;
    instruction: string;
    time?: number;
    image?: string;
  }[];
  tips: string[];
  nutritionBenefits: string[];
  allergens: string[];
  tags: string[];
}

interface RecipeDetailModalProps {
  recipe?: Recipe;
  isOpen: boolean;
  onClose: () => void;
  onSave?: () => void;
  onShare?: () => void;
  onAddToPlan?: () => void;
}

// Datos de ejemplo
const sampleRecipe: Recipe = {
  id: '1',
  name: 'Pollo al Vapor con Quinoa',
  image: 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=400',
  description: 'Una deliciosa comida balanceada, rica en proteínas y perfecta para toda la familia. Ideal para niños en crecimiento.',
  prepTime: 15,
  cookTime: 25,
  servings: 4,
  difficulty: 'Intermedio',
  calories: 450,
  protein: 35,
  carbs: 40,
  fats: 12,
  fiber: 8,
  ingredients: [
    { id: '1', name: 'Pechuga de pollo', amount: '500', unit: 'g', category: 'Proteínas' },
    { id: '2', name: 'Quinoa', amount: '200', unit: 'g', category: 'Cereales' },
    { id: '3', name: 'Brócoli', amount: '300', unit: 'g', category: 'Verduras' },
    { id: '4', name: 'Zanahoria', amount: '150', unit: 'g', category: 'Verduras' },
    { id: '5', name: 'Aceite de oliva', amount: '2', unit: 'cdas', category: 'Grasas' },
    { id: '6', name: 'Sal marina', amount: '1', unit: 'cdta', category: 'Condimentos' },
    { id: '7', name: 'Pimienta negra', amount: '1/2', unit: 'cdta', category: 'Condimentos' },
    { id: '8', name: 'Limón', amount: '1', unit: 'unidad', category: 'Frutas' }
  ],
  instructions: [
    {
      step: 1,
      instruction: 'Lava y corta el pollo en trozos medianos. Sazona con sal, pimienta y un poco de aceite de oliva.',
      time: 5
    },
    {
      step: 2,
      instruction: 'Enjuaga la quinoa hasta que el agua salga clara. Cocínala en agua con sal durante 15 minutos.',
      time: 15
    },
    {
      step: 3,
      instruction: 'Corta el brócoli en floretes y la zanahoria en bastones. Cocina al vapor por 8-10 minutos.',
      time: 10
    },
    {
      step: 4,
      instruction: 'En una vaporera, cocina el pollo sazonado durante 12-15 minutos hasta que esté bien cocido.',
      time: 15
    },
    {
      step: 5,
      instruction: 'Sirve el pollo sobre la quinoa, acompaña con las verduras y rocía con limón fresco.',
      time: 2
    }
  ],
  tips: [
    'Para niños pequeños, puedes cortar el pollo en trozos más pequeños',
    'La quinoa se puede cocinar con caldo de pollo para más sabor',
    'Agrega hierbas frescas como perejil o cilantro al final'
  ],
  nutritionBenefits: [
    'Alto contenido de proteína completa',
    'Rica en fibra por la quinoa y verduras',
    'Fuente de vitaminas A y C del brócoli',
    'Libre de grasas saturadas al cocinar al vapor'
  ],
  allergens: ['Ninguno'],
  tags: ['Saludable', 'Niños', 'Alto en proteína', 'Sin gluten', 'Familiar']
};

export function RecipeDetailModal({
  recipe = sampleRecipe,
  isOpen,
  onClose,
  onSave,
  onShare,
  onAddToPlan
}: RecipeDetailModalProps) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Fácil': return 'bg-success text-white';
      case 'Intermedio': return 'bg-warning text-white';
      case 'Avanzado': return 'bg-destructive text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'Proteínas': 'bg-chart-1 text-white',
      'Verduras': 'bg-success text-white',
      'Cereales': 'bg-chart-2 text-white',
      'Frutas': 'bg-accent text-accent-foreground',
      'Grasas': 'bg-chart-3 text-chart-3-foreground',
      'Condimentos': 'bg-muted text-muted-foreground'
    };
    return colors[category] || 'bg-muted text-muted-foreground';
  };

  const totalTime = recipe.prepTime + recipe.cookTime;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto p-0">
        {/* Header con imagen */}
        <div className="relative h-64 overflow-hidden">
          <img
            src={recipe.image}
            alt={recipe.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />

          {/* Información superpuesta */}
          <div className="absolute bottom-4 left-6 right-6 text-white">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h1 className="text-2xl font-bold mb-2">{recipe.name}</h1>
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-1">
                    <Clock size={16} />
                    <span>{totalTime} min</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Users size={16} />
                    <span>{recipe.servings} porciones</span>
                  </div>
                  <Badge className={getDifficultyColor(recipe.difficulty)}>
                    {recipe.difficulty}
                  </Badge>
                </div>
              </div>

              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="text-white hover:bg-white/20"
              >
                <X size={20} />
              </Button>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Descripción */}
          <div>
            <p className="text-muted-foreground leading-relaxed">{recipe.description}</p>
          </div>

          {/* Acciones rápidas */}
          <div className="flex flex-wrap gap-3">
            <Button onClick={onAddToPlan} className="bg-primary hover:bg-primary-dark">
              <ChefHat size={16} className="mr-2" />
              Agregar al Plan
            </Button>
            <Button variant="outline" onClick={onSave}>
              <Bookmark size={16} className="mr-2" />
              Guardar
            </Button>
            <Button variant="outline" onClick={onShare}>
              <Share2 size={16} className="mr-2" />
              Compartir
            </Button>
          </div>

          {/* Información nutricional */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="text-center p-3 bg-muted rounded-lg">
              <p className="text-2xl font-bold text-primary">{recipe.calories}</p>
              <p className="text-sm text-muted-foreground">Calorías</p>
            </div>
            <div className="text-center p-3 bg-chart-1/10 rounded-lg">
              <p className="text-2xl font-bold text-chart-1">{recipe.protein}g</p>
              <p className="text-sm text-muted-foreground">Proteína</p>
            </div>
            <div className="text-center p-3 bg-chart-2/10 rounded-lg">
              <p className="text-2xl font-bold text-chart-2">{recipe.carbs}g</p>
              <p className="text-sm text-muted-foreground">Carbohidratos</p>
            </div>
            <div className="text-center p-3 bg-chart-3/10 rounded-lg">
              <p className="text-2xl font-bold text-chart-3">{recipe.fats}g</p>
              <p className="text-sm text-muted-foreground">Grasas</p>
            </div>
            <div className="text-center p-3 bg-success/10 rounded-lg">
              <p className="text-2xl font-bold text-success">{recipe.fiber}g</p>
              <p className="text-sm text-muted-foreground">Fibra</p>
            </div>
          </div>

          <Separator />

          {/* Ingredientes */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Ingredientes</h3>
            <div className="space-y-3">
              {Object.entries(
                recipe.ingredients.reduce((acc, ingredient) => {
                  if (!acc[ingredient.category]) acc[ingredient.category] = [];
                  acc[ingredient.category].push(ingredient);
                  return acc;
                }, {} as Record<string, typeof recipe.ingredients>)
              ).map(([category, ingredients]) => (
                <div key={category}>
                  <Badge className={`mb-2 ${getCategoryColor(category)}`}>
                    {category}
                  </Badge>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 ml-2">
                    {ingredients.map((ingredient) => (
                      <div key={ingredient.id} className="flex justify-between items-center">
                        <span>{ingredient.name}</span>
                        <span className="text-muted-foreground">
                          {ingredient.amount} {ingredient.unit}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <Separator />

          {/* Instrucciones */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Instrucciones</h3>
            <div className="space-y-4">
              {recipe.instructions.map((instruction) => (
                <motion.div
                  key={instruction.step}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: instruction.step * 0.1 }}
                  className="flex space-x-4 p-4 border rounded-lg"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-semibold">
                    {instruction.step}
                  </div>
                  <div className="flex-1">
                    <p className="mb-2">{instruction.instruction}</p>
                    {instruction.time && (
                      <div className="flex items-center text-sm text-muted-foreground">
                        <Clock size={14} className="mr-1" />
                        <span>{instruction.time} minutos</span>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Tips y beneficios */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-semibold mb-4">Tips de Cocina</h3>
              <div className="space-y-2">
                {recipe.tips.map((tip, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <span className="text-accent text-lg">💡</span>
                    <p className="text-sm text-muted-foreground">{tip}</p>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold mb-4">Beneficios Nutricionales</h3>
              <div className="space-y-2">
                {recipe.nutritionBenefits.map((benefit, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <span className="text-success text-lg">✅</span>
                    <p className="text-sm text-muted-foreground">{benefit}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Alérgenos y tags */}
          <div className="space-y-4">
            {recipe.allergens.length > 0 && recipe.allergens[0] !== 'Ninguno' && (
              <Alert>
                <AlertCircle size={16} />
                <AlertDescription>
                  <strong>Contiene alérgenos:</strong> {recipe.allergens.join(', ')}
                </AlertDescription>
              </Alert>
            )}

            <div>
              <h4 className="font-medium mb-2">Etiquetas:</h4>
              <div className="flex flex-wrap gap-2">
                {recipe.tags.map((tag, index) => (
                  <Badge key={index} variant="outline">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
