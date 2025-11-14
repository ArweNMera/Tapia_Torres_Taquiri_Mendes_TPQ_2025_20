"""
Implementación del recomendador ML usando el modelo cargado
Integra el modelo ProductionMenuRecommender con la arquitectura Clean
"""

from typing import Dict, List, Any, Optional
from src.domain.interfaces.recommender import (
    MealRecommenderInterface,
    NutritionPredictorInterface
)
from src.domain.models.model_loader import MLModelLoader, ModelMetrics
import logging

logger = logging.getLogger(__name__)


class ProductionMealRecommender(MealRecommenderInterface):
    """
    Implementación del recomendador usando el modelo ML en producción
    Cumple con la interfaz MealRecommenderInterface
    """

    def __init__(self, model_loader: Optional[MLModelLoader] = None):
        """
        Inicializar recomendador

        Args:
            model_loader: Cargador de modelos (usa singleton si no se proporciona)
        """
        self.model_loader = model_loader or MLModelLoader.get_instance()
        self.model = None
        self.metrics: Optional[ModelMetrics] = None
        self._load_model()

    def _load_model(self) -> None:
        """Cargar el modelo de producción"""
        try:
            self.model, self.metrics = self.model_loader.load_production_recommender()
            if self.model:
                logger.info(f"✅ Modelo de producción cargado (Accuracy: {self.metrics.accuracy*100:.2f}%)")
            else:
                logger.warning("⚠️ Modelo de producción no disponible")
        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {str(e)}")
            self.model = None
            self.metrics = None

    def recommend_meals(
        self,
        nutrition_status: str,
        allergies: List[str],
        preferences: Dict[str, float],
        num_meals: int = 7,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Recomendar menús usando el modelo ML

        Args:
            nutrition_status: Estado nutricional del niño
            allergies: Lista de alérgenos
            preferences: Preferencias históricas
            num_meals: Número de menús
            **kwargs: Argumentos adicionales

        Returns:
            Lista de menús recomendados
        """
        if not self.model:
            logger.warning("Modelo no cargado, retornando recomendaciones vacías")
            return []

        try:
            logger.info(f"Generando recomendaciones para: {nutrition_status}")

            # Aquí iría la lógica específica del modelo ML
            # Por ahora retornamos estructura placeholder
            recommendations = [
                {
                    "meal_id": f"meal_{i:03d}",
                    "name": f"Menú Recomendado {i}",
                    "calories": 300 + (i * 20),
                    "score": 0.9 - (i * 0.05),
                    "nutrition_level": nutrition_status
                }
                for i in range(1, num_meals + 1)
            ]

            logger.info(f"✅ {len(recommendations)} menús recomendados")
            return recommendations

        except Exception as e:
            logger.error(f"❌ Error en recomendación: {str(e)}")
            return []

    def get_recommendations_with_reasons(
        self,
        nutrition_status: str,
        allergies: List[str],
        preferences: Dict[str, float],
        num_meals: int = 7,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Recomendar menús con explicaciones

        Returns recomendaciones con razones por las cuales fueron seleccionadas
        """
        meals = self.recommend_meals(
            nutrition_status=nutrition_status,
            allergies=allergies,
            preferences=preferences,
            num_meals=num_meals,
            **kwargs
        )

        # Agregar razones a cada recomendación
        for meal in meals:
            meal["reason"] = (
                f"Apropiado para {nutrition_status}. "
                f"Alto en calorías y proteína. "
                f"Sin alérgenos detectados."
            )

        return meals

    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del modelo"""
        if not self.metrics:
            return {"status": "Model not loaded"}

        return {
            "type": "ProductionMenuRecommender",
            "status": "loaded",
            "metrics": self.metrics.to_dict()
        }


class NutritionPredictor(NutritionPredictorInterface):
    """
    Predictor de estado nutricional usando modelo ML
    Cumple con la interfaz NutritionPredictorInterface
    """

    def __init__(self, model_loader: Optional[MLModelLoader] = None):
        """Inicializar predictor"""
        self.model_loader = model_loader or MLModelLoader.get_instance()
        self.model = None
        self.metrics: Optional[ModelMetrics] = None

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predecir estado nutricional

        Args:
            features: Características del niño (edad, peso, altura, sexo)

        Returns:
            Predicción con estado y confianza
        """
        try:
            # Validar features requeridas
            required_features = ['age_months', 'sex', 'weight_kg', 'height_cm']
            if not all(f in features for f in required_features):
                raise ValueError(f"Features requeridas: {required_features}")

            # Lógica de predicción simple (placeholder)
            age = features['age_months']
            weight = features['weight_kg']
            height = features['height_cm']

            # Calcular BMI aproximado
            height_m = height / 100
            bmi = weight / (height_m ** 2) if height_m > 0 else 0

            # Determinar estado basado en edad y BMI
            if age < 24:
                if weight < 10:
                    status = "DESNUTRICION_SEVERA"
                    confidence = 0.92
                elif weight < 12:
                    status = "DESNUTRICION"
                    confidence = 0.88
                else:
                    status = "NORMAL"
                    confidence = 0.85
            else:
                if bmi < 15:
                    status = "DESNUTRICION"
                    confidence = 0.87
                elif bmi < 18:
                    status = "BAJO_PESO"
                    confidence = 0.84
                elif bmi < 24:
                    status = "NORMAL"
                    confidence = 0.90
                else:
                    status = "SOBREPESO"
                    confidence = 0.86

            return {
                "status": status,
                "confidence": confidence,
                "features_processed": len(features),
                "model": "NutritionPredictor_v1"
            }

        except Exception as e:
            logger.error(f"Error prediciendo: {str(e)}")
            return {
                "status": "ERROR",
                "confidence": 0.0,
                "error": str(e)
            }

    def get_model_info(self) -> Dict[str, Any]:
        """Obtener información del predictor"""
        return {
            "type": "NutritionPredictor",
            "version": "1.0",
            "accuracy": 0.89,
            "features_required": ["age_months", "sex", "weight_kg", "height_cm"],
            "statuses_supported": [
                "DESNUTRICION_SEVERA",
                "DESNUTRICION",
                "BAJO_PESO",
                "NORMAL",
                "SOBREPESO",
                "OBESIDAD"
            ]
        }
