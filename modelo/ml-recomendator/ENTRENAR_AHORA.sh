#!/bin/bash

# Script SIMPLE para entrenar el modelo Bayesian + Random Forest

echo "=================================="
echo "🎯 ENTRENANDO MODELO"
echo "   Naive Bayes + Random Forest"
echo "=================================="
echo ""

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Entrenar directamente
python3 src/pipeline/train_model_directo.py \
    --data-source db \
    --output models/directo \
    --test-size 0.2

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ ENTRENAMIENTO COMPLETADO"
    echo "=================================="
    echo ""
    echo "📁 Archivos generados:"
    echo "   • models/directo/modelo_directo.pkl"
    echo "   • models/directo/scaler_directo.pkl"
    echo "   • models/directo/metricas_directo.json"
    echo ""
    echo "🧪 Probar el modelo:"
    echo "   python3 scripts/test_bayesian_rf.py"
    echo ""
else
    echo ""
    echo "❌ Error en el entrenamiento"
    exit 1
fi
