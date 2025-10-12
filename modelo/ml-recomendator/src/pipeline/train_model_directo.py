"""
Script para entrenar modelo que aprende DIRECTAMENTE de edad, talla, peso.
NO usa BAZ precalculado - el modelo aprende los patrones de la OMS.

Modelos utilizados:
- Naive Bayes (Bayesian): Clasificación probabilística basada en teorema de Bayes
- Random Forest: Clasificación basada en múltiples árboles de decisión
- Ensemble: Combinación de ambos modelos con votación ponderada
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.utils.db_connector import DatabaseConnector


def cargar_datos_desde_db(db_connector: DatabaseConnector) -> pd.DataFrame:
    """
    Carga datos de antropometrías desde la BD.
    Usa el BAZ que ya está calculado en la BD.
    """
    query = """
    SELECT
        n.nin_sexo as sexo,
        TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as edad_meses,
        a.ant_peso_kg as peso_kg,
        a.ant_talla_cm as talla_cm,
        a.ant_z_imc as baz
    FROM antropometrias a
    INNER JOIN ninos n ON a.nin_id = n.nin_id
    WHERE a.ant_peso_kg IS NOT NULL
      AND a.ant_talla_cm IS NOT NULL
      AND a.ant_peso_kg > 0
      AND a.ant_talla_cm > 0
      AND a.ant_z_imc IS NOT NULL
      AND TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) BETWEEN 0 AND 228
    ORDER BY a.ant_fecha DESC
    """

    df = db_connector.execute_query(query)
    print(f"✅ Cargados {len(df)} registros desde BD")

    # Calcular BMI
    df["bmi"] = df["peso_kg"] / (df["talla_cm"] / 100) ** 2

    # Clasificar según BAZ (usando las reglas OMS)
    def clasificar_baz(baz):
        if baz < -3.0:
            return "DESNUTRICION_SEVERA"
        elif -3.0 <= baz < -2.0:
            return "DESNUTRICION_MODERADA"
        elif -2.0 <= baz < -1.0:
            return "RIESGO_DESNUTRICION"
        elif -1.0 <= baz <= 1.0:
            return "NORMAL"
        elif 1.0 < baz <= 2.0:
            return "RIESGO_SOBREPESO"
        elif 2.0 < baz <= 3.0:
            return "SOBREPESO"
        else:
            return "OBESIDAD"

    df["clasificacion_nutricional"] = df["baz"].apply(clasificar_baz)
    print(f"✅ Clasificación OMS calculada para {len(df)} registros")

    return df


def preparar_features_directas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara features DIRECTAS sin calcular BAZ.
    El modelo aprenderá los patrones de la OMS por sí mismo.
    """
    df = df.copy()

    # 1. Convertir sexo a numérico
    df["sexo_num"] = df["sexo"].map({"M": 0, "F": 1})

    # 2. Calcular BMI (esto es solo peso/altura^2, no es BAZ)
    df["bmi"] = df["peso_kg"] / (df["talla_cm"] / 100) ** 2

    # 3. Features de edad (ayudan al modelo a entender rangos)
    df["edad_anos"] = df["edad_meses"] / 12
    df["es_bebe"] = (df["edad_meses"] < 24).astype(int)
    df["es_preescolar"] = ((df["edad_meses"] >= 24) & (df["edad_meses"] < 60)).astype(int)
    df["es_escolar"] = ((df["edad_meses"] >= 60) & (df["edad_meses"] < 120)).astype(int)
    df["es_adolescente"] = (df["edad_meses"] >= 120).astype(int)

    # 4. Ratios que ayudan al modelo
    df["peso_por_edad"] = df["peso_kg"] / df["edad_meses"]
    df["talla_por_edad"] = df["talla_cm"] / df["edad_meses"]

    # 5. Interacciones importantes
    df["bmi_x_edad"] = df["bmi"] * df["edad_meses"]
    df["peso_x_talla"] = df["peso_kg"] * df["talla_cm"]

    return df


def mapear_clasificacion_a_label(clasificacion: str) -> int:
    """Mapea clasificación OMS a label numérico."""
    mapa = {
        "DESNUTRICION_SEVERA": 0,
        "DESNUTRICION_MODERADA": 1,
        "RIESGO_DESNUTRICION": 2,
        "NORMAL": 3,
        "RIESGO_SOBREPESO": 4,
        "SOBREPESO": 5,
        "OBESIDAD": 6,
    }
    return mapa.get(clasificacion, 3)  # Default: NORMAL


def entrenar_modelo_directo(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    output_dir: Path,
):
    """
    Entrena modelo que aprende DIRECTAMENTE de los datos.
    Usa Naive Bayes (Bayesian) y Random Forest para clasificación.
    """
    print("\n" + "=" * 70)
    print("🎯 ENTRENANDO MODELO DIRECTO (Naive Bayes + Random Forest)")
    print("   Con SMOTE para balancear clases")
    print("=" * 70)

    # Escalar features para mejor aprendizaje
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    # Aplicar SMOTE para balancear clases en training
    print("\n🔄 Aplicando SMOTE para balancear clases...")
    print(f"   Antes: {len(X_train_scaled)} muestras")

    smote = SMOTE(random_state=42, k_neighbors=3)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)

    print(f"   Después: {len(X_train_balanced)} muestras")
    print("   Distribución balanceada:")
    for label in sorted(y_train_balanced.unique()):
        count = (y_train_balanced == label).sum()
        print(f"      Clase {label}: {count} muestras")

    # Probar varios modelos: Naive Bayes y Random Forest
    # Con menos datos, usar modelos más simples para evitar overfitting
    modelos = {
        "NaiveBayes": GaussianNB(),
        "RandomForest": RandomForestClassifier(
            n_estimators=200,  # Reducido para evitar overfitting
            max_depth=10,  # Más shallow
            min_samples_split=20,  # Más conservador
            min_samples_leaf=10,  # Más conservador
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "Ensemble_NB_RF": VotingClassifier(
            estimators=[
                ("nb", GaussianNB()),
                (
                    "rf",
                    RandomForestClassifier(
                        n_estimators=200,
                        max_depth=10,
                        min_samples_split=20,
                        min_samples_leaf=10,
                        class_weight="balanced",
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ],
            voting="soft",
            weights=[2, 1],  # Dar más peso a Naive Bayes (más simple)
        ),
    }

    resultados = {}
    mejor_modelo = None
    mejor_accuracy = 0

    for nombre, modelo in modelos.items():
        print(f"\n🔄 Entrenando {nombre}...")

        # Entrenar con datos balanceados
        modelo.fit(X_train_balanced, y_train_balanced)

        # Predecir (en datos originales sin SMOTE)
        y_pred_train = modelo.predict(X_train_scaled)
        y_pred_val = modelo.predict(X_val_scaled)

        # Métricas
        acc_train = accuracy_score(y_train, y_pred_train)
        acc_val = accuracy_score(y_val, y_pred_val)
        f1_train = f1_score(y_train, y_pred_train, average="weighted")
        f1_val = f1_score(y_val, y_pred_val, average="weighted")

        resultados[nombre] = {
            "accuracy_train": float(acc_train),
            "accuracy_val": float(acc_val),
            "f1_train": float(f1_train),
            "f1_val": float(f1_val),
            "overfitting": float(acc_train - acc_val),
        }

        print(f"   Train Accuracy: {acc_train:.4f}")
        print(f"   Val Accuracy:   {acc_val:.4f}")
        print(f"   Val F1-Score:   {f1_val:.4f}")
        print(f"   Overfitting:    {acc_train - acc_val:.4f}")

        # Guardar mejor modelo
        if acc_val > mejor_accuracy:
            mejor_accuracy = acc_val
            mejor_modelo = (nombre, modelo)

    # Guardar mejor modelo
    nombre_mejor, modelo_mejor = mejor_modelo
    print(f"\n✅ Mejor modelo: {nombre_mejor} (Accuracy: {mejor_accuracy:.4f})")

    # Guardar modelo y scaler
    model_path = output_dir / "modelo_directo.pkl"
    scaler_path = output_dir / "scaler_directo.pkl"

    joblib.dump(modelo_mejor, model_path)
    joblib.dump(scaler, scaler_path)

    print(f"   Modelo guardado: {model_path}")
    print(f"   Scaler guardado: {scaler_path}")

    # Reporte detallado
    y_pred_val = modelo_mejor.predict(X_val_scaled)
    report = classification_report(
        y_val,
        y_pred_val,
        target_names=[
            "DESNUT_SEV",
            "DESNUT_MOD",
            "RIESGO_DESN",
            "NORMAL",
            "RIESGO_SOB",
            "SOBREPESO",
            "OBESIDAD",
        ],
        output_dict=True,
    )

    # Guardar métricas
    metricas = {
        "modelo": nombre_mejor,
        "fecha_entrenamiento": datetime.now().isoformat(),
        "resultados_todos": resultados,
        "mejor_modelo": {
            "nombre": nombre_mejor,
            "accuracy_val": float(mejor_accuracy),
            "f1_val": float(f1_score(y_val, y_pred_val, average="weighted")),
        },
        "classification_report": report,
        "features_usadas": list(X_train.columns),
    }

    metrics_path = output_dir / "metricas_directo.json"
    with open(metrics_path, "w") as f:
        json.dump(metricas, f, indent=2)

    print(f"   Métricas guardadas: {metrics_path}")

    # Feature importance (si es RF)
    if nombre_mejor == "RandomForest":
        importance = pd.DataFrame(
            {"feature": X_train.columns, "importance": modelo_mejor.feature_importances_}
        ).sort_values("importance", ascending=False)

        importance_path = output_dir / "feature_importance_directo.csv"
        importance.to_csv(importance_path, index=False)

        print("\n📊 Top 5 Features más importantes:")
        for idx, row in importance.head(5).iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")

    return modelo_mejor, scaler, metricas


def main():
    parser = argparse.ArgumentParser(
        description="Entrenar modelo DIRECTO (aprende de edad, peso, talla)"
    )
    parser.add_argument(
        "--data-source",
        choices=["db", "csv"],
        default="db",
        help="Fuente de datos: db (MySQL) o csv",
    )
    parser.add_argument("--csv-path", type=Path, help="Ruta al CSV si data-source=csv")
    parser.add_argument(
        "--output", type=Path, default=BASE_DIR / "models" / "directo", help="Directorio de salida"
    )
    parser.add_argument("--test-size", type=float, default=0.2, help="Proporción de validación")

    args = parser.parse_args()

    # Crear directorio de salida
    args.output.mkdir(parents=True, exist_ok=True)

    # Cargar datos
    print("\n📂 Cargando datos...")

    if args.data_source == "db":
        db_connector = DatabaseConnector.from_env()
        db_connector.connect()
        df = cargar_datos_desde_db(db_connector)
        db_connector.disconnect()
    else:
        if not args.csv_path or not args.csv_path.exists():
            print("❌ Debes especificar --csv-path válido")
            return
        df = pd.read_csv(args.csv_path)

    print(f"   Total registros: {len(df)}")
    print(f"   Columnas: {list(df.columns)}")

    # Preparar features DIRECTAS
    print("\n🔧 Preparando features directas...")
    df = preparar_features_directas(df)

    # Mapear clasificación a labels
    df["label"] = df["clasificacion_nutricional"].apply(mapear_clasificacion_a_label)

    # Distribución de clases
    print("\n📊 Distribución de clases:")
    dist = df["label"].value_counts().sort_index()
    nombres = [
        "DESNUT_SEV",
        "DESNUT_MOD",
        "RIESGO_DESN",
        "NORMAL",
        "RIESGO_SOB",
        "SOBREPESO",
        "OBESIDAD",
    ]
    for label, count in dist.items():
        print(f"   {nombres[label]}: {count} ({count/len(df)*100:.1f}%)")

    # Seleccionar features para el modelo
    feature_cols = [
        "edad_meses",
        "sexo_num",
        "peso_kg",
        "talla_cm",
        "bmi",
        "edad_anos",
        "es_bebe",
        "es_preescolar",
        "es_escolar",
        "es_adolescente",
        "peso_por_edad",
        "talla_por_edad",
        "bmi_x_edad",
        "peso_x_talla",
    ]

    X = df[feature_cols]
    y = df["label"]

    # Split train/val
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=args.test_size, stratify=y, random_state=42
    )

    print("\n📈 Split de datos:")
    print(f"   Train: {len(X_train)} muestras")
    print(f"   Val:   {len(X_val)} muestras")

    # Entrenar modelo
    modelo, scaler, metricas = entrenar_modelo_directo(X_train, y_train, X_val, y_val, args.output)

    print("\n" + "=" * 70)
    print("✅ ENTRENAMIENTO COMPLETADO")
    print("=" * 70)
    print(f"\nModelo guardado en: {args.output}")
    print(f"Accuracy de validación: {metricas['mejor_modelo']['accuracy_val']:.2%}")
    print("\n💡 Este modelo aprende DIRECTAMENTE de edad, peso y talla")
    print("   NO necesita BAZ precalculado para hacer predicciones")


if __name__ == "__main__":
    main()
