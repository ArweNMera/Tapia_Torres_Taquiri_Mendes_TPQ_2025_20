from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from passlib.context import CryptContext

from app.domain.interfaces.usuarios_repository import IUsuariosRepository
from app.schemas.auth import UserResponse
from app.schemas.usuarios import UserRegister

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=100,
    pbkdf2_sha256__default_salt_size=8,
    deprecated="auto",
)


class UsuariosRepository(IUsuariosRepository):
    def __init__(self, db: Session):
        self.db = db

    def insert_user(self, user_data: UserRegister) -> Optional[Any]:
        """Registrar un usuario usando procedimiento almacenado."""
        password_value = user_data.contrasena or ""
        if not password_value.startswith("pbkdf2_sha256$"):
            password_value = pwd_context.hash(password_value)

        result = self.db.execute(
            text(
                "CALL sp_usuarios_registrar(:nombres, :apellidos, :usuario, :correo, :contrasena_hash, :rol_nombre)"
            ),
            {
                "nombres": user_data.nombres,
                "apellidos": user_data.apellidos,
                "usuario": user_data.usuario,
                "correo": user_data.correo,
                "contrasena_hash": password_value,
                "rol_nombre": user_data.rol_nombre,
            },
        ).fetchone()

        self.db.commit()
        return result

    def update_user_profile(self, usr_id: int, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar perfil del usuario con sp_usuarios_perfil_guardar"""
        result = self.db.execute(
            text(
                "CALL sp_usuarios_perfil_guardar(:usr_id, :dni, :nombres, :apellidos, :avatar_url, :telefono, :direccion, :genero, :fecha_nac, :idioma)"
            ),
            {
                "usr_id": usr_id,
                "dni": profile_data.get("dni"),
                "nombres": profile_data.get("nombres"),
                "apellidos": profile_data.get("apellidos"),
                "avatar_url": profile_data.get("avatar_url"),
                "telefono": profile_data.get("telefono"),
                "direccion": profile_data.get("direccion"),
                "genero": profile_data.get("genero"),
                "fecha_nac": profile_data.get("fecha_nac"),
                "idioma": profile_data.get("idioma", "es"),
            },
        ).fetchone()
        
        self.db.commit()
        if not result:
            return None
        # Mapear nombres de columnas del SP a claves esperadas por el frontend
        mapped = {
            "usr_id": result.usr_id,
            "usr_nombre": result.usr_nombre,
            "usr_apellido": result.usr_apellido,
            "dni": getattr(result, "usr_dni", None),
            "usr_correo": result.usr_correo,
            "avatar_url": getattr(result, "avatar", None),
            "telefono": result.telefono,
            "direccion": result.direccion,
            "genero": result.genero,
            "fecha_nac": result.fecha_nac,
            "idioma": result.idioma,
        }
        return mapped

    def get_user_by_username(self, username: str) -> Optional[UserResponse]:
        result = self.db.execute(text("CALL sp_login_get_hash(:usuario)"), {"usuario": username}).fetchone()
        if not result:
            return None

        return UserResponse(
            usr_id=result.usr_id,
            usr_usuario=result.usr_usuario,
            usr_correo=result.usr_correo,
            usr_nombre=result.usr_nombre,
            usr_apellido=result.usr_apellido,
            rol_id=result.rol_id,
            usr_activo=bool(result.usr_activo),
            password_hash=result.password_hash
        )

    def get_user_by_id(self, usr_id: int) -> Optional[UserResponse]:
        row = self.db.execute(
            text("CALL sp_usuarios_obtener_por_id(:usr_id)"),
            {"usr_id": usr_id},
        ).fetchone()

        if not row:
            return None

        return UserResponse(
            usr_id=row.usr_id,
            usr_usuario=row.usr_usuario,
            usr_correo=row.usr_correo,
            usr_nombre=row.usr_nombre,
            usr_apellido=row.usr_apellido,
            rol_id=row.rol_id,
            usr_activo=bool(row.usr_activo),
            password_hash=row.password_hash,
        )

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        row = self.db.execute(
            text("CALL sp_usuarios_obtener_por_email(:correo)"),
            {"correo": email},
        ).fetchone()

        if not row:
            return None

        return UserResponse(
            usr_id=row.usr_id,
            usr_usuario=row.usr_usuario,
            usr_correo=row.usr_correo,
            usr_nombre=row.usr_nombre,
            usr_apellido=row.usr_apellido,
            rol_id=row.rol_id,
            usr_activo=bool(row.usr_activo),
            password_hash=row.password_hash,
        )

    def username_exists(self, username: str) -> bool:
        """Verificar si username existe usando sp_usuarios_existe_username"""
        try:
            result = self.db.execute(
                text("CALL sp_usuarios_existe_username(:username)"),
                {"username": username}
            ).fetchone()
            return bool(result.existe) if result else False
        except Exception as e:
            raise e

    def insert_rol(self, rol_codigo: str, rol_nombre: str) -> Optional[Any]:
        result = self.db.execute(
            text("CALL sp_roles_insertar(:rol_codigo, :rol_nombre)"),
            {
                "rol_codigo": rol_codigo,
                "rol_nombre": rol_nombre,
            },
        ).fetchone()

        self.db.commit()
        return result

    def change_user_role(self, usr_id: int, rol_codigo: str) -> Optional[Dict[str, Any]]:
        row = self.db.execute(
            text("CALL sp_usuarios_cambiar_rol(:usr_id, :rol_codigo)"),
            {
                "usr_id": usr_id,
                "rol_codigo": rol_codigo,
            },
        ).fetchone()
        self.db.commit()
        if not row:
            return None
        return {
            "usr_id": row.usr_id,
            "rol_id": row.rol_id,
            "rol_codigo": getattr(row, "rol_codigo", None),
            "rol_nombre": getattr(row, "rol_nombre", None),
            "msg": getattr(row, "msg", None)
        }

    def get_role_code_by_id(self, rol_id: int) -> Optional[str]:
        """Obtener código de rol usando sp_roles_get_codigo_by_id"""
        row = self.db.execute(text("CALL sp_roles_get_codigo_by_id(:rol_id)"), {
            "rol_id": rol_id
        }).fetchone()
        return row.rol_codigo if row else None

    def get_user_profile(self, usr_id: int) -> Optional[Dict[str, Any]]:
        """Obtener perfil completo del usuario con sp_usuarios_perfil_get"""
        row = self.db.execute(text("CALL sp_usuarios_perfil_get(:usr_id)"), {"usr_id": usr_id}).fetchone()
        if not row:
            return None
        return {
            "usr_id": row.usr_id,
            "usr_nombre": row.usr_nombre,
            "usr_apellido": row.usr_apellido,
            "dni": getattr(row, "usr_dni", None),
            "usr_correo": row.usr_correo,
            "avatar_url": getattr(row, "avatar", None),
            "telefono": row.telefono,
            "direccion": row.direccion,
            "genero": row.genero,
            "fecha_nac": row.fecha_nac,
            "idioma": row.idioma,
        }

    def ensure_profile_avatar(
        self,
        usr_id: int,
        avatar_url: str,
        telefono: Optional[str] = None,
        idioma: Optional[str] = None,
    ) -> None:
        """Actualizar o crear perfil con avatar usando procedimiento almacenado."""
        self.db.execute(
            text("CALL sp_usuarios_perfil_actualizar_avatar(:usr_id, :avatar_url, :telefono, :idioma)"),
            {
                "usr_id": usr_id,
                "avatar_url": avatar_url,
                "telefono": telefono,
                "idioma": idioma,
            },
        ).fetchone()
        self.db.commit()
