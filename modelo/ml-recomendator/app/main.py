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
        "db_available": DatabaseConnector is not None
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
    """Consulta las mejores recetas usando sp_top_recetas_por_nombre."""
    if DatabaseConnector is None:
        raise HTTPException(503, "Conector de BD no disponible")
    
    try:
        logger.info(f"Consultando recetas para niño {id_nino}, tipo: {tipo_comida}")
        
        # 1. Obtener nombre del niño
        datos_nino = consultar_datos_nino(id_nino)
        nombre_nino = datos_nino["nombre"]
        
        # 2. Normalizar tipo de comida
        tipo_comida_norm = tipo_comida.upper()
        if tipo_comida_norm not in ["DESAYUNO", "ALMUERZO", "CENA"]:
            logger.warning(f"Tipo de comida '{tipo_comida}' no válido, usando DESAYUNO")
            tipo_comida_norm = "DESAYUNO"
        
        # 3. Ejecutar procedimiento almacenado
        db = DatabaseConnector.from_env()
        db.connect()
        
        query = "CALL sp_top_recetas_por_nombre(%s, %s, %s)"
        df = db.execute_query(query, (nombre_nino, tipo_comida_norm, 5))
        
        db.disconnect()
        
        # 4. Verificar resultado
        if df.empty:
            logger.warning(f"No se encontraron recetas para {nombre_nino}")
            return []
        
        # 5. Verificar status
        if df.iloc[0].get("status") == "NO_MATCH":
            logger.warning(f"No se encontró niño con nombre: {nombre_nino}")
            return []
        
        # 6. Parsear recetas
        recetas = []
        for _, row in df.iterrows():
            recetas.append({
                "id": int(row.get("rec_id", 0)),
                "nombre": row.get("rec_nombre", ""),
                "calorias": float(row.get("kcal", 0)),
                "proteinas": float(row.get("proteina_g", 0)),
                "carbohidratos": float(row.get("carbohidratos_g", 0)),
                "grasas": float(row.get("grasas_g", 0)),
                "fibra": float(row.get("fibra_g", 0)),
                "hierro": float(row.get("hierro_mg", 0)),
                "costo": float(row.get("costo_soles_aprox", 0)),
                "puntuacion": float(row.get("score", 0))
            })
        
        logger.info(f"✅ Encontradas {len(recetas)} recetas para {nombre_nino}")
        return recetas
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error consultando recetas: {str(e)}")
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
    """Crea el prompt para el LLM con toda la información."""
    
    sexo_texto = "Masculino" if datos_nino.get("sexo") == "M" else "Femenino"
    
    prompt = f"""Eres un nutricionista especializado en alimentación infantil. Un padre/madre te consulta sobre recomendaciones nutricionales para su hijo/a.

DATOS DEL NIÑO:
- Nombre: {datos_nino.get('nombre', 'No especificado')}
- Edad: {datos_nino.get('edad_meses', 'No especificada')} meses
- Sexo: {sexo_texto}
- Peso: {datos_nino.get('peso_kg', 'No especificado')} kg
- Talla: {datos_nino.get('talla_cm', 'No especificada')} cm
- IMC: {datos_nino.get('imc', 'No especificado')}
- Estado nutricional: {estado_nutricional.get('diagnostico', 'No especificado')}
- Diagnóstico: {estado_nutricional.get('estado_actual', 'No especificado')}

RECETAS DISPONIBLES PARA {tipo_comida.upper()}:
"""
    
    if recetas:
        for i, receta in enumerate(recetas[:5], 1):
            prompt += f"""
{i}. {receta.get('nombre', 'Sin nombre')}
   - Calorías: {receta.get('calorias', 0):.0f} kcal
   - Proteínas: {receta.get('proteinas', 0):.1f}g
   - Carbohidratos: {receta.get('carbohidratos', 0):.1f}g
   - Grasas: {receta.get('grasas', 0):.1f}g
   - Fibra: {receta.get('fibra', 0):.1f}g
   - Hierro: {receta.get('hierro', 0):.1f}mg
   - Costo aproximado: S/ {receta.get('costo', 0):.2f}
   - Puntuación nutricional: {receta.get('puntuacion', 0):.1f}/10
"""
    else:
        prompt += "\nNo hay recetas específicas disponibles en la base de datos para este tipo de comida.\n"
    
    if pregunta_usuario:
        prompt += f"""

PREGUNTA ESPECÍFICA DEL USUARIO: {pregunta_usuario}

INSTRUCCIONES:
1. Responde de manera clara, amable y profesional a la pregunta específica
2. Considera el estado nutricional del niño al hacer recomendaciones
3. Si hay recetas disponibles, sugiere las más apropiadas
4. Incluye porciones adecuadas para la edad del niño
5. Menciona cualquier precaución nutricional importante
6. Si no hay recetas específicas, da recomendaciones generales saludables
7. Mantén un tono positivo y alentador para los padres
8. No emitas diagnósticos médicos ni reemplaces la consulta profesional

RECOMENDACIÓN PERSONALIZADA:"""
    else:
        prompt += f"""

INSTRUCCIONES:
Proporciona una recomendación nutricional completa para {tipo_comida} considerando:
1. El estado nutricional actual del niño
2. Las mejores recetas disponibles (ordenadas por puntuación)
3. Porciones apropiadas para su edad ({datos_nino.get('edad_meses', 0)} meses)
4. Beneficios nutricionales de las recomendaciones
5. Consejos prácticos para una alimentación saludable
6. Consideraciones económicas (costo de las recetas)

Mantén un tono amable, profesional y alentador. No emitas diagnósticos médicos.

RECOMENDACIÓN PERSONALIZADA:"""
    
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
        
        system_message = """Eres un nutricionista infantil experto especializado en alimentación en Perú. 

IMPORTANTE:
- Proporciona recomendaciones seguras y basadas en evidencia científica
- Adapta las recomendaciones a la edad del niño
- Considera el contexto económico y cultural peruano
- Usa lenguaje claro y amigable para padres
- NO emitas diagnósticos médicos
- NO reemplaces la consulta con un profesional de salud
- Enfócate en recomendaciones nutricionales prácticas y aplicables
- Menciona porciones específicas apropiadas para la edad
- Si el niño tiene desnutrición o sobrepeso, enfatiza la importancia de seguimiento médico"""
        
        respuesta = client.chat(
            system_message=system_message,
            user_message=prompt
        )
        
        if respuesta and len(respuesta.strip()) > 10:
            logger.info(f"✅ LLM respondió exitosamente ({len(respuesta)} chars)")
            return respuesta
        else:
            logger.warning("LLM retornó respuesta vacía o muy corta")
            return "No pude generar una recomendación personalizada. Te recomiendo consultar con un nutricionista profesional."
    
    except Exception as e:
        logger.error(f"Error consultando LLM: {str(e)}")
        return "Hubo un problema técnico generando la recomendación. Por favor, intenta nuevamente o consulta con un especialista."


@app.post("/ml/recomendacion_personalizada", response_model=RecomendacionPersonalizadaResponse)
def generar_recomendacion_personalizada(req: RecomendacionPersonalizadaRequest) -> RecomendacionPersonalizadaResponse:
    """
    Genera una recomendación nutricional personalizada para un niño específico.

    Utiliza datos del niño, su estado nutricional, recetas disponibles y un agente LLM
    para proporcionar recomendaciones personalizadas según el tipo de comida solicitado.
    """
    try:
        logger.info(f"📝 Generando recomendación para niño {req.id_nino}, tipo: {req.tipo_comida}")
        
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
        used_llm = "El servicio de recomendaciones no está disponible" not in recomendacion

        logger.info(f"✅ Recomendación generada exitosamente (LLM usado: {used_llm})")
        
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


# Endpoints de predicción ML eliminados - ahora usamos LLM + procedimientos almacenados


