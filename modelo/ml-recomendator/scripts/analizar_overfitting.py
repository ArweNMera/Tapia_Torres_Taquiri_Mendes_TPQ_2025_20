"""
Script para analizar el overfitting del modelo.
Identifica problemas de data leakage y falta de variabilidad.
"""

import sys
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def main():
    print("\n" + "=" * 60)
    print("🔍 ANÁLISIS DE OVERFITTING")
    print("=" * 60)

    # Cargar datos
    data_path = BASE_DIR / "data/raw/surveys/datos_historicos.csv"
    df = pd.read_csv(data_path)

    print(f"\n📊 Total registros: {len(df)}")
    print(f"📊 Total features: {len(df.columns)}")

    # 1. Verificar correlación de BAZ con label
    print("\n" + "=" * 60)
    print("⚠️  PROBLEMA 1: DATA LEAKAGE")
    print("=" * 60)

    correlation = df["baz"].corr(df["label_status"])
    print(f"\n📈 Correlación BAZ vs Label: {correlation:.4f}")

    if abs(correlation) > 0.95:
        print("❌ CRÍTICO: BAZ tiene correlación muy alta con el label")
        print("   El modelo está 'haciendo trampa' usando BAZ directamente")
        print("   Solución: Remover BAZ de los features de entrenamiento")

    # 2. Verificar variabilidad de features
    print("\n" + "=" * 60)
    print("⚠️  PROBLEMA 2: FALTA DE VARIABILIDAD")
    print("=" * 60)

    features_to_check = [
        "bmi_velocity",
        "weight_velocity",
        "height_velocity",
        "allergy_count",
        "adherence_score",
        "symptom_frequency",
        "dietary_diversity_score",
        "altitude_m",
    ]

    print("\n📊 Variabilidad de features:")
    for feature in features_to_check:
        if feature in df.columns:
            unique_values = df[feature].nunique()
            std = df[feature].std()
            mean = df[feature].mean()
            zeros = (df[feature] == 0).sum()

            print(f"\n{feature}:")
            print(f"  Valores únicos: {unique_values}")
            print(f"  Media: {mean:.2f}, Std: {std:.2f}")
            print(f"  Ceros: {zeros} ({zeros/len(df)*100:.1f}%)")

            if unique_values <= 3:
                print("  ❌ MUY POCA VARIABILIDAD")
            elif std < 0.1:
                print("  ⚠️  Desviación estándar muy baja")

    # 3. Verificar separación de clases
    print("\n" + "=" * 60)
    print("⚠️  PROBLEMA 3: SEPARACIÓN PERFECTA DE CLASES")
    print("=" * 60)

    print("\n📊 Rangos de BAZ por clase:")
    for label in sorted(df["label_status"].unique()):
        label_data = df[df["label_status"] == label]
        baz_min = label_data["baz"].min()
        baz_max = label_data["baz"].max()
        classification = label_data["classification"].iloc[0]

        print(f"\n{label} ({classification}):")
        print(f"  BAZ: [{baz_min:.2f}, {baz_max:.2f}]")

        # Verificar si hay overlap con otras clases
        overlap = False
        for other_label in sorted(df["label_status"].unique()):
            if other_label != label:
                other_data = df[df["label_status"] == other_label]
                other_min = other_data["baz"].min()
                other_max = other_data["baz"].max()

                if baz_min <= other_max and baz_max >= other_min:
                    overlap = True
                    break

        if not overlap:
            print("  ❌ NO HAY OVERLAP con otras clases")

    # 4. Recomendaciones
    print("\n" + "=" * 60)
    print("💡 RECOMENDACIONES")
    print("=" * 60)

    print("\n1. ❌ REMOVER BAZ de los features de entrenamiento")
    print("   - BAZ es prácticamente la etiqueta")
    print("   - El modelo debe predecir basándose en otros features")

    print("\n2. ✅ AGREGAR VARIABILIDAD REALISTA a los features")
    print("   - bmi_velocity: ±0.5 kg/m²/mes")
    print("   - weight_velocity: ±0.3 kg/mes")
    print("   - adherence_score: 40-95 (no siempre 75)")
    print("   - symptom_frequency: 0-10 (no siempre 0)")
    print("   - dietary_diversity_score: 30-90 (no siempre 60)")

    print("\n3. ✅ AGREGAR RUIDO a los datos")
    print("   - Pequeñas variaciones en BMI (±0.1)")
    print("   - Variaciones en edad (±1 mes)")

    print("\n4. ✅ USAR CROSS-VALIDATION")
    print("   - 5-fold o 10-fold CV")
    print("   - Evaluar accuracy promedio, no solo en un split")

    print("\n5. ✅ ACCURACY OBJETIVO: 85-95%")
    print("   - 100% = overfitting")
    print("   - 85-95% = buen balance")
    print("   - <80% = underfitting")

    print("\n" + "=" * 60)
    print("📝 SIGUIENTE PASO")
    print("=" * 60)
    print("\nEjecutar: python3 scripts/agregar_variabilidad.py")
    print("Esto agregará variabilidad realista a los datos")
    print("=" * 60)


if __name__ == "__main__":
    main()
