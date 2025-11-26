"""
Predictor de estado nutricional usando modelo LightGBM entrenado.
Clase para usar en producción para generar predicciones.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class NutritionalPredictor:
    """
    Predictor de estado nutricional futuro.
    Carga y usa modelo LightGBM entrenado para hacer predicciones.
    """

    _instance: Optional["NutritionalPredictor"] = None

    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializar predictor.

        Args:
            model_path: Ruta al modelo entrenado (.pkl)
        """
        self.model = None
        self.feature_names = []
        self.class_names = []
        self.class_mapping = {}
        self.metrics = {}
        self.is_loaded = False

        if model_path:
            self.load_model(model_path)

    @classmethod
    def get_instance(cls, model_path: Optional[str] = None) -> "NutritionalPredictor":
        """Obtener instancia singleton."""
        if cls._instance is None:
            cls._instance = cls(model_path)
        return cls._instance

    def load_model(self, model_path: str) -> bool:
        """
        Cargar modelo desde archivo.

        Args:
            model_path: Ruta al archivo .pkl

        Returns:
            True si se cargó exitosamente
        """
        try:
            logger.info(f"📦 Cargando modelo desde: {model_path}")

            if not Path(model_path).exists():
                logger.error(f"❌ Modelo no encontrado: {model_path}")
                return False

            # Cargar payload
            payload = joblib.load(model_path)

            # Extraer componentes
            self.model = payload.get("model")
            self.feature_names = payload.get("feature_names", [])
            self.class_names = payload.get("class_names", [])
            self.class_mapping = payload.get("class_mapping", {})
            self.metrics = payload.get("metrics", {})

            if self.model is None:
                logger.error("❌ No se encontró modelo en el payload")
                return False

            self.is_loaded = True

            logger.info(f"✅ Modelo cargado exitosamente")
            logger.info(f"   Features: {len(self.feature_names)}")
            logger.info(f"   Clases: {len(self.class_names)}")
            logger.info(f"   Accuracy: {self.metrics.get('accuracy', 0):.4f}")

            return True

        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            self.is_loaded = False
            return False

    def predict_from_features(self, features: Dict[str, float]) -> Dict:
        """
        Hacer predicción desde diccionario de features.

        Args:
            features: Diccionario con los 11 features necesarios

        Returns:
            Diccionario con predicción y probabilidades
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo no cargado. Llama a load_model() primero.")

        # Validar features
        missing_features = set(self.feature_names) - set(features.keys())
        if missing_features:
            raise ValueError(f"Faltan features: {missing_features}")

        # Construir vector de features en el orden correcto
        X = np.array([[features[f] for f in self.feature_names]])

        # Predecir
        y_pred_proba = self.model.predict(X)[0]  # Probabilidades por clase
        y_pred_class = int(np.argmax(y_pred_proba))  # Clase predicha

        # Obtener nombre de clase
        clasificacion = self.class_names[y_pred_class]
        probabilidad = float(y_pred_proba[y_pred_class])

        # Calcular score de riesgo (probabilidad de clases no-normales)
        normal_idx = self.class_mapping.get("NORMAL", 3)
        score_riesgo = float(1.0 - y_pred_proba[normal_idx])

        # Probabilidades por categoría de riesgo
        desnutricion_severa_idx = self.class_mapping.get("DESNUTRICION_SEVERA", 0)
        desnutricion_moderada_idx = self.class_mapping.get("DESNUTRICION_MODERADA", 1)
        riesgo_desnutricion_idx = self.class_mapping.get("RIESGO_DESNUTRICION", 2)
        riesgo_sobrepeso_idx = self.class_mapping.get("RIESGO_SOBREPESO", 4)
        sobrepeso_idx = self.class_mapping.get("SOBREPESO", 5)
        obesidad_idx = self.class_mapping.get("OBESIDAD", 6)

        prob_severo = float(y_pred_proba[desnutricion_severa_idx] + y_pred_proba[obesidad_idx])
        prob_moderado = float(y_pred_proba[desnutricion_moderada_idx] + y_pred_proba[sobrepeso_idx])
        prob_riesgo = float(y_pred_proba[riesgo_desnutricion_idx] + y_pred_proba[riesgo_sobrepeso_idx])
        prob_normal = float(y_pred_proba[normal_idx])

        # Feature importance
        feature_importance = self.model.feature_importance(importance_type="gain")
        features_importantes = [
            (name, float(importance))
            for name, importance in zip(self.feature_names, feature_importance)
        ]
        features_importantes.sort(key=lambda x: x[1], reverse=True)

        # Construir resultado
        result = {
            "clasificacion": clasificacion,
            "probabilidad": probabilidad,
            "score_riesgo": score_riesgo,
            "probabilidades_por_clase": {
                name: float(prob)
                for name, prob in zip(self.class_names, y_pred_proba)
            },
            "prob_normal": prob_normal,
            "prob_riesgo": prob_riesgo,
            "prob_moderado": prob_moderado,
            "prob_severo": prob_severo,
            "features_importantes": features_importantes[:5],  # Top 5
            "features_usados": features,
        }

        return result

    def predict_from_dataframe(self, df: pd.DataFrame) -> List[Dict]:
        """
        Hacer predicciones para múltiples registros.

        Args:
            df: DataFrame con features

        Returns:
            Lista de predicciones
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo no cargado. Llama a load_model() primero.")

        # Validar features
        missing_features = set(self.feature_names) - set(df.columns)
        if missing_features:
            raise ValueError(f"Faltan features: {missing_features}")

        # Extraer features en orden correcto
        X = df[self.feature_names].values

        # Predecir
        y_pred_proba = self.model.predict(X)
        y_pred_classes = np.argmax(y_pred_proba, axis=1)

        # Construir resultados
        results = []
        for i in range(len(df)):
            features_dict = df.iloc[i][self.feature_names].to_dict()
            result = self.predict_from_features(features_dict)
            results.append(result)

        return results

    def get_model_info(self) -> Dict:
        """Obtener información del modelo cargado."""
        if not self.is_loaded:
            return {"loaded": False, "error": "Modelo no cargado"}

        return {
            "loaded": True,
            "feature_names": self.feature_names,
            "class_names": self.class_names,
            "num_features": len(self.feature_names),
            "num_classes": len(self.class_names),
            "metrics": {
                "accuracy": self.metrics.get("accuracy", 0),
                "f1_macro": self.metrics.get("f1_macro", 0),
                "f1_weighted": self.metrics.get("f1_weighted", 0),
            },
        }

    def explain_prediction(self, features: Dict[str, float]) -> Dict:
        """
        Explicar una predicción mostrando contribución de features.

        Args:
            features: Diccionario con features

        Returns:
            Diccionario con explicación detallada
        """
        # Hacer predicción
        prediction = self.predict_from_features(features)

        # Obtener feature importance
        feature_importance = dict(prediction["features_importantes"])

        # Identificar features más influyentes
        top_features = prediction["features_importantes"][:3]

        # Construir explicación
        explanation = {
            "clasificacion_predicha": prediction["clasificacion"],
            "confianza": prediction["probabilidad"],
            "factores_principales": [
                {
                    "feature": name,
                    "valor": features[name],
                    "importancia": importance,
                    "descripcion": self._get_feature_description(name, features[name]),
                }
                for name, importance in top_features
            ],
            "nivel_riesgo": self._get_risk_level(prediction["score_riesgo"]),
            "recomendacion": self._get_recommendation(prediction["clasificacion"]),
        }

        return explanation

    def _get_feature_description(self, feature_name: str, value: float) -> str:
        """Obtener descripción legible de un feature."""
        descriptions = {
            "age_months": f"Edad: {int(value)} meses ({value/12:.1f} años)",
            "sex_numeric": "Sexo: " + ("Masculino" if value == 1 else "Femenino"),
            "BMI": f"IMC: {value:.1f} kg/m²",
            "weight_kg": f"Peso: {value:.1f} kg",
            "height_cm": f"Talla: {value:.1f} cm",
            "bmi_velocity": f"Velocidad IMC: {value:+.2f} kg/m²/mes",
            "weight_velocity": f"Velocidad peso: {value:+.2f} kg/mes",
            "height_velocity": f"Velocidad talla: {value:+.2f} cm/mes",
            "adherence_score": f"Adherencia: {value:.0f}%",
            "allergy_count": f"Alergias: {int(value)}",
            "altitude_m": f"Altitud: {int(value)} msnm",
        }
        return descriptions.get(feature_name, f"{feature_name}: {value}")

    def _get_risk_level(self, score_riesgo: float) -> str:
        """Determinar nivel de riesgo."""
        if score_riesgo < 0.2:
            return "BAJO"
        elif score_riesgo < 0.5:
            return "MODERADO"
        else:
            return "ALTO"

    def _get_recommendation(self, clasificacion: str) -> str:
        """Obtener recomendación según clasificación."""
        recommendations = {
            "DESNUTRICION_SEVERA": "⚠️ URGENTE: Requiere intervención inmediata. Consultar con nutricionista.",
            "DESNUTRICION_MODERADA": "⚠️ IMPORTANTE: Requiere seguimiento cercano y ajuste de plan nutricional.",
            "RIESGO_DESNUTRICION": "⚠️ ATENCIÓN: Monitorear evolución y reforzar adherencia al plan.",
            "NORMAL": "✅ BIEN: Mantener plan nutricional actual y seguimiento regular.",
            "RIESGO_SOBREPESO": "⚠️ ATENCIÓN: Ajustar calorías y aumentar actividad física.",
            "SOBREPESO": "⚠️ IMPORTANTE: Requiere ajuste de plan nutricional y seguimiento.",
            "OBESIDAD": "⚠️ URGENTE: Requiere intervención especializada y seguimiento cercano.",
        }
        return recommendations.get(clasificacion, "Consultar con nutricionista.")


def main():
    """Función de prueba."""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    # Cargar modelo
    model_path = "models/nutritional_predictor.pkl"
    predictor = NutritionalPredictor(model_path)

    if not predictor.is_loaded:
        logger.error("No se pudo cargar el modelo")
        return

    # Ejemplo de predicción
    features_ejemplo = {
        "age_months": 120,  # 10 años
        "sex_numeric": 1,  # Masculino
        "BMI": 16.5,
        "weight_kg": 35.0,
        "height_cm": 145.0,
        "bmi_velocity": -0.1,  # Disminuyendo
        "weight_velocity": 0.3,
        "height_velocity": 0.5,
        "adherence_score": 65.0,  # Baja adherencia
        "allergy_count": 2,
        "altitude_m": 2400,
    }

    # Predecir
    prediction = predictor.predict_from_features(features_ejemplo)

    logger.info("\n" + "=" * 80)
    logger.info("📊 PREDICCIÓN DE EJEMPLO")
    logger.info("=" * 80)
    logger.info(f"Clasificación: {prediction['clasificacion']}")
    logger.info(f"Probabilidad: {prediction['probabilidad']:.2%}")
    logger.info(f"Score de Riesgo: {prediction['score_riesgo']:.2%}")
    logger.info("\nProbabilidades por clase:")
    for clase, prob in prediction["probabilidades_por_clase"].items():
        logger.info(f"  {clase}: {prob:.2%}")
    logger.info("\nFeatures más importantes:")
    for feature, importance in prediction["features_importantes"]:
        logger.info(f"  {feature}: {importance:.2f}")

    # Explicación
    explanation = predictor.explain_prediction(features_ejemplo)
    logger.info("\n" + "=" * 80)
    logger.info("💡 EXPLICACIÓN")
    logger.info("=" * 80)
    logger.info(f"Nivel de Riesgo: {explanation['nivel_riesgo']}")
    logger.info(f"Recomendación: {explanation['recomendacion']}")
    logger.info("\nFactores Principales:")
    for factor in explanation["factores_principales"]:
        logger.info(f"  - {factor['descripcion']} (importancia: {factor['importancia']:.2f})")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
