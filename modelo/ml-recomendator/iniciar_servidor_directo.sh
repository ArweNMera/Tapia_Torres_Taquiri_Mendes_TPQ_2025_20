#!/bin/bash

echo "🚀 INICIANDO SERVIDOR CON MODELO DIRECTO"
echo "========================================="
echo ""

# Ir al directorio correcto
cd "$(dirname "$0")"

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
fi

# Verificar que el modelo existe
if [ ! -f "models/directo/modelo_directo.pkl" ]; then
    echo "❌ Modelo no encontrado"
    echo ""
    echo "Entrena el modelo primero:"
    echo "  ./ENTRENAR_AHORA.sh"
    exit 1
fi

echo "✅ Modelo encontrado"
echo ""
echo "Iniciando servidor en http://localhost:8001"
echo "Documentación: http://localhost:8001/docs"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

# Iniciar servidor
python -m uvicorn app.main_directo:app --host 0.0.0.0 --port 8001 --reload
