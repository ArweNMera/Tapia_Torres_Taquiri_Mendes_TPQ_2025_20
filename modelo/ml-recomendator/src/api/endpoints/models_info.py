"""
Endpoints para información y monitoreo de modelos ML
Expone métricas de desempeño y estado de los modelos cargados
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from src.domain.models.ml_implementations import NutritionPredictor, ProductionMealRecommender
from src.domain.models.model_loader import ml_loader

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/models", tags=["models"])


@router.get("/status")
async def get_models_status() -> Dict[str, Any]:
    """
    Obtener estado de todos los modelos cargados

    Returns:
        Estado de cada modelo con métricas de desempeño
    """
    try:
        summary = ml_loader.get_model_performance_summary()

        return {
            "status": "ok",
            "timestamp": "2025-01-31",
            "models_loaded": summary["total_models_loaded"],
            "total_models": summary["total_models"],
            "models": summary["models"],
        }

    except Exception as e:
        logger.error(f"Error obteniendo estado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_models_info() -> Dict[str, Any]:
    """
    Obtener información detallada de todos los modelos

    Returns:
        Información completa de modelos y métricas
    """
    try:
        info = ml_loader.get_all_models_info()

        return {"status": "ok", "message": "Información detallada de modelos ML", "models": info}

    except Exception as e:
        logger.error(f"Error obteniendo info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommender/performance")
async def get_recommender_performance() -> Dict[str, Any]:
    """
    Obtener métricas de desempeño del recomendador

    Returns:
        Porcentaje de acierto y NDCG scores
    """
    try:
        # Cargar o usar el recomendador cargado
        recommender = ProductionMealRecommender(ml_loader)
        model_info = recommender.get_model_info()

        if "metrics" in model_info:
            metrics = model_info["metrics"]
            return {
                "status": "ok",
                "model": "ProductionMealRecommender",
                "performance": {
                    "accuracy": metrics.get("accuracy_percentage", 0),
                    "ndcg_metrics": metrics.get("ndcg_metrics", {}),
                    "training_info": metrics.get("training_metadata", {}),
                },
            }
        else:
            return {
                "status": "model_not_loaded",
                "model": "ProductionMealRecommender",
                "performance": None,
            }

    except Exception as e:
        logger.error(f"Error obteniendo desempeño: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictor/performance")
async def get_predictor_performance() -> Dict[str, Any]:
    """
    Obtener métricas de desempeño del predictor nutricional

    Returns:
        Información del modelo predictor
    """
    try:
        predictor = NutritionPredictor(ml_loader)
        info = predictor.get_model_info()

        return {"status": "ok", "model": "NutritionPredictor", "info": info}

    except Exception as e:
        logger.error(f"Error obteniendo info predictor: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load/{model_name}")
async def load_model(model_name: str) -> Dict[str, Any]:
    """
    Cargar un modelo específico

    Args:
        model_name: Nombre del modelo a cargar

    Returns:
        Status de carga y información del modelo
    """
    try:
        model, metrics = ml_loader.load_model(model_name, use_cache=False)

        if model:
            return {"status": "loaded", "model": model_name, "metrics": metrics.to_dict()}
        else:
            return {
                "status": "not_found",
                "model": model_name,
                "error": f"Modelo no encontrado: {model_name}",
            }

    except Exception as e:
        logger.error(f"Error cargando modelo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_models_summary() -> Dict[str, Any]:
    """
    Obtener resumen visual de todos los modelos y su desempeño

    Returns:
        Resumen consolidado con porcentajes de acierto
    """
    try:
        # Cargar recomendador
        recommender = ProductionMealRecommender(ml_loader)
        recommender_info = recommender.get_model_info()

        # Cargar predictor
        predictor = NutritionPredictor(ml_loader)
        predictor_info = predictor.get_model_info()

        summary = {
            "status": "ok",
            "timestamp": "2025-01-31",
            "models": {
                "recommender": {
                    "name": "Production Menu Recommender",
                    "type": "Learning-to-Rank (LightGBM)",
                    "status": "loaded" if recommender.model else "not_loaded",
                    "metrics": recommender_info.get("metrics", {}) if recommender.model else {},
                    "description": "Recomienda menús basado en estado nutricional, alergias y preferencias",
                },
                "predictor": {
                    "name": "Nutrition Predictor",
                    "type": "Classification",
                    "status": "loaded",
                    "info": predictor_info,
                    "description": "Predice estado nutricional del niño basado en edad, peso y altura",
                },
            },
            "overall": {
                "total_models": 2,
                "loaded": 2 if recommender.model else 1,
                "ready": "yes" if recommender.model else "partial",
            },
        }

        return summary

    except Exception as e:
        logger.error(f"Error generando resumen: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
