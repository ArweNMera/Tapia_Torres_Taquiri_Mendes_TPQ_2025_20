from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class SexoEnum(str, Enum):
    M = "M"
    F = "F"


class NinoCreate(BaseModel):
    nin_nombres: str = Field(..., min_length=2, max_length=150, description="Nombres del niño")
    nin_fecha_nac: date = Field(..., description="Fecha de nacimiento")
    nin_sexo: SexoEnum = Field(..., description="Sexo del niño (M/F)")
    ent_id: int | None = Field(None, description="ID de la entidad (hospital, clínica, etc.)")


class NinoUpdate(BaseModel):
    nin_nombres: str | None = Field(None, min_length=2, max_length=150)
    ent_id: int | None = None
    nin_fecha_nac: date | None = None


class NinoResponse(BaseModel):
    nin_id: int
    nin_nombres: str
    nin_fecha_nac: date
    nin_sexo: str
    ent_id: int | None = None
    ent_nombre: str | None = None
    ent_codigo: str | None = None
    ent_direccion: str | None = None
    ent_departamento: str | None = None
    ent_provincia: str | None = None
    ent_distrito: str | None = None
    edad_meses: int
    creado_en: str | None = None
    actualizado_en: str | None = None

    class Config:
        from_attributes = True


# Schemas para alergias
class AlergiaCreate(BaseModel):
    ta_codigo: str = Field(..., description="Código del tipo de alergia")
    severidad: str | None = Field("LEVE", description="LEVE, MODERADA, SEVERA")


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
    ant_fecha: date | None = Field(None, description="Fecha de medición (por defecto hoy)")


class AnthropometryUpdate(BaseModel):
    ant_peso_kg: float | None = Field(None, gt=0, le=200)
    ant_talla_cm: float | None = Field(None, gt=0, le=250)


class AnthropometryResponse(BaseModel):
    ant_id: int
    nin_id: int
    ant_fecha: date
    ant_peso_kg: float
    ant_talla_cm: float
    ant_z_imc: float | None = None
    ant_z_peso_edad: float | None = None
    ant_z_talla_edad: float | None = None
    imc: float | None = None
    creado_en: str

    class Config:
        from_attributes = True


class RecomendacionNutricional(BaseModel):
    icono: str
    titulo: str
    descripcion: str


class NutritionalStatusResponse(BaseModel):
    imc: float
    z_score_imc: float | None = None
    classification: str  # "bajo_peso", "normal", "sobrepeso", "obesidad"
    percentile: float | None = None
    recommendations: list[RecomendacionNutricional | str] = []  # Acepta ambos formatos
    risk_level: str  # "BAJO", "MODERADO", "ALTO"


class NinoWithAnthropometry(BaseModel):
    nino: NinoResponse
    antropometrias: list[AnthropometryResponse] = []
    alergias: list[AlergiaResponse] = []
    ultimo_estado_nutricional: NutritionalStatusResponse | None = None


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
