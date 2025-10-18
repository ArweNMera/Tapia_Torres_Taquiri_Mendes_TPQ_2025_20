"""
Schemas para planes de comidas
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class TipoComida(str, Enum):
    DESAYUNO = "DESAYUNO"
    ALMUERZO = "ALMUERZO"
    CENA = "CENA"
    REFACCION = "REFACCION"


class PerfilNutricionalResponse(BaseModel):
    pnn_id: int
    nin_id: int
    pnn_calorias_diarias: int
    pnn_proteinas_g: float
    pnn_carbohidratos_g: float
    pnn_grasas_g: float
    pnn_hierro_mg: Optional[float] = None
    pnn_calcio_mg: Optional[float] = None
    pnn_vitamina_a_ug: Optional[float] = None
    pnn_vitamina_c_mg: Optional[float] = None
    pnn_zinc_mg: Optional[float] = None
    pnn_fibra_g: Optional[float] = None
    pnn_edad_meses: int
    pnn_peso_kg: Optional[float] = None
    pnn_talla_cm: Optional[float] = None
    pnn_clasificacion: Optional[str] = None
    pnn_metodo_calculo: str
    pnn_fecha_calculo: datetime
    pnn_vigente: bool


class IngredienteReceta(BaseModel):
    ali_nombre: str
    cantidad: float
    unidad: str


class ComidaPlanResponse(BaseModel):
    mei_id: Optional[int] = None
    rec_id: int
    rec_nombre: str
    rec_instrucciones: str
    mei_kcal: int
    ingredientes: List[IngredienteReceta] = []
    match_preferencias: List[str] = []


class DiaPlanResponse(BaseModel):
    dia_idx: int
    dia_nombre: str
    fecha: date
    desayuno: ComidaPlanResponse
    almuerzo: ComidaPlanResponse
    cena: ComidaPlanResponse
    total_dia: int


class ResumenPlan(BaseModel):
    calorias_promedio_dia: int
    preferencias_respetadas: int
    preferencias_totales: int
    porcentaje_match: float


class PlanSemanalResponse(BaseModel):
    men_id: int
    nin_id: int
    men_inicio: date
    men_fin: date
    men_kcal_total: int
    men_estado: str
    dias: List[DiaPlanResponse]
    resumen: ResumenPlan


class GenerarPlanRequest(BaseModel):
    nin_id: int
    fecha_inicio: date
    incluir_refacciones: bool = False
    preferencias_adicionales: Optional[str] = None


class MenuListItem(BaseModel):
    men_id: int
    men_inicio: date
    men_fin: date
    men_kcal_total: Optional[int] = None
    men_estado: str
    men_generado_por: str
    creado_en: datetime


class MenusListResponse(BaseModel):
    nin_id: int
    total: int
    menus: List[MenuListItem]
