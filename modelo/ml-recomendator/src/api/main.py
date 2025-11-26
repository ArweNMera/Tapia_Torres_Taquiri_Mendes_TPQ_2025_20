"""
FastAPI main app
Configuración central de la aplicación
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Cargar variables de entorno
load_dotenv()

# Importar endpoints
from src.api.endpoints import (
    models_info_router,
    nutritional_training_router,
    recommendations_router,
    training_router,
)

# Configurar logging basado en variable de entorno
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
logger.info(f"🚀 Logging configurado en nivel: {log_level}")


def create_app() -> FastAPI:
    """
    Factory function para crear la aplicación FastAPI

    Returns:
        FastAPI app configured and ready to use
    """

    app = FastAPI(
        title="ML Nutrition Recommender API",
        description="API para recomendaciones de menús y cálculos nutricionales",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configurar CORS para integración con backend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8000",  # Backend principal
            "http://localhost:3000",  # Frontend
            "http://localhost:8001",  # Este servicio
            "http://127.0.0.1:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8001",
            "*",  # En producción, especificar dominios reales
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Event handlers
    @app.on_event("startup")
    async def startup_event():
        """Ejecutar al iniciar la aplicación"""
        logger.info("🚀 ML Nutrition Recommender API iniciada")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Ejecutar al cerrar la aplicación"""
        logger.info("🛑 ML Nutrition Recommender API cerrada")

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint

        Returns:
            Status de la aplicación
        """
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "ml-nutrition-recommender",
                "version": "1.0.0",
            },
        )

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """
        Root endpoint con información de la API

        Returns:
            Información de bienvenida
        """
        return {
            "message": "ML Nutrition Recommender API",
            "version": "1.0.0",
            "endpoints": {
                "docs": "/docs",
                "redoc": "/redoc",
                "health": "/health",
                "recommendations": "/api/v1/recommendations",
                "nutrition": "/api/v1/nutrition",
                "meals": "/api/v1/meals",
            },
        }

    # Exception handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        """Manejar errores de validación"""
        return JSONResponse(
            status_code=400, content={"detail": str(exc), "error_type": "ValueError"}
        )

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(request, exc):
        """Manejar errores de runtime"""
        return JSONResponse(
            status_code=500, content={"detail": str(exc), "error_type": "RuntimeError"}
        )

    # Incluir routers
    app.include_router(recommendations_router)
    app.include_router(models_info_router)
    app.include_router(training_router)
    app.include_router(nutritional_training_router)

    logger.info("✅ FastAPI app creada exitosamente con endpoints")
    return app


# Crear instancia global
app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
