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
# Stage 3: Builder - Construir para producción
# ============================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar dependencias instaladas
COPY --from=dependencies /app/node_modules ./node_modules

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# ============================================
# Stage 4: Production - Servir con Node (sin nginx)
# ============================================
FROM node:20-alpine AS production

WORKDIR /app

# Instalar serve para servir archivos estáticos
RUN npm install -g serve

# Copiar build desde builder
COPY --from=builder /app/dist ./dist

# Exponer puerto
EXPOSE 5175

# Servir con serve
CMD ["serve", "-s", "dist", "-l", "5175"]
