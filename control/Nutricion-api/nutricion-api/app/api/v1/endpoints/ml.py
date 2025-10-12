from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.ninos_repo import NinosRepository

# Try to import assist from ml-recomendator; add path fallback if needed
# NOTA: Estos imports están comentados porque el backend no necesita acceso directo al código ML
# El backend se comunica con el modelo ML vía HTTP (puerto 8001)
# try:
#     from src.llm.assist import summarize_with_llm, format_recommender_prompt
# except Exception:
#     pass


# Funciones dummy para compatibilidad (no se usan en Docker)
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


# ============================================================================
# NUEVO ENDPOINT: Análisis Nutricional usando procedimientos almacenados
# ============================================================================


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
    Verifica el estado del módulo de análisis nutricional basado en procedimientos almacenados.
    """
    return {
        "status": "ok",
        "source": "stored_procedure",
        "detail": "Analizador nutricional usando sp_evaluar_estado_nutricional",
    }
