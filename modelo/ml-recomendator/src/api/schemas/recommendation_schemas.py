"""
Schemas Pydantic para validación de entrada/salida de la API
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NutritionStatusEnum(str, Enum):
    """Estados nutricionales posibles"""

    DESNUTRICION_SEVERA = "DESNUTRICION_SEVERA"
    DESNUTRICION_MODERADA = "DESNUTRICION_MODERADA"
    RIESGO_DESNUTRICION = "RIESGO_DESNUTRICION"
    NORMAL = "NORMAL"
    RIESGO_SOBREPESO = "RIESGO_SOBREPESO"
    SOBREPESO = "SOBREPESO"
    OBESIDAD = "OBESIDAD"


class PredictionRequest(BaseModel):
    """Request para predicción de estado nutricional"""

    age_months: int = Field(..., ge=0, le=240, description="Edad en meses (0-240)")
    sex: str = Field(..., pattern="^[MF]$", description="Sexo: M o F")
    weight_kg: float = Field(..., gt=0, description="Peso en kg")
    height_cm: float = Field(..., gt=0, description="Altura en cm")
    bmi: Optional[float] = Field(None, gt=0, description="BMI calculado")
    baz: Optional[float] = Field(None, description="BAZ (Z-score)")

    class Config:
        schema_extra = {
            "example": {
                "age_months": 60,
                "sex": "M",
                "weight_kg": 18.5,
                "height_cm": 110.0,
                "bmi": 15.3,
                "baz": 0.5,
            }
        }


class PredictionResponse(BaseModel):
    """Response de predicción"""

    nutrition_status: NutritionStatusEnum
    confidence: float = Field(..., ge=0, le=1, description="Confianza de predicción 0-1")
    model_version: str


class MealRecommendationRequest(BaseModel):
    """Request para generar recomendaciones"""

    nutrition_status: NutritionStatusEnum
    allergies: List[str] = Field(default_factory=list, description="Lista de alergias")
    preferences: Dict[str, float] = Field(
        default_factory=dict, description="Preferencias históricas: {menu_id: rating (0-5)}"
    )
    num_meals: int = Field(default=7, ge=1, le=30, description="Número de menús a recomendar")
    include_reasons: bool = Field(default=True, description="Incluir razones de recomendación")

    class Config:
        schema_extra = {
            "example": {
                "nutrition_status": "NORMAL",
                "allergies": ["maní", "camarón"],
                "preferences": {"menu_1": 4.5, "menu_2": 3.0},
                "num_meals": 7,
                "include_reasons": True,
            }
        }


class MealInfo(BaseModel):
    """Información de un menú"""

    menu_id: int
    nombre: str
    descripcion: Optional[str] = None
    ingredientes: List[str] = Field(default_factory=list)
    alergenos: List[str] = Field(default_factory=list)
    kcal: Optional[float] = None
    proteina_g: Optional[float] = None
    carbos_g: Optional[float] = None
    grasas_g: Optional[float] = None


class RecommendedMeal(BaseModel):
    """Menú recomendado con razones"""

    menu: MealInfo
    score: float = Field(..., ge=0, le=1, description="Score de relevancia 0-1")
    reasons: List[str] = Field(default_factory=list, description="Por qué se recomienda")
    rating_usuario: Optional[float] = Field(
        None, ge=0, le=5, description="Rating previo del usuario"
    )


class MealRecommendationResponse(BaseModel):
    """Response con recomendaciones"""

    recommendations: List[RecommendedMeal]
    total_recommended: int
    nutrition_status_used: NutritionStatusEnum
    model_version: str


class DailyMealSlot(BaseModel):
    """Slot de menú en el día"""

    slot: str = Field(..., description="Desayuno, Almuerzo, Merienda, Cena")
    recommended_meal: RecommendedMeal


class DayMealPlan(BaseModel):
    """Plan de menús para un día"""

    day: str = Field(..., description="Nombre del día")
    day_number: int = Field(..., ge=1, le=7)
    slots: List[DailyMealSlot]


class NutritionalProfile(BaseModel):
    """Perfil nutricional detallado del niño"""

    edad_meses: Optional[int] = Field(None, description="Edad en meses")
    peso_kg: Optional[float] = Field(None, description="Peso en kg")
    talla_cm: Optional[float] = Field(None, description="Talla en cm")
    calorias_diarias: Optional[int] = Field(None, description="Calorías diarias requeridas")
    proteinas_g: Optional[float] = Field(None, description="Proteínas diarias (g)")
    carbohidratos_g: Optional[float] = Field(None, description="Carbohidratos diarios (g)")
    grasas_g: Optional[float] = Field(None, description="Grasas diarias (g)")
    factor_actividad: Optional[float] = Field(1.5, description="Factor de actividad física")


class WeeklyMealPlanRequest(BaseModel):
    """Request para generar plan semanal"""

    child_id: Optional[str] = Field(default="default", description="ID del niño")
    nutrition_status: NutritionStatusEnum
    allergies: List[str] = Field(default_factory=list)
    preferences: Dict[str, float] = Field(default_factory=dict)
    days: int = Field(default=7, ge=1, le=30, description="Número de días a planificar")
    include_reasons: bool = Field(default=True)
    nutritional_profile: Optional[NutritionalProfile] = Field(
        None, description="Perfil nutricional del niño"
    )

    class Config:
        schema_extra = {
            "example": {
                "child_id": "123",
                "nutrition_status": "NORMAL",
                "allergies": ["maní"],
                "preferences": {},
                "days": 7,
                "include_reasons": True,
                "nutritional_profile": {
                    "edad_meses": 36,
                    "peso_kg": 15.5,
                    "talla_cm": 95.0,
                    "calorias_diarias": 1400,
                    "proteinas_g": 20.0,
                    "carbohidratos_g": 180.0,
                    "grasas_g": 45.0,
                    "factor_actividad": 1.5,
                },
            }
        }


class WeeklyMealPlanResponse(BaseModel):
    """Response con plan semanal (7 días × 3 comidas)"""

    weekly_plan: List[Dict[str, Any]] = Field(default_factory=list, description="Plan semanal")
    total_days: int = Field(..., description="Total de días")
    nutrition_status: Optional[str] = Field(None, description="Estado nutricional")
    nutrition_status_used: Optional[NutritionStatusEnum] = Field(
        None, description="Estado nutricional usado"
    )
    allergies_considered: Optional[List[str]] = Field(None, description="Alergias consideradas")
    model_version: Optional[str] = Field(None, description="Versión del modelo")
    meals_per_day: Optional[int] = Field(default=3, description="Comidas por día")
    total_meals: Optional[int] = Field(None, description="Total de comidas")


class HealthCheckResponse(BaseModel):
    """Response de health check"""

    status: str = Field(default="ok", description="Estado del servicio")
    service: str = Field(default="ml-recomendator", description="Nombre del servicio")
    model_loaded: bool = Field(..., description="¿Modelo cargado?")
    model_version: str = Field(..., description="Versión del modelo")
    accuracy: Optional[float] = Field(None, description="Accuracy del modelo")


class ModelInfoResponse(BaseModel):
    """Información del modelo"""

    model_type: str
    version: str
    accuracy: float
    features_count: int
    classes: List[str]
    features: List[str]
