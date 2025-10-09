#!/bin/bash

# Script para generar todas las gráficas del modelo ML
# Uso: ./generar_graficas.sh

echo "🎨 Generando gráficas del modelo ML..."
echo ""

cd "$(dirname "$0")"

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Ejecutar script de generación de gráficas
python scripts/generar_graficas.py

echo ""
echo "✅ Proceso completado!"
echo "📁 Las gráficas están en: reports/figures/"
