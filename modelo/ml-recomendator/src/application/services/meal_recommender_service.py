"""
Servicio de aplicación para recomendaciones de menús
Orquesta la lógica de negocio
"""

from typing import Any, Dict, List, Optional

from src.domain.interfaces.recommender import (
    MealRecommenderInterface,
    NutritionPredictorInterface,
    WeeklyMealPlannerInterface,
)


class MealRecommenderService:
    """
    Servicio de aplicación para recomendaciones
    Coordina entre repositorios, interfaces ML y lógica de negocio
    """

    def __init__(
        self,
        recommender: MealRecommenderInterface,
        predictor: Optional[NutritionPredictorInterface] = None,
        planner: Optional[WeeklyMealPlannerInterface] = None,
    ):
        """
        Inicializar servicio

        Args:
            recommender: Implementación del recomendador ML
            predictor: Opcional - Predictor de estado nutricional
            planner: Opcional - Planificador de semana
        """
        self.recommender = recommender
        self.predictor = predictor
        self.planner = planner

    def generar_recomendaciones(
        self,
        nutrition_status: str,
        allergies: List[str],
        preferences: Dict[str, float],
        num_meals: int = 7,
        include_reasons: bool = True,
    ) -> Dict[str, Any]:
        """
        Generar recomendaciones de menús

        Args:
            nutrition_status: Estado nutricional del niño
            allergies: Alergias
            preferences: Preferencias históricas
            num_meals: Número de menús a recomendar
            include_reasons: Incluir razones de recomendación

        Returns:
            Dict con recomendaciones ordenadas por relevancia
        """
        try:
            # Validaciones de entrada
            if not nutrition_status:
                raise ValueError("nutrition_status es requerido")

            if not isinstance(allergies, list):
                raise ValueError("allergies debe ser una lista")

            if not isinstance(preferences, dict):
                raise ValueError("preferences debe ser un diccionario")

            # Obtener recomendaciones del modelo
            if include_reasons:
                meals = self.recommender.get_recommendations_with_reasons(
                    nutrition_status=nutrition_status, allergies=allergies, preferences=preferences
                )
            else:
                meals = self.recommender.recommend_meals(
                    nutrition_status=nutrition_status,
                    allergies=allergies,
                    preferences=preferences,
                    num_meals=num_meals,
                )

            # Limitar al número solicitado
            meals = meals[:num_meals]

            return {
                "success": True,
                "recommendations": meals,
                "total": len(meals),
                "nutrition_status": nutrition_status,
                "allergies_count": len(allergies),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "recommendations": []}

    def generar_plan_semanal(
        self,
        nutrition_status: str,
        allergies: List[str],
        preferences: Dict[str, float],
        days: int = 7,
        include_reasons: bool = True,
    ) -> Dict[str, Any]:
        """
        Generar plan semanal de menús

        Args:
            nutrition_status: Estado nutricional
            allergies: Alergias
            preferences: Preferencias históricas
            days: Número de días a planificar
            include_reasons: Incluir razones

        Returns:
            Plan semanal estructurado por días y slots
        """
        try:
            if not self.planner:
                raise RuntimeError("Planificador no inicializado")

            # Validaciones
            if days < 1 or days > 30:
                raise ValueError("days debe estar entre 1 y 30")

            # Generar plan
            plan = self.planner.generate_weekly_plan(
                child_nutrition_status=nutrition_status,
                allergies=allergies,
                preferences=preferences,
                days=days,
                slots_per_day=3,
            )

            return {
                "success": True,
                "weekly_plan": plan.get("weekly_plan", []),
                "total_days": days,
                "nutrition_status": nutrition_status,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "weekly_plan": []}

    def predecir_estado_nutricional(
        self,
        age_months: int,
        sex: str,
        weight_kg: float,
        height_cm: float,
        additional_features: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Predecir estado nutricional del niño

        Args:
            age_months: Edad en meses
            sex: Sexo (M/F)
            weight_kg: Peso en kg
            height_cm: Altura en cm
            additional_features: Features adicionales

        Returns:
            Predicción de estado nutricional
        """
        try:
            if not self.predictor:
                raise RuntimeError("Predictor no inicializado")

            # Construir features
            features = {
                "age_months": age_months,
                "sex": sex,
                "weight_kg": weight_kg,
                "height_cm": height_cm,
            }

            if additional_features:
                features.update(additional_features)

            # Predecir
            prediction = self.predictor.predict(features)

            return {"success": True, "prediction": prediction}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_info(self) -> Dict[str, Any]:
        """Obtener información de los modelos cargados"""
        info = {
            "recommender_available": self.recommender is not None,
            "predictor_available": self.predictor is not None,
            "planner_available": self.planner is not None,
        }

        # Agregar info del recomendador si está disponible
        if self.recommender and hasattr(self.recommender, "get_model_info"):
            try:
                info["recommender_info"] = self.recommender.get_model_info()
            except:
                pass

        # Agregar info del predictor si está disponible
        if self.predictor and hasattr(self.predictor, "get_model_info"):
            try:
                info["predictor_info"] = self.predictor.get_model_info()
            except:
                pass

        return info
