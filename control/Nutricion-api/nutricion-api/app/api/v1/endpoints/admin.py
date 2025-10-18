"""
Endpoints de administración - Solo para usuarios con rol ADMIN
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.application.services.auth_service import get_current_user
from app.infrastructure.db.session import get_db
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


@router.get("/usuarios", response_model=List[UsuarioListResponse])
def listar_usuarios(
    db: Session = Depends(get_db), current_user: UserResponse = Depends(verificar_admin)
):
    """
    Listar todos los usuarios del sistema (solo admin)
    """
    query = text("""
        SELECT
            u.usr_id,
            u.usr_usuario,
            u.usr_nombre,
            u.usr_apellido,
            u.usr_correo,
            u.usr_dni,
            r.rol_nombre,
            u.usr_activo,
            u.creado_en
        FROM usuarios u
        INNER JOIN roles r ON u.rol_id = r.rol_id
        WHERE u.eliminado_en IS NULL
        ORDER BY u.creado_en DESC
    """)

    result = db.execute(query)
    usuarios = []

    for row in result:
        usuarios.append(
            UsuarioListResponse(
                usr_id=row[0],
                usr_usuario=row[1],
                usr_nombre=row[2],
                usr_apellido=row[3],
                usr_correo=row[4],
                usr_dni=row[5],
                rol_nombre=row[6],
                usr_activo=bool(row[7]),
                creado_en=str(row[8]),
            )
        )

    return usuarios


@router.post("/reset-password", response_model=ResetPasswordResponse)
def resetear_contrasena_usuario(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(verificar_admin),
):
    """
    Resetear la contraseña de cualquier usuario (solo admin)
    """
    # Verificar que el usuario existe
    query_usuario = text("""
        SELECT usr_id, usr_usuario, usr_activo
        FROM usuarios
        WHERE usr_id = :usr_id AND eliminado_en IS NULL
    """)

    result = db.execute(query_usuario, {"usr_id": request.usr_id}).fetchone()

    if not result:
        raise HTTPException(
            status_code=404, detail=f"Usuario con ID {request.usr_id} no encontrado"
        )

    usr_id, usr_usuario, usr_activo = result

    if not usr_activo:
        raise HTTPException(
            status_code=400, detail="No se puede resetear la contraseña de un usuario inactivo"
        )

    # Hashear la nueva contraseña
    password_service = PasswordService()
    hashed_password = password_service.hash_password(request.nueva_contrasena)

    # Actualizar la contraseña en la base de datos
    update_query = text("""
        UPDATE usuarios
        SET usr_contrasena = :nueva_contrasena,
            actualizado_en = CURRENT_TIMESTAMP
        WHERE usr_id = :usr_id
    """)

    db.execute(update_query, {"nueva_contrasena": hashed_password, "usr_id": usr_id})
    db.commit()

    return ResetPasswordResponse(
        message=f"Contraseña actualizada exitosamente para el usuario '{usr_usuario}'",
        usr_usuario=usr_usuario,
    )


@router.patch("/usuarios/{usr_id}/toggle-active")
def toggle_usuario_activo(
    usr_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(verificar_admin),
):
    """
    Activar/desactivar un usuario (solo admin)
    """
    # Verificar que el usuario existe
    query_usuario = text("""
        SELECT usr_id, usr_usuario, usr_activo
        FROM usuarios
        WHERE usr_id = :usr_id AND eliminado_en IS NULL
    """)

    result = db.execute(query_usuario, {"usr_id": usr_id}).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail=f"Usuario con ID {usr_id} no encontrado")

    usr_id_db, usr_usuario, usr_activo = result

    # No permitir desactivar al propio admin
    if usr_id == current_user.usr_id:
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")

    # Toggle del estado
    nuevo_estado = not usr_activo

    update_query = text("""
        UPDATE usuarios
        SET usr_activo = :nuevo_estado,
            actualizado_en = CURRENT_TIMESTAMP
        WHERE usr_id = :usr_id
    """)

    db.execute(update_query, {"nuevo_estado": nuevo_estado, "usr_id": usr_id})
    db.commit()

    return {
        "message": f"Usuario '{usr_usuario}' {'activado' if nuevo_estado else 'desactivado'} exitosamente",
        "usr_usuario": usr_usuario,
        "usr_activo": nuevo_estado,
    }
