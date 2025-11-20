"""
Planificador híbrido de menús que combina el ranker LightGBM con optimización OR-Tools.
Extiende el MealPlanner original con capacidades de machine learning.
Actualizado para usar el esquema real de base de datos.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from src.database.schema_adapter import SchemaValidator
from src.models.rankers.feature_pipeline import RankerFeatureBuilder
from src.optimization.meal_optimizer import (
    MealPlanConstraints,
    MealPlanOptimizer,
    NutritionalConstraints,
)
from src.pipeline.feature_engineering import FeatureEngineer
from src.recommender.meal_planner import (
    DailyMealPlan,
    MealPlanItem,
    MealPlanner,
    WeeklyMealPlan,
)

logger = logging.getLogger(__name__)


def get_latest_model_path(models_dir: str = "models") -> Optional[str]:
    """
    Busca el modelo más reciente en el directorio especificado.

    Args:
        models_dir: Directorio donde buscar modelos

    Returns:
        Ruta al modelo más reciente o None si no hay modelos
    """
    try:
        # Si es una ruta relativa, hacerla absoluta desde la raíz del proyecto
        if not Path(models_dir).is_absolute():
            # En producción (Cloud Run): /app/models
            # En local: relativo al directorio actual del proyecto
            project_root = Path(__file__).parent.parent.parent
            models_path = project_root / models_dir
        else:
            models_path = Path(models_dir)

        if not models_path.exists():
            logger.warning(f"Directorio de modelos no existe: {models_path}")
            logger.info(f"Ruta absoluta intentada: {models_path.absolute()}")
            return None

        # Buscar archivos .pkl (excluyendo _meta.json)
        model_files = list(models_path.glob("production_menu_recommender_*.pkl"))

        logger.info(f"🔍 Buscando en: {models_path.absolute()}")
        logger.info(f"📂 Archivos encontrados: {len(model_files)}")

        if not model_files:
            logger.warning(f"No se encontraron modelos en {models_path}")
            # Listar qué archivos hay en el directorio para debug
            all_files = list(models_path.glob("*"))
            logger.info(f"Archivos en el directorio: {[f.name for f in all_files]}")
            return None

        # Ordenar por fecha de modificación (más reciente primero)
        latest_model = max(model_files, key=lambda p: p.stat().st_mtime)

        logger.info(f"✅ Modelo más reciente encontrado: {latest_model.name}")
        return str(latest_model)

    except Exception as e:
        logger.error(f"Error buscando modelo más reciente: {e}")
        return None


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

        # ⚠️ Deshabilitando optimización OR-Tools temporalmente (tiene problemas de compatibilidad)
        self.use_optimization = False  # use_optimization
        self.db_connection_string = db_connection_string
        logger.info("⚠️ Optimización OR-Tools deshabilitada - usando ranker ML directo")

        # Inicializar adaptadores de esquema
        self.schema_validator = SchemaValidator()
        self.data_extractor = None

        # Inicializar feature engineer si hay conexión a BD
        self.feature_engineer = None

        # Si no se proporciona db_connection_string, intentar leerlo de .env
        if db_connection_string is None:
            import os

            db_connection_string = os.getenv("DATABASE_URL")
            if db_connection_string:
                logger.info("📊 Usando DATABASE_URL desde .env")
            else:
                logger.warning("⚠️ No se encontró DATABASE_URL en .env ni como parámetro")

        if db_connection_string:
            try:
                self.feature_engineer = FeatureEngineer(db_connection_string)
                logger.info("✅ FeatureEngineer inicializado con esquema real")
            except Exception as e:
                logger.warning(f"❌ No se pudo inicializar FeatureEngineer: {e}")

        # Inicializar ranker con modelo más reciente si está disponible
        self.ranker = None
        self.feature_builder: Optional[RankerFeatureBuilder] = None

        # Si no se especifica modelo, buscar el más reciente automáticamente
        if ranker_model_path is None:
            logger.info("🔍 Buscando modelo más reciente...")
            ranker_model_path = get_latest_model_path()

        if ranker_model_path:
            try:
                # Cargar el modelo LightGBM junto con metadata
                import pickle

                with open(ranker_model_path, "rb") as f:
                    payload = pickle.load(f)

                if isinstance(payload, dict) and "model" in payload:
                    self.ranker = payload.get("model")
                    self.feature_builder = payload.get("feature_builder")
                    logger.info(
                        f"✅ Ranker LightGBM (con metadata) cargado desde: {ranker_model_path}"
                    )
                else:
                    self.ranker = payload
                    self.feature_builder = None
                    logger.info(
                        f"✅ Ranker LightGBM cargado sin metadata desde: {ranker_model_path}"
                    )
            except Exception as e:
                logger.warning(f"⚠️ No se pudo cargar el ranker: {e}")
                self.ranker = None
        else:
            logger.warning("⚠️ No se encontró ningún modelo disponible")

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

    def _create_child_profile_with_custom_data(
        self,
        child_id: int,
        estado_nutricional: str,
        alergias: List[str],
        preferencias: Dict[str, float],
        favoritas: List[str],
        objetivos_nutricionales: Dict[str, float],
        perfil_completo: Optional[Dict[str, float]] = None,
    ) -> ChildProfile:
        """
        Crear perfil del niño usando datos personalizados del perfil nutricional si están disponibles.

        Args:
            perfil_completo: Dict que puede contener edad_meses, peso_kg, talla_cm, calorias_dia, etc.
        """

        # Valores por defecto
        age_months = 120  # 10 años por defecto
        weight_kg = 35.0
        height_cm = 140.0

        # Si se proporcionó perfil completo, usar esos datos (PRIORIDAD MÁS ALTA)
        if perfil_completo:
            age_months = perfil_completo.get("edad_meses", age_months)
            weight_kg = perfil_completo.get("peso_kg", weight_kg)
            height_cm = perfil_completo.get("talla_cm", height_cm)
            logger.info(
                f"✅ Usando perfil personalizado: edad={age_months}m, peso={weight_kg}kg, talla={height_cm}cm"
            )

        # Si no, intentar obtener datos reales de la BD
        elif self.feature_engineer:
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
                    logger.info(f"Datos reales cargados de BD para niño {child_id}")
            except Exception as e:
                logger.warning(f"No se pudieron cargar datos reales para niño {child_id}: {e}")

        return ChildProfile(
            child_id=child_id,
            age_months=int(age_months),
            weight_kg=float(weight_kg) if weight_kg else None,
            height_cm=float(height_cm) if height_cm else None,
            nutritional_status=estado_nutricional,
            allergies=alergias,
            preferences=preferencias,
            favorite_foods=favoritas,
            daily_calories=objetivos_nutricionales.get(
                "calorias_dia", objetivos_nutricionales.get("kcal", 1800)
            ),
            daily_protein=objetivos_nutricionales.get(
                "proteinas_dia", objetivos_nutricionales.get("proteina_g", 50)
            ),
            daily_carbs=objetivos_nutricionales.get(
                "carbs", objetivos_nutricionales.get("kcal", 1800) * 0.55 / 4
            ),
            daily_fat=objetivos_nutricionales.get(
                "fat", objetivos_nutricionales.get("kcal", 1800) * 0.30 / 9
            ),
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
            # Mapear slot a tipo de comida en mayúsculas como está en la BD
            slot_map = {
                "desayuno": "DESAYUNO",
                "almuerzo": "ALMUERZO",
                "cena": "CENA",
                "snack": "SNACK",
            }
            meal_type_filter = slot_map.get(slot, slot.upper())

            if "tipos_comida" in menu_features.columns:
                slot_menus = menu_features[
                    menu_features["tipos_comida"].str.contains(
                        meal_type_filter, case=False, na=False
                    )
                ]
                logger.info(
                    f"🔍 Filtrando {len(menu_features)} recetas por tipo '{meal_type_filter}' → {len(slot_menus)} encontradas"
                )
            elif "meal_types" in menu_features.columns:
                slot_menus = menu_features[menu_features["meal_types"].str.contains(slot, na=False)]
            else:
                slot_menus = menu_features
                logger.warning(
                    f"⚠️ No se encontró columna 'tipos_comida' o 'meal_types', usando todas las {len(slot_menus)} recetas"
                )

            # Convertir a formato dict
            candidates = []
            for _, menu in slot_menus.iterrows():
                # Mapear nombres de columnas del SQL a formato esperado
                candidate = {
                    "menu_id": menu.get("menu_id", menu.name),
                    "name": menu.get("nombre", f"Menu {menu.name}"),
                    "slot": slot,
                    # Usar nombres de columnas correctos del SQL: kcal_total, no energia_kcal
                    "calories": menu.get("kcal_total", menu.get("energia_kcal", 400)),
                    "protein": menu.get("proteina_g", 15),
                    "carbs": menu.get("carbohidratos_g", 50),
                    "fat": menu.get("grasas_g", 12),
                    # Usar tipos_comida_list si existe, sino meal_types
                    "categories": menu.get("tipos_comida_list", menu.get("meal_types", [slot]))
                    if isinstance(menu.get("tipos_comida_list", menu.get("meal_types")), list)
                    else [slot],
                    "ingredients": menu.get("ingredientes_list", [])
                    if isinstance(menu.get("ingredientes_list"), list)
                    else [],
                    "allergens": [],  # Se puede agregar lógica para alergenos
                    "meal_type": slot,
                    "tiempo_preparacion": menu.get("tiempo_preparacion", 30),
                    "avg_rating": menu.get("aceptacion_promedio", menu.get("avg_rating", 3.0)),
                }
                candidates.append(candidate)

            logger.info(f"Obtenidos {len(candidates)} candidatos para {slot} desde BD real")
            return candidates

        except Exception as e:
            import traceback

            logger.error(f"❌ Error obteniendo menús de BD: {e}")
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return []

    def _score_with_ranker(
        self, child_profile: ChildProfile, menu_candidates: List[Dict]
    ) -> List[float]:
        """Usar el ranker para obtener scores de los menús usando el perfil nutricional completo."""
        if not self.ranker or not menu_candidates:
            # Fallback al scoring original
            return [0.5] * len(menu_candidates)

        try:
            if self.feature_builder:
                ranker_df = self._build_ranker_dataframe(child_profile, menu_candidates)
                X = self.feature_builder.transform(ranker_df)
                logger.info(
                    f"📊 Ranker input shape: {X.shape} "
                    f"(features: {len(self.feature_builder.feature_names)})"
                )
            else:
                # Fallback legacy
                X = self._build_legacy_ranker_features(child_profile, menu_candidates)
                logger.info(f"📊 Ranker input shape (legacy): {X.shape}")
            scores = self.ranker.predict(X)

            # Normalizar scores entre 0 y 1 (con manejo de casos edge)
            if len(scores) > 0:
                scores_min = scores.min()
                scores_max = scores.max()
                if scores_max > scores_min:
                    # Normalización estándar
                    scores = (scores - scores_min) / (scores_max - scores_min)
                else:
                    # Si todos los scores son iguales, asignar 0.5 a todos
                    logger.warning(
                        f"⚠️ Todos los scores son iguales ({scores_min:.3f}), asignando 0.5"
                    )
                    scores = np.full_like(scores, 0.5)

            logger.info(
                f"✅ Scores del ranker ML: min={scores.min():.3f}, max={scores.max():.3f}, mean={scores.mean():.3f}"
            )
            return scores.tolist()

        except Exception as e:
            logger.error(f"❌ Error en ranker: {e}", exc_info=True)
            # Fallback al scoring original
            return [0.5] * len(menu_candidates)

    def _build_ranker_dataframe(
        self, child_profile: ChildProfile, menu_candidates: List[Dict]
    ) -> pd.DataFrame:
        """Construye el DataFrame crudo esperado por RankerFeatureBuilder."""
        rows = []
        preferences = child_profile.preferences or {}

        for menu in menu_candidates:
            calories = menu.get("calories", 400)
            meal_type = menu.get("meal_type", menu.get("slot", "ALMUERZO"))
            peso = child_profile.weight_kg or 35.0
            talla = child_profile.height_cm or 140.0
            talla_m = talla / 100.0 if talla else 1.4
            bmi = peso / (talla_m**2) if talla_m else 18.5
            zscore = (bmi - 18.5) / 3.0

            row = {
                "edad_meses": child_profile.age_months,
                "pnn_edad_meses": child_profile.age_months,
                "ant_peso_kg": peso,
                "ant_talla_cm": talla,
                "en_zscore_imc": zscore,
                "pnn_calorias_diarias": child_profile.daily_calories,
                "pnn_proteinas_g": child_profile.daily_protein,
                "mei_kcal": calories,
                "men_kcal_total": calories,
                "mei_comida": meal_type,
                "pnn_clasificacion": child_profile.nutritional_status,
                "nin_sexo": preferences.get("sexo", "M") if isinstance(preferences, dict) else "M",
                "men_generado_por": "IA",
                "num_alergias": len(child_profile.allergies),
                "mf_porcentaje_consumido": 75,
            }
            rows.append(row)

        return pd.DataFrame(rows)

    def _build_legacy_ranker_features(
        self, child_profile: ChildProfile, menu_candidates: List[Dict]
    ):
        """Compatibilidad con modelos antiguos sin metadata."""
        import numpy as np

        ranker_data = []
        for menu in menu_candidates:
            # Reutilizamos la lógica previa de 14 columnas para evitar ruptura.
            calories = menu.get("calories", 400)
            protein = menu.get("protein", 15)
            weight = child_profile.weight_kg or 35.0
            height = child_profile.height_cm or 140.0
            height_m = height / 100.0
            bmi = weight / (height_m**2) if height_m else 18.5
            zscore = (bmi - 18.5) / 3.0
            caloric_score = calories / (child_profile.daily_calories / 3)
            target_protein = child_profile.daily_calories * 0.15 / 4
            protein_balance = max(
                0,
                min(
                    1,
                    1 - abs(protein - target_protein / 3) / (target_protein / 3 + 1e-6),
                ),
            )
            nutritional_balance = (caloric_score + protein_balance) / 2
            meal_type = menu.get("meal_type", menu.get("slot", "ALMUERZO"))
            meal_type_map = {"DESAYUNO": 0, "ALMUERZO": 1, "CENA": 2}
            age_group = (
                0
                if child_profile.age_months < 24
                else 1
                if child_profile.age_months < 60
                else 2
                if child_profile.age_months < 120
                else 3
                if child_profile.age_months < 180
                else 4
            )
            status_map = {
                "DESNUTRICION_SEVERA": 0,
                "DESNUTRICION": 1,
                "RIESGO": 2,
                "NORMAL": 3,
                "SOBREPESO": 4,
                "OBESIDAD": 5,
            }

            ranker_data.append(
                [
                    child_profile.age_months,
                    weight,
                    height,
                    bmi,
                    zscore,
                    child_profile.daily_calories,
                    calories,
                    caloric_score,
                    0.8,
                    nutritional_balance,
                    age_group,
                    1,
                    status_map.get(child_profile.nutritional_status, 3),
                    meal_type_map.get(meal_type, 1),
                ]
            )

        return np.array(ranker_data, dtype=np.float32)

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
            # Preparar restricciones nutricionales - Convertir a enteros para OR-Tools
            nutritional_constraints = NutritionalConstraints(
                min_calories=int(child_profile.daily_calories * 0.9),
                max_calories=int(child_profile.daily_calories * 1.1),
                min_protein=int(child_profile.daily_protein * 0.9),
                max_protein=int(child_profile.daily_protein * 1.1),
                min_carbs=int(child_profile.daily_carbs * 0.9),
                max_carbs=int(child_profile.daily_carbs * 1.1),
                min_fat=int(child_profile.daily_fat * 0.9),
                max_fat=int(child_profile.daily_fat * 1.1),
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
        objetivos: Optional[Dict[str, float]] = None,
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
            objetivos: Objetivos nutricionales personalizados (calorías, proteínas, etc.)

        Returns:
            Plan semanal optimizado
        """
        logger.info(f"Generando plan híbrido para niño {child_id}")

        # Ajustar objetivos por estado o usar los proporcionados
        if objetivos is None:
            objetivos_nutricionales = self._ajustar_objetivos_por_estado(
                self.obj.copy(), estado_nutricional
            )
        else:
            # Combinar objetivos proporcionados con los ajustados por estado
            objetivos_base = self._ajustar_objetivos_por_estado(self.obj.copy(), estado_nutricional)
            objetivos_nutricionales = {
                **objetivos_base,
                **objetivos,
            }  # Los proporcionados tienen prioridad
            logger.info(f"📊 Usando objetivos personalizados: {objetivos_nutricionales}")

        # Crear perfil del niño - Si objetivos incluye datos del perfil (edad, peso, talla), usarlos
        child_profile = self._create_child_profile_with_custom_data(
            child_id,
            estado_nutricional,
            alergias,
            preferencias,
            favoritas,
            objetivos_nutricionales,
            objetivos,
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

            # FILTRO ADICIONAL POR ESTADO NUTRICIONAL (más agresivo)
            # Esto asegura que niños con diferentes estados reciban recetas diferentes
            estado = child_profile.nutritional_status

            if estado in ["SOBREPESO", "OBESIDAD"]:
                # Excluir recetas muy calóricas (> 450 kcal)
                filtered_candidates = [
                    c for c in filtered_candidates if c.get("calories", 400) <= 450
                ]
                logger.info(f"🔽 SOBREPESO/OBESIDAD: Excluidas recetas > 450 kcal para {slot}")

            elif estado in ["DESNUTRICION", "BAJO_PESO", "DESNUTRICIÓN"]:
                # Excluir recetas muy bajas en calorías (< 350 kcal)
                filtered_candidates = [
                    c for c in filtered_candidates if c.get("calories", 400) >= 350
                ]
                logger.info(f"🔼 DESNUTRICIÓN: Excluidas recetas < 350 kcal para {slot}")

            # Para NORMAL no hay exclusiones adicionales

            if filtered_candidates:
                # Obtener scores del ranker
                scores = self._score_with_ranker(child_profile, filtered_candidates)
                all_candidates[slot] = filtered_candidates
                all_scores[slot] = scores
                logger.info(
                    f"✅ {len(filtered_candidates)} candidatos para {slot} después de filtros"
                )
            else:
                all_candidates[slot] = []
                all_scores[slot] = []
                logger.warning(f"⚠️ No hay candidatos para {slot} después de filtros")

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
        """Generar plan usando scores del ranker con temperature sampling para variedad."""
        plan_dias = []
        used_recipes = set()  # Track recipes used across all days
        temperature = 1.5  # Higher = more exploration, lower = more exploitation

        # Seed diferente por niño para asegurar variedad entre diferentes perfiles
        np.random.seed(child_profile.child_id % 10000)
        logger.info(f"🎲 Usando seed {child_profile.child_id % 10000} para variedad personalizada")

        for dia_num in range(dias):
            items = []

            for slot in ["desayuno", "almuerzo", "cena", "snack"]:
                if slot in all_candidates and all_candidates[slot]:
                    # ESTRATEGIA TOP-K + SORTING por calorías según estado nutricional
                    estado = child_profile.nutritional_status
                    candidates_with_scores = list(zip(all_candidates[slot], all_scores[slot]))

                    # Filtrar recetas ya usadas primero
                    available_candidates = [
                        (c, s)
                        for c, s in candidates_with_scores
                        if c["menu_id"] not in used_recipes
                    ]

                    # Si todas están usadas, permitir repetir con penalización
                    if not available_candidates:
                        available_candidates = candidates_with_scores
                        logger.warning(
                            f"⚠️ Todas las recetas de {slot} ya usadas, permitiendo repetición"
                        )

                    # ORDENAR por calorías según estado nutricional
                    if estado in ["SOBREPESO", "OBESIDAD"]:
                        # Filtrar recetas en rango MODERADO-BAJO (250-400 kcal)
                        # Evitar recetas muy bajas (<200) y muy altas (>400)
                        moderate_candidates = [
                            (c, s)
                            for c, s in available_candidates
                            if 200 <= c.get("calories", 400) <= 400
                        ]
                        # Si no hay suficientes moderadas, usar todas las disponibles
                        if len(moderate_candidates) < 3:
                            moderate_candidates = available_candidates

                        # Ordenar por calorías de MENOR a MAYOR dentro del rango moderado
                        moderate_candidates.sort(key=lambda x: x[0].get("calories", 400))
                        top_k = max(4, len(moderate_candidates) // 2)  # Top 50% del rango moderado
                        available_candidates = moderate_candidates
                        logger.info(
                            f"🔽 SOBREPESO: Eligiendo entre top {top_k} recetas MODERADAS (200-400 kcal)"
                        )

                    elif estado in ["DESNUTRICION", "BAJO_PESO", "DESNUTRICIÓN"]:
                        # Ordenar de MAYOR a MENOR calorías (preferir altas)
                        available_candidates.sort(
                            key=lambda x: x[0].get("calories", 400), reverse=True
                        )
                        top_k = max(3, len(available_candidates) // 3)  # Top 33% más altas
                        logger.info(
                            f"🔼 DESNUTRICIÓN: Eligiendo entre top {top_k} recetas MÁS ALTAS en calorías"
                        )

                    else:  # NORMAL
                        # Usar scores ML directamente (ya ordenados por idoneidad)
                        available_candidates.sort(key=lambda x: x[1], reverse=True)
                        top_k = max(5, len(available_candidates) // 2)  # Top 50% por ML score
                        logger.info(
                            f"⚖️ NORMAL: Eligiendo entre top {top_k} recetas mejor rankeadas por ML"
                        )

                    # Limitar a top-k candidatos
                    top_candidates = available_candidates[:top_k]

                    # Extraer candidatos y scores del top-k
                    filtered_candidates = [c for c, s in top_candidates]
                    filtered_scores = np.array([s for c, s in top_candidates])

                    # Temperature sampling solo entre el top-k
                    if filtered_scores.sum() > 0:
                        normalized_scores = filtered_scores / filtered_scores.max()
                        temp_scores = np.exp(normalized_scores / temperature)
                        probabilities = temp_scores / temp_scores.sum()
                    else:
                        probabilities = np.ones(len(filtered_candidates)) / len(filtered_candidates)

                    # Sample del top-k con probabilidad ajustada
                    best_idx = np.random.choice(len(filtered_candidates), p=probabilities)
                    best_menu = filtered_candidates[best_idx]
                    best_score = filtered_scores[best_idx]

                    logger.info(
                        f"  ✅ Seleccionado: {best_menu['name']} ({best_menu.get('calories', 0)} kcal)"
                    )

                    # Registrar receta usada
                    used_recipes.add(best_menu["menu_id"])

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
