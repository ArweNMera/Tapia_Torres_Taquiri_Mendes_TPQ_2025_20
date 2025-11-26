"""
Módulo de visualización para el modelo de predicción nutricional.
Las gráficas principales se generan desde el endpoint /api/v1/nutritional/generate_plots
Este módulo provee funciones auxiliares.
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def get_class_colors() -> Dict[str, str]:
    """Retorna colores para cada clase nutricional."""
    return {
        "DESNUTRICION_SEVERA": "#d62728",
        "DESNUTRICION_MODERADA": "#ff7f0e",
        "RIESGO_DESNUTRICION": "#ffbb78",
        "NORMAL": "#2ca02c",
        "RIESGO_SOBREPESO": "#98df8a",
        "SOBREPESO": "#1f77b4",
        "OBESIDAD": "#9467bd",
    }


def get_class_order() -> List[str]:
    """Retorna orden de clases para gráficas."""
    return [
        "DESNUTRICION_SEVERA",
        "DESNUTRICION_MODERADA",
        "RIESGO_DESNUTRICION",
        "NORMAL",
        "RIESGO_SOBREPESO",
        "SOBREPESO",
        "OBESIDAD",
    ]


def format_feature_name(name: str) -> str:
    """Formatea nombre de feature para mostrar."""
    mapping = {
        "age_months": "Edad (meses)",
        "sex_numeric": "Sexo",
        "BMI": "IMC",
        "weight_kg": "Peso (kg)",
        "height_cm": "Talla (cm)",
        "bmi_velocity": "Vel. IMC",
        "weight_velocity": "Vel. Peso",
        "height_velocity": "Vel. Talla",
        "adherence_score": "Adherencia",
        "allergy_count": "Alergias",
        "altitude_m": "Altitud",
    }
    return mapping.get(name, name)
