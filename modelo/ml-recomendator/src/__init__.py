"""
ML Nutrition Recommender
Recomendador de menús inteligente integrado con predictor nutricional
"""

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

__version__ = "1.0.0"
__author__ = "ML Team"

__all__ = [
    # Interfaces
    "NutritionPredictorInterface",
    "MealRecommenderInterface",
    "WeeklyMealPlannerInterface",
    "MacroCalculatorInterface",
    # Services
    "MealRecommenderService",
    "NutritionCalculatorService",
    # Repositories
    "InMemoryMealRepository",
    "InMemoryPreferenceRepository",
]
