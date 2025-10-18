"""
Endpoints para gestión de planes de comidas
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.services.auth_service import get_current_user
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.ninos_repo import NinosRepository
from app.infrastructure.repositories.planes_comidas_repo import PlanesComidasRepository
from app.infrastructure.repositories.preferencias_repo import PreferenciasRepository
from app.schemas.planes_comidas import (
    GenerarPlanRequest,
    MenuListItem,
    MenusListResponse,
    PerfilNutricionalResponse,
    PlanSemanalResponse,
)

router = APIRouter(prefix="/planes-comidas", tags=["Planes de Comidas"])


@router.get("/ninos/{nin_id}/perfil-nutricional", response_model=PerfilNutricionalResponse)
def obtener_perfil_nutricional(
    nin_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Obtiene el perfil nutricional vigente del niño"""
    repo = PlanesComidasRepository(db)
    perfil = repo.obtener_perfil_nutricional(nin_id)

    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe perfil nutricional para el niño {nin_id}. Debe calcularlo primero.",
        )

    return perfil


@router.post("/ninos/{nin_id}/calcular-perfil")
def calcular_perfil_nutricional(
    nin_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Calcula y guarda el perfil nutricional del niño basado en su última antropometría"""
    import logging

    logger = logging.getLogger(__name__)

    repo = PlanesComidasRepository(db)

    try:
        logger.info(f"🔄 Calculando perfil nutricional para niño {nin_id}")
        resultado = repo.calcular_perfil_nutricional(nin_id)
        logger.info(f"✅ Resultado del SP: {resultado}")

        # Obtener el perfil recién creado
        perfil = repo.obtener_perfil_nutricional(nin_id)
        logger.info(f"📊 Perfil obtenido: {perfil}")

        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se pudo obtener el perfil después de calcularlo",
            )

        return {
            "mensaje": "Perfil nutricional calculado exitosamente",
            "pnn_id": perfil["pnn_id"],
            "nin_id": nin_id,
            "pnn_calorias_diarias": perfil["pnn_calorias_diarias"],
            "pnn_clasificacion": perfil["pnn_clasificacion"],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error calculando perfil: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculando perfil: {str(e)}",
        )


@router.post("/generar", response_model=PlanSemanalResponse)
async def generar_plan_semanal(
    request: GenerarPlanRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Genera un plan de comidas semanal personalizado usando LLM
    Considera: perfil nutricional, preferencias, alergias y disponibilidad
    """
    import logging

    logger = logging.getLogger(__name__)

    repo = PlanesComidasRepository(db)
    prefs_repo = PreferenciasRepository(db)
    ninos_repo = NinosRepository(db)

    # 1. Verificar que existe perfil nutricional
    perfil = repo.obtener_perfil_nutricional(request.nin_id)
    if not perfil:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El niño no tiene perfil nutricional. Debe calcularlo primero.",
        )

    # 2. Obtener datos del niño
    nino = repo.obtener_datos_nino(request.nin_id)
    if not nino:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró el niño {request.nin_id}"
        )

    # 3. Obtener preferencias
    try:
        preferencias_data = prefs_repo.obtener_preferencias_nino(request.nin_id)
        preferencias = {}
        for pref in preferencias_data:
            tipo = pref["npc_tipo_comida"]
            if tipo not in preferencias:
                preferencias[tipo] = []
            preferencias[tipo].append(pref["npc_preferencia"])
    except Exception as e:
        logger.warning(f"No se pudieron obtener preferencias: {e}")
        preferencias = {}

    # 4. Obtener alergias
    try:
        alergias = ninos_repo.obtener_alergias(request.nin_id)
        alergias_list = [a["ta_nombre"] for a in alergias]
    except Exception as e:
        logger.warning(f"No se pudieron obtener alergias: {e}")
        alergias_list = []

    # 5. Generar plan con LLM
    try:
        plan = await repo.generar_plan_con_llm(
            nin_id=request.nin_id,
            perfil=perfil,
            nino=nino,
            preferencias=preferencias,
            alergias=alergias_list,
            fecha_inicio=request.fecha_inicio,
            incluir_refacciones=request.incluir_refacciones,
            preferencias_adicionales=request.preferencias_adicionales,
        )

        return plan

    except Exception as e:
        logger.error(f"Error generando plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando plan de comidas: {str(e)}",
        )


@router.get("/ninos/{nin_id}/menus", response_model=MenusListResponse)
def listar_menus_nino(
    nin_id: int,
    estado: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Lista todos los menús de un niño"""
    repo = PlanesComidasRepository(db)

    menus = repo.listar_menus_nino(nin_id, estado, limit)

    return MenusListResponse(
        nin_id=nin_id, total=len(menus), menus=[MenuListItem(**menu) for menu in menus]
    )


@router.get("/menus/{men_id}")
def obtener_detalle_menu(
    men_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Obtiene el detalle completo de un menú con todos sus items"""
    repo = PlanesComidasRepository(db)

    menu = repo.obtener_detalle_menu(men_id)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró el menú {men_id}"
        )

    items = repo.obtener_items_menu(men_id)

    # Agrupar items por día
    dias = {}
    for item in items:
        dia_idx = item["mei_dia_idx"]
        if dia_idx not in dias:
            dias[dia_idx] = {"dia_idx": dia_idx, "items": []}
        dias[dia_idx]["items"].append(item)

    menu["dias"] = list(dias.values())

    return menu


@router.patch("/menus/{men_id}/estado")
def actualizar_estado_menu(
    men_id: int, estado: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Actualiza el estado de un menú (BORRADOR, APROBADO, ARCHIVADO)"""
    if estado not in ["BORRADOR", "APROBADO", "ARCHIVADO"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Debe ser: BORRADOR, APROBADO o ARCHIVADO",
        )

    repo = PlanesComidasRepository(db)
    repo.actualizar_estado_menu(men_id, estado)

    return {"mensaje": "Estado del menú actualizado", "men_id": men_id, "men_estado": estado}


# ============================================================================
# ENDPOINTS DE ALERGIAS (proxy a ninos endpoint)
# ============================================================================


@router.get("/ninos/{nin_id}/alergias")
def obtener_alergias_nino(
    nin_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Obtiene las alergias de un niño"""
    ninos_repo = NinosRepository(db)
    alergias = ninos_repo.obtener_alergias(nin_id)
    return {"alergias": alergias}


@router.post("/ninos/{nin_id}/alergias")
def agregar_alergia_nino(
    nin_id: int,
    alergia_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Agrega una alergia a un niño"""
    ninos_repo = NinosRepository(db)

    # Buscar o crear el tipo de alergia
    ta_codigo = alergia_data.get("alergeno", "").upper().replace(" ", "_")
    ta_nombre = alergia_data.get("alergeno")
    severidad = alergia_data.get("severidad", "MODERADA")

    # Intentar agregar la alergia
    try:
        result = ninos_repo.agregar_alergia(nin_id, ta_codigo, severidad)
        return result[0] if result else {}
    except:
        # Si no existe el tipo, crearlo primero
        ninos_repo.crear_tipo_alergia(ta_codigo, ta_nombre, "ALIMENTARIA")
        result = ninos_repo.agregar_alergia(nin_id, ta_codigo, severidad)
        return result[0] if result else {}


@router.delete("/alergias/{na_id}")
def eliminar_alergia_nino(
    na_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Elimina una alergia"""
    ninos_repo = NinosRepository(db)

    if not ninos_repo.eliminar_alergia(na_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alergia no encontrada")

    return {"mensaje": "Alergia eliminada exitosamente"}


# ============================================================================
# ENDPOINTS DE COMIDAS FAVORITAS
# ============================================================================


@router.get("/ninos/{nin_id}/favoritas")
def obtener_comidas_favoritas_nino(
    nin_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Obtiene las comidas favoritas de un niño"""
    repo = PlanesComidasRepository(db)
    favoritas = repo.listar_comidas_favoritas(nin_id)

    return {"favoritas": favoritas}


@router.post("/ninos/{nin_id}/favoritas")
def agregar_comida_favorita_nino(
    nin_id: int,
    favorita_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Agrega una comida favorita para un niño"""
    repo = PlanesComidasRepository(db)

    rec_id = favorita_data.get("rec_id")
    if not rec_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rec_id es requerido")

    try:
        repo.agregar_comida_favorita(nin_id, rec_id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró la receta {rec_id}"
        ) from exc

    return {"mensaje": "Comida favorita agregada exitosamente"}


@router.delete("/favoritas/{ncf_id}")
def eliminar_comida_favorita_nino(
    ncf_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Elimina una comida favorita"""
    repo = PlanesComidasRepository(db)

    if not repo.eliminar_comida_favorita(ncf_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comida favorita no encontrada"
        )

    return {"mensaje": "Comida favorita eliminada exitosamente"}


@router.get("/recetas/buscar")
def buscar_recetas_disponibles(
    q: str = "",
    tipo_comida: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Busca recetas por nombre o tipo de comida"""
    repo = PlanesComidasRepository(db)
    recetas = repo.buscar_recetas(q, tipo_comida, limit)
    return {"recetas": recetas}


@router.get("/recetas/{rec_id}")
def obtener_detalle_receta(
    rec_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Obtiene el detalle completo de una receta con ingredientes y nutrientes"""
    repo = PlanesComidasRepository(db)
    detalle = repo.obtener_detalle_receta_completo(rec_id)
    if detalle.get("rec_nombre") == "Receta no encontrada":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Receta {rec_id} no encontrada"
        )

    return {
        "rec_id": rec_id,
        "rec_nombre": detalle["rec_nombre"],
        "rec_instrucciones": detalle.get("rec_instrucciones", ""),
        "rec_activo": detalle.get("rec_activo", True),
        "ingredientes": detalle.get("ingredientes", []),
        "nutrientes": {
            "kcal": detalle.get("nutrientes", {}).get("kcal", 0.0),
            "proteina_g": detalle.get("nutrientes", {}).get("proteina_g", 0.0),
            "carbohidratos_g": detalle.get("nutrientes", {}).get("carbohidratos_g", 0.0),
            "grasa_g": detalle.get("nutrientes", {}).get("grasa_g", 0.0),
            "fibra_g": detalle.get("nutrientes", {}).get("fibra_g", 0.0),
            "hierro_mg": detalle.get("nutrientes", {}).get("hierro_mg", 0.0),
        },
    }
