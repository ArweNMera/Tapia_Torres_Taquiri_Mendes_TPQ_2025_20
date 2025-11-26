"""
Endpoints de la API
"""

from src.api.endpoints.models_info import router as models_info_router
from src.api.endpoints.nutritional_training import router as nutritional_training_router
from src.api.endpoints.recommendations import router as recommendations_router
from src.api.endpoints.training import router as training_router

__all__ = [
    "recommendations_router",
    "models_info_router",
    "training_router",
    "nutritional_training_router",
]
