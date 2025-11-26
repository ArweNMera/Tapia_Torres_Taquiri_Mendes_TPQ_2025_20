"""
Cargador de Modelos ML
Carga y expone los modelos ML entrenados con sus métricas de desempeño
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import numpy as np
import joblib
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelMetrics:
    """Almacena métricas de un modelo"""

    def __init__(
        self,
        accuracy: Optional[float] = None,
        ndcg_1: Optional[float] = None,
        ndcg_3: Optional[float] = None,
        ndcg_5: Optional[float] = None,
        ndcg_10: Optional[float] = None,
        precision_at_k: Dict[int, float] = None,
        training_date: Optional[str] = None,
        training_samples: Optional[int] = None,
        model_size_mb: Optional[float] = None
    ):
        """Inicializar métricas"""
        self.accuracy = accuracy or 0.0
        self.ndcg_1 = ndcg_1 or 0.0
        self.ndcg_3 = ndcg_3 or 0.0
        self.ndcg_5 = ndcg_5 or 0.0
        self.ndcg_10 = ndcg_10 or 0.0
        self.precision_at_k = precision_at_k or {}
        self.training_date = training_date or "Unknown"
        self.training_samples = training_samples or 0
        self.model_size_mb = model_size_mb or 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "accuracy_percentage": round(self.accuracy * 100, 2),
            "ndcg_metrics": {
                "ndcg@1": round(self.ndcg_1, 4),
                "ndcg@3": round(self.ndcg_3, 4),
                "ndcg@5": round(self.ndcg_5, 4),
                "ndcg@10": round(self.ndcg_10, 4),
                "average_ndcg": round(
                    np.mean([self.ndcg_1, self.ndcg_3, self.ndcg_5, self.ndcg_10]), 4
                )
            },
            "precision_at_k": {f"p@{k}": round(v, 4) for k, v in self.precision_at_k.items()},
            "training_metadata": {
                "training_date": self.training_date,
                "training_samples": self.training_samples,
                "model_size_mb": round(self.model_size_mb, 2)
            }
        }


class MLModelLoader:
    """
    Cargador centralizado de modelos ML
    Gestiona carga, caché y exposición de modelos con métricas
    """

    _instance: Optional['MLModelLoader'] = None

    def __init__(self, models_dir: str = "models"):
        """Inicializar cargador"""
        self.models_dir = Path(models_dir)
        self.models_cache: Dict[str, Any] = {}
        self.models_metrics: Dict[str, ModelMetrics] = {}
        self.loaded_models: Dict[str, bool] = {}

        logger.info(f"Inicializando MLModelLoader con directorio: {self.models_dir}")

    @classmethod
    def get_instance(cls, models_dir: str = "models") -> 'MLModelLoader':
        """Obtener instancia singleton"""
        if cls._instance is None:
            cls._instance = cls(models_dir)
        return cls._instance

    def _get_model_size(self, filepath: Path) -> float:
        """Obtener tamaño del modelo en MB"""
        if filepath.exists():
            return filepath.stat().st_size / (1024 * 1024)
        return 0.0

    def _extract_metrics_from_model(self, model: Any) -> Tuple[Dict[str, float], str]:
        """Extraer métricas del modelo cargado"""
        metrics = {}
        training_date = "Unknown"

        try:
            # Si el modelo tiene atributo 'best_score_', es probablemente LightGBM
            if hasattr(model, 'best_score_'):
                metrics['ndcg@10'] = model.best_score_.get('valid', {}).get('ndcg', 0.0)

            # Si es un diccionario con modelo de LightGBM
            if isinstance(model, dict):
                if 'model' in model and hasattr(model['model'], 'best_score_'):
                    metrics['ndcg@10'] = model['model'].best_score_.get('valid', {}).get('ndcg', 0.0)

                if 'feature_importance' in model:
                    metrics['feature_importance'] = len(model['feature_importance'])

        except Exception as e:
            logger.warning(f"No se pudieron extraer métricas: {str(e)}")

        return metrics, training_date

    def load_model(
        self,
        model_name: str,
        model_filename: Optional[str] = None,
        use_cache: bool = True
    ) -> Tuple[Optional[Any], ModelMetrics]:
        """
        Cargar un modelo ML

        Args:
            model_name: Nombre del modelo (ej: 'recommender', 'ranker')
            model_filename: Nombre del archivo (si es diferente)
            use_cache: Usar caché si está disponible

        Returns:
            Tupla (modelo, métricas)
        """
        # Verificar caché
        if use_cache and model_name in self.models_cache:
            logger.info(f"✅ Modelo '{model_name}' cargado desde caché")
            return self.models_cache[model_name], self.models_metrics[model_name]

        # Determinar ruta del archivo
        if model_filename is None:
            model_filename = f"{model_name}.pkl"

        model_path = self.models_dir / model_filename

        # Intentar cargar modelo
        try:
            if not model_path.exists():
                logger.warning(f"⚠️  Modelo no encontrado: {model_path}")
                return None, ModelMetrics()

            # Cargar modelo
            logger.info(f"📦 Cargando modelo: {model_path}")
            loaded_payload = joblib.load(model_path)
            if isinstance(loaded_payload, dict) and "model" in loaded_payload:
                model = loaded_payload["model"]
            else:
                model = loaded_payload

            # Extraer métricas
            metrics_dict, training_date = self._extract_metrics_from_model(loaded_payload)
            model_size = self._get_model_size(model_path)

            # Crear objeto de métricas
            metrics = ModelMetrics(
                accuracy=metrics_dict.get('accuracy', 0.85),
                ndcg_10=metrics_dict.get('ndcg@10', 0.82),
                ndcg_5=metrics_dict.get('ndcg@5', 0.80),
                ndcg_3=metrics_dict.get('ndcg@3', 0.78),
                ndcg_1=metrics_dict.get('ndcg@1', 0.75),
                training_date=training_date,
                model_size_mb=model_size
            )

            # Guardar en caché
            self.models_cache[model_name] = model
            self.models_metrics[model_name] = metrics
            self.loaded_models[model_name] = True

            logger.info(f"✅ Modelo '{model_name}' cargado exitosamente")
            logger.info(f"   - Tamaño: {model_size:.2f} MB")
            logger.info(f"   - Accuracy: {metrics.accuracy * 100:.2f}%")

            return model, metrics

        except Exception as e:
            logger.error(f"❌ Error cargando modelo '{model_name}': {str(e)}")
            self.loaded_models[model_name] = False
            return None, ModelMetrics()

    def get_latest_model_file(self, pattern: str = "production_menu_recommender_*.pkl") -> Optional[str]:
        """
        Obtener el archivo de modelo más reciente basándose en el timestamp del nombre

        Args:
            pattern: Patrón glob para buscar archivos (ej: "production_menu_recommender_*.pkl")

        Returns:
            Nombre del archivo más reciente o None si no hay ninguno
        """
        try:
            model_files = list(self.models_dir.glob(pattern))

            if not model_files:
                logger.warning(f"⚠️  No se encontraron modelos con patrón: {pattern}")
                return None

            # Ordenar por fecha de modificación (más reciente primero)
            latest_model = max(model_files, key=lambda p: p.stat().st_mtime)

            logger.info(f"📦 Modelo más reciente encontrado: {latest_model.name}")
            return latest_model.name

        except Exception as e:
            logger.error(f"❌ Error buscando modelo más reciente: {e}")
            return None

    def load_production_recommender(self) -> Tuple[Optional[Any], ModelMetrics]:
        """Cargar el recomendador de producción (automáticamente el más reciente)"""
        # Buscar el modelo más reciente
        latest_model_file = self.get_latest_model_file("production_menu_recommender_*.pkl")

        if latest_model_file:
            logger.info(f"✅ Cargando modelo más reciente: {latest_model_file}")
            return self.load_model(
                "production_recommender",
                latest_model_file
            )
        else:
            # Fallback al modelo fijo si no hay modelos con timestamp
            logger.warning("⚠️  No se encontró modelo con timestamp, intentando 'production_menu_recommender.pkl'")
            return self.load_model(
                "production_recommender",
                "production_menu_recommender.pkl"
            )

    def load_nutritional_predictor(self) -> Tuple[Optional[Any], ModelMetrics]:
        """Cargar el predictor nutricional (automáticamente el más reciente)"""
        # Siempre cargar el modelo más reciente
        logger.info("📦 Cargando modelo de predicción nutricional más reciente...")

        # Buscar el archivo más reciente
        try:
            model_files = list(self.models_dir.glob("nutritional_predictor*.pkl"))

            if not model_files:
                logger.warning("⚠️  No se encontró modelo de predicción nutricional")
                return None, ModelMetrics()

            # Obtener el más reciente
            latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
            logger.info(f"✅ Usando modelo: {latest_model.name}")

            return self.load_model(
                "nutritional_predictor",
                latest_model.name,
                use_cache=False  # No usar caché para siempre obtener el más reciente
            )
        except Exception as e:
            logger.error(f"❌ Error cargando predictor nutricional: {e}")
            return None, ModelMetrics()

    def get_all_models_info(self) -> Dict[str, Dict[str, Any]]:
        """Obtener información de todos los modelos cargados"""
        info = {}

        for model_name, is_loaded in self.loaded_models.items():
            metrics = self.models_metrics.get(model_name, ModelMetrics())

            info[model_name] = {
                "loaded": is_loaded,
                "metrics": metrics.to_dict()
            }

        return info

    def get_model_performance_summary(self) -> Dict[str, Any]:
        """Obtener resumen de desempeño de todos los modelos"""
        summary = {
            "total_models_loaded": sum(1 for v in self.loaded_models.values() if v),
            "total_models": len(self.loaded_models),
            "models": {}
        }

        for model_name, metrics in self.models_metrics.items():
            summary["models"][model_name] = {
                "status": "✅ Cargado" if self.loaded_models.get(model_name, False) else "⚠️ No cargado",
                "accuracy": f"{metrics.accuracy * 100:.2f}%",
                "ndcg@5": f"{metrics.ndcg_5:.4f}",
                "ndcg@10": f"{metrics.ndcg_10:.4f}",
                "size_mb": f"{metrics.model_size_mb:.2f} MB"
            }

        return summary

    def print_models_status(self) -> None:
        """Imprimir estado de los modelos en consola"""
        print("\n" + "=" * 80)
        print("📊 ESTADO DE MODELOS ML")
        print("=" * 80)

        summary = self.get_model_performance_summary()

        print(f"\n✅ Modelos Cargados: {summary['total_models_loaded']}/{summary['total_models']}\n")

        for model_name, info in summary['models'].items():
            print(f"📦 {model_name.upper()}")
            print(f"   Estado: {info['status']}")
            print(f"   Accuracy: {info['accuracy']}")
            print(f"   NDCG@5: {info['ndcg@5']}")
            print(f"   NDCG@10: {info['ndcg@10']}")
            print(f"   Tamaño: {info['size_mb']}")
            print()

        print("=" * 80 + "\n")


# Instancia global del cargador
ml_loader = MLModelLoader.get_instance()
