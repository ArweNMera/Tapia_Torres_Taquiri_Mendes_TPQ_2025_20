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


@router.post("/generar-ml")
async def generar_plan_semanal_ml(
    request: GenerarPlanRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    🤖 Genera un plan de comidas semanal usando Machine Learning

    Este endpoint utiliza el modelo LightGBM entrenado para generar
    recomendaciones personalizadas de comidas basadas en:
    - Perfil nutricional del niño
    - Estado nutricional (NORMAL, DESNUTRICION, etc.)
    - Alergias activas
    - Preferencias de comidas
    - Modelo ML entrenado con datos reales

    El modelo alcanza:
    - NDCG@5: 89% (muy bueno prediciendo las top 5 recetas)
    - NDCG@10: 85% (muy bueno prediciendo las top 10 recetas)
    - Accuracy ±1: 76% (3 de cada 4 predicciones exactas)

    Args:
        request: Datos para generar plan (nin_id, fecha_inicio, días)

    Returns:
        Plan semanal generado con ML y guardado en la base de datos
    """
    import logging

    logger = logging.getLogger(__name__)

    from app.application.services.ml_menu_service import MLMenuService

    # Instanciar servicios siguiendo arquitectura hexagonal
    planes_repo = PlanesComidasRepository(db)
    ninos_repo = NinosRepository(db)
    prefs_repo = PreferenciasRepository(db)

    ml_service = MLMenuService(
        planes_repo=planes_repo, ninos_repo=ninos_repo, prefs_repo=prefs_repo
    )

    try:
        logger.info(f"🤖 Generando plan ML para niño {request.nin_id}")

        resultado = await ml_service.generar_plan_semanal_con_ml(
            nin_id=request.nin_id,
            fecha_inicio=request.fecha_inicio,
            incluir_refacciones=request.incluir_refacciones,
            dias=7,  # Siempre 7 días por ahora
        )

        if not resultado.get("exito"):
            logger.warning(
                f"⚠️ Plan generado pero no persistido: {resultado.get('error_persistencia')}"
            )

        # Convertir el plan ML al formato esperado por el frontend
        plan_ml = resultado.get("plan_ml", {})
        weekly_plan = plan_ml.get("weekly_plan", [])

        return {
            "mensaje": "Plan semanal generado exitosamente con Machine Learning",
            "men_id": resultado.get("men_id"),
            "nin_id": request.nin_id,
            "generado_por": "IA_ML",
            "modelo_version": "LightGBM_v1.0",
            "metricas_modelo": {
                "ndcg_at_5": 0.89,
                "ndcg_at_10": 0.85,
                "accuracy_tolerance_1": 0.76,
            },
            "plan_semanal": weekly_plan,
            "total_dias": plan_ml.get("total_days", 0),
            "total_comidas": plan_ml.get("total_meals", 0),
            "perfil_nutricional": resultado.get("perfil", {}),
            "alergias_consideradas": resultado.get("alergias", []),
        }

    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error generando plan ML: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando plan con ML: {str(e)}",
        )


@router.get("/ml/salud")
async def verificar_servidor_ml(current_user=Depends(get_current_user)):
    """
    Verifica el estado del servidor ML de recomendaciones

    Returns:
        Estado de conexión con el servidor ML
    """
    from app.application.services.ml_menu_service import MLMenuService

    # No necesita DB para verificar salud
    ml_service = MLMenuService(planes_repo=None, ninos_repo=None, prefs_repo=None)

    try:
        estado = await ml_service.verificar_servidor_ml()
        return estado
    except Exception as e:
        return {
            "servidor_ml_disponible": False,
            "error": str(e),
            "estado": "error",
        }


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


@router.post("/ninos/{nin_id}/favoritas/toggle")
def toggle_comida_favorita_nino(
    nin_id: int,
    favorita_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Agrega o quita una comida favorita (toggle) usando SP.
    Si ya está en favoritas, la quita. Si no está, la agrega.
    """
    repo = PlanesComidasRepository(db)

    rec_id = favorita_data.get("rec_id")
    if not rec_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="rec_id es requerido")

    try:
        accion = repo.toggle_comida_favorita(nin_id, rec_id)
        return {
            "mensaje": f"Comida favorita {accion.lower()}",
            "accion": accion,
            "es_favorita": accion == "AGREGADA",
        }
    except Exception as exc:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error en toggle favorita: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar favorita: {str(exc)}",
        ) from exc


@router.post("/ninos/{nin_id}/favoritas")
def agregar_comida_favorita_nino(
    nin_id: int,
    favorita_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Agrega una comida favorita para un niño (usa el toggle interno)"""
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


# ============================================================================
# ENDPOINTS DE FEEDBACK Y CALIFICACIONES
# ============================================================================


@router.get("/ninos/{nin_id}/recetas-plan")
def obtener_recetas_plan_actual(
    nin_id: int,
    q: Optional[str] = "",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Obtiene todas las recetas del plan de comidas activo/aprobado del niño
    Permite búsqueda por nombre para el autocompletado del modal de favoritos
    """
    repo = PlanesComidasRepository(db)

    try:
        recetas = repo.obtener_recetas_plan_actual(nin_id, busqueda=q)
        return {"recetas": recetas, "total": len(recetas)}
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error obteniendo recetas del plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo recetas del plan: {str(e)}",
        )


@router.post("/menus-feedback")
def registrar_feedback_comida(
    feedback_data: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Registra o actualiza el feedback de una comida (rating, porcentaje consumido, notas)
    Body esperado:
    {
        "mei_id": 123,          # ID del item del menú
        "nin_id": 456,          # ID del niño
        "mf_rating": 4,         # Rating 1-5 estrellas
        "mf_porcentaje_consumido": 80,  # 0-100%
        "mf_completado": true,  # ¿Se consumió?
        "mf_notas": "Le gustó mucho",
        "mf_fecha_consumo": "2025-11-01"
    }
    """
    repo = PlanesComidasRepository(db)

    mei_id = feedback_data.get("mei_id")
    nin_id = feedback_data.get("nin_id")

    if not mei_id or not nin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="mei_id y nin_id son requeridos"
        )

    try:
        # Obtener usr_id del current_user (puede ser objeto o dict)
        registrado_por = None
        if current_user:
            registrado_por = (
                current_user.usr_id
                if hasattr(current_user, "usr_id")
                else current_user.get("usr_id")
                if isinstance(current_user, dict)
                else None
            )

        feedback_id = repo.registrar_feedback_comida(
            mei_id=mei_id,
            nin_id=nin_id,
            mf_rating=feedback_data.get("mf_rating"),
            mf_porcentaje_consumido=feedback_data.get("mf_porcentaje_consumido"),
            mf_completado=feedback_data.get("mf_completado", False),
            mf_notas=feedback_data.get("mf_notas"),
            mf_fecha_consumo=feedback_data.get("mf_fecha_consumo"),
            mf_registrado_por=registrado_por,
        )

        return {"mensaje": "Feedback registrado exitosamente", "mf_id": feedback_id}
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error registrando feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registrando feedback: {str(e)}",
        )


@router.get("/ninos/{nin_id}/feedback")
def listar_feedback_nino(
    nin_id: int,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Lista todo el feedback (calificaciones) del niño.
    Útil para ver el historial de ratings y generar reportes.
    """
    repo = PlanesComidasRepository(db)

    try:
        feedback_list = repo.listar_feedback_nino(nin_id, fecha_desde, fecha_hasta)
        return {"feedback": feedback_list, "total": len(feedback_list)}
    except Exception as e:
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Error listando feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listando feedback: {str(e)}",
        )


@router.get("/ninos/{nin_id}/planes/{men_id}/pdf")
def descargar_plan_pdf(
    nin_id: int,
    men_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Descarga el plan de comidas semanal en formato PDF.
    Incluye 7 días con desayuno, almuerzo y cena, más resumen nutricional.
    """
    import logging
    from datetime import datetime

    from fastapi.responses import StreamingResponse

    from app.services.pdf_generator import PlanComidasPDFGenerator

    logger = logging.getLogger(__name__)

    try:
        # Obtener datos del menú
        repo = PlanesComidasRepository(db)
        menu = repo.obtener_detalle_menu(men_id)

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró el plan de comidas {men_id}",
            )

        # Verificar que el menú pertenezca al niño
        if menu.get("nin_id") != nin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Este menú no pertenece al niño especificado",
            )

        # Obtener items del menú con información nutricional para PDF
        items = repo.obtener_items_menu_para_pdf(men_id)

        if not items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="El menú no tiene comidas asignadas"
            )

        # Obtener datos del niño
        ninos_repo = NinosRepository(db)
        nino = ninos_repo.obtener_nino(nin_id)

        if not nino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró el niño {nin_id}"
            )

        # Obtener perfil nutricional
        perfil = repo.obtener_perfil_nutricional(nin_id)

        # Calcular edad en años desde edad_meses
        edad_meses = nino.get("edad_meses", 0)
        edad_anos = round(edad_meses / 12, 1) if edad_meses else 0

        # Preparar datos del niño para el PDF
        nino_data = {
            "nombre": nino.get("nin_nombres", "Sin nombre"),
            "edad": edad_anos,
            "clasificacion": perfil.get("clasificacion", "Normal") if perfil else "Normal",
        }

        # Formatear datos del plan
        plan_data = {
            "periodo": f"{menu.get('men_inicio', 'N/A')} - {menu.get('men_fin', 'N/A')}",
            "dias": [],
            "total_semanal": 0,
            "promedio_diario": 0,
        }

        # Agrupar comidas por día
        dias_dict = {}
        tipos_comida_orden = {"Desayuno": 1, "Almuerzo": 2, "Cena": 3}

        for item in items:
            dia_idx = item.get("mei_dia_idx", 0)
            if dia_idx not in dias_dict:
                dias_dict[dia_idx] = {"comidas": [], "total_kcal": 0}

            # Calcular calorías y proteínas
            kcal = item.get("kcal", 0) or item.get("rec_kcal_100g", 0)
            proteina_g = item.get("proteina_g", 0) or item.get("rec_proteina_g_100g", 0)

            dias_dict[dia_idx]["comidas"].append(
                {
                    "tipo_comida": item.get("mei_tipo_comida", "N/A"),
                    "nombre": item.get("rec_nombre", "N/A"),
                    "kcal": kcal,
                    "proteina_g": proteina_g,
                    "orden": tipos_comida_orden.get(item.get("mei_tipo_comida", ""), 99),
                }
            )
            dias_dict[dia_idx]["total_kcal"] += kcal

        # Convertir a lista ordenada por día (1-7)
        for dia_idx in sorted(dias_dict.keys()):
            # Ordenar comidas dentro del día (Desayuno -> Almuerzo -> Cena)
            dias_dict[dia_idx]["comidas"].sort(key=lambda x: x["orden"])
            # Remover campo 'orden' antes de agregar a plan_data
            for comida in dias_dict[dia_idx]["comidas"]:
                comida.pop("orden", None)

            plan_data["dias"].append(dias_dict[dia_idx])
            plan_data["total_semanal"] += dias_dict[dia_idx]["total_kcal"]

        if len(plan_data["dias"]) > 0:
            plan_data["promedio_diario"] = plan_data["total_semanal"] / len(plan_data["dias"])

        # Generar PDF
        generator = PlanComidasPDFGenerator()
        pdf_buffer = generator.generar_pdf_plan_semanal(plan_data, nino_data)

        # Preparar nombre del archivo
        nino_nombre_limpio = nino_data["nombre"].replace(" ", "_")
        fecha_str = datetime.now().strftime("%Y%m%d")
        filename = f"plan_comidas_{nino_nombre_limpio}_{fecha_str}.pdf"

        # Retornar como stream
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando PDF: {str(e)}",
        )
