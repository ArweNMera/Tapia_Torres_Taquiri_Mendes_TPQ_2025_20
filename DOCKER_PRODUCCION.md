# 🚀 Guía de Producción con Docker

## 📋 Configuración para Producción

### 1. Variables de Entorno

Tu backend en producción usa estas credenciales (en `control/Nutricion-api/nutricion-api/.env`):

```env
DATABASE_URL=mysql+pymysql://root:tu_password@localhost/nutricion
SECRET_KEY=tu_secret_key_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=30

GOOGLE_CLIENT_ID=tu_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=tu_google_client_secret
GOOGLE_REDIRECT_URI=https://tu-dominio.com/api/v1/auth/google/callback
GOOGLE_POST_LOGIN_REDIRECT=https://tu-frontend.com
GOOGLE_ALLOWED_REDIRECTS=http://localhost:5173,https://tu-frontend.com

ML_API_URL=http://localhost:8003
```

> **NOTA:** Estos son valores de ejemplo. Usa tus credenciales reales en tu archivo `.env` local.

**IMPORTANTE:** No modifiques este archivo. Es para tu producción actual.

---

### 2. Desarrollo Local con Docker

Para desarrollo local, usa el archivo `.env` en la raíz:

```bash
# Copiar ejemplo
cp .env.example .env

# Editar con tus valores de desarrollo
nano .env
```

El `.env` de la raíz es SOLO para Docker en desarrollo local.

---

### 3. Separación de Ambientes

```
proyecto/
├── .env                                    # Docker desarrollo (localhost)
├── .env.production                         # Producción (areallc.tech)
├── control/Nutricion-api/nutricion-api/.env  # Backend producción (NO TOCAR)
```

---

## 🐳 Docker en Desarrollo

### Iniciar servicios
```bash
./docker-start.sh
```

Esto usa el `.env` de la raíz con:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- ML: http://localhost:8001
- Google redirect: http://localhost:8000/api/v1/auth/google/callback

---

## 🌐 Producción (Sin Docker)

Tu producción actual funciona SIN Docker:

### Backend
- URL: https://api.areallc.tech
- Usa: `control/Nutricion-api/nutricion-api/.env`
- Google redirect: https://api.areallc.tech/api/v1/auth/google/callback

### Frontend
- URL: https://appsaludable.netlify.app
- Desplegado en Netlify
- Apunta a: https://api.areallc.tech

---

## 🔄 Flujo de Trabajo

### Desarrollo Local (Docker)
```bash
# 1. Iniciar Docker
./docker-start.sh

# 2. Desarrollar (cambios se reflejan automáticamente)
# Edita archivos en tu IDE

# 3. Probar en:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000/docs

# 4. Detener
./docker-stop.sh
```

### Deploy a Producción
```bash
# 1. Hacer cambios en desarrollo (Docker)

# 2. Probar que funciona

# 3. Hacer commit
git add .
git commit -m "Nuevas funcionalidades"
git push

# 4. Deploy backend (tu proceso actual)
# - SSH a tu servidor
# - Pull cambios
# - Reiniciar servicio

# 5. Deploy frontend (Netlify)
# - Netlify detecta cambios automáticamente
# - O hacer deploy manual
```

---

## ⚠️ Importante

### NO modifiques estos archivos para producción:
- ❌ `control/Nutricion-api/nutricion-api/.env` (Backend producción)
- ❌ Variables de entorno en Netlify (Frontend producción)

### SÍ modifica para desarrollo:
- ✅ `.env` (raíz del proyecto - Docker desarrollo)
- ✅ `docker-compose.yml` (configuración Docker)

---

## 🔧 Configuración de Google OAuth

### Desarrollo (Docker)
```
Redirect URI: http://localhost:8000/api/v1/auth/google/callback
Post-login: http://localhost:3000
```

### Producción
```
Redirect URI: https://api.areallc.tech/api/v1/auth/google/callback
Post-login: https://appsaludable.netlify.app
```

Ambos están configurados en tu Google Cloud Console.

---

## 📊 Puertos

### Desarrollo (Docker)
- Frontend: 3000
- Backend: 8000
- ML: 8001
- MySQL: 3306 (host)

### Producción
- Frontend: 443 (HTTPS)
- Backend: 443 (HTTPS)
- ML: 8003 (interno)
- MySQL: 3306 (interno)

---

## 🎯 Resumen

### Para desarrollo local:
```bash
./docker-start.sh
# Accede a http://localhost:3000
```

### Para producción:
- Backend: Ya está en https://api.areallc.tech
- Frontend: Ya está en https://appsaludable.netlify.app
- **No uses Docker en producción** (por ahora)

---

## 💡 Tips

1. **Desarrollo:** Usa Docker (localhost)
2. **Producción:** Usa tu setup actual (areallc.tech + Netlify)
3. **No mezcles:** Los `.env` son diferentes para cada ambiente
4. **Backup:** Siempre haz backup del `.env` de producción

---

## 🐛 Troubleshooting

### Error: "Google credentials not configured"
- **En Docker:** Verifica `.env` en la raíz
- **En Producción:** Verifica `control/Nutricion-api/nutricion-api/.env`

### Error: "Cannot connect to MySQL"
- **En Docker:** Usa `host.docker.internal`
- **En Producción:** Usa `localhost` o IP del servidor

### Frontend no conecta al backend
- **En Docker:** Backend debe estar en `http://localhost:8000`
- **En Producción:** Backend debe estar en `https://api.areallc.tech`

---

**¿Dudas?** Lee [DOCKER_GUIA.md](DOCKER_GUIA.md) para más detalles sobre Docker.
