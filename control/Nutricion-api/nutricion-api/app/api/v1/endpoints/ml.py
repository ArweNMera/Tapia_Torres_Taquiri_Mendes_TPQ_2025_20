from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Try to import assist from ml-recomendator; add path fallback if needed
try:
    from src.llm.assist import summarize_with_llm, format_recommender_prompt
except Exception:  # pragma: no cover
    import sys
    from pathlib import Path
    here = Path(__file__).resolve()
    # Search upwards for modelo/ml-recomendator
    root = here
    for _ in range(10):
        candidate = root / "modelo" / "ml-recomendator"
        if (candidate / "src").exists():
            sys.path.append(str(candidate))
            break
        root = root.parent
    # retry import
    from src.llm.assist import summarize_with_llm, format_recommender_prompt  # type: ignore


router = APIRouter()


class SummaryRequest(BaseModel):
    features: Dict[str, Any]
    scores: Dict[str, float]
    prefer_llm: bool = True


class SummaryResponse(BaseModel):
    text: str
    used_llm: bool


@router.post("/summary", response_model=SummaryResponse)
def summarize(req: SummaryRequest) -> SummaryResponse:
    # First try LLM if preferred
    used_llm = False
    text: Optional[str] = None
    if req.prefer_llm:
        try:
            text = summarize_with_llm(req.features, req.scores)
            used_llm = text is not None
        except Exception as e:
            # Fall back silently to offline
            text = None
            used_llm = False
    if not text:
        try:
            text = format_recommender_prompt(req.features, req.scores)
        except Exception as e:  # Should not happen; guard anyway
            raise HTTPException(status_code=500, detail=f"No se pudo generar resumen: {e}")
    return SummaryResponse(text=text, used_llm=used_llm)

