# Documentación del Backend - API de Nutrición

## Tabla de Contenidos
1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Configuración y Despliegue](#configuración-y-despliegue)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Endpoints de la API](#endpoints-de-la-api)
6. [Servicios de Aplicación](#servicios-de-aplicación)
7. [Modelos de Datos](#modelos-de-datos)
8. [Sistema de Autenticación](#sistema-de-autenticación)
9. [Integración con ML](#integración-con-ml)
10. [Consideraciones de Seguridad](#consideraciones-de-seguridad)

## Introducción

El backend de la API de Nutrición es una aplicación FastAPI que implementa una arquitectura limpia (Clean Architecture) para gestionar información nutricional de niños y usuarios. El sistema proporciona funcionalidades completas para:

- Gestión de usuarios y autenticación
- Manejo de perfiles de niños y antropometrías
- Sistema de roles y permisos
- Integración con servicios de Machine Learning
- Gestión de alergias y entidades nutricionales
- Autenticación con Google OAuth2

## Arquitectura del Sistema

### Clean Architecture

El proyecto implementa Clean Architecture con las siguientes capas:

```
app/
├── api/                    # Capa de Presentación (Controllers)
├── application/            # Capa de Aplicación (Use Cases)
├── domain/                 # Capa de Dominio (Entidades y Reglas de Negocio)
├── infrastructure/         # Capa de Infraestructura (Acceso a Datos)
└── schemas/               # DTOs y Validaciones
```

### Principios Implementados

1. **Separación de Responsabilidades**: Cada capa tiene una responsabilidad específica
2. **Inversión de Dependencias**: Las capas superiores no dependen de las inferiores
3. **Inyección de Dependencias**: Uso de FastAPI Depends para gestión de dependencias
4. **Repository Pattern**: Abstracción del acceso a datos

## Configuración y Despliegue

### Variables de Entorno Requeridas

```bash
DATABASE_URL=mysql+pymysql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
GOOGLE_POST_LOGIN_REDIRECT=http://localhost:5173
FRONTEND_ORIGINS=http://localhost:5173,https://appsaludable.netlify.app
```

### Docker y Docker Compose

El sistema está configurado para ejecutarse con Docker:

```bash
# Construir y ejecutar
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d
```

### Dependencias Principales

- **FastAPI 0.104.1**: Framework web moderno y rápido
- **SQLAlchemy 2.0.36**: ORM para Python
- **PyMySQL 1.1.0**: Driver MySQL
- **Alembic 1.13.3**: Migraciones de base de datos
- **python-jose**: Manejo de JWT
- **passlib**: Hashing de contraseñas
- **google-auth**: Autenticación con Google

## Estructura del Proyecto

### Capa de API (Presentación)

```
app/api/v1/
├── api.py              # Router principal
├── deps.py             # Dependencias compartidas
└── endpoints/
    ├── auth.py         # Autenticación
    ├── usuarios.py     # Gestión de usuarios
    ├── ninos.py        # Gestión de niños
    ├── ml.py           # Integración ML
    └── entidades.py    # Entidades nutricionales
```

### Capa de Aplicación

```
app/application/services/
├── auth_service.py     # Lógica de autenticación
├── usuarios_service.py # Lógica de usuarios
└── ninos_service.py   # Lógica de niños
```

### Capa de Dominio

```
app/domain/
├── entities/           # Entidades de dominio
├── interfaces/         # Contratos/Interfaces
├── policies/           # Reglas de negocio
└── utils/              # Utilidades de dominio
```

### Capa de Infraestructura

```
app/infrastructure/
├── db/                 # Configuración de base de datos
├── repositories/       # Implementación de repositorios
├── security/           # Servicios de seguridad
└── external/           # Servicios externos
```

## Endpoints de la API

### Autenticación (`/api/v1/auth`)

#### POST `/login`
- **Descripción**: Autenticación con usuario y contraseña
- **Body**: `UserLogin` (usuario, contrasena)
- **Response**: `Token` (access_token, token_type)

#### POST `/logout`
- **Descripción**: Cerrar sesión del usuario
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"detail": "logout ok"}`

#### POST `/google`
- **Descripción**: Autenticación con Google ID Token
- **Body**: `GoogleLogin` (id_token)
- **Response**: `Token`

#### GET `/google/start`
- **Descripción**: Iniciar flujo OAuth2 de Google
- **Query**: `redirect_to` (opcional)
- **Response**: Redirect a Google OAuth

#### GET `/google/callback`
- **Descripción**: Callback de Google OAuth2
- **Query**: `code`, `state`, `error`
- **Response**: Redirect al frontend con token

### Usuarios (`/api/v1/usuarios`)

#### POST `/register`
- **Descripción**: Registrar nuevo usuario
- **Body**: `UserRegister`
- **Response**: `Token`

#### POST `/roles`
- **Descripción**: Crear nuevo rol
- **Body**: `RolInsert` (rol_codigo, rol_nombre)
- **Response**: `RolResponse`

#### GET `/me`
- **Descripción**: Obtener perfil del usuario autenticado
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Perfil completo del usuario

#### PUT `/profile`
- **Descripción**: Actualizar perfil del usuario
- **Body**: `UserProfileSchema`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Perfil actualizado

#### PUT `/{usr_id}/role`
- **Descripción**: Cambiar rol de usuario
- **Body**: `UserRoleChangeRequest`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `UserRoleChangeResponse`

### Niños (`/api/v1/children` y `/api/v1/ninos`)

#### GET `/self`
- **Descripción**: Obtener o crear perfil antropométrico personal
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `NinoResponse`

#### GET `/`
- **Descripción**: Listar niños del usuario
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Lista de `NinoResponse`

#### POST `/`
- **Descripción**: Crear nuevo niño
- **Body**: `NinoCreate`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `NinoResponse`

#### GET `/{nino_id}`
- **Descripción**: Obtener niño específico
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `NinoResponse`

#### PUT `/{nino_id}`
- **Descripción**: Actualizar niño
- **Body**: `NinoUpdate`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `NinoResponse`

#### DELETE `/{nino_id}`
- **Descripción**: Eliminar niño
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"detail": "Niño eliminado"}`

#### POST `/{nino_id}/anthropometry`
- **Descripción**: Agregar medición antropométrica
- **Body**: `AnthropometryCreate`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `AnthropometryResponse`

#### GET `/{nino_id}/anthropometry`
- **Descripción**: Obtener historial antropométrico
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Lista de `AnthropometryResponse`

#### GET `/{nino_id}/nutritional-status`
- **Descripción**: Obtener estado nutricional actual
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `NutritionalStatusResponse`

#### POST `/{nino_id}/allergies`
- **Descripción**: Agregar alergia
- **Body**: `AlergiaCreate`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `AlergiaResponse`

#### GET `/{nino_id}/allergies`
- **Descripción**: Obtener alergias del niño
- **Headers**: `Authorization: Bearer <token>`
- **Response**: Lista de `AlergiaResponse`

#### POST `/{nino_id}/assign-tutor`
- **Descripción**: Asignar tutor al niño
- **Body**: `AssignTutorRequest`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"detail": "Tutor asignado"}`

### Alergias (`/api/v1/alergias`)

#### GET `/tipos`
- **Descripción**: Obtener tipos de alergias
- **Query**: `q` (búsqueda), `limit` (límite)
- **Response**: Lista de tipos de alergias

#### POST `/tipos`
- **Descripción**: Crear tipo de alergia
- **Body**: `{"ta_codigo": str, "ta_nombre": str, "ta_categoria": str}`
- **Response**: Tipo de alergia creado

### Entidades (`/api/v1/entidades`)

#### GET `/`
- **Descripción**: Listar entidades nutricionales
- **Query**: `q` (búsqueda), `limit` (límite)
- **Response**: Lista de entidades

#### GET `/tipos`
- **Descripción**: Obtener tipos de entidades
- **Response**: Lista de tipos de entidades

### Machine Learning (`/api/v1/ml`)

#### POST `/summary`
- **Descripción**: Generar resumen nutricional usando ML/LLM
- **Body**: `SummaryRequest` (features, scores, prefer_llm)
- **Response**: `SummaryResponse` (text, used_llm)

### Health Check

#### GET `/health`
- **Descripción**: Verificar estado del servicio
- **Response**: `{"status": "ok"}`

## Servicios de Aplicación

### AuthService

**Ubicación**: `app/application/services/auth_service.py`

**Responsabilidades**:
- Autenticación de usuarios
- Generación y validación de JWT
- Integración con Google OAuth2
- Gestión de sesiones

**Métodos principales**:
- `login_user()`: Autenticación tradicional
- `login_google_user()`: Autenticación con Google
- `get_current_user()`: Obtener usuario actual desde token
- `build_google_authorize_url()`: Construir URL de autorización Google
- `complete_google_oauth()`: Completar flujo OAuth2

### UsuariosService

**Ubicación**: `app/application/services/usuarios_service.py`

**Responsabilidades**:
- Gestión de usuarios
- Manejo de perfiles
- Gestión de roles
- Validaciones de negocio

**Métodos principales**:
- `register_user()`: Registrar nuevo usuario
- `get_user_with_profile()`: Obtener usuario con perfil
- `update_user_profile()`: Actualizar perfil
- `create_role()`: Crear nuevo rol
- `change_user_role()`: Cambiar rol de usuario

### NinosService

**Ubicación**: `app/application/services/ninos_service.py`

**Responsabilidades**:
- Gestión de perfiles de niños
- Manejo de antropometrías
- Cálculo de estados nutricionales
- Gestión de alergias

**Métodos principales**:
- `create_child()`: Crear nuevo niño
- `get_child_by_id()`: Obtener niño por ID
- `update_child()`: Actualizar niño
- `add_anthropometry()`: Agregar medición antropométrica
- `get_nutritional_status()`: Calcular estado nutricional
- `add_allergy()`: Agregar alergia

## Modelos de Datos

### Modelos de Seguridad

#### Usuario
```python
class Usuario(Base):
    usr_id: BigInteger          # ID único
    usr_dni: String(12)        # DNI
    usr_correo: String(190)     # Email (único)
    usr_contrasena: CHAR(60)    # Hash de contraseña
    usr_nombre: String(150)     # Nombre
    usr_apellido: String(150)  # Apellido
    usr_usuario: String(150)    # Nombre de usuario
    rol_id: SmallInteger        # ID del rol
    usr_activo: TinyInteger     # Estado activo
    creado_en: DateTime         # Fecha de creación
    actualizado_en: DateTime    # Fecha de actualización
    eliminado_en: DateTime      # Fecha de eliminación (soft delete)
```

#### Rol
```python
class Rol(Base):
    rol_id: SmallInteger        # ID único
    rol_codigo: String(32)      # Código del rol (único)
    rol_nombre: String(80)      # Nombre del rol
    creado_en: DateTime         # Fecha de creación
    actualizado_en: DateTime    # Fecha de actualización
```

### Modelos de Niños

#### Niño
```python
class Nino(Base):
    nino_id: BigInteger         # ID único
    nino_nombre: String(150)    # Nombre del niño
    nino_apellido: String(150)  # Apellido del niño
    fecha_nac: Date            # Fecha de nacimiento
    genero: CHAR(1)            # Género (M/F)
    usr_id_propietario: BigInteger  # ID del propietario
    usr_id_tutor: BigInteger   # ID del tutor
    creado_en: DateTime        # Fecha de creación
    actualizado_en: DateTime   # Fecha de actualización
```

#### Antropometría
```python
class Anthropometria(Base):
    ant_id: BigInteger         # ID único
    nino_id: BigInteger        # ID del niño
    peso: DECIMAL(5,2)        # Peso en kg
    talla: DECIMAL(5,2)        # Talla en cm
    fecha_medicion: Date      # Fecha de medición
    observaciones: Text        # Observaciones
    creado_en: DateTime       # Fecha de creación
```

### Esquemas Pydantic

#### Auth Schemas
```python
class UserLogin(BaseModel):
    usuario: str
    contrasena: str

class Token(BaseModel):
    access_token: str
    token_type: str

class GoogleLogin(BaseModel):
    id_token: str
    access_token: Optional[str] = None
```

#### Niño Schemas
```python
class NinoCreate(BaseModel):
    nino_nombre: str
    nino_apellido: str
    fecha_nac: date
    genero: str

class NinoResponse(BaseModel):
    nino_id: int
    nino_nombre: str
    nino_apellido: str
    fecha_nac: date
    genero: str
    usr_id_propietario: int
    usr_id_tutor: Optional[int]
```

## Sistema de Autenticación

### Autenticación Tradicional

1. **Login**: Usuario envía credenciales
2. **Validación**: Se verifica usuario y contraseña
3. **JWT**: Se genera token JWT con información del usuario
4. **Respuesta**: Se retorna token al cliente

### Autenticación con Google OAuth2

1. **Inicio**: Cliente redirige a `/auth/google/start`
2. **Autorización**: Usuario autoriza en Google
3. **Callback**: Google redirige a `/auth/google/callback`
4. **Intercambio**: Se intercambia código por token
5. **Validación**: Se valida token con Google
6. **Usuario**: Se crea/actualiza usuario en BD
7. **JWT**: Se genera JWT propio
8. **Redirect**: Se redirige al frontend con token

### Autorización

- **JWT Tokens**: Tokens con expiración de 30 minutos
- **Roles**: Sistema de roles con permisos específicos
- **Middleware**: Validación automática en endpoints protegidos
- **Dependencias**: `get_current_user()` para obtener usuario actual

## Integración con ML

### Servicio de Resúmenes

**Ubicación**: `app/api/v1/endpoints/ml.py`

**Funcionalidad**:
- Generación de resúmenes nutricionales
- Integración con modelo de ML local
- Fallback a LLM cuando está disponible
- Formateo de recomendaciones

**Flujo**:
1. Cliente envía features y scores
2. Se intenta usar LLM si está disponible
3. Si falla, se usa modelo local
4. Se retorna resumen formateado

### Integración con ML-Recomendator

El sistema se integra con el módulo de ML ubicado en `modelo/ml-recomendator`:
- Importación dinámica del módulo
- Uso de funciones de resumen y formateo
- Manejo de errores y fallbacks

## Consideraciones de Seguridad

### CORS
- Configuración flexible de orígenes permitidos
- Soporte para múltiples entornos (desarrollo, producción)
- Headers de autorización expuestos

### Validación de Datos
- Esquemas Pydantic para validación automática
- Validación de tipos y formatos
- Sanitización de inputs

### Autenticación y Autorización
- JWT con expiración configurable
- Hash seguro de contraseñas (bcrypt)
- Validación de tokens en cada request
- Sistema de roles granular

### Base de Datos
- Soft delete para usuarios
- Auditoría con timestamps
- Transacciones para operaciones críticas
- Validación a nivel de base de datos

### Logging y Monitoreo
- Logging estructurado
- Health check endpoint
- Manejo de errores centralizado
- Trazabilidad de operaciones

## Consideraciones de Rendimiento

### Optimizaciones Implementadas
- Conexiones de base de datos con pool
- Lazy loading en relaciones SQLAlchemy
- Paginación en endpoints de listado
- Caché de consultas frecuentes

### Escalabilidad
- Arquitectura stateless
- Separación de responsabilidades
- Preparado para microservicios
- Configuración por variables de entorno

## Mantenimiento y Desarrollo

### Migraciones
- Alembic para gestión de esquemas
- Versionado de cambios de BD
- Scripts de migración automáticos

### Testing
- Estructura preparada para tests
- Fixtures para datos de prueba
- Tests de integración con BD

### Documentación
- OpenAPI/Swagger automático
- Documentación de endpoints
- Esquemas de validación documentados

---

Esta documentación proporciona una visión completa del backend de la API de Nutrición, incluyendo su arquitectura, funcionalidades, y consideraciones técnicas. El sistema está diseñado para ser escalable, mantenible y seguro, siguiendo las mejores prácticas de desarrollo de APIs modernas.
