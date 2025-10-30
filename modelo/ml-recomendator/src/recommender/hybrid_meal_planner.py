"""
Planificador híbrido de menús que combina el ranker LightGBM con optimización OR-Tools.
Extiende el MealPlanner original con capacidades de machine learning.
Actualizado para usar el esquema real de base de datos.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from database.schema_adapter import SchemaValidator
from optimization.meal_optimizer import (
    MealPlanConstraints,
    MealPlanOptimizer,
    NutritionalConstraints,
)
from pipeline.feature_engineering import FeatureEngineer
from recommender.meal_planner import (
    DailyMealPlan,
    MealPlanItem,
    MealPlanner,
    WeeklyMealPlan,
)

logger = logging.getLogger(__name__)


@dataclass
class ChildProfile:
    """Perfil completo del niño para el sistema híbrido."""

    child_id: int
    age_months: int
    weight_kg: Optional[float]
    height_cm: Optional[float]
    nutritional_status: str
    allergies: List[str]
    preferences: Dict[str, float]
    favorite_foods: List[str]
    daily_calories: float
    daily_protein: float
    daily_carbs: float
    daily_fat: float


class HybridMealPlanner(MealPlanner):
    """
    Planificador híbrido que combina:
    1. Ranker LightGBM para scoring inteligente de menús
    2. Optimización OR-Tools para ensamble óptimo
    3. Lógica original de filtros y restricciones
    """

    def __init__(
        self,
        objetivos_diarios: Optional[Dict[str, float]] = None,
        ranker_model_path: Optional[str] = None,
        db_connection_string: Optional[str] = None,
        use_optimization: bool = True,
    ):
        """
        Inicializar el planificador híbrido.

        Args:
            objetivos_diarios: Objetivos nutricionales por defecto
            ranker_model_path: Ruta al modelo ranker entrenado
            db_connection_string: String de conexión a la base de datos real
            use_optimization: Si usar optimización OR-Tools
        """
        super().__init__(objetivos_diarios)

        self.use_optimization = use_optimization
        self.db_connection_string = db_connection_string

        # Inicializar adaptadores de esquema
        self.schema_validator = SchemaValidator()
        self.data_extractor = None

        # Inicializar feature engineer si hay conexión a BD
        self.feature_engineer = None
        if db_connection_string:
            try:
                self.feature_engineer = FeatureEngineer(db_connection_string)
                logger.info("FeatureEngineer inicializado con esquema real")
            except Exception as e:
                logger.warning(f"No se pudo inicializar FeatureEngineer: {e}")

        # Inicializar ranker si está disponible
        self.ranker = None
        if ranker_model_path:
            try:
                from models.rankers.lgbm_ranker import MenuRanker

                self.ranker = MenuRanker()
                self.ranker.load_model(ranker_model_path)
                logger.info(f"Ranker cargado desde: {ranker_model_path}")
            except Exception as e:
                logger.warning(f"No se pudo cargar el ranker: {e}")
                self.ranker = None

    def _create_child_profile(
        self,
        child_id: int,
        estado_nutricional: str,
        alergias: List[str],
        preferencias: Dict[str, float],
        favoritas: List[str],
        objetivos: Dict[str, float],
    ) -> ChildProfile:
        """Crear perfil completo del niño usando datos reales si están disponibles."""

        # Valores por defecto
        age_months = 120  # 10 años por defecto
        weight_kg = 35.0
        height_cm = 140.0

        # Intentar obtener datos reales de la BD
        if self.feature_engineer:
            try:
                child_features = self.feature_engineer.get_child_features([child_id])
                if not child_features.empty:
                    child_data = child_features.iloc[0]
                    age_months = child_data.get("edad_meses", age_months)
                    weight_kg = child_data.get("ant_peso", weight_kg)
                    height_cm = child_data.get("ant_talla", height_cm)
                    # Actualizar alergias y favoritas desde BD si están disponibles
                    if "alergias_list" in child_data and child_data["alergias_list"]:
                        alergias = child_data["alergias_list"]
                    if (
                        "comidas_favoritas_list" in child_data
                        and child_data["comidas_favoritas_list"]
                    ):
                        favoritas = child_data["comidas_favoritas_list"]
                    logger.info(f"Datos reales cargados para niño {child_id}")
            except Exception as e:
                logger.warning(f"No se pudieron cargar datos reales para niño {child_id}: {e}")

        return ChildProfile(
            child_id=child_id,
            age_months=age_months,
            weight_kg=weight_kg,
            height_cm=height_cm,
            nutritional_status=estado_nutricional,
            allergies=alergias,
            preferences=preferencias,
            favorite_foods=favoritas,
            daily_calories=objetivos["kcal"],
            daily_protein=objetivos["proteina_g"],
            daily_carbs=objetivos.get("carbs", objetivos["kcal"] * 0.55 / 4),  # 55% de calorías
            daily_fat=objetivos.get("fat", objetivos["kcal"] * 0.30 / 9),  # 30% de calorías
        )

    def _get_menu_candidates_from_db(self, slot: str) -> List[Dict]:
        """Obtener candidatos de menús desde la base de datos usando el esquema real."""
        if not self.feature_engineer:
            # Convertir candidatos mock a formato dict
            mock_candidates = self._filtrar_candidatos(slot, [])
            return [
                {
                    "menu_id": c.id,
                    "name": c.nombre,
                    "slot": c.slot,
                    "calories": c.kcal,
                    "protein": c.proteina_g,
                    "carbs": c.kcal * 0.55 / 4,  # Estimación
                    "fat": c.kcal * 0.30 / 9,  # Estimación
                    "categories": c.categorias,
                    "ingredients": c.ingredientes,
                    "allergens": [],  # Por defecto vacío
                    "meal_type": c.slot,
                }
                for c in mock_candidates
            ]

        try:
            # Obtener menús reales usando el feature engineer
            menu_features = self.feature_engineer.get_menu_features()
            if menu_features.empty:
                logger.warning("No se encontraron menús en la BD")
                return []

            # Filtrar por tipo de comida si está disponible
            if "meal_types" in menu_features.columns:
                slot_menus = menu_features[menu_features["meal_types"].str.contains(slot, na=False)]
            else:
                slot_menus = menu_features

            # Convertir a formato dict
            candidates = []
            for _, menu in slot_menus.iterrows():
                candidate = {
                    "menu_id": menu.get("menu_id", menu.name),
                    "name": menu.get("nombre", f"Menu {menu.name}"),
                    "slot": slot,
                    "calories": menu.get("energia_kcal", 400),
                    "protein": menu.get("proteina_g", 15),
                    "carbs": menu.get("carbohidratos_g", 50),
                    "fat": menu.get("grasas_g", 12),
                    "categories": menu.get("meal_types", [slot])
                    if isinstance(menu.get("meal_types"), list)
                    else [slot],
                    "ingredients": menu.get("ingredientes_list", [])
                    if isinstance(menu.get("ingredientes_list"), list)
                    else [],
                    "allergens": [],  # Se puede agregar lógica para alergenos
                    "meal_type": slot,
                    "tiempo_preparacion": menu.get("tiempo_preparacion", 30),
                    "avg_rating": menu.get("avg_rating", 3.0),
                }
                candidates.append(candidate)

            logger.info(f"Obtenidos {len(candidates)} candidatos para {slot} desde BD real")
            return candidates

        except Exception as e:
            logger.error(f"Error obteniendo menús de BD: {e}")
            return []

    def _score_with_ranker(
        self, child_profile: ChildProfile, menu_candidates: List[Dict]
    ) -> List[float]:
        """Usar el ranker para obtener scores de los menús."""
        if not self.ranker or not menu_candidates:
            # Fallback al scoring original
            return [0.5] * len(menu_candidates)

        try:
            # Preparar datos para el ranker
            ranker_data = []
            for menu in menu_candidates:
                # Crear features para el ranker
                features = {
                    "child_id": child_profile.child_id,
                    "menu_id": menu["menu_id"],
                    "child_age_months": child_profile.age_months,
                    "child_weight_kg": child_profile.weight_kg or 35.0,
                    "child_height_cm": child_profile.height_cm or 140.0,
                    "nutritional_status": child_profile.nutritional_status,
                    "menu_calories": menu["calories"],
                    "menu_protein": menu["protein"],
                    "menu_carbs": menu.get("carbs", 0),
                    "menu_fat": menu.get("fat", 0),
                    "calorie_adequacy": menu["calories"] / (child_profile.daily_calories / 3),
                    "protein_adequacy": menu["protein"] / (child_profile.daily_protein / 3),
                    "allergy_compatible": 1.0
                    if not any(
                        allergen in menu.get("allergens", [])
                        for allergen in child_profile.allergies
                    )
                    else 0.0,
                    "nutritional_status_compatible": 1.0
                    if (
                        child_profile.nutritional_status in ["SEVERO", "MODERADO"]
                        and "proteico" in menu.get("categories", [])
                    )
                    else 0.5,
                }
                ranker_data.append(features)

            # Convertir a DataFrame
            df = pd.DataFrame(ranker_data)

            # Obtener predicciones del ranker
            scores = self.ranker.predict(df)
            return scores.tolist()

        except Exception as e:
            logger.error(f"Error en ranker: {e}")
            # Fallback al scoring original
            return [0.5] * len(menu_candidates)

    def _optimize_meal_plan(
        self,
        child_profile: ChildProfile,
        all_candidates: Dict[str, List[Dict]],
        all_scores: Dict[str, List[float]],
        dias: int,
    ) -> Optional[List[Dict]]:
        """Optimizar el plan de comidas usando OR-Tools."""
        if not self.use_optimization:
            return None

        try:
            # Preparar restricciones nutricionales
            nutritional_constraints = NutritionalConstraints(
                min_calories=child_profile.daily_calories * 0.9,
                max_calories=child_profile.daily_calories * 1.1,
                min_protein=child_profile.daily_protein * 0.9,
                max_protein=child_profile.daily_protein * 1.1,
                min_carbs=child_profile.daily_carbs * 0.9,
                max_carbs=child_profile.daily_carbs * 1.1,
                min_fat=child_profile.daily_fat * 0.9,
                max_fat=child_profile.daily_fat * 1.1,
            )

            # Preparar restricciones del plan
            plan_constraints = MealPlanConstraints(
                days=dias,
                meals_per_day=3,  # Solo desayuno, almuerzo, cena (sin snack para optimización)
                max_repetitions=2,
                allergen_restrictions=child_profile.allergies,
            )

            # Crear optimizador
            optimizer = MealPlanOptimizer(
                nutritional_constraints=nutritional_constraints,
                plan_constraints=plan_constraints,
                solver_time_limit=60,  # 1 minuto límite
            )

            # Combinar todos los candidatos
            combined_candidates = []
            combined_scores = []

            for slot in ["desayuno", "almuerzo", "cena"]:
                if slot in all_candidates:
                    combined_candidates.extend(all_candidates[slot])
                    combined_scores.extend(all_scores[slot])

            # Optimizar
            optimized_plan, metrics = optimizer.optimize_meal_plan(
                candidate_menus=combined_candidates,
                ranker_scores=combined_scores,
                child_profile=child_profile.__dict__,
            )

            if metrics["constraints_satisfied"]:
                logger.info(f"Plan optimizado generado: {metrics}")
                return optimized_plan
            else:
                logger.warning("Optimización falló, usando método original")
                return None

        except Exception as e:
            logger.error(f"Error en optimización: {e}")
            return None

    def generar_plan_semanal_hibrido(
        self,
        child_id: int,
        estado_nutricional: str,
        alergias: List[str],
        preferencias: Dict[str, float],
        favoritas: List[str],
        dias: int = 7,
    ) -> WeeklyMealPlan:
        """
        Generar plan semanal usando el enfoque híbrido.

        Args:
            child_id: ID del niño
            estado_nutricional: Estado nutricional del niño
            alergias: Lista de alergias
            preferencias: Diccionario de preferencias
            favoritas: Lista de comidas favoritas
            dias: Número de días del plan

        Returns:
            Plan semanal optimizado
        """
        logger.info(f"Generando plan híbrido para niño {child_id}")

        # Ajustar objetivos por estado
        objetivos = self._ajustar_objetivos_por_estado(self.obj.copy(), estado_nutricional)

        # Crear perfil del niño
        child_profile = self._create_child_profile(
            child_id, estado_nutricional, alergias, preferencias, favoritas, objetivos
        )

        # Obtener candidatos y scores para cada slot
        all_candidates = {}
        all_scores = {}

        for slot in ["desayuno", "almuerzo", "cena", "snack"]:
            # Obtener candidatos (filtrados por alergias)
            candidates = self._get_menu_candidates_from_db(slot)
            filtered_candidates = [
                c
                for c in candidates
                if not any(allergen in c.get("allergens", []) for allergen in alergias)
            ]

            if filtered_candidates:
                # Obtener scores del ranker
                scores = self._score_with_ranker(child_profile, filtered_candidates)
                all_candidates[slot] = filtered_candidates
                all_scores[slot] = scores
            else:
                all_candidates[slot] = []
                all_scores[slot] = []

        # Intentar optimización si está habilitada
        optimized_plan = self._optimize_meal_plan(child_profile, all_candidates, all_scores, dias)

        if optimized_plan:
            # Convertir plan optimizado a formato WeeklyMealPlan
            return self._convert_optimized_plan_to_weekly(
                optimized_plan, dias, all_candidates, all_scores
            )
        else:
            # Fallback al método original con scores del ranker
            return self._generate_plan_with_ranker_scores(
                child_profile, all_candidates, all_scores, dias
            )

    def _convert_optimized_plan_to_weekly(
        self,
        optimized_plan: List[Dict],
        dias: int,
        all_candidates: Dict[str, List[Dict]],
        all_scores: Dict[str, List[float]],
    ) -> WeeklyMealPlan:
        """Convertir plan optimizado a formato WeeklyMealPlan."""
        plan_dias = []

        for day in range(1, dias + 1):
            day_menus = [menu for menu in optimized_plan if menu["day"] == day]
            day_menus.sort(key=lambda x: x["meal"])  # Ordenar por comida

            items = []
            for menu in day_menus:
                item = MealPlanItem(
                    id=menu["menu_id"],
                    nombre=menu["name"],
                    slot=menu["slot"],
                    kcal=int(menu["calories"]),
                    proteina_g=menu["protein"],
                    score=round(menu["ranker_score"], 2),
                    razon=f"Optimizado (score: {menu['ranker_score']:.2f})",
                )
                items.append(item)

            # Agregar snack si falta
            if len(items) == 3:  # Solo desayuno, almuerzo, cena
                # Buscar mejor snack
                if "snack" in all_candidates and all_candidates["snack"]:
                    best_snack_idx = np.argmax(all_scores["snack"])
                    snack_menu = all_candidates["snack"][best_snack_idx]
                    snack_item = MealPlanItem(
                        id=snack_menu["menu_id"],
                        nombre=snack_menu["name"],
                        slot="snack",
                        kcal=int(snack_menu["calories"]),
                        proteina_g=snack_menu["protein"],
                        score=round(all_scores["snack"][best_snack_idx], 2),
                        razon="Mejor snack disponible",
                    )
                    items.append(snack_item)

            plan_dias.append(DailyMealPlan(items=items))

        return WeeklyMealPlan(dias=plan_dias)

    def _generate_plan_with_ranker_scores(
        self,
        child_profile: ChildProfile,
        all_candidates: Dict[str, List[Dict]],
        all_scores: Dict[str, List[float]],
        dias: int,
    ) -> WeeklyMealPlan:
        """Generar plan usando scores del ranker pero sin optimización."""
        plan_dias = []

        for _ in range(dias):
            items = []

            for slot in ["desayuno", "almuerzo", "cena", "snack"]:
                if slot in all_candidates and all_candidates[slot]:
                    # Seleccionar el mejor candidato por score
                    best_idx = np.argmax(all_scores[slot])
                    best_menu = all_candidates[slot][best_idx]
                    best_score = all_scores[slot][best_idx]

                    item = MealPlanItem(
                        id=best_menu["menu_id"],
                        nombre=best_menu["name"],
                        slot=slot,
                        kcal=int(best_menu["calories"]),
                        proteina_g=best_menu["protein"],
                        score=round(best_score, 2),
                        razon=f"Ranker ML (score: {best_score:.2f})",
                    )
                    items.append(item)

                    # Remover el menú seleccionado para evitar repetición inmediata
                    all_candidates[slot].pop(best_idx)
                    all_scores[slot].pop(best_idx)

                    # Si se agotaron los candidatos, recargar
                    if not all_candidates[slot]:
                        candidates = self._get_menu_candidates_from_db(slot)
                        filtered_candidates = [
                            c
                            for c in candidates
                            if not any(
                                allergen in c.get("allergens", [])
                                for allergen in child_profile.allergies
                            )
                        ]
                        if filtered_candidates:
                            all_candidates[slot] = filtered_candidates
                            all_scores[slot] = self._score_with_ranker(
                                child_profile, filtered_candidates
                            )

            plan_dias.append(DailyMealPlan(items=items))

        return WeeklyMealPlan(dias=plan_dias)

    def generar_plan_semanal(
        self,
        estado_nutricional: str,
        alergias: List[str],
        preferencias: Dict[str, float],
        favoritas: List[str],
        dias: int = 7,
    ) -> WeeklyMealPlan:
        """
        Mantener compatibilidad con la API original.
        Usa child_id = 1 por defecto.
        """
        return self.generar_plan_semanal_hibrido(
            child_id=1,
            estado_nutricional=estado_nutricional,
            alergias=alergias,
            preferencias=preferencias,
            favoritas=favoritas,
            dias=dias,
        )


# Función de conveniencia para crear el planificador híbrido
def create_hybrid_planner(
    ranker_model_path: Optional[str] = None,
    db_connection_string: Optional[str] = None,
    use_optimization: bool = True,
) -> HybridMealPlanner:
    """
    Crear un planificador híbrido con configuración por defecto.

    Args:
        ranker_model_path: Ruta al modelo ranker entrenado
        db_connection_string: String de conexión a la base de datos real
        use_optimization: Si usar optimización OR-Tools

    Returns:
        Instancia del planificador híbrido
    """
    return HybridMealPlanner(
        objetivos_diarios={"kcal": 1800, "proteina_g": 50.0},
        ranker_model_path=ranker_model_path,
        db_connection_string=db_connection_string,
        use_optimization=use_optimization,
    )


if __name__ == "__main__":
    # Ejemplo de uso
    planner = create_hybrid_planner(
        ranker_model_path="../../models/ranker/menu_ranker_latest.pkl", use_optimization=True
    )

    plan = planner.generar_plan_semanal_hibrido(
        child_id=1,
        estado_nutricional="MODERADO",
        alergias=["maní"],
        preferencias={"vegetariano": 0.5, "alto_fibra": 0.3},
        favoritas=["fruta", "yogur"],
        dias=3,
    )

    print("Plan híbrido generado:")
    print(plan.resumen())
    for idx, dia in enumerate(plan.dias, 1):
        print(f"\nDía {idx}")
        for item in dia.items:
            print(f"- {item.slot}: {item.nombre} ({item.kcal} kcal) -> {item.score} | {item.razon}")
