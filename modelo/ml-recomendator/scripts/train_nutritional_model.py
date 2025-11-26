"""
Script completo para entrenar el modelo de predicción nutricional.
Ejecuta todo el pipeline: extracción → entrenamiento → validación.
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from src.training.extract_nutritional_status_data import NutritionalStatusDataExtractor
from src.training.train_nutritional_predictor import NutritionalPredictorTrainer

logger = logging.getLogger(__name__)


def main():
    """Pipeline completo de entrenamiento."""
    parser = argparse.ArgumentParser(
        description="Pipeline completo de entrenamiento del modelo nutricional"
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Saltar extracción de datos (usar CSV existente)",
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default="data/nutritional_status_training_data.csv",
        help="Ruta al archivo CSV de datos",
    )
    parser.add_argument(
        "--output-model",
        type=str,
        default=None,
        help="Ruta donde guardar el modelo (default: models/nutritional_predictor_TIMESTAMP.pkl)",
    )
    parser.add_argument(
        "--min-measurements",
        type=int,
        default=3,
        help="Mínimo de mediciones por niño (default: 3)",
    )
    parser.add_argument(
        "--lookback-months",
        type=int,
        default=12,
        help="Meses hacia atrás para considerar (default: 12)",
    )
    parser.add_argument(
        "--include-synthetic",
        action="store_true",
        help="Incluir datos sintéticos para aumentar dataset",
    )
    parser.add_argument(
        "--validation-split",
        type=float,
        default=0.2,
        help="Proporción de datos para validación (default: 0.2)",
    )
    parser.add_argument(
        "--num-boost-round",
        type=int,
        default=500,
        help="Número máximo de iteraciones (default: 500)",
    )

    args = parser.parse_args()

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"logs/training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        ],
    )

    logger.info("=" * 100)
    logger.info("🚀 PIPELINE DE ENTRENAMIENTO - MODELO DE PREDICCIÓN NUTRICIONAL")
    logger.info("=" * 100)

    # Cargar variables de entorno
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")

    if not db_url and not args.skip_extraction:
        logger.error("❌ DATABASE_URL no encontrada en .env")
        logger.error("   Usa --skip-extraction si ya tienes el archivo CSV")
        return 1

    # PASO 1: Extracción de Datos
    if not args.skip_extraction:
        logger.info("\n" + "=" * 100)
        logger.info("📊 PASO 1: EXTRACCIÓN DE DATOS")
        logger.info("=" * 100)

        try:
            extractor = NutritionalStatusDataExtractor(db_url)

            df = extractor.extract_training_data(
                min_measurements=args.min_measurements,
                lookback_months=args.lookback_months,
                include_synthetic=args.include_synthetic,
            )

            if df.empty:
                logger.error("❌ No se pudieron extraer datos")
                return 1

            # Guardar dataset
            Path(args.data_file).parent.mkdir(parents=True, exist_ok=True)
            extractor.save_dataset(df, args.data_file)

            logger.info(f"✅ Datos extraídos y guardados: {len(df)} registros")

        except Exception as e:
            logger.error(f"❌ Error en extracción de datos: {e}", exc_info=True)
            return 1
    else:
        logger.info(f"⏭️  Saltando extracción, usando archivo: {args.data_file}")

        if not Path(args.data_file).exists():
            logger.error(f"❌ Archivo no encontrado: {args.data_file}")
            return 1

    # PASO 2: Entrenamiento
    logger.info("\n" + "=" * 100)
    logger.info("🚀 PASO 2: ENTRENAMIENTO DEL MODELO")
    logger.info("=" * 100)

    try:
        import pandas as pd

        # Cargar datos
        logger.info(f"📂 Cargando datos desde: {args.data_file}")
        df = pd.read_csv(args.data_file)
        logger.info(f"✅ Datos cargados: {len(df)} registros")

        # Inicializar entrenador
        trainer = NutritionalPredictorTrainer()

        # Preparar datos
        train_data, val_data, X_val, y_val = trainer.prepare_data(df, args.validation_split)

        # Entrenar
        model = trainer.train(train_data, val_data, args.num_boost_round)

        # Evaluar
        metrics = trainer.evaluate(X_val, y_val)

        # Guardar modelo
        if args.output_model is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output_model = f"models/nutritional_predictor_{timestamp}.pkl"

        Path(args.output_model).parent.mkdir(parents=True, exist_ok=True)
        trainer.save_model(args.output_model, metrics)

        logger.info("✅ Entrenamiento completado exitosamente")

    except Exception as e:
        logger.error(f"❌ Error en entrenamiento: {e}", exc_info=True)
        return 1

    # PASO 3: Validación
    logger.info("\n" + "=" * 100)
    logger.info("✅ PASO 3: VALIDACIÓN DEL MODELO")
    logger.info("=" * 100)

    try:
        from src.domain.models.nutritional_predictor import NutritionalPredictor

        # Cargar modelo
        predictor = NutritionalPredictor(args.output_model)

        if not predictor.is_loaded:
            logger.error("❌ No se pudo cargar el modelo para validación")
            return 1

        # Mostrar información del modelo
        info = predictor.get_model_info()
        logger.info("✅ Modelo cargado correctamente")
        logger.info(f"   Features: {info['num_features']}")
        logger.info(f"   Clases: {info['num_classes']}")
        logger.info(f"   Accuracy: {info['metrics']['accuracy']:.4f}")

        # Hacer predicción de prueba
        features_test = {
            "age_months": 120,
            "sex_numeric": 1,
            "BMI": 16.5,
            "weight_kg": 35.0,
            "height_cm": 145.0,
            "bmi_velocity": -0.1,
            "weight_velocity": 0.3,
            "height_velocity": 0.5,
            "adherence_score": 65.0,
            "allergy_count": 2,
            "altitude_m": 2400,
        }

        prediction = predictor.predict_from_features(features_test)
        logger.info("\n📊 Predicción de prueba:")
        logger.info(f"   Clasificación: {prediction['clasificacion']}")
        logger.info(f"   Probabilidad: {prediction['probabilidad']:.2%}")
        logger.info(f"   Score de Riesgo: {prediction['score_riesgo']:.2%}")

        logger.info("✅ Validación completada")

    except Exception as e:
        logger.error(f"❌ Error en validación: {e}", exc_info=True)
        return 1

    # RESUMEN FINAL
    logger.info("\n" + "=" * 100)
    logger.info("🎉 PIPELINE COMPLETADO EXITOSAMENTE")
    logger.info("=" * 100)
    logger.info(f"📊 Dataset: {args.data_file}")
    logger.info(f"🤖 Modelo: {args.output_model}")
    logger.info(f"📈 Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"📈 F1-Score (macro): {metrics['f1_macro']:.4f}")
    logger.info("\n🚀 Próximos pasos:")
    logger.info("   1. Copiar modelo a producción: models/nutritional_predictor_latest.pkl")
    logger.info("   2. Actualizar endpoint de predicción en backend")
    logger.info("   3. Probar con datos reales")
    logger.info("=" * 100)

    return 0


if __name__ == "__main__":
    # Crear directorios necesarios
    Path("data").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

    sys.exit(main())
