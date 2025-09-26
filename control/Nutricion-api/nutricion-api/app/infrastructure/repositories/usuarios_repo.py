from sqlalchemy import text
from sqlalchemy.orm import Session
from app.schemas.usuarios import UserRegister, UserProfile
from app.schemas.auth import UserResponse
from passlib.context import CryptContext
from typing import Optional, Dict

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], default="pbkdf2_sha256", pbkdf2_sha256__default_rounds=100, pbkdf2_sha256__default_salt_size=8, deprecated="auto")

class UsuariosRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert_user(self, user_data: UserRegister):
        hashed_password = pwd_context.hash(user_data.contrasena)
        
        # Usar sp_usuarios_registrar para registro básico
        result = self.db.execute(text("CALL sp_usuarios_registrar(:nombres, :apellidos, :usuario, :correo, :contrasena_hash, :rol_nombre)"), {
            "nombres": user_data.nombres,
            "apellidos": user_data.apellidos,
            "usuario": user_data.usuario,
            "correo": user_data.correo,
            "contrasena_hash": hashed_password,
            "rol_nombre": user_data.rol_nombre
        }).fetchone()
        
        self.db.commit()
        return result

    def update_user_profile(self, usr_id: int, profile_data: dict):
        """Actualizar perfil del usuario con sp_usuarios_perfil_guardar"""
        result = self.db.execute(text("CALL sp_usuarios_perfil_guardar(:usr_id, :dni, :nombres, :apellidos, :avatar_url, :telefono, :direccion, :genero, :fecha_nac, :idioma)"), {
            "usr_id": usr_id,
            "dni": profile_data.get('dni'),
            "nombres": profile_data.get('nombres'),
            "apellidos": profile_data.get('apellidos'),
            "avatar_url": profile_data.get('avatar_url'),
            "telefono": profile_data.get('telefono'),
            "direccion": profile_data.get('direccion'),
            "genero": profile_data.get('genero'),
            "fecha_nac": profile_data.get('fecha_nac'),
            "idioma": profile_data.get('idioma', 'es')
        }).fetchone()
        
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

    def get_user_by_username(self, username: str):
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

    def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        row = self.db.execute(
            text(
                """
                SELECT
                    u.usr_id,
                    u.usr_usuario,
                    u.usr_correo,
                    u.usr_nombre,
                    u.usr_apellido,
                    u.rol_id,
                    u.usr_activo,
                    u.usr_contrasena AS password_hash
                FROM usuarios u
                WHERE u.usr_correo = :correo
                LIMIT 1
                """
            ),
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
        row = self.db.execute(
            text(
                "SELECT 1 FROM usuarios WHERE usr_usuario = :usuario LIMIT 1"
            ),
            {"usuario": username},
        ).fetchone()
        return row is not None

    def insert_rol(self, rol_codigo: str, rol_nombre: str):
        result = self.db.execute(text("CALL sp_roles_insertar(:rol_codigo, :rol_nombre)"), {
            "rol_codigo": rol_codigo,
            "rol_nombre": rol_nombre
        }).fetchone()
        
        self.db.commit()
        return result

    def change_user_role(self, usr_id: int, rol_codigo: str) -> Optional[Dict[str, object]]:
        row = self.db.execute(text("CALL sp_usuarios_cambiar_rol(:usr_id, :rol_codigo)"), {
            "usr_id": usr_id,
            "rol_codigo": rol_codigo
        }).fetchone()
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
        row = self.db.execute(text("SELECT rol_codigo FROM roles WHERE rol_id = :rol_id"), {
            "rol_id": rol_id
        }).fetchone()
        return row.rol_codigo if row else None

    def get_user_profile(self, usr_id: int):
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
        telefono_value = (telefono or "").strip() or "000000000"
        idioma_value = (idioma or "es-PE").strip() or "es-PE"

        self.db.execute(
            text(
                """
                INSERT INTO usuarios_perfil (
                    usr_id,
                    usrper_avatar_url,
                    usrper_telefono,
                    usrper_idioma
                ) VALUES (
                    :usr_id,
                    :avatar_url,
                    :telefono,
                    :idioma
                )
                ON DUPLICATE KEY UPDATE
                    usrper_avatar_url = VALUES(usrper_avatar_url)
                """
            ),
            {
                "usr_id": usr_id,
                "avatar_url": avatar_url,
                "telefono": telefono_value[:20],
                "idioma": idioma_value[:10],
            },
        )
        self.db.commit()
