# 🐳 Docker - Resumen Ejecutivo

## ✅ Lo que se Dockerizó

- ✅ **Frontend** (React + Vite) → Puerto 3000
- ✅ **Backend** (FastAPI) → Puerto 8000
- ✅ **Modelo ML** (FastAPI) → Puerto 8001
- ✅ **Hot-reload** activado en todos
- ✅ **MySQL** se conecta desde el host

---

## 🚀 Comandos Esenciales

### Iniciar todo
```bash
./docker-start.sh
```

### Ver logs
```bash
./docker-logs.sh
```

### Detener todo
```bash
./docker-stop.sh
```

---

## 🌐 URLs de Acceso

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000/docs
- **Modelo ML**: http://localhost:8001/docs

---

## 📁 Archivos Creados

```
proyecto/
├── docker-compose.yml              ⭐ Configuración principal
├── .env.example                    Variables de entorno
├── docker-start.sh                 ⭐ Script de inicio
├── docker-stop.sh                  Script de detención
├── docker-logs.sh                  Script de logs
├── DOCKER_GUIA.md                  ⭐ Guía completa
├── README_DOCKER.md                README con Docker
│
├── control/Nutricion-api/
│   ├── Dockerfile                  ⭐ Imagen del backend
│   └── .dockerignore
│
├── vista/AppSaludable/
│   ├── Dockerfile                  ⭐ Imagen del frontend
│   └── .dockerignore
│
└── modelo/ml-recomendator/
    ├── Dockerfile                  ⭐ Imagen del modelo ML
    └── .dockerignore
```

---

## 🔄 Hot-Reload Activado

**Todos los servicios tienen hot-reload:**

- Editas código → Se refleja automáticamente
- No necesitas reiniciar contenedores
- Desarrollo fluido como en local

---

## 🔧 Configuración de MySQL

**MySQL NO está en Docker**, está en tu host:

- Los contenedores se conectan vía `host.docker.internal:3306`
- Configuración en `docker-compose.yml`
- Si cambias la BD, edita las variables de entorno

---

## 📊 Arquitectura

```
Frontend (3000) ──┐
                  │
Backend (8000) ───┼──> MySQL (host:3306)
                  │
Modelo ML (8001) ─┘
```

Todos en la red `app-network` de Docker.

---

## 💡 Ventajas

1. ✅ **Un solo comando** para iniciar todo
2. ✅ **Hot-reload** en desarrollo
3. ✅ **Aislamiento** de dependencias
4. ✅ **Portabilidad** entre máquinas
5. ✅ **Fácil de escalar** en producción

---

## 🎯 Flujo de Trabajo

```bash
# 1. Iniciar
./docker-start.sh

# 2. Desarrollar (edita archivos)
# Los cambios se reflejan automáticamente

# 3. Ver logs si hay errores
./docker-logs.sh

# 4. Detener
./docker-stop.sh
```

---

## 🐛 Problemas Comunes

### "Cannot connect to MySQL"
```bash
# Verifica que MySQL esté corriendo
docker ps | grep mysql
```

### "Port already in use"
```bash
# Ver qué usa el puerto
lsof -i :3000
```

### "Changes not reflecting"
```bash
# Reiniciar el servicio
docker-compose restart frontend
```

---

## 📚 Documentación

- **DOCKER_GUIA.md** - Guía completa y detallada
- **README_DOCKER.md** - README con instrucciones Docker
- **.env.example** - Ejemplo de variables de entorno

---

## 🎓 TL;DR

### Para iniciar:
```bash
./docker-start.sh
```

### Para ver logs:
```bash
./docker-logs.sh
```

### Para detener:
```bash
./docker-stop.sh
```

### URLs:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- ML: http://localhost:8001/docs

---

**Eso es todo!** 🎉

Ahora puedes desarrollar sin preocuparte por dependencias, versiones de Python/Node, o configuraciones complicadas.

Todo funciona en contenedores Docker con hot-reload activado.

**¿Dudas?** Lee [DOCKER_GUIA.md](DOCKER_GUIA.md) 📖
