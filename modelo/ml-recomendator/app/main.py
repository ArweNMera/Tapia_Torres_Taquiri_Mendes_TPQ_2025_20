from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import math
import pandas as pd

# Ensure we can import from src/
import sys
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

try:
    from src.llm.assist import summarize_with_llm, format_recommender_prompt
except Exception:
    summarize_with_llm = None  # type: ignore
    format_recommender_prompt = None  # type: ignore
try:
    from src.llm.client import get_llm_client
except Exception:
    get_llm_client = None  # type: ignore


app = FastAPI(title="ml-recomendator", version="0.1.0")

# CORS (por si llamas desde otro host)
allowed = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in allowed if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- WHO LMS loading utilities (local, similar to pipeline.label_dataset) ---

def _load_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalize column names
    cols = {c: c.strip().replace(" ", "_") for c in df.columns}
    df = df.rename(columns=cols)
    if "Month" in df.columns:
        df = df.rename(columns={"Month": "month"})
    for c in list(df.columns):
        if c.lower() == "month":
            df = df.rename(columns={c: "month"})
            break
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
            parts.append(df[["month", "L", "M", "S"]].assign(sex=sex))
    if not parts:
        raise FileNotFoundError(f"No WHO LMS tables found for sex={sex} under {who_dir}")
    out = pd.concat(parts, ignore_index=True)
    out["month"] = out["month"].astype(int)
    return out.drop_duplicates(subset=["sex", "month"]).sort_values(["sex", "month"]).reset_index(drop=True)


def _load_lms(who_dir: Path) -> pd.DataFrame:
    return pd.concat([_lms_cat(who_dir, "M"), _lms_cat(who_dir, "F")], ignore_index=True)


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
except Exception as e:
    LMS = None  # Lazy load on first call


@app.get("/health")
def health():
    return {"status": "ok"}


class PredictBAZRequest(BaseModel):
    age_months: int
    sex: str = Field(description="M/F")
    BMI: Optional[float] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None
    prefer_llm: bool = True
    features: Dict[str, Any] = Field(default_factory=dict, description="Optional context for summary")


class PredictBAZResponse(BaseModel):
    bmi: float
    baz: float
    label_status: int
    label_text: str
    summary: str
    used_llm: bool


def _classify_from_baz(z: float) -> int:
    if z < -3 or z > 3:
        return 2
    if (-3 <= z < -2) or (2 < z <= 3):
        return 1
    return 0


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
        bmi = float(req.weight_kg) / (h_m ** 2)
    L, M, S = _nearest_lms(LMS, sex, int(round(req.age_months)))
    baz = _baz_from_bmi(bmi, L, M, S)
    label = _classify_from_baz(baz)
    label_map = {0: "normal", 1: "moderado", 2: "severo"}

    # Build simple scores for summary
    if abs(baz) > 3:
        scores = {"severo": 0.9, "moderado": 0.1, "normal": 0.0}
    elif 2 < abs(baz) <= 3:
        scores = {"moderado": 0.8, "severo": 0.2, "normal": 0.0}
    else:
        scores = {"normal": 0.85, "moderado": 0.1, "severo": 0.05}

    used_llm = False
    summary: Optional[str] = None
    if req.prefer_llm and summarize_with_llm is not None:
        try:
            base_features = {"age_months": req.age_months, "sex": sex, "BMI": round(bmi, 2), **(req.features or {})}
            summary = summarize_with_llm(base_features, scores)
            used_llm = summary is not None
        except Exception:
            summary = None
            used_llm = False
    if not summary:
        if format_recommender_prompt is not None:
            base_features = {"age_months": req.age_months, "sex": sex, "BMI": round(bmi, 2), **(req.features or {})}
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
    features: Dict[str, Any]
    scores: Dict[str, float]
    prefer_llm: bool = True


class SummaryResponse(BaseModel):
    text: str
    used_llm: bool


@app.post("/ml/summary", response_model=SummaryResponse)
def summarize(req: SummaryRequest) -> SummaryResponse:
    used_llm = False
    text: Optional[str] = None
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


# --- Simple chat passthrough endpoint ---

class ChatRequest(BaseModel):
    message: str
    system: Optional[str] = Field(
        default=(
            "Eres un asistente que explica y responde de forma clara, "
            "sin emitir consejo médico."
        )
    )


class ChatResponse(BaseModel):
    reply: str
    used_llm: bool


@app.post("/ml/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    # If LLM configured, use it; else deterministic echo
    if get_llm_client is not None:
        try:
            client = get_llm_client()
            reply = client.chat(system_message=req.system or "", user_message=req.message)
            if reply:
                return ChatResponse(reply=reply, used_llm=True)
        except Exception:
            pass
    # Fallback offline response
    echo = f"[offline] Sin LLM configurado. Eco: {req.message}"
    return ChatResponse(reply=echo, used_llm=False)
