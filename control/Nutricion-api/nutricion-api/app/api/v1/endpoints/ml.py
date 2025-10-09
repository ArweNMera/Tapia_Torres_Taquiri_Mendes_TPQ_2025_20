from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import httpx

from app.infrastructure.db.session import get_db
from app.core.config import settings

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
    features: Dict[str, Any]
    scores: Dict[str, float]
    prefer_llm: bool = True


class SummaryResponse(BaseModel):
    text: str
    used_llm: bool


@router.post("/summary", response_model=SummaryResponse)
def summarize(req: SummaryRequest) -> SummaryResponse:
    # First try LLM if preferred
    used_llm = False
    text: Optional[str] = None
    if req.prefer_llm:
        try:
            text = summarize_with_llm(req.features, req.scores)
            used_llm = text is not None
        except Exception as e:
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
# NUEVO ENDPOINT: Análisis Nutricional con Modelo ML
# ============================================================================

class RecomendacionNutricional(BaseModel):
    """Recomendación nutricional."""
    icono: str
    titulo: str
    descripcion: str


class AnalisisNutricionalRequest(BaseModel):
    """Request para análisis nutricional."""
    nin_id: int = Field(description="ID del niño")
    peso_kg: float = Field(description="Peso en kg")
    talla_cm: float = Field(description="Talla en cm")
    fecha_medicion: Optional[str] = Field(None, description="Fecha de medición (YYYY-MM-DD)")


class AnalisisNutricionalResponse(BaseModel):
    """Response de análisis nutricional."""
    # Medición
    fecha: str
    peso_kg: float
    talla_cm: float
    imc: float
    
    # Estado nutricional
    diagnostico: str
    imc_valor: float
    percentil: float
    nivel_riesgo: str
    baz: float
    
    # Probabilidades del modelo
    probabilidad: float
    probabilidades: Dict[str, float]
    
    # Recomendaciones
    recomendaciones: List[RecomendacionNutricional]
    
    # Metadata
    modelo_usado: bool
    modelo_version: str


@router.post("/analisis_nutricional", response_model=AnalisisNutricionalResponse)
async def analisis_nutricional(
    req: AnalisisNutricionalRequest,
    db: Session = Depends(get_db)
) -> AnalisisNutricionalResponse:
    """
    Análisis nutricional completo usando modelo ML.
    
    Este endpoint:
    1. Guarda la antropometría en la BD (opcional)
    2. Llama a la API ML en puerto 8003
    3. Retorna análisis completo con recomendaciones
    
    Reemplaza los procedimientos almacenados anteriores.
    """
    try:
        # Llamar a la API ML en puerto 8003
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.ML_API_URL}/ml/analisis_nutricional",
                json={
                    "nin_id": req.nin_id,
                    "peso_kg": req.peso_kg,
                    "talla_cm": req.talla_cm,
                    "fecha_medicion": req.fecha_medicion
                }
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Niño con ID {req.nin_id} no encontrado"
                )
            
            if response.status_code == 503:
                raise HTTPException(
                    status_code=503,
                    detail="Servicio ML no disponible. Verifica que esté corriendo en puerto 8003"
                )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error en API ML: {response.text}"
                )
            
            # Retornar respuesta de la API ML
            return response.json()
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="No se puede conectar a la API ML. Verifica que esté corriendo en puerto 8003"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Timeout al conectar con API ML"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en análisis nutricional: {str(e)}"
        )


@router.get("/health")
async def ml_health():
    """
    Verifica el estado de la API ML.
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ML_API_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "ok",
                    "ml_api_url": settings.ML_API_URL,
                    "ml_api_status": data.get("status"),
                    "ml_model_loaded": data.get("ml_model_loaded", False)
                }
            else:
                return {
                    "status": "error",
                    "ml_api_url": settings.ML_API_URL,
                    "detail": "API ML no responde correctamente"
                }
    except Exception as e:
        return {
            "status": "error",
            "ml_api_url": settings.ML_API_URL,
            "detail": f"No se puede conectar a API ML: {str(e)}"
        }

