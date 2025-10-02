# Script para probar la integración completa del sistema

## 1. Iniciar el backend
echo "🚀 Iniciando backend..."
cd control/Nutricion-api/nutricion-api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "⏳ Esperando que el backend esté listo..."
sleep 5

## 2. Iniciar el frontend
echo "🎨 Iniciando frontend..."
cd ../../../vista/AppSaludable
npm run dev &
FRONTEND_PID=$!

echo "✅ Sistema iniciado!"
echo "📍 Backend: http://localhost:8000"
echo "📍 Frontend: http://localhost:5173"
echo "📍 API Docs: http://localhost:8000/docs"

echo ""
echo "🧪 Para probar el sistema:"
echo "1. Abre http://localhost:5173"
echo "2. Registra un nuevo usuario"
echo "3. Crea el perfil de un niño"
echo "4. Agrega mediciones antropométricas"
echo "5. Ve la evaluación nutricional automática"

echo ""
echo "🛑 Para detener los servicios:"
echo "kill $BACKEND_PID $FRONTEND_PID"

# Mantener el script activo
wait
