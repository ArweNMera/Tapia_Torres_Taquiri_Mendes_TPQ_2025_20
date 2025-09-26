from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.schemas.auth import GoogleLogin, Token, UserLogin
from app.application.auth_service import (
    build_google_authorize_url,
    build_google_oauth_redirect,
    complete_google_oauth,
    login_google_user,
    login_user,
    logout_user,
    resolve_google_redirect_from_state,
)
from app.core.config import settings

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


@router.post("/google", response_model=Token)
def login_with_google(google_login: GoogleLogin, db: Session = Depends(get_db)):
    return login_google_user(db, google_login.id_token)


@router.get("/google/start")
def start_google_login(redirect_to: Optional[str] = Query(None)):
    target = redirect_to or settings.GOOGLE_POST_LOGIN_REDIRECT
    if not target:
        raise HTTPException(status_code=500, detail="No se configuró GOOGLE_POST_LOGIN_REDIRECT")

    authorization_url = build_google_authorize_url(target)
    return RedirectResponse(authorization_url, status_code=302)


@router.get("/google/callback")
def google_callback(
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
):
    fallback_target = settings.GOOGLE_POST_LOGIN_REDIRECT or "http://localhost:5173"

    if not state:
        redirect_url = build_google_oauth_redirect(fallback_target, error="Estado de Google faltante")
        return RedirectResponse(redirect_url, status_code=302)

    try:
        redirect_target = resolve_google_redirect_from_state(state)
    except HTTPException as exc:
        redirect_url = build_google_oauth_redirect(fallback_target, error=str(exc.detail))
        return RedirectResponse(redirect_url, status_code=302)

    if error:
        redirect_url = build_google_oauth_redirect(redirect_target, error=error)
        return RedirectResponse(redirect_url, status_code=302)

    if not code:
        redirect_url = build_google_oauth_redirect(redirect_target, error="Google no entregó código de autorización")
        return RedirectResponse(redirect_url, status_code=302)

    try:
        token, avatar_url = complete_google_oauth(db, code)
    except HTTPException as exc:
        redirect_url = build_google_oauth_redirect(redirect_target, error=str(exc.detail))
        return RedirectResponse(redirect_url, status_code=302)

    redirect_url = build_google_oauth_redirect(redirect_target, token=token, avatar_url=avatar_url)
    return RedirectResponse(redirect_url, status_code=302)
