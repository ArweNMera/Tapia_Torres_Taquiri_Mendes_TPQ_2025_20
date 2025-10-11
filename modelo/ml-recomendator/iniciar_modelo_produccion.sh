#!/bin/bash

echo "🚀 INICIANDO MODELO ML EN PRODUCCIÓN"
echo "====================================="
echo ""

# Ir al directorio del modelo
cd "$(dirname "$0")"

# Activar entorno virtual
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "❌ No se encontró el entorno virtual"
    echo "   Créalo con: python -m venv venv"
    exit 1
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

# Verificar MySQL
echo "🔍 Verificando MySQL..."
if ! pgrep -x "mysqld" > /dev/null; then
    echo "⚠️  MySQL no está corriendo"
    echo "   Iniciando MySQL..."
    brew services start mysql
    sleep 3
fi

if pgrep -x "mysqld" > /dev/null; then
    echo "✅ MySQL está corriendo"
else
    echo "❌ No se pudo iniciar MySQL"
    exit 1
fi

echo ""
echo "🌐 Iniciando servidor en puerto 8001..."
echo "   URL local: http://localhost:8001"
echo "   URL producción: https://modelo.areallc.tech"
echo ""
echo "📖 Documentación: http://localhost:8001/docs"
echo ""
echo "Presiona Ctrl+C para detener"
echo ""

# Iniciar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
