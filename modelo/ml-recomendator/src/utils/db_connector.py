"""
Conector a base de datos MySQL para extraer datos.
"""

import os
from pathlib import Path

import pandas as pd

# Cargar variables de entorno desde .env
from dotenv import load_dotenv

# Buscar .env en el directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)
    print(f"✅ Cargado .env desde: {ENV_PATH}")
else:
    print(f"⚠️  No se encontró .env en: {ENV_PATH}")

try:
    import pymysql

    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False

try:
    from sqlalchemy import create_engine

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


class DatabaseConnector:
    """
    Conector a MySQL para extraer datos para ML.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "nutricion_db",
    ):
        if not PYMYSQL_AVAILABLE and not SQLALCHEMY_AVAILABLE:
            raise ImportError("Instala pymysql o sqlalchemy: pip install pymysql sqlalchemy")

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.engine = None

    def connect(self):
        """Conecta a la base de datos."""
        if SQLALCHEMY_AVAILABLE:
            connection_string = (
                f"mysql+pymysql://{self.user}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
            # Configuración optimizada para alta latencia (220ms)
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,  # Verifica conexiones antes de usarlas
                pool_size=15,  # Pool más grande para concurrencia
                max_overflow=25,  # Conexiones temporales adicionales
                pool_timeout=45,  # Mayor timeout por latencia
                pool_recycle=1800,  # Reciclar cada 30min
                connect_args={
                    "connect_timeout": 15,
                    "read_timeout": 45,
                    "write_timeout": 45,
                },
            )
            print(f"✅ Conectado a {self.database} (SQLAlchemy con pooling optimizado)")

        elif PYMYSQL_AVAILABLE:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            print(f"✅ Conectado a {self.database} (PyMySQL)")

    def disconnect(self):
        """Desconecta de la base de datos."""
        if self.connection:
            self.connection.close()
            print("✅ Desconectado")

    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        Ejecuta una query y retorna DataFrame.

        Args:
            query: Query SQL (puede incluir %s para parámetros)
            params: Tupla de parámetros para la query

        Returns:
            DataFrame con resultados
        """
        if self.engine:
            return pd.read_sql(query, self.engine, params=params)
        elif self.connection:
            return pd.read_sql(query, self.connection, params=params)
        else:
            raise ConnectionError("No hay conexión a la base de datos")

    def call_procedure(self, procedure_name: str, params: list | None = None) -> pd.DataFrame:
        """
        Llama a un procedimiento almacenado.

        Args:
            procedure_name: Nombre del procedimiento
            params: Parámetros del procedimiento

        Returns:
            DataFrame con resultados
        """
        params = params or []

        # Usar PyMySQL directamente para procedimientos almacenados
        if not PYMYSQL_AVAILABLE:
            raise ImportError("PyMySQL es requerido para llamar procedimientos")

        # Crear conexión temporal con PyMySQL
        conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            autocommit=False,  # Control manual de commit
        )

        try:
            cursor = conn.cursor()

            # Construir CALL statement
            placeholders = ", ".join(["%s"] * len(params))
            query = f"CALL {procedure_name}({placeholders})"

            cursor.execute(query, params)

            # Obtener resultados
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()

            # IMPORTANTE: Hacer commit para guardar cambios
            conn.commit()

            cursor.close()
            conn.close()

            # Convertir a DataFrame
            if rows and columns:
                return pd.DataFrame(rows, columns=columns)
            else:
                return pd.DataFrame()

        except Exception as e:
            conn.rollback()  # Revertir en caso de error
            conn.close()
            raise e

    def extract_training_data(self) -> pd.DataFrame:
        """
        Extrae datos históricos para entrenamiento.

        Returns:
            DataFrame con datos de todos los niños
        """
        query = """
        SELECT
            -- Datos del niño
            n.nin_id,
            n.nin_nombres,
            n.nin_fecha_nac,
            n.nin_sexo as sex,
            TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as age_months,

            -- Antropometría
            a.ant_id,
            a.ant_fecha,
            a.ant_peso_kg as weight_kg,
            a.ant_talla_cm as height_cm,
            a.ant_peso_kg / POWER(a.ant_talla_cm / 100, 2) as BMI,
            COALESCE(a.ant_z_imc, 0) as baz,

            -- Features ML (si existen)
            f.fml_bmi_velocity as bmi_velocity,
            f.fml_weight_velocity as weight_velocity,
            f.fml_height_velocity as height_velocity,
            f.fml_baz_trend as baz_trend,
            f.fml_measurements_count as measurements_count,
            f.fml_adherence_score as adherence_score,
            f.fml_adherence_consistency as adherence_consistency,
            f.fml_menu_completion_rate as menu_completion_rate,
            f.fml_allergy_count as allergy_count,
            f.fml_allergy_severity_max as allergy_severity_max,
            f.fml_food_allergy_count as food_allergy_count,
            f.fml_has_severe_allergy as has_severe_allergy,
            f.fml_symptom_frequency as symptom_frequency,
            f.fml_symptom_severity_avg as symptom_severity_avg,
            f.fml_has_recent_symptoms as has_recent_symptoms,
            f.fml_dietary_diversity_score as dietary_diversity_score,
            f.fml_menu_kcal_avg as menu_kcal_avg,
            f.fml_protein_intake_score as protein_intake_score,

            -- Contexto
            COALESCE(e.ent_altitud_m, 0) as altitude_m,
            e.ent_zona as entity_zone,
            et.entti_codigo as entity_type

        FROM ninos n
        JOIN antropometrias a ON n.nin_id = a.nin_id
        LEFT JOIN features_ml f ON a.ant_id = f.ant_id AND f.nin_id = n.nin_id
        LEFT JOIN entidades e ON n.ent_id = e.ent_id
        LEFT JOIN entidad_tipos et ON e.entti_id = et.entti_id
        WHERE a.ant_peso_kg > 0
          AND a.ant_talla_cm > 0
          AND TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) BETWEEN 0 AND 228
          -- Solo la última antropometría por niño
          AND a.ant_id = (
              SELECT ant_id
              FROM antropometrias
              WHERE nin_id = n.nin_id
              ORDER BY ant_fecha DESC, creado_en DESC
              LIMIT 1
          )
        ORDER BY n.nin_id
        """

        print("📊 Extrayendo datos de entrenamiento...")
        df = self.execute_query(query)
        print(f"✅ Extraídos {len(df)} registros")

        # Eliminar duplicados - mantener solo un registro por niño
        # (el más reciente según ant_fecha)
        df_original_len = len(df)
        df = df.sort_values(["nin_id", "ant_fecha"], ascending=[True, False])
        df = df.drop_duplicates(subset=["nin_id"], keep="first")

        if len(df) < df_original_len:
            print(f"🔧 Eliminados {df_original_len - len(df)} registros duplicados")
            print(f"   Registros únicos: {len(df)}")

        return df

    def get_child_data(self, nin_id: int) -> pd.DataFrame:
        """
        Obtiene datos de un niño específico para predicción.

        Args:
            nin_id: ID del niño

        Returns:
            DataFrame con datos del niño
        """
        return self.call_procedure("sp_obtener_datos_para_ml", [nin_id])

    def save_prediction(
        self,
        nin_id: int,
        ant_id: int,
        fml_id: int | None,
        classification: str,
        probability: float,
        risk_score: float,
        probabilities: dict[str, float],
        model_type: str,
        model_version: str,
        features_json: dict | None = None,
        explanation_json: dict | None = None,
    ) -> int:
        """
        Guarda una predicción en la base de datos.

        Args:
            nin_id: ID del niño
            ant_id: ID de antropometría
            fml_id: ID de features ML
            classification: Clasificación predicha
            probability: Probabilidad de la clase
            risk_score: Score de riesgo
            probabilities: Probabilidades por clase
            model_type: Tipo de modelo
            model_version: Versión del modelo
            features_json: Features usados
            explanation_json: Explicación

        Returns:
            ID de la predicción guardada
        """
        import json

        query = """
        INSERT INTO predicciones_ml (
            nin_id, ant_id, fml_id,
            pml_clasificacion, pml_probabilidad, pml_score_riesgo,
            pml_prob_normal, pml_prob_riesgo, pml_prob_moderado, pml_prob_severo,
            pml_modelo_tipo, pml_modelo_version,
            pml_features_json, pml_explicacion_json
        ) VALUES (
            %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s
        )
        """

        params = [
            nin_id,
            ant_id,
            fml_id,
            classification,
            probability,
            risk_score,
            probabilities.get("NORMAL", 0),
            probabilities.get("RIESGO", 0),
            probabilities.get("MODERADO", 0),
            probabilities.get("SEVERO", 0),
            model_type,
            model_version,
            json.dumps(features_json) if features_json else None,
            json.dumps(explanation_json) if explanation_json else None,
        ]

        if self.connection:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            pml_id = cursor.lastrowid
            cursor.close()
            return pml_id
        else:
            raise NotImplementedError("save_prediction solo funciona con PyMySQL")

    @classmethod
    def from_env(cls) -> "DatabaseConnector":
        """
        Crea conector desde variables de entorno.

        Variables:
        - DB_HOST
        - DB_PORT
        - DB_USER
        - DB_PASSWORD
        - DB_NAME
        """
        return cls(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "nutricion_db"),
        )


def extract_and_save_training_data(output_path: Path, calculate_baz: bool = True):
    """
    Extrae datos de entrenamiento y los guarda en CSV.

    Args:
        output_path: Ruta donde guardar el CSV
        calculate_baz: Si True, calcula BAZ usando tablas OMS de MySQL
    """
    db = DatabaseConnector.from_env()
    db.connect()

    try:
        df = db.extract_training_data()

        # Calcular BAZ y clasificación si se solicita
        if calculate_baz:
            print("\n🔢 Calculando BAZ y clasificación desde tablas OMS en MySQL...")

            # Importar con path absoluto
            import sys
            from pathlib import Path

            BASE_DIR = Path(__file__).resolve().parent.parent.parent
            if str(BASE_DIR) not in sys.path:
                sys.path.insert(0, str(BASE_DIR))

            from src.features import WHOCalculator

            who_calc = WHOCalculator(db_connector=db)
            df = who_calc.process_dataframe(df)
            print(f"✅ BAZ y clasificación calculados para {len(df)} registros")

        # Guardar
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        print(f"\n✅ Datos guardados en: {output_path}")
        print(f"   Filas: {len(df)}")
        print(f"   Columnas: {len(df.columns)}")

        # Estadísticas
        print("\n📊 Estadísticas:")
        print(f"   Niños únicos: {df['nin_id'].nunique()}")
        print(f"   Edad promedio: {df['age_months'].mean():.1f} meses")
        print(f"   BMI promedio: {df['BMI'].mean():.2f}")

        if "baz" in df.columns:
            print(f"   BAZ promedio: {df['baz'].mean():.2f}")
            print("\n📊 Distribución de clasificación:")
            if "classification" in df.columns:
                print(df["classification"].value_counts())

    finally:
        db.disconnect()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extraer datos de BD para ML")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/surveys/datos_historicos.csv"),
        help="Ruta de salida del CSV",
    )

    args = parser.parse_args()

    extract_and_save_training_data(args.output)
