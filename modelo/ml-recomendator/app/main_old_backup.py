from __future__ import annotations

import math
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from src.llm.assist import format_recommender_prompt, summarize_with_llm
except Exception:
    summarize_with_llm = None
    format_recommender_prompt = None
try:
    from src.llm.client import get_llm_client
except Exception:
    get_llm_client = None

# Importar modelo ML
try:
    from src.models import RandomForestNutritionClassifier
    from src.utils import DatabaseConnector
except Exception as e:
    print(f"⚠️  Error importando modelos ML: {e}")
    RandomForestNutritionClassifier = None
    DatabaseConnector = None


app = FastAPI(title="ml-recomendator", version="0.1.0")

allowed = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Limpiar nombres de columnas (quitar comillas, espacios, etc.)
    df.columns = df.columns.str.strip().str.replace('"', "").str.replace("'", "")

    # Normalizar nombres de columnas
    cols = {c: c.strip().replace(" ", "_") for c in df.columns}
    df = df.rename(columns=cols)

    # Mapear variaciones de nombres de columnas a nombres estándar
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower()
        if col_lower in ["month", "months", "age", "edad"]:
            column_mapping[col] = "month"
        elif col_lower in ["l"]:
            column_mapping[col] = "L"
        elif col_lower in ["m"]:
            column_mapping[col] = "M"
        elif col_lower in ["s"]:
            column_mapping[col] = "S"

    if column_mapping:
        df = df.rename(columns=column_mapping)

    return df


def _lms_cat(who_dir: Path, sex: str) -> pd.DataFrame:
    parts = []
    if sex == "M":
        patterns = [
            "bmi_boys_0-to-2-years_zcores_1.csv",
            "bmi_boys_2-to-5-years_zscores.csv",
            "bmifa-boys-5-19years-z.csv",
        ]
    else:
        patterns = [
            "tab_bmi_girls_p_0_2.csv",
            "tab_bmi_girls_p_2_5.csv",
            "bmifa-girls-5-19years-z.csv",
        ]
    for pat in patterns:
        p = who_dir / pat
        if p.exists():
            df = _load_table(p)
            # Verificar que tenemos las columnas necesarias
            required_cols = ["month", "L", "M", "S"]
            if all(col in df.columns for col in required_cols):
                parts.append(df[required_cols].assign(sex=sex))
            else:
                print(
                    f"⚠️  Archivo {pat} no tiene todas las columnas requeridas. Columnas: {df.columns.tolist()}"
                )
    if not parts:
        raise FileNotFoundError(f"No WHO LMS tables found for sex={sex} under {who_dir}")
    out = pd.concat(parts, ignore_index=True)
    out["month"] = out["month"].astype(int)
    return (
        out.drop_duplicates(subset=["sex", "month"])
        .sort_values(["sex", "month"])
        .reset_index(drop=True)
    )


def _load_lms_from_db() -> pd.DataFrame:
    """Carga tablas LMS desde la base de datos MySQL."""
    try:
        if DatabaseConnector is None:
            raise Exception("DatabaseConnector no disponible")

        db = DatabaseConnector.from_env()
        db.connect()

        # Consultar tabla oms_bmi_lms
        query = """
        SELECT
            sexo as sex,
            edad_meses as month,
            L,
            M,
            S
        FROM oms_bmi_lms
        WHERE version = 'OMS_2007'
        ORDER BY sexo, edad_meses
        """

        df = db.execute_query(query)
        db.disconnect()

        if df.empty:
            raise Exception("No se encontraron datos en oms_bmi_lms")

        print(f"✅ Tablas OMS cargadas desde BD: {len(df)} registros (0-{df['month'].max()} meses)")
        return df

    except Exception as e:
        print(f"⚠️  Error cargando desde BD: {e}, intentando archivos CSV...")
        return _load_lms_from_files(WHO_DIR)


def _load_lms_from_files(who_dir: Path) -> pd.DataFrame:
    """Carga tablas LMS desde archivos CSV (fallback)."""
    return pd.concat([_lms_cat(who_dir, "M"), _lms_cat(who_dir, "F")], ignore_index=True)


def _load_lms(who_dir: Path) -> pd.DataFrame:
    """Carga tablas LMS (primero intenta BD, luego archivos)."""
    try:
        return _load_lms_from_db()
    except Exception as e:
        print(f"⚠️  No se pudo cargar desde BD: {e}")
        return _load_lms_from_files(who_dir)


def _baz_from_bmi(bmi: float, L: float, M: float, S: float) -> float:
    if L == 0:
        return math.log(bmi / M) / S
    return ((bmi / M) ** L - 1) / (L * S)


def _nearest_lms(df: pd.DataFrame, sex: str, month: int) -> tuple[float, float, float]:
    d = df[df["sex"] == sex]
    if d.empty:
        raise ValueError(f"Sex {sex} not in LMS table")
    row = d[d["month"] == month]
    if not row.empty:
        r = row.iloc[0]
        return float(r["L"]), float(r["M"]), float(r["S"])
    nearest = d.iloc[(d["month"] - month).abs().argsort().iloc[0]]
    return float(nearest["L"]), float(nearest["M"]), float(nearest["S"])


WHO_DIR = Path(os.getenv("WHO_DIR", BASE_DIR / "data/raw/who"))
try:
    LMS = _load_lms(WHO_DIR)
except Exception:
    LMS = None

# Cargar modelo ML al iniciar
ML_MODEL = None
MODEL_PATH = BASE_DIR / "models/rf_model.pkl"


def load_ml_model():
    """Carga el modelo Random Forest entrenado."""
    global ML_MODEL
    if RandomForestNutritionClassifier is None:
        print("⚠️  RandomForestNutritionClassifier no disponible")
        return

    if not MODEL_PATH.exists():
        print(f"⚠️  Modelo no encontrado en: {MODEL_PATH}")
        return

    try:
        ML_MODEL = RandomForestNutritionClassifier()
        ML_MODEL.load(MODEL_PATH)
        print(f"✅ Modelo ML cargado desde: {MODEL_PATH}")
        print(f"   Features: {ML_MODEL.feature_names}")
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        ML_MODEL = None


# Cargar modelo al iniciar
load_ml_model()


@app.get("/health")
def health():
    return {"status": "ok", "ml_model_loaded": ML_MODEL is not None, "lms_loaded": LMS is not None}


class PredictBAZRequest(BaseModel):
    age_months: int
    sex: str = Field(description="M/F")
    BMI: float | None = None
    weight_kg: float | None = None
    height_cm: float | None = None
    prefer_llm: bool = True
    features: dict[str, Any] = Field(
        default_factory=dict, description="Optional context for summary"
    )


class PredictBAZResponse(BaseModel):
    bmi: float
    baz: float
    label_status: int
    label_text: str
    summary: str
    used_llm: bool


def _classify_from_baz(z: float) -> int:
    """
    Clasifica según BAZ usando 7 categorías OMS.
    0=DESNUTRICION_SEVERA, 1=DESNUTRICION_MODERADA, 2=RIESGO_DESNUTRICION,
    3=NORMAL, 4=RIESGO_SOBREPESO, 5=SOBREPESO, 6=OBESIDAD
    """
    if z < -3.0:
        return 0  # DESNUTRICION_SEVERA
    elif -3.0 <= z < -2.0:
        return 1  # DESNUTRICION_MODERADA
    elif -2.0 <= z < -1.0:
        return 2  # RIESGO_DESNUTRICION
    elif -1.0 <= z <= 1.0:
        return 3  # NORMAL
    elif 1.0 < z <= 2.0:
        return 4  # RIESGO_SOBREPESO
    elif 2.0 < z <= 3.0:
        return 5  # SOBREPESO
    else:  # z > 3.0
        return 6  # OBESIDAD


@app.post("/ml/predict_baz", response_model=PredictBAZResponse)
def predict_baz(req: PredictBAZRequest) -> PredictBAZResponse:
    global LMS
    if LMS is None:
        LMS = _load_lms(WHO_DIR)
    sex = str(req.sex).strip().upper()[0]
    if req.BMI is not None:
        bmi = float(req.BMI)
    else:
        if req.weight_kg is None or req.height_cm is None:
            raise HTTPException(status_code=400, detail="Provide BMI or weight_kg and height_cm")
        h_m = float(req.height_cm) / 100.0
        if h_m <= 0:
            raise HTTPException(status_code=400, detail="height_cm must be > 0")
        bmi = float(req.weight_kg) / (h_m**2)
    L, M, S = _nearest_lms(LMS, sex, int(round(req.age_months)))
    baz = _baz_from_bmi(bmi, L, M, S)
    label = _classify_from_baz(baz)

    # Mapeo de 7 categorías OMS
    label_map = {
        0: "DESNUTRICION_SEVERA",
        1: "DESNUTRICION_MODERADA",
        2: "RIESGO_DESNUTRICION",
        3: "NORMAL",
        4: "RIESGO_SOBREPESO",
        5: "SOBREPESO",
        6: "OBESIDAD",
    }

    # Scores según categoría
    if baz < -3:
        scores = {"DESNUTRICION_SEVERA": 0.9, "DESNUTRICION_MODERADA": 0.1}
    elif -3 <= baz < -2:
        scores = {"DESNUTRICION_MODERADA": 0.8, "RIESGO_DESNUTRICION": 0.2}
    elif -2 <= baz < -1:
        scores = {"RIESGO_DESNUTRICION": 0.8, "NORMAL": 0.2}
    elif -1 <= baz <= 1:
        scores = {"NORMAL": 0.9, "RIESGO_DESNUTRICION": 0.05, "RIESGO_SOBREPESO": 0.05}
    elif 1 < baz <= 2:
        scores = {"RIESGO_SOBREPESO": 0.8, "NORMAL": 0.2}
    elif 2 < baz <= 3:
        scores = {"SOBREPESO": 0.8, "RIESGO_SOBREPESO": 0.2}
    else:  # baz > 3
        scores = {"OBESIDAD": 0.9, "SOBREPESO": 0.1}

    used_llm = False
    summary: str | None = None
    if req.prefer_llm and summarize_with_llm is not None:
        try:
            base_features = {
                "age_months": req.age_months,
                "sex": sex,
                "BMI": round(bmi, 2),
                **(req.features or {}),
            }
            summary = summarize_with_llm(base_features, scores)
            used_llm = summary is not None
        except Exception:
            summary = None
            used_llm = False
    if not summary:
        if format_recommender_prompt is not None:
            base_features = {
                "age_months": req.age_months,
                "sex": sex,
                "BMI": round(bmi, 2),
                **(req.features or {}),
            }
            summary = format_recommender_prompt(base_features, scores)
        else:
            summary = f"Clase: {label_map[label]} (baz={baz:.2f})."

    return PredictBAZResponse(
        bmi=round(bmi, 2),
        baz=round(baz, 2),
        label_status=label,
        label_text=label_map[label],
        summary=summary,
        used_llm=used_llm,
    )


class SummaryRequest(BaseModel):
    features: dict[str, Any]
    scores: dict[str, float]
    prefer_llm: bool = True


class SummaryResponse(BaseModel):
    text: str
    used_llm: bool


@app.post("/ml/summary", response_model=SummaryResponse)
def summarize(req: SummaryRequest) -> SummaryResponse:
    used_llm = False
    text: str | None = None
    if req.prefer_llm and summarize_with_llm is not None:
        try:
            text = summarize_with_llm(req.features, req.scores)
            used_llm = text is not None
        except Exception:
            text = None
            used_llm = False
    if not text:
        if format_recommender_prompt is not None:
            text = format_recommender_prompt(req.features, req.scores)
        else:
            top = sorted(req.scores.items(), key=lambda kv: kv[1], reverse=True)
            text = f"Mejor clase: {top[0][0]} ({top[0][1]:.2%})" if top else "Sin puntuaciones"
    return SummaryResponse(text=text, used_llm=used_llm)


class ChatRequest(BaseModel):
    message: str
    system: str | None = Field(
        default=(
            "Eres un asistente que explica y responde de forma clara, " "sin emitir consejo médico."
        )
    )


class ChatResponse(BaseModel):
    reply: str
    used_llm: bool


@app.post("/ml/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if get_llm_client is not None:
        try:
            client = get_llm_client()
            reply = client.chat(system_message=req.system or "", user_message=req.message)
            if reply:
                return ChatResponse(reply=reply, used_llm=True)
        except Exception:
            pass
    echo = f"[offline] Sin LLM configurado. Eco: {req.message}"
    return ChatResponse(reply=echo, used_llm=False)


# ============================================================================
# ENDPOINTS PARA MODELO ML (Random Forest)
# ============================================================================


class PredictMLRequest(BaseModel):
    """Request para predicción con modelo ML."""

    nin_id: int = Field(description="ID del niño")


class PredictMLResponse(BaseModel):
    """Response de predicción ML."""

    nin_id: int
    prediction: int  # 0-6: Ver classification_mapper.py para mapeo completo
    label: str  # DESNUTRICION_SEVERA, DESNUTRICION_MODERADA, etc.
    probability: float
    probabilities: dict[str, float]
    risk_score: float
    features_used: dict[str, float]
    model_version: str


@app.post("/ml/predict", response_model=PredictMLResponse)
def predict_ml(req: PredictMLRequest) -> PredictMLResponse:
    """
    Predice el estado nutricional usando el modelo Random Forest.

    Obtiene datos del niño desde la BD y hace predicción.
    """
    if ML_MODEL is None:
        raise HTTPException(
            status_code=503,
            detail="Modelo ML no disponible. Ejecuta: python src/pipeline/train_model.py",
        )

    if DatabaseConnector is None:
        raise HTTPException(status_code=503, detail="DatabaseConnector no disponible")

    # Conectar a BD y obtener datos
    try:
        db = DatabaseConnector.from_env()
        db.connect()

        # Obtener datos del niño usando procedimiento almacenado
        df = db.get_child_data(req.nin_id)

        if df.empty:
            raise HTTPException(
                status_code=404, detail=f"No se encontraron datos para nin_id={req.nin_id}"
            )

        # Preparar features
        feature_cols = ML_MODEL.feature_names

        # Convertir sex a sex_numeric si es necesario
        if "sex_numeric" in feature_cols and "nin_sexo" in df.columns:
            df["sex_numeric"] = df["nin_sexo"].map({"M": 1, "F": 0})

        # Verificar que todos los features existen
        missing_features = [f for f in feature_cols if f not in df.columns]
        if missing_features:
            raise HTTPException(status_code=400, detail=f"Features faltantes: {missing_features}")

        X = df[feature_cols].iloc[0:1]  # Primera fila como DataFrame

        # Hacer predicción
        result = ML_MODEL.predict_with_metadata(X)
        pred = result["predictions"][0]

        # Extraer features usados
        features_dict = X.iloc[0].to_dict()

        db.disconnect()

        return PredictMLResponse(
            nin_id=req.nin_id,
            prediction=pred["prediction"],
            label=pred["label"],
            probability=pred["probability"],
            probabilities=pred["probabilities"],
            risk_score=pred["risk_score"],
            features_used=features_dict,
            model_version=ML_MODEL.version,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


class PredictMLDirectRequest(BaseModel):
    """Request para predicción directa (sin BD)."""

    age_months: int
    sex: str = Field(description="M o F")
    BMI: float
    baz: float
    bmi_velocity: float = 0.0
    weight_velocity: float = 0.0
    height_velocity: float = 0.0
    allergy_count: int = 0
    adherence_score: float = 75.0
    symptom_frequency: int = 0
    dietary_diversity_score: float = 60.0
    altitude_m: float = 0.0


@app.post("/ml/predict_direct", response_model=PredictMLResponse)
def predict_ml_direct(req: PredictMLDirectRequest) -> PredictMLResponse:
    """
    Predice el estado nutricional directamente con features proporcionados.

    No requiere conexión a BD. Útil para testing o integración externa.
    """
    if ML_MODEL is None:
        raise HTTPException(status_code=503, detail="Modelo ML no disponible")

    try:
        # Convertir sex a numeric
        sex_numeric = 1 if req.sex.upper() == "M" else 0

        # Crear DataFrame con features
        data = {
            "age_months": [req.age_months],
            "sex_numeric": [sex_numeric],
            "BMI": [req.BMI],
            "baz": [req.baz],
            "bmi_velocity": [req.bmi_velocity],
            "weight_velocity": [req.weight_velocity],
            "height_velocity": [req.height_velocity],
            "allergy_count": [req.allergy_count],
            "adherence_score": [req.adherence_score],
            "symptom_frequency": [req.symptom_frequency],
            "dietary_diversity_score": [req.dietary_diversity_score],
            "altitude_m": [req.altitude_m],
        }

        X = pd.DataFrame(data)

        # Asegurar que tenemos todos los features del modelo
        for feature in ML_MODEL.feature_names:
            if feature not in X.columns:
                X[feature] = 0.0

        X = X[ML_MODEL.feature_names]

        # Hacer predicción
        result = ML_MODEL.predict_with_metadata(X)
        pred = result["predictions"][0]

        # Extraer features usados
        features_dict = X.iloc[0].to_dict()

        return PredictMLResponse(
            nin_id=0,  # No hay nin_id en predicción directa
            prediction=pred["prediction"],
            label=pred["label"],
            probability=pred["probability"],
            probabilities=pred["probabilities"],
            risk_score=pred["risk_score"],
            features_used=features_dict,
            model_version=ML_MODEL.version,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@app.get("/ml/model_info")
def model_info():
    """Información sobre el modelo cargado."""
    if ML_MODEL is None:
        return {"loaded": False, "message": "Modelo no cargado"}

    return {
        "loaded": True,
        "model_name": ML_MODEL.model_name,
        "version": ML_MODEL.version,
        "is_trained": ML_MODEL.is_trained,
        "features": ML_MODEL.feature_names,
        "n_features": len(ML_MODEL.feature_names),
        "feature_importance": ML_MODEL.get_feature_importance(),
        "model_path": str(MODEL_PATH),
    }


# ============================================================================
# ENDPOINT PARA REEMPLAZAR PROCEDIMIENTOS ALMACENADOS
# ============================================================================


class AnalisisNutricionalRequest(BaseModel):
    """Request para análisis nutricional completo (reemplaza procedimientos)."""

    nin_id: int = Field(description="ID del niño")
    peso_kg: float = Field(description="Peso en kg")
    talla_cm: float = Field(description="Talla en cm")
    fecha_medicion: str | None = Field(None, description="Fecha de medición (YYYY-MM-DD)")


class RecomendacionNutricional(BaseModel):
    """Recomendación nutricional."""

    icono: str
    titulo: str
    descripcion: str


class AnalisisNutricionalResponse(BaseModel):
    """Response completo de análisis nutricional."""

    # Medición
    fecha: str
    peso_kg: float
    talla_cm: float
    imc: float

    # Estado nutricional
    diagnostico: str  # 7 categorías OMS: DESNUTRICION_SEVERA, DESNUTRICION_MODERADA, RIESGO_DESNUTRICION, NORMAL, RIESGO_SOBREPESO, SOBREPESO, OBESIDAD
    imc_valor: float
    percentil: float
    nivel_riesgo: str  # BAJO, MEDIO, ALTO
    baz: float

    # Probabilidades del modelo
    probabilidad: float
    probabilidades: dict[str, float]

    # Recomendaciones
    recomendaciones: list[RecomendacionNutricional]

    # Metadata
    modelo_usado: bool
    modelo_version: str


@app.post("/ml/analisis_nutricional", response_model=AnalisisNutricionalResponse)
def analisis_nutricional(req: AnalisisNutricionalRequest) -> AnalisisNutricionalResponse:
    """
    Análisis nutricional completo (reemplaza procedimientos almacenados).

    Este endpoint:
    1. Calcula BMI y BAZ usando tablas OMS
    2. Calcula features ML desde la BD
    3. Hace predicción con modelo Random Forest
    4. Genera recomendaciones personalizadas
    5. Retorna análisis completo para el frontend
    """
    if ML_MODEL is None:
        raise HTTPException(status_code=503, detail="Modelo ML no disponible")

    if DatabaseConnector is None:
        raise HTTPException(status_code=503, detail="DatabaseConnector no disponible")

    try:
        # 1. Calcular BMI
        altura_m = req.talla_cm / 100.0
        if altura_m <= 0:
            raise HTTPException(400, "Talla debe ser mayor a 0")

        bmi = req.peso_kg / (altura_m**2)

        # 2. Obtener datos del niño para calcular edad y BAZ
        db = DatabaseConnector.from_env()
        db.connect()

        # Obtener datos básicos del niño
        query_nino = f"""
        SELECT
            nin_id,
            nin_nombres,
            nin_fecha_nac,
            nin_sexo,
            TIMESTAMPDIFF(MONTH, nin_fecha_nac, CURDATE()) as age_months
        FROM ninos
        WHERE nin_id = {req.nin_id}
        """

        df_nino = db.execute_query(query_nino)

        if df_nino.empty:
            raise HTTPException(404, f"Niño con ID {req.nin_id} no encontrado")

        nino = df_nino.iloc[0]
        age_months = int(nino["age_months"])
        sex = str(nino["nin_sexo"]).strip().upper()[0]

        # 3. Calcular BAZ usando tablas OMS
        global LMS
        if LMS is None:
            LMS = _load_lms(WHO_DIR)

        L, M, S = _nearest_lms(LMS, sex, age_months)
        baz = _baz_from_bmi(bmi, L, M, S)

        # 4. Obtener features ML desde BD
        try:
            df_features = db.get_child_data(req.nin_id)

            if df_features.empty:
                # Si no hay features, calcularlos
                db.call_procedure("sp_calcular_features_ml", [req.nin_id, 0])
                df_features = db.get_child_data(req.nin_id)
        except:
            # Si falla, usar valores por defecto (SIN BAZ - removido para evitar overfitting)
            df_features = pd.DataFrame(
                {
                    "age_months": [age_months],
                    "nin_sexo": [sex],
                    "sex_numeric": [1 if sex == "M" else 0],
                    "BMI": [bmi],
                    "bmi_velocity": [0.0],
                    "weight_velocity": [0.0],
                    "height_velocity": [0.0],
                    "allergy_count": [0],
                    "adherence_score": [75.0],
                    "symptom_frequency": [0],
                    "dietary_diversity_score": [60.0],
                    "altitude_m": [0.0],
                }
            )

        # 5. Preparar features para el modelo
        if "sex_numeric" not in df_features.columns:
            df_features["sex_numeric"] = df_features.get("nin_sexo", sex).map({"M": 1, "F": 0})

        # Asegurar que tenemos todos los features (SIN BAZ - removido para evitar overfitting)
        for feature in ML_MODEL.feature_names:
            if feature not in df_features.columns:
                if feature == "BMI":
                    df_features[feature] = bmi
                elif feature == "age_months":
                    df_features[feature] = age_months
                elif feature == "sex_numeric":
                    df_features[feature] = 1 if sex == "M" else 0
                else:
                    # Valores por defecto para otros features
                    df_features[feature] = 0.0

        X = df_features[ML_MODEL.feature_names].iloc[0:1]

        # 6. Hacer predicción
        result = ML_MODEL.predict_with_metadata(X)
        pred = result["predictions"][0]

        # 7. Calcular percentil (aproximado desde BAZ)
        # percentil ≈ CDF de distribución normal estándar
        from scipy.stats import norm

        percentil = norm.cdf(baz) * 100

        # 8. ✅ USAR PREDICCIÓN DEL MODELO ML (Random Forest con 90.18% accuracy)
        # El modelo ya fue entrenado con datos OMS y tiene mejor accuracy que clasificación por BAZ
        # pred ya contiene la predicción del modelo desde el paso 6

        # 9. Determinar nivel de riesgo
        if pred["prediction"] in [0, 6]:  # DESNUTRICION_SEVERA o OBESIDAD
            nivel_riesgo = "ALTO"
        elif pred["prediction"] in [1, 5] or pred["prediction"] in [
            2,
            4,
        ]:  # DESNUTRICION_MODERADA o SOBREPESO
            nivel_riesgo = "MEDIO"
        else:  # NORMAL
            nivel_riesgo = "BAJO"

        # 10. Generar recomendaciones personalizadas
        recomendaciones = _generar_recomendaciones(
            diagnostico=pred["label"], baz=baz, edad_meses=age_months, bmi=bmi
        )

        # 11. Fecha de medición
        from datetime import datetime

        fecha = req.fecha_medicion or datetime.now().strftime("%d/%m/%Y")
        if req.fecha_medicion and "-" in req.fecha_medicion:
            # Convertir YYYY-MM-DD a DD/MM/YYYY
            fecha = datetime.strptime(req.fecha_medicion, "%Y-%m-%d").strftime("%d/%m/%Y")

        db.disconnect()

        return AnalisisNutricionalResponse(
            # Medición
            fecha=fecha,
            peso_kg=round(req.peso_kg, 2),
            talla_cm=round(req.talla_cm, 2),
            imc=round(bmi, 2),
            # Estado nutricional
            diagnostico=pred["label"],
            imc_valor=round(bmi, 2),
            percentil=round(percentil, 1),
            nivel_riesgo=nivel_riesgo,
            baz=round(baz, 2),
            # Probabilidades
            probabilidad=round(pred["probability"], 4),
            probabilidades=pred["probabilities"],
            # Recomendaciones
            recomendaciones=recomendaciones,
            # Metadata
            modelo_usado=True,
            modelo_version=ML_MODEL.version,
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback

        error_detail = f"Error en análisis nutricional: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ ERROR: {error_detail}")
        raise HTTPException(status_code=500, detail=f"Error en análisis nutricional: {str(e)}")


def _generar_recomendaciones(
    diagnostico: str, baz: float, edad_meses: int, bmi: float
) -> list[RecomendacionNutricional]:
    """Genera recomendaciones personalizadas según el diagnóstico (7 categorías OMS)."""

    recomendaciones = []

    if diagnostico == "NORMAL":
        recomendaciones = [
            RecomendacionNutricional(
                icono="✅",
                titulo="Mantener alimentación balanceada y variada actual",
                descripcion="Continuar con 3 comidas principales y 2 meriendas saludables",
            ),
            RecomendacionNutricional(
                icono="🥗",
                titulo="Incluir diariamente: frutas, verduras, proteínas, lácteos y cereales integrales",
                descripcion="Hidratación adecuada con agua (evitar bebidas azucaradas)",
            ),
            RecomendacionNutricional(
                icono="🏃",
                titulo="Fomentar actividad física regular según edad",
                descripcion="Limitar consumo de alimentos ultraprocesados y comida rápida",
            ),
            RecomendacionNutricional(
                icono="📅",
                titulo="Monitoreo de crecimiento cada 3-6 meses",
                descripcion="Mantener buenos hábitos alimenticios y horarios regulares",
            ),
            RecomendacionNutricional(
                icono="💪",
                titulo="Promover imagen corporal positiva y autoestima",
                descripcion="Educación nutricional para autonomía alimentaria",
            ),
        ]

    elif diagnostico == "RIESGO_DESNUTRICION":
        recomendaciones = [
            RecomendacionNutricional(
                icono="⚠️",
                titulo="Aumentar frecuencia de comidas a 5-6 al día",
                descripcion="Incluir alimentos densos en energía y nutrientes",
            ),
            RecomendacionNutricional(
                icono="🥛",
                titulo="Incrementar proteínas: carnes, huevos, lácteos, legumbres",
                descripcion="Agregar grasas saludables: aguacate, frutos secos, aceite de oliva",
            ),
            RecomendacionNutricional(
                icono="📊",
                titulo="Monitoreo mensual de peso y talla",
                descripcion="Consulta con nutricionista para plan personalizado",
            ),
            RecomendacionNutricional(
                icono="💊",
                titulo="Evaluar suplementación de vitaminas y minerales",
                descripcion="Descartar causas médicas de bajo peso",
            ),
        ]

    elif diagnostico == "RIESGO_SOBREPESO":
        recomendaciones = [
            RecomendacionNutricional(
                icono="⚠️",
                titulo="Controlar porciones y evitar segundas porciones",
                descripcion="Reducir alimentos altos en azúcar y grasas saturadas",
            ),
            RecomendacionNutricional(
                icono="🥗",
                titulo="Aumentar consumo de frutas y verduras",
                descripcion="Preferir agua en lugar de jugos o bebidas azucaradas",
            ),
            RecomendacionNutricional(
                icono="🏃",
                titulo="Incrementar actividad física a 60 min diarios",
                descripcion="Limitar tiempo de pantalla (TV, tablet, celular)",
            ),
            RecomendacionNutricional(
                icono="📅",
                titulo="Monitoreo mensual con nutricionista",
                descripcion="Involucrar a toda la familia en cambios de hábitos",
            ),
        ]

    elif diagnostico == "DESNUTRICION_MODERADA":
        recomendaciones = [
            RecomendacionNutricional(
                icono="🚨",
                titulo="Consulta urgente con nutricionista y pediatra",
                descripcion="Plan de recuperación nutricional intensivo",
            ),
            RecomendacionNutricional(
                icono="🍽️",
                titulo="6 comidas al día con alta densidad calórica",
                descripcion="Suplementos nutricionales según indicación médica",
            ),
            RecomendacionNutricional(
                icono="📊",
                titulo="Monitoreo semanal de peso y talla",
                descripcion="Evaluación de causas subyacentes (infecciones, parásitos)",
            ),
            RecomendacionNutricional(
                icono="👨‍⚕️",
                titulo="Seguimiento médico continuo",
                descripcion="Educación nutricional familiar intensiva",
            ),
        ]

    elif diagnostico == "SOBREPESO":
        recomendaciones = [
            RecomendacionNutricional(
                icono="🚨",
                titulo="Consulta con nutricionista para plan personalizado",
                descripcion="Evaluación de hábitos alimentarios y actividad física",
            ),
            RecomendacionNutricional(
                icono="🥗",
                titulo="Dieta balanceada con control de porciones",
                descripcion="Eliminar bebidas azucaradas y comida chatarra",
            ),
            RecomendacionNutricional(
                icono="🏃",
                titulo="Actividad física estructurada 60 min diarios",
                descripcion="Reducir sedentarismo y tiempo de pantalla",
            ),
            RecomendacionNutricional(
                icono="📅",
                titulo="Monitoreo quincenal de progreso",
                descripcion="Apoyo psicológico si hay problemas emocionales",
            ),
        ]

    elif diagnostico == "DESNUTRICION_SEVERA":
        recomendaciones = [
            RecomendacionNutricional(
                icono="🚨",
                titulo="ATENCIÓN MÉDICA URGENTE - Hospitalización si es necesario",
                descripcion="Evaluación completa por equipo multidisciplinario",
            ),
            RecomendacionNutricional(
                icono="💊",
                titulo="Tratamiento médico intensivo con suplementación",
                descripcion="Fórmulas especiales de recuperación nutricional",
            ),
            RecomendacionNutricional(
                icono="📊",
                titulo="Monitoreo diario de signos vitales y peso",
                descripcion="Tratamiento de complicaciones médicas",
            ),
            RecomendacionNutricional(
                icono="👨‍⚕️",
                titulo="Seguimiento hospitalario o ambulatorio intensivo",
                descripcion="Apoyo social y familiar integral",
            ),
        ]

    elif diagnostico == "OBESIDAD":
        recomendaciones = [
            RecomendacionNutricional(
                icono="🚨",
                titulo="Evaluación médica completa urgente",
                descripcion="Descartar complicaciones metabólicas (diabetes, hipertensión)",
            ),
            RecomendacionNutricional(
                icono="👨‍⚕️",
                titulo="Tratamiento multidisciplinario: nutricionista, pediatra, psicólogo",
                descripcion="Plan de reducción de peso supervisado médicamente",
            ),
            RecomendacionNutricional(
                icono="🥗",
                titulo="Dieta terapéutica estricta",
                descripcion="Eliminación total de alimentos ultraprocesados",
            ),
            RecomendacionNutricional(
                icono="🏃",
                titulo="Programa de ejercicio supervisado",
                descripcion="Cambio de estilo de vida familiar completo",
            ),
            RecomendacionNutricional(
                icono="📅",
                titulo="Monitoreo semanal con equipo médico",
                descripcion="Apoyo psicológico para manejo de ansiedad y autoestima",
            ),
        ]

    return recomendaciones
