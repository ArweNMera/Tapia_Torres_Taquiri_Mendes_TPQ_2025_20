# Configuración del Backend para App Saludable

## 📋 Prerrequisitos del Backend

Antes de ejecutar el frontend, asegúrate de tener el backend FastAPI configurado y ejecutándose.

## 🗄️ Base de Datos

### 1. Crear la Base de Datos MySQL

```sql
CREATE DATABASE IF NOT EXISTS nutricion
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
```

### 2. Ejecutar el Script de Creación de Tablas

Ejecuta el script SQL completo que incluye:
- Tablas de usuarios y roles
- Tablas de nutricionistas y tutores
- Tablas de niños y antropometría
- Tablas de alimentos y recetas
- Procedimientos almacenados

### 3. Insertar Roles Básicos

Los roles se insertan automáticamente con los procedimientos almacenados:
- `ADMIN` - Administrador
- `NUTRI` - Nutricionista
- `TUTOR` - Tutor/Padre de familia
- `usr` - Usuario general

## 🚀 Backend FastAPI

### Estructura del Backend

El backend debe estar corriendo en `http://localhost:8000` con los siguientes endpoints:

#### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/logout` - Cerrar sesión (requiere token)
- `POST /api/v1/usuarios/register` - Registrar usuario

#### Usuarios
- `POST /api/v1/usuarios/roles` - Crear rol

### Configuración del Backend

Asegúrate de que el backend tenga:

1. **CORS configurado** para permitir solicitudes desde `http://localhost:5173`
2. **Variables de entorno** para la base de datos
3. **JWT configurado** con las mismas claves

### Ejemplo de configuración CORS en FastAPI

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔧 Variables de Entorno del Backend

El backend debería tener estas variables configuradas:

```env
# Base de datos
DATABASE_URL=mysql://username:password@localhost/nutricion

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_STR=/api/v1
```

## 🔄 Flujo de Datos

### Registro de Usuario

1. Frontend envía datos a `POST /api/v1/usuarios/register`
2. Backend llama al procedimiento `sp_usuarios_registrar`
3. Se genera automáticamente un JWT token
4. Frontend recibe el token y lo almacena

### Login de Usuario

1. Frontend envía credenciales a `POST /api/v1/auth/login`
2. Backend llama al procedimiento `sp_login_get_hash`
3. Se verifica la contraseña hasheada
4. Se genera un JWT token si es válido
5. Frontend recibe el token

### Estructura de Respuestas

#### Login/Register Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Error Response
```json
{
  "detail": "Mensaje de error descriptivo"
}
```

## 🧪 Testing del Backend

### Probar Registro

```bash
curl -X POST "http://localhost:8000/api/v1/usuarios/register" \
  -H "Content-Type: application/json" \
  -d '{
    "nombres": "Juan",
    "apellidos": "Pérez",
    "usuario": "jperez",
    "correo": "juan@example.com",
    "contrasena": "password123",
    "rol_nombre": "TUTOR"
  }'
```

### Probar Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "jperez",
    "contrasena": "password123"
  }'
```

## 🔍 Verificación

### Checklist antes de usar el Frontend

- [ ] Base de datos MySQL creada y tablas configuradas
- [ ] Procedimientos almacenados ejecutados correctamente
- [ ] Backend FastAPI ejecutándose en puerto 8000
- [ ] CORS configurado para permitir localhost:5173
- [ ] Variables de entorno del backend configuradas
- [ ] Endpoints de autenticación funcionando

### Comandos de Verificación

```bash
# Verificar que el backend esté ejecutándose
curl http://localhost:8000/docs

# Verificar conectividad desde el frontend
curl http://localhost:8000/api/v1/auth/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"usuario":"test","contrasena":"test"}'
```

## ⚠️ Problemas Comunes

### Error de CORS
```
Access to fetch at 'http://localhost:8000/api/v1/auth/login' from origin 'http://localhost:5173' has been blocked by CORS policy
```
**Solución:** Configurar CORS en el backend para permitir localhost:5173

### Error de Base de Datos
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")
```
**Solución:** Verificar que MySQL esté ejecutándose y las credenciales sean correctas

### Error de Token
```
401 Unauthorized: Token inválido
```
**Solución:** Verificar que las claves SECRET_KEY coincidan entre frontend y backend

## 📞 Endpoints Completos

Una vez configurado, el backend debería exponer estos endpoints:

```
GET  /docs                          # Documentación Swagger
GET  /redoc                         # Documentación ReDoc
POST /api/v1/auth/login            # Login de usuario
POST /api/v1/usuarios/register     # Registro de usuario
POST /api/v1/usuarios/roles        # Crear rol (admin)
```

Con esta configuración, el frontend debería conectarse correctamente al backend y permitir el registro y login de usuarios.
