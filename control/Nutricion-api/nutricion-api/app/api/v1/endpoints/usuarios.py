from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.schemas.usuarios import (
    UserRegister,
    UserProfile as UserProfileSchema,
    UserRoleChangeRequest,
    UserRoleChangeResponse
)
from app.schemas.auth import Token
from app.application.ninos_service import register_user
from app.application.riesgo_service import insert_rol
from pydantic import BaseModel
from app.application.auth_service import get_current_user
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from app.schemas.auth import UserResponse as AuthUserResponse

class RolInsert(BaseModel):
    rol_codigo: str
    rol_nombre: str

class RolResponse(BaseModel):
    rol_id: int
    msg: str

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_register: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, user_register)

@router.post("/roles", response_model=RolResponse)
def create_rol(rol_insert: RolInsert, db: Session = Depends(get_db)):
    result = insert_rol(db, rol_insert.rol_codigo, rol_insert.rol_nombre)
    return RolResponse(rol_id=result.rol_id, msg=result.msg)

@router.get("/me")
def get_me(
    current_user: AuthUserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = UsuariosRepository(db)
    perfil = repo.get_user_profile(current_user.usr_id) or {}
    # Combinar datos básicos del usuario autenticado con el perfil
    return {
        "usr_id": current_user.usr_id,
        "usr_usuario": current_user.usr_usuario,
        "usr_correo": perfil.get("usr_correo"),
        "usr_nombre": perfil.get("usr_nombre"),
        "usr_apellido": perfil.get("usr_apellido"),
        "rol_id": current_user.rol_id,
        "usr_activo": current_user.usr_activo,
        # Campos de perfil opcionales
        "dni": perfil.get("dni"),
        "avatar_url": perfil.get("avatar_url"),
        "telefono": perfil.get("telefono"),
        "direccion": perfil.get("direccion"),
        "genero": perfil.get("genero"),
        "fecha_nac": perfil.get("fecha_nac"),
        "idioma": perfil.get("idioma"),
    }

@router.put("/profile")
def update_profile(
    profile: UserProfileSchema,
    current_user: AuthUserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = UsuariosRepository(db)
    updated = repo.update_user_profile(current_user.usr_id, profile.model_dump(exclude_unset=True)) or {}
    # Unir con datos base del usuario autenticado
    return {
        "usr_id": current_user.usr_id,
        "usr_usuario": current_user.usr_usuario,
        "usr_correo": updated.get("usr_correo"),
        "usr_nombre": updated.get("usr_nombre"),
        "usr_apellido": updated.get("usr_apellido"),
        "rol_id": current_user.rol_id,
        "usr_activo": current_user.usr_activo,
        # Campos de perfil opcionales
        "dni": updated.get("dni"),
        "avatar_url": updated.get("avatar_url"),
        "telefono": updated.get("telefono"),
        "direccion": updated.get("direccion"),
        "genero": updated.get("genero"),
        "fecha_nac": updated.get("fecha_nac"),
        "idioma": updated.get("idioma"),
    }

@router.put("/{usr_id}/role", response_model=UserRoleChangeResponse)
def change_user_role(
    usr_id: int,
    payload: UserRoleChangeRequest,
    current_user: AuthUserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = UsuariosRepository(db)

    current_role_code = repo.get_role_code_by_id(current_user.rol_id)
    is_self_request = current_user.usr_id == usr_id
    is_admin = current_role_code in {"ADMIN", "SUPERADMIN"}

    if not (is_self_request or is_admin):
        raise HTTPException(status_code=403, detail="No tienes permiso para cambiar este rol")

    rol_codigo = payload.rol_codigo.strip() if payload.rol_codigo else payload.rol_codigo
    result = repo.change_user_role(usr_id, rol_codigo)
    if not result:
        raise HTTPException(status_code=400, detail="No se pudo cambiar el rol del usuario")

    return UserRoleChangeResponse(**result)
