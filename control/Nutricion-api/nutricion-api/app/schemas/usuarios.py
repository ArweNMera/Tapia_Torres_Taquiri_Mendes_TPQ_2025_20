from datetime import date

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    nombres: str
    apellidos: str
    usuario: str
    correo: EmailStr
    contrasena: str
    rol_nombre: str = "TUTOR"  # Por defecto tutor


class UserProfile(BaseModel):
    dni: str | None = None
    nombres: str | None = None
    apellidos: str | None = None
    avatar_url: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    genero: str | None = None  # 'M', 'F', 'X'
    fecha_nac: date | None = None
    idioma: str | None = "es"


class UserRegisterResponse(BaseModel):
    usr_id: int
    msg: str


class UserRoleChangeRequest(BaseModel):
    rol_codigo: str


class UserRoleChangeResponse(BaseModel):
    usr_id: int
    rol_id: int
    rol_codigo: str
    rol_nombre: str
    msg: str
