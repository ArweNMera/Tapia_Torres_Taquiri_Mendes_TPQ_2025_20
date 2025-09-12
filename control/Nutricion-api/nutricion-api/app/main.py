from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.api import api_router
from .core.config import settings
import os

# ÚNICA instancia de la app
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Orígenes permitidos (extensible vía variable FRONTEND_ORIGINS separada por comas)
frontend_origins_env = os.getenv("FRONTEND_ORIGINS")
if frontend_origins_env:
    allowed_origins = [o.strip() for o in frontend_origins_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

# Middleware CORS (incluye OPTIONS automáticamente)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Incluye OPTIONS
    allow_headers=["*"],
    expose_headers=["Authorization"],
)

# Rutas API
app.include_router(api_router, prefix=settings.API_V1_STR)

# (Opcional) Endpoint de salud rápido
@app.get("/health", tags=["health"])  # útil para pruebas rápidas
def health():
    return {"status": "ok"}

