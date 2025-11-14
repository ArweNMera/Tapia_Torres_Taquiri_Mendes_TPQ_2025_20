# ============================================
# Stage 1: Dependencies - Instalar dependencias
# ============================================
FROM node:20-alpine AS dependencies

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias (con caché optimizado)
RUN npm ci --prefer-offline --no-audit

# ============================================
# Stage 2: Development - Para desarrollo local
# ============================================
FROM node:20-alpine AS development

WORKDIR /app

# Copiar dependencias instaladas
COPY --from=dependencies /app/node_modules ./node_modules

# Copiar package files
COPY package*.json ./

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 5175

# Comando para desarrollo con hot-reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ============================================
# Stage 3: Production - Modo desarrollo (sin build)
# ============================================
FROM node:20-alpine AS production

WORKDIR /app

# Copiar dependencias instaladas
COPY --from=dependencies /app/node_modules ./node_modules

# Copiar package files
COPY package*.json ./

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 5175

# Comando para producción (usa dev server, más confiable)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5175"]
