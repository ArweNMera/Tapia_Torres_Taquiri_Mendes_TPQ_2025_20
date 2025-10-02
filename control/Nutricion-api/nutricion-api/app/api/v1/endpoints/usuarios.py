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
from app.application.services.usuarios_service import UsuariosService
from app.infrastructure.security.password_service import PasswordService
from app.infrastructure.security.jwt_service import JWTService
from pydantic import BaseModel
from app.application.services.auth_service import get_current_user
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from app.schemas.auth import UserResponse as AuthUserResponse

class RolInsert(BaseModel):
    rol_codigo: str
    rol_nombre: str

class RolResponse(BaseModel):
    rol_id: int
    msg: str

router = APIRouter()


def get_usuarios_service(db: Session = Depends(get_db)) -> UsuariosService:
    """Dependencia para obtener el servicio de usuarios con inyección de dependencias."""
    return UsuariosService(
        repository=UsuariosRepository(db),
        password_service=PasswordService(),
        jwt_service=JWTService()
    )


@router.post("/register", response_model=Token)
def register(
    user_register: UserRegister,
    usuarios_service: UsuariosService = Depends(get_usuarios_service)
):
    """Registrar un nuevo usuario."""
    return usuarios_service.register_user(user_register)


@router.post("/roles", response_model=RolResponse)
def create_rol(
    rol_insert: RolInsert,
    usuarios_service: UsuariosService = Depends(get_usuarios_service)
):
    """Crear un nuevo rol en el sistema."""
    result = usuarios_service.create_role(rol_insert.rol_codigo, rol_insert.rol_nombre)
    return RolResponse(rol_id=result.rol_id, msg=result.msg)

@router.get("/me")
def get_me(
    current_user: AuthUserResponse = Depends(get_current_user),
    usuarios_service: UsuariosService = Depends(get_usuarios_service)
):
    """Obtener perfil del usuario autenticado."""
    return usuarios_service.get_user_with_profile(current_user.usr_id)


@router.put("/profile")
def update_profile(
    profile: UserProfileSchema,
    current_user: AuthUserResponse = Depends(get_current_user),
    usuarios_service: UsuariosService = Depends(get_usuarios_service)
):
    """Actualizar perfil del usuario autenticado."""
    return usuarios_service.update_user_profile(
        current_user.usr_id,
        profile.model_dump(exclude_unset=True)
    )

@router.put("/{usr_id}/role", response_model=UserRoleChangeResponse)
def change_user_role(
    usr_id: int,
    payload: UserRoleChangeRequest,
    current_user: AuthUserResponse = Depends(get_current_user),
    usuarios_service: UsuariosService = Depends(get_usuarios_service)
):
    """Cambiar rol de un usuario."""
    rol_codigo = payload.rol_codigo.strip() if payload.rol_codigo else payload.rol_codigo
    result = usuarios_service.change_user_role(
        usr_id=usr_id,
        rol_codigo=rol_codigo,
        requesting_user_id=current_user.usr_id
    )
    return UserRoleChangeResponse(**result)
