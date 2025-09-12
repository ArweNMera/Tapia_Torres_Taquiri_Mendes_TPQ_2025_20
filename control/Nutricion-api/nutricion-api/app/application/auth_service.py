from sqlalchemy.orm import Session
from app.schemas.auth import UserLogin, UserResponse, Token, TokenData
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], default="pbkdf2_sha256", pbkdf2_sha256__default_rounds=100, pbkdf2_sha256__default_salt_size=8, deprecated="auto")

def authenticate_user(db: Session, user_login: UserLogin):
    repo = UsuariosRepository(db)
    user = repo.get_user_by_username(user_login.usuario)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    if not pwd_context.verify(user_login.contrasena, user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def login_user(db: Session, user_login: UserLogin):
    user = authenticate_user(db, user_login)
    access_token = create_access_token(data={"sub": user.usr_usuario})
    return Token(access_token=access_token, token_type="bearer")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def logout_user(_token: str):
    return

