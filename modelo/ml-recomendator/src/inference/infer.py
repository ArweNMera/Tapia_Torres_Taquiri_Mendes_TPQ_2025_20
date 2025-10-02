from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import joblib
import pandas as pd
from typing import Dict, Any, Optional

try:
    # Optional: LLM-backed explanations
    from ..llm.assist import summarize_with_llm, format_recommender_prompt
except Exception:  # pragma: no cover
    summarize_with_llm = None  # type: ignore
    format_recommender_prompt = None  # type: ignore

@dataclass
class ModelBundle:
    model: any
    preprocess: any


def load_bundle(model_path: Path, preprocess_path: Path) -> ModelBundle:
    model = joblib.load(model_path)
    pre = joblib.load(preprocess_path)
    return ModelBundle(model=model, preprocess=pre)


def predict_proba(bundle: ModelBundle, X: pd.DataFrame):
    Xp = bundle.preprocess.transform(X)
    return bundle.model.predict_proba(Xp)


def summarize_prediction(features: Dict[str, Any], scores: Dict[str, float], prefer_llm: bool = True) -> str:
    """Return a human-friendly summary of model scores.

    If LLM env is configured and prefer_llm=True, uses it; otherwise
    returns a deterministic offline text based on the features/scores.
    """
    text: Optional[str] = None
    if prefer_llm and summarize_with_llm is not None:
        try:
            text = summarize_with_llm(features, scores)
        except Exception:
            text = None
    if not text:
        if format_recommender_prompt is not None:
            text = format_recommender_prompt(features, scores)
        else:
            # Minimal fallback
            top = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
            best = f"Mejor clase: {top[0][0]} ({top[0][1]:.2%})" if top else "Sin puntuaciones"
            text = best
    return text
