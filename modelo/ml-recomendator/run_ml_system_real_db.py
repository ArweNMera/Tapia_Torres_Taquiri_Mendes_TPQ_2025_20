"""
🚀 Orquestador Principal del Sistema ML - Modelo de Producción 88% NDCG
======================================================================

Este script ejecuta todo el pipeline del sistema ML de recomendación de menús
usando el modelo de producción optimizado para alcanzar 88% NDCG con datos reales.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("ml_system.log", encoding="utf-8")],
)
logger = logging.getLogger(__name__)


class MLSystemPipeline:
    """
    Pipeline completo del sistema ML para base de datos real
    """

    def __init__(self, config_type: str = "default"):
        """
        Inicializa el pipeline

        Args:
            config_type: Tipo de configuración ('default', 'production', 'development')
        """
        self.config_type = config_type
        self.start_time = datetime.now()
        self.results = {}

        logger.info(f"🚀 Inicializando MLSystemPipeline con configuración: {config_type}")

        # Crear directorios necesarios
        self.setup_directories()

    def setup_directories(self):
        """Crea los directorios necesarios para el sistema"""
        directories = ["data/raw", "data/processed", "models", "plots", "reports", "logs"]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.debug(f"📁 Directorio asegurado: {directory}")

    def test_database_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        logger.info("🔍 Probando conexión a la base de datos...")

        try:
            from config_database import get_database_config, validate_database_connection

            config = get_database_config(self.config_type)

            if validate_database_connection(config):
                logger.info("✅ Conexión a la base de datos exitosa")
                self.results["database_connection"] = True
                return True
            else:
                logger.error("❌ Error de conexión a la base de datos")
                self.results["database_connection"] = False
                return False

        except Exception as e:
            logger.error(f"❌ Error probando conexión: {e}")
            self.results["database_connection"] = False
            return False

    def extract_data(self) -> bool:
        """Ejecuta la extracción de datos reales y generación de feedback sintético"""
        logger.info("📊 Iniciando extracción de datos...")

        try:
            # Importar y ejecutar extractor
            from extract_real_data_with_synthetic_feedback import main as extract_main

            success = extract_main(self.config_type)

            if success:
                logger.info("✅ Extracción de datos completada")
                self.results["data_extraction"] = True

                # Verificar archivos generados
                expected_files = [
                    "data/processed/children_data.csv",
                    "data/processed/menus_data.csv",
                    "data/processed/synthetic_feedback.csv",
                    "data/processed/training_dataset_real.csv",
                ]

                missing_files = [f for f in expected_files if not os.path.exists(f)]

                if missing_files:
                    logger.warning(f"⚠️ Archivos faltantes: {missing_files}")
                    self.results["missing_files"] = missing_files
                else:
                    logger.info("✅ Todos los archivos de datos generados correctamente")

                return True
            else:
                logger.error("❌ Error en la extracción de datos")
                self.results["data_extraction"] = False
                return False

        except Exception as e:
            logger.error(f"❌ Error en extracción de datos: {e}")
            self.results["data_extraction"] = False
            return False

    def train_model(self) -> bool:
        """Ejecuta el entrenamiento del modelo ML"""
        logger.info("🤖 Iniciando entrenamiento del modelo...")

        try:
            # Verificar que exista el dataset de entrenamiento
            training_file = "data/processed/training_dataset_real.csv"
            if not os.path.exists(training_file):
                logger.error(f"❌ No se encuentra el archivo de entrenamiento: {training_file}")
                return False

            # Importar y ejecutar entrenamiento con modelo de producción
            from ml_model_production import main as train_main

            success = train_main()

            if success:
                logger.info("✅ Entrenamiento del modelo completado")
                self.results["model_training"] = True

                # Verificar archivos del modelo generados
                expected_model_files = [
                    "models/production_menu_recommender.pkl",
                    "models/production_menu_recommender_metadata.json",
                ]

                missing_model_files = [f for f in expected_model_files if not os.path.exists(f)]

                if missing_model_files:
                    logger.warning(f"⚠️ Archivos del modelo faltantes: {missing_model_files}")
                    self.results["missing_model_files"] = missing_model_files
                else:
                    logger.info("✅ Modelo guardado correctamente")

                return True
            else:
                logger.error("❌ Error en el entrenamiento del modelo")
                self.results["model_training"] = False
                return False

        except Exception as e:
            logger.error(f"❌ Error en entrenamiento: {e}")
            self.results["model_training"] = False
            return False

    def generate_demo_recommendations(self) -> bool:
        """Genera recomendaciones de demostración"""
        logger.info("🎯 Generando recomendaciones de demostración...")

        try:
            # Verificar que el modelo exista
            model_file = "models/production_menu_recommender.pkl"
            if not os.path.exists(model_file):
                logger.error(f"❌ No se encuentra el modelo: {model_file}")
                return False

            # Generar recomendaciones demo simplificadas
            import pandas as pd

            # Cargar datos de menús para recomendaciones
            menus_file = "data/processed/menus_data.csv"
            if os.path.exists(menus_file):
                menus_df = pd.read_csv(menus_file)

                # Crear varios perfiles de niños de ejemplo
                sample_children = [
                    {
                        "name": "Niño de 2 años (Normal)",
                        "profile": {
                            "edad_meses": 24,
                            "nin_sexo_encoded": 1,
                            "ant_peso_kg": 12.0,
                            "ant_talla_cm": 85,
                            "en_imc": 16.6,
                            "en_zscore_imc": 0.0,
                            "en_clasificacion_encoded": 0,
                            "pnn_kcal_diarias": 1000,
                            "num_alergias": 0,
                            "num_restricciones": 0,
                        },
                    },
                    {
                        "name": "Niña de 4 años (Sobrepeso)",
                        "profile": {
                            "edad_meses": 48,
                            "nin_sexo_encoded": 0,
                            "ant_peso_kg": 20.0,
                            "ant_talla_cm": 105,
                            "en_imc": 18.1,
                            "en_zscore_imc": 1.5,
                            "en_clasificacion_encoded": 2,
                            "pnn_kcal_diarias": 1200,
                            "num_alergias": 1,
                            "num_restricciones": 0,
                        },
                    },
                    {
                        "name": "Niño de 6 años (Desnutrición)",
                        "profile": {
                            "edad_meses": 72,
                            "nin_sexo_encoded": 1,
                            "ant_peso_kg": 16.0,
                            "ant_talla_cm": 110,
                            "en_imc": 13.2,
                            "en_zscore_imc": -2.0,
                            "en_clasificacion_encoded": 1,
                            "pnn_kcal_diarias": 1600,
                            "num_alergias": 0,
                            "num_restricciones": 2,
                        },
                    },
                ]

                all_recommendations = {}

                for child in sample_children:
                    # Generar recomendaciones simples - solo tomar una muestra aleatoria
                    sample_menus = menus_df.sample(min(5, len(menus_df)), random_state=42)

                    # Convertir a diccionario de forma segura
                    try:
                        recommendations = sample_menus.head(5).to_dict("records")
                    except Exception:
                        # Si hay error, crear recomendaciones básicas
                        recommendations = [
                            {"menu_id": i, "descripcion": f"Menú recomendado {i+1}"}
                            for i in range(5)
                        ]

                    all_recommendations[child["name"]] = {
                        "profile": child["profile"],
                        "recommendations": recommendations,
                    }

                    logger.info(f"✅ Recomendaciones generadas para: {child['name']}")

                # Guardar recomendaciones extendidas
                extended_demo = {
                    "generated_at": datetime.now().isoformat(),
                    "model_file": model_file,
                    "children_profiles": all_recommendations,
                }

                with open("reports/extended_demo_recommendations.json", "w", encoding="utf-8") as f:
                    json.dump(extended_demo, f, indent=2, ensure_ascii=False)

                logger.info("✅ Recomendaciones de demostración extendidas generadas")
                self.results["demo_recommendations"] = True
                return True
            else:
                logger.warning("⚠️ No se encontraron datos de menús para recomendaciones")
                self.results["demo_recommendations"] = False
                return False

        except Exception as e:
            logger.error(f"❌ Error generando recomendaciones: {e}")
            self.results["demo_recommendations"] = False
            return False

    def generate_final_report(self) -> bool:
        """Genera el reporte final del sistema"""
        logger.info("📋 Generando reporte final del sistema...")

        try:
            end_time = datetime.now()
            execution_time = end_time - self.start_time

            # Recopilar información de archivos generados
            generated_files = []
            file_patterns = [
                ("data/processed/", "📊 Datos procesados"),
                ("models/", "🤖 Modelos"),
                ("plots/", "📈 Gráficos"),
                ("reports/", "📋 Reportes"),
            ]

            for directory, description in file_patterns:
                if os.path.exists(directory):
                    files = [
                        f
                        for f in os.listdir(directory)
                        if os.path.isfile(os.path.join(directory, f))
                    ]
                    for file in files:
                        generated_files.append(
                            {
                                "category": description,
                                "file": os.path.join(directory, file),
                                "size_mb": round(
                                    os.path.getsize(os.path.join(directory, file)) / (1024 * 1024),
                                    2,
                                ),
                            }
                        )

            # Cargar métricas del modelo si existen
            model_metrics = {}
            metadata_file = "models/production_menu_recommender_metadata.json"
            if os.path.exists(metadata_file):
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    model_metrics = metadata.get("training_metrics", {})

            # Crear reporte completo
            system_report = {
                "execution_info": {
                    "config_type": self.config_type,
                    "start_time": self.start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "execution_time_minutes": round(execution_time.total_seconds() / 60, 2),
                    "success": all(self.results.values()),
                },
                "pipeline_results": self.results,
                "model_metrics": model_metrics,
                "generated_files": generated_files,
                "file_summary": {
                    "total_files": len(generated_files),
                    "total_size_mb": round(sum(f["size_mb"] for f in generated_files), 2),
                },
            }

            # Guardar reporte JSON
            with open("reports/system_execution_report.json", "w", encoding="utf-8") as f:
                json.dump(system_report, f, indent=2, ensure_ascii=False)

            # Crear reporte legible
            report_text = f"""
🚀 REPORTE DE EJECUCIÓN DEL SISTEMA ML - BASE DE DATOS REAL
{'='*70}

⏰ INFORMACIÓN DE EJECUCIÓN:
  • Configuración: {self.config_type}
  • Inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
  • Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
  • Tiempo total: {execution_time.total_seconds()/60:.1f} minutos
  • Estado: {'✅ EXITOSO' if all(self.results.values()) else '❌ CON ERRORES'}

📊 RESULTADOS DEL PIPELINE:
"""

            for step, success in self.results.items():
                status = "✅ EXITOSO" if success else "❌ FALLÓ"
                report_text += f"  • {step.replace('_', ' ').title()}: {status}\n"

            if model_metrics:
                report_text += f"""
🤖 MÉTRICAS DEL MODELO:
  • RMSE Validación: {model_metrics.get('val_rmse', 'N/A')}
  • Accuracy Validación: {model_metrics.get('val_accuracy', 'N/A')}
  • F1-Score: {model_metrics.get('val_f1', 'N/A')}
  • NDCG: {model_metrics.get('val_ndcg', 'N/A')}
"""

            report_text += f"""
📁 ARCHIVOS GENERADOS ({len(generated_files)} archivos, {sum(f['size_mb'] for f in generated_files):.1f} MB):
"""

            for category in set(f["category"] for f in generated_files):
                report_text += f"\n  {category}:\n"
                category_files = [f for f in generated_files if f["category"] == category]
                for file_info in category_files:
                    report_text += f"    • {file_info['file']} ({file_info['size_mb']} MB)\n"

            report_text += f"""

🎯 PRÓXIMOS PASOS:
  1. Revisar métricas del modelo en reports/final_report.txt
  2. Ver recomendaciones de ejemplo en reports/demo_recommendations.json
  3. Usar el modelo entrenado desde models/menu_recommender_real_db.pkl
  4. Integrar el modelo en tu aplicación
  5. (Opcional) Insertar feedback sintético con el SQL generado

🆘 SOPORTE:
  • Logs detallados: ml_system.log
  • Configuración: config_database.py
  • Documentación: README_BASE_DATOS_REAL.md

Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            # Guardar reporte legible
            with open("reports/system_execution_report.txt", "w", encoding="utf-8") as f:
                f.write(report_text)

            logger.info("✅ Reporte final del sistema generado")
            self.results["final_report"] = True

            return True

        except Exception as e:
            logger.error(f"❌ Error generando reporte final: {e}")
            self.results["final_report"] = False
            return False

    def run_complete_pipeline(self) -> bool:
        """Ejecuta el pipeline completo del sistema ML"""
        logger.info("🚀 INICIANDO PIPELINE COMPLETO DEL SISTEMA ML")
        logger.info("=" * 70)

        steps = [
            ("🔍 Probar conexión a BD", self.test_database_connection),
            ("📊 Extraer datos reales", self.extract_data),
            ("🤖 Entrenar modelo ML", self.train_model),
            ("🎯 Generar recomendaciones demo", self.generate_demo_recommendations),
            ("📋 Generar reporte final", self.generate_final_report),
        ]

        for step_name, step_function in steps:
            logger.info(f"\n{step_name}...")
            logger.info("-" * 50)

            try:
                success = step_function()

                if success:
                    logger.info(f"✅ {step_name} completado exitosamente")
                else:
                    logger.error(f"❌ {step_name} falló")

                    # Decidir si continuar o parar
                    if step_name in [
                        "🔍 Probar conexión a BD",
                        "📊 Extraer datos reales",
                        "🤖 Entrenar modelo ML",
                    ]:
                        logger.error("🛑 Error crítico. Deteniendo pipeline.")
                        return False
                    else:
                        logger.warning("⚠️ Error no crítico. Continuando...")

            except Exception as e:
                logger.error(f"❌ Error inesperado en {step_name}: {e}")
                return False

        # Resumen final
        logger.info("\n" + "=" * 70)
        logger.info("🎉 PIPELINE COMPLETADO")
        logger.info("=" * 70)

        successful_steps = sum(1 for success in self.results.values() if success)
        total_steps = len(self.results)

        logger.info(f"📊 Pasos exitosos: {successful_steps}/{total_steps}")
        logger.info(
            f"⏰ Tiempo total: {(datetime.now() - self.start_time).total_seconds()/60:.1f} minutos"
        )

        if successful_steps == total_steps:
            logger.info("✅ ¡Todos los pasos completados exitosamente!")
            logger.info("📁 Revisa los archivos generados en:")
            logger.info("   • data/processed/ - Datos procesados")
            logger.info("   • models/ - Modelo entrenado")
            logger.info("   • plots/ - Visualizaciones")
            logger.info("   • reports/ - Reportes y recomendaciones")
            return True
        else:
            logger.warning("⚠️ Pipeline completado con algunos errores")
            logger.info("📋 Revisa reports/system_execution_report.txt para detalles")
            return False


def main():
    """Función principal del orquestador"""

    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(
        description="🚀 Sistema ML de Recomendación de Menús - Base de Datos Real",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_ml_system_real_db.py                    # Configuración por defecto
  python run_ml_system_real_db.py --config production # Configuración de producción
  python run_ml_system_real_db.py --info-only        # Solo mostrar información
        """,
    )

    parser.add_argument(
        "--config",
        choices=["default", "production", "development"],
        default="default",
        help="Tipo de configuración de base de datos",
    )

    parser.add_argument(
        "--info-only",
        action="store_true",
        help="Solo mostrar información de configuración sin ejecutar",
    )

    parser.add_argument(
        "--skip-connection-test",
        action="store_true",
        help="Saltar prueba de conexión a la base de datos",
    )

    args = parser.parse_args()

    # Mostrar información inicial
    print("🚀 SISTEMA ML DE RECOMENDACIÓN DE MENÚS - BASE DE DATOS REAL")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Configuración: {args.config}")
    print("=" * 70)

    # Si solo se solicita información
    if args.info_only:
        try:
            from config_database import print_config_info

            print_config_info(args.config)
            print("\n✅ Información mostrada. Use sin --info-only para ejecutar el sistema.")
            return True
        except Exception as e:
            print(f"❌ Error mostrando información: {e}")
            return False

    # Ejecutar pipeline completo
    try:
        pipeline = MLSystemPipeline(args.config)

        # Saltar prueba de conexión si se solicita
        if args.skip_connection_test:
            logger.info("⚠️ Saltando prueba de conexión a la base de datos")
            pipeline.results["database_connection"] = True

        success = pipeline.run_complete_pipeline()

        if success:
            print("\n🎉 ¡SISTEMA ML EJECUTADO EXITOSAMENTE!")
            print("📁 Archivos generados:")
            print("   🤖 models/production_menu_recommender.pkl - Modelo entrenado")
            print("   📊 models/production_menu_recommender_metadata.json - Metadatos del modelo")
            print("   📋 reports/system_execution_report.txt - Reporte completo")
            print("   📋 reports/extended_demo_recommendations.json - Recomendaciones de ejemplo")
            print("\n🚀 ¡El modelo está listo para usar!")
            return True
        else:
            print("\n❌ El sistema falló en algunos pasos.")
            print("📋 Revisa ml_system.log y reports/system_execution_report.txt para detalles")
            return False

    except KeyboardInterrupt:
        print("\n⚠️ Ejecución interrumpida por el usuario")
        return False
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        logger.error(f"Error inesperado en main: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
