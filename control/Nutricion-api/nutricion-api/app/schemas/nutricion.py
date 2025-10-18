"""
Schemas para el módulo de nutrición (alimentos, recetas, nutrientes).
"""

from typing import Any

from pydantic import BaseModel, Field


# ========== NUTRIENTES ==========
class NutrienteBase(BaseModel):
    nutri_codigo: str = Field(..., max_length=10)
    nutri_nombre: str = Field(..., max_length=100)
    nutri_unidad: str = Field(..., max_length=20)


class NutrienteCreate(NutrienteBase):
    pass


class NutrienteUpdate(BaseModel):
    nutri_codigo: str | None = None
    nutri_nombre: str | None = None
    nutri_unidad: str | None = None


class NutrienteResponse(NutrienteBase):
    nutri_id: int

    class Config:
        from_attributes = True


# ========== ALIMENTOS ==========
class AlimentoBase(BaseModel):
    ali_nombre: str = Field(..., max_length=200)
    ali_nombre_cientifico: str | None = Field(None, max_length=200)
    ali_grupo: str | None = Field(None, max_length=100)
    ali_unidad: str = Field(default="g", max_length=20)
    ali_activo: bool = Field(default=True)


class AlimentoCreate(AlimentoBase):
    pass


class AlimentoUpdate(BaseModel):
    ali_nombre: str | None = None
    ali_nombre_cientifico: str | None = None
    ali_grupo: str | None = None
    ali_unidad: str | None = None
    ali_activo: bool | None = None


class AlimentoResponse(AlimentoBase):
    ali_id: int

    class Config:
        from_attributes = True


# ========== ALIMENTOS_NUTRIENTES ==========
class AlimentoNutrienteBase(BaseModel):
    ali_id: int
    nutri_id: int
    an_cantidad_100: float = Field(..., description="Cantidad por 100g o 100ml")
    an_fuente: str | None = Field(None, max_length=100)


class AlimentoNutrienteCreate(AlimentoNutrienteBase):
    pass


class AlimentoNutrienteUpdate(BaseModel):
    an_cantidad_100: float | None = None
    an_fuente: str | None = None


class AlimentoNutrienteResponse(AlimentoNutrienteBase):
    class Config:
        from_attributes = True


# ========== RECETAS ==========
class RecetaBase(BaseModel):
    rec_nombre: str = Field(..., max_length=200)
    rec_instrucciones: str | None = None
    rec_activo: bool = Field(default=True)


class RecetaCreate(RecetaBase):
    pass


class RecetaUpdate(BaseModel):
    rec_nombre: str | None = None
    rec_instrucciones: str | None = None
    rec_activo: bool | None = None


class RecetaResponse(RecetaBase):
    rec_id: int

    class Config:
        from_attributes = True


# ========== RECETAS_INGREDIENTES ==========
class RecetaIngredienteBase(BaseModel):
    rec_id: int
    ali_id: int
    ri_cantidad: float
    ri_unidad: str = Field(default="g", max_length=20)


class RecetaIngredienteCreate(RecetaIngredienteBase):
    pass


class RecetaIngredienteUpdate(BaseModel):
    ri_cantidad: float | None = None
    ri_unidad: str | None = None


class RecetaIngredienteResponse(RecetaIngredienteBase):
    ali_nombre: str | None = None

    class Config:
        from_attributes = True


# ========== RECETAS_COMIDAS ==========
class RecetaComidaBase(BaseModel):
    rec_id: int
    rc_comida: str = Field(..., description="DESAYUNO, ALMUERZO, CENA")


class RecetaComidaCreate(RecetaComidaBase):
    pass


class RecetaComidaResponse(RecetaComidaBase):
    rc_id: int

    class Config:
        from_attributes = True


# ========== DISPONIBILIDAD_ALIMENTOS ==========
class DisponibilidadAlimentoBase(BaseModel):
    ali_id: int
    ent_id: int
    dis_periodo: str = Field(..., max_length=20, description="Ej: Q1, Q2, Q3, Q4")
    dis_disponible: bool = Field(default=True)
    dis_precio_promedio: float | None = None
    dis_region: str | None = Field(None, max_length=100)


class DisponibilidadAlimentoCreate(DisponibilidadAlimentoBase):
    pass


class DisponibilidadAlimentoUpdate(BaseModel):
    dis_disponible: bool | None = None
    dis_precio_promedio: float | None = None
    dis_region: str | None = None


class DisponibilidadAlimentoResponse(DisponibilidadAlimentoBase):
    dis_id: int

    class Config:
        from_attributes = True


# ========== RESPONSES COMPLEJOS ==========
class AlimentoConNutrientesResponse(AlimentoResponse):
    """Alimento con sus nutrientes."""

    nutrientes: list[dict[str, Any]] = []


class RecetaCompletaResponse(RecetaResponse):
    """Receta con ingredientes y tipo de comida."""

    ingredientes: list[RecetaIngredienteResponse] = []
    tipos_comida: list[str] = []
    informacion_nutricional: dict[str, Any] = {}
