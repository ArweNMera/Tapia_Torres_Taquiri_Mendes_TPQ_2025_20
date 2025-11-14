# ============================================
# Stage 1: Builder - Instalar dependencias Python
# ============================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================
# Stage 2: Development - Para desarrollo local
# ============================================
FROM python:3.11-slim AS development

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8080

# Comando para desarrollo con hot-reload
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]

# ============================================
# Stage 3: Production - Para producción
# ============================================
FROM python:3.11-slim AS production

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copiar todo el código (más simple y seguro)
COPY . .

# Exponer puerto
EXPOSE 8080

# Comando para producción (sin workers por ahora, para debug)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
