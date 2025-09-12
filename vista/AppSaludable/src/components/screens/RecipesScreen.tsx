import { useState } from 'react';
import { Search, Filter, Clock, Star } from 'lucide-react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { RecipeCard } from '../RecipeCard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';

interface RecipesScreenProps {
  onRecipeClick?: (recipeId: string) => void;
}

export function RecipesScreen({ onRecipeClick }: RecipesScreenProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', label: 'Todas', count: 24 },
    { id: 'breakfast', label: 'Desayuno', count: 8 },
    { id: 'lunch', label: 'Almuerzo', count: 10 },
    { id: 'snack', label: 'Merienda', count: 6 }
  ];

  const recipes = [
    {
      id: '1',
      title: 'Puré de calabaza con pollo',
      image: 'https://images.unsplash.com/photo-1583506955278-b24cb3b0c9b5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2xvcmZ1bCUyMHZlZ2V0YWJsZXMlMjBmcnVpdHMlMjBraWRzJTIwbWVhbHxlbnwxfHx8fDE3NTcyMjA0NTB8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      cookTime: '20 min',
      servings: 2,
      rating: 4.8,
      difficulty: 'Fácil' as const,
      calories: 180,
      category: 'lunch'
    },
    {
      id: '2',
      title: 'Smoothie de frutas y avena',
      image: 'https://images.unsplash.com/photo-1744028982670-67ca067bedfa?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb29raW5nJTIwcmVjaXBlJTIwaGVhbHRoeSUyMGluZ3JlZGllbnRzfGVufDF8fHx8MTc1NzIyMDQ1MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      cookTime: '5 min',
      servings: 1,
      rating: 4.9,
      difficulty: 'Fácil' as const,
      calories: 220,
      category: 'breakfast'
    },
    {
      id: '3',
      title: 'Papilla de plátano y avena',
      image: 'https://images.unsplash.com/photo-1670698783848-5cf695a1b308?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFsdGh5JTIwZm9vZCUyMGZhbWlseSUyMGNoaWxkcmVuJTIwbnV0cml0aW9ufGVufDF8fHx8MTc1NzIyMDQ1MHww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      cookTime: '10 min',
      servings: 1,
      rating: 4.7,
      difficulty: 'Fácil' as const,
      calories: 150,
      category: 'breakfast'
    },
    {
      id: '4',
      title: 'Pescado al vapor con verduras',
      image: 'https://images.unsplash.com/photo-1583506955278-b24cb3b0c9b5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2xvcmZ1bCUyMHZlZ2V0YWJsZXMlMjBmcnVpdHMlMjBraWRzJTIwbWVhbHxlbnwxfHx8fDE3NTcyMjA0NTB8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      cookTime: '25 min',
      servings: 3,
      rating: 4.6,
      difficulty: 'Medio' as const,
      calories: 200,
      category: 'lunch'
    },
    {
      id: '5',
      title: 'Galletas de avena sin azúcar',
      image: 'https://images.unsplash.com/photo-1744028982670-67ca067bedfa?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb29raW5nJTIwcmVjaXBlJTIwaGVhbHRoeSUyMGluZ3JlZGllbnRzfGVufDF8fHx8MTc1NzIyMDQ1MXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      cookTime: '30 min',
      servings: 12,
      rating: 4.5,
      difficulty: 'Medio' as const,
      calories: 80,
      category: 'snack'
    },
    {
      id: '6',
      title: 'Compota de manzana casera',
      image: 'https://images.unsplash.com/photo-1670698783848-5cf695a1b308?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFsdGh5JTIwZm9vZCUyMGZhbWlseSUyMGNoaWxkcmVuJTIwbnV0cml0aW9ufGVufDF8fHx8MTc1NzIyMDQ1MHww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral',
      cookTime: '15 min',
      servings: 4,
      rating: 4.8,
      difficulty: 'Fácil' as const,
      calories: 60,
      category: 'snack'
    }
  ];

  const filteredRecipes = recipes.filter(recipe => {
    const matchesSearch = recipe.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || recipe.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-800 mb-2">Recetas Saludables</h1>
        <p className="text-gray-600">Encuentra la alimentación perfecta para tu familia</p>
      </div>

      {/* Search and Filter */}
      <div className="space-y-3">
        <div className="relative">
          <Search size={18} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          <Input
            placeholder="Buscar recetas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 overflow-x-auto">
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedCategory(category.id)}
                className={`whitespace-nowrap ${
                  selectedCategory === category.id 
                    ? 'bg-green-600 text-white' 
                    : 'text-gray-600 border-gray-300'
                }`}
              >
                {category.label} ({category.count})
              </Button>
            ))}
          </div>
          <Button variant="outline" size="sm">
            <Filter size={16} className="mr-1" />
            Filtros
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <Clock size={20} className="mx-auto text-green-600 mb-1" />
          <p className="text-xs text-gray-600">Promedio</p>
          <p className="text-sm font-semibold text-gray-800">18 min</p>
        </div>
        <div className="text-center p-3 bg-orange-50 rounded-lg">
          <Star size={20} className="mx-auto text-orange-600 mb-1" />
          <p className="text-xs text-gray-600">Calificación</p>
          <p className="text-sm font-semibold text-gray-800">4.7 ⭐</p>
        </div>
        <div className="text-center p-3 bg-yellow-50 rounded-lg">
          <span className="block text-yellow-600 mb-1">🍎</span>
          <p className="text-xs text-gray-600">Saludables</p>
          <p className="text-sm font-semibold text-gray-800">100%</p>
        </div>
      </div>

      {/* Recipe Tabs */}
      <Tabs defaultValue="grid" className="w-full">
        <TabsList className="grid w-full grid-cols-2 mb-4">
          <TabsTrigger value="grid">Vista en Tarjetas</TabsTrigger>
          <TabsTrigger value="list">Vista en Lista</TabsTrigger>
        </TabsList>
        
        <TabsContent value="grid">
          <div className="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 lg:gap-4">
            {filteredRecipes.map((recipe) => (
              <RecipeCard
                key={recipe.id}
                {...recipe}
                onClick={() => onRecipeClick?.(recipe.id)}
              />
            ))}
          </div>
        </TabsContent>
        
        <TabsContent value="list">
          <div className="space-y-3">
            {filteredRecipes.map((recipe) => (
              <div 
                key={recipe.id}
                onClick={() => onRecipeClick?.(recipe.id)}
                className="flex items-center p-3 bg-white rounded-lg border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
              >
                <img 
                  src={recipe.image} 
                  alt={recipe.title}
                  className="w-16 h-16 rounded-lg object-cover mr-3"
                />
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-800 mb-1">{recipe.title}</h3>
                  <div className="flex items-center space-x-3 text-xs text-gray-600">
                    <span className="flex items-center">
                      <Clock size={12} className="mr-1" />
                      {recipe.cookTime}
                    </span>
                    <span>{recipe.calories} cal</span>
                    <Badge className="text-xs">{recipe.difficulty}</Badge>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center text-yellow-500 mb-1">
                    <Star size={14} className="fill-current" />
                    <span className="text-xs ml-1">{recipe.rating}</span>
                  </div>
                  <span className="text-xs text-gray-500">{recipe.servings} pers.</span>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* No Results */}
      {filteredRecipes.length === 0 && (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">🔍</div>
          <h3 className="font-semibold text-gray-800 mb-1">No se encontraron recetas</h3>
          <p className="text-gray-600 text-sm">Intenta con otros términos de búsqueda</p>
        </div>
      )}
    </div>
  );
}