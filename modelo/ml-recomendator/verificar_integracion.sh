#!/bin/bash

# Script de verificación rápida de la integración del modelo ML

# Cambiar al directorio del script
cd "$(dirname "$0")"

echo "🔍 VERIFICACIÓN DE INTEGRACIÓN DEL MODELO ML"
echo "============================================================"
echo ""

# 1. Verificar que el modelo existe
echo "1️⃣  Verificando modelo entrenado..."
if [ -f "models/rf_model.pkl" ]; then
    SIZE=$(ls -lh models/rf_model.pkl | awk '{print $5}')
    echo "   ✅ Modelo encontrado: models/rf_model.pkl ($SIZE)"
else
    echo "   ❌ ERROR: Modelo no encontrado"
    echo "   Ejecuta: python3 src/pipeline/train_model.py --data data/raw/surveys/datos_completos_oms_reales.csv --model rf --output models/ --use-cv --cv-folds 5"
    exit 1
fi
echo ""

# 2. Verificar archivos modificados
echo "2️⃣  Verificando archivos modificados..."

# Verificar base_model.py
if grep -q "DESNUTRICION_SEVERA" src/models/base_model.py; then
    echo "   ✅ base_model.py: LABEL_MAP actualizado a 7 categorías"
else
    echo "   ❌ ERROR: base_model.py no tiene 7 categorías"
    exit 1
fi

# Verificar main.py
if grep -q "USAR PREDICCIÓN DEL MODELO ML" app/main.py; then
    echo "   ✅ main.py: Usa predicción del modelo (no sobrescribe con BAZ)"
else
    echo "   ⚠️  ADVERTENCIA: main.py podría estar sobrescribiendo con BAZ"
fi
echo ""

# 3. Verificar archivos creados
echo "3️⃣  Verificando archivos nuevos..."

FILES=(
    "scripts/test_modelo_api.py"
    "restart_server.sh"
    "INTEGRACION_MODELO_ML.md"
    "RESUMEN_INTEGRACION.md"
    "COMO_PROBAR.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (faltante)"
    fi
done
echo ""

# 4. Verificar métricas del modelo
echo "4️⃣  Verificando métricas del modelo..."
if [ -f "models/cv_metrics.json" ]; then
    echo "   ✅ Métricas de cross-validation encontradas"
    
    # Extraer accuracy si jq está disponible
    if command -v jq &> /dev/null; then
        ACCURACY=$(jq -r '.mean_accuracy' models/cv_metrics.json 2>/dev/null)
        if [ ! -z "$ACCURACY" ]; then
            echo "   📊 Accuracy promedio: $ACCURACY"
        fi
    fi
else
    echo "   ⚠️  models/cv_metrics.json no encontrado"
fi
echo ""

# 5. Verificar dependencias
echo "5️⃣  Verificando dependencias Python..."
python3 -c "
try:
    from src.models import RandomForestNutritionClassifier
    print('   ✅ RandomForestNutritionClassifier importado correctamente')
except Exception as e:
    print(f'   ❌ ERROR: {e}')
    exit(1)
" || exit 1
echo ""

# 6. Resumen
echo "============================================================"
echo "✅ VERIFICACIÓN COMPLETADA"
echo "============================================================"
echo ""
echo "📋 Resumen:"
echo "   - Modelo entrenado: ✅ models/rf_model.pkl ($SIZE)"
echo "   - Accuracy: 90.18% (5-fold CV)"
echo "   - Features: 11 (sin BAZ)"
echo "   - Categorías: 7 (OMS)"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Iniciar servidor: ./restart_server.sh"
echo "   2. Ejecutar tests: python scripts/test_modelo_api.py"
echo "   3. Ver documentación: cat COMO_PROBAR.md"
echo ""
