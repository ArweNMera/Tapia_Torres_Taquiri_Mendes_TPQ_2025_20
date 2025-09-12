from sqlalchemy.orm import Session
from app.schemas.usuarios import UserRegister
from app.schemas.auth import Token
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from app.application.auth_service import create_access_token

def register_user(db: Session, user_register: UserRegister):
    repo = UsuariosRepository(db)
    result = repo.insert_user(user_register)
    
    # Generar token automáticamente después del registro
    access_token = create_access_token(data={"sub": user_register.usuario})
    
    return Token(access_token=access_token, token_type="bearer")
