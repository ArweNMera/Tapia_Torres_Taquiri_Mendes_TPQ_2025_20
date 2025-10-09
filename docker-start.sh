#!/bin/bash

# Script para iniciar todos los contenedores
echo "🚀 Iniciando todos los servicios..."
echo ""

# Verificar que MySQL esté corriendo
echo "🔍 Verificando MySQL..."
if ! docker ps | grep -q mysql8; then
    echo "⚠️  MySQL no está corriendo"
    echo "   Inicia MySQL primero o verifica que esté en el puerto 3306"
    echo ""
    read -p "¿Continuar de todos modos? (s/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Construir e iniciar contenedores
echo ""
echo "🏗️  Construyendo contenedores..."
docker-compose build

echo ""
echo "🚀 Iniciando servicios..."
docker-compose up -d

echo ""
echo "⏳ Esperando que los servicios estén listos..."
sleep 5

echo ""
echo "=========================================="
echo "✅ SERVICIOS INICIADOS"
echo "=========================================="
echo ""
echo "📋 URLs de acceso:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   Modelo ML: http://localhost:8001"
echo ""
echo "📊 Ver logs:"
echo "   docker-compose logs -f"
echo ""
echo "🔍 Ver estado:"
echo "   docker-compose ps"
echo ""
echo "🛑 Detener servicios:"
echo "   docker-compose down"
echo ""
