"""
Script para verificar que las clasificaciones usan las 7 categorías OMS.
"""

import sys
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.utils import DatabaseConnector
from src.features import WHOCalculator

def main():
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO CLASIFICACIONES OMS (7 CATEGORÍAS)")
    print("=" * 60)
    
    # Conectar a BD
    db = DatabaseConnector.from_env()
    db.connect()
    
    try:
        # Obtener datos antropométricos (solo el último registro de cada niño)
        query = """
        SELECT 
            a.ant_id,
            a.nin_id,
            a.ant_peso_kg,
            a.ant_talla_cm,
            a.ant_z_imc as baz,
            n.nin_sexo,
            TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as edad_meses
        FROM antropometrias a
        JOIN ninos n ON a.nin_id = n.nin_id
        WHERE a.ant_z_imc IS NOT NULL
        AND a.ant_id IN (
            SELECT MAX(a2.ant_id)
            FROM antropometrias a2
            WHERE a2.ant_z_imc IS NOT NULL
            GROUP BY a2.nin_id
        )
        ORDER BY a.ant_fecha DESC
        """
        
        df = pd.read_sql(query, db.engine)
        print(f"\n📊 Total registros: {len(df)}")
        
        # Inicializar calculadora WHO
        who_calc = WHOCalculator(db_connector=db)
        
        # Clasificar según BAZ
        df['classification'] = df['baz'].apply(who_calc.classify_nutritional_status)
        df['label_status'] = df['baz'].apply(who_calc.classify_to_label)
        
        # Mostrar distribución
        print("\n📊 Distribución de clasificación:")
        print(df['classification'].value_counts().sort_index())
        
        print("\n📊 Distribución de labels:")
        print(df['label_status'].value_counts().sort_index())
        
        # Mostrar rangos de BAZ por categoría
        print("\n📊 Rangos de BAZ por categoría:")
        for cat in sorted(df['classification'].unique()):
            cat_data = df[df['classification'] == cat]
            print(f"\n{cat}:")
            print(f"   Cantidad: {len(cat_data)}")
            print(f"   BAZ promedio: {cat_data['baz'].mean():.2f}")
            print(f"   BAZ rango: [{cat_data['baz'].min():.2f}, {cat_data['baz'].max():.2f}]")
        
        # Verificar que tenemos las 7 categorías esperadas
        expected_categories = [
            'DESNUTRICION_SEVERA',
            'DESNUTRICION_MODERADA',
            'RIESGO_DESNUTRICION',
            'NORMAL',
            'RIESGO_SOBREPESO',
            'SOBREPESO',
            'OBESIDAD'
        ]
        
        actual_categories = set(df['classification'].unique())
        expected_set = set(expected_categories)
        
        print("\n" + "=" * 60)
        if actual_categories == expected_set:
            print("✅ TODAS LAS 7 CATEGORÍAS OMS ESTÁN PRESENTES")
        else:
            missing = expected_set - actual_categories
            extra = actual_categories - expected_set
            if missing:
                print(f"⚠️  Categorías faltantes: {missing}")
            if extra:
                print(f"⚠️  Categorías inesperadas: {extra}")
        print("=" * 60)
        
        # Filtrar para tener exactamente 200 niños balanceados
        categorias_objetivo = {
            'DESNUTRICION_SEVERA': 26,
            'DESNUTRICION_MODERADA': 26,
            'RIESGO_DESNUTRICION': 29,
            'NORMAL': 69,  # Ajustar para tener total de 200
            'RIESGO_SOBREPESO': 20,
            'SOBREPESO': 15,
            'OBESIDAD': 15
        }  # Total: 200
        
        # Filtrar para mantener solo los primeros N de cada categoría
        df_filtered = []
        for cat, cantidad in categorias_objetivo.items():
            cat_data = df[df['classification'] == cat].head(cantidad)
            df_filtered.append(cat_data)
        
        df = pd.concat(df_filtered, ignore_index=True)
        
        print(f"\n📊 Datos filtrados a 200 niños balanceados:")
        print(df['classification'].value_counts().sort_index())
        
        # Guardar datos clasificados
        output_path = BASE_DIR / "data/raw/surveys/datos_historicos.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Calcular BMI si no existe
        df['BMI'] = df['ant_peso_kg'] / (df['ant_talla_cm'] / 100) ** 2
        
        # Renombrar columnas para compatibilidad
        df['age_months'] = df['edad_meses']
        df['weight_kg'] = df['ant_peso_kg']
        df['height_cm'] = df['ant_talla_cm']
        
        # Mapear sexo
        df['sex'] = df['nin_sexo']
        df['sex_numeric'] = df['nin_sexo'].map({'M': 0, 'F': 1})
        
        # Agregar features faltantes con valores por defecto
        default_features = {
            'bmi_velocity': 0.0,
            'weight_velocity': 0.0,
            'height_velocity': 0.0,
            'allergy_count': 0,
            'adherence_score': 75.0,
            'symptom_frequency': 0,
            'dietary_diversity_score': 60.0,
            'altitude_m': 0
        }
        
        for feature, default_value in default_features.items():
            if feature not in df.columns:
                df[feature] = default_value
        
        # Seleccionar columnas para guardar (incluir weight_kg y height_cm para validación)
        output_cols = [
            'nin_id', 'age_months', 'sex', 'sex_numeric', 
            'weight_kg', 'height_cm', 'BMI', 'baz',
            'classification', 'label_status',
            'bmi_velocity', 'weight_velocity', 'height_velocity',
            'allergy_count', 'adherence_score', 'symptom_frequency',
            'dietary_diversity_score', 'altitude_m'
        ]
        
        df_output = df[output_cols]
        df_output.to_csv(output_path, index=False)
        
        print(f"\n💾 Datos guardados en: {output_path}")
        print(f"   Columnas: {list(df_output.columns)}")
        print(f"   Filas: {len(df_output)}")
        
    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
