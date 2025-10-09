#!/bin/bash

# Script completo para rebalancear datos y reentrenar modelo
# Uso: ./scripts/rebalancear_y_reentrenar.sh

echo "🔄 PROCESO COMPLETO: REBALANCEAR Y REENTRENAR"
echo "=============================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "scripts/balancear_datos.sql" ]; then
    echo "❌ Error: Ejecuta este script desde modelo/ml-recomendator/"
    exit 1
fi

# Pedir confirmación
echo "⚠️  ADVERTENCIA: Este script va a:"
echo "   1. Modificar las antropometrías en la BD"
echo "   2. Crear un backup en antropometrias_backup_original"
echo "   3. Limpiar features_ml"
echo "   4. Recalcular todos los features"
echo "   5. Reentrenar el modelo"
echo ""
read -p "¿Continuar? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Cancelado"
    exit 1
fi

# Cargar variables de entorno
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-root123456}"
DB_NAME="${DB_NAME:-nutricion}"
DB_HOST="${DB_HOST:-localhost}"

echo ""
echo "📊 PASO 1: Balancear datos antropométricos"
echo "=============================================="
python3 scripts/balancear_datos.py

if [ $? -ne 0 ]; then
    echo "❌ Error al balancear datos"
    exit 1
fi

echo ""
echo "✅ Datos balanceados correctamente"
echo ""

echo "🧹 PASO 2: Limpiar features_ml"
echo "=============================================="
python3 scripts/limpiar_features.py

if [ $? -ne 0 ]; then
    echo "❌ Error al limpiar features_ml"
    exit 1
fi

echo "✅ features_ml limpiado"
echo ""

echo "🔧 PASO 3: Recalcular features ML"
echo "=============================================="
python3 scripts/calcular_features_todos.py

if [ $? -ne 0 ]; then
    echo "❌ Error al calcular features"
    exit 1
fi

echo ""
echo "✅ Features calculados"
echo ""

echo "📥 PASO 4: Extraer y verificar datos para entrenamiento"
echo "=============================================="
python3 scripts/verificar_clasificacion.py

if [ $? -ne 0 ]; then
    echo "❌ Error al extraer datos"
    exit 1
fi

echo ""
echo "✅ Datos extraídos y verificados"
echo ""

echo "🎯 PASO 5: Entrenar modelo con cross-validation"
echo "=============================================="
python3 src/pipeline/train_model.py \
    --data data/raw/surveys/datos_historicos.csv \
    --model rf \
    --output models/ \
    --use-cv \
    --cv-folds 5

if [ $? -ne 0 ]; then
    echo "❌ Error al entrenar modelo"
    exit 1
fi

echo ""
echo "✅ Modelo entrenado"
echo ""

echo "📊 PASO 6: Generar gráficas"
echo "=============================================="
python3 scripts/generar_graficas.py

if [ $? -ne 0 ]; then
    echo "⚠️  Error al generar gráficas (no crítico)"
fi

echo ""
echo "=============================================="
echo "✅ PROCESO COMPLETADO"
echo "=============================================="
echo ""
echo "📊 Resultados:"
echo "   - Modelo: models/rf_model.pkl"
echo "   - Métricas CV: models/cv_metrics.json"
echo "   - Gráficas: reports/figures/"
echo "   - Backup datos originales: antropometrias_backup_original (en MySQL)"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Revisar gráficas en reports/figures/"
echo "   2. Verificar accuracy en models/cv_metrics.json"
echo "   3. Reiniciar API ML: ./run_api.sh"
echo ""
echo "💡 Para restaurar datos originales:"
echo "   mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME -e \"INSERT INTO antropometrias SELECT * FROM antropometrias_backup_original;\""
echo ""
