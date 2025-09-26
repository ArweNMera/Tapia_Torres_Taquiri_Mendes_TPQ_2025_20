import re
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from fastapi import Depends, Header, HTTPException
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import requests as http_requests

from app.core.config import settings
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from app.schemas.auth import Token, TokenData, UserLogin, UserResponse
from app.schemas.usuarios import UserRegister

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

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Obtener el usuario actual a partir del token de autorización
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Token de autorización requerido"
        )
    
    token = authorization.split(" ", 1)[1].strip()
    username = verify_token(token)
    
    repo = UsuariosRepository(db)
    user = repo.get_user_by_username(username)
    
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    if not user.usr_activo:
        raise HTTPException(status_code=401, detail="Usuario inactivo")
    
    return user

def logout_user(_token: str):
    return

def _verify_google_token(id_token_value: str) -> dict:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Sign-In no está configurado en el backend")

    try:
        id_info = google_id_token.verify_oauth2_token(
            id_token_value,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Token de Google inválido") from exc

    issuer = id_info.get("iss")
    if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
        raise HTTPException(status_code=400, detail="Token de Google con emisor no válido")

    if not id_info.get("email_verified", False):
        raise HTTPException(status_code=400, detail="El correo de Google no está verificado")

    return id_info


def _finalize_google_login(db: Session, id_info: dict) -> Token:
    email = id_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Token de Google sin correo electrónico")

    repo = UsuariosRepository(db)
    user = repo.get_user_by_email(email)
    created_new_user = False

    if user and not user.usr_activo:
        raise HTTPException(status_code=401, detail="Usuario inactivo")

    if not user:
        nombres, apellidos = _build_names(id_info)
        username_base = id_info.get("email", "")
        if not username_base:
            username_base = id_info.get("sub", "googleuser")
        username = _ensure_username(repo, username_base.split("@", 1)[0])

        random_password = secrets.token_urlsafe(32)
        register_payload = UserRegister(
            nombres=nombres or "Usuario",
            apellidos=apellidos or "",
            usuario=username,
            correo=email,
            contrasena=random_password,
            rol_nombre="TUTOR",
        )

        try:
            repo.insert_user(register_payload)
        except SQLAlchemyError as exc:
            raise HTTPException(status_code=400, detail="No se pudo registrar el usuario de Google") from exc

        user = repo.get_user_by_email(email)
        created_new_user = True

    if not user:
        raise HTTPException(status_code=500, detail="No se pudo completar el inicio de sesión con Google")

    picture_url: Optional[str] = id_info.get("picture")
    locale_hint: Optional[str] = id_info.get("locale")
    if picture_url:
        profile = repo.get_user_profile(user.usr_id)
        has_avatar = bool(profile and profile.get("avatar_url"))
        if created_new_user or not has_avatar:
            telefono_val = (profile or {}).get("telefono")
            idioma_val = locale_hint or (profile or {}).get("idioma")
            try:
                repo.ensure_profile_avatar(
                    usr_id=user.usr_id,
                    avatar_url=picture_url,
                    telefono=telefono_val,
                    idioma=idioma_val,
                )
            except SQLAlchemyError:
                db.rollback()

    access_token = create_access_token(data={"sub": user.usr_usuario})
    return Token(access_token=access_token, token_type="bearer")


def _sanitize_username_base(value: str) -> str:
    normalized = value.lower()
    normalized = re.sub(r"[^a-z0-9._-]", "", normalized)
    return normalized or "googleuser"


def _build_names(id_info: dict) -> tuple[str, str]:
    given_name = id_info.get("given_name") or ""
    family_name = id_info.get("family_name") or ""

    if given_name or family_name:
        return given_name[:150] or "Usuario", family_name[:150]

    full_name = id_info.get("name")
    if full_name:
        parts = full_name.split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""
        return first[:150], last[:150]

    email = id_info.get("email", "usuario@google")
    local_part = email.split("@", 1)[0]
    return local_part[:150] or "Usuario", ""


def _ensure_username(repo: UsuariosRepository, base: str) -> str:
    candidate_base = _sanitize_username_base(base)[:150]
    candidate = candidate_base or "googleuser"
    suffix = 1
    while repo.username_exists(candidate):
        tail = f"{candidate_base}{suffix}"
        candidate = tail[:150]
        suffix += 1
    return candidate


def login_google_user(db: Session, id_token_value: str) -> Token:
    id_info = _verify_google_token(id_token_value)
    return _finalize_google_login(db, id_info)


def _build_state_token(redirect_to: str) -> str:
    payload = {
        "redirect_to": redirect_to,
        "exp": datetime.utcnow() + timedelta(minutes=5),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def _decode_state_token(state_token: str) -> str:
    try:
        payload = jwt.decode(state_token, settings.SECRET_KEY, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(status_code=400, detail="Estado de Google inválido") from exc

    redirect_to = payload.get("redirect_to")
    if not redirect_to:
        raise HTTPException(status_code=400, detail="Estado de Google incompleto")

    return redirect_to


def _build_allowed_redirects() -> set[str]:
    raw = settings.GOOGLE_ALLOWED_REDIRECTS or ""
    allowed = {url.strip() for url in raw.split(",") if url.strip()}
    if settings.GOOGLE_POST_LOGIN_REDIRECT:
        allowed.add(settings.GOOGLE_POST_LOGIN_REDIRECT)
    return allowed


def _validate_redirect_target(redirect_to: str) -> str:
    if not redirect_to:
        raise HTTPException(status_code=400, detail="redirect_to es requerido")

    parsed = urlparse(redirect_to)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="redirect_to debe ser una URL válida")

    allowed = _build_allowed_redirects()
    if allowed:
        def _same_origin(candidate: str, reference: str) -> bool:
            candidate_parsed = urlparse(candidate)
            reference_parsed = urlparse(reference)
            return (
                candidate_parsed.scheme == reference_parsed.scheme
                and candidate_parsed.netloc == reference_parsed.netloc
            )

        if not any(_same_origin(redirect_to, reference) for reference in allowed):
            raise HTTPException(status_code=400, detail="redirect_to no está permitido")

    return redirect_to


def build_google_authorize_url(redirect_to: str) -> str:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Google Sign-In no está configurado")

    target = _validate_redirect_target(redirect_to or settings.GOOGLE_POST_LOGIN_REDIRECT)
    state_token = _build_state_token(target)
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state_token,
        "prompt": "select_account",
        "access_type": "offline",
        "include_granted_scopes": "true",
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def _exchange_code_for_tokens(code: str) -> Dict[str, object]:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET or not settings.GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Google Sign-In no está configurado correctamente")

    response = http_requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )

    payload: Dict[str, object]
    try:
        payload = response.json()
    except ValueError:
        payload = {}

    if response.status_code != 200:
        detail = payload.get("error_description") or payload.get("error") or response.text
        raise HTTPException(status_code=400, detail=f"No se pudo intercambiar el código de Google: {detail}")

    return payload


def _append_params_to_url(url: str, params: Dict[str, str]) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update(params)
    new_query = urlencode(query)
    return urlunparse(parsed._replace(query=new_query))


def resolve_google_redirect_from_state(state_token: str) -> str:
    redirect_to = _decode_state_token(state_token)
    return _validate_redirect_target(redirect_to)


def complete_google_oauth(db: Session, code: str) -> tuple[Token, Optional[str]]:
    token_response = _exchange_code_for_tokens(code)
    id_token_value = token_response.get("id_token")
    if not id_token_value:
        raise HTTPException(status_code=400, detail="Google no devolvió un id_token")

    id_info = _verify_google_token(id_token_value)
    token = _finalize_google_login(db, id_info)
    return token, id_info.get("picture")


def build_google_oauth_redirect(
    url: str,
    token: Token | None = None,
    error: str | None = None,
    avatar_url: Optional[str] = None,
) -> str:
    params: Dict[str, str] = {}
    if error:
        params["google_error"] = error
    elif token:
        params["google_token"] = token.access_token
        params["token_type"] = token.token_type
        if avatar_url:
            params["google_avatar"] = avatar_url

    if not params:
        return url

    return _append_params_to_url(url, params)
