"""
Repositorios para acceso a datos
Implementan el patrón Repository
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class MealRepository(ABC):
    """
    Interfaz base para acceso a datos de comidas
    """

    @abstractmethod
    def find_by_id(self, meal_id: str) -> Optional[Dict[str, Any]]:
        """Encontrar comida por ID"""
        pass

    @abstractmethod
    def find_by_nutrition_status(
        self, nutrition_status: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Encontrar comidas recomendadas para un estado nutricional"""
        pass

    @abstractmethod
    def find_safe_for_allergies(
        self, allergies: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Encontrar comidas sin los alérgenos indicados"""
        pass

    @abstractmethod
    def find_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener todas las comidas"""
        pass

    @abstractmethod
    def get_meal_count(self) -> int:
        """Contar total de comidas disponibles"""
        pass


class InMemoryMealRepository(MealRepository):
    """
    Implementación en memoria del repositorio de comidas
    Útil para desarrollo y testing
    """

    # Base de datos en memoria (en producción vendría de MySQL)
    _meals_db = {
        "meal_001": {
            "id": "meal_001",
            "name": "Arroz con pollo",
            "calories": 350,
            "protein_g": 25,
            "carbs_g": 40,
            "fat_g": 8,
            "allergens": [],
            "min_age_months": 12,
            "max_age_months": 240,
            "nutrition_level": "NORMAL",
        },
        "meal_002": {
            "id": "meal_002",
            "name": "Papilla de quinua",
            "calories": 200,
            "protein_g": 8,
            "carbs_g": 35,
            "fat_g": 3,
            "allergens": [],
            "min_age_months": 6,
            "max_age_months": 24,
            "nutrition_level": "DESNUTRICION",
        },
        "meal_003": {
            "id": "meal_003",
            "name": "Caldo con verduras",
            "calories": 150,
            "protein_g": 12,
            "carbs_g": 20,
            "fat_g": 2,
            "allergens": [],
            "min_age_months": 6,
            "max_age_months": 240,
            "nutrition_level": "DESNUTRICION",
        },
    }

    def __init__(self):
        """Inicializar repositorio"""
        self._cache = dict(self._meals_db)

    def find_by_id(self, meal_id: str) -> Optional[Dict[str, Any]]:
        """Encontrar comida por ID"""
        return self._cache.get(meal_id)

    def find_by_nutrition_status(
        self, nutrition_status: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Encontrar comidas para estado nutricional"""
        results = [
            meal for meal in self._cache.values() if meal.get("nutrition_level") == nutrition_status
        ]
        return results[:limit]

    def find_safe_for_allergies(
        self, allergies: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Encontrar comidas sin alérgenos"""
        results = []
        for meal in self._cache.values():
            meal_allergens = set(meal.get("allergens", []))
            allergies_set = set(allergies)

            if not meal_allergens.intersection(allergies_set):
                results.append(meal)

        return results[:limit]

    def find_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener todas las comidas"""
        return list(self._cache.values())[:limit]

    def get_meal_count(self) -> int:
        """Contar comidas"""
        return len(self._cache)

    def add_meal(self, meal_id: str, meal_data: Dict[str, Any]) -> bool:
        """Agregar comida (solo para testing)"""
        self._cache[meal_id] = meal_data
        return True

    def remove_meal(self, meal_id: str) -> bool:
        """Remover comida (solo para testing)"""
        if meal_id in self._cache:
            del self._cache[meal_id]
            return True
        return False


class PreferenceRepository(ABC):
    """
    Interfaz base para acceso a datos de preferencias
    """

    @abstractmethod
    def save_preference(self, child_id: str, meal_id: str, rating: float) -> bool:
        """Guardar preferencia del niño"""
        pass

    @abstractmethod
    def get_preferences(self, child_id: str) -> Dict[str, float]:
        """Obtener todas las preferencias del niño"""
        pass

    @abstractmethod
    def get_preference(self, child_id: str, meal_id: str) -> Optional[float]:
        """Obtener calificación específica"""
        pass

    @abstractmethod
    def delete_preference(self, child_id: str, meal_id: str) -> bool:
        """Eliminar preferencia"""
        pass


class InMemoryPreferenceRepository(PreferenceRepository):
    """
    Implementación en memoria del repositorio de preferencias
    Útil para desarrollo y testing
    """

    def __init__(self):
        """Inicializar repositorio"""
        self._preferences: Dict[str, Dict[str, float]] = {}

    def save_preference(self, child_id: str, meal_id: str, rating: float) -> bool:
        """Guardar preferencia"""
        if child_id not in self._preferences:
            self._preferences[child_id] = {}

        if 0 <= rating <= 5:
            self._preferences[child_id][meal_id] = rating
            return True
        return False

    def get_preferences(self, child_id: str) -> Dict[str, float]:
        """Obtener preferencias del niño"""
        return self._preferences.get(child_id, {})

    def get_preference(self, child_id: str, meal_id: str) -> Optional[float]:
        """Obtener preferencia específica"""
        return self._preferences.get(child_id, {}).get(meal_id)

    def delete_preference(self, child_id: str, meal_id: str) -> bool:
        """Eliminar preferencia"""
        if child_id in self._preferences and meal_id in self._preferences[child_id]:
            del self._preferences[child_id][meal_id]
            return True
        return False
