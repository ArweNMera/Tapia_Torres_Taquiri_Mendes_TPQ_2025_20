"""
Ejemplo completo de uso del sistema ML de evaluación nutricional.
"""

import sys
from pathlib import Path

import pandas as pd

# Agregar src al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.features import DataValidator, FeatureEngineer, WHOCalculator
from src.models import EnsembleNutritionClassifier


def ejemplo_prediccion_simple():
    """Ejemplo 1: Predicción simple con datos mínimos."""

    print("\n" + "=" * 60)
    print("EJEMPLO 1: Predicción Simple")
    print("=" * 60)

    # Datos de un niño
    data = pd.DataFrame(
        {
            "age_months": [36],
            "sex": ["M"],
            "weight_kg": [13.5],
            "height_cm": [92.0],
        }
    )

    # Calcular BAZ con OMS
    who_dir = BASE_DIR / "data/raw/who"
    who_calc = WHOCalculator(who_dir)
    data = who_calc.process_dataframe(data)

    print("\n📊 Datos procesados:")
    print(f"   BMI: {data['BMI'].iloc[0]:.2f}")
    print(f"   BAZ (z-score): {data['baz'].iloc[0]:.2f}")
    print(f"   Clasificación OMS: {data['classification'].iloc[0]}")

    # Agregar features por defecto
    engineer = FeatureEngineer()
    data = engineer.create_features(data)

    # Cargar modelo
    model_path = BASE_DIR / "models/ensemble_model.pkl"
    if not model_path.exists():
        print(f"\n⚠️  Modelo no encontrado en: {model_path}")
        print("   Entrena el modelo primero con: python src/pipeline/train_model.py")
        return

    model = EnsembleNutritionClassifier()
    model.load(model_path)

    # Seleccionar features
    features = engineer.select_features(data)

    # Predecir
    result = model.predict_with_metadata(features)

    print("\n🎯 Predicción del Modelo:")
    pred = result["predictions"][0]
    print(f"   Clasificación: {pred['label']}")
    print(f"   Probabilidad: {pred['probability']:.2%}")
    print(f"   Score de riesgo: {pred['risk_score']:.3f}")
    print("\n   Probabilidades por clase:")
    for clase, prob in pred["probabilities"].items():
        print(f"      {clase}: {prob:.2%}")


def ejemplo_con_features_completos():
    """Ejemplo 2: Predicción con features completos."""

    print("\n" + "=" * 60)
    print("EJEMPLO 2: Predicción con Features Completos")
    print("=" * 60)

    # Datos completos de un niño
    data = pd.DataFrame(
        {
            # Básicos
            "age_months": [48],
            "sex": ["F"],
            "weight_kg": [15.2],
            "height_cm": [98.5],
            # Temporales
            "bmi_velocity": [0.3],
            "weight_velocity": [0.5],
            "height_velocity": [1.2],
            "baz_trend": [0.2],
            "measurements_count": [5],
            # Alergias
            "allergy_count": [2],
            "allergy_severity_max": [2],
            "food_allergy_count": [1],
            # Adherencia
            "adherence_score": [82.0],
            "adherence_consistency": [75.0],
            "menu_completion_rate": [88.0],
            # Síntomas
            "symptom_frequency": [1],
            "symptom_severity_avg": [1.5],
            "has_recent_symptoms": [0],
            # Nutricionales
            "dietary_diversity_score": [72.0],
            "menu_kcal_avg": [1400],
            "protein_intake_score": [68.0],
            # Contextuales
            "altitude_m": [2400],
        }
    )

    # Calcular BAZ
    who_dir = BASE_DIR / "data/raw/who"
    who_calc = WHOCalculator(who_dir)
    data = who_calc.process_dataframe(data)

    # Feature engineering
    engineer = FeatureEngineer()
    data = engineer.create_features(data)

    print("\n📊 Datos del niño:")
    print(f"   Edad: {data['age_months'].iloc[0]} meses ({data['age_months'].iloc[0]/12:.1f} años)")
    print(f"   Sexo: {'Femenino' if data['sex'].iloc[0] == 'F' else 'Masculino'}")
    print(f"   BMI: {data['BMI'].iloc[0]:.2f}")
    print(f"   BAZ: {data['baz'].iloc[0]:.2f}")
    print(
        f"   Tendencia BAZ: {'Mejorando' if data['baz_trend'].iloc[0] > 0 else 'Estable/Empeorando'}"
    )
    print(f"   Adherencia: {data['adherence_score'].iloc[0]:.0f}%")
    print(f"   Alergias: {data['allergy_count'].iloc[0]}")
    print(f"   Síntomas (30d): {data['symptom_frequency'].iloc[0]}")

    # Cargar modelo
    model_path = BASE_DIR / "models/ensemble_model.pkl"
    if not model_path.exists():
        print("\n⚠️  Modelo no encontrado")
        return

    model = EnsembleNutritionClassifier()
    model.load(model_path)

    # Predecir con desglose
    features = engineer.select_features(data)
    result = model.predict_with_breakdown(features)

    print("\n🎯 Predicción del Ensemble:")
    ensemble = result["predictions"][0]["ensemble"]
    print(f"   Clasificación: {ensemble['label']}")
    print(f"   Probabilidades: {[f'{p:.2%}' for p in ensemble['probabilities']]}")

    print("\n🌲 Random Forest:")
    rf = result["predictions"][0]["rf"]
    print(f"   Clasificación: {rf['label']}")

    print("\n🧠 Red Neuronal:")
    nn = result["predictions"][0]["nn"]
    print(f"   Clasificación: {nn['label']}")

    print(
        f"\n🤝 Acuerdo entre modelos: {'✅ Sí' if result['predictions'][0]['agreement'] else '❌ No'}"
    )


def ejemplo_validacion_datos():
    """Ejemplo 3: Validación de datos."""

    print("\n" + "=" * 60)
    print("EJEMPLO 3: Validación de Datos")
    print("=" * 60)

    # Datos con algunos problemas
    data = pd.DataFrame(
        {
            "age_months": [36, 240, -5],  # 240 y -5 son inválidos
            "sex": ["M", "F", "X"],  # X es inválido
            "weight_kg": [13.5, 15.2, 0],  # 0 es inválido
            "height_cm": [92.0, 98.5, 300],  # 300 es inválido
        }
    )

    validator = DataValidator()

    # Validar datos antropométricos
    result = validator.validate_anthropometric_data(data)

    print("\n🔍 Resultado de validación:")
    print(f"   Válido: {'✅ Sí' if result['valid'] else '❌ No'}")
    print(f"   Filas totales: {result['n_rows']}")
    print(f"   Filas completas: {result['n_complete']}")

    if result["issues"]:
        print("\n❌ Problemas encontrados:")
        for issue in result["issues"]:
            print(f"   - {issue}")

    if result["warnings"]:
        print("\n⚠️  Advertencias:")
        for warning in result["warnings"]:
            print(f"   - {warning}")

    # Análisis de calidad
    quality = validator.check_data_quality(data)

    print("\n📊 Calidad de datos:")
    print(f"   Filas: {quality['n_rows']}")
    print(f"   Columnas: {quality['n_cols']}")
    print(f"   % Nulos: {quality['null_percentage']:.2f}%")
    print(f"   Duplicados: {quality['n_duplicates']}")

    # Detectar outliers
    outliers = validator.detect_outliers(data, method="iqr")

    if outliers["outliers_by_column"]:
        print("\n🔍 Outliers detectados:")
        for col, info in outliers["outliers_by_column"].items():
            print(f"   {col}: {info['n_outliers']} outliers ({info['percentage']:.1f}%)")


def ejemplo_feature_importance():
    """Ejemplo 4: Análisis de feature importance."""

    print("\n" + "=" * 60)
    print("EJEMPLO 4: Feature Importance")
    print("=" * 60)

    # Cargar modelo
    model_path = BASE_DIR / "models/ensemble_model.pkl"
    if not model_path.exists():
        print("\n⚠️  Modelo no encontrado")
        return

    model = EnsembleNutritionClassifier()
    model.load(model_path)

    # Obtener feature importance del Random Forest
    importance = model.get_feature_importance()

    if importance:
        # Ordenar por importancia
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)

        print("\n📊 Top 10 Features Más Importantes:")
        for i, (feature, imp) in enumerate(sorted_features[:10], 1):
            bar = "█" * int(imp * 50)
            print(f"   {i:2d}. {feature:30s} {bar} {imp:.4f}")
    else:
        print("\n⚠️  Feature importance no disponible")


def main():
    """Ejecuta todos los ejemplos."""

    print("\n" + "=" * 60)
    print("🎯 EJEMPLOS DE USO - SISTEMA ML NUTRICIONAL")
    print("=" * 60)

    try:
        ejemplo_prediccion_simple()
    except Exception as e:
        print(f"\n❌ Error en ejemplo 1: {e}")

    try:
        ejemplo_con_features_completos()
    except Exception as e:
        print(f"\n❌ Error en ejemplo 2: {e}")

    try:
        ejemplo_validacion_datos()
    except Exception as e:
        print(f"\n❌ Error en ejemplo 3: {e}")

    try:
        ejemplo_feature_importance()
    except Exception as e:
        print(f"\n❌ Error en ejemplo 4: {e}")

    print("\n" + "=" * 60)
    print("✅ Ejemplos completados")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
