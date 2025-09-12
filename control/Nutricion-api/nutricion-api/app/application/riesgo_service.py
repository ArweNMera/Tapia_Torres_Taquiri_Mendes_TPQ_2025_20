from sqlalchemy.orm import Session
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from fastapi import HTTPException

def insert_rol(db: Session, rol_codigo: str, rol_nombre: str):
    repo = UsuariosRepository(db)
    result = repo.insert_rol(rol_codigo, rol_nombre)
    return result
