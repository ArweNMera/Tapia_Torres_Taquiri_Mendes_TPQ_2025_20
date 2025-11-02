"""
Configuración y setup de inyección de dependencias
"""

from typing import Optional

from src.application.services.meal_recommender_service import MealRecommenderService
from src.application.services.nutrition_calculator_service import NutritionCalculatorService
from src.domain.interfaces.recommender import (
    MacroCalculatorInterface,
    MealRecommenderInterface,
    NutritionPredictorInterface,
    WeeklyMealPlannerInterface,
)
from src.infrastructure.repositories.meal_repository import (
    InMemoryMealRepository,
    InMemoryPreferenceRepository,
)


class DIContainer:
    """
    Contenedor de inyección de dependencias
    Maneja la creación y configuración de servicios
    """

    _instance: Optional["DIContainer"] = None

    def __init__(self):
        """Inicializar contenedor"""
        self.meal_repo = InMemoryMealRepository()
        self.preference_repo = InMemoryPreferenceRepository()
        self.meal_recommender: Optional[MealRecommenderInterface] = None
        self.nutrition_predictor: Optional[NutritionPredictorInterface] = None
        self.weekly_planner: Optional[WeeklyMealPlannerInterface] = None
        self.macro_calculator: Optional[MacroCalculatorInterface] = None

    @classmethod
    def get_instance(cls) -> "DIContainer":
        """Obtener instancia singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_meal_recommender(self, recommender: MealRecommenderInterface) -> None:
        """Establecer recomendador de menús"""
        self.meal_recommender = recommender

    def set_nutrition_predictor(self, predictor: NutritionPredictorInterface) -> None:
        """Establecer predictor nutricional"""
        self.nutrition_predictor = predictor

    def set_weekly_planner(self, planner: WeeklyMealPlannerInterface) -> None:
        """Establecer planificador semanal"""
        self.weekly_planner = planner

    def set_macro_calculator(self, calculator: MacroCalculatorInterface) -> None:
        """Establecer calculador de macros"""
        self.macro_calculator = calculator

    def get_meal_recommender_service(self) -> MealRecommenderService:
        """Obtener servicio de recomendaciones"""
        return MealRecommenderService(
            recommender=self.meal_recommender,
            predictor=self.nutrition_predictor,
            planner=self.weekly_planner,
        )

    def get_nutrition_calculator_service(self) -> NutritionCalculatorService:
        """Obtener servicio de cálculos nutricionales"""
        return NutritionCalculatorService(calculator=self.macro_calculator)


# Instancia global del contenedor
di_container = DIContainer.get_instance()
