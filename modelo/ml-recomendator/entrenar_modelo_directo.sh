#!/bin/bash

# Script para entrenar el modelo DIRECTO
# Aprende de edad, peso, talla sin calcular BAZ

echo "=================================="
echo "🎯 ENTRENANDO MODELO DIRECTO"
echo "=================================="
echo ""
echo "Este modelo aprende DIRECTAMENTE de:"
echo "  • Edad (meses)"
echo "  • Sexo (M/F)"
echo "  • Peso (kg)"
echo "  • Talla (cm)"
echo ""
echo "NO necesita calcular BAZ previamente"
echo ""

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "📦 Activando entorno virtual..."
    source venv/bin/activate
fi

# Verificar que existan datos en la BD
echo "🔍 Verificando datos en la base de datos..."
python -c "
from src.utils.db_connector import DatabaseConnector
db = DatabaseConnector.from_env()
db.connect()
result = db.execute_query('SELECT COUNT(*) as total FROM antropometrias WHERE ant_peso_kg IS NOT NULL AND ant_talla_cm IS NOT NULL AND ant_z_imc IS NOT NULL')
total = result['total'].iloc[0]
print(f'   ✅ Encontradas {total} antropometrías con datos completos')
if total < 100:
    print('   ⚠️  Advertencia: Pocos datos para entrenar (mínimo recomendado: 500)')
db.disconnect()
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error al verificar datos"
    echo "   Asegúrate de que:"
    echo "   1. MySQL esté corriendo"
    echo "   2. La BD 'nutricion' exista"
    echo "   3. Haya datos en 'antropometrias'"
    exit 1
fi

echo ""
echo "🚀 Iniciando entrenamiento..."
echo ""

# Entrenar modelo
python src/pipeline/train_model_directo.py \
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
    echo "   • models/directo/feature_importance_directo.csv"
    echo ""
    echo "🧪 Probar el modelo:"
    echo "   python scripts/test_modelo_directo.py"
    echo ""
    echo "📖 Ver documentación:"
    echo "   cat MODELO_DIRECTO.md"
else
    echo ""
    echo "❌ Error en el entrenamiento"
    echo ""
    echo "💡 Posibles soluciones:"
    echo "   1. Verificar que haya suficientes datos"
    echo "   2. Revisar que las clasificaciones estén correctas"
    echo "   3. Verificar conexión a MySQL"
    exit 1
fi
