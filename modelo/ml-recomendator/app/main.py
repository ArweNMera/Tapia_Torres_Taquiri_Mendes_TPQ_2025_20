from __future__ import annotations

import logging
import math
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    from src.utils import DatabaseConnector
except Exception as e:
    print(f"⚠️  Error importando DatabaseConnector: {e}")
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


@app.get("/health")
def health():
    llm_available = False
    try:
        if get_llm_client is not None:
            client = get_llm_client()
            llm_available = True
    except:
        pass

    return {
        "status": "ok",
        "llm_available": llm_available,
        "lms_loaded": LMS is not None,
        "db_available": DatabaseConnector is not None,
    }


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
            "Eres un asistente que explica y responde de forma clara, sin emitir consejo médico."
        )
    )


class ChatResponse(BaseModel):
    reply: str
    used_llm: bool


class RecomendacionPersonalizadaRequest(BaseModel):
    nombre_nino: str = Field(description="Nombre del niño para buscar (búsqueda fuzzy)")
    tipo_comida: str = Field(description="Tipo de comida (desayuno, almuerzo, cena)")
    pregunta_usuario: str | None = Field(
        default=None, description="Pregunta específica del usuario sobre recomendaciones"
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


def consultar_recetas_por_nombre(
    nombre_nino: str, tipo_comida: str
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Consulta las mejores recetas usando sp_top_recetas_por_nombre.

    Returns:
        tuple: (lista de recetas, datos del niño encontrado o None)
    """
    if DatabaseConnector is None:
        raise HTTPException(503, "Conector de BD no disponible")

    try:
        logger.info(f"Consultando recetas para niño '{nombre_nino}', tipo: {tipo_comida}")

        # 1. Normalizar tipo de comida
        tipo_comida_norm = tipo_comida.upper()
        if tipo_comida_norm not in ["DESAYUNO", "ALMUERZO", "CENA"]:
            logger.warning(f"Tipo de comida '{tipo_comida}' no válido, usando DESAYUNO")
            tipo_comida_norm = "DESAYUNO"

        # 2. Ejecutar procedimiento almacenado
        db = DatabaseConnector.from_env()
        db.connect()

        query = "CALL sp_top_recetas_por_nombre(%s, %s, %s)"
        df = db.execute_query(query, (nombre_nino, tipo_comida_norm, 5))

        db.disconnect()

        # 3. Verificar resultado
        if df.empty:
            logger.warning(f"No se encontraron recetas para '{nombre_nino}'")
            return [], None

        # 4. Verificar status
        if df.iloc[0].get("status") == "NO_MATCH":
            logger.warning(f"No se encontró niño con nombre: '{nombre_nino}'")
            return [], None

        # 5. Extraer datos del niño de la primera fila
        first_row = df.iloc[0]
        datos_nino = {
            "id": int(first_row.get("nin_id", 0)),
            "nombre": first_row.get("nin_nombres", nombre_nino),
            "estado_nutricional": first_row.get("en_clasificacion", ""),
            "diagnostico": first_row.get("en_clasificacion", ""),
            # Campos opcionales que pueden no estar en el procedimiento
            "sexo": first_row.get("nin_sexo", ""),
            "edad_meses": int(first_row.get("edad_meses", 0))
            if "edad_meses" in first_row
            else None,
            "peso_kg": float(first_row.get("peso_kg", 0)) if "peso_kg" in first_row else None,
            "talla_cm": float(first_row.get("talla_cm", 0)) if "talla_cm" in first_row else None,
            "imc": float(first_row.get("imc", 0)) if "imc" in first_row else None,
        }

        # 6. Parsear recetas
        recetas = []
        for _, row in df.iterrows():
            recetas.append(
                {
                    "id": int(row.get("rec_id", 0)),
                    "nombre": row.get("rec_nombre", ""),
                    "calorias": float(row.get("kcal", 0)),
                    "proteinas": float(row.get("proteina_g", 0)),
                    "carbohidratos": float(row.get("carbohidratos_g", 0))
                    if "carbohidratos_g" in row
                    else 0.0,
                    "grasas": float(row.get("grasas_g", 0)) if "grasas_g" in row else 0.0,
                    "fibra": float(row.get("fibra_g", 0)),
                    "hierro": float(row.get("hierro_mg", 0)),
                    "costo": float(row.get("costo_soles_aprox", 0)),
                    "puntuacion": float(row.get("score", 0)),
                }
            )

        logger.info(f"✅ Encontradas {len(recetas)} recetas para '{datos_nino['nombre']}'")
        return recetas, datos_nino

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error consultando recetas: {str(e)}")
        return [], None


def crear_prompt_recomendacion(
    datos_nino: dict[str, Any],
    estado_nutricional: dict[str, Any],
    recetas: list[dict[str, Any]],
    tipo_comida: str,
    pregunta_usuario: str | None = None,
) -> str:
    """Crea el prompt para el LLM con toda la información."""

    sexo = datos_nino.get("sexo", "")
    sexo_texto = "Masculino" if sexo == "M" else ("Femenino" if sexo == "F" else "No especificado")

    edad_texto = (
        f"{datos_nino.get('edad_meses')} meses"
        if datos_nino.get("edad_meses")
        else "No especificada"
    )
    peso_texto = (
        f"{datos_nino.get('peso_kg')} kg" if datos_nino.get("peso_kg") else "No especificado"
    )
    talla_texto = (
        f"{datos_nino.get('talla_cm')} cm" if datos_nino.get("talla_cm") else "No especificada"
    )
    imc_texto = f"{datos_nino.get('imc')}" if datos_nino.get("imc") else "No especificado"

    prompt = f"""Eres un nutricionista especializado en alimentación infantil. Un padre/madre te consulta sobre recomendaciones nutricionales para su hijo/a.

DATOS DEL NIÑO:
- Nombre: {datos_nino.get("nombre", "No especificado")}
- Edad: {edad_texto}
- Sexo: {sexo_texto}
- Peso: {peso_texto}
- Talla: {talla_texto}
- IMC: {imc_texto}
- Estado nutricional: {datos_nino.get("estado_nutricional", "No especificado")}

RECETAS DISPONIBLES PARA {tipo_comida.upper()}:
"""

    if recetas:
        for i, receta in enumerate(recetas[:5], 1):
            prompt += f"""
{i}. {receta.get("nombre", "Sin nombre")}
   - Calorías: {receta.get("calorias", 0):.0f} kcal
   - Proteínas: {receta.get("proteinas", 0):.1f}g
   - Carbohidratos: {receta.get("carbohidratos", 0):.1f}g
   - Grasas: {receta.get("grasas", 0):.1f}g
   - Fibra: {receta.get("fibra", 0):.1f}g
   - Hierro: {receta.get("hierro", 0):.1f}mg
   - Costo aproximado: S/ {receta.get("costo", 0):.2f}
   - Puntuación nutricional: {receta.get("puntuacion", 0):.1f}/10
"""
    else:
        prompt += "\nNo hay recetas específicas disponibles en la base de datos para este tipo de comida.\n"

    if pregunta_usuario:
        prompt += f"""

PREGUNTA DEL USUARIO: {pregunta_usuario}

Responde de forma concisa (máximo 300 palabras) considerando el estado nutricional del niño y las recetas disponibles.

RESPUESTA:"""
    else:
        prompt += f"""

TAREA:
Recomienda las 3 mejores opciones de {tipo_comida} para {datos_nino.get("nombre", "el niño")}, considerando:
- Estado nutricional: {datos_nino.get("estado_nutricional", "No especificado")}
- Edad: {edad_texto}
- Recetas ordenadas por puntuación nutricional

Sé breve y práctico (máximo 300 palabras). Incluye porciones específicas.

RECOMENDACIÓN:"""

    return prompt


def consultar_agente_llm(prompt: str) -> str:
    """Consulta al agente LLM (CORA) con el prompt creado."""
    if get_llm_client is None:
        logger.error("Cliente LLM no disponible")
        return "El servicio de recomendaciones no está disponible. Consulta con un nutricionista profesional."

    try:
        logger.info("Consultando agente LLM...")
        logger.debug(f"Prompt (primeros 200 chars): {prompt[:200]}...")

        client = get_llm_client()

        system_message = """Eres un nutricionista infantil experto en Perú.

FORMATO DE RESPUESTA (MÁXIMO 300 PALABRAS):
1. Saludo breve y contexto del estado nutricional (1-2 líneas)
2. Lista las 3 mejores recetas con:
   - Nombre de la receta
   - Calorías, proteínas, fibra
   - Porción recomendada para la edad
   - Por qué es adecuada (1 línea)
3. Consejo práctico final (2-3 líneas)

REGLAS:
- SÉ CONCISO: Máximo 300 palabras
- NO uses tablas extensas ni secciones largas
- NO incluyas emojis excesivos
- Usa lenguaje claro y directo
- Menciona que debe consultar con un profesional si tiene dudas
- NO des diagnósticos médicos"""

        respuesta = client.chat(system_message=system_message, user_message=prompt)

        if respuesta and len(respuesta.strip()) > 10:
            logger.info(f"✅ LLM respondió exitosamente ({len(respuesta)} chars)")
            return respuesta
        else:
            logger.warning("LLM retornó respuesta vacía o muy corta")
            return "No pude generar una recomendación personalizada. Te recomiendo consultar con un nutricionista profesional."

    except Exception as e:
        logger.error(f"❌ Error consultando LLM: {str(e)}", exc_info=True)
        return "Hubo un problema técnico generando la recomendación. Por favor, intenta nuevamente o consulta con un especialista."


@app.post("/ml/recomendacion_personalizada", response_model=RecomendacionPersonalizadaResponse)
def generar_recomendacion_personalizada(
    req: RecomendacionPersonalizadaRequest,
) -> RecomendacionPersonalizadaResponse:
    """
    Genera una recomendación nutricional personalizada buscando al niño por nombre.

    Utiliza búsqueda fuzzy por nombre, datos del niño, recetas disponibles y un agente LLM
    para proporcionar recomendaciones personalizadas según el tipo de comida solicitado.
    """
    try:
        logger.info(
            f"📝 Generando recomendación para niño '{req.nombre_nino}', tipo: {req.tipo_comida}"
        )

        # 1. Consultar recetas (el procedimiento busca al niño por nombre y devuelve todo)
        recetas, datos_nino = consultar_recetas_por_nombre(req.nombre_nino, req.tipo_comida)

        # 2. Verificar si se encontró al niño
        if not datos_nino:
            return RecomendacionPersonalizadaResponse(
                recomendacion=f"No encontré un niño con el nombre '{req.nombre_nino}'. ¿Podrías verificar el nombre?",
                datos_nino={},
                recetas_disponibles=[],
                estado_nutricional={},
                used_llm=False,
            )

        # 3. Preparar estado nutricional desde los datos ya obtenidos
        estado_nutricional = {
            "diagnostico": datos_nino.get("estado_nutricional", "No disponible"),
            "estado_actual": datos_nino.get("estado_nutricional", "No disponible"),
        }

        # 4. Crear prompt para el LLM
        prompt = crear_prompt_recomendacion(
            datos_nino, estado_nutricional, recetas, req.tipo_comida, req.pregunta_usuario
        )

        # 5. Consultar al agente LLM
        recomendacion = consultar_agente_llm(prompt)
        used_llm = "El servicio de recomendaciones no está disponible" not in recomendacion

        logger.info(f"✅ Recomendación generada exitosamente (LLM usado: {used_llm})")

        return RecomendacionPersonalizadaResponse(
            recomendacion=recomendacion,
            datos_nino=datos_nino,
            recetas_disponibles=recetas,
            estado_nutricional=estado_nutricional,
            used_llm=used_llm,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando recomendación: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error generando recomendación personalizada: {str(e)}"
        )


# ============================================================================
# ENDPOINT PARA GENERAR PLAN SEMANAL DE COMIDAS
# ============================================================================


class GenerarPlanSemanalRequest(BaseModel):
    nin_id: int = Field(description="ID del niño")
    perfil: dict[str, Any] = Field(description="Perfil nutricional del niño")
    nino: dict[str, Any] = Field(description="Datos básicos del niño")
    preferencias: dict[str, list[str]] = Field(
        default_factory=dict, description="Preferencias por tipo de comida"
    )
    alergias: list[str] = Field(default_factory=list, description="Lista de alergias")
    recetas_disponibles: list[dict[str, Any]] = Field(description="Recetas disponibles")
    incluir_refacciones: bool = Field(default=False)


class GenerarPlanSemanalResponse(BaseModel):
    dias: list[dict[str, Any]]
    preferencias_respetadas: int
    preferencias_totales: int
    porcentaje_match: float
    used_llm: bool


@app.post("/ml/generar_plan_semanal", response_model=GenerarPlanSemanalResponse)
def generar_plan_semanal(req: GenerarPlanSemanalRequest) -> GenerarPlanSemanalResponse:
    """
    Genera un plan de comidas semanal (7 días) usando LLM.
    Considera perfil nutricional, preferencias, alergias y recetas disponibles.
    """
    try:
        logger.info(f"📅 Generando plan semanal para niño {req.nin_id}")

        # 1. Preparar contexto para el LLM
        contexto = _preparar_contexto_plan_semanal(
            req.perfil, req.nino, req.preferencias, req.alergias, req.recetas_disponibles
        )

        # 2. Llamar al LLM
        plan = _generar_plan_con_llm(contexto)

        # 3. Validar y retornar
        if not plan or "dias" not in plan:
            logger.warning("LLM no generó plan válido, usando fallback")
            plan = _generar_plan_fallback_semanal(req.recetas_disponibles)

        return GenerarPlanSemanalResponse(
            dias=plan.get("dias", []),
            preferencias_respetadas=plan.get("preferencias_respetadas", 0),
            preferencias_totales=plan.get("preferencias_totales", 0),
            porcentaje_match=plan.get("porcentaje_match", 0.0),
            used_llm=plan.get("used_llm", False),
        )

    except Exception as e:
        logger.error(f"❌ Error generando plan semanal: {str(e)}", exc_info=True)
        # Fallback en caso de error
        plan = _generar_plan_fallback_semanal(req.recetas_disponibles)
        return GenerarPlanSemanalResponse(
            dias=plan.get("dias", []),
            preferencias_respetadas=0,
            preferencias_totales=0,
            porcentaje_match=0.0,
            used_llm=False,
        )


def _preparar_contexto_plan_semanal(
    perfil: dict, nino: dict, preferencias: dict, alergias: list, recetas: list
) -> str:
    """Prepara el contexto para el LLM"""

    # Agrupar recetas por tipo
    recetas_por_tipo = {"DESAYUNO": [], "ALMUERZO": [], "CENA": []}

    for receta in recetas:
        tipos = receta.get("tipos_comida", "").split(",") if receta.get("tipos_comida") else []
        for tipo in tipos:
            tipo = tipo.strip()
            if tipo in recetas_por_tipo:
                recetas_por_tipo[tipo].append(
                    {
                        "id": receta["rec_id"],
                        "nombre": receta["rec_nombre"],
                        "calorias": int(receta.get("calorias_aprox", 0)),
                    }
                )

    contexto = f"""Eres un nutricionista experto. Genera un plan de comidas semanal (7 días) para un niño.

PERFIL DEL NIÑO:
- Nombre: {nino.get("nin_nombres")}
- Edad: {nino.get("edad_meses", 0) // 12} años ({nino.get("edad_meses", 0)} meses)
- Sexo: {nino.get("nin_sexo")}
- Clasificación: {perfil.get("pnn_clasificacion", "No especificada")}

REQUERIMIENTOS DIARIOS:
- Calorías: {perfil.get("pnn_calorias_diarias", 0)} kcal
- Proteínas: {perfil.get("pnn_proteinas_g", 0)} g
- Carbohidratos: {perfil.get("pnn_carbohidratos_g", 0)} g
- Grasas: {perfil.get("pnn_grasas_g", 0)} g

PREFERENCIAS:
- Desayuno: {", ".join(preferencias.get("DESAYUNO", [])) or "Sin preferencias"}
- Almuerzo: {", ".join(preferencias.get("ALMUERZO", [])) or "Sin preferencias"}
- Cena: {", ".join(preferencias.get("CENA", [])) or "Sin preferencias"}

ALERGIAS: {", ".join(alergias) if alergias else "Ninguna"}

RECETAS DISPONIBLES:

DESAYUNOS ({len(recetas_por_tipo["DESAYUNO"])} opciones):
{_format_recetas_para_prompt(recetas_por_tipo["DESAYUNO"][:15])}

ALMUERZOS ({len(recetas_por_tipo["ALMUERZO"])} opciones):
{_format_recetas_para_prompt(recetas_por_tipo["ALMUERZO"][:20])}

CENAS ({len(recetas_por_tipo["CENA"])} opciones):
{_format_recetas_para_prompt(recetas_por_tipo["CENA"][:15])}

INSTRUCCIONES:
1. Genera un plan para 7 días (lunes a domingo)
2. Cada día: desayuno, almuerzo y cena
3. Respeta las preferencias del niño
4. Evita completamente los alérgenos
5. Distribuye calorías: 25% desayuno, 40% almuerzo, 35% cena
6. Varía las recetas (no repetir en la semana)
7. Prioriza recetas que coincidan con preferencias

FORMATO JSON (responde SOLO con JSON, sin texto adicional):
{{
  "dias": [
    {{
      "desayuno": {{"rec_id": 1, "rec_nombre": "Nombre", "kcal": 500}},
      "almuerzo": {{"rec_id": 2, "rec_nombre": "Nombre", "kcal": 800}},
      "cena": {{"rec_id": 3, "rec_nombre": "Nombre", "kcal": 700}}
    }}
  ]
}}
"""
    return contexto


def _format_recetas_para_prompt(recetas: list) -> str:
    """Formatea recetas para el prompt"""
    if not recetas:
        return "No hay recetas disponibles"
    return "\n".join(
        [f"- ID: {r['id']}, Nombre: {r['nombre']}, Calorías: {r['calorias']} kcal" for r in recetas]
    )


def _generar_plan_con_llm(contexto: str) -> dict:
    """Genera el plan usando LLM"""
    if get_llm_client is None:
        logger.warning("Cliente LLM no disponible")
        return {"dias": [], "used_llm": False}

    try:
        logger.info("Consultando LLM para generar plan...")
        client = get_llm_client()

        respuesta = client.chat(
            system_message="Eres un nutricionista experto. Responde SOLO con JSON válido, sin texto adicional.",
            user_message=contexto,
        )

        logger.info(
            f"📝 Respuesta del LLM (primeros 500 chars): {respuesta[:500] if respuesta else 'VACÍA'}"
        )

        if not respuesta or len(respuesta.strip()) < 10:
            logger.warning("LLM retornó respuesta vacía o muy corta")
            return {"dias": [], "used_llm": False}

        # Limpiar respuesta
        respuesta = respuesta.strip()
        if respuesta.startswith("```json"):
            respuesta = respuesta[7:]
        if respuesta.startswith("```"):
            respuesta = respuesta[3:]
        if respuesta.endswith("```"):
            respuesta = respuesta[:-3]
        respuesta = respuesta.strip()

        logger.info(f"🧹 Respuesta limpia (primeros 300 chars): {respuesta[:300]}")

        # Parsear JSON
        import json

        plan = json.loads(respuesta)

        if "dias" not in plan or not isinstance(plan["dias"], list):
            logger.error(f"❌ Plan no tiene estructura correcta: {plan.keys()}")
            return {"dias": [], "used_llm": False}

        plan["used_llm"] = True
        plan["preferencias_respetadas"] = 0
        plan["preferencias_totales"] = 0
        plan["porcentaje_match"] = 0.0

        logger.info(f"✅ Plan generado con LLM: {len(plan.get('dias', []))} días")
        return plan

    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando JSON del LLM: {str(e)}")
        logger.error(
            f"Respuesta que falló: {respuesta[:500] if 'respuesta' in locals() else 'N/A'}"
        )
        return {"dias": [], "used_llm": False}
    except Exception as e:
        logger.error(f"❌ Error generando plan con LLM: {str(e)}", exc_info=True)
        return {"dias": [], "used_llm": False}


def _generar_plan_fallback_semanal(recetas: list) -> dict:
    """Genera un plan básico sin LLM"""
    logger.warning("Generando plan fallback sin LLM")

    # Agrupar recetas por tipo
    por_tipo = {"DESAYUNO": [], "ALMUERZO": [], "CENA": []}
    for r in recetas:
        tipos = r.get("tipos_comida", "").split(",") if r.get("tipos_comida") else []
        for tipo in tipos:
            tipo = tipo.strip()
            if tipo in por_tipo:
                por_tipo[tipo].append(r)

    dias = []
    for dia in range(7):
        dia_plan = {}

        # Desayuno
        if por_tipo["DESAYUNO"]:
            idx = dia % len(por_tipo["DESAYUNO"])
            r = por_tipo["DESAYUNO"][idx]
            dia_plan["desayuno"] = {
                "rec_id": r["rec_id"],
                "rec_nombre": r["rec_nombre"],
                "kcal": int(r.get("calorias_aprox", 500)),
            }

        # Almuerzo
        if por_tipo["ALMUERZO"]:
            idx = dia % len(por_tipo["ALMUERZO"])
            r = por_tipo["ALMUERZO"][idx]
            dia_plan["almuerzo"] = {
                "rec_id": r["rec_id"],
                "rec_nombre": r["rec_nombre"],
                "kcal": int(r.get("calorias_aprox", 800)),
            }

        # Cena
        if por_tipo["CENA"]:
            idx = dia % len(por_tipo["CENA"])
            r = por_tipo["CENA"][idx]
            dia_plan["cena"] = {
                "rec_id": r["rec_id"],
                "rec_nombre": r["rec_nombre"],
                "kcal": int(r.get("calorias_aprox", 600)),
            }

        dias.append(dia_plan)

    return {
        "dias": dias,
        "preferencias_respetadas": 0,
        "preferencias_totales": 0,
        "porcentaje_match": 0.0,
        "used_llm": False,
    }


# Endpoint alternativo para chatbot que acepta nombre directamente
class ChatRecomendacionRequest(BaseModel):
    nombre_nino: str = Field(description="Nombre del niño")
    tipo_comida: str = Field(description="Tipo de comida (DESAYUNO, ALMUERZO, CENA)")
    pregunta_usuario: str | None = Field(
        default=None, description="Pregunta específica del usuario"
    )


@app.post("/ml/chat_recomendacion", response_model=RecomendacionPersonalizadaResponse)
def chat_recomendacion(req: ChatRecomendacionRequest) -> RecomendacionPersonalizadaResponse:
    """
    Endpoint simplificado para chatbot que acepta el nombre del niño directamente.
    Usa el procedimiento sp_top_recetas_por_nombre que busca por nombre.
    """
    try:
        logger.info(f"📝 Chat recomendación para: {req.nombre_nino}, tipo: {req.tipo_comida}")

        # Normalizar tipo de comida
        tipo_comida_norm = req.tipo_comida.upper()
        if tipo_comida_norm not in ["DESAYUNO", "ALMUERZO", "CENA"]:
            tipo_comida_norm = "DESAYUNO"

        # Consultar recetas usando el procedimiento almacenado (que busca por nombre)
        if DatabaseConnector is None:
            raise HTTPException(503, "Conector de BD no disponible")

        db = DatabaseConnector.from_env()
        db.connect()

        # Ejecutar procedimiento almacenado directamente con el nombre
        query = "CALL sp_top_recetas_por_nombre(%s, %s, %s)"
        df = db.execute_query(query, (req.nombre_nino, tipo_comida_norm, 5))

        db.disconnect()

        # Verificar resultado
        if df.empty or df.iloc[0].get("status") == "NO_MATCH":
            logger.warning(f"No se encontró niño con nombre: {req.nombre_nino}")
            return RecomendacionPersonalizadaResponse(
                recomendacion=f"No encontré información del niño '{req.nombre_nino}'. Por favor verifica el nombre o registra al niño primero.",
                datos_nino={},
                recetas_disponibles=[],
                estado_nutricional={},
                used_llm=False,
            )

        # Parsear datos del niño y recetas
        first_row = df.iloc[0]
        datos_nino = {
            "id": int(first_row.get("nin_id", 0)),
            "nombre": first_row.get("nin_nombres", req.nombre_nino),
            "estado_nutricional": first_row.get("en_clasificacion", ""),
            "fecha_nacimiento": None,
            "sexo": "",
            "peso_kg": None,
            "talla_cm": None,
            "imc": None,
            "edad_meses": None,
            "diagnostico": first_row.get("en_clasificacion", ""),
            "entidad": "",
            "codigo_entidad": "",
        }

        estado_nutricional = {
            "diagnostico": first_row.get("en_clasificacion", ""),
            "estado_actual": first_row.get("en_clasificacion", ""),
            "imc": None,
            "peso_kg": None,
            "talla_cm": None,
            "edad_meses": None,
            "sexo": None,
        }

        recetas = []
        for _, row in df.iterrows():
            recetas.append(
                {
                    "id": int(row.get("rec_id", 0)),
                    "nombre": row.get("rec_nombre", ""),
                    "calorias": float(row.get("kcal", 0)),
                    "proteinas": float(row.get("proteina_g", 0)),
                    "carbohidratos": float(row.get("carbohidratos_g", 0))
                    if "carbohidratos_g" in row
                    else 0.0,
                    "grasas": float(row.get("grasas_g", 0)) if "grasas_g" in row else 0.0,
                    "fibra": float(row.get("fibra_g", 0)),
                    "hierro": float(row.get("hierro_mg", 0)),
                    "costo": float(row.get("costo_soles_aprox", 0)),
                    "puntuacion": float(row.get("score", 0)),
                }
            )

        # Crear prompt para el LLM
        prompt = crear_prompt_recomendacion(
            datos_nino, estado_nutricional, recetas, tipo_comida_norm, req.pregunta_usuario
        )

        # Consultar al agente LLM
        recomendacion = consultar_agente_llm(prompt)
        used_llm = "El servicio de recomendaciones no está disponible" not in recomendacion

        logger.info(f"✅ Recomendación generada exitosamente (LLM usado: {used_llm})")

        return RecomendacionPersonalizadaResponse(
            recomendacion=recomendacion,
            datos_nino=datos_nino,
            recetas_disponibles=recetas,
            estado_nutricional=estado_nutricional,
            used_llm=used_llm,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en chat_recomendacion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generando recomendación: {str(e)}")


# Endpoints de predicción ML eliminados - ahora usamos LLM + procedimientos almacenados
