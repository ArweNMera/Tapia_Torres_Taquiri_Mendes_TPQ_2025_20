"""
Sistema de recomendación de menús basado en reglas.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class MenuRecommendation:
    """Recomendación de menú."""
    menu_id: int
    nombre: str
    kcal_total: int
    proteina_g: float
    score: float
    razon: str


class MenuRecommender:
    """
    Recomendador de menús basado en clasificación nutricional.
    
    Usa reglas de negocio para filtrar y rankear menús según:
    - Clasificación nutricional (NORMAL, RIESGO, MODERADO, SEVERO)
    - Alergias del niño
    - Edad
    - Requerimientos nutricionales
    """
    
    # Requerimientos nutricionales por clasificación
    REQUIREMENTS = {
        "SEVERO": {
            "kcal_min": 2000,
            "kcal_max": 2500,
            "proteina_min": 60,
            "proteina_max": 80,
            "descripcion": "Alto en calorías y proteínas para recuperación"
        },
        "MODERADO": {
            "kcal_min": 1800,
            "kcal_max": 2200,
            "proteina_min": 50,
            "proteina_max": 70,
            "descripcion": "Balanceado con énfasis nutricional"
        },
        "RIESGO": {
            "kcal_min": 1600,
            "kcal_max": 2000,
            "proteina_min": 45,
            "proteina_max": 60,
            "descripcion": "Preventivo y balanceado"
        },
        "NORMAL": {
            "kcal_min": 1500,
            "kcal_max": 1900,
            "kcal_max": 1900,
            "proteina_min": 40,
            "proteina_max": 55,
            "descripcion": "Mantenimiento saludable"
        }
    }
    
    def __init__(self, db_connector=None):
        """
        Inicializa el recomendador.
        
        Args:
            db_connector: Conector a base de datos (opcional)
        """
        self.db = db_connector
    
    def recomendar(
        self,
        clasificacion: str,
        alergias: List[str],
        edad_meses: int,
        top_n: int = 5
    ) -> List[MenuRecommendation]:
        """
        Recomienda menús para un niño.
        
        Args:
            clasificacion: NORMAL, RIESGO, MODERADO, SEVERO
            alergias: Lista de alergias alimentarias
            edad_meses: Edad del niño en meses
            top_n: Número de recomendaciones
            
        Returns:
            Lista de recomendaciones ordenadas por score
        """
        # Obtener requerimientos
        req = self.REQUIREMENTS.get(clasificacion, self.REQUIREMENTS["NORMAL"])
        
        # Obtener menús de BD (o usar mock si no hay BD)
        if self.db:
            menus = self._obtener_menus_db(req, alergias)
        else:
            menus = self._obtener_menus_mock(req, alergias)
        
        # Calcular score para cada menú
        recomendaciones = []
        for menu in menus:
            score = self._calcular_score(menu, req, clasificacion)
            
            recomendaciones.append(MenuRecommendation(
                menu_id=menu["id"],
                nombre=menu["nombre"],
                kcal_total=menu["kcal"],
                proteina_g=menu["proteina"],
                score=score,
                razon=self._generar_razon(menu, req, clasificacion)
            ))
        
        # Ordenar por score y retornar top N
        recomendaciones.sort(key=lambda x: x.score, reverse=True)
        return recomendaciones[:top_n]
    
    def _calcular_score(
        self,
        menu: Dict,
        req: Dict,
        clasificacion: str
    ) -> float:
        """
        Calcula score de un menú (0-100).
        
        Criterios:
        - Calorías en rango óptimo: +40 puntos
        - Proteínas en rango óptimo: +30 puntos
        - Diversidad de alimentos: +20 puntos
        - Sin alergias: +10 puntos
        """
        score = 0.0
        
        # Score por calorías (40 puntos)
        kcal = menu["kcal"]
        kcal_min = req["kcal_min"]
        kcal_max = req["kcal_max"]
        
        if kcal_min <= kcal <= kcal_max:
            score += 40
        elif kcal < kcal_min:
            # Penalizar por estar bajo
            diff = (kcal_min - kcal) / kcal_min
            score += max(0, 40 - diff * 40)
        else:
            # Penalizar menos por estar alto
            diff = (kcal - kcal_max) / kcal_max
            score += max(0, 40 - diff * 20)
        
        # Score por proteínas (30 puntos)
        prot = menu["proteina"]
        prot_min = req["proteina_min"]
        prot_max = req["proteina_max"]
        
        if prot_min <= prot <= prot_max:
            score += 30
        elif prot < prot_min:
            diff = (prot_min - prot) / prot_min
            score += max(0, 30 - diff * 30)
        else:
            diff = (prot - prot_max) / prot_max
            score += max(0, 30 - diff * 15)
        
        # Score por diversidad (20 puntos)
        diversidad = menu.get("diversidad", 0.5)
        score += diversidad * 20
        
        # Score por sin alergias (10 puntos)
        if not menu.get("tiene_alergias", False):
            score += 10
        
        return round(score, 2)
    
    def _generar_razon(
        self,
        menu: Dict,
        req: Dict,
        clasificacion: str
    ) -> str:
        """Genera explicación de por qué se recomienda este menú."""
        razones = []
        
        # Calorías
        kcal = menu["kcal"]
        if req["kcal_min"] <= kcal <= req["kcal_max"]:
            razones.append(f"Calorías óptimas ({kcal} kcal)")
        
        # Proteínas
        prot = menu["proteina"]
        if req["proteina_min"] <= prot <= req["proteina_max"]:
            razones.append(f"Proteínas adecuadas ({prot}g)")
        
        # Clasificación
        razones.append(req["descripcion"])
        
        return " | ".join(razones)
    
    def _obtener_menus_db(
        self,
        req: Dict,
        alergias: List[str]
    ) -> List[Dict]:
        """Obtiene menús de la base de datos."""
        # TODO: Implementar query a BD
        # Por ahora usar mock
        return self._obtener_menus_mock(req, alergias)
    
    def _obtener_menus_mock(
        self,
        req: Dict,
        alergias: List[str]
    ) -> List[Dict]:
        """Menús de ejemplo para testing."""
        menus = [
            {
                "id": 1,
                "nombre": "Menú Alto en Proteínas",
                "kcal": 2100,
                "proteina": 65,
                "diversidad": 0.8,
                "tiene_alergias": False
            },
            {
                "id": 2,
                "nombre": "Menú Balanceado Estándar",
                "kcal": 1700,
                "proteina": 50,
                "diversidad": 0.7,
                "tiene_alergias": False
            },
            {
                "id": 3,
                "nombre": "Menú Vegetariano",
                "kcal": 1600,
                "proteina": 45,
                "diversidad": 0.9,
                "tiene_alergias": False
            },
            {
                "id": 4,
                "nombre": "Menú Recuperación Nutricional",
                "kcal": 2300,
                "proteina": 70,
                "diversidad": 0.75,
                "tiene_alergias": False
            },
            {
                "id": 5,
                "nombre": "Menú Mantenimiento",
                "kcal": 1500,
                "proteina": 42,
                "diversidad": 0.65,
                "tiene_alergias": False
            }
        ]
        
        # Filtrar por alergias (simplificado)
        # En producción, verificar ingredientes contra alergias
        return menus


# Ejemplo de uso
if __name__ == "__main__":
    recommender = MenuRecommender()
    
    # Caso 1: Niño con desnutrición severa
    print("=" * 60)
    print("CASO 1: Desnutrición SEVERA")
    print("=" * 60)
    recomendaciones = recommender.recomendar(
        clasificacion="SEVERO",
        alergias=[],
        edad_meses=60
    )
    
    for i, rec in enumerate(recomendaciones, 1):
        print(f"\n{i}. {rec.nombre}")
        print(f"   Score: {rec.score}/100")
        print(f"   Calorías: {rec.kcal_total} kcal")
        print(f"   Proteínas: {rec.proteina_g}g")
        print(f"   Razón: {rec.razon}")
    
    # Caso 2: Niño normal
    print("\n" + "=" * 60)
    print("CASO 2: Estado NORMAL")
    print("=" * 60)
    recomendaciones = recommender.recomendar(
        clasificacion="NORMAL",
        alergias=[],
        edad_meses=84
    )
    
    for i, rec in enumerate(recomendaciones, 1):
        print(f"\n{i}. {rec.nombre}")
        print(f"   Score: {rec.score}/100")
        print(f"   Calorías: {rec.kcal_total} kcal")
        print(f"   Proteínas: {rec.proteina_g}g")
        print(f"   Razón: {rec.razon}")
