"""
Servicio de aplicación para gestión de usuarios.
Contiene los casos de uso relacionados con usuarios.
"""

from typing import Any

from fastapi import HTTPException

from app.domain.interfaces.usuarios_repository import IUsuariosRepository
from app.infrastructure.security.jwt_service import JWTService
from app.infrastructure.security.password_service import PasswordService
from app.schemas.auth import Token
from app.schemas.usuarios import UserRegister


class UsuariosService:
    """
    Servicio de aplicación para casos de uso de usuarios.
    Coordina entre repositorios y servicios de infraestructura.
    """

    def __init__(
        self,
        repository: IUsuariosRepository,
        password_service: PasswordService,
        jwt_service: JWTService,
    ):
        self.repository = repository
        self.password_service = password_service
        self.jwt_service = jwt_service

    def register_user(self, user_data: UserRegister) -> Token:
        """
        Caso de uso: Registrar un nuevo usuario.

        Args:
            user_data: Datos del usuario a registrar

        Returns:
            Token de acceso para el usuario registrado

        Raises:
            HTTPException: Si el usuario o email ya existen
        """
        # Validar que el username no existe
        if self.repository.username_exists(user_data.usuario):
            raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")

        # Validar que el email no existe
        existing_user = self.repository.get_user_by_email(user_data.correo)
        if existing_user:
            raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")

        # Hash de la contraseña
        user_data.contrasena = self.password_service.hash_password(user_data.contrasena)

        # Crear usuario
        try:
            result = self.repository.insert_user(user_data)
            # result es una tupla (user_id, "OK")
            user_id = result[0] if isinstance(result, tuple) else result

            # Crear token de acceso para el usuario registrado
            access_token = self.jwt_service.create_access_token(data={"sub": user_data.usuario})

            return Token(access_token=access_token, token_type="bearer")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al registrar usuario: {str(e)}")

    def get_user_with_profile(self, usr_id: int) -> dict[str, Any]:
        """
        Caso de uso: Obtener usuario con su perfil completo.

        Args:
            usr_id: ID del usuario

        Returns:
            Diccionario con datos del usuario y perfil

        Raises:
            HTTPException: Si el usuario no existe
        """
        user = self.repository.get_user_by_id(usr_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        profile = self.repository.get_user_profile(usr_id) or {}

        # Obtener el nombre del rol
        rol_nombre = self.repository.get_rol_nombre_by_id(user.rol_id) if user.rol_id else None

        # Ensamblar respuesta
        return {
            "usr_id": user.usr_id,
            "usr_usuario": user.usr_usuario,
            "usr_correo": profile.get("usr_correo"),
            "usr_nombre": profile.get("usr_nombre"),
            "usr_apellido": profile.get("usr_apellido"),
            "rol_id": user.rol_id,
            "rol_nombre": rol_nombre,
            "usr_activo": user.usr_activo,
            # Campos de perfil opcionales
            "dni": profile.get("dni"),
            "avatar_url": profile.get("avatar_url"),
            "telefono": profile.get("telefono"),
            "direccion": profile.get("direccion"),
            "genero": profile.get("genero"),
            "fecha_nac": profile.get("fecha_nac"),
            "idioma": profile.get("idioma"),
        }

    def update_user_profile(self, usr_id: int, profile_data: dict[str, Any]) -> dict[str, Any]:
        """
        Caso de uso: Actualizar perfil del usuario.

        Args:
            usr_id: ID del usuario
            profile_data: Datos del perfil a actualizar

        Returns:
            Perfil actualizado

        Raises:
            HTTPException: Si el usuario no existe o hay error
        """
        user = self.repository.get_user_by_id(usr_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        try:
            updated = self.repository.update_user_profile(usr_id, profile_data) or {}

            # Retornar perfil completo
            return {
                "usr_id": user.usr_id,
                "usr_usuario": user.usr_usuario,
                "usr_correo": updated.get("usr_correo"),
                "usr_nombre": updated.get("usr_nombre"),
                "usr_apellido": updated.get("usr_apellido"),
                "rol_id": user.rol_id,
                "usr_activo": user.usr_activo,
                "dni": updated.get("dni"),
                "avatar_url": updated.get("avatar_url"),
                "telefono": updated.get("telefono"),
                "direccion": updated.get("direccion"),
                "genero": updated.get("genero"),
                "fecha_nac": updated.get("fecha_nac"),
                "idioma": updated.get("idioma"),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al actualizar perfil: {str(e)}")

    def change_user_role(
        self, usr_id: int, rol_codigo: str, requesting_user_id: int
    ) -> dict[str, Any]:
        """
        Caso de uso: Cambiar rol de un usuario.

        Args:
            usr_id: ID del usuario a cambiar
            rol_codigo: Código del nuevo rol
            requesting_user_id: ID del usuario que solicita el cambio

        Returns:
            Información del cambio de rol

        Raises:
            HTTPException: Si no tiene permisos o hay error
        """
        # Verificar que el usuario solicitante tiene permisos (debe ser ADMIN)
        requesting_user = self.repository.get_user_by_id(requesting_user_id)
        if not requesting_user:
            raise HTTPException(status_code=404, detail="Usuario solicitante no encontrado")

        requesting_role_code = self.repository.get_role_code_by_id(requesting_user.rol_id)

        # Validar permisos (solo ADMIN puede cambiar roles, excepto cambio propio a TUTOR/PADRE)
        is_self_request = requesting_user_id == usr_id

        if not is_self_request and requesting_role_code != "ADMIN":
            raise HTTPException(
                status_code=403,
                detail="Solo administradores pueden cambiar roles de otros usuarios",
            )

        if is_self_request and rol_codigo not in ("TUTOR", "PADRE", "PADRES"):
            raise HTTPException(
                status_code=403, detail="Solo puedes cambiar tu rol a TUTOR o PADRE"
            )

        # Cambiar rol
        try:
            result = self.repository.change_user_role(usr_id, rol_codigo)
            if not result:
                raise HTTPException(status_code=400, detail="No se pudo cambiar el rol")

            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al cambiar rol: {str(e)}")

    def list_users_admin(self) -> list[dict[str, Any]]:
        """Caso de uso: Listar usuarios para administración."""
        try:
            return self.repository.admin_list_users()
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Error al listar usuarios: {exc}") from exc

    def reset_password_admin(self, usr_id: int, plain_password: str) -> None:
        """Caso de uso: Resetear contraseña de un usuario por admin."""
        hashed_password = self.password_service.hash_password(plain_password)
        try:
            success = self.repository.admin_reset_password(usr_id, hashed_password)
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Error al resetear la contraseña: {exc}"
            ) from exc

        if not success:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {usr_id} no encontrado")

    def toggle_user_active_admin(self, usr_id: int, actor_id: int) -> dict[str, Any]:
        """Caso de uso: Alternar estado activo/inactivo de un usuario."""
        usuario = self.repository.get_user_by_id(usr_id)
        if not usuario:
            raise HTTPException(status_code=404, detail=f"Usuario con ID {usr_id} no encontrado")

        if usr_id == actor_id:
            raise HTTPException(status_code=400, detail="No puedes desactivar tu propia cuenta")

        try:
            result = self.repository.admin_toggle_active(usr_id, actor_id)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Error al cambiar estado del usuario: {exc}"
            ) from exc

        if not result or not result.get("affected_rows"):
            raise HTTPException(
                status_code=500, detail="No se pudo actualizar el estado del usuario"
            )

        return {
            "usr_usuario": result.get("usr_usuario"),
            "usr_activo": result.get("usr_activo"),
        }

    def create_role(self, rol_codigo: str, rol_nombre: str) -> Any:
        """
        Caso de uso: Crear un nuevo rol.

        Args:
            rol_codigo: Código del rol
            rol_nombre: Nombre del rol

        Returns:
            Rol creado

        Raises:
            HTTPException: Si hay error
        """
        try:
            return self.repository.insert_rol(rol_codigo, rol_nombre)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al crear rol: {str(e)}")

    def delete_user_account(self, usr_id: int) -> dict[str, Any]:
        """
        Caso de uso: Anonimizar y desactivar la cuenta de un usuario.
        """
        user = self.repository.get_user_by_id(usr_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        try:
            success = self.repository.anonymize_user_account(usr_id)
        except Exception as exc:
            raise HTTPException(
                status_code=500, detail=f"Error al eliminar la cuenta: {str(exc)}"
            ) from exc

        if not success:
            raise HTTPException(status_code=500, detail="No se pudo eliminar la cuenta")

        return {"detail": "Cuenta eliminada y datos personales anonimizados"}
