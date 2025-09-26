from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class UserRegister(BaseModel):
    nombres: str
    apellidos: str
    usuario: str
    correo: EmailStr
    contrasena: str
    rol_nombre: str = "TUTOR"  # Por defecto tutor

class UserProfile(BaseModel):
    dni: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    avatar_url: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    genero: Optional[str] = None  # 'M', 'F', 'X'
    fecha_nac: Optional[date] = None
    idioma: Optional[str] = "es"

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
