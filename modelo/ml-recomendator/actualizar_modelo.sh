#!/bin/bash

# Script para actualizar el modelo ML cuando hay nuevos datos en la BD
# Uso:
#   ./actualizar_modelo.sh              # Usa solo datos reales
#   ./actualizar_modelo.sh --sinteticos # Incluye datos sintéticos

echo "🔄 ACTUALIZANDO MODELO ML CON NUEVOS DATOS"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Verificar si se quiere incluir sintéticos
USAR_SINTETICOS=false
if [ "$1" == "--sinteticos" ] || [ "$1" == "-s" ]; then
    USAR_SINTETICOS=true
fi

# Paso 1: Hacer backup del modelo actual
echo "💾 Paso 1/6: Haciendo backup del modelo actual..."
if [ -f "models/rf_model.pkl" ]; then
    FECHA=$(date +%Y%m%d_%H%M%S)
    mkdir -p models/backups
    cp models/rf_model.pkl models/backups/rf_model_$FECHA.pkl
    cp models/rf_metrics.json models/backups/rf_metrics_$FECHA.json 2>/dev/null
    echo "✅ Backup guardado: models/backups/rf_model_$FECHA.pkl"
else
    echo "ℹ️  No hay modelo previo para hacer backup"
fi
echo ""

# Paso 2: Exportar datos desde la BD
echo "📊 Paso 2/6: Exportando datos desde la base de datos MySQL..."
if [ "$USAR_SINTETICOS" = true ]; then
    echo "   Modo: Datos reales + sintéticos"
    python scripts/generar_datos_desde_oms.py --samples 1000
else
    echo "   Modo: Solo datos reales"
    python scripts/generar_solo_datos_reales.py
fi

if [ $? -ne 0 ]; then
    echo "❌ Error exportando datos"
    echo ""
    echo "Verifica:"
    echo "  - La BD MySQL está corriendo"
    echo "  - Las credenciales en .env son correctas"
    echo "  - Las tablas existen (ninos, antropometrias, oms_bmi_lms)"
    exit 1
fi
echo "✅ Datos exportados"
echo ""

# Paso 3: Verificar cantidad de datos
echo "📈 Paso 3/6: Verificando cantidad de registros..."
if [ -f "data/raw/surveys/datos_completos_oms_reales.csv" ]; then
    TOTAL_REGISTROS=$(tail -n +2 data/raw/surveys/datos_completos_oms_reales.csv | wc -l)
    echo "   Total de registros: $TOTAL_REGISTROS"

    if [ $TOTAL_REGISTROS -lt 100 ]; then
        echo "   ⚠️  ADVERTENCIA: Menos de 100 registros"
        echo "   El modelo puede no funcionar bien con tan pocos datos"
        echo ""
        read -p "   ¿Continuar de todos modos? (s/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            echo "❌ Proceso cancelado"
            exit 1
        fi
    fi
else
    echo "❌ No se encontró el archivo de datos"
    exit 1
fi
echo ""

# Paso 4: Reentrenar el modelo
echo "🤖 Paso 4/6: Reentrenando modelo con nuevos datos..."
python src/pipeline/train_model.py --data data/raw/surveys/datos_completos_oms_reales.csv --model rf --use-cv --cv-folds 5
if [ $? -ne 0 ]; then
    echo "❌ Error entrenando modelo"
    echo ""
    echo "Restaurando backup..."
    if [ -f "models/backups/rf_model_$FECHA.pkl" ]; then
        cp models/backups/rf_model_$FECHA.pkl models/rf_model.pkl
        cp models/backups/rf_metrics_$FECHA.json models/rf_metrics.json 2>/dev/null
        echo "✅ Modelo anterior restaurado"
    fi
    exit 1
fi
echo "✅ Modelo reentrenado"
echo ""

# Paso 5: Verificar clasificación
echo "🔍 Paso 5/6: Verificando clasificaciones..."
python scripts/test_clasificacion.py
if [ $? -ne 0 ]; then
    echo "⚠️  Advertencia: Error en verificación (continuando...)"
fi
echo ""

# Paso 6: Generar gráficas actualizadas
echo "📊 Paso 6/6: Generando gráficas actualizadas..."
python scripts/generar_graficas.py
if [ $? -ne 0 ]; then
    echo "⚠️  Advertencia: Error generando gráficas (continuando...)"
else
    echo "✅ Gráficas generadas en: reports/figures/"
fi
echo ""

# Mostrar métricas del nuevo modelo
echo "=========================================="
echo "📈 MÉTRICAS DEL MODELO ACTUALIZADO"
echo "=========================================="
if [ -f "models/rf_metrics.json" ]; then
    python -c "
import json
with open('models/rf_metrics.json', 'r') as f:
    metrics = json.load(f)
    print(f\"Accuracy: {metrics.get('accuracy', 'N/A'):.4f}\")
    print(f\"Precision: {metrics.get('precision_macro', 'N/A'):.4f}\")
    print(f\"Recall: {metrics.get('recall_macro', 'N/A'):.4f}\")
    print(f\"F1-Score: {metrics.get('f1_macro', 'N/A'):.4f}\")
" 2>/dev/null || cat models/rf_metrics.json
fi
echo ""

echo "=========================================="
echo "✅ MODELO ACTUALIZADO EXITOSAMENTE"
echo "=========================================="
echo ""
echo "📋 Próximos pasos:"
echo "   1. Revisar métricas: cat models/rf_metrics.json"
echo "   2. Revisar gráficas: open reports/figures/"
echo "   3. Reiniciar API del modelo:"
echo "      cd modelo/ml-recomendator"
echo "      docker-compose down && docker-compose up -d"
echo ""
echo "💡 Tips:"
echo "   - Compara métricas con el backup anterior"
echo "   - Si el accuracy bajó, considera restaurar el backup"
echo "   - Backup guardado en: models/backups/rf_model_$FECHA.pkl"
echo ""
