"""
Pipeline de entrenamiento para el modelo LightGBM Ranker.
Incluye validación cruzada, optimización de hiperparámetros y evaluación.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import ndcg_score
from sklearn.model_selection import GroupKFold, ParameterGrid

from ..models.rankers.lgbm_ranker import MenuRanker, evaluate_ranker
from .feature_engineering import FeatureEngineer, create_mysql_connection_string

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RankerTrainingPipeline:
    """Pipeline completo para entrenar y evaluar el modelo ranker."""

    def __init__(
        self,
        db_connection_string: Optional[str] = None,
        model_save_path: str = "models/",
        random_state: int = 42,
    ):
        """
        Inicializar el pipeline de entrenamiento.

        Args:
            db_connection_string: String de conexión a la base de datos (opcional, usa .env si no se proporciona)
            model_save_path: Ruta donde guardar los modelos entrenados
            random_state: Semilla para reproducibilidad
        """
        # Usar conexión del .env si no se proporciona
        if db_connection_string is None:
            db_connection_string = create_mysql_connection_string()

        self.db_connection_string = db_connection_string
        self.model_save_path = model_save_path
        self.random_state = random_state
        self.feature_engineer = FeatureEngineer(db_connection_string)

        # Crear directorio de modelos si no existe
        os.makedirs(model_save_path, exist_ok=True)

        # Configuración por defecto del modelo
        self.default_params = {
            "objective": "lambdarank",
            "metric": "ndcg",
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "feature_fraction": 0.9,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
            "random_state": random_state,
        }

    def prepare_training_data(
        self, n_samples: int = 10000, test_size: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Preparar datos de entrenamiento y validación.

        Args:
            n_samples: Número de muestras a generar
            test_size: Proporción de datos para validación

        Returns:
            Tuple con DataFrames de entrenamiento y validación
        """
        logger.info(f"Generando {n_samples} muestras de entrenamiento...")

        # Generar dataset completo
        df = self.feature_engineer.generate_training_dataset()

        # Dividir por niños para evitar data leakage
        unique_children = df["child_id"].unique()
        np.random.shuffle(unique_children)

        split_idx = int(len(unique_children) * (1 - test_size))
        train_children = unique_children[:split_idx]
        val_children = unique_children[split_idx:]

        train_df = df[df["child_id"].isin(train_children)].copy()
        val_df = df[df["child_id"].isin(val_children)].copy()

        logger.info(
            f"Datos de entrenamiento: {len(train_df)} muestras, {len(train_children)} niños"
        )
        logger.info(f"Datos de validación: {len(val_df)} muestras, {len(val_children)} niños")

        return train_df, val_df

    def hyperparameter_search(
        self, train_df: pd.DataFrame, param_grid: Optional[Dict] = None, cv_folds: int = 3
    ) -> Dict[str, Any]:
        """
        Búsqueda de hiperparámetros usando validación cruzada.

        Args:
            train_df: DataFrame de entrenamiento
            param_grid: Grid de parámetros a probar
            cv_folds: Número de folds para CV

        Returns:
            Mejores parámetros encontrados
        """
        if param_grid is None:
            param_grid = {
                "num_leaves": [15, 31, 63],
                "learning_rate": [0.01, 0.05, 0.1],
                "feature_fraction": [0.8, 0.9, 1.0],
                "min_data_in_leaf": [10, 20, 50],
            }

        logger.info("Iniciando búsqueda de hiperparámetros...")

        # Preparar datos para LightGBM
        feature_cols = [
            col for col in train_df.columns if col not in ["child_id", "menu_id", "relevance_score"]
        ]

        X = train_df[feature_cols]
        y = train_df["relevance_score"]
        groups = train_df["child_id"]

        # Validación cruzada por grupos (niños)
        gkf = GroupKFold(n_splits=cv_folds)

        best_score = -np.inf
        best_params = None
        results = []

        # Probar todas las combinaciones de parámetros
        param_combinations = list(ParameterGrid(param_grid))

        for i, params in enumerate(param_combinations):
            logger.info(f"Probando combinación {i+1}/{len(param_combinations)}: {params}")

            # Combinar con parámetros por defecto
            current_params = {**self.default_params, **params}

            cv_scores = []

            for train_idx, val_idx in gkf.split(X, y, groups):
                X_train_fold, X_val_fold = X.iloc[train_idx], X.iloc[val_idx]
                y_train_fold, y_val_fold = y.iloc[train_idx], y.iloc[val_idx]
                groups_train = groups.iloc[train_idx]
                groups_val = groups.iloc[val_idx]

                # Crear datasets de LightGBM
                train_data = lgb.Dataset(
                    X_train_fold, label=y_train_fold, group=groups_train.value_counts().sort_index()
                )
                val_data = lgb.Dataset(
                    X_val_fold, label=y_val_fold, group=groups_val.value_counts().sort_index()
                )

                # Entrenar modelo
                model = lgb.train(
                    current_params,
                    train_data,
                    valid_sets=[val_data],
                    num_boost_round=100,
                    callbacks=[lgb.early_stopping(10), lgb.log_evaluation(0)],
                )

                # Evaluar
                y_pred = model.predict(X_val_fold)

                # Calcular NDCG por grupo
                ndcg_scores = []
                for child_id in groups_val.unique():
                    mask = groups_val == child_id
                    if mask.sum() > 1:  # Necesitamos al menos 2 elementos para NDCG
                        y_true_child = y_val_fold[mask].values.reshape(1, -1)
                        y_pred_child = y_pred[mask].reshape(1, -1)
                        ndcg = ndcg_score(y_true_child, y_pred_child, k=10)
                        ndcg_scores.append(ndcg)

                if ndcg_scores:
                    cv_scores.append(np.mean(ndcg_scores))

            if cv_scores:
                mean_score = np.mean(cv_scores)
                std_score = np.std(cv_scores)

                results.append({"params": params, "mean_ndcg": mean_score, "std_ndcg": std_score})

                logger.info(f"NDCG: {mean_score:.4f} (+/- {std_score:.4f})")

                if mean_score > best_score:
                    best_score = mean_score
                    best_params = current_params

        logger.info(f"Mejores parámetros encontrados: {best_params}")
        logger.info(f"Mejor NDCG: {best_score:.4f}")

        # Guardar resultados
        results_path = os.path.join(self.model_save_path, "hyperparameter_search_results.json")
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)

        return best_params

    def train_final_model(
        self, train_df: pd.DataFrame, val_df: pd.DataFrame, params: Optional[Dict] = None
    ) -> MenuRanker:
        """
        Entrenar el modelo final con los mejores parámetros.

        Args:
            train_df: DataFrame de entrenamiento
            val_df: DataFrame de validación
            params: Parámetros del modelo

        Returns:
            Modelo entrenado
        """
        if params is None:
            params = self.default_params

        logger.info("Entrenando modelo final...")

        # Crear y entrenar el ranker
        ranker = MenuRanker(params=params, random_state=self.random_state)
        ranker.fit(train_df)

        # Evaluar en validación
        logger.info("Evaluando modelo en datos de validación...")
        metrics = evaluate_ranker(ranker, val_df)

        logger.info("Métricas de validación:")
        for metric, value in metrics.items():
            logger.info(f"  {metric}: {value:.4f}")

        # Guardar modelo y métricas
        model_path = os.path.join(
            self.model_save_path, f"menu_ranker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        )
        ranker.save_model(model_path)

        metrics_path = os.path.join(self.model_save_path, "validation_metrics.json")
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)

        logger.info(f"Modelo guardado en: {model_path}")

        return ranker

    def run_full_pipeline(
        self,
        n_samples: int = 10000,
        optimize_hyperparams: bool = True,
        param_grid: Optional[Dict] = None,
    ) -> MenuRanker:
        """
        Ejecutar el pipeline completo de entrenamiento.

        Args:
            n_samples: Número de muestras a generar
            optimize_hyperparams: Si optimizar hiperparámetros
            param_grid: Grid de parámetros para optimización

        Returns:
            Modelo entrenado
        """
        logger.info("=== Iniciando pipeline de entrenamiento ===")

        # 1. Preparar datos
        train_df, val_df = self.prepare_training_data(n_samples=n_samples)

        # 2. Optimizar hiperparámetros (opcional)
        if optimize_hyperparams:
            best_params = self.hyperparameter_search(train_df, param_grid)
        else:
            best_params = self.default_params

        # 3. Entrenar modelo final
        ranker = self.train_final_model(train_df, val_df, best_params)

        logger.info("=== Pipeline completado exitosamente ===")

        return ranker


def main():
    """Función principal para ejecutar el entrenamiento."""

    # Crear pipeline (usa credenciales del .env automáticamente)
    pipeline = RankerTrainingPipeline(model_save_path="../../models/ranker/", random_state=42)

    # Ejecutar entrenamiento
    ranker = pipeline.run_full_pipeline(n_samples=20000, optimize_hyperparams=True)

    print("Entrenamiento completado!")


if __name__ == "__main__":
    main()
