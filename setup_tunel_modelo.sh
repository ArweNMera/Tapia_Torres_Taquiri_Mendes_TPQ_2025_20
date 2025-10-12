#!/bin/bash

echo "🚀 CONFIGURANDO TÚNEL CLOUDFLARE PARA MODELO ML"
echo "================================================"
echo ""

# Verificar que cloudflared esté instalado
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared no está instalado"
    echo ""
    echo "Instálalo con:"
    echo "  brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

echo "✅ cloudflared está instalado"
echo ""

# Paso 1: Crear el túnel
echo "📝 Paso 1: Creando túnel 'modelo'..."
echo ""
echo "Ejecuta este comando:"
echo "  cloudflared tunnel create modelo"
echo ""
read -p "¿Ya creaste el túnel? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Crea el túnel primero y vuelve a ejecutar este script"
    exit 1
fi

# Obtener el UUID del túnel
echo ""
echo "📋 Paso 2: Obtener UUID del túnel..."
TUNNEL_UUID=$(cloudflared tunnel list | grep "modelo" | awk '{print $1}')

if [ -z "$TUNNEL_UUID" ]; then
    echo "❌ No se encontró el túnel 'modelo'"
    echo "   Verifica con: cloudflared tunnel list"
    exit 1
fi

echo "✅ Túnel encontrado: $TUNNEL_UUID"
echo ""

# Paso 3: Crear configuración
echo "📝 Paso 3: Creando configuración..."
CONFIG_FILE="$HOME/.cloudflared/config.yml"

# Backup si existe
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✅ Backup creado: $CONFIG_FILE.backup.*"
fi

# Crear nueva configuración
cat > "$CONFIG_FILE" << EOF
tunnel: $TUNNEL_UUID
credentials-file: $HOME/.cloudflared/${TUNNEL_UUID}.json

ingress:
  # Modelo ML
  - hostname: modelo.areallc.tech
    service: http://localhost:8001

  # Backend API
  - hostname: api.areallc.tech
    service: http://localhost:8000

  # Catch-all rule
  - service: http_status:404
EOF

echo "✅ Configuración creada en: $CONFIG_FILE"
echo ""

# Paso 4: Configurar DNS
echo "📝 Paso 4: Configurando DNS..."
echo ""
echo "Ejecuta este comando:"
echo "  cloudflared tunnel route dns modelo modelo.areallc.tech"
echo ""
read -p "¿Ya configuraste el DNS? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Configura el DNS y continúa"
    exit 1
fi

echo "✅ DNS configurado"
echo ""

# Paso 5: Instalar como servicio
echo "📝 Paso 5: Instalando como servicio..."
echo ""
echo "Esto requiere permisos de administrador"
echo ""
read -p "¿Instalar como servicio? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    sudo cloudflared service install

    if [ $? -eq 0 ]; then
        echo "✅ Servicio instalado"
        echo ""
        echo "Iniciando servicio..."
        sudo launchctl start com.cloudflare.cloudflared
        echo "✅ Servicio iniciado"
    else
        echo "❌ Error instalando servicio"
        exit 1
    fi
fi

echo ""
echo "================================================"
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "================================================"
echo ""
echo "🌐 URLs disponibles:"
echo "   • Modelo ML: https://modelo.areallc.tech"
echo "   • Health: https://modelo.areallc.tech/health"
echo "   • Docs: https://modelo.areallc.tech/docs"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver túneles: cloudflared tunnel list"
echo "   • Ver info: cloudflared tunnel info modelo"
echo "   • Ver logs: sudo launchctl list | grep cloudflared"
echo "   • Detener: sudo launchctl stop com.cloudflare.cloudflared"
echo "   • Iniciar: sudo launchctl start com.cloudflare.cloudflared"
echo ""
echo "🚀 Asegúrate de que el modelo esté corriendo:"
echo "   cd modelo/ml-recomendator"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --host 0.0.0.0 --port 8001"
echo ""
