import os
from pathlib import Path
from typing import Optional, Dict, Any

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
from firebase_admin import exceptions as firebase_exceptions

from app.core.config import settings


class FirebaseNotConfigured(RuntimeError):
    """Se lanza cuando Firebase no está configurado correctamente."""


_firebase_app: Optional[firebase_admin.App] = None


def _resolve_credentials_path(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate

    base_dir = Path(__file__).resolve().parents[2]  # control/Nutricion-api/nutricion-api
    return (base_dir / candidate).resolve()


def _initialize_firebase_app() -> firebase_admin.App:
    global _firebase_app
    if _firebase_app:
        return _firebase_app

    cred_path = settings.FIREBASE_CREDENTIALS_PATH
    if not cred_path:
        raise FirebaseNotConfigured("FIREBASE_CREDENTIALS_PATH no está configurado")

    resolved_path = _resolve_credentials_path(cred_path)
    if not resolved_path.exists():
        raise FirebaseNotConfigured(f"Archivo de credenciales Firebase no encontrado: {resolved_path}")

    cred = credentials.Certificate(str(resolved_path))

    options: Dict[str, Any] = {}
    if settings.FIREBASE_PROJECT_ID:
        options["projectId"] = settings.FIREBASE_PROJECT_ID

    try:
        _firebase_app = firebase_admin.get_app()
    except ValueError:
        _firebase_app = firebase_admin.initialize_app(cred, options or None)

    return _firebase_app


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verifica un ID token emitido por Firebase Authentication.

    Args:
        id_token: Token JWT enviado por el cliente.

    Returns:
        Dict con los claims del usuario autenticado.

    Raises:
        FirebaseNotConfigured: Si Firebase no está configurado.
        firebase_admin.exceptions.InvalidIdTokenError, etc.: Cuando el token es inválido.
    """
    if not id_token:
        raise firebase_exceptions.InvalidIdTokenError("Token vacío")

    app = _initialize_firebase_app()
    return firebase_auth.verify_id_token(id_token, app=app)
