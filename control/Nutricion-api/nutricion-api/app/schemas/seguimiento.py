"""
Schemas para el sistema de seguimiento y monitoreo nutricional (PMV3)
"""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field

# ============================================================================
# ENUMS
# ============================================================================


class EstadoAdherenciaEnum(str, Enum):
    """Estado de cumplimiento del plan nutricional"""

    OK = "OK"
    PARCIAL = "PARCIAL"
    NO = "NO"


class DificultadEnum(str, Enum):
    """Nivel de dificultad experimentado"""

    NINGUNA = "NINGUNA"
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"


class SeveridadSintomaEnum(str, Enum):
    """Severidad del síntoma"""

    LEVE = "LEVE"
    MODERADO = "MODERADO"
    SEVERO = "SEVERO"


class TendenciaEnum(str, Enum):
    """Tendencia nutricional"""

    MEJORANDO = "MEJORANDO"
    ESTABLE = "ESTABLE"
    EMPEORANDO = "EMPEORANDO"


class ClasificacionNutricionalEnum(str, Enum):
    """Clasificación nutricional según OMS (7 categorías)"""

    DESNUTRICION_SEVERA = "DESNUTRICION_SEVERA"
    DESNUTRICION_MODERADA = "DESNUTRICION_MODERADA"
    RIESGO_DESNUTRICION = "RIESGO_DESNUTRICION"
    NORMAL = "NORMAL"
    RIESGO_SOBREPESO = "RIESGO_SOBREPESO"
    SOBREPESO = "SOBREPESO"
    OBESIDAD = "OBESIDAD"


# ============================================================================
# ADHERENCIA SCHEMAS
# ============================================================================


class AdherenciaCreate(BaseModel):
    """Schema para registrar adherencia"""

    nin_id: int = Field(..., description="ID del niño")
    men_id: int = Field(..., description="ID del menú")
    mei_id: int | None = Field(None, description="ID del ítem de menú específico")
    fecha: date = Field(..., description="Fecha del registro")
    estado: EstadoAdherenciaEnum = Field(..., description="Estado de cumplimiento")
    porcentaje: float = Field(..., ge=0, le=100, description="Porcentaje de cumplimiento (0-100)")
    dificultad: DificultadEnum = Field(
        DificultadEnum.NINGUNA, description="Nivel de dificultad experimentado"
    )
    comentario: str | None = Field(None, max_length=500, description="Comentarios opcionales")


class AdherenciaUpdate(BaseModel):
    """Schema para actualizar adherencia"""

    estado: EstadoAdherenciaEnum | None = Field(None, description="Estado de cumplimiento")
    porcentaje: float | None = Field(
        None, ge=0, le=100, description="Porcentaje de cumplimiento (0-100)"
    )
    dificultad: DificultadEnum | None = Field(None, description="Nivel de dificultad experimentado")
    comentario: str | None = Field(None, max_length=500, description="Comentarios opcionales")


class AdherenciaResponse(BaseModel):
    """Schema de respuesta para adherencia"""

    adh_id: int
    nin_id: int
    men_id: int | None = None
    mei_id: int | None = None
    fecha: datetime | None = None  # Alias del procedimiento
    estado: str | None = None  # Alias del procedimiento
    porcentaje: float | None = None  # Alias del procedimiento
    dificultad: str | None = None  # Alias del procedimiento
    comentario: str | None = None  # Alias del procedimiento
    # Información del menú asociado
    men_inicio: date | None = None
    men_fin: date | None = None
    mei_comida: str | None = None
    mei_kcal: float | None = None
    # Estadísticas (vienen en cada fila del procedimiento)
    adherencia_promedio: float | None = None
    dias_dificultad_alta: int | None = None

    class Config:
        from_attributes = True


class AdherenciaPromedioResponse(BaseModel):
    """Schema para adherencia promedio"""

    adherencia_promedio: float
    consistencia: float
    total_registros: int
    dias_analizados: int


class AdherenciaHistorialResponse(BaseModel):
    """Schema para historial de adherencia con estadísticas"""

    registros: list[AdherenciaResponse]
    adherencia_promedio: float
    dias_con_dificultad_alta: int


# ============================================================================
# SÍNTOMAS SCHEMAS
# ============================================================================


class SintomaCreate(BaseModel):
    """Schema para registrar síntoma"""

    nin_id: int = Field(..., description="ID del niño")
    fecha: date = Field(..., description="Fecha del síntoma")
    tipo: str = Field(..., max_length=120, description="Tipo de síntoma")
    severidad: SeveridadSintomaEnum = Field(..., description="Severidad del síntoma")
    duracion_dias: int = Field(..., ge=1, le=365, description="Duración en días")
    relacionado_menu: bool = Field(False, description="¿Está relacionado con el menú?")
    notas: str | None = Field(None, max_length=500, description="Notas descriptivas")


class SintomaUpdate(BaseModel):
    """Schema para actualizar síntoma"""

    tipo: str | None = Field(None, max_length=120, description="Tipo de síntoma")
    severidad: SeveridadSintomaEnum | None = Field(None, description="Severidad del síntoma")
    duracion_dias: int | None = Field(None, ge=1, le=365, description="Duración en días")
    relacionado_menu: bool | None = Field(None, description="¿Está relacionado con el menú?")
    notas: str | None = Field(None, max_length=500, description="Notas descriptivas")


class SintomaResponse(BaseModel):
    """Schema de respuesta para síntoma"""

    sin_id: int
    nin_id: int
    # Aceptar ambos nombres (tabla y alias)
    sin_fecha: date | None = None
    fecha: date | None = None
    sin_tipo: str | None = None
    tipo: str | None = None
    sin_severidad: str | None = None
    severidad: str | None = None
    sin_grado: int | None = None
    grado: int | None = None
    sin_duracion_dias: int | None = None
    duracion_dias: int | None = None
    sin_relacionado_menu: bool | None = None
    relacionado_menu: bool | None = None
    sin_notas: str | None = None
    notas: str | None = None
    creado_en: datetime

    class Config:
        from_attributes = True


class SintomaFrecuenciaResponse(BaseModel):
    """Schema para frecuencia de síntomas"""

    frecuencia_total: int
    severidad_promedio: float
    sintomas_recientes_7dias: int
    tiene_sintomas_recientes: bool


# ============================================================================
# EVOLUCIÓN SCHEMAS
# ============================================================================


class EvolucionDataPoint(BaseModel):
    """Punto de datos de evolución"""

    ant_id: int
    ant_fecha: date
    ant_peso_kg: float
    ant_talla_cm: float
    imc: float
    en_z_score_imc: float | None
    en_clasificacion: str | None
    en_nivel_riesgo: str | None
    adherencia_promedio_7dias: float | None
    sintomas_7dias: int


class EvolucionResponse(BaseModel):
    """Schema de respuesta para evolución nutricional"""

    nin_id: int
    nin_nombres: str
    fecha_inicio: date
    fecha_fin: date
    datos: list[EvolucionDataPoint]


class TendenciaResponse(BaseModel):
    """Schema para tendencia nutricional"""

    tendencia: TendenciaEnum
    bmi_velocity: float | None
    weight_velocity: float | None
    height_velocity: float | None
    z_score_trend: float | None
    mediciones_analizadas: int


# ============================================================================
# PREDICCIONES ML SCHEMAS
# ============================================================================


class PrediccionMLCreate(BaseModel):
    """Schema para crear predicción ML (interno)"""

    ant_id: int
    fml_id: int
    clasificacion: ClasificacionNutricionalEnum
    probabilidad: float = Field(..., ge=0, le=1)
    score_riesgo: float
    prob_normal: float = Field(..., ge=0, le=1)
    prob_riesgo: float = Field(..., ge=0, le=1)
    prob_moderado: float = Field(..., ge=0, le=1)
    prob_severo: float = Field(..., ge=0, le=1)
    modelo_tipo: str = Field(..., max_length=50)
    modelo_version: str = Field(..., max_length=20)
    features_json: dict | None = None
    explicacion_json: dict | None = None


class PrediccionMLResponse(BaseModel):
    """Schema de respuesta para predicción ML"""

    pml_id: int
    nin_id: int
    ant_id: int
    fml_id: int
    pml_clasificacion: str
    pml_probabilidad: float
    pml_score_riesgo: float
    pml_prob_normal: float
    pml_prob_riesgo: float
    pml_prob_moderado: float
    pml_prob_severo: float
    pml_modelo_tipo: str
    pml_modelo_version: str
    pml_features_json: dict | None = None
    pml_explicacion_json: dict | None = None
    pml_validado: bool | None = None
    pml_usr_id_validador: int | None = None
    pml_feedback: str | None = None
    pml_fecha_validacion: datetime | None = None
    creado_en: datetime | None = None
    # Datos de antropometría asociada
    ant_fecha: date | None = None
    ant_peso_kg: float | None = None
    ant_talla_cm: float | None = None
    # Datos del validador
    validador_nombre: str | None = None

    class Config:
        from_attributes = True


class ValidarPrediccionRequest(BaseModel):
    """Schema para validar predicción"""

    validado: bool = Field(..., description="¿Es correcta la predicción?")
    feedback: str | None = Field(None, max_length=500, description="Comentarios del nutricionista")


# ============================================================================
# ALERTAS SCHEMAS
# ============================================================================


class AlertaResponse(BaseModel):
    """Schema de respuesta para alerta"""

    not_id: int
    not_tipo: str
    not_payload: dict
    not_leido: bool
    creado_en: datetime

    class Config:
        from_attributes = True


class VerificarAlertasResponse(BaseModel):
    """Schema para respuesta de verificación de alertas"""

    alertas_generadas: list[AlertaResponse]
    total_alertas: int
