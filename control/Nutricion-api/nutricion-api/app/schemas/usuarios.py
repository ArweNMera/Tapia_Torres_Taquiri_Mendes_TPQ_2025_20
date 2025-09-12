from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    nombres: str
    apellidos: str
    usuario: str
    correo: EmailStr
    contrasena: str
    rol_nombre: str

class UserRegisterResponse(BaseModel):
    usr_id: int
    msg: str
