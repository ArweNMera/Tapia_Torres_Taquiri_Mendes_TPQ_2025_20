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


@router.get("/models/list-files")
async def list_model_files():
    """Endpoint temporal para ver qué archivos existen"""
    from pathlib import Path

    models_dir = Path(__file__).parent.parent.parent.parent / "models"

    if not models_dir.exists():
        return {"error": "Directorio no existe", "path": str(models_dir)}

    pkl_files = [f.name for f in models_dir.glob("*.pkl")]
    meta_files = [f.name for f in models_dir.glob("*_meta.json")]

    return {
        "models_dir": str(models_dir),
        "pkl_files": pkl_files,
        "meta_files": meta_files,
        "pkl_count": len(pkl_files),
        "meta_count": len(meta_files),
    }


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


class DeleteModelsRequest(BaseModel):
    """Request para eliminar modelos por timestamps"""

    timestamps: List[str] = Field(
        ...,
        description="Lista de timestamps de modelos a eliminar (formato: YYYY-MM-DDTHH:MM:SS)",
        example=["2025-11-06T05:23:06", "2025-11-06T05:39:04"],
    )


class DeleteModelsResponse(BaseModel):
    """Response de eliminación de modelos"""

    success: bool = Field(..., description="¿Fue exitoso?")
    deleted_count: int = Field(..., description="Cantidad de modelos eliminados")
    remaining_count: int = Field(..., description="Cantidad de modelos restantes")
    deleted_models: List[str] = Field(default_factory=list, description="Modelos eliminados")
    message: str = Field(..., description="Mensaje de resultado")


@router.delete("/models/delete", response_model=DeleteModelsResponse)
async def delete_models(
    request: DeleteModelsRequest,
) -> DeleteModelsResponse:
    """
    Eliminar modelos específicos por timestamp

    Permite eliminar modelos defectuosos o no deseados.

    ⚠️ PRECAUCIÓN: Esta acción es irreversible

    Ejemplo:
        DELETE /api/v1/models/models/delete
        {
            "timestamps": [
                "2025-11-06T05:23:06",
                "2025-11-06T05:39:04",
                "2025-11-06T05:44:56"
            ]
        }
    """
    try:
        from datetime import datetime
        from pathlib import Path

        logger.info(f"🗑️  Iniciando eliminación de {len(request.timestamps)} modelo(s)")
        logger.info(f"📋 Timestamps a eliminar: {request.timestamps}")

        models_dir = Path(__file__).parent.parent.parent.parent / "models"

        if not models_dir.exists():
            raise HTTPException(
                status_code=404,
                detail="Directorio de modelos no encontrado",
            )

        # Obtener todos los archivos .pkl y _meta.json
        all_models = list(models_dir.glob("*.pkl"))
        all_metadata = list(models_dir.glob("*_meta.json"))
        initial_count = len(all_metadata)

        # LOG: Mostrar archivos encontrados
        logger.info(f"📂 Archivos .pkl encontrados: {[f.name for f in all_models]}")
        logger.info(f"📂 Archivos _meta.json encontrados: {[f.name for f in all_metadata]}")

        deleted_models = []
        deleted_count = 0

        # Para cada timestamp, buscar y eliminar el modelo Y su metadata
        for timestamp in request.timestamps:
            try:
                # Convertir timestamp a formato de archivo: 20251106_052306
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                file_pattern = dt.strftime("%Y%m%d_%H%M%S")

                # Buscar archivos .pkl que coincidan
                matching_models = [f for f in all_models if file_pattern in f.name]

                # Buscar archivos _meta.json que coincidan
                matching_metadata = [f for f in all_metadata if file_pattern in f.name]

                # Eliminar modelos .pkl
                for model_file in matching_models:
                    logger.info(f"🗑️  Eliminando modelo: {model_file.name}")
                    model_file.unlink()
                    deleted_models.append(model_file.name)
                    deleted_count += 1

                # Eliminar archivos metadata _meta.json
                for meta_file in matching_metadata:
                    logger.info(f"🗑️  Eliminando metadata: {meta_file.name}")
                    meta_file.unlink()
                    deleted_models.append(meta_file.name)
                    deleted_count += 1

            except Exception as e:
                logger.warning(f"⚠️  No se pudo eliminar modelo con timestamp {timestamp}: {e}")

        # Contar modelos restantes (basado en metadata)
        remaining_models = list(models_dir.glob("*_meta.json"))
        remaining_count = len(remaining_models)

        logger.info(f"✅ Eliminación completada: {deleted_count} modelo(s) eliminado(s)")

        return DeleteModelsResponse(
            success=True,
            deleted_count=deleted_count,
            remaining_count=remaining_count,
            deleted_models=deleted_models,
            message=f"✅ {deleted_count} modelo(s) eliminado(s). {remaining_count} modelo(s) restante(s)",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en delete_models: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando modelos: {str(e)}",
        )
