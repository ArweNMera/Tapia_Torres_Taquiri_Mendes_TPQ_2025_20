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

try:
    from src.models.direct_classifier import DirectNutritionClassifier, cargar_modelo_directo
    from src.utils import DatabaseConnector
except Exception as e:
    print(f"⚠️  Error importando modelos ML: {e}")
    cargar_modelo_directo = None
    DirectNutritionClassifier = None
    DatabaseConnector = None


app = FastAPI(title="ml-recomendator", version="0.1.0")

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
        "https://appsaludable.netlify.app",  
        "*",  
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


def _load_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.replace('"', "").str.replace("'", "")

    cols = {c: c.strip().replace(" ", "_") for c in df.columns}
    df = df.rename(columns=cols)

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

ML_MODEL = None


def load_ml_model():
    """Carga el modelo DIRECTO entrenado."""
    global ML_MODEL
    if cargar_modelo_directo is None:
        print("⚠️  cargar_modelo_directo no disponible")
        return

    try:
        ML_MODEL = cargar_modelo_directo()
        print("✅ Modelo DIRECTO cargado exitosamente")
        print("   Tipo: DirectNutritionClassifier")
        print("   Categorías: 7 (OMS)")
    except Exception as e:
        print(f"⚠️  Modelo no cargado: {e}")
        print("   Entrena primero: ./ENTRENAR_AHORA.sh")
        ML_MODEL = None

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
        return 0  
    elif -3.0 <= z < -2.0:
        return 1  
    elif -2.0 <= z < -1.0:
        return 2  
    elif -1.0 <= z <= 1.0:
        return 3  
    elif 1.0 < z <= 2.0:
        return 4  
    elif 2.0 < z <= 3.0:
        return 5  
    else:  
        return 6  


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

    label_map = {
        0: "DESNUTRICION_SEVERA",
        1: "DESNUTRICION_MODERADA",
        2: "RIESGO_DESNUTRICION",
        3: "NORMAL",
        4: "RIESGO_SOBREPESO",
        5: "SOBREPESO",
        6: "OBESIDAD",
    }

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


class RecomendacionPersonalizadaRequest(BaseModel):
    id_nino: int = Field(description="ID del niño para el que se solicita recomendación")
    tipo_comida: str = Field(description="Tipo de comida (desayuno, almuerzo, cena, merienda)")
    pregunta_usuario: str | None = Field(
        default=None,
        description="Pregunta específica del usuario sobre recomendaciones"
    )


class RecomendacionPersonalizadaResponse(BaseModel):
    recomendacion: str
    datos_nino: dict[str, Any]
    recetas_disponibles: list[dict[str, Any]]
    estado_nutricional: dict[str, Any]
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


def consultar_datos_nino(id_nino: int) -> dict[str, Any]:
    """Consulta los datos básicos del niño desde la base de datos."""
    if DatabaseConnector is None:
        raise HTTPException(status_code=503, detail="Conector de base de datos no disponible")

    try:
        db = DatabaseConnector.from_env()
        db.connect()

        query = """
        SELECT
            n.nin_id,
            n.nin_nombre,
            n.nin_apellido,
            n.nin_fecha_nacimiento,
            n.nin_sexo,
            n.nin_peso_actual,
            n.nin_talla_actual,
            n.nin_imc_actual,
            n.nin_edad_meses,
            n.nin_estado_nutricional,
            n.nin_diagnostico_nutricional,
            e.ent_nombre,
            e.ent_codigo
        FROM ninos n
        LEFT JOIN entidades e ON n.ent_id = e.ent_id
        WHERE n.nin_id = %s
        """

        df = db.execute_query(query, (id_nino,))
        db.disconnect()

        if df.empty:
            raise HTTPException(status_code=404, detail=f"Niño con ID {id_nino} no encontrado")

        row = df.iloc[0]
        return {
            "id": int(row["nin_id"]),
            "nombre": f"{row['nin_nombre']} {row['nin_apellido']}",
            "fecha_nacimiento": str(row["nin_fecha_nacimiento"]) if row["nin_fecha_nacimiento"] else None,
            "sexo": row["nin_sexo"],
            "peso_kg": float(row["nin_peso_actual"]) if row["nin_peso_actual"] else None,
            "talla_cm": float(row["nin_talla_actual"]) if row["nin_talla_actual"] else None,
            "imc": float(row["nin_imc_actual"]) if row["nin_imc_actual"] else None,
            "edad_meses": int(row["nin_edad_meses"]) if row["nin_edad_meses"] else None,
            "estado_nutricional": row["nin_estado_nutricional"],
            "diagnostico": row["nin_diagnostico_nutricional"],
            "entidad": row["ent_nombre"],
            "codigo_entidad": row["ent_codigo"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando datos del niño: {str(e)}")


def consultar_recetas_por_nino(id_nino: int, tipo_comida: str) -> list[dict[str, Any]]:
    """Consulta las mejores recetas disponibles para el niño usando el procedimiento almacenado."""
    if DatabaseConnector is None:
        raise HTTPException(status_code=503, detail="Conector de base de datos no disponible")

    try:
        db = DatabaseConnector.from_env()
        db.connect()

        # Llamar al procedimiento almacenado sp_top_recetas_por_nombre
        # Asumimos que el nombre del niño se puede obtener de los datos del niño
        datos_nino = consultar_datos_nino(id_nino)
        nombre_nino = datos_nino["nombre"]

        # Ejecutar el procedimiento almacenado
        query = "CALL sp_top_recetas_por_nombre(%s, %s)"
        df = db.execute_query(query, (nombre_nino, tipo_comida))

        db.disconnect()

        if df.empty:
            return []

        recetas = []
        for _, row in df.iterrows():
            recetas.append({
                "id": int(row.get("rec_id", 0)),
                "nombre": row.get("rec_nombre", ""),
                "descripcion": row.get("rec_descripcion", ""),
                "tipo_comida": row.get("rec_tipo_comida", ""),
                "calorias": float(row.get("rec_calorias", 0)),
                "proteinas": float(row.get("rec_proteinas", 0)),
                "carbohidratos": float(row.get("rec_carbohidratos", 0)),
                "grasas": float(row.get("rec_grasas", 0)),
                "puntuacion": float(row.get("puntuacion", 0))
            })

        return recetas

    except Exception as e:
        print(f"Error consultando recetas: {str(e)}")
        return []


def obtener_estado_nutricional(id_nino: int) -> dict[str, Any]:
    """Obtiene el estado nutricional detallado del niño."""
    try:
        datos_nino = consultar_datos_nino(id_nino)

        estado = {
            "diagnostico": datos_nino.get("diagnostico", "No disponible"),
            "estado_actual": datos_nino.get("estado_nutricional", "No disponible"),
            "imc": datos_nino.get("imc"),
            "peso_kg": datos_nino.get("peso_kg"),
            "talla_cm": datos_nino.get("talla_cm"),
            "edad_meses": datos_nino.get("edad_meses"),
            "sexo": datos_nino.get("sexo")
        }

        return estado

    except Exception as e:
        return {
            "diagnostico": "Error obteniendo diagnóstico",
            "estado_actual": "Error obteniendo estado",
            "imc": None,
            "peso_kg": None,
            "talla_cm": None,
            "edad_meses": None,
            "sexo": None
        }


def crear_prompt_recomendacion(
    datos_nino: dict[str, Any],
    estado_nutricional: dict[str, Any],
    recetas: list[dict[str, Any]],
    tipo_comida: str,
    pregunta_usuario: str | None = None
) -> str:
    """Crea el prompt para el LLM con toda la información del niño y recetas disponibles."""

    prompt = f"""Eres un nutricionista especializado en alimentación infantil. Un padre/madre te consulta sobre recomendaciones nutricionales para su hijo/a.

DATOS DEL NIÑO:
- Nombre: {datos_nino.get('nombre', 'No especificado')}
- Edad: {datos_nino.get('edad_meses', 'No especificada')} meses
- Sexo: {'Masculino' if datos_nino.get('sexo') == 'M' else 'Femenino'}
- Peso: {datos_nino.get('peso_kg', 'No especificado')} kg
- Talla: {datos_nino.get('talla_cm', 'No especificada')} cm
- IMC: {datos_nino.get('imc', 'No especificado')}
- Estado nutricional: {estado_nutricional.get('diagnostico', 'No especificado')}
- Diagnóstico: {estado_nutricional.get('estado_actual', 'No especificado')}

RECETAS DISPONIBLES PARA {tipo_comida.upper()}:
"""

    if recetas:
        for i, receta in enumerate(recetas[:5], 1):  # Limitar a 5 mejores recetas
            prompt += f"""
{i}. {receta.get('nombre', 'Sin nombre')}
   - Descripción: {receta.get('descripcion', 'Sin descripción')}
   - Calorías: {receta.get('calorias', 0)} kcal
   - Proteínas: {receta.get('proteinas', 0)}g
   - Carbohidratos: {receta.get('carbohidratos', 0)}g
   - Grasas: {receta.get('grasas', 0)}g
   - Puntuación nutricional: {receta.get('puntuacion', 0)}/10
"""
    else:
        prompt += "\nNo hay recetas específicas disponibles para este tipo de comida.\n"

    if pregunta_usuario:
        prompt += f"""

PREGUNTA ESPECÍFICA DEL USUARIO: {pregunta_usuario}

INSTRUCCIONES:
1. Responde de manera clara, amable y profesional
2. Considera el estado nutricional del niño al hacer recomendaciones
3. Si hay recetas disponibles, sugiere las más apropiadas
4. Incluye porciones adecuadas para la edad
5. Menciona cualquier precaución nutricional importante
6. Si no hay recetas específicas, da recomendaciones generales saludables
7. Mantén un tono positivo y alentador para los padres

RECOMENDACIÓN PERSONALIZADA:"""
    else:
        prompt += f"""

INSTRUCCIONES:
Proporciona una recomendación nutricional completa para {tipo_comida} considerando:
1. El estado nutricional actual del niño
2. Las mejores recetas disponibles
3. Porciones apropiadas para su edad
4. Beneficios nutricionales de las recomendaciones
5. Consejos para una alimentación saludable

RECOMENDACIÓN PERSONALIZADA:"""

    return prompt


def consultar_agente_llm(prompt: str) -> str:
    """Consulta al agente LLM (CORA) con el prompt creado."""
    if get_llm_client is None:
        return "Lo siento, el servicio de recomendaciones está temporalmente no disponible. Consulta con un nutricionista profesional."

    try:
        client = get_llm_client()
        respuesta = client.chat(
            system_message="Eres un nutricionista infantil experto. Proporciona recomendaciones seguras, basadas en evidencia científica y apropiadas para la edad del niño.",
            user_message=prompt
        )

        if respuesta and len(respuesta.strip()) > 10:  # Verificar que no sea una respuesta vacía o demasiado corta
            return respuesta
        else:
            return "No pude generar una recomendación personalizada en este momento. Te recomiendo consultar con un profesional de la nutrición."

    except Exception as e:
        print(f"Error consultando LLM: {str(e)}")
        return "Hubo un problema técnico generando la recomendación. Por favor, intenta nuevamente o consulta con un especialista."


@app.post("/ml/recomendacion_personalizada", response_model=RecomendacionPersonalizadaResponse)
def generar_recomendacion_personalizada(req: RecomendacionPersonalizadaRequest) -> RecomendacionPersonalizadaResponse:
    """
    Genera una recomendación nutricional personalizada para un niño específico.

    Utiliza datos del niño, su estado nutricional, recetas disponibles y un agente LLM
    para proporcionar recomendaciones personalizadas según el tipo de comida solicitado.
    """
    try:
        # 1. Obtener datos del niño
        datos_nino = consultar_datos_nino(req.id_nino)

        # 2. Obtener estado nutricional
        estado_nutricional = obtener_estado_nutricional(req.id_nino)

        # 3. Consultar recetas disponibles
        recetas = consultar_recetas_por_nino(req.id_nino, req.tipo_comida)

        # 4. Crear prompt para el LLM
        prompt = crear_prompt_recomendacion(
            datos_nino,
            estado_nutricional,
            recetas,
            req.tipo_comida,
            req.pregunta_usuario
        )

        # 5. Consultar al agente LLM
        recomendacion = consultar_agente_llm(prompt)
        used_llm = recomendacion != "Lo siento, el servicio de recomendaciones está temporalmente no disponible. Consulta con un nutricionista profesional."

        return RecomendacionPersonalizadaResponse(
            recomendacion=recomendacion,
            datos_nino=datos_nino,
            recetas_disponibles=recetas,
            estado_nutricional=estado_nutricional,
            used_llm=used_llm
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando recomendación personalizada: {str(e)}"
        )


class PredictMLRequest(BaseModel):
    """Request para predicción con modelo ML."""

    nin_id: int = Field(description="ID del niño")


class PredictMLResponse(BaseModel):
    """Response de predicción ML."""

    nin_id: int
    prediction: int  
    probability: float
    probabilities: dict[str, float]
    risk_score: float
    features_used: dict[str, Any]  
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

    try:
        db = DatabaseConnector.from_env()
        db.connect()

        df = db.get_child_data(req.nin_id)

        if df.empty:
            raise HTTPException(
                status_code=404, detail=f"No se encontraron datos para nin_id={req.nin_id}"
            )

        feature_cols = ML_MODEL.feature_names

        if "sex_numeric" in feature_cols and "nin_sexo" in df.columns:
            df["sex_numeric"] = df["nin_sexo"].map({"M": 1, "F": 0})

        missing_features = [f for f in feature_cols if f not in df.columns]
        if missing_features:
            raise HTTPException(status_code=400, detail=f"Features faltantes: {missing_features}")

        X = df[feature_cols].iloc[0:1]  

        result = ML_MODEL.predict_with_metadata(X)
        pred = result["predictions"][0]

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
    """Request para predicción directa con MODELO DIRECTO (solo datos básicos)."""

    age_months: int = Field(description="Edad en meses (0-228)")
    sex: str = Field(description="M o F")
    weight_kg: float = Field(description="Peso en kilogramos")
    height_cm: float = Field(description="Talla en centímetros")


@app.post("/ml/predict_direct", response_model=PredictMLResponse)
def predict_ml_direct(req: PredictMLDirectRequest) -> PredictMLResponse:
    """
    Predice el estado nutricional usando MODELO DIRECTO.

    Solo necesita: edad, sexo, peso, talla.
    NO necesita BAZ ni otros features complejos.
    """
    if ML_MODEL is None:
        raise HTTPException(
            status_code=503, detail="Modelo ML no disponible. Entrena: ./ENTRENAR_AHORA.sh"
        )

    try:
        if req.age_months < 0 or req.age_months > 228:
            raise HTTPException(400, "Edad debe estar entre 0 y 228 meses")

        if req.sex.upper() not in ["M", "F"]:
            raise HTTPException(400, "Sexo debe ser M o F")

        if req.weight_kg <= 0:
            raise HTTPException(400, "Peso debe ser mayor a 0")

        if req.height_cm <= 0:
            raise HTTPException(400, "Talla debe ser mayor a 0")

        resultado = ML_MODEL.predecir(
            edad_meses=req.age_months,
            sexo=req.sex.upper(),
            peso_kg=req.weight_kg,
            talla_cm=req.height_cm,
        )

        bmi = req.weight_kg / (req.height_cm / 100) ** 2

        risk_map = {
            "DESNUTRICION_SEVERA": 1.0,
            "DESNUTRICION_MODERADA": 0.8,
            "RIESGO_DESNUTRICION": 0.6,
            "NORMAL": 0.0,
            "RIESGO_SOBREPESO": 0.6,
            "SOBREPESO": 0.8,
            "OBESIDAD": 1.0,
        }
        risk_score = risk_map.get(resultado["clasificacion"], 0.5)

        return PredictMLResponse(
            nin_id=0,  
            prediction=resultado["label"],
            label=resultado["clasificacion"],
            probability=resultado["confianza"],
            probabilities=resultado["probabilidades"],
            risk_score=risk_score,
            features_used={
                "edad_meses": req.age_months,
                "sexo": req.sex.upper(),
                "peso_kg": req.weight_kg,
                "talla_cm": req.height_cm,
                "bmi": round(bmi, 2),
            },
            model_version="2.0.0-directo",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@app.get("/ml/model_info")
def model_info():
    """Información sobre el modelo cargado."""
    if ML_MODEL is None:
        return {"loaded": False, "message": "Modelo no cargado. Entrena: ./ENTRENAR_AHORA.sh"}

    return {
        "loaded": True,
        "model_name": "DirectNutritionClassifier",
        "model_type": "Modelo Directo (aprende de edad, peso, talla)",
        "version": "2.0.0-directo",
        "categorias": list(ML_MODEL.LABEL_TO_CATEGORY.values()),
        "features_basicas": ["edad_meses", "sexo", "peso_kg", "talla_cm"],
        "descripcion": "Modelo que aprende DIRECTAMENTE de datos antropométricos básicos",
    }


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

    fecha: str
    peso_kg: float
    talla_cm: float
    imc: float
    diagnostico: str  
    imc_valor: float
    percentil: float
    nivel_riesgo: str 
    baz: float
    probabilidad: float
    probabilidades: dict[str, float]

    recomendaciones: list[RecomendacionNutricional]

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
        altura_m = req.talla_cm / 100.0
        if altura_m <= 0:
            raise HTTPException(400, "Talla debe ser mayor a 0")

        bmi = req.peso_kg / (altura_m**2)
        db = DatabaseConnector.from_env()
        db.connect()

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

        global LMS
        if LMS is None:
            LMS = _load_lms(WHO_DIR)

        L, M, S = _nearest_lms(LMS, sex, age_months)
        baz = _baz_from_bmi(bmi, L, M, S)

        try:
            df_features = db.get_child_data(req.nin_id)

            if df_features.empty:
                db.call_procedure("sp_calcular_features_ml", [req.nin_id, 0])
                df_features = db.get_child_data(req.nin_id)
        except Exception:
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

        resultado = ML_MODEL.predecir(
            edad_meses=age_months, sexo=sex, peso_kg=req.peso_kg, talla_cm=req.talla_cm
        )
        pred = {
            "prediction": resultado["label"],
            "label": resultado["clasificacion"],
            "probability": resultado["confianza"],
            "probabilities": resultado["probabilidades"],
        }
        from scipy.stats import norm

        percentil = norm.cdf(baz) * 100

        clasificacion = pred["label"]
        if clasificacion in ["DESNUTRICION_SEVERA", "OBESIDAD"]:
            nivel_riesgo = "ALTO"
        elif clasificacion in ["DESNUTRICION_MODERADA", "SOBREPESO"] or clasificacion in [
            "RIESGO_DESNUTRICION",
            "RIESGO_SOBREPESO",
        ]:
            nivel_riesgo = "MEDIO"
        else:  
            nivel_riesgo = "BAJO"

        recomendaciones = _generar_recomendaciones(
            diagnostico=clasificacion, baz=baz, edad_meses=age_months, bmi=bmi
        )

        from datetime import datetime

        fecha = req.fecha_medicion or datetime.now().strftime("%d/%m/%Y")
        if req.fecha_medicion and "-" in req.fecha_medicion:
            fecha = datetime.strptime(req.fecha_medicion, "%Y-%m-%d").strftime("%d/%m/%Y")

        db.disconnect()

        return AnalisisNutricionalResponse(
            fecha=fecha,
            peso_kg=round(req.peso_kg, 2),
            talla_cm=round(req.talla_cm, 2),
            imc=round(bmi, 2),
            diagnostico=clasificacion,
            imc_valor=round(bmi, 2),
            percentil=round(percentil, 1),
            nivel_riesgo=nivel_riesgo,
            baz=round(baz, 2),
            probabilidad=round(pred["probability"], 4),
            probabilidades=pred["probabilities"],
            recomendaciones=recomendaciones,
            modelo_usado=True,
            modelo_version="2.0.0-directo",
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
