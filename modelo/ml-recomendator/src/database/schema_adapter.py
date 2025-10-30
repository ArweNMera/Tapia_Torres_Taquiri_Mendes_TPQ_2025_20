"""
Adaptador de esquema para mapear tablas reales de la BD MySQL a features del modelo.

Este módulo valida el acceso a tablas y extrae datos para ML usando el esquema real.
"""

import logging
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import MetaData, Table, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class SchemaValidator:
    """
    Validador de esquema para verificar acceso a tablas requeridas.
    """

    REQUIRED_TABLES = [
        "ninos",  # Datos de niños
        "antropometrias",  # Medidas antropométricas
        "evaluaciones_nutricionales",  # Evaluaciones nutricionales
        "ninos_alergias",  # Alergias
        "ninos_comidas_favoritas",  # Preferencias
        "ninos_restricciones_alimentos",  # Restricciones
        "menus",  # Menús
        "menus_items",  # Items de menús
        "menus_feedback",  # Feedback de menús
        "recetas",  # Recetas
        "alimentos_nutrientes",  # Nutrientes de alimentos
        "recetas_ingredientes",  # Ingredientes de recetas
        "features_ml",  # Features precomputadas si existen
    ]

    def __init__(self):
        pass

    def validate_table_access(self, engine, table_name: str) -> bool:
        """
        Valida si una tabla existe y es accesible.

        Args:
            engine: SQLAlchemy engine
            table_name: Nombre de la tabla

        Returns:
            True si la tabla es accesible
        """
        try:
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)
            with engine.connect() as conn:
                conn.execute(text(f"SELECT 1 FROM {table_name} LIMIT 1"))
            return True
        except SQLAlchemyError as e:
            logger.warning(f"Tabla {table_name} no accesible: {str(e)}")
            return False

    def validate_schema(self, engine) -> Dict[str, bool]:
        """
        Valida todas las tablas requeridas.

        Returns:
            Diccionario con estado de cada tabla
        """
        return {table: self.validate_table_access(engine, table) for table in self.REQUIRED_TABLES}


class MLDataExtractor:
    """
    Extractor de datos para ML desde el esquema real.
    """

    def __init__(self, engine):
        self.engine = engine
        self.validator = SchemaValidator()

    def extract_child_features(self, child_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Extrae features de niños desde las tablas reales.

        Returns:
            DataFrame con features de niños
        """
        query = """
        SELECT
            n.nin_id as child_id,
            n.nin_nombres as nombre,
            n.nin_fecha_nac as fecha_nacimiento,
            n.nin_sexo as sexo,
            a.ant_peso_kg as peso_kg,
            a.ant_talla_cm as talla_cm,
            a.ant_fecha as fecha_antropometria,
            a.ant_z_imc as z_score_imc,
            a.ant_z_peso_edad as z_score_peso_edad,
            a.ant_z_talla_edad as z_score_talla_edad,
            en.en_clasificacion as clasificacion_nutricional,
            en.en_nivel_riesgo as nivel_riesgo,
            GROUP_CONCAT(DISTINCT na.ta_id) as alergias_tipos,
            GROUP_CONCAT(DISTINCT na.na_severidad) as alergias_severidad,
            GROUP_CONCAT(DISTINCT ncf.rec_id) as comidas_favoritas,
            GROUP_CONCAT(DISTINCT nra.ali_id) as restricciones_alimentarias,
            GROUP_CONCAT(DISTINCT nra.nra_tipo) as tipos_restricciones
        FROM ninos n
        LEFT JOIN antropometrias a ON n.nin_id = a.nin_id
            AND a.ant_fecha = (
                SELECT MAX(ant_fecha)
                FROM antropometrias a2
                WHERE a2.nin_id = n.nin_id
            )
        LEFT JOIN evaluaciones_nutricionales en ON a.ant_id = en.ant_id
        LEFT JOIN ninos_alergias na ON n.nin_id = na.nin_id AND na.na_activo = 1
        LEFT JOIN ninos_comidas_favoritas ncf ON n.nin_id = ncf.nin_id
        LEFT JOIN ninos_restricciones_alimentos nra ON n.nin_id = nra.nin_id AND nra.nra_activo = 1
        GROUP BY n.nin_id, n.nin_nombres, n.nin_fecha_nac, n.nin_sexo,
                 a.ant_peso_kg, a.ant_talla_cm, a.ant_fecha, a.ant_z_imc,
                 a.ant_z_peso_edad, a.ant_z_talla_edad, en.en_clasificacion, en.en_nivel_riesgo
        """

        if child_ids:
            query += f" HAVING n.nin_id IN ({','.join(map(str, child_ids))})"

        return pd.read_sql(text(query), self.engine)

    def extract_menu_features(self, menu_ids: Optional[List[int]] = None) -> pd.DataFrame:
        """
        Extrae features de menús desde las tablas reales.

        Returns:
            DataFrame con features de menús
        """
        base_query = """
        SELECT
            m.men_id as menu_id,
            m.nin_id as child_id,
            m.men_generado_por as generado_por,
            m.men_inicio as fecha_inicio,
            m.men_fin as fecha_fin,
            m.men_kcal_total as kcal_total,
            m.men_estado as estado,
            COUNT(DISTINCT mi.rec_id) as num_recetas,
            GROUP_CONCAT(DISTINCT mi.mei_comida) as tipos_comida,
            AVG(mf.mf_rating) as avg_rating,
            AVG(mf.mf_porcentaje_consumido) as avg_porcentaje_consumido,
            COUNT(DISTINCT mf.mf_id) as total_feedback_entries,
            SUM(CASE WHEN mf.mf_completado = 1 THEN 1 ELSE 0 END) as comidas_completadas
        FROM menus m
        LEFT JOIN menus_items mi ON m.men_id = mi.men_id
        LEFT JOIN menus_feedback mf ON mi.mei_id = mf.mei_id
        WHERE m.men_estado IN ('APROBADO', 'BORRADOR')
        """

        if menu_ids:
            base_query += f" AND m.men_id IN ({','.join(map(str, menu_ids))})"

        query = (
            base_query
            + """
        GROUP BY m.men_id, m.nin_id, m.men_generado_por, m.men_inicio, m.men_fin, m.men_kcal_total, m.men_estado
        """
        )

        df = pd.read_sql(text(query), self.engine)
        df["tipos_comida_list"] = df["tipos_comida"].apply(
            lambda x: x.split(",") if pd.notna(x) else []
        )
        return df

    def extract_ml_features(self) -> pd.DataFrame:
        """
        Extrae features precomputadas si existen.
        """
        if self.validator.validate_table_access(self.engine, "features_ml"):
            query = "SELECT * FROM features_ml"
            return pd.read_sql(query, self.engine)
        else:
            logger.warning("Tabla features_ml no disponible")
            return pd.DataFrame()
