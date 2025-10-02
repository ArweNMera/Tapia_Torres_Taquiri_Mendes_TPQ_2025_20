"""
Servicio de infraestructura para manejo de contraseñas.
Encapsula la lógica de hashing y verificación.
"""
from passlib.context import CryptContext


class PasswordService:
    """Servicio para operaciones con contraseñas"""
    
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["pbkdf2_sha256"],
            default="pbkdf2_sha256",
            pbkdf2_sha256__default_rounds=100,
            pbkdf2_sha256__default_salt_size=8,
            deprecated="auto"
        )
    
    def hash_password(self, plain_password: str) -> str:
        """
        Hash de una contraseña en texto plano.
        
        Args:
            plain_password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
        """
        return self.pwd_context.hash(plain_password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verificar si una contraseña coincide con su hash.
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Hash almacenado
            
        Returns:
            True si coincide, False en caso contrario
        """
        return self.pwd_context.verify(plain_password, hashed_password)
