"""
Cliente HTTP para comunicarse con el servidor ML de recomendaciones
"""

import logging
from typing import Any, Dict, List

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class MLRecommenderClient:
    """Cliente para el servidor ML de recomendaciones de menús"""

    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Inicializa el cliente ML

        Args:
            base_url: URL base del servidor ML (default: http://localhost:8001)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = 30.0

    async def generar_plan_semanal_ml(
        self,
        child_id: int,
        nutrition_status: str,
        allergies: List[str] = None,
        preferences: Dict[str, Any] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """
        Genera un plan semanal de comidas usando el modelo ML entrenado

        Args:
            child_id: ID del niño
            nutrition_status: Estado nutricional (NORMAL, DESNUTRICION, etc.)
            allergies: Lista de alergias del niño
            preferences: Diccionario de preferencias (opcional)
            days: Número de días del plan (1-7)

        Returns:
            Dict con el plan semanal generado

        Raises:
            HTTPException: Si el servidor ML no está disponible o hay error
        """
        allergies = allergies or []
        preferences = preferences or {}

        payload = {
            "child_id": str(child_id),
            "nutrition_status": nutrition_status,
            "allergies": allergies,
            "preferences": preferences,
            "days": min(days, 7),
        }

        logger.info(f"📡 Llamando servidor ML para generar plan semanal (niño {child_id})")
        logger.debug(f"   Payload: {payload}")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/recommendations/weekly-plan",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(
                        f"✅ Plan semanal generado: {data.get('total_days')} días, "
                        f"{data.get('total_meals')} comidas"
                    )
                    return data
                else:
                    error_detail = response.text
                    logger.error(
                        f"❌ Error del servidor ML: {response.status_code} - {error_detail}"
                    )
                    raise HTTPException(
                        status_code=503,
                        detail=f"Error en servidor ML: {response.status_code} - {error_detail}",
                    )

        except httpx.TimeoutException as e:
            logger.error(f"⏱️ Timeout conectando con servidor ML: {e}")
            raise HTTPException(
                status_code=504,
                detail="Timeout esperando respuesta del servidor ML. Intente nuevamente.",
            )
        except httpx.ConnectError as e:
            logger.error(f"🔌 Error de conexión con servidor ML: {e}")
            raise HTTPException(
                status_code=503,
                detail=(
                    "No se pudo conectar con el servidor ML. "
                    "Verifique que esté ejecutándose en http://localhost:8001"
                ),
            )
        except Exception as e:
            logger.error(f"❌ Error inesperado llamando servidor ML: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Error comunicándose con servidor ML: {str(e)}"
            )

    async def entrenar_modelo(self) -> Dict[str, Any]:
        """
        Solicita entrenamiento rápido del modelo ML

        Returns:
            Dict con resultados del entrenamiento y métricas
        """
        logger.info("🤖 Solicitando entrenamiento del modelo ML...")

        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/models/train/quick",
                    json={},
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"✅ Modelo entrenado: {data.get('metrics', {})}")
                    return data
                else:
                    logger.error(f"❌ Error entrenando modelo: {response.status_code}")
                    raise HTTPException(
                        status_code=503, detail=f"Error entrenando modelo: {response.status_code}"
                    )

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Timeout entrenando modelo. El proceso continúa en segundo plano.",
            )
        except Exception as e:
            logger.error(f"❌ Error entrenando modelo: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error entrenando modelo: {str(e)}")

    async def verificar_salud(self) -> bool:
        """
        Verifica si el servidor ML está disponible

        Returns:
            bool: True si el servidor está disponible
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/v1/models/info")
                return response.status_code == 200
        except Exception:
            return False


ml_client = MLRecommenderClient()
