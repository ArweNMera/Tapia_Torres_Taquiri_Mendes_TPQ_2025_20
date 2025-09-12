from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.schemas.usuarios import UserRegister
from app.schemas.auth import Token
from app.application.ninos_service import register_user
from app.application.riesgo_service import insert_rol
from pydantic import BaseModel

class RolInsert(BaseModel):
    rol_codigo: str
    rol_nombre: str

class RolResponse(BaseModel):
    rol_id: int
    msg: str

router = APIRouter()

@router.post("/register", response_model=Token)
def register(user_register: UserRegister, db: Session = Depends(get_db)):
    return register_user(db, user_register)

@router.post("/roles", response_model=RolResponse)
def create_rol(rol_insert: RolInsert, db: Session = Depends(get_db)):
    result = insert_rol(db, rol_insert.rol_codigo, rol_insert.rol_nombre)
    return RolResponse(rol_id=result.rol_id, msg=result.msg)
