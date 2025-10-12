"""
Script para limpiar duplicados y analizar el impacto en el modelo.
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent


def main():
    # Cargar datos
    data_path = BASE_DIR / "data/raw/surveys/datos_historicos.csv"
    df = pd.read_csv(data_path)

    print("📊 ANÁLISIS DE DUPLICADOS")
    print("=" * 60)
    print(f"Total registros: {len(df)}")
    print(f"Duplicados: {df.duplicated().sum()}")

    # Identificar columnas clave para duplicados
    # Excluir columnas que pueden variar entre mediciones del mismo niño
    key_cols = [
        "nin_id",
        "age_months",
        "sex_numeric",
        "BMI",
        "baz",
        "bmi_velocity",
        "weight_velocity",
        "height_velocity",
        "allergy_count",
        "adherence_score",
        "symptom_frequency",
        "dietary_diversity_score",
        "altitude_m",
        "label_status",
    ]

    # Verificar qué columnas existen
    available_key_cols = [col for col in key_cols if col in df.columns]

    print("\n🔍 Buscando duplicados en columnas clave...")
    duplicates_mask = df.duplicated(subset=available_key_cols, keep="first")
    n_duplicates = duplicates_mask.sum()

    print(f"Duplicados encontrados: {n_duplicates}")

    if n_duplicates > 0:
        print("\n📋 Ejemplos de duplicados:")
        dup_examples = (
            df[df.duplicated(subset=available_key_cols, keep=False)].sort_values("nin_id").head(10)
        )
        print(dup_examples[["nin_id", "age_months", "BMI", "baz", "label_status"]])

        # Eliminar duplicados
        df_clean = df.drop_duplicates(subset=available_key_cols, keep="first")

        print("\n✅ Datos limpios:")
        print(f"   Registros originales: {len(df)}")
        print(f"   Registros únicos: {len(df_clean)}")
        print(f"   Eliminados: {len(df) - len(df_clean)}")

        # Distribución de clases después de limpiar
        print("\n📊 Distribución de clases (limpio):")
        print(df_clean["label_status"].value_counts().sort_index())
        print("\n📊 Porcentaje por clase:")
        print((df_clean["label_status"].value_counts(normalize=True) * 100).round(2).sort_index())

        # Guardar datos limpios
        output_path = BASE_DIR / "data/raw/surveys/datos_historicos_clean.csv"
        df_clean.to_csv(output_path, index=False)
        print(f"\n✅ Datos limpios guardados en: {output_path}")

        # También crear backup del original
        backup_path = BASE_DIR / "data/raw/surveys/datos_historicos_backup.csv"
        if not backup_path.exists():
            df.to_csv(backup_path, index=False)
            print(f"✅ Backup creado en: {backup_path}")
    else:
        print("\n✅ No se encontraron duplicados")


if __name__ == "__main__":
    main()
