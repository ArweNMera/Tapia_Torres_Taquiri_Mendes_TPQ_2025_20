from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.infrastructure.db.session import get_db
from app.schemas.ninos import (
    NinoCreate, NinoUpdate, NinoResponse, 
    AnthropometryCreate, AnthropometryResponse,
    CreateChildProfileRequest, CreateChildProfileResponse,
    NinoWithAnthropometry, NutritionalStatusResponse,
    AlergiaCreate, AlergiaResponse
)
from app.application import ninos_service
from app.application.auth_service import get_current_user
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
    return ninos_service.create_child_profile(db, profile_data, current_user.usr_id)

@router.get("/", response_model=List[NinoWithAnthropometry])
def get_my_children(
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Obtener todos los niños del tutor actual con sus datos antropométricos
    y estado nutricional calculado.
    """
    return ninos_service.get_children_by_tutor(db, current_user.usr_id)

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
    return ninos_service.get_child_by_id(db, nin_id, current_user.usr_id)

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
    return ninos_service.update_child(db, nin_id, nino_data, current_user.usr_id)

@router.delete("/{nin_id}")
def delete_child(
    nin_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Eliminar un niño del sistema.
    """
    return ninos_service.delete_child(db, nin_id, current_user.usr_id)

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
    return ninos_service.add_anthropometry(db, nin_id, antropo_data, current_user.usr_id)

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
    child_data = ninos_service.get_child_by_id(db, nin_id, current_user.usr_id)
    
    if not child_data.ultimo_estado_nutricional:
        raise HTTPException(
            status_code=404, 
            detail="No hay datos antropométricos disponibles para calcular el estado nutricional"
        )
    
    return child_data.ultimo_estado_nutricional

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
    # Verificar que el niño pertenece al tutor
    child_data = ninos_service.get_child_by_id(db, nin_id, current_user.usr_id)
    
    from app.infrastructure.repositories.ninos_repo import NinosRepository
    repo = NinosRepository(db)
    
    antropometrias_dict = repo.get_antropometrias_by_nino(nin_id, limit=limit)
    return [AnthropometryResponse(**ant) for ant in antropometrias_dict]


@router.post("/{nin_id}/alergias", response_model=AlergiaResponse, status_code=status.HTTP_201_CREATED)
def add_child_allergy(
    nin_id: int,
    alergia: AlergiaCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    # Verifica pertenencia
    _ = ninos_service.get_child_by_id(db, nin_id, current_user.usr_id)
    repo = NinosRepository(db)
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
    _ = ninos_service.get_child_by_id(db, nin_id, current_user.usr_id)
    repo = NinosRepository(db)
    items = repo.obtener_alergias(nin_id)
    return [AlergiaResponse(**it) for it in items]

@router.delete("/{nin_id}/alergias/{alergia_id}")
def delete_child_allergy(
    nin_id: int,
    alergia_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    _ = ninos_service.get_child_by_id(db, nin_id, current_user.usr_id)
    # Eliminar relación específica
    affected = db.execute(text("DELETE FROM ninos_alergias WHERE na_id = :na_id AND nin_id = :nin_id"), {
        "na_id": alergia_id,
        "nin_id": nin_id
    })
    db.commit()
    if affected.rowcount == 0:
        raise HTTPException(status_code=404, detail="Alergia no encontrada para este niño")
    return {"message": "Alergia eliminada"}
