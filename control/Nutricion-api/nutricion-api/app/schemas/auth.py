from pydantic import BaseModel, EmailStr


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
    usuario: str | None = None


class GoogleLogin(BaseModel):
    id_token: str
    access_token: str | None = None
