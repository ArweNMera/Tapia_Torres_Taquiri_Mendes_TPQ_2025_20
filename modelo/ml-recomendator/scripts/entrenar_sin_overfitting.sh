#!/bin/bash

# Script completo para entrenar modelo sin overfitting
# Uso: ./scripts/entrenar_sin_overfitting.sh

echo "🚀 ENTRENAMIENTO SIN OVERFITTING"
echo "=============================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "scripts/agregar_variabilidad.py" ]; then
    echo "❌ Error: Ejecuta este script desde modelo/ml-recomendator/"
    exit 1
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "❌ Error: No se encontró el entorno virtual"
    echo "   Crea uno con: python3 -m venv venv"
    exit 1
fi

# Verificar que scikit-learn esté instalado
echo ""
echo "🔍 Verificando dependencias..."
python3 -c "import sklearn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  scikit-learn no está instalado"
    echo "   Instalando dependencias..."
    pip install scikit-learn matplotlib seaborn scipy
    if [ $? -ne 0 ]; then
        echo "❌ Error al instalar dependencias"
        exit 1
    fi
fi
echo "✅ Dependencias verificadas"

# Paso 1: Analizar overfitting actual
echo ""
echo "📊 PASO 1: Analizar overfitting"
echo "=============================================="
python3 scripts/analizar_overfitting.py

if [ $? -ne 0 ]; then
    echo "❌ Error en análisis"
    exit 1
fi

# Paso 2: Agregar variabilidad
echo ""
echo "🔧 PASO 2: Agregar variabilidad a los datos"
echo "=============================================="
python3 scripts/agregar_variabilidad.py

if [ $? -ne 0 ]; then
    echo "❌ Error al agregar variabilidad"
    exit 1
fi

# Paso 3: Limpiar features_ml (opcional, solo si existe)
echo ""
echo "🧹 PASO 3: Limpiar features_ml (opcional)"
echo "=============================================="
read -p "¿Limpiar tabla features_ml en la BD? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    python3 scripts/limpiar_features.py
    if [ $? -ne 0 ]; then
        echo "⚠️  Error al limpiar features_ml (continuando...)"
    fi
fi

# Paso 4: Entrenar modelo con cross-validation
echo ""
echo "🎯 PASO 4: Entrenar modelo (SIN BAZ, con CV)"
echo "=============================================="
echo "⚠️  IMPORTANTE: BAZ ha sido removido de los features"
echo "   Esto evitará el overfitting (100% accuracy)"
echo ""

python3 src/pipeline/train_model.py \
    --data data/raw/surveys/datos_historicos_variabilidad.csv \
    --model rf \
    --output models/ \
    --use-cv \
    --cv-folds 5

if [ $? -ne 0 ]; then
    echo "❌ Error al entrenar modelo"
    exit 1
fi

# Paso 5: Generar gráficas
echo ""
echo "📊 PASO 5: Generar gráficas"
echo "=============================================="
python3 scripts/generar_graficas_simple.py

if [ $? -ne 0 ]; then
    echo "⚠️  Error al generar gráficas (no crítico)"
fi

# Resumen final
echo ""
echo "=============================================="
echo "✅ ENTRENAMIENTO COMPLETADO"
echo "=============================================="
echo ""
echo "📊 Resultados:"
echo "   - Modelo: models/rf_model.pkl"
echo "   - Métricas: models/rf_metrics.json"
echo "   - CV Metrics: models/cv_metrics.json"
echo "   - Gráficas: reports/figures/"
echo ""
echo "🎯 Accuracy esperado: 85-95% (no 100%)"
echo ""
echo "💡 Próximos pasos:"
echo "   1. Revisar models/cv_metrics.json"
echo "   2. Ver gráficas en reports/figures/"
echo "   3. Si accuracy < 80%, ajustar hiperparámetros"
echo "   4. Si accuracy > 98%, revisar data leakage"
echo ""
echo "🔄 Para reiniciar API ML:"
echo "   ./run_api.sh"
echo ""
