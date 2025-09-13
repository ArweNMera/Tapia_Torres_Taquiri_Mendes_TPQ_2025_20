from fastapi import APIRouter
from .endpoints import auth, usuarios, ninos
from .endpoints import entidades as entidades_endpoints
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.ninos_repo import NinosRepository

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(ninos.router, prefix="/children", tags=["children"])
"""
Compatibilidad: expone también las rutas de `children` bajo `/ninos` para
evitar desajustes con el frontend actual.
"""
api_router.include_router(ninos.router, prefix="/ninos", tags=["children-compat"]) 

# Rutas para tipos de alergias (compatibles con el frontend)
alergias_router = APIRouter()

@alergias_router.get("/tipos")
def get_allergy_types(q: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    repo = NinosRepository(db)
    return repo.obtener_tipos_alergias(q=q, limit=limit)

@alergias_router.post("/tipos")
def create_allergy_type(payload: dict, db: Session = Depends(get_db)):
    ta_codigo = payload.get("ta_codigo")
    ta_nombre = payload.get("ta_nombre")
    ta_categoria = payload.get("ta_categoria")
    if not ta_codigo or not ta_nombre or not ta_categoria:
        return {"detail": "ta_codigo, ta_nombre y ta_categoria son requeridos"}
    repo = NinosRepository(db)
    return repo.crear_tipo_alergia(ta_codigo, ta_nombre, ta_categoria)

api_router.include_router(alergias_router, prefix="/alergias", tags=["alergias"])
api_router.include_router(entidades_endpoints.router, prefix="/entidades", tags=["entidades"])
