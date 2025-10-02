from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.infrastructure.db.session import get_db
from app.schemas.ninos import (
    NinoCreate, NinoUpdate, NinoResponse,
    AnthropometryCreate, AnthropometryResponse,
    CreateChildProfileRequest, CreateChildProfileResponse,
    NinoWithAnthropometry, NutritionalStatusResponse,
    AlergiaCreate, AlergiaResponse,
    AssignTutorRequest
)
from app.application.services import ninos_service
from app.application.services.auth_service import get_current_user
from app.schemas.auth import UserResponse
from typing import List
from app.infrastructure.repositories.ninos_repo import NinosRepository
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from app.schemas.ninos import NinoCreate

router = APIRouter()

@router.get("/self", response_model=NinoResponse)
def get_or_create_self_child(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener (o crear si no existe) el perfil antropométrico personal
    del usuario autogestionado (>=13) como registro en `ninos` asociado
    a `usr_id_propietario`.
    """
    nrepo = NinosRepository(db)
    existing = nrepo.get_nino_by_owner(current_user.usr_id)
    if existing:
        return NinoResponse(**existing)

    # Necesitamos datos de perfil para crear (fecha_nac y genero)
    urepo = UsuariosRepository(db)
    perfil = urepo.get_user_profile(current_user.usr_id)
    if not perfil or not perfil.get("fecha_nac") or not perfil.get("genero"):
        raise HTTPException(status_code=400, detail="Completa tu fecha de nacimiento y género en el perfil antes de registrar medidas")
    genero = perfil.get("genero")
    if genero not in ("M", "F"):
        raise HTTPException(status_code=400, detail="El género debe ser M o F para crear el perfil antropométrico personal")

    # Intento de reconciliación: si el usuario ya creó "niños" donde es tutor
    # y alguno coincide con su fecha de nacimiento y género, promover a propietario.
    try:
        posibles = nrepo.get_ninos_by_tutor(current_user.usr_id)
        for cand in posibles:
            if cand.get("nin_fecha_nac") == perfil.get("fecha_nac") and cand.get("nin_sexo") == genero:
                promovido = nrepo.promote_child_to_owner(cand["nin_id"], current_user.usr_id)
                if promovido:
                    return NinoResponse(**promovido)
    except Exception:
        pass

    # Construir NinoCreate usando los datos del usuario
    nombres = (perfil.get("usr_nombre") or current_user.usr_nombre) if hasattr(current_user, 'usr_nombre') else perfil.get("usr_nombre")
    apellidos = (perfil.get("usr_apellido") or current_user.usr_apellido) if hasattr(current_user, 'usr_apellido') else perfil.get("usr_apellido")
    display_name = (f"{nombres} {apellidos}" if nombres or apellidos else current_user.usr_usuario).strip()

    nino_create = NinoCreate(
        nin_nombres=display_name,
        nin_fecha_nac=perfil.get("fecha_nac"),
        nin_sexo=genero,
        ent_id=None
    )

    created = nrepo.create_nino(nino_create, current_user.usr_id)
    if not created:
        raise HTTPException(status_code=400, detail="No se pudo crear el perfil antropométrico personal")
    return NinoResponse(**created)

@router.post("/profiles", response_model=CreateChildProfileResponse, status_code=status.HTTP_201_CREATED)
def create_child_profile(
    profile_data: CreateChildProfileRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Crear perfil completo de niño con datos antropométricos iniciales.
    Este endpoint cumple con el PMV 1: permite registrar niños con edad, peso y talla.
    """
    from app.domain.utils.nutrition_recommendations import generar_recomendaciones_nutricionales
    
    repo = NinosRepository(db)
    
    # 1. Crear el niño
    nino_dict = repo.create_nino(profile_data.nino, current_user.usr_id)
    if not nino_dict:
        raise HTTPException(status_code=400, detail="Error al crear el perfil del niño")
    
    nin_id = nino_dict["nin_id"]
    
    # 2. Agregar antropometría inicial
    antropometria_dict = repo.agregar_antropometria(nin_id, profile_data.antropometria.model_dump())
    if not antropometria_dict:
        raise HTTPException(status_code=400, detail="Error al agregar datos antropométricos")
    
    # 3. Evaluar estado nutricional
    estado = repo.evaluar_estado_nutricional(nin_id)
    if not estado:
        raise HTTPException(status_code=400, detail="Error al evaluar estado nutricional")
    
    # 4. Generar recomendaciones
    clasificacion = estado.get("en_clasificacion", "")
    imc = estado.get("imc_calculado", 0)
    edad_meses = nino_dict.get("edad_meses", 0)
    
    estado_nutricional = {
        "imc": imc,
        "z_score_imc": estado.get("en_z_score_imc"),
        "classification": clasificacion,
        "percentile": estado.get("percentil_calculado"),
        "risk_level": estado.get("en_nivel_riesgo"),
        "recommendations": generar_recomendaciones_nutricionales(clasificacion, imc, edad_meses)
    }
    
    return CreateChildProfileResponse(
        nino=NinoResponse(**nino_dict),
        antropometria=AnthropometryResponse(**antropometria_dict),
        estado_nutricional=NutritionalStatusResponse(**estado_nutricional)
    )

@router.get("/", response_model=List[NinoWithAnthropometry])
def get_my_children(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener todos los niños del tutor actual con sus datos antropométricos
    y estado nutricional calculado.
    """
    repo = NinosRepository(db)
    return repo.get_ninos_completos_by_tutor(current_user.usr_id)

@router.get("/{nin_id}", response_model=NinoWithAnthropometry)
def get_child_by_id(
    nin_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener un niño específico con todos sus datos antropométricos
    y estado nutricional actual.
    """
    repo = NinosRepository(db)
    child = repo.get_perfil_completo_con_datos(nin_id)
    if not child:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    return child

@router.put("/{nin_id}", response_model=NinoResponse)
def update_child(
    nin_id: int,
    nino_data: NinoUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Actualizar datos básicos de un niño (nombre, alergias, entidad).
    """
    repo = NinosRepository(db)
    # Verificar que el niño existe
    nino = repo.get_nino_by_id(nin_id)
    if not nino:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    # Actualizar
    updated = repo.actualizar_nino(nin_id, nino_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=400, detail="No se pudo actualizar el niño")
    
    return NinoResponse(**updated)

@router.delete("/{nin_id}")
def delete_child(
    nin_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Eliminar un niño del sistema.
    """
    repo = NinosRepository(db)
    # Verificar que el niño existe
    nino = repo.get_nino_by_id(nin_id)
    if not nino:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    # Eliminar
    success = repo.delete_nino(nin_id)
    if not success:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el niño")
    
    return {"message": "Niño eliminado exitosamente"}

@router.post("/{nin_id}/anthropometry", response_model=AnthropometryResponse, status_code=status.HTTP_201_CREATED)
def add_anthropometry_data(
    nin_id: int,
    antropo_data: AnthropometryCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Agregar nuevos datos antropométricos (peso, talla) a un niño.
    Permite seguimiento del crecimiento en el tiempo.
    """
    repo = NinosRepository(db)
    # Verificar que el niño existe
    nino = repo.get_nino_by_id(nin_id)
    if not nino:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    # Agregar antropometría
    antropometria_dict = repo.agregar_antropometria(nin_id, antropo_data.model_dump())
    if not antropometria_dict:
        raise HTTPException(status_code=400, detail="No se pudo agregar la medición antropométrica")
    
    return AnthropometryResponse(**antropometria_dict)

@router.post("/{nin_id}/assign-tutor", response_model=NinoResponse)
def assign_child_tutor(
    nin_id: int,
    payload: AssignTutorRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Asignar un niño existente a un tutor/padre específico."""
    nrepo = NinosRepository(db)
    nino_dict = nrepo.get_nino_by_id(nin_id)
    if not nino_dict:
        raise HTTPException(status_code=404, detail="Niño no encontrado")

    urepo = UsuariosRepository(db)
    current_role_code = urepo.get_role_code_by_id(current_user.rol_id)
    is_admin = current_role_code in {"ADMIN", "SUPERADMIN"}
    is_self_assignment = payload.usr_id_tutor == current_user.usr_id
    is_current_responsible = nino_dict.get("usr_id_tutor") == current_user.usr_id or nino_dict.get("usr_id_propietario") == current_user.usr_id

    if not (is_admin or is_self_assignment or is_current_responsible):
        raise HTTPException(status_code=403, detail="No tienes permiso para asignar este niño")

    updated = nrepo.assign_child_to_tutor(nin_id, payload.usr_id_tutor)
    if not updated:
        raise HTTPException(status_code=400, detail="No se pudo asignar el tutor")
    
    return NinoResponse(**updated)

@router.get("/{nin_id}/nutritional-status", response_model=NutritionalStatusResponse)
def get_nutritional_status(
    nin_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener el estado nutricional actual de un niño basado en sus 
    últimos datos antropométricos.
    
    Cumple con PMV 1: predice estado nutricional (bajo peso, normal, sobrepeso)
    a partir de datos antropométricos comparados con estándares.
    """
    repo = NinosRepository(db)
    child_data = repo.get_perfil_completo_con_datos(nin_id)
    if not child_data:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    ultimo_estado = child_data.get("ultimo_estado_nutricional")
    if not ultimo_estado:
        raise HTTPException(
            status_code=404, 
            detail="No hay datos antropométricos disponibles para calcular el estado nutricional"
        )
    
    return NutritionalStatusResponse(**ultimo_estado)

# Endpoints adicionales para casos específicos

@router.post("/", response_model=NinoResponse, status_code=status.HTTP_201_CREATED)
def create_child_basic(
    nino_data: NinoCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Crear solo el perfil básico de un niño sin datos antropométricos.
    Para casos donde se quiere registrar el niño primero y agregar medidas después.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # 🔍 DEBUG LOG
    logger.warning(f"🔍 CREATE CHILD DEBUG:")
    logger.warning(f"  📝 Datos recibidos del formulario:")
    logger.warning(f"    - nin_nombres: {nino_data.nin_nombres}")
    logger.warning(f"    - nin_fecha_nac: {nino_data.nin_fecha_nac}")
    logger.warning(f"    - nin_sexo: {nino_data.nin_sexo}")
    logger.warning(f"    - ent_id: {nino_data.ent_id}")
    logger.warning(f"  👤 Usuario actual (tutor/propietario):")
    logger.warning(f"    - usr_id: {current_user.usr_id}")
    logger.warning(f"    - usr_usuario: {current_user.usr_usuario if hasattr(current_user, 'usr_usuario') else 'N/A'}")
    
    from app.infrastructure.repositories.ninos_repo import NinosRepository
    
    repo = NinosRepository(db)
    nino_dict = repo.create_nino(nino_data, current_user.usr_id)
    
    if not nino_dict:
        raise HTTPException(status_code=400, detail="Error al crear el perfil del niño")
    
    return NinoResponse(**nino_dict)

@router.get("/{nin_id}/anthropometry", response_model=List[AnthropometryResponse])
def get_child_anthropometry_history(
    nin_id: int,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener el historial de datos antropométricos de un niño.
    Útil para ver la evolución del crecimiento en el tiempo.
    """
    repo = NinosRepository(db)
    # Verificar que el niño existe
    nino = repo.get_nino_by_id(nin_id)
    if not nino:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    antropometrias_dict = repo.get_antropometrias_by_nino(nin_id, limit=limit)
    return [AnthropometryResponse(**ant) for ant in antropometrias_dict]


@router.post("/{nin_id}/alergias", response_model=AlergiaResponse, status_code=status.HTTP_201_CREATED)
def add_child_allergy(
    nin_id: int,
    alergia: AlergiaCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    repo = NinosRepository(db)
    # Verificar que el niño existe
    nino = repo.get_nino_by_id(nin_id)
    if not nino:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    result_list = repo.agregar_alergia(nin_id, alergia.ta_codigo, alergia.severidad or "LEVE")
    if not result_list:
        raise HTTPException(status_code=400, detail="No se pudo agregar la alergia")
    # Retornar el último registro correspondiente al tipo agregado
    last = result_list[-1]
    return AlergiaResponse(**last)

@router.get("/{nin_id}/alergias", response_model=List[AlergiaResponse])
def get_child_allergies(
    nin_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    repo = NinosRepository(db)
    # Verificar que el niño existe
    nino = repo.get_nino_by_id(nin_id)
    if not nino:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    items = repo.obtener_alergias(nin_id)
    return [AlergiaResponse(**it) for it in items]

@router.delete("/{nin_id}/alergias/{alergia_id}")
def delete_child_allergy(
    nin_id: int,
    alergia_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    repo = NinosRepository(db)
    # Verificar que el niño existe
    nino = repo.get_nino_by_id(nin_id)
    if not nino:
        raise HTTPException(status_code=404, detail="Niño no encontrado")
    
    # Eliminar relación específica
    affected = db.execute(text("DELETE FROM ninos_alergias WHERE na_id = :na_id AND nin_id = :nin_id"), {
        "na_id": alergia_id,
        "nin_id": nin_id
    })
    db.commit()
    if affected.rowcount == 0:
        raise HTTPException(status_code=404, detail="Alergia no encontrada para este niño")
    return {"message": "Alergia eliminada"}
