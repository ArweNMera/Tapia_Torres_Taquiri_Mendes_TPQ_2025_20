"""
Servicio de infraestructura para Google OAuth.
Encapsula la lógica de autenticación con Google.
"""
from typing import Dict, Tuple
from urllib.parse import urlencode, urlparse, parse_qsl, urlunparse
from datetime import datetime, timedelta

import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from fastapi import HTTPException
from jose import jwt, JWTError

from app.core.config import settings


class GoogleOAuthClient:
    """Cliente para operaciones de Google OAuth"""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.token_url = "https://oauth2.googleapis.com/token"
        self.userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        # Ya no necesitamos almacenamiento en memoria, usamos JWT
    
    def verify_id_token(self, id_token_value: str) -> Dict[str, any]:
        """
        Verificar token de Google.
        
        Args:
            id_token_value: Token ID de Google
            
        Returns:
            Información del usuario extraída del token
            
        Raises:
            HTTPException: Si el token es inválido
        """
        if not self.client_id:
            raise HTTPException(
                status_code=500, 
                detail="Google Sign-In no está configurado en el backend"
            )
        
        try:
            id_info = google_id_token.verify_oauth2_token(
                id_token_value,
                google_requests.Request(),
                self.client_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Token de Google inválido") from exc
        
        # Validar emisor
        issuer = id_info.get("iss")
        if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
            raise HTTPException(status_code=400, detail="Token de Google con emisor no válido")
        
        # Validar que el email esté verificado
        if not id_info.get("email_verified", False):
            raise HTTPException(status_code=400, detail="El correo de Google no está verificado")
        
        return id_info
    
    def build_authorization_url(self, redirect_target: str) -> str:
        """
        Construir URL de autorización de Google.
        
        Args:
            redirect_target: URL a la que redirigir después del login
            
        Returns:
            URL completa de autorización de Google
        """
        if not self.client_id or not self.redirect_uri:
            raise HTTPException(
                status_code=500, 
                detail="Credenciales de Google no configuradas"
            )
        
        # Generar estado JWT con expiración de 10 minutos
        expires = datetime.utcnow() + timedelta(minutes=10)
        state_payload = {
            "redirect_to": redirect_target,
            "exp": expires
        }
        state = jwt.encode(state_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent",
        }
        
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        return f"{base_url}?{urlencode(params)}"
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, str]:
        """
        Intercambiar código de autorización por tokens.
        
        Args:
            code: Código de autorización de Google
            
        Returns:
            Diccionario con access_token, id_token, etc.
            
        Raises:
            HTTPException: Si hay error en el intercambio
        """
        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        try:
            response = requests.post(self.token_url, data=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=400, 
                detail=f"Error al obtener tokens de Google: {str(exc)}"
            ) from exc
    
    def get_user_info(self, access_token: str) -> Dict[str, any]:
        """
        Obtener información del usuario usando access token.
        
        Args:
            access_token: Token de acceso de Google
            
        Returns:
            Información del usuario
            
        Raises:
            HTTPException: Si hay error al obtener la info
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(self.userinfo_url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise HTTPException(
                status_code=400, 
                detail=f"Error al obtener info de Google: {str(exc)}"
            ) from exc
    
    def resolve_redirect_from_state(self, state: str) -> str:
        """
        Resolver URL de redirección desde el estado JWT.
        
        Args:
            state: Estado JWT generado
            
        Returns:
            URL de redirección original
            
        Raises:
            HTTPException: Si el estado es inválido o expirado
        """
        try:
            # Decodificar el JWT state
            payload = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            redirect_target = payload.get("redirect_to")
            
            if not redirect_target:
                raise HTTPException(
                    status_code=400,
                    detail="Estado de OAuth inválido: falta redirect_to"
                )
            
            return redirect_target
            
        except JWTError as exc:
            raise HTTPException(
                status_code=400, 
                detail="Estado de OAuth inválido o expirado"
            ) from exc
    
    def build_redirect_url(
        self, 
        target: str, 
        token: str = None, 
        avatar_url: str = None, 
        error: str = None
    ) -> str:
        """
        Construir URL de redirección con parámetros.
        
        Args:
            target: URL base de redirección
            token: Token JWT (opcional)
            avatar_url: URL del avatar (opcional)
            error: Mensaje de error (opcional)
            
        Returns:
            URL completa de redirección
        """
        parsed = urlparse(target)
        query_params = dict(parse_qsl(parsed.query))
        
        if token:
            query_params["google_token"] = token
            query_params["token_type"] = "bearer"
        if avatar_url:
            query_params["google_avatar"] = avatar_url
        if error:
            query_params["google_error"] = error
        
        new_query = urlencode(query_params)
        redirect_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))
        
        return redirect_url
