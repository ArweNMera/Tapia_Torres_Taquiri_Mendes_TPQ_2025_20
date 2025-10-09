#!/usr/bin/env python3
"""
Genera dataset de entrenamiento basado en tablas OMS.
Crea ejemplos sintéticos con clasificación correcta según BAZ.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
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

def generar_datos_oms(n_samples=5000):
    """
    Genera dataset sintético basado en tablas OMS.
    
    Args:
        n_samples: Número de muestras a generar
    
    Returns:
        DataFrame con datos de entrenamiento
    """
    print("=" * 80)
    print("GENERANDO DATASET DESDE TABLAS OMS")
    print("=" * 80)
    print()
    
    # Conectar a BD y obtener tablas OMS
    db = DatabaseConnector.from_env()
    db.connect()
    
    query = """
    SELECT sexo, edad_meses, L, M, S
    FROM oms_bmi_lms
    WHERE version = 'OMS_2007'
    ORDER BY sexo, edad_meses
    """
    
    lms_data = db.execute_query(query)
    db.disconnect()
    
    print(f"✅ Tablas OMS cargadas: {len(lms_data)} registros")
    print(f"   Rango edad: {lms_data['edad_meses'].min()} - {lms_data['edad_meses'].max()} meses")
    print()
    
    # Generar muestras
    datos = []
    
    # Distribución de categorías (balanceada)
    categorias_target = {
        0: int(n_samples * 0.10),  # DESNUTRICION_SEVERA
        1: int(n_samples * 0.15),  # DESNUTRICION_MODERADA
        2: int(n_samples * 0.15),  # RIESGO_DESNUTRICION
        3: int(n_samples * 0.30),  # NORMAL
        4: int(n_samples * 0.15),  # RIESGO_SOBREPESO
        5: int(n_samples * 0.10),  # SOBREPESO
        6: int(n_samples * 0.05),  # OBESIDAD
    }
    
    print("📊 Generando muestras por categoría:")
    for cat, count in categorias_target.items():
        _, label = clasificar_por_baz(cat - 3)  # Aproximado
        print(f"   {label}: {count} muestras")
    print()
    
    # Generar muestras para cada categoría
    for categoria, n_muestras in categorias_target.items():
        # Rangos de BAZ para cada categoría
        if categoria == 0:  # DESNUTRICION_SEVERA
            baz_min, baz_max = -5.0, -3.0
        elif categoria == 1:  # DESNUTRICION_MODERADA
            baz_min, baz_max = -3.0, -2.0
        elif categoria == 2:  # RIESGO_DESNUTRICION
            baz_min, baz_max = -2.0, -1.0
        elif categoria == 3:  # NORMAL
            baz_min, baz_max = -1.0, 1.0
        elif categoria == 4:  # RIESGO_SOBREPESO
            baz_min, baz_max = 1.0, 2.0
        elif categoria == 5:  # SOBREPESO
            baz_min, baz_max = 2.0, 3.0
        else:  # OBESIDAD
            baz_min, baz_max = 3.0, 5.0
        
        for _ in range(n_muestras):
            # Seleccionar edad y sexo aleatorio
            row = lms_data.sample(1).iloc[0]
            edad_meses = int(row['edad_meses'])
            sexo = row['sexo']
            L, M, S = float(row['L']), float(row['M']), float(row['S'])
            
            # Generar BAZ objetivo en el rango de la categoría
            baz_target = np.random.uniform(baz_min, baz_max)
            
            # Calcular IMC que produce ese BAZ
            # Invertir fórmula de BAZ
            try:
                if L == 0:
                    imc = M * np.exp(baz_target * S)
                else:
                    # Asegurar que el valor dentro del paréntesis sea positivo
                    valor_interno = baz_target * L * S + 1
                    if valor_interno <= 0:
                        # Si es negativo, ajustar BAZ para que sea válido
                        baz_target = (0.01 - 1) / (L * S)
                        valor_interno = 0.01
                    imc = M * (valor_interno ** (1 / L))
                
                # Validar que IMC sea realista
                if imc < 10 or imc > 40 or np.isnan(imc) or np.isinf(imc):
                    continue  # Saltar esta muestra
                    
            except (ValueError, ZeroDivisionError, OverflowError):
                continue  # Saltar si hay error matemático
            
            # Calcular peso y talla realistas
            # Usar percentiles de talla para la edad
            if edad_meses < 24:
                talla_cm = 50 + (edad_meses * 1.5) + np.random.normal(0, 2)
            elif edad_meses < 60:
                talla_cm = 75 + ((edad_meses - 24) * 0.8) + np.random.normal(0, 3)
            else:
                talla_cm = 100 + ((edad_meses - 60) * 0.5) + np.random.normal(0, 4)
            
            talla_cm = max(45, min(200, talla_cm))  # Límites realistas
            peso_kg = imc * (talla_cm / 100) ** 2
            
            # Verificar que el BAZ calculado coincide
            baz_calculado = calcular_baz(imc, L, M, S)
            
            # Validar que BAZ sea un número real
            if np.isnan(baz_calculado) or np.isinf(baz_calculado) or np.iscomplex(baz_calculado):
                continue  # Saltar esta muestra
            
            # Convertir a float si es complejo (tomar solo parte real)
            if isinstance(baz_calculado, complex):
                baz_calculado = baz_calculado.real
            
            cat_calculada, label = clasificar_por_baz(baz_calculado)
            
            # Solo agregar si la categoría coincide
            if cat_calculada == categoria:
                # Generar features adicionales con variabilidad
                datos.append({
                    'age_months': edad_meses,
                    'sex': sexo,  # M o F
                    'sex_numeric': 1 if sexo == 'M' else 0,
                    'BMI': round(imc, 2),
                    'weight_kg': round(peso_kg, 2),  # Nombre correcto
                    'height_cm': round(talla_cm, 1),  # Nombre correcto
                    'bmi_velocity': round(np.random.normal(0, 0.2), 2),
                    'weight_velocity': round(np.random.normal(0, 0.2), 2),
                    'height_velocity': round(np.random.uniform(0.3, 0.7), 2),
                    'allergy_count': np.random.choice([0, 1, 2, 3], p=[0.7, 0.2, 0.08, 0.02]),
                    'adherence_score': round(np.random.uniform(40, 95), 1),
                    'symptom_frequency': np.random.choice(range(11), p=[0.4] + [0.06]*10),
                    'dietary_diversity_score': round(np.random.uniform(30, 90), 1),
                    'altitude_m': np.random.choice([0, 500, 1000, 2500, 3500], p=[0.4, 0.2, 0.2, 0.15, 0.05]),
                    'baz': round(baz_calculado, 2),
                    'label': categoria,
                    'label_name': label,
                    'label_status': categoria  # Para el script de entrenamiento
                })
    
    df = pd.DataFrame(datos)
    
    print("=" * 80)
    print("DATASET GENERADO")
    print("=" * 80)
    print(f"Total muestras: {len(df)}")
    print()
    print("Distribución por categoría:")
    print(df['label_name'].value_counts().sort_index())
    print()
    print("Estadísticas:")
    print(df[['age_months', 'BMI', 'baz']].describe())
    print()
    
    # Guardar
    output_path = Path("data/raw/surveys/datos_oms_sinteticos.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✅ Dataset guardado en: {output_path}")
    print()
    
    return df

def extraer_datos_reales():
    """
    Extrae datos reales de niños desde la BD.
    """
    print("=" * 80)
    print("EXTRAYENDO DATOS REALES DE LA BD")
    print("=" * 80)
    print()
    
    db = DatabaseConnector.from_env()
    db.connect()
    
    # Query con tus tablas reales (MySQL)
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
    db.disconnect()
    
    if df_real.empty:
        print("⚠️  No se encontraron datos reales en la BD")
        return pd.DataFrame()
    
    print(f"✅ Datos reales extraídos: {len(df_real)} registros")
    print(f"   Niños únicos: {df_real['nin_id'].nunique()}")
    print()
    
    # Rellenar features faltantes con valores por defecto
    print("📊 Rellenando features faltantes...")
    
    # Rellenar con valores aleatorios donde falten
    mask = df_real['bmi_velocity'].isna()
    df_real.loc[mask, 'bmi_velocity'] = np.random.normal(0, 0.2, mask.sum())
    
    mask = df_real['weight_velocity'].isna()
    df_real.loc[mask, 'weight_velocity'] = np.random.normal(0, 0.2, mask.sum())
    
    mask = df_real['height_velocity'].isna()
    df_real.loc[mask, 'height_velocity'] = np.random.uniform(0.3, 0.7, mask.sum())
    
    # Rellenar con valores fijos
    df_real['allergy_count'] = df_real['allergy_count'].fillna(0).astype(int)
    df_real['adherence_score'] = df_real['adherence_score'].fillna(75.0)
    df_real['symptom_frequency'] = df_real['symptom_frequency'].fillna(0).astype(int)
    df_real['dietary_diversity_score'] = df_real['dietary_diversity_score'].fillna(60.0)
    
    print()
    
    # Calcular BAZ y clasificación para TODOS
    print("📊 Calculando clasificaciones con tablas OMS...")
    
    # Cargar tablas OMS
    db.connect()
    lms_query = """
    SELECT sexo, edad_meses, L, M, S
    FROM oms_bmi_lms
    WHERE version = 'OMS_2007'
    """
    lms_data = db.execute_query(lms_query)
    db.disconnect()
    
    # Calcular BAZ y clasificación para todos los registros
    df_real['baz'] = None
    df_real['label'] = None
    df_real['label_name'] = None
    
    for idx, row in df_real.iterrows():
        # Buscar LMS para esta edad y sexo
        sexo = row['nin_sexo']
        edad = int(row['age_months'])
        
        lms_row = lms_data[
            (lms_data['sexo'] == sexo) & 
            (lms_data['edad_meses'] == edad)
        ]
        
        if not lms_row.empty:
            L = float(lms_row.iloc[0]['L'])
            M = float(lms_row.iloc[0]['M'])
            S = float(lms_row.iloc[0]['S'])
            
            baz = calcular_baz(row['BMI'], L, M, S)
            
            # Validar que BAZ sea real
            if not (np.isnan(baz) or np.isinf(baz) or np.iscomplex(baz)):
                if isinstance(baz, complex):
                    baz = baz.real
                
                label_num, label_name = clasificar_por_baz(baz)
                
                df_real.at[idx, 'baz'] = baz
                df_real.at[idx, 'label_name'] = label_name
                df_real.at[idx, 'label'] = label_num
    
    # Ya no necesitamos mapear porque lo hicimos en el loop
    
    # Eliminar registros sin clasificación
    df_real = df_real.dropna(subset=['label', 'baz'])
    
    print(f"✅ Registros con clasificación: {len(df_real)}")
    print()
    print("Distribución de datos reales:")
    print(df_real['label_name'].value_counts().sort_index())
    print()
    
    # Renombrar columnas para que coincidan con el formato esperado
    df_real = df_real.rename(columns={
        'nin_sexo': 'sex',
        'peso_kg': 'weight_kg',
        'talla_cm': 'height_cm'
    })
    
    # Agregar label_status (igual a label)
    df_real['label_status'] = df_real['label']
    
    # Seleccionar solo las columnas necesarias
    columnas = [
        'age_months', 'sex', 'sex_numeric', 'BMI', 'weight_kg', 'height_cm',
        'bmi_velocity', 'weight_velocity', 'height_velocity',
        'allergy_count', 'adherence_score', 'symptom_frequency',
        'dietary_diversity_score', 'altitude_m',
        'baz', 'label', 'label_name', 'label_status'
    ]
    
    df_real = df_real[columnas]
    
    return df_real


def combinar_datos(df_sintetico, df_real):
    """
    Combina datos sintéticos y reales.
    """
    print("=" * 80)
    print("COMBINANDO DATOS SINTÉTICOS Y REALES")
    print("=" * 80)
    print()
    
    print(f"📊 Datos sintéticos: {len(df_sintetico)} registros")
    print(f"📊 Datos reales: {len(df_real)} registros")
    print()
    
    # Combinar
    df_combined = pd.concat([df_sintetico, df_real], ignore_index=True)
    
    # Mezclar aleatoriamente
    df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"✅ Dataset combinado: {len(df_combined)} registros")
    print()
    print("Distribución final:")
    print(df_combined['label_name'].value_counts().sort_index())
    print()
    
    # Guardar
    output_path = Path("data/raw/surveys/datos_completos_oms_reales.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_combined.to_csv(output_path, index=False)
    
    print(f"✅ Dataset combinado guardado en: {output_path}")
    print()
    
    return df_combined


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generar dataset desde tablas OMS y datos reales")
    parser.add_argument("--samples", type=int, default=5000, help="Número de muestras sintéticas a generar")
    parser.add_argument("--solo-reales", action="store_true", help="Solo extraer datos reales (sin sintéticos)")
    args = parser.parse_args()
    
    if args.solo_reales:
        # Solo extraer datos reales
        df_real = extraer_datos_reales()
        if not df_real.empty:
            output_path = Path("data/raw/surveys/datos_reales.csv")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df_real.to_csv(output_path, index=False)
            print(f"✅ Datos reales guardados en: {output_path}")
    else:
        # Generar sintéticos y combinar con reales
        df_sintetico = generar_datos_oms(n_samples=args.samples)
        df_real = extraer_datos_reales()
        
        if not df_real.empty:
            df_combined = combinar_datos(df_sintetico, df_real)
        else:
            print("⚠️  No hay datos reales, usando solo sintéticos")
            df_combined = df_sintetico
