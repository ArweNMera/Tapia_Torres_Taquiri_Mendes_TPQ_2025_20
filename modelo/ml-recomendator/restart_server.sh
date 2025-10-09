#!/bin/bash

# Script para reiniciar el servidor FastAPI con el modelo ML actualizado

echo "🔄 Reiniciando servidor FastAPI con modelo ML..."
echo ""

# Verificar que el modelo existe
if [ ! -f "models/rf_model.pkl" ]; then
    echo "❌ ERROR: Modelo no encontrado en models/rf_model.pkl"
    echo "   Ejecuta primero: python3 src/pipeline/train_model.py --data data/raw/surveys/datos_completos_oms_reales.csv --model rf --output models/ --use-cv --cv-folds 5"
    exit 1
fi

echo "✅ Modelo encontrado: models/rf_model.pkl"
echo ""

# Matar proceso anterior si existe
echo "🔍 Buscando procesos uvicorn anteriores..."
pkill -f "uvicorn app.main:app" 2>/dev/null
sleep 1

# Iniciar servidor
echo "🚀 Iniciando servidor en http://localhost:8003"
echo ""
echo "📊 Endpoints disponibles:"
echo "   - GET  /health                      - Health check"
echo "   - GET  /ml/model_info               - Info del modelo"
echo "   - POST /ml/predict_direct           - Predicción directa"
echo "   - POST /ml/analisis_nutricional     - Análisis completo"
echo ""
echo "🧪 Para probar: python scripts/test_modelo_api.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Iniciar servidor
uvicorn app.main:app --reload --port 8003
