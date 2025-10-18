"""
Schemas para preferencias alimentarias
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TipoComida(str, Enum):
    DESAYUNO = "DESAYUNO"
    ALMUERZO = "ALMUERZO"
    CENA = "CENA"
    SNACKS = "SNACKS"


class PreferenciaItem(BaseModel):
    npc_id: int
    npc_preferencia: str
    creado_en: datetime


class PreferenciasRequest(BaseModel):
    desayuno: List[str] = Field(default_factory=list, description="Preferencias de desayuno")
    almuerzo: List[str] = Field(default_factory=list, description="Preferencias de almuerzo")
    cena: List[str] = Field(default_factory=list, description="Preferencias de cena")
    snacks: List[str] = Field(default_factory=list, description="Preferencias de snacks")


class PreferenciasResponse(BaseModel):
    nin_id: int
    nin_nombres: str
    preferencias: dict
    actualizado_en: Optional[datetime] = None


class PreferenciasPorTipoResponse(BaseModel):
    nin_id: int
    tipo_comida: TipoComida
    preferencias: List[PreferenciaItem]
