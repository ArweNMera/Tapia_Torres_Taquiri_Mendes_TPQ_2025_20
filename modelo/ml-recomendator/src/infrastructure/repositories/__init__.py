"""
Repositorios para acceso a datos
"""

from src.infrastructure.repositories.meal_repository import (
    InMemoryMealRepository,
    InMemoryPreferenceRepository,
    MealRepository,
    PreferenceRepository,
)

__all__ = [
    "MealRepository",
    "InMemoryMealRepository",
    "PreferenceRepository",
    "InMemoryPreferenceRepository",
]
