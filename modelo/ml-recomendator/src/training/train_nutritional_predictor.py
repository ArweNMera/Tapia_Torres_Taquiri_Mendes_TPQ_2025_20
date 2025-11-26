"""
Script de entrenamiento del modelo de predicción nutricional.
Entrena un clasificador LightGBM para predecir estado nutricional futuro.
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class NutritionalPredictorTrainer:
    """
    Entrenador del modelo de predicción nutricional.
    """

    # Mapeo de clasificaciones OMS a índices
    CLASS_MAPPING = {
        "DESNUTRICION_SEVERA": 0,
        "DESNUTRICION_MODERADA": 1,
        "RIESGO_DESNUTRICION": 2,
        "NORMAL": 3,
        "RIESGO_SOBREPESO": 4,
        "SOBREPESO": 5,
        "OBESIDAD": 6,
    }

    # Features esperados (11 características)
    FEATURE_NAMES = [
        "age_months",
        "sex_numeric",
        "BMI",
        "weight_kg",
        "height_cm",
        "bmi_velocity",
        "weight_velocity",
        "height_velocity",
        "adherence_score",
        "allergy_count",
        "altitude_m",
    ]

    def __init__(self, config: Dict = None):
        """
        Inicializar entrenador.

        Args:
            config: Configuración del modelo LightGBM
        """
        self.config = config or self._get_default_config()
        self.model = None
        self.feature_names = self.FEATURE_NAMES
        self.class_names = list(self.CLASS_MAPPING.keys())

    def _get_default_config(self) -> Dict:
        """Obtener configuración por defecto de LightGBM con MUCHA regularización."""
        return {
            "objective": "multiclass",
            "num_class": 7,
            "metric": "multi_logloss",
            "boosting_type": "gbdt",
            "num_leaves": 12,  # Muy reducido para menos overfitting
            "learning_rate": 0.02,  # Muy lento para generalizar mejor
            "feature_fraction": 0.5,  # Solo 50% de features por árbol
            "bagging_fraction": 0.6,  # Solo 60% de datos por árbol
            "bagging_freq": 2,  # Muy frecuente
            "verbose": -1,
            "max_depth": 4,  # Árboles muy simples
            "min_data_in_leaf": 25,  # Más datos por hoja
            "lambda_l1": 1.0,  # Mucha regularización L1
            "lambda_l2": 1.0,  # Mucha regularización L2
            "min_gain_to_split": 0.2,  # Requiere más ganancia para split
            "drop_rate": 0.1,  # Dropout de árboles
        }

    def prepare_data(
        self, df: pd.DataFrame, validation_split: float = 0.2
    ) -> Tuple[lgb.Dataset, lgb.Dataset, pd.DataFrame, pd.DataFrame]:
        """
        Preparar datos para entrenamiento.

        Args:
            df: DataFrame con features y target
            validation_split: Proporción de datos para validación

        Returns:
            Tupla (train_data, val_data, X_val, y_val)
        """
        logger.info("📊 Preparando datos para entrenamiento...")

        # Validar columnas
        missing_features = set(self.feature_names) - set(df.columns)
        if missing_features:
            raise ValueError(f"Faltan features: {missing_features}")

        if "clasificacion_oms" not in df.columns:
            raise ValueError("Falta columna 'clasificacion_oms'")

        # Extraer features y target
        X = df[self.feature_names].copy()
        y = df["clasificacion_oms"].map(self.CLASS_MAPPING)

        # Verificar que no haya NaN en target
        if y.isna().any():
            logger.warning(
                f"⚠️ {y.isna().sum()} registros con clasificación desconocida, eliminando..."
            )
            valid_idx = ~y.isna()
            X = X[valid_idx]
            y = y[valid_idx]

        # Convertir a numpy
        y = y.astype(int).values

        logger.info(f"   Features: {X.shape}")
        logger.info(f"   Target: {y.shape}")
        logger.info("   Distribución de clases:")
        for class_name, class_idx in self.CLASS_MAPPING.items():
            count = (y == class_idx).sum()
            logger.info(f"      {class_name}: {count} ({count/len(y)*100:.1f}%)")

        # Split train/validation (30% validación para mejor evaluación)
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.30, random_state=42, stratify=y
        )

        logger.info(f"✅ Train: {len(X_train)}, Validation: {len(X_val)}")

        # Crear datasets de LightGBM
        train_data = lgb.Dataset(
            X_train,
            label=y_train,
            feature_name=self.feature_names,
            categorical_feature=[],
        )

        val_data = lgb.Dataset(
            X_val,
            label=y_val,
            feature_name=self.feature_names,
            categorical_feature=[],
            reference=train_data,
        )

        return train_data, val_data, X_val, y_val

    def train(
        self,
        train_data: lgb.Dataset,
        val_data: lgb.Dataset,
        num_boost_round: int = 500,
        early_stopping_rounds: int = 50,
    ) -> lgb.Booster:
        """
        Entrenar modelo LightGBM.

        Args:
            train_data: Dataset de entrenamiento
            val_data: Dataset de validación
            num_boost_round: Número máximo de iteraciones
            early_stopping_rounds: Paradas tempranas

        Returns:
            Modelo entrenado
        """
        logger.info("🚀 Entrenando modelo LightGBM...")
        logger.info(f"   Configuración: {self.config}")

        # Entrenar
        self.model = lgb.train(
            self.config,
            train_data,
            num_boost_round=num_boost_round,
            valid_sets=[train_data, val_data],
            valid_names=["train", "valid"],
            callbacks=[
                lgb.early_stopping(stopping_rounds=early_stopping_rounds),
                lgb.log_evaluation(period=50),
            ],
        )

        logger.info(f"✅ Entrenamiento completado en {self.model.num_trees()} iteraciones")

        return self.model

    def evaluate(self, X_val: pd.DataFrame, y_val: np.ndarray) -> Dict:
        """
        Evaluar modelo en conjunto de validación.

        Args:
            X_val: Features de validación
            y_val: Target de validación

        Returns:
            Diccionario con métricas
        """
        logger.info("📊 Evaluando modelo...")

        # Predicciones
        y_pred_proba = self.model.predict(X_val)
        y_pred = np.argmax(y_pred_proba, axis=1)

        # Métricas globales
        accuracy = accuracy_score(y_val, y_pred)
        f1_macro = f1_score(y_val, y_pred, average="macro")
        f1_weighted = f1_score(y_val, y_pred, average="weighted")

        logger.info(f"✅ Accuracy: {accuracy:.4f}")
        logger.info(f"✅ F1-Score (macro): {f1_macro:.4f}")
        logger.info(f"✅ F1-Score (weighted): {f1_weighted:.4f}")

        # Reporte por clase (solo para las clases presentes en validación)
        unique_classes = np.unique(np.concatenate([y_val, y_pred]))
        present_class_names = [self.class_names[i] for i in unique_classes]

        report = classification_report(
            y_val,
            y_pred,
            labels=unique_classes,
            target_names=present_class_names,
            output_dict=True,
            zero_division=0,
        )

        logger.info("\n📋 Reporte por clase:")
        for class_name in present_class_names:
            if class_name in report:
                metrics = report[class_name]
                logger.info(
                    f"   {class_name}: "
                    f"Precision={metrics['precision']:.3f}, "
                    f"Recall={metrics['recall']:.3f}, "
                    f"F1={metrics['f1-score']:.3f}, "
                    f"Support={int(metrics['support'])}"
                )

        # Matriz de confusión (solo para clases presentes)
        cm = confusion_matrix(y_val, y_pred, labels=unique_classes)
        logger.info("\n📊 Matriz de Confusión:")
        logger.info(f"Clases: {present_class_names}")
        logger.info(f"\n{cm}")

        # Feature importance
        feature_importance = self.model.feature_importance(importance_type="gain")
        feature_importance_dict = dict(zip(self.feature_names, feature_importance))
        sorted_features = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)

        logger.info("\n🔍 Feature Importance (Top 5):")
        for feature, importance in sorted_features[:5]:
            logger.info(f"   {feature}: {importance:.2f}")

        metrics = {
            "accuracy": float(accuracy),
            "f1_macro": float(f1_macro),
            "f1_weighted": float(f1_weighted),
            "classification_report": report,
            "confusion_matrix": cm.tolist(),
            "feature_importance": feature_importance_dict,
        }

        return metrics

    def save_model(self, output_path: str, metrics: Dict) -> None:
        """
        Guardar modelo entrenado con metadata.

        Args:
            output_path: Ruta donde guardar el modelo
            metrics: Métricas de evaluación
        """
        logger.info(f"💾 Guardando modelo en: {output_path}")

        # Crear directorio si no existe
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Preparar payload
        payload = {
            "model": self.model,
            "feature_names": self.feature_names,
            "class_names": self.class_names,
            "class_mapping": self.CLASS_MAPPING,
            "metrics": metrics,
            "config": self.config,
            "training_date": datetime.now().isoformat(),
            "version": "1.0",
        }

        # Guardar
        joblib.dump(payload, output_path)

        logger.info("✅ Modelo guardado exitosamente")
        logger.info(f"   Tamaño: {Path(output_path).stat().st_size / (1024*1024):.2f} MB")


def main():
    """Función principal para entrenamiento."""
    parser = argparse.ArgumentParser(description="Entrenar modelo de predicción nutricional")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Ruta al archivo CSV con datos de entrenamiento",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="models/nutritional_predictor.pkl",
        help="Ruta donde guardar el modelo entrenado",
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
    parser.add_argument(
        "--early-stopping",
        type=int,
        default=50,
        help="Paradas tempranas (default: 50)",
    )

    args = parser.parse_args()

    # Configurar logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    logger.info("=" * 80)
    logger.info("🚀 ENTRENAMIENTO DE MODELO DE PREDICCIÓN NUTRICIONAL")
    logger.info("=" * 80)

    # 1. Cargar datos
    logger.info(f"📂 Cargando datos desde: {args.input}")
    df = pd.read_csv(args.input)
    logger.info(f"✅ Datos cargados: {len(df)} registros, {len(df.columns)} columnas")

    # 2. Inicializar entrenador
    trainer = NutritionalPredictorTrainer()

    # 3. Preparar datos
    train_data, val_data, X_val, y_val = trainer.prepare_data(df, args.validation_split)

    # 4. Entrenar
    model = trainer.train(train_data, val_data, args.num_boost_round, args.early_stopping)

    # 5. Evaluar
    metrics = trainer.evaluate(X_val, y_val)

    # 6. Guardar
    trainer.save_model(args.output, metrics)

    logger.info("=" * 80)
    logger.info("✅ ENTRENAMIENTO COMPLETADO")
    logger.info(f"   Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"   F1-Score (macro): {metrics['f1_macro']:.4f}")
    logger.info(f"   Modelo guardado en: {args.output}")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
