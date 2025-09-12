import { Clock, Users, Star } from 'lucide-react';
import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { ImageWithFallback } from './figma/ImageWithFallback';

interface RecipeCardProps {
  title: string;
  image: string;
  cookTime: string;
  servings: number;
  rating: number;
  difficulty: 'Fácil' | 'Medio' | 'Difícil';
  calories: number;
  onClick?: () => void;
}

export function RecipeCard({
  title,
  image,
  cookTime,
  servings,
  rating,
  difficulty,
  calories,
  onClick
}: RecipeCardProps) {
  const difficultyColors = {
    'Fácil': 'bg-green-100 text-green-800',
    'Medio': 'bg-yellow-100 text-yellow-800',
    'Difícil': 'bg-red-100 text-red-800',
  };

  return (
    <Card 
      className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow"
      onClick={onClick}
    >
      <div className="relative">
        <ImageWithFallback
          src={image}
          alt={title}
          className="w-full h-32 object-cover"
        />
        <Badge 
          className={`absolute top-2 right-2 ${difficultyColors[difficulty]}`}
        >
          {difficulty}
        </Badge>
      </div>
      
      <div className="p-3">
        <h3 className="font-semibold text-gray-800 mb-2 line-clamp-2">{title}</h3>
        
        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
          <div className="flex items-center">
            <Clock size={14} className="mr-1" />
            <span>{cookTime}</span>
          </div>
          <div className="flex items-center">
            <Users size={14} className="mr-1" />
            <span>{servings} pers.</span>
          </div>
          <div className="flex items-center">
            <Star size={14} className="mr-1 fill-yellow-400 text-yellow-400" />
            <span>{rating}</span>
          </div>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-green-600">{calories} cal</span>
          <button className="text-xs bg-green-600 text-white px-3 py-1 rounded-full hover:bg-green-700 transition-colors">
            Ver receta
          </button>
        </div>
      </div>
    </Card>
  );
}