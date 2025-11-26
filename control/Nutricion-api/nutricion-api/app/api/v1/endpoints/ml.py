from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.ninos_repo import NinosRepository


def summarize_with_llm(features, scores):
    return None


def format_recommender_prompt(features, scores):
    return "Análisis nutricional disponible vía API ML"


router = APIRouter()


class SummaryRequest(BaseModel):
    features: dict[str, Any]
    scores: dict[str, float]
    prefer_llm: bool = True


class SummaryResponse(BaseModel):
    text: str
    used_llm: bool


@router.post("/summary", response_model=SummaryResponse)
def summarize(req: SummaryRequest) -> SummaryResponse:
    # First try LLM if preferred
    used_llm = False
    text: str | None = None
    if req.prefer_llm:
        try:
            text = summarize_with_llm(req.features, req.scores)
            used_llm = text is not None
        except Exception:
            # Fall back silently to offline
            text = None
            used_llm = False
    if not text:
        try:
            text = format_recommender_prompt(req.features, req.scores)
        except Exception as e:  # Should not happen; guard anyway
            raise HTTPException(status_code=500, detail=f"No se pudo generar resumen: {e}")
    return SummaryResponse(text=text, used_llm=used_llm)


class AnalisisNutricionalRequest(BaseModel):
    """Request para análisis nutricional."""

    nin_id: int = Field(description="ID del niño")
    peso_kg: float | None = Field(None, description="Peso en kg (opcional)")
    talla_cm: float | None = Field(None, description="Talla en cm (opcional)")
    fecha_medicion: str | None = Field(None, description="Fecha de medición (YYYY-MM-DD)")


class AnalisisNutricionalResponse(BaseModel):
    """Response de análisis nutricional."""

    nin_id: int
    ant_id: int | None
    fecha: str | None
    edad_meses: int | None
    peso_kg: float | None
    talla_cm: float | None
    imc: float | None
    diagnostico: str
    z_score_imc: float | None
    percentil: float | None
    nivel_riesgo: str
    riesgo_porcentaje: float | None
    recomendaciones: list[dict[str, str]]
    fuente: str = "procedimiento_almacenado"


@router.post("/analisis_nutricional", response_model=AnalisisNutricionalResponse)
async def analisis_nutricional(
    req: AnalisisNutricionalRequest, db: Session = Depends(get_db)
) -> AnalisisNutricionalResponse:
    """
    Análisis nutricional completo basado en el procedimiento almacenado sp_evaluar_estado_nutricional.
    Permite registrar opcionalmente una nueva medición antropométrica antes de evaluar.
    """
    repo = NinosRepository(db)

    nino = repo.obtener_nino(req.nin_id)
    if not nino:
        raise HTTPException(status_code=404, detail=f"Niño con ID {req.nin_id} no encontrado")

    if req.peso_kg is not None and req.talla_cm is not None:
        try:
            repo.agregar_antropometria(
                req.nin_id,
                {
                    "ant_peso_kg": req.peso_kg,
                    "ant_talla_cm": req.talla_cm,
                    "ant_fecha": req.fecha_medicion,
                },
            )
        except Exception as exc:
            raise HTTPException(
                status_code=400, detail=f"No se pudo registrar la antropometría: {exc}"
            )

    try:
        estado = repo.evaluar_estado_nutricional(req.nin_id)
        if not estado:
            raise HTTPException(
                status_code=400, detail="No fue posible obtener la evaluación nutricional"
            )

        return AnalisisNutricionalResponse(
            nin_id=estado.get("nin_id", req.nin_id),
            ant_id=estado.get("ant_id"),
            fecha=estado.get("ant_fecha"),
            edad_meses=estado.get("en_edad_meses"),
            peso_kg=estado.get("peso_kg"),
            talla_cm=estado.get("talla_cm"),
            imc=estado.get("imc_calculado"),
            diagnostico=estado.get("en_clasificacion", "NORMAL"),
            z_score_imc=estado.get("en_z_score_imc"),
            percentil=estado.get("percentil_calculado"),
            nivel_riesgo=estado.get("en_nivel_riesgo", "BAJO"),
            riesgo_porcentaje=estado.get("riesgo_porcentaje"),
            recomendaciones=estado.get("recomendaciones", []),
            fuente="procedimiento_almacenado",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en análisis nutricional: {exc}")


@router.get("/health")
async def ml_health():
    """
    Verifica el estado del servicio ML externo y la conectividad.
    """
    import os

    import httpx

    ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
    ml_service_url = ml_service_url.rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ml_service_url}/health")

            if response.status_code == 200:
                ml_data = response.json()
                return {
                    "status": "ok",
                    "ml_api_url": ml_service_url,
                    "ml_api_status": "ok",
                    "ml_model_loaded": ml_data.get("lms_loaded", False),
                    "ml_llm_available": ml_data.get("llm_available", False),
                    "ml_db_available": ml_data.get("db_available", False),
                }
            else:
                return {
                    "status": "error",
                    "ml_api_url": ml_service_url,
                    "ml_api_status": f"HTTP {response.status_code}",
                    "detail": "Servicio ML no responde correctamente",
                }

    except Exception as e:
        return {
            "status": "error",
            "ml_api_url": ml_service_url,
            "ml_api_status": "unreachable",
            "detail": f"No se puede conectar al servicio ML: {str(e)}",
        }


class TrainModelRequest(BaseModel):
    """Request para entrenar el modelo ML."""

    min_measurements: int = Field(2, description="Mínimo de mediciones por niño")
    lookback_months: int = Field(24, description="Meses hacia atrás para considerar")
    include_synthetic: bool = Field(True, description="Incluir datos sintéticos")


class TrainModelResponse(BaseModel):
    """Response del entrenamiento del modelo."""

    status: str
    message: str
    accuracy: float | None = None
    f1_score: float | None = None
    model_path: str | None = None
    training_time_seconds: float | None = None
    dataset_size: int | None = None


@router.post("/train_model", response_model=TrainModelResponse)
async def train_model(req: TrainModelRequest) -> TrainModelResponse:
    """
    Entrena el modelo de predicción nutricional usando datos de la BD.
    Puede ser llamado desde Colab o scripts externos.
    """
    import os
    import subprocess
    import time
    from pathlib import Path

    try:
        # Rutas
        ml_dir = Path(os.getenv("ML_RECOMENDATOR_PATH", "/app/ml-recomendator"))
        extract_script = ml_dir / "src/training/extract_nutritional_status_data.py"
        train_script = ml_dir / "src/training/train_nutritional_predictor.py"
        data_file = ml_dir / "data/nutritional_status_training_data.csv"
        model_file = ml_dir / "models/nutritional_predictor.pkl"

        if not extract_script.exists() or not train_script.exists():
            return TrainModelResponse(
                status="error",
                message="Scripts de entrenamiento no encontrados",
                model_path=None,
            )

        start_time = time.time()

        # 1. Extraer datos
        extract_result = subprocess.run(
            [
                "python3",
                str(extract_script),
            ],
            cwd=str(ml_dir),
            capture_output=True,
            text=True,
            timeout=300,
        )

        if extract_result.returncode != 0:
            return TrainModelResponse(
                status="error",
                message=f"Error extrayendo datos: {extract_result.stderr}",
                model_path=None,
            )

        # Contar registros
        dataset_size = 0
        if data_file.exists():
            with open(data_file) as f:
                dataset_size = sum(1 for _ in f) - 1  # Excluir header

        # 2. Entrenar modelo
        train_result = subprocess.run(
            [
                "python3",
                str(train_script),
                "--input",
                str(data_file),
                "--output",
                str(model_file),
            ],
            cwd=str(ml_dir),
            capture_output=True,
            text=True,
            timeout=600,
        )

        training_time = time.time() - start_time

        if train_result.returncode != 0:
            return TrainModelResponse(
                status="error",
                message=f"Error entrenando modelo: {train_result.stderr}",
                model_path=None,
                training_time_seconds=training_time,
                dataset_size=dataset_size,
            )

        # Extraer métricas del output
        accuracy = None
        f1_score = None
        for line in train_result.stderr.split("\n"):
            if "Accuracy:" in line:
                try:
                    accuracy = float(line.split("Accuracy:")[-1].strip())
                except:
                    pass
            if "F1-Score (macro):" in line:
                try:
                    f1_score = float(line.split("F1-Score (macro):")[-1].strip())
                except:
                    pass

        return TrainModelResponse(
            status="success",
            message="Modelo entrenado exitosamente",
            accuracy=accuracy,
            f1_score=f1_score,
            model_path=str(model_file),
            training_time_seconds=training_time,
            dataset_size=dataset_size,
        )

    except subprocess.TimeoutExpired:
        return TrainModelResponse(
            status="error",
            message="Entrenamiento excedió el tiempo límite (10 minutos)",
            model_path=None,
        )
    except Exception as e:
        return TrainModelResponse(
            status="error",
            message=f"Error inesperado: {str(e)}",
            model_path=None,
        )
