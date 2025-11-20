"""
🔧 Configuración de Base de Datos para Sistema ML
=================================================

Este archivo maneja las configuraciones de conexión a la base de datos
para el sistema de recomendación de menús con datos reales.
"""

import os
from typing import Any, Dict

from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


def get_default_config() -> Dict[str, Any]:
    """Configuración por defecto para desarrollo local"""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "nutricion"),
        "charset": "utf8mb4",
        "autocommit": True,
        "raise_on_warnings": True,
    }


def get_production_config() -> Dict[str, Any]:
    """Configuración para producción (DigitalOcean Database)"""
    return {
        "host": os.getenv("DB_HOST_PROD", os.getenv("DB_HOST", "")),
        "port": int(os.getenv("DB_PORT_PROD", os.getenv("DB_PORT", "25060"))),
        "user": os.getenv("DB_USER_PROD", os.getenv("DB_USER", "")),
        "password": os.getenv("DB_PASSWORD_PROD", os.getenv("DB_PASSWORD", "")),
        "database": os.getenv("DB_NAME_PROD", os.getenv("DB_NAME", "nutricion")),
        "charset": "utf8mb4",
        "autocommit": True,
        "raise_on_warnings": True,
        "ssl_disabled": True,
        "ssl_verify_cert": False,
        "ssl_verify_identity": False,
        "use_unicode": True,
    }


def get_development_config() -> Dict[str, Any]:
    """Configuración para desarrollo con datos de prueba"""
    return {
        "host": os.getenv("DB_HOST_DEV", "localhost"),
        "port": int(os.getenv("DB_PORT_DEV", "3306")),
        "user": os.getenv("DB_USER_DEV", "dev_user"),
        "password": os.getenv("DB_PASSWORD_DEV", ""),
        "database": os.getenv("DB_NAME_DEV", "nutricion_dev"),
        "charset": "utf8mb4",
        "autocommit": True,
        "raise_on_warnings": True,
    }


def get_database_config(config_type: str = "default") -> Dict[str, Any]:
    """
    Obtiene la configuración de base de datos según el tipo especificado

    Args:
        config_type: 'default', 'production', o 'development'

    Returns:
        Dict con la configuración de la base de datos
    """
    configs = {
        "default": get_default_config(),
        "production": get_production_config(),
        "development": get_development_config(),
    }

    if config_type not in configs:
        raise ValueError(
            f"Tipo de configuración '{config_type}' no válido. Opciones: {list(configs.keys())}"
        )

    return configs[config_type]


ML_TABLES_CONFIG = {
    # Configuración de tablas ML
    "ml_tables": {
        "children": "ninos",
        "menus": "menus",
        "menu_feedback": "menus_feedback",
        "synthetic_feedback": "synthetic_feedback",
        "perfil_nutricional": "perfil_nutricional_nino",
        "antropometrias": "antropometrias",
        "menus_items": "menus_items",
        "menus_nutrientes": "menus_nutrientes",
    },
    "real_tables": {
        "ninos": {
            "id": "nin_id",
            "nombre": "nin_nombres",
            "fecha_nacimiento": "nin_fecha_nac",
            "sexo": "nin_sexo",
            "tutor_id": "usr_id_tutor",
            "propietario_id": "usr_id_propietario",
            "entidad_id": "ent_id",
        },
        "antropometrias": {
            "id": "ant_id",
            "nin_id": "nin_id",
            "fecha": "ant_fecha",
            "edad_meses": "ant_edad_meses",
            "peso_kg": "ant_peso_kg",
            "talla_cm": "ant_talla_cm",
            "z_imc": "ant_z_imc",
            "z_peso_edad": "ant_z_peso_edad",
            "z_talla_edad": "ant_z_talla_edad",
        },
        "perfil_nutricional_nino": {
            "id": "pnn_id",
            "nin_id": "nin_id",
            "calorias_diarias": "pnn_calorias_diarias",
            "proteinas_g": "pnn_proteinas_g",
            "carbohidratos_g": "pnn_carbohidratos_g",
            "grasas_g": "pnn_grasas_g",
            "edad_meses": "pnn_edad_meses",
            "peso_kg": "pnn_peso_kg",
            "talla_cm": "pnn_talla_cm",
            "clasificacion": "pnn_clasificacion",
            "vigente": "pnn_vigente",
            "fecha_calculo": "pnn_fecha_calculo",
        },
        "menus": {
            "id": "men_id",
            "nin_id": "nin_id",
            "generado_por": "men_generado_por",
            "inicio": "men_inicio",
            "fin": "men_fin",
            "kcal_total": "men_kcal_total",
            "estado": "men_estado",
        },
        "menus_items": {
            "id": "mei_id",
            "men_id": "men_id",
            "dia_idx": "mei_dia_idx",
            "comida": "mei_comida",
            "rec_id": "rec_id",
            "kcal": "mei_kcal",
        },
        "menus_feedback": {
            "id": "mf_id",
            "mei_id": "mei_id",
            "nin_id": "nin_id",
            "completado": "mf_completado",
            "porcentaje_consumido": "mf_porcentaje_consumido",
            "rating": "mf_rating",
            "notas": "mf_notas",
            "fecha_consumo": "mf_fecha_consumo",
            "registrado_por": "mf_registrado_por",
        },
    },
    # Tabla para datos SINTÉTICOS (escritura permitida)
    "synthetic_tables": {
        "menus_feedback": {
            "required_columns": [
                "mf_id",
                "mei_id",
                "nin_id",
                "mf_rating",
                "mf_porcentaje_consumido",
            ],
            "description": "Feedback sintético de menús",
            "writable": True,
        }
    },
}


FEATURE_CONFIG = {
    "child_features": [
        "edad_meses",
        "nin_sexo_encoded",
        "ant_peso_kg",
        "ant_talla_cm",
        "en_imc",
        "en_zscore_imc",
        "en_clasificacion_encoded",
        "pnn_kcal_diarias",
        "num_alergias",
    ],
    "menu_features": [
        "mei_comida_encoded",
        "mei_kcal",
        "men_generado_por_encoded",
        "num_items_menu",
        "calorias_promedio_item",
    ],
    "compatibility_features": [
        "caloric_compatibility_score",
        "age_compatibility_score",
        "nutritional_balance_score",
    ],
    "temporal_features": ["hora_del_dia", "dia_semana"],
}

# ========================================
# 🎲 CONFIGURACIÓN DE DATOS SINTÉTICOS
# ========================================

SYNTHETIC_DATA_CONFIG = {
    "n_feedback_records": 2000,
    "rating_distribution": {
        1: 0.05,  # 5% ratings de 1 estrella
        2: 0.10,  # 10% ratings de 2 estrellas
        3: 0.25,  # 25% ratings de 3 estrellas
        4: 0.35,  # 35% ratings de 4 estrellas
        5: 0.25,  # 25% ratings de 5 estrellas
    },
    "consumption_patterns": {
        "high_rating_consumption": (80, 100),  # 80-100% consumo para ratings altos
        "medium_rating_consumption": (50, 80),  # 50-80% consumo para ratings medios
        "low_rating_consumption": (10, 50),  # 10-50% consumo para ratings bajos
    },
    "compatibility_factors": {
        "caloric_weight": 0.4,
        "nutritional_weight": 0.3,
        "age_weight": 0.2,
        "preference_weight": 0.1,
    },
}


def print_config_info(config_type: str = "default"):
    """Imprime información sobre la configuración actual"""
    print(f"\n🔧 CONFIGURACIÓN DE BASE DE DATOS ({config_type.upper()})")
    print("=" * 50)

    config = get_database_config(config_type)
    for key, value in config.items():
        if key == "password":
            print(f"  {key}: {'*' * len(str(value))}")
        else:
            print(f"  {key}: {value}")

    print("\n📊 TABLAS REQUERIDAS:")
    print("  Tablas REALES (solo lectura):")
    for table, info in ML_TABLES_CONFIG["real_tables"].items():
        print(f"    ✅ {table}: Tabla de datos reales")

    print("  Tablas SINTÉTICAS (escritura permitida):")
    for table, info in ML_TABLES_CONFIG["synthetic_tables"].items():
        print(f"    🎲 {table}: {info['description']}")

    print("\n🎯 CARACTERÍSTICAS ML:")
    print(f"  - Características del niño: {len(FEATURE_CONFIG['child_features'])}")
    print(f"  - Características del menú: {len(FEATURE_CONFIG['menu_features'])}")
    print(f"  - Características de compatibilidad: {len(FEATURE_CONFIG['compatibility_features'])}")
    print(f"  - Características temporales: {len(FEATURE_CONFIG['temporal_features'])}")

    print("\n🎲 DATOS SINTÉTICOS:")
    print(f"  - Registros de feedback a generar: {SYNTHETIC_DATA_CONFIG['n_feedback_records']}")
    print(f"  - Distribución de ratings: {SYNTHETIC_DATA_CONFIG['rating_distribution']}")


def validate_database_connection(config: Dict[str, Any]) -> bool:
    """
    Valida la conexión a la base de datos

    Args:
        config: Configuración de la base de datos

    Returns:
        bool: True si la conexión es exitosa
    """
    try:
        import mysql.connector

        connection = mysql.connector.connect(**config)

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            connection.close()

            return result is not None
        else:
            return False

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def get_required_tables() -> list:
    """Retorna la lista de todas las tablas requeridas"""
    tables = []
    tables.extend(ML_TABLES_CONFIG["real_tables"].keys())
    tables.extend(ML_TABLES_CONFIG["synthetic_tables"].keys())
    return tables


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Configuración de Base de Datos ML")
    parser.add_argument(
        "--config",
        choices=["default", "production", "development"],
        default="default",
        help="Tipo de configuración",
    )
    parser.add_argument(
        "--test-connection", action="store_true", help="Probar conexión a la base de datos"
    )

    args = parser.parse_args()

    # Mostrar información de configuración
    print_config_info(args.config)

    # Probar conexión si se solicita
    if args.test_connection:
        print("\n🔍 PROBANDO CONEXIÓN...")
        config = get_database_config(args.config)
        if validate_database_connection(config):
            print("✅ Conexión exitosa!")
        else:
            print("❌ Error de conexión!")
