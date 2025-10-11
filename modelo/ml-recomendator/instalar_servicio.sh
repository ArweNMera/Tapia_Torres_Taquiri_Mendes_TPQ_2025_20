#!/bin/bash

echo "📦 INSTALANDO MODELO ML COMO SERVICIO"
echo "======================================"
echo ""

# Crear directorio de logs
mkdir -p logs
echo "✅ Directorio de logs creado"

# Copiar plist a LaunchAgents
PLIST_FILE="com.areallc.modelo-ml.plist"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

mkdir -p "$LAUNCH_AGENTS"

cp "$PLIST_FILE" "$LAUNCH_AGENTS/"
echo "✅ Archivo plist copiado a $LAUNCH_AGENTS"

# Cargar el servicio
launchctl load "$LAUNCH_AGENTS/$PLIST_FILE"
echo "✅ Servicio cargado"

# Iniciar el servicio
launchctl start com.areallc.modelo-ml
echo "✅ Servicio iniciado"

echo ""
echo "======================================"
echo "✅ SERVICIO INSTALADO"
echo "======================================"
echo ""
echo "🔧 Comandos útiles:"
echo "   • Ver estado: launchctl list | grep modelo-ml"
echo "   • Ver logs: tail -f logs/modelo-ml.log"
echo "   • Ver errores: tail -f logs/modelo-ml-error.log"
echo "   • Detener: launchctl stop com.areallc.modelo-ml"
echo "   • Iniciar: launchctl start com.areallc.modelo-ml"
echo "   • Desinstalar: launchctl unload ~/Library/LaunchAgents/$PLIST_FILE"
echo ""
echo "🌐 El modelo estará disponible en:"
echo "   • Local: http://localhost:8001"
echo "   • Producción: https://modelo.areallc.tech (después de configurar túnel)"
echo ""
