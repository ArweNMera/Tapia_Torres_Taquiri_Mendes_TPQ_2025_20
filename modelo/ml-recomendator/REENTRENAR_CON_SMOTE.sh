#!/bin/bash

echo "=================================="
echo "🔧 INSTALANDO DEPENDENCIAS"
echo "=================================="
echo ""

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Instalar imbalanced-learn
echo "📦 Instalando imbalanced-learn..."
pip install imbalanced-learn>=0.11.0

if [ $? -ne 0 ]; then
    echo "❌ Error instalando imbalanced-learn"
    exit 1
fi

echo ""
echo "=================================="
echo "🎯 REENTRENANDO CON SMOTE"
echo "=================================="
echo ""
echo "SMOTE (Synthetic Minority Over-sampling Technique)"
echo "Balancea las clases generando ejemplos sintéticos"
echo ""

# Entrenar
python3 src/pipeline/train_model_directo.py \
    --data-source db \
    --output models/directo \
    --test-size 0.2

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ REENTRENAMIENTO COMPLETADO"
    echo "=================================="
    echo ""
    echo "🧪 Probar el modelo:"
    echo "   python3 scripts/test_bayesian_rf.py"
    echo ""
else
    echo ""
    echo "❌ Error en el reentrenamiento"
    exit 1
fi
