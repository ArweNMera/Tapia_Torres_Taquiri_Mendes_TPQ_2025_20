"""
Endpoints de administración - Solo para usuarios con rol ADMIN
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.application.services.auth_service import get_current_user
from app.application.services.usuarios_service import UsuariosService
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from app.infrastructure.security.jwt_service import JWTService
from app.infrastructure.security.password_service import PasswordService
from app.schemas.auth import UserResponse

router = APIRouter()


class ResetPasswordRequest(BaseModel):
    """Request para resetear contraseña de un usuario"""

    usr_id: int = Field(..., description="ID del usuario")
    nueva_contrasena: str = Field(..., min_length=6, description="Nueva contraseña")


class ResetPasswordResponse(BaseModel):
    """Response del reset de contraseña"""

    message: str
    usr_usuario: str


class UsuarioListResponse(BaseModel):
    """Response con información básica de usuario para admin"""

    usr_id: int
    usr_usuario: str
    usr_nombre: str
    usr_apellido: str
    usr_correo: str
    usr_dni: str | None
    rol_nombre: str
    usr_activo: bool
    creado_en: str


def verificar_admin(current_user: UserResponse = Depends(get_current_user)):
    """
    Dependency para verificar que el usuario actual es administrador
    """
    # Validar por rol_id (1 = Administrador) o por rol_nombre
    es_admin = current_user.rol_id == 1 or (
        current_user.rol_nombre and current_user.rol_nombre == "Administrador"
    )

    if not es_admin:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Solo administradores pueden acceder a este recurso.",
        )
    return current_user


def get_admin_usuarios_service(db: Session = Depends(get_db)) -> UsuariosService:
    """Dependencia para obtener el servicio de usuarios en contexto admin."""
    return UsuariosService(
        repository=UsuariosRepository(db),
        password_service=PasswordService(),
        jwt_service=JWTService(),
    )


@router.get("/usuarios", response_model=List[UsuarioListResponse])
def listar_usuarios(
    usuarios_service: UsuariosService = Depends(get_admin_usuarios_service),
    current_user: UserResponse = Depends(verificar_admin),
):
    """
    Listar todos los usuarios del sistema (solo admin)
    """
    usuarios = usuarios_service.list_users_admin()
    return [UsuarioListResponse(**usuario) for usuario in usuarios]


@router.post("/reset-password", response_model=ResetPasswordResponse)
def resetear_contrasena_usuario(
    request: ResetPasswordRequest,
    usuarios_service: UsuariosService = Depends(get_admin_usuarios_service),
    current_user: UserResponse = Depends(verificar_admin),
):
    """
    Resetear la contraseña de cualquier usuario (solo admin)
    """
    usuarios_service.reset_password_admin(request.usr_id, request.nueva_contrasena)
    usuario = usuarios_service.repository.get_user_by_id(request.usr_id)
    if not usuario:
        raise HTTPException(
            status_code=404,
            detail=f"Usuario con ID {request.usr_id} no encontrado",
        )
    return ResetPasswordResponse(
        message=f"Contraseña actualizada exitosamente para el usuario '{usuario.usr_usuario}'",
        usr_usuario=usuario.usr_usuario,
    )


@router.patch("/usuarios/{usr_id}/toggle-active")
def toggle_usuario_activo(
    usr_id: int,
    usuarios_service: UsuariosService = Depends(get_admin_usuarios_service),
    current_user: UserResponse = Depends(verificar_admin),
):
    """
    Activar/desactivar un usuario (solo admin)
    """
    if usr_id == current_user.usr_id:
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")

    resultado = usuarios_service.toggle_user_active_admin(usr_id, current_user.usr_id)

    return {
        "message": f"Usuario '{resultado['usr_usuario']}' "
        f"{'activado' if resultado['usr_activo'] else 'desactivado'} exitosamente",
        "usr_usuario": resultado["usr_usuario"],
        "usr_activo": resultado["usr_activo"],
    }
