"""
Script para mejorar el rendimiento del modelo con técnicas avanzadas.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.combine import SMOTETomek
import json

BASE_DIR = Path(__file__).resolve().parent.parent

def main():
    # Cargar datos limpios
    data_path = BASE_DIR / "data/raw/surveys/datos_historicos_clean.csv"
    df = pd.read_csv(data_path)
    
    print("📊 MEJORANDO MODELO CON TÉCNICAS AVANZADAS")
    print("=" * 60)
    
    # Features - verificar cuáles existen
    feature_cols_candidates = [
        "age_months", "sex", "sex_numeric", "BMI", "baz",
        "bmi_velocity", "weight_velocity", "height_velocity",
        "allergy_count", "adherence_score", "symptom_frequency",
        "dietary_diversity_score", "altitude_m",
    ]
    
    # Filtrar solo las que existen
    feature_cols = [col for col in feature_cols_candidates if col in df.columns]
    
    # Si sex existe pero no sex_numeric, convertir
    if 'sex' in df.columns and 'sex_numeric' not in df.columns:
        df['sex_numeric'] = df['sex'].map({'M': 1, 'F': 0})
        if 'sex_numeric' not in feature_cols:
            feature_cols.append('sex_numeric')
        if 'sex' in feature_cols:
            feature_cols.remove('sex')
    
    print(f"Features seleccionados: {feature_cols}")
    
    X = df[feature_cols]
    y = df["label_status"]
    
    print(f"Total muestras: {len(X)}")
    print(f"\n📊 Distribución original:")
    print(y.value_counts().sort_index())
    
    # ============================================================
    # TÉCNICA 1: Cross-Validation (más confiable que un solo split)
    # ============================================================
    print("\n" + "=" * 60)
    print("🔄 TÉCNICA 1: Cross-Validation (5-fold)")
    print("=" * 60)
    
    rf_base = RandomForestClassifier(
        n_estimators=300,
        max_depth=None,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42
    )
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(rf_base, X, y, cv=cv, scoring='accuracy')
    
    print(f"Accuracy por fold: {[f'{s:.4f}' for s in scores]}")
    print(f"Accuracy promedio: {scores.mean():.4f} (+/- {scores.std():.4f})")
    
    # ============================================================
    # TÉCNICA 2: SMOTE para balancear clases
    # ============================================================
    print("\n" + "=" * 60)
    print("⚖️  TÉCNICA 2: SMOTE (Synthetic Minority Over-sampling)")
    print("=" * 60)
    
    try:
        # SMOTE con k_neighbors adaptativo
        min_samples = y.value_counts().min()
        k_neighbors = min(5, min_samples - 1) if min_samples > 1 else 1
        
        smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
        X_resampled, y_resampled = smote.fit_resample(X, y)
        
        print(f"\n📊 Distribución después de SMOTE:")
        print(pd.Series(y_resampled).value_counts().sort_index())
        
        # Entrenar con datos balanceados
        scores_smote = cross_val_score(rf_base, X_resampled, y_resampled, cv=cv, scoring='accuracy')
        
        print(f"\nAccuracy con SMOTE: {scores_smote.mean():.4f} (+/- {scores_smote.std():.4f})")
        
    except Exception as e:
        print(f"⚠️  SMOTE falló: {e}")
        print("   (Probablemente muy pocos casos en alguna clase)")
    
    # ============================================================
    # TÉCNICA 3: Ajustar hiperparámetros para dataset pequeño
    # ============================================================
    print("\n" + "=" * 60)
    print("🎛️  TÉCNICA 3: Hiperparámetros optimizados para dataset pequeño")
    print("=" * 60)
    
    rf_optimized = RandomForestClassifier(
        n_estimators=500,  # Más árboles
        max_depth=5,  # Limitar profundidad para evitar overfitting
        min_samples_split=5,  # Más conservador
        min_samples_leaf=3,  # Más conservador
        max_features='sqrt',  # Menos features por árbol
        class_weight='balanced_subsample',  # Balanceo por subsample
        random_state=42,
        bootstrap=True,
        oob_score=True  # Out-of-bag score
    )
    
    rf_optimized.fit(X, y)
    
    print(f"OOB Score: {rf_optimized.oob_score_:.4f}")
    
    scores_opt = cross_val_score(rf_optimized, X, y, cv=cv, scoring='accuracy')
    print(f"Accuracy optimizado: {scores_opt.mean():.4f} (+/- {scores_opt.std():.4f})")
    
    # ============================================================
    # ANÁLISIS DE ERRORES
    # ============================================================
    print("\n" + "=" * 60)
    print("🔍 ANÁLISIS DE ERRORES")
    print("=" * 60)
    
    from sklearn.model_selection import cross_val_predict
    y_pred = cross_val_predict(rf_optimized, X, y, cv=cv)
    
    print("\n📊 Reporte de clasificación:")
    print(classification_report(y, y_pred, target_names=['NORMAL', 'RIESGO', 'MODERADO', 'SEVERO']))
    
    print("\n📊 Matriz de confusión:")
    cm = confusion_matrix(y, y_pred)
    print(cm)
    
    # Feature importance
    print("\n📊 Top 5 Features más importantes:")
    importances = pd.DataFrame({
        'feature': feature_cols,
        'importance': rf_optimized.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(importances.head(5).to_string(index=False))
    
    # ============================================================
    # RECOMENDACIONES
    # ============================================================
    print("\n" + "=" * 60)
    print("💡 RECOMENDACIONES")
    print("=" * 60)
    
    print("""
1. 📈 RECOLECTAR MÁS DATOS (prioridad alta):
   - Objetivo: al menos 300-500 casos únicos
   - Especialmente clase RIESGO (solo 5 casos)
   
2. ⚖️  USAR SMOTE en producción:
   - Balancea las clases minoritarias
   - Mejora detección de casos RIESGO/MODERADO/SEVERO
   
3. 🔄 USAR CROSS-VALIDATION:
   - Más confiable que un solo train/val split
   - Mejor estimación del rendimiento real
   
4. 🎯 OPTIMIZAR PARA RECALL en clases críticas:
   - Es mejor detectar falsos positivos que perder casos SEVERO
   - Ajustar threshold de clasificación
   
5. 📊 MONITOREAR MÉTRICAS POR CLASE:
   - No solo accuracy global
   - F1-score, precision, recall por clase
""")
    
    # Guardar resultados
    results = {
        "dataset_size": len(X),
        "cv_baseline": float(scores.mean()),
        "cv_baseline_std": float(scores.std()),
        "cv_optimized": float(scores_opt.mean()),
        "cv_optimized_std": float(scores_opt.std()),
        "oob_score": float(rf_optimized.oob_score_),
        "class_distribution": y.value_counts().to_dict(),
    }
    
    output_path = BASE_DIR / "models/optimization_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Resultados guardados en: {output_path}")


if __name__ == "__main__":
    main()
