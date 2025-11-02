"""
Capa de infraestructura
Contiene repositorios, adaptadores y acceso a BD/APIs externas
"""

from src.infrastructure.repositories import (
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
