from sqlalchemy import text
from sqlalchemy.orm import Session
from app.schemas.usuarios import UserRegister
from app.schemas.auth import UserResponse
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], default="pbkdf2_sha256", pbkdf2_sha256__default_rounds=100, pbkdf2_sha256__default_salt_size=8, deprecated="auto")

class UsuariosRepository:
    def __init__(self, db: Session):
        self.db = db

    def insert_user(self, user_data: UserRegister):
        hashed_password = pwd_context.hash(user_data.contrasena)
        
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

    def insert_rol(self, rol_codigo: str, rol_nombre: str):
        result = self.db.execute(text("CALL sp_roles_insertar(:rol_codigo, :rol_nombre)"), {
            "rol_codigo": rol_codigo,
            "rol_nombre": rol_nombre
        }).fetchone()
        
        self.db.commit()
        return result
