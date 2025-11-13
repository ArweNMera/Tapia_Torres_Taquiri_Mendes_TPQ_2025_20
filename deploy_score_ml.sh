#!/bin/bash

# Script para desplegar las actualizaciones del score ML a Google Cloud Run
# Fecha: 2025-11-05
# Cambios: Implementación de visualización del score ML del modelo de recomendación

set -e

echo "🚀 ======================================"
echo "   DESPLIEGUE DE SCORE ML A PRODUCCIÓN"
echo "   ======================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuración
PROJECT_ID="nutricion-dd80c"
REGION="us-east1"

echo -e "${BLUE}📋 Configuración:${NC}"
echo "   - Proyecto: $PROJECT_ID"
echo "   - Región: $REGION"
echo ""

# Verificar que gcloud está instalado y autenticado
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ Error: gcloud CLI no está instalado${NC}"
    exit 1
fi

echo -e "${YELLOW}🔐 Configurando proyecto de GCP...${NC}"
gcloud config set project $PROJECT_ID

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📦 PASO 1: DESPLEGAR BACKEND${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd control/Nutricion-api

echo -e "${YELLOW}🔨 Construyendo imagen del backend...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/nutricion-backend

echo -e "${YELLOW}🚀 Desplegando backend a Cloud Run...${NC}"
gcloud run deploy nutricion-backend \
  --image gcr.io/$PROJECT_ID/nutricion-backend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 300 \
  --max-instances 10

echo -e "${GREEN}✅ Backend desplegado exitosamente${NC}"
echo ""

cd ../..

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🎨 PASO 2: DESPLEGAR FRONTEND${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd vista/AppSaludable

echo -e "${YELLOW}📦 Instalando dependencias del frontend...${NC}"
npm install

echo -e "${YELLOW}🔨 Construyendo frontend...${NC}"
npm run build

echo -e "${YELLOW}🚀 Desplegando frontend a Cloud Run...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/nutricion-frontend

gcloud run deploy nutricion-frontend \
  --image gcr.io/$PROJECT_ID/nutricion-frontend \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 256Mi

echo -e "${GREEN}✅ Frontend desplegado exitosamente${NC}"
echo ""

cd ../..

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ DESPLIEGUE COMPLETADO${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📊 Servicios actualizados:${NC}"
echo "   ✓ Backend: Con soporte para mei_score_ml"
echo "   ✓ Frontend: Visualización de badges con porcentaje IA"
echo ""
echo -e "${YELLOW}🔍 URLs de los servicios:${NC}"
gcloud run services describe nutricion-backend --region=$REGION --format='value(status.url)'
gcloud run services describe nutricion-frontend --region=$REGION --format='value(status.url)'
echo ""
echo -e "${GREEN}🎉 ¡Listo! El score ML del modelo ahora se visualiza en producción${NC}"
