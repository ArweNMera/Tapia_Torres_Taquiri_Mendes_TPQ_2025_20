"""
Database Schema Adapter for ML Model
Maps the real database schema to ML model requirements.
Only includes necessary tables and columns for the hybrid recommendation system.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
import pandas as pd


@dataclass
class DatabaseSchema:
    """Defines the database schema mapping for ML model"""

    # Core tables needed for ML model
    REQUIRED_TABLES = {
        "ninos": ["nin_id", "nin_nombres", "nin_fecha_nac", "nin_sexo"],
        "menus": [
            "men_id",
            "nin_id",
            "men_generado_por",
            "men_inicio",
            "men_fin",
            "men_kcal_total",
            "men_estado",
            "creado_en",
        ],
        "menus_items": [
            "mei_id",
            "men_id",
            "mei_dia_idx",
            "mei_comida",
            "rec_id",
            "mei_kcal",
        ],
        "recetas": ["rec_id", "rec_nombre", "rec_instrucciones", "rec_activo"],
        "recetas_ingredientes": ["rec_id", "ali_id", "ri_cantidad", "ri_unidad"],
        "alimentos": ["ali_id", "ali_nombre", "ali_categoria", "ali_activo"],
        "alimentos_nutrientes": ["ali_id", "nutri_id", "aln_cantidad"],
        "nutrientes": ["nutri_id", "nutri_codigo", "nutri_nombre", "nutri_unidad"],
        "antropometrias": [
            "ant_id",
            "nin_id",
            "ant_peso",
            "ant_talla",
            "ant_fecha",
            "ant_imc",
            "ant_percentil_peso",
            "ant_percentil_talla",
            "ant_percentil_imc",
        ],
        "ninos_alergias": ["na_id", "nin_id", "ta_id", "na_severidad", "na_activo"],
        "tipos_alergias": ["ta_id", "ta_codigo", "ta_nombre", "ta_categoria"],
        "ninos_restricciones_alimentos": [
            "nra_id",
            "nin_id",
            "ali_id",
            "nra_tipo",
            "nra_severidad",
            "nra_activo",
        ],
        "perfil_nutricional_nino": [
            "pnn_id",
            "nin_id",
            "pnn_calorias_diarias",
            "pnn_proteinas_g",
            "pnn_carbohidratos_g",
            "pnn_grasas_g",
            "pnn_hierro_mg",
            "pnn_calcio_mg",
            "pnn_vitamina_a_ug",
            "pnn_vitamina_c_mg",
            "pnn_zinc_mg",
            "pnn_fibra_g",
            "pnn_clasificacion",
            "pnn_vigente",
        ],
        "menus_feedback": [
            "mf_id",
            "mei_id",
            "nin_id",
            "mf_completado",
            "mf_porcentaje_consumido",
            "mf_rating",
            "mf_fecha_consumo",
        ],
        "ninos_comidas_favoritas": ["ncf_id", "nin_id", "rec_id", "creado_en"],
        "recetas_comidas": ["rec_id", "rc_comida"],
        "menus_nutrientes": [
            "mn_id",
            "men_id",
            "mn_kcal_total",
            "mn_proteina_g",
            "mn_carbohidratos_g",
            "mn_grasas_g",
            "mn_fibra_g",
            "mn_hierro_mg",
            "mn_calcio_mg",
            "mn_vitamina_a_ug",
            "mn_vitamina_c_mg",
            "mn_zinc_mg",
            "mn_diversity_score",
            "mn_quality_score",
        ],
    }

    # Key nutrient codes we care about for ML
    CORE_NUTRIENTS = [
        "KCAL",  # Calorías
        "PROT",  # Proteínas
        "CARB",  # Carbohidratos
        "FAT",  # Grasas
        "FIBER",  # Fibra
        "IRON",  # Hierro
        "CALC",  # Calcio
        "VITA",  # Vitamina A
        "VITC",  # Vitamina C
        "ZINC",  # Zinc
    ]

    # Meal types mapping
    MEAL_TYPES = ["DESAYUNO", "ALMUERZO", "CENA", "REFACCION"]

    # Nutritional status classifications
    NUTRITIONAL_STATUS = [
        "DESNUTRICION_SEVERA",
        "DESNUTRICION",
        "RIESGO",
        "NORMAL",
        "SOBREPESO",
        "OBESIDAD",
    ]

    # Allergy severity levels
    ALLERGY_SEVERITY = ["LEVE", "MODERADA", "SEVERA"]

    # Food restriction types
    RESTRICTION_TYPES = [
        "ALERGIA",
        "INTOLERANCIA",
        "PREFERENCIA",
        "CULTURAL",
        "RELIGIOSA",
        "MEDICA",
    ]


class SchemaValidator:
    """Validates that queries only use allowed tables and columns"""

    def __init__(self):
        self.schema = DatabaseSchema()

    def validate_table_access(self, table_name: str) -> bool:
        """Check if table is allowed for ML model"""
        return table_name in self.schema.REQUIRED_TABLES

    def validate_column_access(self, table_name: str, columns: List[str]) -> bool:
        """Check if columns are allowed for the given table"""
        if not self.validate_table_access(table_name):
            return False

        allowed_columns = self.schema.REQUIRED_TABLES[table_name]
        return all(col in allowed_columns for col in columns)

    def get_allowed_columns(self, table_name: str) -> List[str]:
        """Get list of allowed columns for a table"""
        return self.schema.REQUIRED_TABLES.get(table_name, [])

    def build_safe_query(
        self,
        table_name: str,
        columns: List[str] = None,
        where_clause: str = "",
        joins: List[str] = None,
    ) -> str:
        """Build a safe SQL query using only allowed tables and columns"""

        if not self.validate_table_access(table_name):
            raise ValueError(f"Table '{table_name}' not allowed for ML model")

        # Use all allowed columns if none specified
        if columns is None:
            columns = self.get_allowed_columns(table_name)
        else:
            if not self.validate_column_access(table_name, columns):
                raise ValueError(f"Some columns not allowed for table '{table_name}'")

        # Build base query
        query = f"SELECT {', '.join(columns)} FROM {table_name}"

        # Add joins if specified
        if joins:
            for join in joins:
                # Validate join tables
                join_table = join.split()[2]  # Extract table name from JOIN clause
                if not self.validate_table_access(join_table):
                    raise ValueError(f"Join table '{join_table}' not allowed")
                query += f" {join}"

        # Add where clause
        if where_clause:
            query += f" WHERE {where_clause}"

        return query


class MLDataExtractor:
    """Extracts data for ML model using only allowed schema elements"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.validator = SchemaValidator()
        self.schema = DatabaseSchema()

    def get_child_features(self, child_id: int) -> Dict[str, Any]:
        """Extract child features using only allowed columns"""

        # Basic child info
        child_query = self.validator.build_safe_query(
            "ninos", ["nin_id", "nin_fecha_nac", "nin_sexo"], f"nin_id = {child_id}"
        )

        # Latest anthropometry
        anthro_query = self.validator.build_safe_query(
            "antropometrias",
            [
                "ant_peso",
                "ant_talla",
                "ant_imc",
                "ant_percentil_peso",
                "ant_percentil_talla",
                "ant_percentil_imc",
            ],
            f"nin_id = {child_id} ORDER BY ant_fecha DESC LIMIT 1",
        )

        # Nutritional profile
        profile_query = self.validator.build_safe_query(
            "perfil_nutricional_nino",
            [
                "pnn_calorias_diarias",
                "pnn_proteinas_g",
                "pnn_carbohidratos_g",
                "pnn_grasas_g",
                "pnn_clasificacion",
            ],
            f"nin_id = {child_id} AND pnn_vigente = 1",
        )

        # Allergies
        allergies_query = self.validator.build_safe_query(
            "ninos_alergias",
            ["ta_id", "na_severidad"],
            f"nin_id = {child_id} AND na_activo = 1",
        )

        # Execute queries and combine results
        child_data = pd.read_sql(child_query, self.db)
        anthro_data = pd.read_sql(anthro_query, self.db)
        profile_data = pd.read_sql(profile_query, self.db)
        allergies_data = pd.read_sql(allergies_query, self.db)

        return {
            "child_info": child_data.to_dict("records")[0]
            if not child_data.empty
            else {},
            "anthropometry": anthro_data.to_dict("records")[0]
            if not anthro_data.empty
            else {},
            "nutrition_profile": profile_data.to_dict("records")[0]
            if not profile_data.empty
            else {},
            "allergies": allergies_data.to_dict("records")
            if not allergies_data.empty
            else [],
        }

    def get_recipe_features(self, recipe_id: int) -> Dict[str, Any]:
        """Extract recipe features using only allowed columns"""

        # Basic recipe info
        recipe_query = self.validator.build_safe_query(
            "recetas",
            ["rec_id", "rec_nombre"],
            f"rec_id = {recipe_id} AND rec_activo = 1",
        )

        # Recipe meal types
        meal_types_query = self.validator.build_safe_query(
            "recetas_comidas", ["rc_comida"], f"rec_id = {recipe_id}"
        )

        # Recipe ingredients with nutritional info
        ingredients_query = """
        SELECT ri.ali_id, ri.ri_cantidad, ri.ri_unidad,
               a.ali_nombre, a.ali_categoria,
               an.nutri_id, an.aln_cantidad, n.nutri_codigo
        FROM recetas_ingredientes ri
        JOIN alimentos a ON ri.ali_id = a.ali_id
        JOIN alimentos_nutrientes an ON a.ali_id = an.ali_id
        JOIN nutrientes n ON an.nutri_id = n.nutri_id
        WHERE ri.rec_id = %s AND a.ali_activo = 1
        AND n.nutri_codigo IN %s
        """

        # Execute queries
        recipe_data = pd.read_sql(recipe_query, self.db)
        meal_types_data = pd.read_sql(meal_types_query, self.db)
        ingredients_data = pd.read_sql(
            ingredients_query,
            self.db,
            params=[recipe_id, tuple(self.schema.CORE_NUTRIENTS)],
        )

        return {
            "recipe_info": recipe_data.to_dict("records")[0]
            if not recipe_data.empty
            else {},
            "meal_types": meal_types_data["rc_comida"].tolist()
            if not meal_types_data.empty
            else [],
            "ingredients": ingredients_data.to_dict("records")
            if not ingredients_data.empty
            else [],
        }

    def get_feedback_data(
        self, child_id: int = None, recipe_id: int = None
    ) -> pd.DataFrame:
        """Extract feedback data for training labels"""

        where_conditions = []
        if child_id:
            where_conditions.append(f"mf.nin_id = {child_id}")
        if recipe_id:
            where_conditions.append(f"mi.rec_id = {recipe_id}")

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        feedback_query = (
            """
        SELECT mf.nin_id, mi.rec_id, mf.mf_rating, mf.mf_completado,
               mf.mf_porcentaje_consumido, mi.mei_comida
        FROM menus_feedback mf
        JOIN menus_items mi ON mf.mei_id = mi.mei_id
        WHERE """
            + where_clause
        )

        return pd.read_sql(feedback_query, self.db)

    def get_menu_candidates(self, meal_type: str = None) -> pd.DataFrame:
        """Get available recipes as menu candidates"""

        where_conditions = ["r.rec_activo = 1"]
        if meal_type and meal_type in self.schema.MEAL_TYPES:
            where_conditions.append(f"rc.rc_comida = '{meal_type}'")

        where_clause = " AND ".join(where_conditions)

        candidates_query = f"""
        SELECT DISTINCT r.rec_id, r.rec_nombre
        FROM recetas r
        JOIN recetas_comidas rc ON r.rec_id = rc.rec_id
        WHERE {where_clause}
        """

        return pd.read_sql(candidates_query, self.db)


# Usage example and validation
def validate_ml_queries():
    """Validate that all ML queries use only allowed schema elements"""
    validator = SchemaValidator()

    # Test cases
    test_cases = [
        ("ninos", ["nin_id", "nin_nombres"]),  # Should pass
        ("ninos", ["nin_id", "invalid_column"]),  # Should fail
        ("invalid_table", ["any_column"]),  # Should fail
        ("recetas", ["rec_id", "rec_nombre"]),  # Should pass
    ]

    for table, columns in test_cases:
        try:
            is_valid = validator.validate_column_access(table, columns)
            print(
                f"Table: {table}, Columns: {columns} -> {'VALID' if is_valid else 'INVALID'}"
            )
        except Exception as e:
            print(f"Table: {table}, Columns: {columns} -> ERROR: {e}")


if __name__ == "__main__":
    validate_ml_queries()
