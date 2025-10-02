"""
Interface abstracta para el repositorio de niños.
Define el contrato que debe cumplir cualquier implementación.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class INinosRepository(ABC):
    """Interface para operaciones de niños en la capa de persistencia"""
    
    @abstractmethod
    def crear_nino(self, nino_data: Dict[str, Any]) -> Optional[Any]:
        """Crear un nuevo niño"""
        pass
    
    @abstractmethod
    def actualizar_nino(self, nin_id: int, nino_data: Dict[str, Any]) -> Optional[Any]:
        """Actualizar datos del niño"""
        pass
    
    @abstractmethod
    def obtener_nino(self, nin_id: int) -> Optional[Any]:
        """Obtener datos del niño por ID"""
        pass
    
    @abstractmethod
    def agregar_antropometria(self, nin_id: int, ant_data: Dict[str, Any]) -> Optional[Any]:
        """Agregar medidas antropométricas"""
        pass
    
    @abstractmethod
    def evaluar_estado_nutricional(self, nin_id: int) -> Optional[Any]:
        """Evaluar estado nutricional del niño"""
        pass
    
    @abstractmethod
    def agregar_alergia(self, nin_id: int, alergia_data: Dict[str, Any]) -> Optional[Any]:
        """Agregar alergia al niño"""
        pass
    
    @abstractmethod
    def obtener_alergias(self, nin_id: int) -> List[Dict[str, Any]]:
        """Obtener alergias del niño"""
        pass
    
    @abstractmethod
    def obtener_tipos_alergias(self, q: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Buscar tipos de alergias"""
        pass
    
    @abstractmethod
    def get_perfil_completo(self, nin_id: int) -> Dict[str, Any]:
        """Obtener perfil completo del niño con antropometría"""
        pass
    
    @abstractmethod
    def listar_ninos_tutor(self, usr_id: int) -> List[Dict[str, Any]]:
        """Listar niños de un tutor"""
        pass
    
    @abstractmethod
    def asignar_tutor(self, nin_id: int, usr_id: int) -> Optional[Any]:
        """Asignar tutor a un niño"""
        pass
