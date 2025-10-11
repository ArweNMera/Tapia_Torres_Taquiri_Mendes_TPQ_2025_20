"""
FastAPI server usando el MODELO DIRECTO.
Más simple y directo que el anterior.

Utiliza Naive Bayes (Bayesian) y Random Forest para clasificación
según las 7 categorías nutricionales basándose en edad, peso y talla.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Dict, Optional
import sys

# Setup paths
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.models.direct_classifier import cargar_modelo_directo

# Crear app
app = FastAPI(
    title="ML Recomendator - Modelo Directo",
    version="2.0.0",
    description="API de clasificación nutricional usando Naive Bayes y Random Forest"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelo al iniciar
MODELO = None

@app.on_event("startup")
async def startup():
    global MODELO
    try:
        MODELO = cargar_modelo_directo()
        print("✅ Modelo directo cargado exitosamente")
    except Exception as e:
        print(f"⚠️  No se pudo cargar el modelo: {e}")
        print("   Entrena el modelo primero: ./ENTRENAR_AHORA.sh")


# ============================================================================
# SCHEMAS
# ============================================================================

class ClasificarRequest(BaseModel):
    """Request para clasificación nutricional."""
    edad_meses: int = Field(description="Edad en meses (0-228)")
    sexo: str = Field(description="M o F")
    peso_kg: float = Field(description="Peso en kilogramos")
    talla_cm: float = Field(description="Talla en centímetros")


class ClasificarResponse(BaseModel):
    """Response de clasificación."""
    clasificacion: str
    confianza: float
    probabilidades: Dict[str, float]
    datos_entrada: Dict
    bmi: float


class ExplicacionResponse(BaseModel):
    """Response con explicación detallada."""
    prediccion: str
    confianza: float
    datos_entrada: Dict
    contexto: str
    probabilidades_top3: list
    bmi: float


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    return {
        "app": "ML Recomendator - Modelo Directo",
        "version": "2.0.0",
        "modelo_cargado": MODELO is not None,
        "endpoints": {
            "clasificar": "/clasificar",
            "explicar": "/explicar",
            "health": "/health"
        }
    }


@app.get("/health")
def health():
    return {
        "status": "ok" if MODELO is not None else "modelo_no_cargado",
        "modelo_cargado": MODELO is not None
    }


@app.post("/clasificar", response_model=ClasificarResponse)
def clasificar(req: ClasificarRequest):
    """
    Clasifica el estado nutricional de un niño.
    
    Usa SOLO edad, sexo, peso y talla.
    NO necesita BAZ precalculado.
    """
    if MODELO is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo no disponible. Entrena primero: ./ENTRENAR_AHORA.sh"
        )
    
    try:
        # Validar datos
        if req.edad_meses < 0 or req.edad_meses > 228:
            raise HTTPException(400, "Edad debe estar entre 0 y 228 meses")
        
        if req.sexo.upper() not in ['M', 'F']:
            raise HTTPException(400, "Sexo debe ser M o F")
        
        if req.peso_kg <= 0:
            raise HTTPException(400, "Peso debe ser mayor a 0")
        
        if req.talla_cm <= 0:
            raise HTTPException(400, "Talla debe ser mayor a 0")
        
        # Predecir
        resultado = MODELO.predecir(
            edad_meses=req.edad_meses,
            sexo=req.sexo.upper(),
            peso_kg=req.peso_kg,
            talla_cm=req.talla_cm
        )
        
        # Calcular BMI
        bmi = req.peso_kg / (req.talla_cm / 100) ** 2
        
        return ClasificarResponse(
            clasificacion=resultado['clasificacion'],
            confianza=resultado['confianza'],
            probabilidades=resultado['probabilidades'],
            datos_entrada={
                'edad_meses': req.edad_meses,
                'edad_anos': round(req.edad_meses / 12, 1),
                'sexo': req.sexo.upper(),
                'peso_kg': req.peso_kg,
                'talla_cm': req.talla_cm
            },
            bmi=round(bmi, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error en clasificación: {str(e)}")


@app.post("/explicar", response_model=ExplicacionResponse)
def explicar(req: ClasificarRequest):
    """
    Clasifica y explica el resultado de forma detallada.
    """
    if MODELO is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo no disponible"
        )
    
    try:
        # Validar datos
        if req.edad_meses < 0 or req.edad_meses > 228:
            raise HTTPException(400, "Edad debe estar entre 0 y 228 meses")
        
        if req.sexo.upper() not in ['M', 'F']:
            raise HTTPException(400, "Sexo debe ser M o F")
        
        if req.peso_kg <= 0:
            raise HTTPException(400, "Peso debe ser mayor a 0")
        
        if req.talla_cm <= 0:
            raise HTTPException(400, "Talla debe ser mayor a 0")
        
        # Explicar
        explicacion = MODELO.explicar_prediccion(
            edad_meses=req.edad_meses,
            sexo=req.sexo.upper(),
            peso_kg=req.peso_kg,
            talla_cm=req.talla_cm
        )
        
        return ExplicacionResponse(
            prediccion=explicacion['prediccion'],
            confianza=explicacion['confianza'],
            datos_entrada=explicacion['datos_entrada'],
            contexto=explicacion['contexto'],
            probabilidades_top3=explicacion['probabilidades_top3'],
            bmi=explicacion['datos_entrada']['bmi']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error en explicación: {str(e)}")


@app.get("/modelo/info")
def modelo_info():
    """Información sobre el modelo cargado."""
    if MODELO is None:
        return {
            "cargado": False,
            "mensaje": "Modelo no cargado"
        }
    
    return {
        "cargado": True,
        "tipo": "DirectNutritionClassifier",
        "version": "2.0.0",
        "algoritmos": ["Naive Bayes (Bayesian)", "Random Forest", "Ensemble"],
        "categorias": list(MODELO.LABEL_TO_CATEGORY.values()),
        "features_usadas": [
            "edad_meses", "sexo", "peso_kg", "talla_cm", "bmi",
            "edad_anos", "es_bebe", "es_preescolar", "es_escolar", "es_adolescente",
            "peso_por_edad", "talla_por_edad", "bmi_x_edad", "peso_x_talla"
        ],
        "descripcion": "Modelo que usa Naive Bayes y Random Forest para clasificar según edad, peso y talla"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
