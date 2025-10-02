"""
Interface abstracta para el repositorio de usuarios.
Define el contrato que debe cumplir cualquier implementación.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.schemas.usuarios import UserRegister, UserProfile


class IUsuariosRepository(ABC):
    """Interface para operaciones de usuarios en la capa de persistencia"""
    
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[Any]:
        """Obtener usuario por nombre de usuario"""
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Obtener usuario por correo electrónico"""
        pass
    
    @abstractmethod
    def get_user_by_id(self, usr_id: int) -> Optional[Any]:
        """Obtener usuario por ID"""
        pass
    
    @abstractmethod
    def username_exists(self, username: str) -> bool:
        """Verificar si existe un nombre de usuario"""
        pass
    
    @abstractmethod
    def insert_user(self, user_data: UserRegister) -> Optional[Any]:
        """Crear un nuevo usuario"""
        pass
    
    @abstractmethod
    def get_user_profile(self, usr_id: int) -> Optional[Dict[str, Any]]:
        """Obtener perfil completo del usuario"""
        pass
    
    @abstractmethod
    def update_user_profile(self, usr_id: int, profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar perfil del usuario"""
        pass
    
    @abstractmethod
    def ensure_profile_avatar(self, usr_id: int, avatar_url: str, telefono: Optional[str], idioma: Optional[str]) -> None:
        """Asegurar que existe el perfil con avatar del usuario"""
        pass
    
    @abstractmethod
    def get_role_code_by_id(self, rol_id: int) -> Optional[str]:
        """Obtener código de rol por ID"""
        pass
    
    @abstractmethod
    def change_user_role(self, usr_id: int, rol_codigo: str) -> Optional[Dict[str, Any]]:
        """Cambiar rol de un usuario"""
        pass
    
    @abstractmethod
    def insert_rol(self, rol_codigo: str, rol_nombre: str) -> Any:
        """Insertar un nuevo rol"""
        pass
