"""
Feature Engineering para el modelo de ranking de menús.

Este módulo genera features del niño, del menú y de interacción
para entrenar el modelo Learning-to-Rank usando el esquema real de la base de datos.
"""

import logging
import os
from datetime import date
from typing import List, Optional

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Import schema adapter for validation
from ..database.schema_adapter import MLDataExtractor, SchemaValidator

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)


def create_mysql_connection_string() -> str:
    """
    Crea el string de conexión MySQL usando las credenciales del .env

    Returns:
        String de conexión MySQL
    """
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "root123456")
    db_name = os.getenv("DB_NAME", "nutricion")

    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class FeatureEngineer:
    """
    Generador de features para el modelo de ranking de menús usando esquema real.
    """

    def __init__(self, db_connection_string: str):
        """
        Inicializa el generador de features.

        Args:
            db_connection_string: String de conexión a la base de datos
        """
        self.engine = create_engine(db_connection_string)
        self.validator = SchemaValidator()
        self.extractor = MLDataExtractor(self.engine)

    def get_child_features(self, child_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Extrae features del niño desde la base de datos usando esquema real.

        Args:
            child_ids: Lista de IDs de niños (opcional, si None toma todos)

        Returns:
            DataFrame con features del niño
        """
        # Usar el validador para construir query segura
        base_query = """
        SELECT
            n.nin_id as child_id,
            n.nin_nombres,
            n.nin_fecha_nac,
            n.nin_sexo,
            -- Datos antropométricos más recientes
            a.ant_peso,
            a.ant_talla,
            a.ant_imc,
            a.ant_percentil_peso,
            a.ant_percentil_talla,
            a.ant_percentil_imc,
            -- Perfil nutricional vigente
            pnn.pnn_calorias_diarias,
            pnn.pnn_proteinas_g,
            pnn.pnn_carbohidratos_g,
            pnn.pnn_grasas_g,
            pnn.pnn_clasificacion,
            -- Alergias (conteo y severidad)
            COALESCE(COUNT(DISTINCT na.na_id), 0) as num_alergias,
            COALESCE(AVG(CASE
                WHEN na.na_severidad = 'LEVE' THEN 1
                WHEN na.na_severidad = 'MODERADA' THEN 2
                WHEN na.na_severidad = 'SEVERA' THEN 3
                ELSE 0 END), 0) as severidad_alergias_promedio,
            -- Comidas favoritas
            COALESCE(COUNT(DISTINCT ncf.rec_id), 0) as num_comidas_favoritas,
            -- Restricciones alimentarias
            COALESCE(COUNT(DISTINCT nra.nra_id), 0) as num_restricciones
        FROM ninos n
        LEFT JOIN antropometrias a ON n.nin_id = a.nin_id
            AND a.ant_fecha = (
                SELECT MAX(ant_fecha)
                FROM antropometrias a2
                WHERE a2.nin_id = n.nin_id
            )
        LEFT JOIN perfil_nutricional_nino pnn ON n.nin_id = pnn.nin_id
            AND pnn.pnn_vigente = 1
        LEFT JOIN ninos_alergias na ON n.nin_id = na.nin_id
            AND na.na_activo = 1
        LEFT JOIN ninos_comidas_favoritas ncf ON n.nin_id = ncf.nin_id
        LEFT JOIN ninos_restricciones_alimentos nra ON n.nin_id = nra.nin_id
            AND nra.nra_activo = 1
        WHERE 1=1
        """

        if child_ids:
            placeholders = ",".join(["%s"] * len(child_ids))
            base_query += f" AND n.nin_id IN ({placeholders})"

        base_query += """
        GROUP BY n.nin_id, n.nin_nombres, n.nin_fecha_nac, n.nin_sexo,
                 a.ant_peso, a.ant_talla, a.ant_imc, a.ant_percentil_peso,
                 a.ant_percentil_talla, a.ant_percentil_imc,
                 pnn.pnn_calorias_diarias, pnn.pnn_proteinas_g,
                 pnn.pnn_carbohidratos_g, pnn.pnn_grasas_g, pnn.pnn_clasificacion
        """

        params = child_ids if child_ids else []
        df = pd.read_sql(base_query, self.engine, params=params)

        # Calcular edad en meses desde fecha de nacimiento
        if not df.empty:
            df["edad_meses"] = df["nin_fecha_nac"].apply(
                lambda x: self._calculate_age_months(x) if pd.notna(x) else 0
            )

        # Features derivadas del niño
        df = self._create_child_derived_features(df)

        return df

    def get_menu_features(self, menu_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Extrae features del menú/receta desde la base de datos usando esquema real.

        Args:
            menu_ids: Lista de IDs de recetas (opcional)

        Returns:
            DataFrame con features del menú/receta
        """
        base_query = """
        SELECT
            r.rec_id as menu_id,
            r.rec_nombre as nombre,
            -- Tipos de comida para esta receta
            GROUP_CONCAT(DISTINCT rc.rc_comida) as tipos_comida,
            -- Nutrientes calculados desde ingredientes (usar códigos correctos de la BD)
            -- Códigos correctos: EN=Energía, PRO=Proteína, CHO=Carbohidratos, GRA=Grasa, FIB=Fibra, FE=Hierro, CA=Calcio, VA=Vit A, VC=Vit C, ZN=Zinc
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'EN' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as kcal_total,
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'PRO' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as proteina_g,
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'CHO' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as carbohidratos_g,
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'GRA' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as grasas_g,
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'FIB' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as fibra_g,
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'FE' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as hierro_mg,
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'CA' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as calcio_mg,
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'VA' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as vitamina_a_ug,
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'VC' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as vitamina_c_mg,
            COALESCE(SUM(CASE WHEN n.nutri_codigo = 'ZN' THEN an.an_cantidad_100 * ri.ri_cantidad / 100.0 ELSE 0 END), 0) as zinc_mg,
            -- Diversidad de ingredientes
            COUNT(DISTINCT ri.ali_id) as num_ingredientes,
            -- Popularidad basada en feedback (usando subconsultas para evitar duplicación de filas)
            COALESCE((
                SELECT AVG(mf_inner.mf_rating)
                FROM menus_items mi_inner
                LEFT JOIN menus_feedback mf_inner ON mi_inner.mei_id = mf_inner.mei_id
                WHERE mi_inner.rec_id = r.rec_id
            ), 3.0) as aceptacion_promedio,
            COALESCE((
                SELECT COUNT(DISTINCT mf_inner.mf_id)
                FROM menus_items mi_inner
                LEFT JOIN menus_feedback mf_inner ON mi_inner.mei_id = mf_inner.mei_id
                WHERE mi_inner.rec_id = r.rec_id
            ), 0) as num_evaluaciones,
            -- Porcentaje de completado promedio
            COALESCE((
                SELECT AVG(mf_inner.mf_porcentaje_consumido)
                FROM menus_items mi_inner
                LEFT JOIN menus_feedback mf_inner ON mi_inner.mei_id = mf_inner.mei_id
                WHERE mi_inner.rec_id = r.rec_id
            ), 50) as porcentaje_consumido_promedio,
            -- Número de veces que aparece en favoritas
            COALESCE((
                SELECT COUNT(DISTINCT ncf_inner.ncf_id)
                FROM ninos_comidas_favoritas ncf_inner
                WHERE ncf_inner.rec_id = r.rec_id
            ), 0) as veces_favorita
        FROM recetas r
        LEFT JOIN recetas_comidas rc ON r.rec_id = rc.rec_id
        LEFT JOIN recetas_ingredientes ri ON r.rec_id = ri.rec_id
        LEFT JOIN alimentos a ON ri.ali_id = a.ali_id AND a.ali_activo = 1
        LEFT JOIN alimentos_nutrientes an ON a.ali_id = an.ali_id
        LEFT JOIN nutrientes n ON an.nutri_id = n.nutri_id
        WHERE r.rec_activo = 1
        """

        if menu_ids:
            placeholders = ",".join(["%s"] * len(menu_ids))
            base_query += f" AND r.rec_id IN ({placeholders})"

        base_query += """
        GROUP BY r.rec_id, r.rec_nombre
        """

        params = menu_ids if menu_ids else []
        df = pd.read_sql(base_query, self.engine, params=params)

        # Procesar tipos de comida como lista
        if not df.empty:
            df["tipos_comida_list"] = df["tipos_comida"].apply(
                lambda x: x.split(",") if pd.notna(x) else []
            )

        # Features derivadas del menú
        df = self._create_menu_derived_features(df)

        return df

    def _calculate_age_months(self, birth_date) -> int:
        """Calcula edad en meses desde fecha de nacimiento"""
        if isinstance(birth_date, str):
            birth_date = pd.to_datetime(birth_date).date()
        elif isinstance(birth_date, pd.Timestamp):
            birth_date = birth_date.date()

        today = date.today()
        months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
        return max(0, months)

    def _create_child_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea features derivadas del niño.

        Args:
            df: DataFrame con features base del niño

        Returns:
            DataFrame con features adicionales
        """
        df = df.copy()

        # Calcular BMI usando datos antropométricos reales
        df["bmi"] = df["ant_peso"] / (df["ant_talla"] / 100) ** 2

        # Categorías de edad
        df["edad_categoria"] = pd.cut(
            df["edad_meses"],
            bins=[0, 12, 24, 60, 120, 216],  # 0-1, 1-2, 2-5, 5-10, 10-18 años
            labels=["lactante", "toddler", "preescolar", "escolar", "adolescente"],
        )

        # IMC categorizado
        df["bmi_categoria"] = pd.cut(
            df["bmi"],
            bins=[0, 18.5, 25, 30, float("inf")],
            labels=["bajo_peso", "normal", "sobrepeso", "obesidad"],
        )

        # Riesgo nutricional basado en percentiles IMC
        df["riesgo_nutricional"] = df["ant_percentil_imc"].apply(
            lambda x: "alto" if x < 5 or x > 95 else "medio" if x < 15 or x > 85 else "bajo"
        )

        # Complejidad alimentaria (basada en alergias)
        df["complejidad_alimentaria"] = df.apply(
            lambda row: "alta"
            if row["num_alergias"] > 2 or row["severidad_alergias_promedio"] > 2
            else "media"
            if row["num_alergias"] > 0
            else "baja",
            axis=1,
        )

        # Score de preferencias (normalizado)
        max_favoritas = (
            df["num_comidas_favoritas"].max() if df["num_comidas_favoritas"].max() > 0 else 1
        )
        df["preferencias_score"] = df["num_comidas_favoritas"] / max_favoritas

        return df

    def _create_menu_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea features derivadas del menú usando el esquema real.

        Args:
            df: DataFrame con features base del menú

        Returns:
            DataFrame con features adicionales
        """
        df = df.copy()

        # Usar kcal_total (nombre correcto de la columna SQL)
        # Crear alias para compatibilidad con código legacy
        if "kcal_total" in df.columns and "energia_kcal" not in df.columns:
            df["energia_kcal"] = df["kcal_total"]

        # Densidad nutricional (usando columnas reales)
        df["densidad_proteina"] = df["proteina_g"] / (df["kcal_total"] + 1)
        df["densidad_fibra"] = df["fibra_g"] / (df["kcal_total"] + 1)
        df["densidad_hierro"] = df["hierro_mg"] / (df["kcal_total"] + 1)
        df["densidad_calcio"] = df["calcio_mg"] / (df["kcal_total"] + 1)

        # Balance de macronutrientes
        total_macros = df["proteina_g"] + df["carbohidratos_g"] + df["grasas_g"]
        df["ratio_proteina"] = df["proteina_g"] / (total_macros + 1)
        df["ratio_carbohidratos"] = df["carbohidratos_g"] / (total_macros + 1)
        df["ratio_grasas"] = df["grasas_g"] / (total_macros + 1)

        # Categorías de calorías
        df["categoria_calorias"] = pd.cut(
            df["kcal_total"],
            bins=[0, 100, 200, 400, 600, float("inf")],
            labels=["muy_bajo", "bajo", "medio", "alto", "muy_alto"],
        )

        # Score de popularidad basado en feedback (aceptacion_promedio es el nombre en SQL)
        # Crear alias si no existe
        if "aceptacion_promedio" in df.columns and "avg_rating" not in df.columns:
            df["avg_rating"] = df["aceptacion_promedio"]

        df["popularidad_score"] = df.get("avg_rating", pd.Series([3.0] * len(df))).fillna(2.5) / 5.0

        # Complejidad de preparación (usar valor default si no existe tiempo_preparacion)
        if "tiempo_preparacion" not in df.columns:
            df["tiempo_preparacion"] = 30  # Default 30 minutos

        df["complejidad_preparacion"] = df["tiempo_preparacion"].apply(
            lambda x: "alta" if x > 60 else "media" if x > 30 else "baja"
        )

        # Score de complejidad (basado en ingredientes y tiempo)
        df["complejidad_score"] = (
            df["num_ingredientes"] * 0.3
            + df["tiempo_preparacion"] * 0.01
            + (df["dificultad"] if "dificultad" in df.columns else 2) * 0.2
        )

        # Score de diversidad (ingredientes únicos)
        max_ingredientes = df["num_ingredientes"].max() if df["num_ingredientes"].max() > 0 else 1
        df["diversity_score"] = df["num_ingredientes"] / max_ingredientes

        # Score de popularidad normalizado
        if df["popularidad_score"].max() > 0:
            df["popularidad_norm"] = df["popularidad_score"] / df["popularidad_score"].max()
        else:
            df["popularidad_norm"] = 0.5

        # Categoría de alergenos (si existe la columna)
        if "num_alergenos" in df.columns:
            df["categoria_alergenos"] = pd.cut(
                df["num_alergenos"],
                bins=[-1, 0, 2, 5, float("inf")],
                labels=[
                    "sin_alergenos",
                    "pocos_alergenos",
                    "algunos_alergenos",
                    "muchos_alergenos",
                ],
            )
        else:
            df["categoria_alergenos"] = "sin_alergenos"

        return df

    def create_interaction_features(
        self, child_df: pd.DataFrame, menu_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Crea features de interacción niño-menú.

        Args:
            child_df: DataFrame con features del niño
            menu_df: DataFrame con features del menú

        Returns:
            DataFrame con features de interacción
        """
        # Crear producto cartesiano
        child_df["key"] = 1
        menu_df["key"] = 1
        interaction_df = child_df.merge(menu_df, on="key").drop("key", axis=1)

        # Features de compatibilidad nutricional
        interaction_df["kcal_adecuadas"] = self._check_calorie_adequacy(
            interaction_df["edad_meses"],
            interaction_df["sexo"],
            interaction_df["estado_nutricional"],
            interaction_df["kcal_total"],
        )

        # Compatibilidad con alergias
        interaction_df["compatible_alergias"] = (interaction_df["num_alergenos"] == 0).astype(int)

        # Score de preferencias (si el menú está en favoritas)
        interaction_df["es_favorita"] = self._check_favorite_match(
            interaction_df["child_id"], interaction_df["menu_id"]
        )

        # Distancia nutricional al objetivo
        interaction_df["distancia_proteina"] = abs(
            interaction_df["proteina_g"]
            - self._get_protein_target(interaction_df["edad_meses"], interaction_df["peso_kg"])
        )

        # Compatibilidad con estado nutricional
        interaction_df["compatible_estado"] = self._check_nutritional_state_compatibility(
            interaction_df["estado_nutricional"],
            interaction_df["categoria_calorias"],
            interaction_df["densidad_proteina"],
        )

        # Score de diversidad personalizada
        interaction_df["diversidad_personalizada"] = interaction_df["diversity_score"] * (
            1 + interaction_df["preferencias_score"]
        )

        return interaction_df

    def _check_calorie_adequacy(
        self,
        edad_meses: pd.Series,
        sexo: pd.Series,
        estado_nutricional: pd.Series,
        kcal_total: pd.Series,
    ) -> pd.Series:
        """
        Verifica si las calorías son adecuadas para el niño.
        """
        # Rangos aproximados de calorías por edad y sexo (por comida, ~25% del total diario)
        calorie_ranges = {
            ("M", "lactante"): (80, 150),
            ("F", "lactante"): (75, 140),
            ("M", "toddler"): (100, 200),
            ("F", "toddler"): (95, 190),
            ("M", "preescolar"): (150, 300),
            ("F", "preescolar"): (140, 280),
            ("M", "escolar"): (200, 400),
            ("F", "escolar"): (180, 350),
            ("M", "adolescente"): (300, 600),
            ("F", "adolescente"): (250, 500),
        }

        # Categorizar edad
        edad_cat = pd.cut(
            edad_meses,
            bins=[0, 12, 24, 60, 120, 216],
            labels=["lactante", "toddler", "preescolar", "escolar", "adolescente"],
        )

        adequacy = []
        for i, (sexo_val, edad_val, estado_val, kcal_val) in enumerate(
            zip(sexo, edad_cat, estado_nutricional, kcal_total)
        ):
            if pd.isna(edad_val):
                adequacy.append(0.5)
                continue

            range_key = (sexo_val, edad_val)
            if range_key in calorie_ranges:
                min_kcal, max_kcal = calorie_ranges[range_key]

                # Ajustar por estado nutricional
                if estado_val == "desnutricion":
                    max_kcal *= 1.2  # Más calorías para recuperación
                elif estado_val == "sobrepeso":
                    max_kcal *= 0.8  # Menos calorías para control

                if min_kcal <= kcal_val <= max_kcal:
                    adequacy.append(1.0)
                else:
                    # Score gradual basado en distancia
                    distance = min(abs(kcal_val - min_kcal), abs(kcal_val - max_kcal))
                    score = max(0, 1 - distance / max_kcal)
                    adequacy.append(score)
            else:
                adequacy.append(0.5)

        return pd.Series(adequacy)

    def _check_favorite_match(self, child_ids: pd.Series, menu_ids: pd.Series) -> pd.Series:
        """
        Verifica si el menú está en las favoritas del niño.
        """
        # Consultar favoritas desde la base de datos
        query = """
        SELECT nino_id, comida_id
        FROM preferencias_favoritas
        WHERE nino_id IN %s AND comida_id IN %s
        """

        unique_child_ids = child_ids.unique().tolist()
        unique_menu_ids = menu_ids.unique().tolist()

        try:
            favorites_df = pd.read_sql(
                query, self.engine, params=[unique_child_ids, unique_menu_ids]
            )

            # Crear set de pares favoritos
            favorite_pairs = set(zip(favorites_df["nino_id"], favorites_df["comida_id"]))

            # Verificar cada par
            is_favorite = [
                1 if (child_id, menu_id) in favorite_pairs else 0
                for child_id, menu_id in zip(child_ids, menu_ids)
            ]

        except Exception as e:
            logger.warning(f"Error consultando favoritas: {e}")
            is_favorite = [0] * len(child_ids)

        return pd.Series(is_favorite)

    def _get_protein_target(self, edad_meses: pd.Series, peso_kg: pd.Series) -> pd.Series:
        """
        Calcula el objetivo de proteína por comida (g).
        """
        # Aproximadamente 1.2-2.0 g/kg/día según edad, dividido por 4 comidas
        protein_per_kg_day = edad_meses.apply(lambda x: 2.0 if x < 12 else 1.5 if x < 60 else 1.2)

        return (protein_per_kg_day * peso_kg) / 4  # Por comida

    def _check_nutritional_state_compatibility(
        self,
        estado_nutricional: pd.Series,
        categoria_calorias: pd.Series,
        densidad_proteina: pd.Series,
    ) -> pd.Series:
        """
        Verifica compatibilidad entre estado nutricional y características del menú.
        """
        compatibility = []

        for estado, cal_cat, dens_prot in zip(
            estado_nutricional, categoria_calorias, densidad_proteina
        ):
            score = 0.5  # Base

            if estado == "desnutricion":
                # Necesita más calorías y proteína
                if cal_cat in ["alto", "muy_alto"]:
                    score += 0.3
                if dens_prot > 0.15:  # Alta densidad proteica
                    score += 0.2

            elif estado == "sobrepeso":
                # Necesita menos calorías, más fibra
                if cal_cat in ["bajo", "muy_bajo"]:
                    score += 0.3
                if dens_prot > 0.12:  # Proteína para saciedad
                    score += 0.2

            elif estado == "normal":
                # Flexible, pero balanceado
                if cal_cat == "medio":
                    score += 0.2
                if 0.10 <= dens_prot <= 0.20:
                    score += 0.3

            compatibility.append(min(1.0, score))

        return pd.Series(compatibility)

    def generate_training_dataset(
        self,
        child_ids: Optional[List[int]] = None,
        menu_ids: Optional[List[int]] = None,
        slots: List[str] = ["desayuno", "almuerzo", "merienda", "cena"],
        days: int = 7,
    ) -> pd.DataFrame:
        """
        Genera dataset completo de entrenamiento.

        Args:
            child_ids: IDs de niños a incluir
            menu_ids: IDs de menús a incluir
            slots: Slots de comida
            days: Número de días a simular

        Returns:
            DataFrame con dataset de entrenamiento
        """
        logger.info("Generando dataset de entrenamiento...")

        # Obtener features base
        child_df = self.get_child_features(child_ids)
        menu_df = self.get_menu_features(menu_ids)

        logger.info(f"Niños: {len(child_df)}, Menús: {len(menu_df)}")

        # Crear combinaciones por slot y día
        datasets = []

        for day in range(1, days + 1):
            for slot in slots:
                # Crear features de interacción
                interaction_df = self.create_interaction_features(child_df, menu_df)

                # Agregar contexto temporal
                interaction_df["dia"] = day
                interaction_df["slot"] = slot
                interaction_df["query_id"] = (
                    interaction_df["child_id"].astype(str) + "_" + str(day) + "_" + slot
                )

                # Filtrar menús apropiados por slot
                slot_appropriate = self._filter_by_slot(interaction_df, slot)
                interaction_df = interaction_df[slot_appropriate]

                datasets.append(interaction_df)

        # Combinar todos los datasets
        final_dataset = pd.concat(datasets, ignore_index=True)

        logger.info(f"Dataset generado: {len(final_dataset)} registros")

        return final_dataset

    def _filter_by_slot(self, df: pd.DataFrame, slot: str) -> pd.Series:
        """
        Filtra menús apropiados por slot de comida.
        """
        slot_mapping = {
            "desayuno": ["desayuno", "bebida", "cereal"],
            "almuerzo": ["almuerzo", "plato_principal", "sopa", "ensalada"],
            "merienda": ["merienda", "snack", "fruta", "bebida"],
            "cena": ["cena", "plato_principal", "sopa", "ensalada"],
        }

        appropriate_categories = slot_mapping.get(slot, [])

        if not appropriate_categories:
            return pd.Series([True] * len(df))

        return df["categoria"].isin(appropriate_categories)


def create_bootstrap_labels(
    df: pd.DataFrame, rule_based_planner_scores: Optional[pd.Series] = None
) -> pd.Series:
    """
    Crea labels de bootstrapping usando el planificador por reglas.

    Args:
        df: DataFrame con features
        rule_based_planner_scores: Scores del planificador por reglas (opcional)

    Returns:
        Series con labels de relevancia (0, 1, 2)
    """
    if rule_based_planner_scores is not None:
        # Usar scores del planificador existente
        # Convertir a labels categóricas
        labels = pd.cut(
            rule_based_planner_scores,
            bins=[-float("inf"), 0.3, 0.7, float("inf")],
            labels=[0, 1, 2],
        ).astype(int)
    else:
        # Crear labels basadas en features de compatibilidad
        compatibility_score = (
            df["kcal_adecuadas"] * 0.3
            + df["compatible_alergias"] * 0.3
            + df["es_favorita"] * 0.2
            + df["compatible_estado"] * 0.2
        )

        labels = pd.cut(
            compatibility_score, bins=[0, 0.4, 0.7, 1.0], labels=[0, 1, 2], include_lowest=True
        ).astype(int)

    return labels
