import secrets
from typing import Any

from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import Session

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

    def insert_user(self, user_data: UserRegister) -> Any | None:
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

    def update_user_profile(
        self, usr_id: int, profile_data: dict[str, Any]
    ) -> dict[str, Any] | None:
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

    def get_user_by_username(self, username: str) -> UserResponse | None:
        result = self.db.execute(
            text("CALL sp_login_get_hash(:usuario)"), {"usuario": username}
        ).fetchone()
        if not result:
            return None

        return UserResponse(
            usr_id=result.usr_id,
            usr_usuario=result.usr_usuario,
            usr_correo=result.usr_correo,
            usr_nombre=result.usr_nombre,
            usr_apellido=result.usr_apellido,
            rol_id=result.rol_id,
            rol_nombre=result.rol_nombre if hasattr(result, "rol_nombre") else None,
            usr_activo=bool(result.usr_activo),
            password_hash=result.password_hash,
        )

    def get_user_by_id(self, usr_id: int) -> UserResponse | None:
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
            rol_nombre=row.rol_nombre if hasattr(row, "rol_nombre") else None,
            usr_activo=bool(row.usr_activo),
            password_hash=row.password_hash,
        )

    def get_user_by_email(self, email: str) -> UserResponse | None:
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
                text("CALL sp_usuarios_existe_username(:username)"), {"username": username}
            ).fetchone()
            return bool(result.existe) if result else False
        except Exception as e:
            raise e

    def insert_rol(self, rol_codigo: str, rol_nombre: str) -> Any | None:
        result = self.db.execute(
            text("CALL sp_roles_insertar(:rol_codigo, :rol_nombre)"),
            {
                "rol_codigo": rol_codigo,
                "rol_nombre": rol_nombre,
            },
        ).fetchone()

        self.db.commit()
        return result

    def change_user_role(self, usr_id: int, rol_codigo: str) -> dict[str, Any] | None:
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
            "msg": getattr(row, "msg", None),
        }

    def get_role_code_by_id(self, rol_id: int) -> str | None:
        """Obtener código de rol usando sp_roles_get_codigo_by_id"""
        row = self.db.execute(
            text("CALL sp_roles_get_codigo_by_id(:rol_id)"), {"rol_id": rol_id}
        ).fetchone()
        return row.rol_codigo if row else None

    def get_user_profile(self, usr_id: int) -> dict[str, Any] | None:
        """Obtener perfil completo del usuario con sp_usuarios_perfil_get"""
        row = self.db.execute(
            text("CALL sp_usuarios_perfil_get(:usr_id)"), {"usr_id": usr_id}
        ).fetchone()
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
        telefono: str | None = None,
        idioma: str | None = None,
    ) -> None:
        """Actualizar o crear perfil con avatar usando procedimiento almacenado."""
        self.db.execute(
            text(
                "CALL sp_usuarios_perfil_actualizar_avatar(:usr_id, :avatar_url, :telefono, :idioma)"
            ),
            {
                "usr_id": usr_id,
                "avatar_url": avatar_url,
                "telefono": telefono,
                "idioma": idioma,
            },
        ).fetchone()
        self.db.commit()

    def anonymize_user_account(self, usr_id: int) -> bool:
        """Anonimizar datos sensibles del usuario y marcar la cuenta como inactiva."""
        suffix = secrets.token_hex(6)
        temp_username = f"deleted_{usr_id}_{suffix}"
        temp_email = f"{temp_username}@deleted.local"
        random_password = pwd_context.hash(secrets.token_urlsafe(32))

        result = self.db.execute(
            text(
                "CALL sp_usuarios_anonimizar(:usr_id, :usuario_temp, :correo_temp, :password_hash, :telefono)"
            ),
            {
                "usr_id": usr_id,
                "usuario_temp": temp_username,
                "correo_temp": temp_email,
                "password_hash": random_password,
                "telefono": "000000000",
            },
        )

        self.db.commit()
        row = result.fetchone()
        return bool(row and getattr(row, "affected_rows", 0))

    def get_rol_nombre_by_id(self, rol_id: int) -> str | None:
        """Obtener el nombre del rol por su ID."""
        row = self.db.execute(
            text("CALL sp_roles_nombre_por_id(:rol_id)"), {"rol_id": rol_id}
        ).fetchone()
        return row.rol_nombre if row and hasattr(row, "rol_nombre") else None

    def admin_list_users(self) -> list[dict[str, Any]]:
        """Listar usuarios para administración."""
        result = self.db.execute(text("CALL sp_admin_usuarios_listar()"))
        return [dict(row._mapping) for row in result]

    def admin_reset_password(self, usr_id: int, password_hash: str) -> bool:
        """Resetear contraseña desde administración."""
        row = self.db.execute(
            text("CALL sp_admin_resetear_contrasena(:usr_id, :password_hash)"),
            {"usr_id": usr_id, "password_hash": password_hash},
        ).fetchone()
        self.db.commit()
        return bool(row and getattr(row, "affected_rows", 0))

    def admin_toggle_active(self, usr_id: int, actor_id: int) -> dict[str, Any]:
        """Alternar estado activo de usuario desde administración."""
        result = self.db.execute(
            text("CALL sp_admin_toggle_usuario(:usr_id, :actor_id)"),
            {"usr_id": usr_id, "actor_id": actor_id},
        )
        self.db.commit()
        row = result.fetchone()
        if not row:
            return {}
        return {
            "affected_rows": getattr(row, "affected_rows", 0),
            "usr_usuario": getattr(row, "usr_usuario", None),
            "usr_activo": bool(getattr(row, "usr_activo", 0)),
        }
