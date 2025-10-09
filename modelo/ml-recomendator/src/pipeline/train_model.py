"""
Script para entrenar modelos de clasificación nutricional.
"""

import argparse
from pathlib import Path
import pandas as pd
import yaml
import json
from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score

import sys
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.models import (
    RandomForestNutritionClassifier,
    NeuralNetNutritionClassifier,
    EnsembleNutritionClassifier,
)
from src.features import FeatureEngineer, WHOCalculator, DataValidator


def load_config(config_path: Path) -> dict:
    """Carga configuración desde YAML."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def train_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    config: dict,
    output_dir: Path,
) -> RandomForestNutritionClassifier:
    """Entrena modelo Random Forest."""
    
    print("\n" + "=" * 60)
    print("🌲 ENTRENANDO RANDOM FOREST")
    print("=" * 60)
    
    model_params = config.get("model", {})
    model = RandomForestNutritionClassifier(
        n_estimators=model_params.get("n_estimators", 300),
        max_depth=model_params.get("max_depth"),
        min_samples_leaf=model_params.get("min_samples_leaf", 2),
        class_weight=model_params.get("class_weight", "balanced"),
        random_state=config.get("seed", 42),
    )
    
    metrics = model.train(X_train, y_train, X_val, y_val)
    
    # Guardar modelo
    model_path = output_dir / "rf_model.pkl"
    model.save(model_path)
    
    # Guardar métricas
    metrics_path = output_dir / "rf_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    
    # Feature importance
    importance = model.get_feature_importance()
    importance_df = pd.DataFrame(
        list(importance.items()),
        columns=["feature", "importance"]
    ).sort_values("importance", ascending=False)
    
    importance_path = output_dir / "rf_feature_importance.csv"
    importance_df.to_csv(importance_path, index=False)
    
    print(f"\n✅ Random Forest entrenado")
    print(f"   Accuracy (val): {metrics.get('val_accuracy', 0):.4f}")
    print(f"   F1-Score (val): {metrics.get('val_f1_weighted', 0):.4f}")
    
    return model


def train_neural_net(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    config: dict,
    output_dir: Path,
) -> NeuralNetNutritionClassifier:
    """Entrena Red Neuronal."""
    
    print("\n" + "=" * 60)
    print("🧠 ENTRENANDO RED NEURONAL")
    print("=" * 60)
    
    model_params = config.get("model", {})
    model = NeuralNetNutritionClassifier(
        hidden_layers=model_params.get("hidden_layers", [64, 32]),
        dropout=model_params.get("dropout", 0.2),
        lr=model_params.get("lr", 0.001),
        epochs=model_params.get("epochs", 50),
        batch_size=model_params.get("batch_size", 64),
        random_state=config.get("seed", 42),
    )
    
    metrics = model.train(X_train, y_train, X_val, y_val)
    
    # Guardar modelo
    model_path = output_dir / "nn_model.pkl"
    model.save(model_path)
    
    # Guardar métricas
    metrics_path = output_dir / "nn_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✅ Red Neuronal entrenada")
    print(f"   Accuracy (val): {metrics.get('val_accuracy', 0):.4f}")
    print(f"   F1-Score (val): {metrics.get('val_f1_weighted', 0):.4f}")
    
    return model


def train_ensemble(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    config_rf: dict,
    config_nn: dict,
    output_dir: Path,
) -> EnsembleNutritionClassifier:
    """Entrena Ensemble (RF + NN)."""
    
    print("\n" + "=" * 60)
    print("🎯 ENTRENANDO ENSEMBLE")
    print("=" * 60)
    
    rf_params = {
        "n_estimators": config_rf.get("model", {}).get("n_estimators", 300),
        "max_depth": config_rf.get("model", {}).get("max_depth"),
        "min_samples_leaf": config_rf.get("model", {}).get("min_samples_leaf", 2),
        "class_weight": config_rf.get("model", {}).get("class_weight", "balanced"),
        "random_state": config_rf.get("seed", 42),
    }
    
    nn_params = {
        "hidden_layers": config_nn.get("model", {}).get("hidden_layers", [64, 32]),
        "dropout": config_nn.get("model", {}).get("dropout", 0.2),
        "lr": config_nn.get("model", {}).get("lr", 0.001),
        "epochs": config_nn.get("model", {}).get("epochs", 50),
        "batch_size": config_nn.get("model", {}).get("batch_size", 64),
        "random_state": config_nn.get("seed", 42),
    }
    
    model = EnsembleNutritionClassifier(
        rf_weight=0.7,
        nn_weight=0.3,
        rf_params=rf_params,
        nn_params=nn_params,
    )
    
    metrics = model.train(X_train, y_train, X_val, y_val)
    
    # Guardar modelo
    model_path = output_dir / "ensemble_model.pkl"
    model.save(model_path)
    
    # Guardar métricas
    metrics_path = output_dir / "ensemble_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✅ Ensemble entrenado")
    print(f"   Accuracy (val): {metrics.get('ensemble_val_accuracy', 0):.4f}")
    print(f"   F1-Score (val): {metrics.get('ensemble_val_f1_weighted', 0):.4f}")
    
    return model


def main():
    parser = argparse.ArgumentParser(description="Entrenar modelos de clasificación nutricional")
    parser.add_argument("--data", type=Path, required=True, help="CSV con datos etiquetados")
    parser.add_argument("--model", type=str, choices=["rf", "nn", "ensemble"], default="ensemble",
                        help="Tipo de modelo a entrenar")
    parser.add_argument("--config-rf", type=Path, default=BASE_DIR / "configs/rf.yaml",
                        help="Config para Random Forest")
    parser.add_argument("--config-nn", type=Path, default=BASE_DIR / "configs/nn.yaml",
                        help="Config para Red Neuronal")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "models",
                        help="Directorio de salida")
    parser.add_argument("--test-size", type=float, default=0.2, help="Proporción de test")
    parser.add_argument("--use-cv", action="store_true", help="Usar cross-validation en lugar de train/val split")
    parser.add_argument("--cv-folds", type=int, default=5, help="Número de folds para cross-validation")
    
    args = parser.parse_args()
    
    # Crear directorio de salida
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Cargar datos
    print(f"\n📂 Cargando datos desde: {args.data}")
    df = pd.read_csv(args.data)
    print(f"   Filas: {len(df)}, Columnas: {len(df.columns)}")
    
    # Validar datos
    print("\n🔍 Validando datos...")
    validator = DataValidator()
    validation = validator.validate_anthropometric_data(df)
    
    if not validation["valid"]:
        print("❌ Datos inválidos:")
        for issue in validation["issues"]:
            print(f"   - {issue}")
        return
    
    if validation["warnings"]:
        print("⚠️  Advertencias:")
        for warning in validation["warnings"]:
            print(f"   - {warning}")
    
    # Separar features y labels
    if "label_status" not in df.columns:
        print("❌ Columna 'label_status' no encontrada")
        return
    
    # Seleccionar features (SIN BAZ para evitar data leakage)
    feature_cols_candidates = [
        "age_months", "sex_numeric", "BMI",
        # "baz",  # ❌ REMOVIDO: BAZ es prácticamente la etiqueta (98% correlación)
        "bmi_velocity", "weight_velocity", "height_velocity",
        "allergy_count", "adherence_score", "symptom_frequency",
        "dietary_diversity_score", "altitude_m",
    ]
    
    # Si sex existe pero no sex_numeric, convertir
    if 'sex' in df.columns and 'sex_numeric' not in df.columns:
        df['sex_numeric'] = df['sex'].map({'M': 0, 'F': 1})
    
    # Filtrar solo features disponibles (excluir 'sex' string)
    available_features = [f for f in feature_cols_candidates if f in df.columns]
    
    print(f"\n📊 Features disponibles: {len(available_features)}")
    
    X = df[available_features]
    y = df["label_status"]
    
    # Eliminar duplicados si existen
    df_unique = pd.concat([X, y], axis=1).drop_duplicates()
    if len(df_unique) < len(df):
        print(f"\n⚠️  Eliminados {len(df) - len(df_unique)} registros duplicados")
        X = df_unique[available_features]
        y = df_unique["label_status"]
    
    # Split train/val
    X_train, X_val, y_train, y_val = train_test_split(
        X, y,
        test_size=args.test_size,
        stratify=y,
        random_state=42
    )
    
    print(f"\n📈 Split de datos:")
    print(f"   Train: {len(X_train)} muestras")
    print(f"   Val:   {len(X_val)} muestras")
    
    # Si se usa cross-validation, mostrar info adicional
    if args.use_cv:
        print(f"   CV: {args.cv_folds}-fold cross-validation")
        print(f"   Total: {len(X)} muestras")
    
    # Cargar configs
    config_rf = load_config(args.config_rf)
    config_nn = load_config(args.config_nn)
    
    # Entrenar modelo
    if args.model == "rf":
        model = train_random_forest(X_train, y_train, X_val, y_val, config_rf, args.output)
    
    elif args.model == "nn":
        model = train_neural_net(X_train, y_train, X_val, y_val, config_nn, args.output)
    
    elif args.model == "ensemble":
        model = train_ensemble(X_train, y_train, X_val, y_val, config_rf, config_nn, args.output)
    
    # Si se usa cross-validation, evaluar con CV
    if args.use_cv and args.model == "rf":
        print("\n" + "=" * 60)
        print("🔄 EVALUACIÓN CON CROSS-VALIDATION")
        print("=" * 60)
        
        from sklearn.ensemble import RandomForestClassifier
        
        rf_cv = RandomForestClassifier(
            n_estimators=config_rf.get("model", {}).get("n_estimators", 300),
            max_depth=config_rf.get("model", {}).get("max_depth"),
            min_samples_leaf=config_rf.get("model", {}).get("min_samples_leaf", 2),
            class_weight=config_rf.get("model", {}).get("class_weight", "balanced"),
            random_state=config_rf.get("seed", 42),
        )
        
        cv = StratifiedKFold(n_splits=args.cv_folds, shuffle=True, random_state=42)
        scores = cross_val_score(rf_cv, X, y, cv=cv, scoring='accuracy')
        
        print(f"Accuracy por fold: {[f'{s:.4f}' for s in scores]}")
        print(f"Accuracy promedio: {scores.mean():.4f} (+/- {scores.std():.4f})")
        
        # Guardar métricas de CV
        cv_metrics = {
            "cv_accuracy_mean": float(scores.mean()),
            "cv_accuracy_std": float(scores.std()),
            "cv_scores": [float(s) for s in scores],
            "cv_folds": args.cv_folds,
        }
        
        cv_metrics_path = args.output / "cv_metrics.json"
        with open(cv_metrics_path, "w") as f:
            json.dump(cv_metrics, f, indent=2)
        
        print(f"\n✅ Métricas CV guardadas en: {cv_metrics_path}")
    
    print(f"\n✅ Entrenamiento completado")
    print(f"   Modelos guardados en: {args.output}")
    
    if args.use_cv:
        print(f"\n💡 Tip: El accuracy con CV ({scores.mean():.2%}) es más confiable")
        print(f"   que el accuracy de validación simple para datasets pequeños.")


if __name__ == "__main__":
    main()
