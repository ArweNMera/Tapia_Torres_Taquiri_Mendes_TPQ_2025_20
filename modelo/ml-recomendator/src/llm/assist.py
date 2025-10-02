"""
LLM assist utilities: explain predictions in simple language.
By default works offline with deterministic text. If environment
variables for an LLM provider are set, it can call an external
LLM via an OpenAI-compatible API to improve phrasing.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import os

try:
    # Lazy import; only used if env is configured
    from .client import get_llm_client
except Exception:  # pragma: no cover - keep assist working without client
    get_llm_client = None  # type: ignore


@dataclass
class Explanation:
    title: str
    summary: str
    bullet_points: List[str]


def explain_baz_prediction(age_months: int, sex: str, bmi: float, baz: float, status_label: int) -> Explanation:
    # Map status to readable words
    label_map = {0: "dentro del rango esperado", 1: "riesgo/moderado", 2: "alto/desviado"}
    title = "Resumen de estimación del estado nutricional"
    summary = (
        f"Para un niño de {age_months} meses, sexo {sex}, con BMI {bmi:.1f}, "
        f"el BAZ estimado es {baz:.2f} y se clasifica como {label_map.get(status_label, 'desconocido')} (solo informativo, no consejo médico)."
    )
    bullets = [
        "BAZ usa tablas de referencia OMS por edad y sexo (método LMS).",
        "El resultado es orientativo. Consulte a personal de salud para evaluación clínica.",
    ]
    return Explanation(title=title, summary=summary, bullet_points=bullets)


def explain_classifier_scores(scores: Dict[str, float]) -> Explanation:
    # scores: e.g., {"normal": 0.82, "moderado": 0.12, "severo": 0.06}
    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top = ordered[0][0] if ordered else "desconocido"
    title = "Resumen de clasificación"
    summary = (
        f"La clase con mayor probabilidad es: {top}. "
        "Las probabilidades están calibradas para interpretación orientativa."
    )
    bullets = [f"{k}: {v:.2%}" for k, v in ordered[:3]]
    return Explanation(title=title, summary=summary, bullet_points=bullets)


def format_recommender_prompt(features: Dict[str, Any], scores: Dict[str, float]) -> str:
    """Format a structured prompt or message to feed a recommender system.
    This intentionally avoids any medical advice; summarizes signals only.
    """
    parts = ["Contexto del caso:"]
    for k, v in features.items():
        parts.append(f"- {k}: {v}")
    parts.append("\nSeñales del modelo:")
    for k, v in sorted(scores.items(), key=lambda kv: kv[1], reverse=True):
        parts.append(f"- {k}: {v:.2%}")
    parts.append(
        "\nNota: Este resumen es informativo y no constituye consejo médico."
    )
    return "\n".join(parts)


def summarize_with_llm(features: Dict[str, Any], scores: Dict[str, float]) -> Optional[str]:
    """Optional LLM summary if env is configured; otherwise returns None.

    Required env vars for OpenAI-compatible endpoints:
      - LLM_API_KEY
      - LLM_BASE_URL (e.g., https://api.openai.com/v1 or your gateway)
      - LLM_MODEL (e.g., gpt-4o-mini / llama3 / etc.)
    Optional: LLM_TEMPERATURE, LLM_MAX_TOKENS
    """
    if get_llm_client is None:
        return None
    # Only proceed if API key present
    if not os.getenv("LLM_API_KEY"):
        return None
    try:
        client = get_llm_client()
    except Exception:
        return None

    system = (
        "Eres un asistente que explica resultados de modelos de forma "
        "clara y no clínica. No des consejos médicos."
    )
    prompt = format_recommender_prompt(features, scores)
    try:
        return client.chat(system_message=system, user_message=prompt)
    except Exception:
        return None
