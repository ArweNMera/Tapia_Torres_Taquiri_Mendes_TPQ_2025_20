"""
🎯 Endpoints para Entrenamiento de Modelos ML
==============================================

Expone endpoints HTTP para:
- Entrenar nuevos modelos
- Obtener estado del entrenamiento
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/models", tags=["training"])


# ============================================================================
# SCHEMAS
# ============================================================================


class TrainingRequest(BaseModel):
    """Request para entrenar nuevo modelo"""

    model_name: str = Field(
        default="production_menu_recommender",
        description="Nombre del modelo a entrenar",
    )
    include_synthetic_data: bool = Field(
        default=True,
        description="Incluir datos sintéticos en entrenamiento",
    )
    validation_split: float = Field(
        default=0.2,
        ge=0.1,
        le=0.5,
        description="Porcentaje de datos para validación (10-50%)",
    )
    config_type: str = Field(
        default="default",
        description="Tipo de configuración ('default', 'production', 'development')",
    )


class TrainingResponse(BaseModel):
    """Response del entrenamiento"""

    success: bool = Field(..., description="¿Fue exitoso?")
    model_name: str = Field(..., description="Nombre del modelo")
    timestamp: str = Field(..., description="Timestamp del entrenamiento")
    message: str = Field(..., description="Mensaje de resultado")
    model_path: Optional[str] = Field(None, description="Ruta del modelo")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Métricas")
    error: Optional[str] = Field(None, description="Error si existe")


class ModelInfo(BaseModel):
    """Información de un modelo"""

    name: str
    path: str
    size_mb: float
    created_at: str
    metrics: Optional[Dict[str, Any]] = None


class TrainingStatusResponse(BaseModel):
    """Response del estado de entrenamiento"""

    success: bool = Field(..., description="¿Fue exitoso?")
    models_count: int = Field(..., description="Cantidad de modelos")
    models: List[ModelInfo] = Field(default_factory=list, description="Lista de modelos")
    message: str = Field(..., description="Mensaje")


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/train", response_model=TrainingResponse)
async def train_model(
    request: TrainingRequest,
) -> TrainingResponse:
    """
    Entrenar nuevo modelo ML

    Este endpoint inicia el pipeline completo:
    1. Extrae datos reales de BD
    2. Genera feedback sintético
    3. Entrena modelo LightGBM
    4. Calcula métricas
    5. Guarda el modelo

    ⚠️ NOTA: Toma VARIOS MINUTOS

    Ejemplo:
        POST /api/v1/models/train
        {
            "model_name": "production_menu_recommender",
            "include_synthetic_data": true,
            "validation_split": 0.2,
            "config_type": "default"
        }
    """
    try:
        from src.application.services.model_training_service import ModelTrainingService

        logger.info(f"🚀 Iniciando entrenamiento: {request.model_name}")

        # Inicializar servicio
        service = ModelTrainingService(config_type=request.config_type)

        # Ejecutar entrenamiento
        result = service.train_new_model(
            model_name=request.model_name,
            include_synthetic_data=request.include_synthetic_data,
            validation_split=request.validation_split,
            random_state=42,
        )

        if result["success"]:
            return TrainingResponse(
                success=True,
                model_name=result["model_name"],
                timestamp=result["timestamp"],
                message=f"✅ Modelo '{request.model_name}' entrenado exitosamente",
                model_path=result.get("model_path"),
                metrics=result.get("metrics", {}),
            )
        else:
            error_msg = result.get("error", "Error desconocido")
            logger.error(f"❌ Error en entrenamiento: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=f"Error entrenando modelo: {error_msg}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error inesperado en train_model: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}",
        )


@router.get("/train/status", response_model=TrainingStatusResponse)
async def get_training_status() -> TrainingStatusResponse:
    """
    Obtener estado actual de los modelos entrenados

    Retorna:
        Lista de modelos disponibles con información

    Ejemplo:
        GET /api/v1/models/train/status
    """
    try:
        from src.application.services.model_training_service import ModelTrainingService

        service = ModelTrainingService()
        status = service.get_training_status()

        if status["success"]:
            models = [
                ModelInfo(
                    name=m.get("name", "unknown"),
                    path=m.get("path", ""),
                    size_mb=m.get("size_mb", 0),
                    created_at=m.get("created_at", ""),
                    metrics=m.get("metrics"),
                )
                for m in status.get("models", [])
            ]

            return TrainingStatusResponse(
                success=True,
                models_count=status["models_count"],
                models=models,
                message=f"✅ {status['models_count']} modelo(s) disponible(s)",
            )
        else:
            return TrainingStatusResponse(
                success=False,
                models_count=0,
                models=[],
                message=f"❌ Error: {status.get('error', 'Desconocido')}",
            )

    except Exception as e:
        logger.error(f"❌ Error en get_training_status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado: {str(e)}",
        )


@router.post("/train/quick", response_model=TrainingResponse)
async def quick_train() -> TrainingResponse:
    """
    Entrenamiento rápido con configuración default

    Versión simplificada con parámetros por defecto

    Ejemplo:
        POST /api/v1/models/train/quick
    """
    try:
        request = TrainingRequest(
            model_name="production_menu_recommender",
            include_synthetic_data=True,
            validation_split=0.2,
            config_type="default",
        )

        # Usar el endpoint principal
        return await train_model(request)

    except Exception as e:
        logger.error(f"❌ Error en quick_train: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error en entrenamiento rápido: {str(e)}",
        )
