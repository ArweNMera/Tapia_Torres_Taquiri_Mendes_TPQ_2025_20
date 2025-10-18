/**
 * Pantalla de Plan de Comidas - Integrada con backend
 */
import { MealPlanPage } from '../../pages/MealPlanPage';

interface MealPlanScreenProps {
  onRecipeClick?: (recipeId: string) => void;
}

export function MealPlanScreen({ onRecipeClick }: MealPlanScreenProps) {
  return <MealPlanPage />;
}
