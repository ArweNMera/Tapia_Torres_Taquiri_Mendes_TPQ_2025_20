"""
Modelos de dominio y cargadores ML
"""

# Imports directos sin usar el __init__ para evitar circulares
try:
    from src.domain.models.model_loader import MLModelLoader, ModelMetrics, ml_loader
    from src.domain.models.ml_implementations import (
        ProductionMealRecommender,
        NutritionPredictor
    )

    __all__ = [
        "MLModelLoader",
        "ModelMetrics",
        "ml_loader",
        "ProductionMealRecommender",
        "NutritionPredictor"
    ]
except Exception as e:
    # Si falla la importación, al menos el módulo existe
    import logging
    logging.warning(f"Error importing models: {e}")
    __all__ = []
