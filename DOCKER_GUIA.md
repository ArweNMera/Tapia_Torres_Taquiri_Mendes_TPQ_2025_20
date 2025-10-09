# 🐳 Guía de Docker - Proyecto Nutrición

## 🚀 Inicio Rápido

### 1. Iniciar todos los servicios
```bash
./docker-start.sh
```

### 2. Acceder a las aplicaciones
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Modelo ML**: http://localhost:8001
- **Docs Backend**: http://localhost:8000/docs
- **Docs ML**: http://localhost:8001/docs

### 3. Detener servicios
```bash
./docker-stop.sh
```

---

## 📋 Servicios Dockerizados

| Servicio | Puerto | Descripción | Hot-Reload |
|----------|--------|-------------|------------|
| **Frontend** | 3000 | React + Vite | ✅ Sí |
| **Backend** | 8000 | FastAPI (Nutrición) | ✅ Sí |
| **Modelo ML** | 8001 | FastAPI (ML) | ✅ Sí |
| **MySQL** | 3306 | Base de Datos | ❌ (Ya existe) |

---

## 🔧 Configuración

### Requisitos Previos
1. ✅ Docker instalado
2. ✅ Docker Compose instalado
3. ✅ MySQL corriendo en el host (puerto 3306)

### Variables de Entorno

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

Edita `.env` con tus valores:
```env
GOOGLE_CLIENT_ID=tu_google_client_id
GOOGLE_CLIENT_SECRET=tu_google_client_secret
DB_PASSWORD=tu_password_mysql
```

---

## 📦 Estructura de Contenedores

```
┌─────────────────────────────────────────────┐
│           Docker Network (app-network)       │
│                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Frontend │  │ Backend  │  │ Modelo ML│  │
│  │  :3000   │  │  :8000   │  │  :8001   │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │              │         │
│       └─────────────┴──────────────┘         │
│                     │                        │
└─────────────────────┼────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │    MySQL     │
              │ (Host:3306)  │
              └──────────────┘
```

---

## 🔄 Hot-Reload (Desarrollo)

Todos los servicios tienen **hot-reload activado**:

### Frontend
- Edita archivos en `vista/AppSaludable/src/`
- Los cambios se reflejan automáticamente
- No necesitas reiniciar el contenedor

### Backend
- Edita archivos en `control/Nutricion-api/nutricion-api/app/`
- Uvicorn detecta cambios y recarga automáticamente
- No necesitas reiniciar el contenedor

### Modelo ML
- Edita archivos en `modelo/ml-recomendator/`
- Uvicorn detecta cambios y recarga automáticamente
- Si cambias el modelo (`.pkl`), reinicia: `docker-compose restart modelo-ml`

---

## 📝 Comandos Útiles

### Ver logs de todos los servicios
```bash
./docker-logs.sh
```

### Ver logs de un servicio específico
```bash
./docker-logs.sh backend
./docker-logs.sh frontend
./docker-logs.sh modelo-ml
```

### Ver estado de los contenedores
```bash
docker-compose ps
```

### Reiniciar un servicio específico
```bash
docker-compose restart backend
docker-compose restart frontend
docker-compose restart modelo-ml
```

### Reconstruir un servicio (después de cambiar Dockerfile)
```bash
docker-compose build backend
docker-compose up -d backend
```

### Entrar a un contenedor
```bash
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec modelo-ml bash
```

### Ver uso de recursos
```bash
docker stats
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to MySQL"

**Problema:** Los contenedores no pueden conectar a MySQL

**Solución:**
```bash
# Verifica que MySQL esté corriendo
docker ps | grep mysql

# Verifica que esté en el puerto 3306
netstat -an | grep 3306

# Si MySQL está en Docker, usa:
# host.docker.internal:3306 (ya configurado)
```

---

### Error: "Port already in use"

**Problema:** El puerto ya está siendo usado

**Solución:**
```bash
# Ver qué está usando el puerto
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :8001  # Modelo ML

# Detener el proceso o cambiar el puerto en docker-compose.yml
```

---

### Error: "Module not found" en Frontend

**Problema:** node_modules no está instalado

**Solución:**
```bash
# Reconstruir el contenedor
docker-compose build frontend
docker-compose up -d frontend
```

---

### Error: "No module named 'app'" en Backend

**Problema:** El código no se montó correctamente

**Solución:**
```bash
# Verificar volúmenes
docker-compose down
docker-compose up -d

# Si persiste, reconstruir
docker-compose build backend
docker-compose up -d backend
```

---

### Los cambios no se reflejan (Hot-reload no funciona)

**Problema:** El hot-reload no está detectando cambios

**Solución:**

**Frontend:**
```bash
# Reiniciar el contenedor
docker-compose restart frontend
```

**Backend/ML:**
```bash
# Verificar logs
docker-compose logs -f backend

# Reiniciar si es necesario
docker-compose restart backend
```

---

### Error: "Permission denied" en volúmenes

**Problema:** Permisos de archivos

**Solución:**
```bash
# En Linux, ajustar permisos
sudo chown -R $USER:$USER .

# O ejecutar Docker con tu usuario
docker-compose up -d --user $(id -u):$(id -g)
```

---

## 🔒 Producción

Para producción, necesitas:

### 1. Cambiar a modo producción

**Frontend:**
```dockerfile
# En vista/AppSaludable/Dockerfile
# Cambiar CMD a:
CMD ["npm", "run", "build"] && ["npm", "run", "preview"]
```

**Backend/ML:**
```dockerfile
# Cambiar CMD a (sin --reload):
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Usar variables de entorno seguras
```bash
# No uses .env en producción
# Usa secrets de Docker o variables del sistema
```

### 3. Agregar health checks
```yaml
# En docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 4. Limitar recursos
```yaml
# En docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 1G
```

---

## 📊 Monitoreo

### Ver logs en tiempo real
```bash
# Todos los servicios
docker-compose logs -f

# Solo errores
docker-compose logs -f | grep ERROR

# Últimas 100 líneas
docker-compose logs --tail=100
```

### Ver uso de recursos
```bash
docker stats
```

### Ver redes
```bash
docker network ls
docker network inspect app-network
```

---

## 🧹 Limpieza

### Detener y eliminar contenedores
```bash
docker-compose down
```

### Eliminar también volúmenes
```bash
docker-compose down -v
```

### Limpiar imágenes no usadas
```bash
docker image prune -a
```

### Limpiar todo (cuidado!)
```bash
docker system prune -a --volumes
```

---

## 🎯 Flujos Comunes

### Desarrollo Normal
```bash
# 1. Iniciar servicios
./docker-start.sh

# 2. Desarrollar (los cambios se reflejan automáticamente)
# Edita archivos en tu IDE

# 3. Ver logs si hay errores
./docker-logs.sh

# 4. Al terminar
./docker-stop.sh
```

---

### Actualizar Dependencias

**Frontend:**
```bash
# Agregar dependencia
docker-compose exec frontend npm install nueva-libreria

# Reconstruir
docker-compose build frontend
docker-compose up -d frontend
```

**Backend/ML:**
```bash
# Agregar a requirements.txt
echo "nueva-libreria==1.0.0" >> control/Nutricion-api/nutricion-api/requirements.txt

# Reconstruir
docker-compose build backend
docker-compose up -d backend
```

---

### Reentrenar Modelo ML

```bash
# Entrar al contenedor
docker-compose exec modelo-ml bash

# Ejecutar script de reentrenamiento
./actualizar_modelo.sh

# Salir
exit

# Reiniciar para cargar nuevo modelo
docker-compose restart modelo-ml
```

---

## 📚 Archivos Importantes

```
proyecto/
├── docker-compose.yml          # Configuración principal
├── .env                        # Variables de entorno
├── docker-start.sh             # Script para iniciar
├── docker-stop.sh              # Script para detener
├── docker-logs.sh              # Script para ver logs
│
├── control/Nutricion-api/
│   ├── Dockerfile              # Imagen del backend
│   └── .dockerignore           # Archivos a ignorar
│
├── vista/AppSaludable/
│   ├── Dockerfile              # Imagen del frontend
│   └── .dockerignore           # Archivos a ignorar
│
└── modelo/ml-recomendator/
    ├── Dockerfile              # Imagen del modelo ML
    └── .dockerignore           # Archivos a ignorar
```

---

## 🎓 Resumen Ejecutivo

### Para iniciar todo:
```bash
./docker-start.sh
```

### Para ver logs:
```bash
./docker-logs.sh
```

### Para detener todo:
```bash
./docker-stop.sh
```

### URLs:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- Modelo ML: http://localhost:8001/docs

---

## 💡 Tips

1. **Hot-reload está activado** - No necesitas reiniciar al editar código
2. **Los volúmenes persisten** - Los datos del modelo se guardan
3. **MySQL está en el host** - No en Docker (usa `host.docker.internal`)
4. **Logs en tiempo real** - Usa `./docker-logs.sh` para debugging
5. **Reconstruye si cambias Dockerfile** - `docker-compose build`

---

**¿Problemas?** Revisa la sección de Troubleshooting o los logs con `./docker-logs.sh` 🐛
