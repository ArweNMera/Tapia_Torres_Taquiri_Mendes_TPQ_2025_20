"""
Interfaces de dominio para el recomendador de menús
Define los contratos que deben cumplir los modelos ML
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class NutritionPredictorInterface(ABC):
    """Interface para predicción de estado nutricional"""

    @abstractmethod
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predecir categoría nutricional basada en features

        Args:
            features: Dict con features antropométricos y contextuales

        Returns:
            Dict con predicción y confianza
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo (versión, accuracy, etc)"""
        pass


class MealRecommenderInterface(ABC):
    """Interface para recomendador de menús"""

    @abstractmethod
    def recommend_meals(
        self,
        nutrition_status: str,
        allergies: List[str],
        preferences: Dict[str, float],
        num_meals: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Recomendar menús personalizados

        Args:
            nutrition_status: Estado nutricional (DESNUTRICION_SEVERA, NORMAL, OBESIDAD, etc)
            allergies: Lista de alergias del niño
            preferences: Dict con preferencias históricas (menu_id -> rating)
            num_meals: Número de menús a recomendar

        Returns:
            Lista de menús recomendados ordenados por relevancia
        """
        pass

    @abstractmethod
    def get_recommendations_with_reasons(
        self, nutrition_status: str, allergies: List[str], preferences: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Recomendar menús CON RAZONES (por qué se recomienda)

        Returns:
            Lista con formato: {
                "menu_id": int,
                "nombre": str,
                "razones": ["Alta en fibra", "Preferencias previas positivas"],
                "score": float
            }
        """
        pass


class WeeklyMealPlannerInterface(ABC):
    """Interface para planificador de plan semanal"""

    @abstractmethod
    def generate_weekly_plan(
        self,
        child_nutrition_status: str,
        allergies: List[str],
        preferences: Dict[str, float],
        days: int = 7,
        slots_per_day: int = 3,
    ) -> Dict[str, Any]:
        """
        Generar plan semanal de menús

        Args:
            child_nutrition_status: Estado nutricional actual
            allergies: Alergias del niño
            preferences: Preferencias históricas
            days: Número de días a planificar
            slots_per_day: Número de slots por día (desayuno, almuerzo, etc)

        Returns:
            Dict con estructura:
            {
                "weekly_plan": [
                    {
                        "day": "Lunes",
                        "slots": [
                            {
                                "slot": "Desayuno",
                                "menu": {...},
                                "reasons": [...]
                            }
                        ]
                    }
                ],
                "status": "success"
            }
        """
        pass


class MacroCalculatorInterface(ABC):
    """Interface para cálculo de macronutrientes"""

    @abstractmethod
    def calculate_daily_requirements(
        self, age_months: int, weight_kg: float, nutrition_status: str
    ) -> Dict[str, float]:
        """Calcular requerimientos diarios basado en perfil del niño"""
        pass

    @abstractmethod
    def calculate_meal_macros(self, menu_id: int) -> Dict[str, float]:
        """Calcular macronutrientes de un menú específico"""
        pass
