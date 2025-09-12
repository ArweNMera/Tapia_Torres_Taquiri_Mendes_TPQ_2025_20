from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.schemas.auth import UserLogin, Token
from app.application.auth_service import login_user, logout_user

router = APIRouter()

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    return login_user(db, user_login)

@router.post("/logout")
def logout(authorization: str = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=400, detail="Authorization header faltante o inválido")
    token = authorization.split(" ", 1)[1].strip()
    logout_user(token)
    return {"detail": "logout ok (token descartado en cliente)"}

