"""
Endpoints para entrenamiento del modelo de predicción nutricional.
Diseñado para ser llamado desde Google Colab.

Flujo:
1. POST /extract_csv - Extrae datos de BD y genera CSV
2. POST /train - Entrena modelo con el CSV
3. GET /metrics - Obtiene métricas del modelo entrenado
4. POST /generate_plots - Genera 5 gráficas importantes
"""

import base64
import logging
import time
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/nutritional", tags=["nutritional-training"])

# Rutas base
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
PLOTS_DIR = BASE_DIR / "plots"


# ============================================================================
# SCHEMAS
# ============================================================================


class ExtractCSVRequest(BaseModel):
    """Request para extraer CSV."""

    min_measurements: int = Field(2, description="Mínimo mediciones por niño")
    lookback_months: int = Field(24, description="Meses hacia atrás")
    include_synthetic: bool = Field(True, description="Incluir datos sintéticos")
    target_size: int = Field(180, description="Tamaño objetivo del dataset")


class ExtractCSVResponse(BaseModel):
    """Response de extracción CSV."""

    status: str
    message: str
    csv_path: Optional[str] = None
    records_count: int = 0
    class_distribution: Optional[Dict[str, int]] = None
    extraction_time_seconds: Optional[float] = None


class TrainModelRequest(BaseModel):
    """Request para entrenar modelo."""

    csv_path: Optional[str] = Field(
        None, description="Ruta al CSV (default: data/nutritional_status_training_data.csv)"
    )
    validation_split: float = Field(0.3, ge=0.1, le=0.5)
    num_boost_round: int = Field(500, ge=100, le=2000)
    early_stopping: int = Field(50, ge=10, le=200)


class TrainModelResponse(BaseModel):
    """Response del entrenamiento."""

    status: str
    message: str
    model_path: Optional[str] = None
    accuracy: Optional[float] = None
    f1_macro: Optional[float] = None
    f1_weighted: Optional[float] = None
    training_time_seconds: Optional[float] = None
    num_iterations: Optional[int] = None


class MetricsResponse(BaseModel):
    """Response de métricas."""

    status: str
    model_loaded: bool = False
    accuracy: Optional[float] = None
    f1_macro: Optional[float] = None
    f1_weighted: Optional[float] = None
    feature_importance: Optional[Dict[str, float]] = None
    class_metrics: Optional[Dict[str, Any]] = None
    confusion_matrix: Optional[List[List[int]]] = None


class GeneratePlotsRequest(BaseModel):
    """Request para generar gráficas."""

    plots_to_generate: List[str] = Field(
        default=[
            "feature_importance",
            "class_distribution",
            "confusion_matrix",
            "bmi_by_class",
            "correlation",
        ],
        description="Lista de gráficas a generar",
    )


class GeneratePlotsResponse(BaseModel):
    """Response de generación de gráficas."""

    status: str
    message: str
    plots_generated: List[str] = []
    plots_base64: Optional[Dict[str, str]] = None  # Para enviar imágenes a Colab
    plots_paths: Optional[Dict[str, str]] = None


# ============================================================================
# ENDPOINT 1: EXTRAER CSV
# ============================================================================


@router.post("/extract_csv", response_model=ExtractCSVResponse)
async def extract_csv(request: ExtractCSVRequest) -> ExtractCSVResponse:
    """
    Extrae datos de la BD y genera CSV para entrenamiento.

    Proceso:
    1. Conecta a la BD MySQL
    2. Extrae antropometrías, adherencias, síntomas
    3. Genera datos sintéticos para balancear clases
    4. Guarda CSV en data/nutritional_status_training_data.csv
    """
    import os

    from dotenv import load_dotenv

    load_dotenv()

    start_time = time.time()

    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")

        logger.info("📊 Iniciando extracción de datos...")

        from src.training.extract_nutritional_status_data import NutritionalStatusDataExtractor

        extractor = NutritionalStatusDataExtractor(db_url)
        df = extractor.extract_training_data(
            min_measurements=request.min_measurements,
            lookback_months=request.lookback_months,
            include_synthetic=request.include_synthetic,
            target_size=request.target_size,
        )

        if df.empty:
            return ExtractCSVResponse(
                status="error",
                message="No se pudieron extraer datos. Verifica que haya niños con mediciones.",
                records_count=0,
            )

        # Guardar CSV
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        csv_path = DATA_DIR / "nutritional_status_training_data.csv"
        df.to_csv(csv_path, index=False)

        # Distribución de clases
        class_dist = df["clasificacion_oms"].value_counts().to_dict()

        extraction_time = time.time() - start_time

        logger.info(f"✅ CSV generado: {len(df)} registros en {extraction_time:.1f}s")

        return ExtractCSVResponse(
            status="success",
            message=f"CSV generado exitosamente con {len(df)} registros",
            csv_path=str(csv_path),
            records_count=len(df),
            class_distribution=class_dist,
            extraction_time_seconds=extraction_time,
        )

    except Exception as e:
        logger.error(f"❌ Error extrayendo CSV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINT 2: ENTRENAR MODELO
# ============================================================================


@router.post("/train", response_model=TrainModelResponse)
async def train_model(request: TrainModelRequest) -> TrainModelResponse:
    """
    Entrena el modelo de predicción nutricional con el CSV.

    Proceso:
    1. Carga CSV de entrenamiento
    2. Prepara datos (split train/val)
    3. Entrena LightGBM multiclase
    4. Guarda modelo en models/nutritional_predictor.pkl
    """
    start_time = time.time()

    try:
        # Determinar ruta del CSV
        csv_path = (
            Path(request.csv_path)
            if request.csv_path
            else DATA_DIR / "nutritional_status_training_data.csv"
        )

        if not csv_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"CSV no encontrado: {csv_path}. Ejecuta /extract_csv primero.",
            )

        logger.info(f"🚀 Iniciando entrenamiento desde: {csv_path}")

        import pandas as pd

        from src.training.train_nutritional_predictor import NutritionalPredictorTrainer

        # Cargar datos
        df = pd.read_csv(csv_path)
        logger.info(f"   Datos cargados: {len(df)} registros")

        # Inicializar entrenador
        trainer = NutritionalPredictorTrainer()

        # Preparar datos
        train_data, val_data, X_val, y_val = trainer.prepare_data(df, request.validation_split)

        # Entrenar
        model = trainer.train(train_data, val_data, request.num_boost_round, request.early_stopping)

        # Evaluar
        metrics = trainer.evaluate(X_val, y_val)

        # Guardar modelo
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        model_path = MODELS_DIR / "nutritional_predictor.pkl"
        trainer.save_model(str(model_path), metrics)

        training_time = time.time() - start_time

        logger.info(f"✅ Modelo entrenado en {training_time:.1f}s")

        return TrainModelResponse(
            status="success",
            message="Modelo entrenado exitosamente",
            model_path=str(model_path),
            accuracy=metrics.get("accuracy"),
            f1_macro=metrics.get("f1_macro"),
            f1_weighted=metrics.get("f1_weighted"),
            training_time_seconds=training_time,
            num_iterations=model.num_trees(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error entrenando modelo: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINT 3: OBTENER MÉTRICAS
# ============================================================================


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """
    Obtiene métricas del modelo entrenado.

    Retorna:
    - Accuracy, F1-scores
    - Feature importance
    - Métricas por clase
    - Matriz de confusión
    """
    try:
        model_path = MODELS_DIR / "nutritional_predictor.pkl"

        if not model_path.exists():
            return MetricsResponse(status="error", model_loaded=False, accuracy=None)

        import joblib

        payload = joblib.load(model_path)

        metrics = payload.get("metrics", {})
        model = payload.get("model")
        feature_names = payload.get("feature_names", [])

        # Feature importance
        feature_importance = {}
        if model is not None:
            importance = model.feature_importance(importance_type="gain")
            feature_importance = {name: float(imp) for name, imp in zip(feature_names, importance)}

        return MetricsResponse(
            status="success",
            model_loaded=True,
            accuracy=metrics.get("accuracy"),
            f1_macro=metrics.get("f1_macro"),
            f1_weighted=metrics.get("f1_weighted"),
            feature_importance=feature_importance,
            class_metrics=metrics.get("classification_report"),
            confusion_matrix=metrics.get("confusion_matrix"),
        )

    except Exception as e:
        logger.error(f"❌ Error obteniendo métricas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINT 4: GENERAR GRÁFICAS
# ============================================================================


@router.post("/generate_plots", response_model=GeneratePlotsResponse)
async def generate_plots(request: GeneratePlotsRequest) -> GeneratePlotsResponse:
    """
    Genera 5 gráficas importantes del modelo.

    Gráficas disponibles:
    1. feature_importance - Importancia de features
    2. class_distribution - Distribución de clases en dataset
    3. confusion_matrix - Matriz de confusión
    4. bmi_by_class - Distribución de BMI por clase
    5. correlation - Correlación entre features

    Retorna las imágenes en base64 para mostrar en Colab.
    """
    import matplotlib

    matplotlib.use("Agg")  # Backend sin GUI
    import joblib
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns

    try:
        PLOTS_DIR.mkdir(parents=True, exist_ok=True)

        # Cargar modelo y datos
        model_path = MODELS_DIR / "nutritional_predictor.pkl"
        csv_path = DATA_DIR / "nutritional_status_training_data.csv"

        if not model_path.exists():
            raise HTTPException(status_code=404, detail="Modelo no encontrado. Entrena primero.")

        payload = joblib.load(model_path)
        model = payload.get("model")
        feature_names = payload.get("feature_names", [])
        metrics = payload.get("metrics", {})
        class_names = payload.get("class_names", [])

        df = None
        if csv_path.exists():
            df = pd.read_csv(csv_path)

        plots_generated = []
        plots_base64 = {}
        plots_paths = {}

        # Configurar estilo
        plt.style.use("seaborn-v0_8-whitegrid")

        # 1. FEATURE IMPORTANCE
        if "feature_importance" in request.plots_to_generate and model is not None:
            fig, ax = plt.subplots(figsize=(10, 6))
            importance = model.feature_importance(importance_type="gain")
            sorted_idx = np.argsort(importance)
            colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(feature_names)))

            ax.barh(range(len(feature_names)), importance[sorted_idx], color=colors[sorted_idx])
            ax.set_yticks(range(len(feature_names)))
            ax.set_yticklabels([feature_names[i] for i in sorted_idx])
            ax.set_xlabel("Importancia (Gain)", fontsize=12)
            ax.set_title(
                "Importancia de Features - Modelo Nutricional", fontsize=14, fontweight="bold"
            )
            plt.tight_layout()

            path = PLOTS_DIR / "feature_importance.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plots_base64["feature_importance"] = _fig_to_base64(fig)
            plots_paths["feature_importance"] = str(path)
            plots_generated.append("feature_importance")
            plt.close(fig)
            logger.info("   ✅ feature_importance.png")

        # 2. CLASS DISTRIBUTION
        if "class_distribution" in request.plots_to_generate and df is not None:
            fig, ax = plt.subplots(figsize=(12, 6))
            class_counts = df["clasificacion_oms"].value_counts()
            colors = ["#d62728", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#1f77b4", "#9467bd"]

            bars = ax.bar(
                range(len(class_counts)), class_counts.values, color=colors[: len(class_counts)]
            )
            ax.set_xticks(range(len(class_counts)))
            ax.set_xticklabels(class_counts.index, rotation=45, ha="right")
            ax.set_ylabel("Cantidad", fontsize=12)
            ax.set_title("Distribución de Clases en Dataset", fontsize=14, fontweight="bold")

            for bar, count in zip(bars, class_counts.values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 1,
                    str(count),
                    ha="center",
                    va="bottom",
                    fontsize=10,
                )
            plt.tight_layout()

            path = PLOTS_DIR / "class_distribution.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plots_base64["class_distribution"] = _fig_to_base64(fig)
            plots_paths["class_distribution"] = str(path)
            plots_generated.append("class_distribution")
            plt.close(fig)
            logger.info("   ✅ class_distribution.png")

        # 3. CONFUSION MATRIX
        if "confusion_matrix" in request.plots_to_generate and metrics.get("confusion_matrix"):
            fig, ax = plt.subplots(figsize=(10, 8))
            cm = np.array(metrics["confusion_matrix"])

            # Usar solo las clases presentes
            n_classes = cm.shape[0]
            labels = (
                class_names[:n_classes] if class_names else [f"Clase {i}" for i in range(n_classes)]
            )

            sns.heatmap(
                cm, annot=True, fmt="d", cmap="Blues", ax=ax, xticklabels=labels, yticklabels=labels
            )
            ax.set_xlabel("Predicción", fontsize=12)
            ax.set_ylabel("Real", fontsize=12)
            ax.set_title("Matriz de Confusión", fontsize=14, fontweight="bold")
            plt.tight_layout()

            path = PLOTS_DIR / "confusion_matrix.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plots_base64["confusion_matrix"] = _fig_to_base64(fig)
            plots_paths["confusion_matrix"] = str(path)
            plots_generated.append("confusion_matrix")
            plt.close(fig)
            logger.info("   ✅ confusion_matrix.png")

        # 4. BMI BY CLASS
        if "bmi_by_class" in request.plots_to_generate and df is not None:
            fig, ax = plt.subplots(figsize=(12, 6))
            order = [
                "DESNUTRICION_SEVERA",
                "DESNUTRICION_MODERADA",
                "RIESGO_DESNUTRICION",
                "NORMAL",
                "RIESGO_SOBREPESO",
                "SOBREPESO",
                "OBESIDAD",
            ]
            order = [c for c in order if c in df["clasificacion_oms"].unique()]

            sns.boxplot(
                data=df, x="clasificacion_oms", y="BMI", order=order, ax=ax, palette="coolwarm"
            )
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
            ax.set_xlabel("Clasificación OMS", fontsize=12)
            ax.set_ylabel("IMC (kg/m²)", fontsize=12)
            ax.set_title("Distribución de IMC por Clasificación", fontsize=14, fontweight="bold")
            plt.tight_layout()

            path = PLOTS_DIR / "bmi_by_class.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plots_base64["bmi_by_class"] = _fig_to_base64(fig)
            plots_paths["bmi_by_class"] = str(path)
            plots_generated.append("bmi_by_class")
            plt.close(fig)
            logger.info("   ✅ bmi_by_class.png")

        # 5. CORRELATION
        if "correlation" in request.plots_to_generate and df is not None:
            fig, ax = plt.subplots(figsize=(10, 8))
            numeric_cols = [c for c in feature_names if c in df.columns]
            corr_matrix = df[numeric_cols].corr()

            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
            sns.heatmap(
                corr_matrix,
                mask=mask,
                annot=True,
                fmt=".2f",
                cmap="RdBu_r",
                center=0,
                ax=ax,
                square=True,
                linewidths=0.5,
            )
            ax.set_title("Correlación entre Features", fontsize=14, fontweight="bold")
            plt.tight_layout()

            path = PLOTS_DIR / "correlation.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plots_base64["correlation"] = _fig_to_base64(fig)
            plots_paths["correlation"] = str(path)
            plots_generated.append("correlation")
            plt.close(fig)
            logger.info("   ✅ correlation.png")

        logger.info(f"✅ Generadas {len(plots_generated)} gráficas")

        return GeneratePlotsResponse(
            status="success",
            message=f"Generadas {len(plots_generated)} gráficas",
            plots_generated=plots_generated,
            plots_base64=plots_base64,
            plots_paths=plots_paths,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando gráficas: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


def _fig_to_base64(fig) -> str:
    """Convierte figura matplotlib a base64."""
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


# ============================================================================
# ENDPOINTS AUXILIARES
# ============================================================================


@router.get("/download_csv")
async def download_csv():
    """Descarga el CSV de entrenamiento."""
    csv_path = DATA_DIR / "nutritional_status_training_data.csv"
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="CSV no encontrado")
    return FileResponse(csv_path, filename="nutritional_training_data.csv")


@router.get("/download_model")
async def download_model():
    """Descarga el modelo entrenado."""
    model_path = MODELS_DIR / "nutritional_predictor.pkl"
    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Modelo no encontrado")
    return FileResponse(model_path, filename="nutritional_predictor.pkl")


@router.get("/download_plot/{plot_name}")
async def download_plot(plot_name: str):
    """Descarga una gráfica específica."""
    plot_path = PLOTS_DIR / f"{plot_name}.png"
    if not plot_path.exists():
        raise HTTPException(status_code=404, detail=f"Gráfica {plot_name} no encontrada")
    return FileResponse(plot_path, filename=f"{plot_name}.png")


@router.get("/status")
async def get_status():
    """Estado del sistema de entrenamiento."""
    csv_exists = (DATA_DIR / "nutritional_status_training_data.csv").exists()
    model_exists = (MODELS_DIR / "nutritional_predictor.pkl").exists()

    csv_records = 0
    if csv_exists:
        import pandas as pd

        df = pd.read_csv(DATA_DIR / "nutritional_status_training_data.csv")
        csv_records = len(df)

    plots_available = [p.stem for p in PLOTS_DIR.glob("*.png")] if PLOTS_DIR.exists() else []

    return {
        "status": "ok",
        "csv_exists": csv_exists,
        "csv_records": csv_records,
        "model_exists": model_exists,
        "plots_available": plots_available,
        "paths": {
            "data_dir": str(DATA_DIR),
            "models_dir": str(MODELS_DIR),
            "plots_dir": str(PLOTS_DIR),
        },
    }
