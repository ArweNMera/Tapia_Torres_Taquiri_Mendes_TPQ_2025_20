from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    usuario: str
    contrasena: str

class UserResponse(BaseModel):
    usr_id: int
    usr_usuario: str
    usr_correo: EmailStr
    usr_nombre: str
    usr_apellido: str
    rol_id: int
    usr_activo: bool
    password_hash: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    usuario: Optional[str] = None


class GoogleLogin(BaseModel):
    id_token: str
    access_token: Optional[str] = None
