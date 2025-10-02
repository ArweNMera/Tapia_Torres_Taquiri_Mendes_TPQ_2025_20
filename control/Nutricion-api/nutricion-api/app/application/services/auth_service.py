"""
Servicio de autenticación refactorizado.
Usa servicios de infraestructura en lugar de implementaciones directas.
Sigue los principios de Clean Architecture.
"""
import re
import secrets
from typing import Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import Depends, Header, HTTPException

from app.domain.interfaces.usuarios_repository import IUsuariosRepository
from app.infrastructure.repositories.usuarios_repo import UsuariosRepository
from app.infrastructure.security.password_service import PasswordService
from app.infrastructure.security.jwt_service import JWTService
from app.infrastructure.security.google_oauth_client import GoogleOAuthClient
from app.infrastructure.db.session import get_db
from app.schemas.auth import Token, UserLogin, UserResponse
from app.schemas.usuarios import UserRegister


class AuthService:
    """
    Servicio de autenticación que coordina los casos de uso de login/logout.
    """
    
    def __init__(
        self,
        repository: IUsuariosRepository,
        password_service: PasswordService,
        jwt_service: JWTService,
        google_client: Optional[GoogleOAuthClient] = None
    ):
        self.repository = repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        self.google_client = google_client or GoogleOAuthClient()
    
    def authenticate_user(self, user_login: UserLogin) -> UserResponse:
        """
        Caso de uso: Autenticar usuario con credenciales.
        
        Args:
            user_login: Credenciales del usuario
            
        Returns:
            Usuario autenticado
            
        Raises:
            HTTPException: Si las credenciales son inválidas
        """
        user = self.repository.get_user_by_username(user_login.usuario)
        if not user:
            raise HTTPException(status_code=400, detail="Usuario no encontrado")
        
        # Verificar contraseña usando el servicio de passwords
        if not self.password_service.verify_password(user_login.contrasena, user.password_hash):
            raise HTTPException(status_code=400, detail="Contraseña incorrecta")
        
        if not user.usr_activo:
            raise HTTPException(status_code=401, detail="Usuario inactivo")
        
        return user
    
    def login_user(self, user_login: UserLogin) -> Token:
        """
        Caso de uso: Login de usuario.
        
        Args:
            user_login: Credenciales del usuario
            
        Returns:
            Token de acceso
        """
        user = self.authenticate_user(user_login)
        
        # Crear token usando el servicio de JWT
        access_token = self.jwt_service.create_access_token(
            data={"sub": user.usr_usuario}
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    def get_current_user_from_token(self, token: str) -> UserResponse:
        """
        Caso de uso: Obtener usuario actual desde un token.
        
        Args:
            token: Token JWT
            
        Returns:
            Usuario actual
            
        Raises:
            HTTPException: Si el token es inválido o el usuario no existe
        """
        # Verificar token usando el servicio de JWT
        username = self.jwt_service.verify_token(token)
        
        user = self.repository.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        if not user.usr_activo:
            raise HTTPException(status_code=401, detail="Usuario inactivo")
        
        return user
    
    def login_with_google(self, id_token_value: str) -> Token:
        """
        Caso de uso: Login con Google OAuth.
        
        Args:
            id_token_value: Token de Google
            
        Returns:
            Token de acceso
            
        Raises:
            HTTPException: Si hay error en el proceso de Google OAuth
        """
        # Verificar token de Google usando el cliente OAuth
        id_info = self.google_client.verify_id_token(id_token_value)
        
        # Procesar login/registro
        return self._finalize_google_login(id_info)
    
    def build_google_auth_url(self, redirect_target: str) -> str:
        """
        Caso de uso: Construir URL de autorización de Google.
        
        Args:
            redirect_target: URL a la que redirigir después del login
            
        Returns:
            URL completa de autorización
        """
        return self.google_client.build_authorization_url(redirect_target)
    
    def complete_google_oauth(self, code: str) -> Tuple[Token, Optional[str]]:
        """
        Caso de uso: Completar el flujo OAuth de Google.
        
        Args:
            code: Código de autorización de Google
            
        Returns:
            Tupla con (Token, avatar_url)
            
        Raises:
            HTTPException: Si hay error en el proceso
        """
        # Intercambiar código por tokens
        token_response = self.google_client.exchange_code_for_tokens(code)
        
        id_token_value = token_response.get("id_token")
        if not id_token_value:
            raise HTTPException(status_code=400, detail="Google no devolvió un id_token")
        
        # Verificar y procesar
        id_info = self.google_client.verify_id_token(id_token_value)
        token = self._finalize_google_login(id_info)
        
        return token, id_info.get("picture")
    
    def resolve_google_redirect_from_state(self, state: str) -> str:
        """
        Resolver URL de redirección desde el estado de OAuth.
        
        Args:
            state: Estado de OAuth
            
        Returns:
            URL de redirección
        """
        return self.google_client.resolve_redirect_from_state(state)
    
    def build_google_redirect_url(
        self,
        url: str,
        token: Optional[Token] = None,
        error: Optional[str] = None,
        avatar_url: Optional[str] = None
    ) -> str:
        """
        Construir URL de redirección con parámetros.
        
        Args:
            url: URL base
            token: Token (opcional)
            error: Error (opcional)
            avatar_url: Avatar URL (opcional)
            
        Returns:
            URL completa
        """
        token_str = token.access_token if token else None
        return self.google_client.build_redirect_url(url, token_str, avatar_url, error)
    
    # ========== Métodos privados ==========
    
    def _finalize_google_login(self, id_info: dict) -> Token:
        """
        Finalizar el proceso de login con Google.
        Registra al usuario si no existe.
        """
        email = id_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Token de Google sin correo electrónico")
        
        user = self.repository.get_user_by_email(email)
        created_new_user = False
        
        if user and not user.usr_activo:
            raise HTTPException(status_code=401, detail="Usuario inactivo")
        
        # Si el usuario no existe, registrarlo
        if not user:
            user = self._register_google_user(id_info)
            created_new_user = True
        
        if not user:
            raise HTTPException(
                status_code=500, 
                detail="No se pudo completar el inicio de sesión con Google"
            )
        
        # Actualizar avatar si es necesario
        picture_url = id_info.get("picture")
        if picture_url:
            self._update_user_avatar_if_needed(user, picture_url, id_info, created_new_user)
        
        # Crear token
        access_token = self.jwt_service.create_access_token(
            data={"sub": user.usr_usuario}
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    def _register_google_user(self, id_info: dict) -> Optional[UserResponse]:
        """Registrar un nuevo usuario desde Google"""
        nombres, apellidos = self._extract_names_from_google(id_info)
        username = self._generate_unique_username(id_info)
        
        # Generar contraseña aleatoria (el usuario no la usará)
        random_password = secrets.token_urlsafe(32)
        
        # Hash de la contraseña
        hashed_password = self.password_service.hash_password(random_password)
        
        register_payload = UserRegister(
            nombres=nombres or "Usuario",
            apellidos=apellidos or "",
            usuario=username,
            correo=id_info.get("email"),
            contrasena=hashed_password,  # Ya viene hasheada
            rol_nombre="TUTOR",
        )
        
        try:
            self.repository.insert_user(register_payload)
        except SQLAlchemyError as exc:
            raise HTTPException(
                status_code=400, 
                detail="No se pudo registrar el usuario de Google"
            ) from exc
        
        return self.repository.get_user_by_email(id_info.get("email"))
    
    def _update_user_avatar_if_needed(
        self,
        user: UserResponse,
        picture_url: str,
        id_info: dict,
        created_new_user: bool
    ):
        """Actualizar avatar del usuario si es necesario"""
        try:
            profile = self.repository.get_user_profile(user.usr_id)
            has_avatar = bool(profile and profile.get("avatar_url"))
            
            if created_new_user or not has_avatar:
                telefono_val = (profile or {}).get("telefono")
                locale_hint = id_info.get("locale")
                idioma_val = locale_hint or (profile or {}).get("idioma")
                
                self.repository.ensure_profile_avatar(
                    usr_id=user.usr_id,
                    avatar_url=picture_url,
                    telefono=telefono_val,
                    idioma=idioma_val,
                )
        except SQLAlchemyError:
            # No es crítico si falla la actualización del avatar
            pass
    
    def _extract_names_from_google(self, id_info: dict) -> Tuple[str, str]:
        """Extraer nombres y apellidos del token de Google"""
        given_name = id_info.get("given_name") or ""
        family_name = id_info.get("family_name") or ""
        
        if given_name or family_name:
            return given_name[:150] or "Usuario", family_name[:150]
        
        # Si no vienen separados, intentar dividir el nombre completo
        full_name = id_info.get("name")
        if full_name:
            parts = full_name.split(" ", 1)
            first = parts[0]
            last = parts[1] if len(parts) > 1 else ""
            return first[:150], last[:150]
        
        # Como último recurso, usar el email
        email = id_info.get("email", "usuario@google")
        local_part = email.split("@", 1)[0]
        return local_part[:150] or "Usuario", ""
    
    def _generate_unique_username(self, id_info: dict) -> str:
        """Generar un username único para el usuario de Google"""
        # Intentar con el email
        username_base = id_info.get("email", "")
        if not username_base:
            username_base = id_info.get("sub", "googleuser")
        
        # Limpiar el username
        candidate_base = self._sanitize_username(username_base.split("@", 1)[0])
        candidate = candidate_base or "googleuser"
        
        # Asegurar que sea único
        suffix = 1
        while self.repository.username_exists(candidate):
            tail = f"{candidate_base}{suffix}"
            candidate = tail[:150]
            suffix += 1
        
        return candidate
    
    @staticmethod
    def _sanitize_username(value: str) -> str:
        """Sanitizar un username eliminando caracteres no permitidos"""
        normalized = value.lower()
        normalized = re.sub(r"[^a-z0-9._-]", "", normalized)
        return normalized or "googleuser"


# ========== Funciones globales para compatibilidad con código existente ==========
# TODO: Migrar todos los usos a AuthService

def login_user(db: Session, user_login: UserLogin) -> Token:
    """Función legacy - usar AuthService.login_user()"""
    auth_service = AuthService(
        repository=UsuariosRepository(db),
        password_service=PasswordService(),
        jwt_service=JWTService()
    )
    return auth_service.login_user(user_login)


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Dependency para obtener el usuario actual desde el token.
    Se mantiene como función global para usarla en Depends().
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401, 
            detail="Token de autorización requerido"
        )
    
    token = authorization.split(" ", 1)[1].strip()
    
    # Usar AuthService
    auth_service = AuthService(
        repository=UsuariosRepository(db),
        password_service=PasswordService(),
        jwt_service=JWTService()
    )
    
    return auth_service.get_current_user_from_token(token)


def logout_user(_token: str):
    """Logout (placeholder para futura implementación con blacklist)"""
    return


def login_google_user(db: Session, id_token_value: str) -> Token:
    """Función legacy - usar AuthService.login_with_google()"""
    auth_service = AuthService(
        repository=UsuariosRepository(db),
        password_service=PasswordService(),
        jwt_service=JWTService(),
        google_client=GoogleOAuthClient()
    )
    return auth_service.login_with_google(id_token_value)


def build_google_authorize_url(redirect_to: str) -> str:
    """Función legacy - usar AuthService.build_google_auth_url()"""
    auth_service = AuthService(
        repository=UsuariosRepository(Session()),  # Session dummy
        password_service=PasswordService(),
        jwt_service=JWTService(),
        google_client=GoogleOAuthClient()
    )
    return auth_service.build_google_auth_url(redirect_to)


def resolve_google_redirect_from_state(state_token: str) -> str:
    """Función legacy"""
    auth_service = AuthService(
        repository=UsuariosRepository(Session()),  # Session dummy
        password_service=PasswordService(),
        jwt_service=JWTService(),
        google_client=GoogleOAuthClient()
    )
    return auth_service.resolve_google_redirect_from_state(state_token)


def complete_google_oauth(db: Session, code: str) -> Tuple[Token, Optional[str]]:
    """Función legacy"""
    auth_service = AuthService(
        repository=UsuariosRepository(db),
        password_service=PasswordService(),
        jwt_service=JWTService(),
        google_client=GoogleOAuthClient()
    )
    return auth_service.complete_google_oauth(code)


def build_google_oauth_redirect(
    url: str,
    token: Optional[Token] = None,
    error: Optional[str] = None,
    avatar_url: Optional[str] = None,
) -> str:
    """Función legacy"""
    auth_service = AuthService(
        repository=UsuariosRepository(Session()),  # Session dummy
        password_service=PasswordService(),
        jwt_service=JWTService(),
        google_client=GoogleOAuthClient()
    )
    return auth_service.build_google_redirect_url(url, token, error, avatar_url)
