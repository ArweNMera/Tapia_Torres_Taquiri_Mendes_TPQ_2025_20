# 🐳 Proyecto Nutrición - Dockerizado

Sistema completo de evaluación nutricional infantil con Machine Learning.

## 🚀 Inicio Rápido con Docker

### 1. Clonar el repositorio
```bash
git clone <tu-repo>
cd proyecto-nutricion
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Edita .env con tus credenciales
```

### 3. Iniciar todos los servicios
```bash
./docker-start.sh
```

### 4. Acceder a las aplicaciones
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Modelo ML API**: http://localhost:8001/docs

---

## 📦 Servicios

| Servicio | Puerto | Tecnología | Hot-Reload |
|----------|--------|------------|------------|
| Frontend | 3000 | React + Vite | ✅ |
| Backend | 8000 | FastAPI + Python | ✅ |
| Modelo ML | 8001 | FastAPI + Scikit-learn | ✅ |
| Base de Datos | 3306 | MySQL 8 | - |

---

## 🛠️ Comandos Principales

```bash
# Iniciar servicios
./docker-start.sh

# Ver logs
./docker-logs.sh

# Ver logs de un servicio específico
./docker-logs.sh backend

# Detener servicios
./docker-stop.sh

# Ver estado
docker-compose ps

# Reiniciar un servicio
docker-compose restart backend
```

---

## 🔄 Desarrollo con Hot-Reload

Todos los servicios tienen **hot-reload activado**:

- **Frontend**: Edita archivos en `vista/AppSaludable/src/` → Cambios automáticos
- **Backend**: Edita archivos en `control/Nutricion-api/nutricion-api/app/` → Recarga automática
- **Modelo ML**: Edita archivos en `modelo/ml-recomendator/` → Recarga automática

No necesitas reiniciar contenedores al editar código! 🎉

---

## 📚 Documentación

- **[DOCKER_GUIA.md](DOCKER_GUIA.md)** - Guía completa de Docker
- **[modelo/ml-recomendator/GUIA_RAPIDA.md](modelo/ml-recomendator/GUIA_RAPIDA.md)** - Guía del modelo ML
- **[control/Nutricion-api/README.md](control/Nutricion-api/README.md)** - Documentación del backend
- **[vista/AppSaludable/README.md](vista/AppSaludable/README.md)** - Documentación del frontend

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────┐
│           Docker Network (app-network)       │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Frontend │  │ Backend  │  │ Modelo ML│  │
│  │  React   │  │ FastAPI  │  │ FastAPI  │  │
│  │  :3000   │  │  :8000   │  │  :8001   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │              │         │
│       └─────────────┴──────────────┘         │
│                     │                        │
└─────────────────────┼────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │    MySQL 8   │
              │ (Host:3306)  │
              └──────────────┘
```

---

## 🔧 Configuración

### Variables de Entorno

Edita `.env` con tus valores:

```env
# Google OAuth (opcional)
GOOGLE_CLIENT_ID=tu_client_id
GOOGLE_CLIENT_SECRET=tu_client_secret

# Base de Datos
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=nutricion
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to MySQL"
```bash
# Verifica que MySQL esté corriendo
docker ps | grep mysql

# Verifica el puerto
netstat -an | grep 3306
```

### Error: "Port already in use"
```bash
# Ver qué está usando el puerto
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :8001  # Modelo ML
```

### Los cambios no se reflejan
```bash
# Reiniciar el servicio
docker-compose restart frontend
```

**Más soluciones:** Ver [DOCKER_GUIA.md](DOCKER_GUIA.md#troubleshooting)

---

## 📊 Características

### Frontend (React + Vite)
- ✅ Interfaz moderna con Tailwind CSS
- ✅ Gestión de niños y mediciones antropométricas
- ✅ Visualización de estado nutricional
- ✅ Autenticación con Google OAuth
- ✅ Hot-reload en desarrollo

### Backend (FastAPI)
- ✅ API RESTful con documentación automática
- ✅ Autenticación JWT
- ✅ Integración con modelo ML
- ✅ Procedimientos almacenados MySQL
- ✅ Hot-reload en desarrollo

### Modelo ML (Scikit-learn)
- ✅ Random Forest Classifier (90.18% accuracy)
- ✅ 7 categorías nutricionales OMS
- ✅ API FastAPI para predicciones
- ✅ Reentrenamiento automático
- ✅ Hot-reload en desarrollo

---

## 🎯 Flujo de Trabajo

### Desarrollo Normal
```bash
# 1. Iniciar servicios
./docker-start.sh

# 2. Desarrollar (edita archivos en tu IDE)
# Los cambios se reflejan automáticamente

# 3. Ver logs si hay errores
./docker-logs.sh

# 4. Al terminar
./docker-stop.sh
```

### Reentrenar Modelo ML
```bash
# Entrar al contenedor
docker-compose exec modelo-ml bash

# Reentrenar
./actualizar_modelo.sh

# Salir y reiniciar
exit
docker-compose restart modelo-ml
```

---

## 📁 Estructura del Proyecto

```
proyecto-nutricion/
├── docker-compose.yml          # Orquestación de servicios
├── .env                        # Variables de entorno
├── docker-start.sh             # Script de inicio
├── docker-stop.sh              # Script de detención
├── docker-logs.sh              # Script de logs
│
├── control/Nutricion-api/      # Backend FastAPI
│   ├── Dockerfile
│   └── nutricion-api/
│       └── app/
│
├── vista/AppSaludable/         # Frontend React
│   ├── Dockerfile
│   └── src/
│
└── modelo/ml-recomendator/     # Modelo ML
    ├── Dockerfile
    ├── models/                 # Modelos entrenados
    └── src/
```

---

## 🚀 Despliegue en Producción

Para producción, necesitas:

1. **Cambiar a modo producción** en los Dockerfiles
2. **Usar variables de entorno seguras** (no .env)
3. **Agregar health checks**
4. **Configurar reverse proxy** (nginx)
5. **Usar HTTPS**

Ver [DOCKER_GUIA.md](DOCKER_GUIA.md#producción) para más detalles.

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.

---

## 👥 Equipo

- **Backend**: FastAPI + MySQL
- **Frontend**: React + Vite + Tailwind
- **ML**: Scikit-learn + FastAPI

---

## 🎓 Resumen

### Para iniciar:
```bash
./docker-start.sh
```

### URLs:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- ML: http://localhost:8001/docs

### Para detener:
```bash
./docker-stop.sh
```

---

**¿Dudas?** Lee la [Guía Completa de Docker](DOCKER_GUIA.md) 📖
