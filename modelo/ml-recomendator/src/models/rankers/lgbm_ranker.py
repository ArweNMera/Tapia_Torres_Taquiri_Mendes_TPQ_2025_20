"""
LightGBM Ranker para recomendación de menús.

Este módulo implementa un modelo Learning-to-Rank usando LightGBM
para puntuar candidatos de menú por slot, dado el contexto del niño.
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import shap
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)


class MenuRanker:
    """
    Ranker de menús usando LightGBM con Learning-to-Rank.

    Utiliza LambdaMART para ordenar candidatos de menú por slot
    considerando el contexto del niño (edad, estado nutricional, preferencias).
    """

    def __init__(
        self,
        objective: str = "lambdarank",
        metric: str = "ndcg",
        num_leaves: int = 31,
        learning_rate: float = 0.1,
        feature_fraction: float = 0.9,
        bagging_fraction: float = 0.8,
        bagging_freq: int = 5,
        verbose: int = -1,
        random_state: int = 42,
        **kwargs
    ):
        """
        Inicializa el MenuRanker.

        Args:
            objective: Objetivo de LightGBM ('lambdarank', 'rank_xendcg')
            metric: Métrica de evaluación ('ndcg', 'map')
            num_leaves: Número de hojas en los árboles
            learning_rate: Tasa de aprendizaje
            feature_fraction: Fracción de features por árbol
            bagging_fraction: Fracción de datos para bagging
            bagging_freq: Frecuencia de bagging
            verbose: Nivel de verbosidad
            random_state: Semilla aleatoria
            **kwargs: Parámetros adicionales para LightGBM
        """
        self.params = {
            "objective": objective,
            "metric": metric,
            "num_leaves": num_leaves,
            "learning_rate": learning_rate,
            "feature_fraction": feature_fraction,
            "bagging_fraction": bagging_fraction,
            "bagging_freq": bagging_freq,
            "verbose": verbose,
            "random_state": random_state,
            **kwargs
        }

        self.model = None
        self.feature_names = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.explainer = None

    def _prepare_features(
        self,
        df: pd.DataFrame,
        fit_encoders: bool = False
    ) -> pd.DataFrame:
        """
        Prepara las features para entrenamiento/predicción.

        Args:
            df: DataFrame con features crudas
            fit_encoders: Si ajustar los encoders (solo en entrenamiento)

        Returns:
            DataFrame con features procesadas
        """
        df_processed = df.copy()

        # Identificar columnas categóricas y numéricas
        categorical_cols = df_processed.select_dtypes(include=['object', 'category']).columns
        numerical_cols = df_processed.select_dtypes(include=[np.number]).columns

        # Codificar variables categóricas
        for col in categorical_cols:
            if col not in self.label_encoders:
                if fit_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df_processed[col] = self.label_encoders[col].fit_transform(
                        df_processed[col].astype(str)
                    )
                else:
                    logger.warning(f"Encoder para {col} no encontrado, usando valores por defecto")
                    df_processed[col] = 0
            else:
                # Manejar valores no vistos durante entrenamiento
                known_values = set(self.label_encoders[col].classes_)
                df_processed[col] = df_processed[col].astype(str).apply(
                    lambda x: x if x in known_values else 'unknown'
                )

                # Agregar 'unknown' si no existe
                if 'unknown' not in known_values and not fit_encoders:
                    # Usar el valor más frecuente como fallback
                    df_processed[col] = df_processed[col].apply(
                        lambda x: self.label_encoders[col].classes_[0] if x == 'unknown' else x
                    )

                df_processed[col] = self.label_encoders[col].transform(df_processed[col])

        # Escalar variables numéricas
        if len(numerical_cols) > 0:
            if fit_encoders:
                df_processed[numerical_cols] = self.scaler.fit_transform(
                    df_processed[numerical_cols]
                )
            else:
                df_processed[numerical_cols] = self.scaler.transform(
                    df_processed[numerical_cols]
                )

        return df_processed

    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crea features de interacción y derivadas.

        Args:
            df: DataFrame base con features del niño y menú

        Returns:
            DataFrame con features adicionales
        """
        df_features = df.copy()

        # Features de interacción niño-menú
        if 'edad_meses' in df.columns and 'kcal_total' in df.columns:
            df_features['kcal_por_edad'] = df['kcal_total'] / (df['edad_meses'] + 1)

        if 'bmi' in df.columns and 'proteina_g' in df.columns:
            df_features['proteina_por_bmi'] = df['proteina_g'] / (df['bmi'] + 1)

        # Features de balance nutricional
        if all(col in df.columns for col in ['proteina_g', 'carbohidratos_g', 'grasas_g']):
            total_macros = df['proteina_g'] + df['carbohidratos_g'] + df['grasas_g']
            df_features['ratio_proteina'] = df['proteina_g'] / (total_macros + 1)
            df_features['ratio_carbohidratos'] = df['carbohidratos_g'] / (total_macros + 1)
            df_features['ratio_grasas'] = df['grasas_g'] / (total_macros + 1)

        # Features de diversidad (si están disponibles)
        if 'diversity_score' in df.columns:
            df_features['diversity_score_norm'] = df['diversity_score'] / df['diversity_score'].max()

        return df_features

    def fit(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        group: np.ndarray,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[np.ndarray] = None,
        group_val: Optional[np.ndarray] = None,
        num_boost_round: int = 100,
        early_stopping_rounds: int = 10,
        verbose_eval: int = 10
    ) -> 'MenuRanker':
        """
        Entrena el modelo de ranking.

        Args:
            X: Features de entrenamiento
            y: Labels de relevancia (0, 1, 2, etc.)
            group: IDs de grupo (query_id = niño + día + slot)
            X_val: Features de validación (opcional)
            y_val: Labels de validación (opcional)
            group_val: Grupos de validación (opcional)
            num_boost_round: Número de iteraciones
            early_stopping_rounds: Paradas tempranas
            verbose_eval: Frecuencia de logging

        Returns:
            self
        """
        logger.info("Iniciando entrenamiento del MenuRanker")

        # Crear features adicionales
        X_enhanced = self._create_features(X)

        # Preparar features
        X_processed = self._prepare_features(X_enhanced, fit_encoders=True)
        self.feature_names = X_processed.columns.tolist()

        # Crear dataset de LightGBM
        train_data = lgb.Dataset(
            X_processed,
            label=y,
            group=np.bincount(group),  # LightGBM espera conteos por grupo
            feature_name=self.feature_names
        )

        valid_sets = [train_data]
        valid_names = ['train']

        # Preparar validación si se proporciona
        if X_val is not None and y_val is not None and group_val is not None:
            X_val_enhanced = self._create_features(X_val)
            X_val_processed = self._prepare_features(X_val_enhanced, fit_encoders=False)

            val_data = lgb.Dataset(
                X_val_processed,
                label=y_val,
                group=np.bincount(group_val),
                reference=train_data,
                feature_name=self.feature_names
            )
            valid_sets.append(val_data)
            valid_names.append('valid')

        # Entrenar modelo
        self.model = lgb.train(
            self.params,
            train_data,
            num_boost_round=num_boost_round,
            valid_sets=valid_sets,
            valid_names=valid_names,
            callbacks=[
                lgb.early_stopping(early_stopping_rounds),
                lgb.log_evaluation(verbose_eval)
            ]
        )

        # Calcular importancia de features
        self.feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importance(importance_type='gain')
        }).sort_values('importance', ascending=False)

        logger.info(f"Entrenamiento completado. Mejor iteración: {self.model.best_iteration}")
        logger.info(f"Top 5 features: {self.feature_importance.head()['feature'].tolist()}")

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predice scores de ranking para candidatos.

        Args:
            X: Features de los candidatos

        Returns:
            Array con scores de ranking
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llama a fit() primero.")

        # Crear features adicionales
        X_enhanced = self._create_features(X)

        # Preparar features
        X_processed = self._prepare_features(X_enhanced, fit_encoders=False)

        # Asegurar que tenemos todas las features esperadas
        missing_features = set(self.feature_names) - set(X_processed.columns)
        if missing_features:
            logger.warning(f"Features faltantes: {missing_features}")
            for feature in missing_features:
                X_processed[feature] = 0

        # Reordenar columnas
        X_processed = X_processed[self.feature_names]

        # Predecir
        scores = self.model.predict(X_processed)
        return scores

    def rank_candidates(
        self,
        candidates_df: pd.DataFrame,
        group_col: str = 'query_id',
        top_k: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Rankea candidatos por grupo y retorna los top-k.

        Args:
            candidates_df: DataFrame con candidatos y features
            group_col: Columna que identifica grupos (query_id)
            top_k: Número de candidatos a retornar por grupo

        Returns:
            DataFrame con candidatos rankeados
        """
        # Predecir scores
        scores = self.predict(candidates_df.drop(columns=[group_col]))

        # Agregar scores al DataFrame
        result_df = candidates_df.copy()
        result_df['ranking_score'] = scores

        # Rankear por grupo
        result_df['rank'] = result_df.groupby(group_col)['ranking_score'].rank(
            method='dense', ascending=False
        )

        # Filtrar top-k si se especifica
        if top_k is not None:
            result_df = result_df[result_df['rank'] <= top_k]

        # Ordenar por grupo y rank
        result_df = result_df.sort_values([group_col, 'rank'])

        return result_df

    def explain_predictions(
        self,
        X: pd.DataFrame,
        max_display: int = 10
    ) -> shap.Explanation:
        """
        Explica las predicciones usando SHAP.

        Args:
            X: Features para explicar
            max_display: Número máximo de features a mostrar

        Returns:
            Objeto SHAP Explanation
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llama a fit() primero.")

        # Preparar features
        X_enhanced = self._create_features(X)
        X_processed = self._prepare_features(X_enhanced, fit_encoders=False)
        X_processed = X_processed[self.feature_names]

        # Crear explainer si no existe
        if self.explainer is None:
            self.explainer = shap.TreeExplainer(self.model)

        # Calcular valores SHAP
        shap_values = self.explainer.shap_values(X_processed)

        return shap.Explanation(
            values=shap_values,
            data=X_processed,
            feature_names=self.feature_names
        )

    def get_feature_importance(self, top_k: int = 20) -> pd.DataFrame:
        """
        Retorna la importancia de features.

        Args:
            top_k: Número de features a retornar

        Returns:
            DataFrame con importancia de features
        """
        if self.feature_importance is None:
            raise ValueError("Modelo no entrenado. Llama a fit() primero.")

        return self.feature_importance.head(top_k)

    def save(self, filepath: Union[str, Path]) -> None:
        """
        Guarda el modelo entrenado.

        Args:
            filepath: Ruta donde guardar el modelo
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llama a fit() primero.")

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Guardar modelo y metadatos
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'label_encoders': self.label_encoders,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance,
            'params': self.params
        }

        joblib.dump(model_data, filepath)
        logger.info(f"Modelo guardado en: {filepath}")

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> 'MenuRanker':
        """
        Carga un modelo entrenado.

        Args:
            filepath: Ruta del modelo guardado

        Returns:
            Instancia de MenuRanker cargada
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

        model_data = joblib.load(filepath)

        # Crear instancia
        ranker = cls(**model_data['params'])
        ranker.model = model_data['model']
        ranker.feature_names = model_data['feature_names']
        ranker.label_encoders = model_data['label_encoders']
        ranker.scaler = model_data['scaler']
        ranker.feature_importance = model_data['feature_importance']

        logger.info(f"Modelo cargado desde: {filepath}")
        return ranker


def evaluate_ranker(
    ranker: MenuRanker,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
    group_test: np.ndarray,
    k_values: List[int] = [1, 3, 5, 10]
) -> Dict[str, float]:
    """
    Evalúa el rendimiento del ranker.

    Args:
        ranker: Modelo entrenado
        X_test: Features de test
        y_test: Labels de test
        group_test: Grupos de test
        k_values: Valores de k para métricas @k

    Returns:
        Diccionario con métricas de evaluación
    """
    from sklearn.metrics import ndcg_score

    # Predecir scores
    scores = ranker.predict(X_test)

    # Calcular métricas por grupo
    unique_groups = np.unique(group_test)
    metrics = {f'ndcg@{k}': [] for k in k_values}

    for group_id in unique_groups:
        group_mask = group_test == group_id
        group_y = y_test[group_mask]
        group_scores = scores[group_mask]

        if len(group_y) > 1:  # Necesitamos al menos 2 elementos para ranking
            for k in k_values:
                if len(group_y) >= k:
                    ndcg_k = ndcg_score(
                        [group_y], [group_scores], k=k
                    )
                    metrics[f'ndcg@{k}'].append(ndcg_k)

    # Promediar métricas
    final_metrics = {}
    for metric, values in metrics.items():
        if values:
            final_metrics[metric] = np.mean(values)
        else:
            final_metrics[metric] = 0.0

    return final_metrics
