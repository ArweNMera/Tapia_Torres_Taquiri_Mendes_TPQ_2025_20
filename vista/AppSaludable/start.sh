#!/bin/bash

# Script para ejecutar App Saludable Frontend
# Asegúrate de que el backend esté ejecutándose en localhost:8000

echo "🚀 Iniciando App Saludable Frontend..."
echo ""

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instala Node.js 18+ antes de continuar."
    exit 1
fi

# Verificar si npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ npm no está instalado. Por favor instala npm antes de continuar."
    exit 1
fi

# Verificar si el backend está ejecutándose
echo "🔍 Verificando conexión con el backend..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Backend detectado en http://localhost:8000"
else
    echo "⚠️  No se puede conectar al backend en http://localhost:8000"
    echo "   Asegúrate de que el backend FastAPI esté ejecutándose antes de continuar."
    echo ""
    echo "   Para ejecutar el backend:"
    echo "   cd /path/to/backend"
    echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    echo ""
    read -p "¿Deseas continuar de todas formas? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar si node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error al instalar dependencias"
        exit 1
    fi
    echo "✅ Dependencias instaladas correctamente"
fi

# Verificar si el archivo .env existe
if [ ! -f ".env" ]; then
    echo "❌ Archivo .env no encontrado. Creando archivo .env por defecto..."
    cat > .env << EOL
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1

# JWT Configuration
VITE_TOKEN_KEY=auth_token

# App Configuration
VITE_APP_NAME=App Saludable
VITE_APP_VERSION=1.0.0
EOL
    echo "✅ Archivo .env creado"
fi

echo ""
echo "🌐 Iniciando servidor de desarrollo..."
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo ""
echo "📱 Funcionalidades disponibles:"
echo "   ✅ Registro de usuarios"
echo "   ✅ Inicio de sesión"
echo "   ✅ Navegación entre pantallas"
echo "   ✅ Logout desde configuración"
echo ""
echo "👤 Para probar, puedes registrar un nuevo usuario o usar credenciales existentes"
echo ""

# Ejecutar el servidor de desarrollo
npm run dev
