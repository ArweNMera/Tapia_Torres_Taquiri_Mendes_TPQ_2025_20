"""
📊 Extractor de Datos Reales con Feedback Sintético Mejorado
===========================================================

Este script extrae datos reales de tu base de datos y genera feedback sintético
REALISTA para entrenar el modelo ML de recomendación de menús.

MEJORAS EN ESTA VERSIÓN:
- Patrones de comportamiento infantil por edad
- Preferencias alimentarias realistas
- Variabilidad temporal en el consumo
- Factores psicológicos y sociales
- Patrones de rechazo y aceptación más auténticos
"""

import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict

import mysql.connector
import numpy as np
import pandas as pd

# Importar configuraciones
from config_database import (
    ML_TABLES_CONFIG,
    SYNTHETIC_DATA_CONFIG,
    get_database_config,
)

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RealDataExtractor:
    """Extractor de datos reales de la base de datos"""

    def __init__(self, config_type: str = "default"):
        """
        Inicializa el extractor con la configuración de BD especificada

        Args:
            config_type: Tipo de configuración ('default', 'production', 'development')
        """
        self.config = get_database_config(config_type)
        self.connection = None
        self.config_type = config_type

        # Crear directorios necesarios
        os.makedirs("data/processed", exist_ok=True)
        os.makedirs("data/raw", exist_ok=True)

    def connect_database(self) -> bool:
        """Establece conexión con la base de datos"""
        try:
            logger.info(f"🔌 Conectando a la base de datos ({self.config_type})...")
            self.connection = mysql.connector.connect(**self.config)

            if self.connection.is_connected():
                logger.info("✅ Conexión exitosa!")
                return True
            else:
                logger.error("❌ No se pudo establecer la conexión")
                return False

        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            return False

    def disconnect_database(self):
        """Cierra la conexión con la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("🔌 Conexión cerrada")

    def validate_required_tables(self) -> bool:
        """Valida que existan todas las tablas requeridas"""
        try:
            cursor = self.connection.cursor()

            # Obtener lista de tablas en la BD
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]

            # Verificar tablas requeridas
            required_tables = list(ML_TABLES_CONFIG["real_tables"].keys())
            required_tables.extend(ML_TABLES_CONFIG["synthetic_tables"].keys())

            missing_tables = [table for table in required_tables if table not in existing_tables]

            if missing_tables:
                logger.error(f"❌ Faltan las siguientes tablas: {missing_tables}")
                return False

            logger.info("✅ Todas las tablas requeridas están presentes")
            return True

        except Exception as e:
            logger.error(f"❌ Error validando tablas: {e}")
            return False
        finally:
            cursor.close()

    def extract_children_data(self) -> pd.DataFrame:
        """Extrae datos completos de los niños"""
        logger.info("👶 Extrayendo datos de niños...")

        query = """
        SELECT
            n.nin_id,
            n.nin_nombres,
            n.nin_fecha_nac,
            n.nin_sexo,
            TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE()) as edad_meses,

            -- Datos antropométricos más recientes
            a.ant_peso_kg,
            a.ant_talla_cm,
            a.ant_z_imc,
            a.ant_z_peso_edad,
            a.ant_z_talla_edad,
            a.ant_fecha as ultima_antropometria,

            -- Evaluación nutricional más reciente
            en.en_imc,
            en.en_z_score_imc,
            en.en_clasificacion,
            en.en_nivel_riesgo,

            -- Perfil nutricional
            pnn.pnn_calorias_diarias,
            pnn.pnn_proteinas_g,
            pnn.pnn_carbohidratos_g,
            pnn.pnn_grasas_g,

            -- Contar alergias/restricciones
            COALESCE(alergias.num_alergias, 0) as num_alergias,
            COALESCE(restricciones.num_restricciones, 0) as num_restricciones

        FROM ninos n

        -- Antropometría más reciente
        LEFT JOIN (
            SELECT nin_id, ant_peso_kg, ant_talla_cm, ant_z_imc, ant_z_peso_edad, ant_z_talla_edad, ant_fecha,
                   ROW_NUMBER() OVER (PARTITION BY nin_id ORDER BY ant_fecha DESC) as rn
            FROM antropometrias
        ) a ON n.nin_id = a.nin_id AND a.rn = 1

        -- Evaluación nutricional más reciente
        LEFT JOIN (
            SELECT nin_id, en_imc, en_z_score_imc, en_clasificacion, en_nivel_riesgo, creado_en,
                   ROW_NUMBER() OVER (PARTITION BY nin_id ORDER BY creado_en DESC) as rn
            FROM evaluaciones_nutricionales
        ) en ON n.nin_id = en.nin_id AND en.rn = 1

        -- Perfil nutricional más reciente
        LEFT JOIN (
            SELECT nin_id, pnn_calorias_diarias, pnn_proteinas_g, pnn_carbohidratos_g, pnn_grasas_g,
                   pnn_clasificacion, pnn_edad_meses, pnn_peso_kg, pnn_talla_cm,
                   ROW_NUMBER() OVER (PARTITION BY nin_id ORDER BY pnn_fecha_calculo DESC) as rn
            FROM perfil_nutricional_nino
            WHERE pnn_vigente = 1
        ) pnn ON n.nin_id = pnn.nin_id AND pnn.rn = 1

        -- Contar alergias
        LEFT JOIN (
            SELECT nin_id, COUNT(*) as num_alergias
            FROM ninos_alergias
            GROUP BY nin_id
        ) alergias ON n.nin_id = alergias.nin_id

        -- Contar restricciones
        LEFT JOIN (
            SELECT nin_id, COUNT(*) as num_restricciones
            FROM ninos_restricciones_alimentos
            WHERE nra_activo = 1
            GROUP BY nin_id
        ) restricciones ON n.nin_id = restricciones.nin_id

        WHERE n.nin_id IS NOT NULL
        ORDER BY n.nin_id
        """

        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"✅ Extraídos {len(df)} registros de niños")

            # Guardar datos crudos
            df.to_csv("data/raw/children_raw.csv", index=False)

            return df

        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de niños: {e}")
            return pd.DataFrame()

    def extract_menus_data(self) -> pd.DataFrame:
        """Extrae datos completos de menús"""
        logger.info("🍽️ Extrayendo datos de menús...")

        query = """
        SELECT
            m.men_id,
            m.nin_id,
            m.men_generado_por,
            m.men_inicio,
            m.men_fin,
            m.men_kcal_total,
            m.men_estado,
            m.creado_en as fecha_creacion,

            -- Datos del item del menú
            mi.mei_id,
            mi.mei_dia_idx,
            mi.mei_comida,
            mi.mei_kcal,

            -- Datos de la receta
            r.rec_id,
            r.rec_nombre,
            r.rec_instrucciones,
            r.rec_activo

        FROM menus m
        INNER JOIN menus_items mi ON m.men_id = mi.men_id
        INNER JOIN recetas r ON mi.rec_id = r.rec_id

        WHERE m.men_id IS NOT NULL
        ORDER BY m.men_id, mi.mei_id
        """

        try:
            df = pd.read_sql(query, self.connection)
            logger.info(f"✅ Extraídos {len(df)} registros de menús-items")

            # Guardar datos crudos
            df.to_csv("data/raw/menus_raw.csv", index=False)

            return df

        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de menús: {e}")
            return pd.DataFrame()

    def calculate_compatibility_scores(
        self, children_df: pd.DataFrame, menus_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Calcula scores de compatibilidad entre niños y menús"""
        logger.info("🎯 Calculando scores de compatibilidad...")

        compatibility_data = []

        for _, child in children_df.iterrows():
            for _, menu_item in menus_df.iterrows():
                # Score de compatibilidad calórica
                if pd.notna(child["pnn_calorias_diarias"]) and pd.notna(menu_item["mei_kcal"]):
                    daily_calories = child["pnn_calorias_diarias"]
                    item_calories = menu_item["mei_kcal"]

                    # Asumiendo 3 comidas principales + 2 snacks
                    if menu_item["mei_comida"] in ["DESAYUNO", "ALMUERZO", "CENA"]:
                        expected_calories = daily_calories * 0.25  # 25% por comida principal
                    else:
                        expected_calories = daily_calories * 0.125  # 12.5% por snack

                    caloric_diff = abs(item_calories - expected_calories) / expected_calories
                    caloric_compatibility = max(0, 1 - caloric_diff)
                else:
                    caloric_compatibility = 0.5  # Valor neutro si faltan datos

                # Score de compatibilidad por edad
                age_months = child["edad_meses"] if pd.notna(child["edad_meses"]) else 36

                if age_months < 12:  # Bebés
                    age_compatibility = 0.3
                elif age_months < 24:  # Niños pequeños
                    age_compatibility = 0.6
                elif age_months < 60:  # Preescolares
                    age_compatibility = 0.9
                else:  # Escolares
                    age_compatibility = 1.0

                # Score nutricional basado en clasificación
                classification = child.get("en_clasificacion", "NORMAL")
                if classification == "DESNUTRICION":
                    nutritional_score = 0.8 if menu_item["mei_kcal"] > 200 else 0.4
                elif classification == "SOBREPESO":
                    nutritional_score = 0.8 if menu_item["mei_kcal"] < 300 else 0.4
                else:  # NORMAL
                    nutritional_score = 0.7

                # Score combinado
                weights = SYNTHETIC_DATA_CONFIG["compatibility_factors"]
                combined_score = (
                    caloric_compatibility * weights["caloric_weight"]
                    + age_compatibility * weights["age_weight"]
                    + nutritional_score * weights["nutritional_weight"]
                    + 0.6 * weights["preference_weight"]  # Preferencia base
                )

                compatibility_data.append(
                    {
                        "nin_id": child["nin_id"],
                        "mei_id": menu_item["mei_id"],
                        "men_id": menu_item["men_id"],
                        "caloric_compatibility_score": caloric_compatibility,
                        "age_compatibility_score": age_compatibility,
                        "nutritional_balance_score": nutritional_score,
                        "combined_compatibility_score": combined_score,
                    }
                )

        compatibility_df = pd.DataFrame(compatibility_data)
        logger.info(f"✅ Calculados {len(compatibility_df)} scores de compatibilidad")

        return compatibility_df


class RealisticFeedbackGenerator:
    """Generador de feedback sintético REALISTA basado en comportamiento infantil"""

    def __init__(self):
        self.config = SYNTHETIC_DATA_CONFIG
        random.seed(42)  # Para reproducibilidad
        np.random.seed(42)

        # Patrones de comportamiento por edad (en meses)
        self.age_behavior_patterns = {
            "baby": {  # 6-12 meses
                "range": (6, 12),
                "pickiness_factor": 0.8,  # Muy selectivos
                "completion_rate": 0.4,  # Baja tasa de completado
                "texture_sensitivity": 0.9,
                "flavor_acceptance": 0.3,
                "mood_variability": 0.9,  # Muy variable según humor
            },
            "toddler": {  # 12-36 meses
                "range": (12, 36),
                "pickiness_factor": 0.9,  # Extremadamente selectivos
                "completion_rate": 0.3,  # Muy baja tasa de completado
                "texture_sensitivity": 0.8,
                "flavor_acceptance": 0.2,
                "mood_variability": 0.95,  # Máxima variabilidad
            },
            "preschooler": {  # 36-60 meses
                "range": (36, 60),
                "pickiness_factor": 0.6,  # Moderadamente selectivos
                "completion_rate": 0.6,  # Moderada tasa de completado
                "texture_sensitivity": 0.5,
                "flavor_acceptance": 0.5,
                "mood_variability": 0.7,
            },
            "school_age": {  # 60+ meses
                "range": (60, 120),
                "pickiness_factor": 0.4,  # Menos selectivos
                "completion_rate": 0.7,  # Buena tasa de completado
                "texture_sensitivity": 0.3,
                "flavor_acceptance": 0.7,
                "mood_variability": 0.5,
            },
        }

        # Patrones de preferencias por tipo de comida
        self.food_preferences = {
            "DESAYUNO": {
                "sweet_preference": 0.8,  # Les gustan cosas dulces
                "texture_smooth": 0.7,  # Prefieren texturas suaves
                "familiar_foods": 0.9,  # Prefieren comidas familiares
                "colorful_appeal": 0.6,
            },
            "ALMUERZO": {
                "sweet_preference": 0.3,
                "texture_smooth": 0.5,
                "familiar_foods": 0.7,
                "colorful_appeal": 0.8,  # Importante presentación visual
            },
            "CENA": {
                "sweet_preference": 0.2,
                "texture_smooth": 0.6,
                "familiar_foods": 0.8,  # Más conservadores en la cena
                "colorful_appeal": 0.5,
            },
            "SNACK": {
                "sweet_preference": 0.9,  # Máxima preferencia por dulce
                "texture_smooth": 0.4,
                "familiar_foods": 0.6,
                "colorful_appeal": 0.9,  # Muy importante la apariencia
            },
        }

        # Factores temporales que afectan el consumo
        self.temporal_factors = {
            "morning_energy": 0.8,  # Más energía en la mañana
            "afternoon_fatigue": 0.6,  # Cansancio en la tarde
            "evening_resistance": 0.4,  # Resistencia en la noche
            "weekend_relaxed": 0.7,  # Más relajados los fines de semana
            "school_stress": 0.5,  # Estrés escolar afecta apetito
        }

    def get_age_category(self, age_months: int) -> str:
        """Determina la categoría de edad del niño"""
        for category, pattern in self.age_behavior_patterns.items():
            if pattern["range"][0] <= age_months < pattern["range"][1]:
                return category
        return "school_age"  # Por defecto para niños mayores

    def generate_realistic_feedback(
        self, compatibility_df: pd.DataFrame, children_df: pd.DataFrame, menus_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Genera feedback sintético REALISTA"""
        logger.info("🎭 Generando feedback sintético REALISTA...")

        # Seleccionar muestra aleatoria para feedback
        n_records = min(self.config["n_feedback_records"], len(compatibility_df))
        sample_df = compatibility_df.sample(n=n_records, random_state=42)

        feedback_data = []

        for _, row in sample_df.iterrows():
            # Obtener datos del niño y menú
            child_data = children_df[children_df["nin_id"] == row["nin_id"]].iloc[0]
            menu_data = menus_df[menus_df["mei_id"] == row["mei_id"]].iloc[0]

            # Generar feedback realista
            feedback = self._generate_realistic_interaction(row, child_data, menu_data)

            feedback_data.append(feedback)

        feedback_df = pd.DataFrame(feedback_data)
        logger.info(f"✅ Generados {len(feedback_df)} registros de feedback REALISTA")

        return feedback_df

    def _generate_realistic_interaction(
        self, compatibility_row: pd.Series, child_data: pd.Series, menu_data: pd.Series
    ) -> Dict:
        """Genera una interacción realista basada en múltiples factores"""

        # Obtener edad y categoría del niño
        age_months = child_data.get("edad_meses", 36)
        age_category = self.get_age_category(age_months)
        age_pattern = self.age_behavior_patterns[age_category]

        # Obtener tipo de comida
        meal_type = menu_data.get("mei_comida", "ALMUERZO")
        food_prefs = self.food_preferences.get(meal_type, self.food_preferences["ALMUERZO"])

        # Score base de compatibilidad
        base_compatibility = compatibility_row["combined_compatibility_score"]

        # Aplicar factores de comportamiento infantil

        # 1. Factor de selectividad por edad
        pickiness_impact = age_pattern["pickiness_factor"] * random.uniform(0.5, 1.5)
        adjusted_compatibility = base_compatibility * (2 - pickiness_impact)

        # 2. Factor de variabilidad del humor
        mood_factor = random.uniform(
            1 - age_pattern["mood_variability"], 1 + age_pattern["mood_variability"]
        )
        adjusted_compatibility *= mood_factor

        # 3. Factor temporal (hora del día, día de la semana)
        temporal_factor = self._get_temporal_factor(meal_type)
        adjusted_compatibility *= temporal_factor

        # 4. Factor nutricional (niños con desnutrición pueden ser más selectivos)
        nutritional_factor = self._get_nutritional_behavior_factor(child_data)
        adjusted_compatibility *= nutritional_factor

        # 5. Factor de familiaridad (simulamos si es una comida "conocida")
        familiarity_factor = random.uniform(0.3, 1.0)  # Algunas comidas son más familiares
        if familiarity_factor < food_prefs["familiar_foods"]:
            adjusted_compatibility *= 1.2  # Boost para comidas familiares
        else:
            adjusted_compatibility *= 0.7  # Penalización para comidas nuevas

        # Normalizar el score ajustado
        adjusted_compatibility = max(0, min(1, adjusted_compatibility))

        # Generar rating basado en compatibilidad ajustada
        rating = self._generate_realistic_rating(adjusted_compatibility, age_pattern)

        # Generar porcentaje de consumo realista
        consumption_pct = self._generate_realistic_consumption(
            rating, age_pattern, meal_type, child_data
        )

        # Determinar si completó la comida
        completed = 1 if consumption_pct >= 70 else random.choice([0, 1])

        # Generar fecha de consumo con patrones realistas
        consumption_date = self._generate_realistic_date(meal_type)

        # Generar notas realistas
        notes = self._generate_realistic_notes(rating, consumption_pct, age_category, meal_type)

        return {
            "mei_id": int(compatibility_row["mei_id"]),
            "nin_id": int(compatibility_row["nin_id"]),
            "mf_completado": completed,
            "mf_porcentaje_consumido": consumption_pct,
            "mf_rating": rating,
            "mf_notas": notes,
            "mf_fecha_consumo": consumption_date,
            "mf_registrado_por": "SISTEMA_ML_REALISTA",
        }

    def _get_temporal_factor(self, meal_type: str) -> float:
        """Calcula factor temporal basado en el tipo de comida"""
        hour = random.randint(6, 22)  # Horas de comida típicas
        day_of_week = random.randint(0, 6)  # 0=Lunes, 6=Domingo

        # Factor base por hora del día
        if meal_type == "DESAYUNO":
            if 6 <= hour <= 9:
                time_factor = self.temporal_factors["morning_energy"]
            else:
                time_factor = 0.5  # Desayuno fuera de hora
        elif meal_type == "ALMUERZO":
            if 11 <= hour <= 14:
                time_factor = self.temporal_factors["afternoon_fatigue"]
            else:
                time_factor = 0.6
        elif meal_type == "CENA":
            if 17 <= hour <= 20:
                time_factor = self.temporal_factors["evening_resistance"]
            else:
                time_factor = 0.4
        else:  # SNACK
            time_factor = 0.7

        # Ajuste por día de la semana
        if day_of_week >= 5:  # Fin de semana
            time_factor *= self.temporal_factors["weekend_relaxed"]
        else:  # Día escolar
            time_factor *= self.temporal_factors["school_stress"]

        return time_factor

    def _get_nutritional_behavior_factor(self, child_data: pd.Series) -> float:
        """Factor de comportamiento basado en estado nutricional"""
        classification = child_data.get("en_clasificacion", "NORMAL")

        if classification == "DESNUTRICION":
            # Niños desnutridos pueden ser más selectivos o tener menos apetito
            return random.uniform(0.6, 0.9)
        elif classification == "SOBREPESO":
            # Niños con sobrepeso pueden tener más apetito pero ser selectivos
            return random.uniform(0.8, 1.2)
        else:  # NORMAL
            return random.uniform(0.9, 1.1)

    def _generate_realistic_rating(self, compatibility_score: float, age_pattern: Dict) -> int:
        """Genera rating realista considerando comportamiento infantil"""

        # Los niños pequeños son más extremos en sus ratings
        if age_pattern["pickiness_factor"] > 0.7:  # Niños muy selectivos
            if compatibility_score > 0.7:
                weights = [0.05, 0.05, 0.15, 0.25, 0.50]  # Favorece 4-5
            elif compatibility_score > 0.4:
                weights = [0.15, 0.20, 0.30, 0.25, 0.10]  # Distribución media
            else:
                weights = [0.60, 0.25, 0.10, 0.03, 0.02]  # Favorece 1-2
        else:  # Niños menos selectivos
            if compatibility_score > 0.6:
                weights = [0.02, 0.08, 0.20, 0.40, 0.30]  # Más moderado
            elif compatibility_score > 0.3:
                weights = [0.10, 0.20, 0.40, 0.20, 0.10]  # Distribución normal
            else:
                weights = [0.40, 0.30, 0.20, 0.08, 0.02]  # Favorece ratings bajos

        return np.random.choice([1, 2, 3, 4, 5], p=weights)

    def _generate_realistic_consumption(
        self, rating: int, age_pattern: Dict, meal_type: str, child_data: pd.Series
    ) -> int:
        """Genera porcentaje de consumo realista"""

        # Base de consumo por rating
        base_consumption = {
            1: (5, 25),  # Muy poco
            2: (15, 45),  # Poco
            3: (35, 70),  # Moderado
            4: (60, 90),  # Bastante
            5: (80, 100),  # Mucho
        }

        min_pct, max_pct = base_consumption[rating]

        # Ajustar por edad - niños pequeños comen menos consistentemente
        age_factor = age_pattern["completion_rate"]
        min_pct = int(min_pct * age_factor)
        max_pct = int(max_pct * age_factor)

        # Ajustar por tipo de comida
        if meal_type == "SNACK":
            min_pct = int(min_pct * 1.2)  # Snacks se consumen más
            max_pct = int(max_pct * 1.1)
        elif meal_type == "CENA":
            min_pct = int(min_pct * 0.8)  # Cenas se consumen menos
            max_pct = int(max_pct * 0.9)

        # Asegurar rangos válidos
        min_pct = max(0, min(min_pct, 95))
        max_pct = max(min_pct + 5, min(max_pct, 100))

        return random.randint(min_pct, max_pct)

    def _generate_realistic_date(self, meal_type: str) -> str:
        """Genera fecha realista con patrones de comida"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=180)

        # Generar fecha aleatoria
        random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

        # Ajustar hora según tipo de comida
        if meal_type == "DESAYUNO":
            hour = random.randint(6, 9)
        elif meal_type == "ALMUERZO":
            hour = random.randint(11, 14)
        elif meal_type == "CENA":
            hour = random.randint(17, 20)
        else:  # SNACK
            hour = random.choice([10, 15, 16])  # Media mañana o tarde

        minute = random.randint(0, 59)

        final_date = random_date.replace(hour=hour, minute=minute, second=0)
        return final_date.strftime("%Y-%m-%d %H:%M:%S")

    def _generate_realistic_notes(
        self, rating: int, consumption_pct: int, age_category: str, meal_type: str
    ) -> str:
        """Genera notas realistas basadas en comportamiento infantil"""

        # Solo generar notas en ~40% de los casos (más realista)
        if random.random() > 0.4:
            return None

        notes_by_context = {
            "baby": {
                1: [
                    "Escupió la comida",
                    "No quiso abrir la boca",
                    "Lloró mucho",
                    "Rechazó completamente",
                ],
                2: [
                    "Comió muy poco",
                    "Se distrajo fácilmente",
                    "No le gustó la textura",
                    "Jugó con la comida",
                ],
                3: [
                    "Comió algo",
                    "Estuvo tranquilo",
                    "Aceptó algunos bocados",
                    "Normal para su edad",
                ],
                4: ["Comió bien", "Le gustó", "Sonrió mientras comía", "Abrió la boca"],
                5: ["Le encantó", "Pidió más", "Comió todo rápido", "Muy contento"],
            },
            "toddler": {
                1: [
                    "Rabieta durante la comida",
                    "Tiró la comida",
                    "No quiso ni probar",
                    "Dijo 'no me gusta'",
                ],
                2: [
                    "Muy selectivo",
                    "Solo comió un poquito",
                    "Se levantó de la mesa",
                    "Prefirió jugar",
                ],
                3: ["Comió despacio", "Necesitó ayuda", "Estuvo bien", "Sin problemas"],
                4: ["Le gustó bastante", "Comió solo", "Pidió repetir", "Muy cooperativo"],
                5: ["Su comida favorita", "Comió todo feliz", "Aplaudió", "Quiere más"],
            },
            "preschooler": {
                1: ["No le gustó nada", "Dijo que sabía feo", "Se negó a comer", "Hizo caras"],
                2: [
                    "Comió poco",
                    "No era su favorito",
                    "Prefiere otras comidas",
                    "Le costó terminar",
                ],
                3: ["Comida normal", "Estuvo bien", "Sin quejas", "Comió tranquilo"],
                4: ["Le gustó mucho", "Comió bien", "Dijo que estaba rico", "Buena aceptación"],
                5: [
                    "Le encantó",
                    "Su nueva comida favorita",
                    "Pidió la receta",
                    "Comió todo feliz",
                ],
            },
            "school_age": {
                1: [
                    "No le gustó",
                    "Dijo que no tenía hambre",
                    "Prefiere otra comida",
                    "No terminó",
                ],
                2: ["Comió poco", "No estaba muy rico", "Le faltaba sabor", "Comió por obligación"],
                3: ["Estuvo bien", "Comida normal", "Sin comentarios", "Aceptable"],
                4: ["Le gustó", "Comió bien", "Dijo que estaba bueno", "Buena comida"],
                5: ["Excelente", "Le encantó", "Pidió repetir", "Su comida favorita"],
            },
        }

        # Ajustar notas por consumo bajo
        if consumption_pct < 30 and rating >= 3:
            # Si consumió poco pero rating alto, explicar por qué
            low_consumption_notes = [
                "Le gustó pero no tenía mucha hambre",
                "Estaba cansado pero le gustó",
                "Comió poco porque ya había comido antes",
                "Le gustó pero se llenó rápido",
            ]
            return random.choice(low_consumption_notes)

        # Notas específicas por tipo de comida
        if meal_type == "SNACK" and rating >= 4:
            snack_notes = ["Le encantó el snack", "Perfecto para la merienda", "Snack favorito"]
            return random.choice(snack_notes)

        # Seleccionar nota apropiada
        category_notes = notes_by_context.get(age_category, notes_by_context["preschooler"])
        rating_notes = category_notes.get(rating, ["Sin comentarios"])

        return random.choice(rating_notes)


def main(config_type: str = "default"):
    """Función principal para extraer datos y generar feedback sintético REALISTA"""

    logger.info("🚀 INICIANDO EXTRACCIÓN DE DATOS REALES CON FEEDBACK SINTÉTICO REALISTA")
    logger.info("=" * 80)

    # Inicializar extractor
    extractor = RealDataExtractor(config_type)

    try:
        # Conectar a la base de datos
        if not extractor.connect_database():
            logger.error("❌ No se pudo conectar a la base de datos")
            return False

        # Validar tablas requeridas
        if not extractor.validate_required_tables():
            logger.error("❌ Faltan tablas requeridas")
            return False

        # Extraer datos de niños
        children_df = extractor.extract_children_data()
        if children_df.empty:
            logger.error("❌ No se pudieron extraer datos de niños")
            return False

        # Extraer datos de menús
        menus_df = extractor.extract_menus_data()
        if menus_df.empty:
            logger.error("❌ No se pudieron extraer datos de menús")
            return False

        # Calcular compatibilidades
        compatibility_df = extractor.calculate_compatibility_scores(children_df, menus_df)

        # Generar feedback sintético REALISTA
        generator = RealisticFeedbackGenerator()
        feedback_df = generator.generate_realistic_feedback(compatibility_df, children_df, menus_df)

        # Guardar todos los datasets
        logger.info("💾 Guardando datasets...")

        # Datos procesados
        children_df.to_csv("data/processed/children_data.csv", index=False)
        menus_df.to_csv("data/processed/menus_data.csv", index=False)
        compatibility_df.to_csv("data/processed/compatibility_scores.csv", index=False)
        feedback_df.to_csv("data/processed/synthetic_feedback_realistic.csv", index=False)

        # Crear dataset combinado para entrenamiento
        training_data = []

        for _, feedback in feedback_df.iterrows():
            # Buscar datos del niño
            child_data = children_df[children_df["nin_id"] == feedback["nin_id"]].iloc[0]

            # Buscar datos del menú
            menu_data = menus_df[menus_df["mei_id"] == feedback["mei_id"]].iloc[0]

            # Buscar compatibilidad
            comp_data = compatibility_df[
                (compatibility_df["nin_id"] == feedback["nin_id"])
                & (compatibility_df["mei_id"] == feedback["mei_id"])
            ].iloc[0]

            # Combinar todos los datos
            combined_record = {
                **child_data.to_dict(),
                **menu_data.to_dict(),
                **comp_data.to_dict(),
                **feedback.to_dict(),
            }

            training_data.append(combined_record)

        training_df = pd.DataFrame(training_data)
        training_df.to_csv("data/processed/training_dataset_realistic.csv", index=False)

        # Generar SQL para insertar feedback (opcional)
        generate_insert_sql(feedback_df, "realistic")

        # Análisis de calidad del feedback generado
        analyze_feedback_quality(feedback_df)

        # Resumen final
        logger.info("\n" + "=" * 80)
        logger.info("✅ EXTRACCIÓN COMPLETADA EXITOSAMENTE - FEEDBACK REALISTA")
        logger.info("=" * 80)
        logger.info(f"👶 Niños extraídos: {len(children_df)}")
        logger.info(f"🍽️ Menús-items extraídos: {len(menus_df)}")
        logger.info(f"🎯 Compatibilidades calculadas: {len(compatibility_df)}")
        logger.info(f"🎭 Feedback REALISTA generado: {len(feedback_df)}")
        logger.info(f"📈 Dataset de entrenamiento: {len(training_df)} registros")
        logger.info("\n📁 Archivos generados:")
        logger.info("  - data/processed/children_data.csv")
        logger.info("  - data/processed/menus_data.csv")
        logger.info("  - data/processed/compatibility_scores.csv")
        logger.info("  - data/processed/synthetic_feedback_realistic.csv")
        logger.info("  - data/processed/training_dataset_realistic.csv")
        logger.info("  - data/processed/synthetic_feedback_realistic_insert.sql")

        return True

    except Exception as e:
        logger.error(f"❌ Error en el proceso principal: {e}")
        return False

    finally:
        extractor.disconnect_database()


def generate_insert_sql(feedback_df: pd.DataFrame, suffix: str = "realistic"):
    """Genera archivo SQL para insertar el feedback en la base de datos"""
    logger.info("📝 Generando archivo SQL de inserción...")

    sql_file = f"data/processed/synthetic_feedback_{suffix}_insert.sql"

    with open(sql_file, "w", encoding="utf-8") as f:
        f.write("-- Inserción de feedback sintético realista\n")
        f.write("-- Generado automáticamente\n\n")

        for _, row in feedback_df.iterrows():
            notes_value = f"'{row['mf_notas']}'" if pd.notna(row["mf_notas"]) else "NULL"

            sql = f"""INSERT INTO menus_feedback (mei_id, nin_id, mf_completado, mf_porcentaje_consumido, mf_rating, mf_notas, mf_fecha_consumo, mf_registrado_por)
VALUES ({row['mei_id']}, {row['nin_id']}, {row['mf_completado']}, {row['mf_porcentaje_consumido']}, {row['mf_rating']}, {notes_value}, '{row['mf_fecha_consumo']}', '{row['mf_registrado_por']}');
"""
            f.write(sql)

    logger.info(f"✅ Archivo SQL generado: {sql_file}")


def analyze_feedback_quality(feedback_df: pd.DataFrame):
    """Analiza la calidad y realismo del feedback generado"""
    logger.info("\n📊 ANÁLISIS DE CALIDAD DEL FEEDBACK REALISTA")
    logger.info("=" * 50)

    # Distribución de ratings
    rating_dist = feedback_df["mf_rating"].value_counts().sort_index()
    logger.info("📈 Distribución de ratings:")
    for rating, count in rating_dist.items():
        percentage = (count / len(feedback_df)) * 100
        logger.info(f"  ⭐ {rating} estrellas: {count} ({percentage:.1f}%)")

    # Estadísticas de consumo
    logger.info("\n🍽️ Estadísticas de consumo:")
    logger.info(f"  📊 Promedio: {feedback_df['mf_porcentaje_consumido'].mean():.1f}%")
    logger.info(f"  📊 Mediana: {feedback_df['mf_porcentaje_consumido'].median():.1f}%")
    logger.info(f"  📊 Desviación estándar: {feedback_df['mf_porcentaje_consumido'].std():.1f}%")

    # Tasa de completado
    completion_rate = (feedback_df["mf_completado"].sum() / len(feedback_df)) * 100
    logger.info(f"  ✅ Tasa de completado: {completion_rate:.1f}%")

    # Porcentaje con notas
    notes_rate = (feedback_df["mf_notas"].notna().sum() / len(feedback_df)) * 100
    logger.info(f"  📝 Registros con notas: {notes_rate:.1f}%")

    # Correlación rating vs consumo
    correlation = feedback_df["mf_rating"].corr(feedback_df["mf_porcentaje_consumido"])
    logger.info(f"  🔗 Correlación rating-consumo: {correlation:.3f}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extractor de Datos Reales con Feedback Sintético REALISTA"
    )
    parser.add_argument(
        "--config",
        choices=["default", "production", "development"],
        default="default",
        help="Tipo de configuración de BD",
    )

    args = parser.parse_args()

    success = main(args.config)

    if success:
        print("\n🎉 ¡Proceso completado exitosamente!")
        print("📁 Revisa los archivos generados en data/processed/")
        print("🚀 Ahora puedes ejecutar el entrenamiento del modelo ML con datos REALISTAS")
        print("📊 El feedback generado simula comportamiento infantil auténtico")
    else:
        print("\n❌ El proceso falló. Revisa los logs para más detalles.")
        exit(1)
