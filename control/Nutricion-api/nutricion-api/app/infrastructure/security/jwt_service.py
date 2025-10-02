"""
Servicio de infraestructura para manejo de JWT (JSON Web Tokens).
Encapsula la lógica de creación y verificación de tokens.
"""
from datetime import datetime, timedelta
from typing import Dict, Optional

from jose import JWTError, jwt
from fastapi import HTTPException

from app.core.config import settings


class JWTService:
    """Servicio para operaciones con JWT"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    def create_access_token(
        self, 
        data: Dict[str, any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crear un token de acceso JWT.
        
        Args:
            data: Datos a codificar en el token (ej: {"sub": username})
            expires_delta: Tiempo de expiración personalizado
            
        Returns:
            Token JWT codificado
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> str:
        """
        Verificar y decodificar un token JWT.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            Username extraído del token (subject)
            
        Raises:
            HTTPException: Si el token es inválido o expiró
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            
            if username is None:
                raise HTTPException(status_code=401, detail="Token inválido: no contiene subject")
            
            return username
            
        except JWTError as e:
            raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
    
    def decode_token(self, token: str) -> Dict[str, any]:
        """
        Decodificar token sin verificar (usar con precaución).
        
        Args:
            token: Token JWT a decodificar
            
        Returns:
            Payload del token
        """
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return {}
