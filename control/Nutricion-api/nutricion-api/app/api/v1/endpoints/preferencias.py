"""
Endpoints para gestión de preferencias alimentarias
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.services.auth_service import get_current_user
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.ninos_repo import NinosRepository
from app.infrastructure.repositories.preferencias_repo import PreferenciasRepository
from app.schemas.preferencias import (
    PreferenciasPorTipoResponse,
    PreferenciasRequest,
    PreferenciasResponse,
    TipoComida,
)

router = APIRouter(prefix="/preferencias", tags=["Preferencias"])


@router.post("/ninos/{nin_id}", status_code=status.HTTP_200_OK)
def guardar_preferencias_nino(
    nin_id: int,
    preferencias: PreferenciasRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Guarda las preferencias alimentarias de un niño"""
    repo = PreferenciasRepository(db)

    total_guardadas = 0

    # Guardar preferencias por tipo de comida
    for tipo_comida in ["DESAYUNO", "ALMUERZO", "CENA", "SNACKS"]:
        prefs = getattr(preferencias, tipo_comida.lower(), [])
        if prefs:
            repo.guardar_preferencias(nin_id=nin_id, tipo_comida=tipo_comida, preferencias=prefs)
            total_guardadas += len(prefs)

    return {
        "mensaje": "Preferencias guardadas exitosamente",
        "nin_id": nin_id,
        "total_preferencias": total_guardadas,
    }


@router.get("/ninos/{nin_id}", response_model=PreferenciasResponse)
def obtener_preferencias_nino(
    nin_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Obtiene todas las preferencias de un niño agrupadas por tipo de comida"""
    repo = PreferenciasRepository(db)

    # Obtener todas las preferencias
    prefs_raw = repo.obtener_preferencias_nino(nin_id)

    if not prefs_raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron preferencias para el niño {nin_id}",
        )

    # Agrupar por tipo de comida
    preferencias_agrupadas = {"desayuno": [], "almuerzo": [], "cena": [], "snacks": []}

    ultima_actualizacion = None

    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"📊 Procesando {len(prefs_raw)} preferencias para niño {nin_id}")

    for pref in prefs_raw:
        tipo = pref["npc_tipo_comida"].lower()
        logger.info(f"  - Tipo: {tipo}, Preferencia: {pref['npc_preferencia']}")
        if tipo in preferencias_agrupadas:
            preferencias_agrupadas[tipo].append(pref["npc_preferencia"])

        if not ultima_actualizacion or pref["creado_en"] > ultima_actualizacion:
            ultima_actualizacion = pref["creado_en"]

    logger.info(f"✅ Preferencias agrupadas: {preferencias_agrupadas}")

    # Obtener nombre del niño
    ninos_repo = NinosRepository(db)
    nino = ninos_repo.obtener_nino(nin_id)

    return PreferenciasResponse(
        nin_id=nin_id,
        nin_nombres=nino["nin_nombres"] if nino else "Desconocido",
        preferencias=preferencias_agrupadas,
        actualizado_en=ultima_actualizacion,
    )


@router.get("/ninos/{nin_id}/{tipo_comida}", response_model=PreferenciasPorTipoResponse)
def obtener_preferencias_por_tipo(
    nin_id: int,
    tipo_comida: TipoComida,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtiene las preferencias de un niño para un tipo de comida específico"""
    repo = PreferenciasRepository(db)

    prefs = repo.obtener_preferencias_nino(nin_id, tipo_comida.value)

    return PreferenciasPorTipoResponse(nin_id=nin_id, tipo_comida=tipo_comida, preferencias=prefs)


@router.delete("/items/{npc_id}", status_code=status.HTTP_200_OK)
def eliminar_preferencia(
    npc_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Elimina (desactiva) una preferencia específica"""
    repo = PreferenciasRepository(db)

    success = repo.eliminar_preferencia(npc_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró la preferencia {npc_id}"
        )

    return {"mensaje": "Preferencia eliminada exitosamente", "npc_id": npc_id}


@router.get("/usuarios/me/resumen")
def obtener_resumen_preferencias_usuario(
    db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Obtiene un resumen de las preferencias de todos los niños del usuario"""
    repo = PreferenciasRepository(db)

    usr_id = current_user.get("usr_id")
    resumen = repo.obtener_resumen_preferencias(usr_id)

    return {"total_ninos": len(resumen), "ninos": resumen}
