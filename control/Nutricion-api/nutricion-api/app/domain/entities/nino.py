"""
Entidad Niño - Representa un niño/a en el sistema.
Entidad pura de dominio sin dependencias de frameworks.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


@dataclass
class Nino:
    """
    Entidad de dominio para Niño.
    Representa un niño con sus datos básicos.
    """
    nin_id: int
    nin_nombres: str
    nin_apellidos: str
    nin_fecha_nac: date
    nin_genero: str
    usr_id_tutor: Optional[int] = None
    nin_dni: Optional[str] = None
    nin_autogestiona: bool = False
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de negocio"""
        if not self.nin_nombres or len(self.nin_nombres.strip()) == 0:
            raise ValueError("El nombre del niño no puede estar vacío")
        
        if not self.nin_apellidos or len(self.nin_apellidos.strip()) == 0:
            raise ValueError("Los apellidos del niño no pueden estar vacíos")
        
        if self.nin_genero not in ("M", "F"):
            raise ValueError("El género debe ser 'M' o 'F'")
        
        if self.nin_fecha_nac > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del niño"""
        return f"{self.nin_nombres} {self.nin_apellidos}".strip()
    
    def edad_en_meses(self, fecha_referencia: Optional[date] = None) -> int:
        """Calcula la edad del niño en meses"""
        ref = fecha_referencia or date.today()
        
        meses = (ref.year - self.nin_fecha_nac.year) * 12
        meses += ref.month - self.nin_fecha_nac.month
        
        # Ajustar si el día no ha llegado
        if ref.day < self.nin_fecha_nac.day:
            meses -= 1
        
        return max(0, meses)
    
    def edad_en_anios(self, fecha_referencia: Optional[date] = None) -> int:
        """Calcula la edad del niño en años"""
        ref = fecha_referencia or date.today()
        edad = ref.year - self.nin_fecha_nac.year
        
        # Ajustar si aún no ha cumplido años este año
        if (ref.month, ref.day) < (self.nin_fecha_nac.month, self.nin_fecha_nac.day):
            edad -= 1
        
        return max(0, edad)
    
    def puede_autogestionar(self) -> bool:
        """
        Determina si el niño puede autogestionar su cuenta.
        Regla de negocio: >= 13 años
        """
        return self.edad_en_anios() >= 13


@dataclass
class Antropometria:
    """
    Entidad de dominio para medidas antropométricas.
    Representa una medición de peso y talla de un niño.
    """
    ant_id: int
    nin_id: int
    ant_fecha: date
    ant_edad_meses: int
    ant_peso_kg: Decimal
    ant_talla_cm: Decimal
    ant_z_imc: Optional[Decimal] = None
    ant_z_peso_edad: Optional[Decimal] = None
    ant_z_talla_edad: Optional[Decimal] = None
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de negocio"""
        if self.ant_peso_kg <= 0:
            raise ValueError("El peso debe ser mayor a cero")
        
        if self.ant_talla_cm <= 0:
            raise ValueError("La talla debe ser mayor a cero")
        
        # Validar rangos razonables
        if self.ant_peso_kg > 200:  # 200 kg máximo
            raise ValueError("El peso parece no ser válido")
        
        if self.ant_talla_cm > 250:  # 2.5 metros máximo
            raise ValueError("La talla parece no ser válida")
        
        # Si la talla viene en metros (<=3), convertir a cm
        if self.ant_talla_cm <= 3:
            self.ant_talla_cm = self.ant_talla_cm * 100
    
    def calcular_imc(self) -> Decimal:
        """Calcula el IMC (Índice de Masa Corporal)"""
        talla_metros = self.ant_talla_cm / 100
        imc = self.ant_peso_kg / (talla_metros ** 2)
        return round(imc, 2)
    
    def clasificar_estado_nutricional_por_imc(self) -> str:
        """
        Clasifica el estado nutricional según z-score de IMC.
        Según estándares de la OMS.
        """
        if self.ant_z_imc is None:
            return "NO_EVALUADO"
        
        z = float(self.ant_z_imc)
        
        if z < -3:
            return "DESNUTRICION_SEVERA"
        elif z < -2:
            return "DESNUTRICION"
        elif z < -1:
            return "RIESGO_DESNUTRICION"
        elif z <= 1:
            return "NORMAL"
        elif z <= 2:
            return "SOBREPESO"
        elif z <= 3:
            return "OBESIDAD"
        else:
            return "OBESIDAD_SEVERA"


@dataclass
class Alergia:
    """
    Entidad de dominio para alergias de niños.
    """
    nina_id: int
    nin_id: int
    ta_id: int
    nina_severidad: str
    nina_notas: Optional[str] = None
    nina_diagnosticado_en: Optional[date] = None
    creado_en: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de negocio"""
        severidades_validas = ("LEVE", "MODERADA", "SEVERA")
        if self.nina_severidad not in severidades_validas:
            raise ValueError(f"La severidad debe ser una de: {', '.join(severidades_validas)}")


@dataclass
class TipoAlergia:
    """
    Entidad de dominio para tipos de alergias.
    """
    ta_id: int
    ta_codigo: str
    ta_nombre: str
    ta_categoria: str
    ta_activo: bool = True
    creado_en: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de negocio"""
        if not self.ta_codigo or len(self.ta_codigo.strip()) == 0:
            raise ValueError("El código de tipo de alergia no puede estar vacío")
        
        if not self.ta_nombre or len(self.ta_nombre.strip()) == 0:
            raise ValueError("El nombre de tipo de alergia no puede estar vacío")
