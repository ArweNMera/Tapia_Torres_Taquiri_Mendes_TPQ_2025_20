"""
Extractor de datos para entrenamiento del modelo de predicción nutricional.
Extrae datos históricos de antropometrías, adherencias y síntomas.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)


class NutritionalStatusDataExtractor:
    """
    Extrae datos de la base de datos para entrenar el modelo de predicción nutricional.
    """

    def __init__(self, db_connection_string: str):
        """
        Inicializar extractor.

        Args:
            db_connection_string: String de conexión a MySQL
        """
        self.engine = create_engine(db_connection_string)
        logger.info("✅ NutritionalStatusDataExtractor inicializado")

    def extract_training_data(
        self,
        min_measurements: int = 2,
        lookback_months: int = 24,
        include_synthetic: bool = False,
        target_size: int = 180,
    ) -> pd.DataFrame:
        """
        Extraer datos de entrenamiento completos.

        Args:
            min_measurements: Mínimo de mediciones por niño para incluirlo
            lookback_months: Meses hacia atrás para considerar
            include_synthetic: Si incluir datos sintéticos (para aumentar dataset)

        Returns:
            DataFrame con features y target
        """
        logger.info("📊 Extrayendo datos de entrenamiento...")
        logger.info(f"   - Mínimo mediciones: {min_measurements}")
        logger.info(f"   - Lookback: {lookback_months} meses")
        logger.info(f"   - Incluir sintéticos: {include_synthetic}")

        # 1. Obtener niños con suficientes mediciones
        ninos_validos = self._get_valid_children(min_measurements, lookback_months)
        logger.info(f"✅ {len(ninos_validos)} niños con suficientes mediciones")

        if ninos_validos.empty:
            logger.warning("⚠️ No hay niños con suficientes mediciones")
            return pd.DataFrame()

        # 2. Extraer features para cada niño
        all_features = []

        for _, nino in ninos_validos.iterrows():
            nin_id = nino["nin_id"]

            try:
                # Obtener mediciones del niño
                measurements = self._get_child_measurements(nin_id, lookback_months)

                if len(measurements) < min_measurements:
                    continue

                # Para cada medición (excepto la primera), crear un registro de entrenamiento
                for i in range(1, len(measurements)):
                    features = self._build_features_for_measurement(nin_id, measurements, i, nino)

                    if features is not None:
                        all_features.append(features)

            except Exception as e:
                logger.warning(f"⚠️ Error procesando niño {nin_id}: {e}")
                continue

        if not all_features:
            logger.warning("⚠️ No se pudieron extraer features")
            return pd.DataFrame()

        # 3. Convertir a DataFrame
        df = pd.DataFrame(all_features)
        logger.info(f"✅ Dataset extraído: {len(df)} registros, {len(df.columns)} columnas")

        # 4. Agregar datos sintéticos si se solicita
        if include_synthetic and len(df) > 0:
            # Calcular factor para alcanzar target_size (pero limitado)
            current_size = len(df)
            needed = min(target_size - current_size, current_size * 4)  # Máximo 4x los datos reales
            factor = needed / current_size if current_size > 0 else 3.0
            factor = min(factor, 3.5)  # Máximo 3.5x para evitar overfitting

            logger.info(
                f"🎯 Target: ~{int(current_size * (1 + factor))} registros (actuales: {current_size}, factor: {factor:.2f})"
            )
            df_synthetic = self._generate_synthetic_data(df, factor=factor)

            # Generar datos para clases faltantes
            df_missing = self._generate_missing_classes_data(df, target_per_class=25)

            df = pd.concat([df, df_synthetic, df_missing], ignore_index=True)
            logger.info(f"✅ Dataset con sintéticos: {len(df)} registros")

        # 5. Validar y limpiar
        df = self._validate_and_clean(df)

        logger.info(f"✅ Dataset final: {len(df)} registros")
        logger.info("   Distribución de clases:")
        if "clasificacion_oms" in df.columns:
            for clase, count in df["clasificacion_oms"].value_counts().items():
                logger.info(f"      {clase}: {count} ({count/len(df)*100:.1f}%)")

        return df

    def _get_valid_children(self, min_measurements: int, lookback_months: int) -> pd.DataFrame:
        """Obtener niños con suficientes mediciones."""
        query = text(
            """
            SELECT
                n.nin_id,
                n.nin_sexo,
                COUNT(DISTINCT a.ant_id) as num_mediciones,
                MIN(a.ant_fecha) as primera_medicion,
                MAX(a.ant_fecha) as ultima_medicion
            FROM ninos n
            INNER JOIN antropometrias a ON n.nin_id = a.nin_id
            WHERE a.ant_fecha >= DATE_SUB(CURDATE(), INTERVAL :lookback_months MONTH)
                AND a.ant_peso_kg IS NOT NULL
                AND a.ant_talla_cm IS NOT NULL
            GROUP BY n.nin_id, n.nin_sexo
            HAVING num_mediciones >= :min_measurements
            ORDER BY num_mediciones DESC
            """
        )

        with self.engine.connect() as conn:
            df = pd.read_sql(
                query,
                conn,
                params={"min_measurements": min_measurements, "lookback_months": lookback_months},
            )

        return df

    def _get_child_measurements(self, nin_id: int, lookback_months: int) -> pd.DataFrame:
        """Obtener mediciones antropométricas de un niño."""
        query = text(
            """
            SELECT
                a.ant_id,
                a.ant_fecha,
                a.ant_peso_kg,
                a.ant_talla_cm,
                a.ant_z_imc,
                en.en_clasificacion,
                en.en_z_score_imc,
                en.en_imc
            FROM antropometrias a
            LEFT JOIN evaluaciones_nutricionales en ON a.ant_id = en.ant_id
            WHERE a.nin_id = :nin_id
                AND a.ant_fecha >= DATE_SUB(CURDATE(), INTERVAL :lookback_months MONTH)
                AND a.ant_peso_kg IS NOT NULL
                AND a.ant_talla_cm IS NOT NULL
            ORDER BY a.ant_fecha ASC
            """
        )

        with self.engine.connect() as conn:
            df = pd.read_sql(
                query, conn, params={"nin_id": nin_id, "lookback_months": lookback_months}
            )

        return df

    def _build_features_for_measurement(
        self, nin_id: int, measurements: pd.DataFrame, current_idx: int, nino_info: pd.Series
    ) -> Optional[dict]:
        """
        Construir features para una medición específica.

        Args:
            nin_id: ID del niño
            measurements: DataFrame con todas las mediciones del niño
            current_idx: Índice de la medición actual
            nino_info: Información del niño

        Returns:
            Diccionario con features o None si no se puede construir
        """
        try:
            current = measurements.iloc[current_idx]
            fecha_actual = current["ant_fecha"]

            # Features antropométricos actuales
            age_months = self._calculate_age_months(nin_id, fecha_actual)
            sex_numeric = 1 if nino_info["nin_sexo"] == "M" else 0
            weight_kg = float(current["ant_peso_kg"])
            height_cm = float(current["ant_talla_cm"])
            bmi = weight_kg / ((height_cm / 100) ** 2)

            # Velocidades de cambio (últimos 3 meses)
            velocities = self._calculate_velocities(measurements, current_idx)

            # Adherencia (últimos 30 días)
            adherence_score = self._calculate_adherence_score(nin_id, fecha_actual)

            # Contexto
            allergy_count = self._get_allergy_count(nin_id, fecha_actual)
            altitude_m = self._get_altitude(nin_id, fecha_actual)

            # Target: Clasificación OMS
            clasificacion = current.get("en_clasificacion")
            if pd.isna(clasificacion) or clasificacion is None:
                # Si no hay clasificación, calcularla del z-score
                z_score = current.get("en_z_score_imc") or current.get("ant_z_imc")
                if pd.isna(z_score):
                    return None
                clasificacion = self._z_score_to_classification(z_score)

            features = {
                # Features
                "age_months": age_months,
                "sex_numeric": sex_numeric,
                "BMI": bmi,
                "weight_kg": weight_kg,
                "height_cm": height_cm,
                "bmi_velocity": velocities["bmi_velocity"],
                "weight_velocity": velocities["weight_velocity"],
                "height_velocity": velocities["height_velocity"],
                "adherence_score": adherence_score,
                "allergy_count": allergy_count,
                "altitude_m": altitude_m,
                # Target
                "clasificacion_oms": clasificacion,
                # Metadata
                "nin_id": nin_id,
                "ant_id": current["ant_id"],
                "fecha": fecha_actual,
            }

            return features

        except Exception as e:
            logger.warning(f"⚠️ Error construyendo features: {e}")
            return None

    def _calculate_age_months(self, nin_id: int, fecha: datetime) -> int:
        """Calcular edad en meses en una fecha específica."""
        query = text(
            """
            SELECT TIMESTAMPDIFF(MONTH, nin_fecha_nac, :fecha) as edad_meses
            FROM ninos
            WHERE nin_id = :nin_id
            """
        )

        with self.engine.connect() as conn:
            result = conn.execute(query, {"nin_id": nin_id, "fecha": fecha}).fetchone()

        return int(result[0]) if result else 120  # Default: 10 años

    def _calculate_velocities(self, measurements: pd.DataFrame, current_idx: int) -> dict:
        """Calcular velocidades de cambio de los últimos 3 meses."""
        current = measurements.iloc[current_idx]
        current_date = current["ant_fecha"]

        # Buscar medición de hace ~3 meses
        three_months_ago = current_date - timedelta(days=90)

        # Encontrar la medición más cercana a 3 meses atrás
        past_measurements = measurements[measurements["ant_fecha"] < current_date]

        if len(past_measurements) == 0:
            return {"bmi_velocity": 0.0, "weight_velocity": 0.0, "height_velocity": 0.0}

        # Tomar la más reciente antes de la actual
        past = past_measurements.iloc[-1]

        # Calcular diferencias
        days_diff = (current_date - past["ant_fecha"]).days
        if days_diff == 0:
            return {"bmi_velocity": 0.0, "weight_velocity": 0.0, "height_velocity": 0.0}

        months_diff = days_diff / 30.0

        # BMI
        current_bmi = current["ant_peso_kg"] / ((current["ant_talla_cm"] / 100) ** 2)
        past_bmi = past["ant_peso_kg"] / ((past["ant_talla_cm"] / 100) ** 2)
        bmi_velocity = (current_bmi - past_bmi) / months_diff

        # Peso
        weight_velocity = (current["ant_peso_kg"] - past["ant_peso_kg"]) / months_diff

        # Talla
        height_velocity = (current["ant_talla_cm"] - past["ant_talla_cm"]) / months_diff

        return {
            "bmi_velocity": float(bmi_velocity),
            "weight_velocity": float(weight_velocity),
            "height_velocity": float(height_velocity),
        }

    def _calculate_adherence_score(self, nin_id: int, fecha: datetime) -> float:
        """Calcular score de adherencia de los últimos 30 días."""
        query = text(
            """
            SELECT AVG(adh_porcentaje) as adherencia_promedio
            FROM adherencias
            WHERE nin_id = :nin_id
                AND adh_registrado_en BETWEEN DATE_SUB(:fecha, INTERVAL 30 DAY) AND :fecha
            """
        )

        with self.engine.connect() as conn:
            result = conn.execute(query, {"nin_id": nin_id, "fecha": fecha}).fetchone()

        return float(result[0]) if result and result[0] is not None else 75.0  # Default: 75%

    def _get_allergy_count(self, nin_id: int, fecha: datetime) -> int:
        """Obtener número de alergias del niño."""
        query = text(
            """
            SELECT COUNT(*) as num_alergias
            FROM ninos_alergias
            WHERE nin_id = :nin_id
                AND creado_en <= :fecha
            """
        )

        with self.engine.connect() as conn:
            result = conn.execute(query, {"nin_id": nin_id, "fecha": fecha}).fetchone()

        return int(result[0]) if result else 0

    def _get_altitude(self, nin_id: int, fecha: datetime) -> float:
        """Obtener altitud de la entidad del niño."""
        query = text(
            """
            SELECT COALESCE(e.ent_altitud_m, 0) as altitud
            FROM ninos n
            LEFT JOIN entidades e ON n.ent_id = e.ent_id
            WHERE n.nin_id = :nin_id
            """
        )

        with self.engine.connect() as conn:
            result = conn.execute(query, {"nin_id": nin_id}).fetchone()

        return float(result[0]) if result else 0.0

    def _z_score_to_classification(self, z_score: float) -> str:
        """Convertir z-score a clasificación OMS (7 clases)."""
        if z_score < -3:
            return "DESNUTRICION_SEVERA"  # z < -3
        elif z_score < -2:
            return "DESNUTRICION_MODERADA"  # -3 <= z < -2
        elif z_score < -1:
            return "RIESGO_DESNUTRICION"  # -2 <= z < -1
        elif z_score <= 1:
            return "NORMAL"  # -1 <= z <= 1
        elif z_score <= 2:
            return "RIESGO_SOBREPESO"  # 1 < z <= 2
        elif z_score <= 3:
            return "SOBREPESO"  # 2 < z <= 3
        else:
            return "OBESIDAD"  # z > 3

    def _generate_synthetic_data(self, df: pd.DataFrame, factor: float = 0.3) -> pd.DataFrame:
        """
        Generar datos sintéticos realistas usando interpolación entre muestras (SMOTE-like).

        Args:
            df: DataFrame original
            factor: Factor de aumento (0.3 = 30% más datos)

        Returns:
            DataFrame con datos sintéticos balanceados y realistas
        """

        # Calcular cuántos sintéticos generar por clase para balancear
        class_counts = df["clasificacion_oms"].value_counts()
        max_count = class_counts.max()

        synthetic_rows = []

        logger.info("🔄 Generando datos sintéticos con interpolación SMOTE-like...")

        for clase in class_counts.index:
            # Calcular cuántos sintéticos necesita esta clase
            current_count = class_counts[clase]
            # Balancear moderadamente (no perfecto para evitar overfitting)
            target_count = int(max_count * (1 + factor * 0.7))
            n_to_generate = max(target_count - current_count, int(current_count * factor * 0.9))

            logger.info(
                f"   {clase}: {current_count} → {current_count + n_to_generate} (+{n_to_generate})"
            )

            # Obtener registros de esta clase
            class_df = df[df["clasificacion_oms"] == clase]

            # Si solo hay 1 registro, usar ruido simple
            if len(class_df) == 1:
                for _ in range(n_to_generate):
                    base_row = class_df.iloc[0].to_dict()
                    base_row = self._add_simple_noise(base_row)
                    synthetic_rows.append(base_row)
            else:
                # Usar interpolación SMOTE-like entre pares de muestras
                for _ in range(n_to_generate):
                    # Seleccionar dos muestras aleatorias de la misma clase
                    samples = class_df.sample(n=2)
                    sample1 = samples.iloc[0]
                    sample2 = samples.iloc[1]

                    # Crear muestra sintética interpolando entre las dos
                    synthetic_row = self._interpolate_samples(sample1, sample2)
                    synthetic_rows.append(synthetic_row)

        logger.info(f"✅ Generados {len(synthetic_rows)} registros sintéticos realistas")
        return pd.DataFrame(synthetic_rows)

    def _add_simple_noise(self, row: dict) -> dict:
        """Agregar ruido simple a un registro."""
        import numpy as np

        noise_features = {
            "age_months": 0.10,  # 10% variación
            "BMI": 0.18,  # 18% variación (muy alto)
            "weight_kg": 0.15,
            "height_cm": 0.10,
            "bmi_velocity": 0.30,  # 30% variación en velocidades
            "weight_velocity": 0.30,
            "height_velocity": 0.25,
            "adherence_score": 0.28,  # 28% variación
        }

        new_row = row.copy()
        for feature, noise_factor in noise_features.items():
            if feature in new_row and new_row[feature] is not None:
                noise = np.random.normal(0, noise_factor * abs(new_row[feature]))
                new_row[feature] = new_row[feature] + noise

                # Asegurar rangos válidos
                if feature in ["age_months", "BMI", "weight_kg", "height_cm"]:
                    new_row[feature] = max(new_row[feature], 1.0)
                elif feature == "adherence_score":
                    new_row[feature] = np.clip(new_row[feature], 0, 100)

        return new_row

    def _interpolate_samples(self, sample1: pd.Series, sample2: pd.Series) -> dict:
        """
        Interpolar entre dos muestras (SMOTE-like).
        Crea una nueva muestra en el espacio entre dos muestras existentes.
        """
        import numpy as np

        # Factor de interpolación aleatorio entre 0.3 y 0.7 (evitar extremos)
        alpha = np.random.uniform(0.3, 0.7)

        synthetic_row = {}

        # Features numéricos: interpolar
        numeric_features = [
            "age_months",
            "BMI",
            "weight_kg",
            "height_cm",
            "bmi_velocity",
            "weight_velocity",
            "height_velocity",
            "adherence_score",
            "altitude_m",
        ]

        for feature in numeric_features:
            if feature in sample1.index and feature in sample2.index:
                val1 = sample1[feature]
                val2 = sample2[feature]

                if pd.notna(val1) and pd.notna(val2):
                    # Interpolación con ruido MUY ALTO para máxima diversidad
                    interpolated = alpha * val1 + (1 - alpha) * val2
                    # Ruido muy alto (12-25%) + variación adicional
                    noise_factor = np.random.uniform(0.12, 0.25)
                    noise = np.random.normal(0, noise_factor * abs(interpolated))

                    # Agregar variación extra ocasionalmente (30% probabilidad)
                    if np.random.random() < 0.3:
                        extra_noise = np.random.uniform(-0.15, 0.15) * abs(interpolated)
                        noise += extra_noise

                    synthetic_row[feature] = interpolated + noise

                    # Asegurar rangos válidos
                    if feature in ["age_months", "BMI", "weight_kg", "height_cm"]:
                        synthetic_row[feature] = max(synthetic_row[feature], 1.0)
                    elif feature == "adherence_score":
                        synthetic_row[feature] = np.clip(synthetic_row[feature], 0, 100)
                else:
                    synthetic_row[feature] = val1 if pd.notna(val1) else val2

        # Features categóricos/enteros: elegir uno u otro con variación
        if "sex_numeric" in sample1.index:
            # 40% probabilidad de cada muestra, 20% aleatorio
            rand = np.random.random()
            if rand < 0.4:
                synthetic_row["sex_numeric"] = sample1["sex_numeric"]
            elif rand < 0.8:
                synthetic_row["sex_numeric"] = sample2["sex_numeric"]
            else:
                synthetic_row["sex_numeric"] = np.random.randint(0, 2)

        if "allergy_count" in sample1.index:
            # Mezclar con variación
            avg_allergies = (sample1["allergy_count"] + sample2["allergy_count"]) / 2
            synthetic_row["allergy_count"] = int(
                np.clip(avg_allergies + np.random.randint(-1, 2), 0, 5)
            )

        # Mantener clasificación y metadata de sample1
        for feature in ["clasificacion_oms", "nin_id", "ant_id", "fecha"]:
            if feature in sample1.index:
                synthetic_row[feature] = sample1[feature]

        return synthetic_row

    def _generate_missing_classes_data(
        self, df: pd.DataFrame, target_per_class: int = 25
    ) -> pd.DataFrame:
        """
        Generar datos sintéticos para clases que no existen en los datos reales.
        Usa conocimiento médico de rangos de z-scores para cada clasificación.
        """
        import numpy as np

        # Definir todas las clases posibles (7 clases OMS)
        all_classes = [
            "DESNUTRICION_SEVERA",
            "DESNUTRICION_MODERADA",
            "RIESGO_DESNUTRICION",
            "NORMAL",
            "RIESGO_SOBREPESO",
            "SOBREPESO",
            "OBESIDAD",
        ]

        # Clases que ya existen y cuántas tienen
        existing_classes = df["clasificacion_oms"].value_counts().to_dict()

        # Generar para clases faltantes O con pocos datos (< 10)
        classes_to_generate = []
        for c in all_classes:
            if c not in existing_classes:
                classes_to_generate.append((c, target_per_class))
            elif existing_classes[c] < 10:
                classes_to_generate.append((c, target_per_class - existing_classes[c]))

        if not classes_to_generate:
            logger.info("✅ Todas las clases tienen suficientes datos")
            return pd.DataFrame()

        missing_classes = [c for c, _ in classes_to_generate]

        logger.info(f"🔧 Generando datos para clases faltantes: {missing_classes}")

        # Rangos de BMI con SOLAPAMIENTO para más realismo
        # Los rangos se solapan para simular casos límite
        bmi_ranges = {
            "DESNUTRICION_SEVERA": (9.5, 13.5),  # Solapado con moderada
            "DESNUTRICION_MODERADA": (12, 15),  # Solapado con severa y riesgo
            "RIESGO_DESNUTRICION": (13.5, 17),  # Solapado con moderada y normal
            "NORMAL": (14.5, 20),  # Amplio rango, solapado con riesgos
            "RIESGO_SOBREPESO": (17.5, 22),  # Solapado con normal y sobrepeso
            "SOBREPESO": (19, 25),  # Solapado con riesgo y obesidad
            "OBESIDAD": (22, 35),  # Solapado con sobrepeso
        }

        synthetic_rows = []

        # Usar datos existentes como base para estadísticas
        age_mean = df["age_months"].mean()
        age_std = df["age_months"].std()

        for clase, n_samples in classes_to_generate:
            logger.info(f"   Generando {n_samples} muestras para {clase}")

            bmi_min, bmi_max = bmi_ranges.get(clase, (16, 19))

            for _ in range(n_samples):
                # Generar edad variada
                age = np.clip(
                    np.random.normal(age_mean, age_std * 1.5),
                    24,
                    180,  # 2-15 años
                )

                # Generar BMI según la clase
                bmi = np.random.uniform(bmi_min, bmi_max)

                # Calcular peso y talla consistentes con BMI y edad
                # Talla aproximada por edad (cm)
                height = 75 + (age / 12) * 5 + np.random.normal(0, 5)
                height = np.clip(height, 70, 180)

                # Peso consistente con BMI
                weight = bmi * ((height / 100) ** 2)
                weight = np.clip(weight, 8, 80)

                # Velocidades con MUCHO SOLAPAMIENTO para más realismo
                # Agregar ruido aleatorio adicional
                base_noise = np.random.uniform(-0.15, 0.15)

                if clase == "DESNUTRICION_SEVERA":
                    bmi_vel = np.random.uniform(-0.5, 0.1) + base_noise
                    weight_vel = np.random.uniform(-0.7, 0.2) + base_noise
                elif clase == "DESNUTRICION_MODERADA":
                    bmi_vel = np.random.uniform(-0.35, 0.15) + base_noise
                    weight_vel = np.random.uniform(-0.5, 0.25) + base_noise
                elif clase == "RIESGO_DESNUTRICION":
                    bmi_vel = np.random.uniform(-0.25, 0.2) + base_noise
                    weight_vel = np.random.uniform(-0.3, 0.35) + base_noise
                elif clase == "NORMAL":
                    bmi_vel = np.random.uniform(-0.2, 0.25) + base_noise
                    weight_vel = np.random.uniform(-0.15, 0.5) + base_noise
                elif clase == "RIESGO_SOBREPESO":
                    bmi_vel = np.random.uniform(-0.1, 0.35) + base_noise
                    weight_vel = np.random.uniform(0.05, 0.6) + base_noise
                elif clase == "SOBREPESO":
                    bmi_vel = np.random.uniform(0.0, 0.5) + base_noise
                    weight_vel = np.random.uniform(0.15, 0.8) + base_noise
                else:  # OBESIDAD
                    bmi_vel = np.random.uniform(0.1, 0.7) + base_noise
                    weight_vel = np.random.uniform(0.3, 1.2) + base_noise

                height_vel = np.random.uniform(0.3, 0.8)  # Siempre positivo en niños

                # Adherencia: mejor en normales, peor en extremos
                if clase == "NORMAL":
                    adherence = np.random.uniform(70, 95)
                elif clase in ["DESNUTRICION_SEVERA", "OBESIDAD"]:
                    adherence = np.random.uniform(35, 65)
                elif clase in ["DESNUTRICION_MODERADA", "SOBREPESO"]:
                    adherence = np.random.uniform(45, 75)
                else:  # RIESGO_DESNUTRICION, RIESGO_SOBREPESO
                    adherence = np.random.uniform(55, 85)

                synthetic_row = {
                    "age_months": age,
                    "sex_numeric": np.random.randint(0, 2),
                    "BMI": bmi,
                    "weight_kg": weight,
                    "height_cm": height,
                    "bmi_velocity": bmi_vel,
                    "weight_velocity": weight_vel,
                    "height_velocity": height_vel,
                    "adherence_score": adherence,
                    "allergy_count": np.random.randint(0, 3),
                    "altitude_m": np.random.choice([0, 500, 1500, 2500, 3500]),
                    "clasificacion_oms": clase,
                    "nin_id": 9999,  # ID ficticio
                    "ant_id": 9999,
                    "fecha": pd.Timestamp.now(),
                }

                synthetic_rows.append(synthetic_row)

        logger.info(f"✅ Generados {len(synthetic_rows)} registros para clases faltantes")
        return pd.DataFrame(synthetic_rows)

    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validar y limpiar dataset."""
        logger.info("🧹 Validando y limpiando dataset...")

        initial_len = len(df)

        # Eliminar NaN en features críticos
        critical_features = [
            "age_months",
            "BMI",
            "weight_kg",
            "height_cm",
            "clasificacion_oms",
        ]

        df = df.dropna(subset=critical_features)

        # Rellenar NaN en features opcionales con 0
        optional_features = [
            "bmi_velocity",
            "weight_velocity",
            "height_velocity",
            "adherence_score",
            "allergy_count",
            "altitude_m",
        ]

        for feature in optional_features:
            if feature in df.columns:
                df[feature] = df[feature].fillna(0.0)

        # Eliminar outliers extremos
        df = df[df["BMI"] > 10]  # BMI mínimo razonable
        df = df[df["BMI"] < 40]  # BMI máximo razonable
        df = df[df["age_months"] > 0]
        df = df[df["age_months"] < 216]  # Máximo 18 años

        final_len = len(df)
        removed = initial_len - final_len

        if removed > 0:
            logger.info(
                f"   Eliminados {removed} registros inválidos ({removed/initial_len*100:.1f}%)"
            )

        return df

    def save_dataset(self, df: pd.DataFrame, output_path: str) -> None:
        """Guardar dataset a CSV."""
        df.to_csv(output_path, index=False)
        logger.info(f"💾 Dataset guardado en: {output_path}")


def main():
    """Función principal para testing."""
    import os

    from dotenv import load_dotenv

    load_dotenv()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        logger.error("❌ DATABASE_URL no encontrada en .env")
        return

    extractor = NutritionalStatusDataExtractor(db_url)

    # Extraer datos con factor alto para ~180 registros
    df = extractor.extract_training_data(
        min_measurements=2, lookback_months=24, include_synthetic=True
    )

    if not df.empty:
        # Guardar
        output_path = "data/nutritional_status_training_data.csv"
        extractor.save_dataset(df, output_path)

        logger.info(f"✅ Extracción completada: {len(df)} registros")
    else:
        logger.warning("⚠️ No se pudieron extraer datos")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
