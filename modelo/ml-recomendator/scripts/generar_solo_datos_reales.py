#!/usr/bin/env python3
"""
Genera dataset SOLO con datos reales de la BD (sin sintéticos).
Útil cuando ya tienes suficientes datos reales.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd

from src.utils import DatabaseConnector


def calcular_baz(imc, L, M, S):
    """Calcula BAZ usando fórmula de Cole (OMS)."""
    if L == 0:
        return np.log(imc / M) / S
    return ((imc / M) ** L - 1) / (L * S)


def clasificar_por_baz(baz):
    """Clasifica según BAZ (7 categorías OMS)."""
    if baz < -3:
        return 0, "DESNUTRICION_SEVERA"
    elif -3 <= baz < -2:
        return 1, "DESNUTRICION_MODERADA"
    elif -2 <= baz < -1:
        return 2, "RIESGO_DESNUTRICION"
    elif -1 <= baz <= 1:
        return 3, "NORMAL"
    elif 1 < baz <= 2:
        return 4, "RIESGO_SOBREPESO"
    elif 2 < baz <= 3:
        return 5, "SOBREPESO"
    else:
        return 6, "OBESIDAD"


def extraer_datos_reales():
    """
    Extrae SOLO datos reales de niños desde la BD MySQL.
    """
    print("=" * 80)
    print("EXTRAYENDO DATOS REALES DE LA BD MYSQL")
    print("=" * 80)
    print()

    db = DatabaseConnector.from_env()
    db.connect()

    # Query para MySQL
    query = """
    SELECT
        n.nin_id,
        n.nin_nombres,
        TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as age_months,
        IF(n.nin_sexo = 'M', 1, 0) as sex_numeric,
        n.nin_sexo,
        a.ant_peso_kg as peso_kg,
        a.ant_talla_cm as talla_cm,
        (a.ant_peso_kg / POWER(a.ant_talla_cm / 100, 2)) as BMI,

        -- Features de la tabla features_ml (si existen)
        f.fml_bmi_velocity as bmi_velocity,
        f.fml_weight_velocity as weight_velocity,
        f.fml_height_velocity as height_velocity,
        f.fml_allergy_count as allergy_count,
        f.fml_adherence_score as adherence_score,
        f.fml_symptom_frequency as symptom_frequency,
        f.fml_dietary_diversity_score as dietary_diversity_score,
        0 as altitude_m,

        -- Clasificación de evaluaciones_nutricionales (si existe)
        e.en_clasificacion as label_name,
        e.en_z_score_imc as baz

    FROM ninos n
    INNER JOIN antropometrias a ON n.nin_id = a.nin_id
    LEFT JOIN features_ml f ON a.ant_id = f.ant_id
    LEFT JOIN evaluaciones_nutricionales e ON a.ant_id = e.ant_id
    WHERE a.ant_peso_kg IS NOT NULL
      AND a.ant_talla_cm IS NOT NULL
      AND a.ant_talla_cm > 0
      AND TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) >= 61
      AND TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) <= 228
    ORDER BY n.nin_id, a.ant_fecha DESC
    """

    df_real = db.execute_query(query)

    if df_real.empty:
        print("❌ No se encontraron datos reales en la BD")
        print("   Verifica que:")
        print("   - La BD esté corriendo")
        print("   - Las tablas existan (ninos, antropometrias)")
        print("   - Haya niños con mediciones")
        db.disconnect()
        return pd.DataFrame()

    print(f"✅ Datos reales extraídos: {len(df_real)} registros")
    print(f"   Niños únicos: {df_real['nin_id'].nunique()}")
    print()

    # Rellenar features faltantes con valores por defecto
    print("📊 Rellenando features faltantes...")

    # Rellenar con valores aleatorios donde falten
    mask = df_real["bmi_velocity"].isna()
    if mask.sum() > 0:
        df_real.loc[mask, "bmi_velocity"] = np.random.normal(0, 0.2, mask.sum())

    mask = df_real["weight_velocity"].isna()
    if mask.sum() > 0:
        df_real.loc[mask, "weight_velocity"] = np.random.normal(0, 0.2, mask.sum())

    mask = df_real["height_velocity"].isna()
    if mask.sum() > 0:
        df_real.loc[mask, "height_velocity"] = np.random.uniform(0.3, 0.7, mask.sum())

    # Rellenar con valores fijos
    df_real["allergy_count"] = df_real["allergy_count"].fillna(0).astype(int)
    df_real["adherence_score"] = df_real["adherence_score"].fillna(75.0)
    df_real["symptom_frequency"] = df_real["symptom_frequency"].fillna(0).astype(int)
    df_real["dietary_diversity_score"] = df_real["dietary_diversity_score"].fillna(60.0)

    print()

    # Calcular BAZ y clasificación para TODOS
    print("📊 Calculando clasificaciones con tablas OMS...")

    # Cargar tablas OMS
    lms_query = """
    SELECT sexo, edad_meses, L, M, S
    FROM oms_bmi_lms
    WHERE version = 'OMS_2007'
    """
    lms_data = db.execute_query(lms_query)
    db.disconnect()

    # Calcular BAZ y clasificación para todos los registros
    df_real["baz"] = None
    df_real["label"] = None
    df_real["label_name"] = None

    for idx, row in df_real.iterrows():
        # Buscar LMS para esta edad y sexo
        sexo = row["nin_sexo"]
        edad = int(row["age_months"])

        lms_row = lms_data[(lms_data["sexo"] == sexo) & (lms_data["edad_meses"] == edad)]

        if not lms_row.empty:
            L = float(lms_row.iloc[0]["L"])
            M = float(lms_row.iloc[0]["M"])
            S = float(lms_row.iloc[0]["S"])

            baz = calcular_baz(row["BMI"], L, M, S)

            # Validar que BAZ sea real
            if not (np.isnan(baz) or np.isinf(baz) or np.iscomplex(baz)):
                if isinstance(baz, complex):
                    baz = baz.real

                label_num, label_name = clasificar_por_baz(baz)

                df_real.at[idx, "baz"] = baz
                df_real.at[idx, "label_name"] = label_name
                df_real.at[idx, "label"] = label_num

    # Eliminar registros sin clasificación
    df_real = df_real.dropna(subset=["label", "baz"])

    print(f"✅ Registros con clasificación: {len(df_real)}")
    print()
    print("Distribución de datos reales:")
    print(df_real["label_name"].value_counts().sort_index())
    print()

    # Renombrar columnas para que coincidan con el formato esperado
    df_real = df_real.rename(
        columns={"nin_sexo": "sex", "peso_kg": "weight_kg", "talla_cm": "height_cm"}
    )

    # Agregar label_status (igual a label)
    df_real["label_status"] = df_real["label"]

    # Seleccionar solo las columnas necesarias
    columnas = [
        "age_months",
        "sex",
        "sex_numeric",
        "BMI",
        "weight_kg",
        "height_cm",
        "bmi_velocity",
        "weight_velocity",
        "height_velocity",
        "allergy_count",
        "adherence_score",
        "symptom_frequency",
        "dietary_diversity_score",
        "altitude_m",
        "baz",
        "label",
        "label_name",
        "label_status",
    ]

    df_real = df_real[columnas]

    # Guardar
    output_path = Path("data/raw/surveys/datos_completos_oms_reales.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_real.to_csv(output_path, index=False)

    print(f"✅ Dataset guardado en: {output_path}")
    print()

    # Estadísticas
    print("=" * 80)
    print("ESTADÍSTICAS DEL DATASET")
    print("=" * 80)
    print()
    print(f"Total registros: {len(df_real)}")
    print(
        f"Niños únicos: {df_real.get('nin_id', pd.Series()).nunique() if 'nin_id' in df_real.columns else 'N/A'}"
    )
    print()
    print("Distribución por categoría:")
    print(df_real["label_name"].value_counts().sort_index())
    print()
    print("Rango de edad:")
    print(f"  Min: {df_real['age_months'].min()} meses ({df_real['age_months'].min()//12} años)")
    print(f"  Max: {df_real['age_months'].max()} meses ({df_real['age_months'].max()//12} años)")
    print(f"  Media: {df_real['age_months'].mean():.1f} meses")
    print()
    print("Estadísticas de BAZ:")
    print(df_real["baz"].describe())
    print()

    return df_real


if __name__ == "__main__":
    print("\n🎯 GENERANDO DATASET SOLO CON DATOS REALES")
    print("   (Sin datos sintéticos)")
    print()

    df = extraer_datos_reales()

    if not df.empty:
        print("=" * 80)
        print("✅ DATASET GENERADO EXITOSAMENTE")
        print("=" * 80)
        print()
        print("📋 Próximos pasos:")
        print("   1. Entrenar modelo: python src/pipeline/train_model.py")
        print("   2. Verificar: python scripts/test_clasificacion.py")
        print("   3. Generar gráficas: ./generar_graficas.sh")
        print()

        # Advertencia si hay pocas muestras
        if len(df) < 100:
            print("⚠️  ADVERTENCIA: Tienes menos de 100 registros")
            print("   El modelo puede no funcionar bien con tan pocos datos")
            print("   Considera:")
            print("   - Agregar más niños a la BD")
            print("   - Usar datos sintéticos: python scripts/generar_datos_desde_oms.py")
            print()
    else:
        print("=" * 80)
        print("❌ NO SE PUDO GENERAR EL DATASET")
        print("=" * 80)
        print()
        print("Verifica:")
        print("  1. La BD MySQL está corriendo")
        print("  2. Las credenciales en .env son correctas")
        print("  3. Las tablas existen (ninos, antropometrias, oms_bmi_lms)")
        print("  4. Hay niños con mediciones en la BD")
        print()
