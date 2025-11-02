# Modelo ML - FastAPI
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Configurar PYTHONPATH para que Python encuentre el módulo src
# Como WORKDIR es /app y el código está en /app/src, usamos /app como base
ENV PYTHONPATH=/app

# Exponer puerto (Cloud Run asigna dinámicamente)
EXPOSE 8080

# Comando para producción (sin --reload para Cloud Run)
# Usa la variable $PORT de Cloud Run, por defecto 8080
CMD exec uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8080}
