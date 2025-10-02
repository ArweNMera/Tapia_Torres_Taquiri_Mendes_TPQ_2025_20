from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from enum import Enum

class SexoEnum(str, Enum):
    M = "M"
    F = "F"

class NinoCreate(BaseModel):
    nin_nombres: str = Field(..., min_length=2, max_length=150, description="Nombres del niño")
    nin_fecha_nac: date = Field(..., description="Fecha de nacimiento")
    nin_sexo: SexoEnum = Field(..., description="Sexo del niño (M/F)")
    ent_id: Optional[int] = Field(None, description="ID de la entidad (hospital, clínica, etc.)")

class NinoUpdate(BaseModel):
    nin_nombres: Optional[str] = Field(None, min_length=2, max_length=150)
    ent_id: Optional[int] = None
    nin_fecha_nac: Optional[date] = None

class NinoResponse(BaseModel):
    nin_id: int
    nin_nombres: str
    nin_fecha_nac: date
    nin_sexo: str
    ent_id: Optional[int] = None
    ent_nombre: Optional[str] = None
    ent_codigo: Optional[str] = None
    ent_direccion: Optional[str] = None
    ent_departamento: Optional[str] = None
    ent_provincia: Optional[str] = None
    ent_distrito: Optional[str] = None
    edad_meses: int
    creado_en: Optional[str] = None
    actualizado_en: Optional[str] = None

    class Config:
        from_attributes = True

# Schemas para alergias
class AlergiaCreate(BaseModel):
    ta_codigo: str = Field(..., description="Código del tipo de alergia")
    severidad: Optional[str] = Field("LEVE", description="LEVE, MODERADA, SEVERA")

class AlergiaResponse(BaseModel):
    na_id: int
    nin_id: int
    ta_codigo: str
    ta_nombre: str
    ta_categoria: str
    na_severidad: str
    creado_en: str

    class Config:
        from_attributes = True

class TipoAlergiaCreate(BaseModel):
    ta_codigo: str = Field(..., max_length=20, description="Código único")
    ta_nombre: str = Field(..., max_length=100, description="Nombre de la alergia")
    ta_categoria: str = Field(..., description="ALIMENTARIA, MEDICAMENTO, AMBIENTAL")

class TipoAlergiaResponse(BaseModel):
    ta_id: int
    ta_codigo: str
    ta_nombre: str
    ta_categoria: str
    ta_activo: bool
    creado_en: str

    class Config:
        from_attributes = True

class AnthropometryCreate(BaseModel):
    ant_peso_kg: float = Field(..., gt=0, le=200, description="Peso en kilogramos")
    ant_talla_cm: float = Field(..., gt=0, le=250, description="Talla en centímetros")
    ant_fecha: Optional[date] = Field(None, description="Fecha de medición (por defecto hoy)")

class AnthropometryUpdate(BaseModel):
    ant_peso_kg: Optional[float] = Field(None, gt=0, le=200)
    ant_talla_cm: Optional[float] = Field(None, gt=0, le=250)

class AnthropometryResponse(BaseModel):
    ant_id: int
    nin_id: int
    ant_fecha: date
    ant_peso_kg: float
    ant_talla_cm: float
    ant_z_imc: Optional[float] = None
    ant_z_peso_edad: Optional[float] = None
    ant_z_talla_edad: Optional[float] = None
    imc: Optional[float] = None
    creado_en: str

    class Config:
        from_attributes = True

class NutritionalStatusResponse(BaseModel):
    imc: float
    z_score_imc: Optional[float] = None
    classification: str  # "bajo_peso", "normal", "sobrepeso", "obesidad"
    percentile: Optional[float] = None
    recommendations: List[str] = []
    risk_level: str  # "BAJO", "MODERADO", "ALTO"

class NinoWithAnthropometry(BaseModel):
    nino: NinoResponse
    antropometrias: List[AnthropometryResponse] = []
    alergias: List[AlergiaResponse] = []
    ultimo_estado_nutricional: Optional[NutritionalStatusResponse] = None

class CreateChildProfileRequest(BaseModel):
    nino: NinoCreate
    antropometria: AnthropometryCreate

class CreateChildProfileResponse(BaseModel):
    nino: NinoResponse
    antropometria: AnthropometryResponse
    estado_nutricional: NutritionalStatusResponse
    message: str = "Perfil del niño creado exitosamente"

class AssignTutorRequest(BaseModel):
    usr_id_tutor: int = Field(..., description="Identificador del tutor o padre")
