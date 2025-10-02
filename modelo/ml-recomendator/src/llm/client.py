from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    def load_dotenv(*args, **kwargs):  # type: ignore
        return False

import httpx


@dataclass
class OpenAICompatClient:
    base_url: str
    api_key: str
    model: str
    temperature: float = 0.2
    max_tokens: int = 256
    timeout: float = 30.0

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, system_message: str, user_message: str) -> str:
        url = self.base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(url, headers=self._headers(), json=payload)
            r.raise_for_status()
            data = r.json()
        # OpenAI-compatible response parsing
        return (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )


def get_llm_client() -> OpenAICompatClient:
    """Factory that reads environment vars and returns a client.

    Required env vars:
      - LLM_API_KEY
      - LLM_BASE_URL (e.g., https://api.openai.com/v1 or your gateway)
      - LLM_MODEL (e.g., gpt-4o-mini / llama3 / etc.)
    Optional:
      - LLM_TEMPERATURE (float)
      - LLM_MAX_TOKENS (int)
      - LLM_TIMEOUT (seconds)
    """
    # Load from local .env if present (modelo/ml-recomendator/.env)
    env_path = Path(__file__).resolve().parents[2] / ".env"  # .../ml-recomendator/.env
    load_dotenv(dotenv_path=str(env_path))

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL")
    if not api_key or not base_url or not model:
        raise RuntimeError("LLM env vars not fully configured (LLM_API_KEY, LLM_BASE_URL, LLM_MODEL)")
    temp = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    max_toks = int(os.getenv("LLM_MAX_TOKENS", "256"))
    timeout = float(os.getenv("LLM_TIMEOUT", "30"))
    return OpenAICompatClient(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=temp,
        max_tokens=max_toks,
        timeout=timeout,
    )
