# Ejemplos de Uso - App Saludable API

Este archivo contiene ejemplos de cómo interactuar con la API del backend desde el frontend.

## 🔐 Autenticación

### Registro de Usuario

```typescript
import { apiService } from './src/services/api';

// Registrar un nuevo usuario tutor
const registerUser = async () => {
  const userData = {
    nombres: "María",
    apellidos: "González",
    usuario: "mgonzalez",
    correo: "maria.gonzalez@email.com",
    contrasena: "password123",
    rol_nombre: "TUTOR"
  };

  const response = await apiService.register(userData);
  
  if (response.success) {
    console.log('Usuario registrado:', response.data);
    // Token automáticamente guardado en localStorage
  } else {
    console.error('Error en registro:', response.error);
  }
};
```

### Login de Usuario

```typescript
// Iniciar sesión
const loginUser = async () => {
  const credentials = {
    usuario: "mgonzalez",
    contrasena: "password123"
  };

  const response = await apiService.login(credentials);
  
  if (response.success) {
    console.log('Login exitoso:', response.data);
    // Token automáticamente guardado en localStorage
  } else {
    console.error('Error en login:', response.error);
  }
};
```

### Logout de Usuario

```typescript
// Cerrar sesión
const logoutUser = async () => {
  const response = await apiService.logout();
  
  if (response.success) {
    console.log('Logout exitoso');
    // Token automáticamente removido del localStorage
  } else {
    console.error('Error en logout:', response.error);
    // El logout local se ejecuta de todas formas
  }
};
```

## 🎯 Uso del Contexto de Autenticación

### En un Componente React

```typescript
import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const MyComponent: React.FC = () => {
  const { user, login, logout, isAuthenticated, isLoading } = useAuth();

  const handleLogin = async () => {
    const result = await login({
      usuario: "mgonzalez",
      contrasena: "password123"
    });

    if (result.success) {
      console.log('Login exitoso');
    } else {
      console.error('Error:', result.error);
    }
  };

  const handleLogout = () => {
    logout();
    console.log('Sesión cerrada');
  };

  if (isLoading) {
    return <div>Cargando...</div>;
  }

  return (
    <div>
      {isAuthenticated ? (
        <div>
          <h1>Bienvenido, {user?.usr_usuario}</h1>
          <button onClick={handleLogout}>Cerrar Sesión</button>
        </div>
      ) : (
        <div>
          <h1>Por favor inicia sesión</h1>
          <button onClick={handleLogin}>Iniciar Sesión</button>
        </div>
      )}
    </div>
  );
};
```

## 🧪 Testing con curl

### Registro

```bash
curl -X POST "http://localhost:8000/api/v1/usuarios/register" \
  -H "Content-Type: application/json" \
  -d '{
    "nombres": "Carlos",
    "apellidos": "Ruiz",
    "usuario": "cruiz",
    "correo": "carlos.ruiz@email.com",
    "contrasena": "mypassword",
    "rol_nombre": "TUTOR"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "cruiz",
    "contrasena": "mypassword"
  }'
```

### Logout

```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Crear Rol (Admin)

```bash
curl -X POST "http://localhost:8000/api/v1/usuarios/roles" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "rol_codigo": "DOCTOR",
    "rol_nombre": "Doctor"
  }'
```

## 📱 Flujo de Usuario en Frontend

### 1. Nuevo Usuario (Registro)

```
1. Usuario llega a la app
2. Ve pantalla de Onboarding
3. Navega a registro
4. Completa formulario de registro
5. Backend crea usuario y devuelve JWT
6. Frontend guarda token y navega a dashboard
7. Usuario está autenticado
```

### 2. Usuario Existente (Login)

```
1. Usuario llega a la app
2. Si ya vio onboarding, va directo a login
3. Ingresa credenciales
4. Backend valida y devuelve JWT
5. Frontend guarda token y navega a dashboard
6. Usuario está autenticado
```

### 3. Sesión Persistente

```
1. Usuario regresa a la app
2. Frontend verifica token en localStorage
3. Si existe y es válido, va directo a dashboard
4. Si no existe o es inválido, va a login
```

## 🔄 Estados de la Aplicación

### Estados de Autenticación

```typescript
type AuthState = 
  | 'loading'        // Verificando token inicial
  | 'unauthenticated' // Sin token o token inválido
  | 'authenticated'   // Usuario logueado

type AppState = 
  | 'onboarding'     // Primera vez en la app
  | 'login'          // Pantalla de login
  | 'register'       // Pantalla de registro
  | 'main'           // Aplicación principal
```

## 🛠️ Manejo de Errores

### Errores Comunes

```typescript
// Error de red
{
  "success": false,
  "error": "Failed to fetch"
}

// Error de autenticación
{
  "success": false,
  "error": "Usuario no encontrado"
}

// Error de validación
{
  "success": false,
  "error": "Contraseña incorrecta"
}

// Error de registro (usuario duplicado)
{
  "success": false,
  "error": "Usuario ya registrado"
}
```

### Manejo en el Frontend

```typescript
const handleApiCall = async () => {
  try {
    const response = await apiService.login(credentials);
    
    if (response.success) {
      // Éxito
      handleSuccess(response.data);
    } else {
      // Error de API
      showError(response.error);
    }
  } catch (error) {
    // Error de red o JavaScript
    console.error('Error inesperado:', error);
    showError('Error de conexión. Verifica tu internet.');
  }
};
```

## 💾 Gestión de Tokens

### Almacenamiento

```typescript
// El token se guarda automáticamente en localStorage
const token = localStorage.getItem('auth_token');

// Verificar si el usuario está autenticado
const isAuthenticated = apiService.isAuthenticated();

// Limpiar token (logout)
apiService.removeToken();
```

### Headers de Autenticación

```typescript
// Los headers se agregan automáticamente en las peticiones
const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};
```

## 🔍 Debugging

### Console Logs Útiles

```typescript
// Ver datos del usuario actual
console.log('Usuario actual:', user);

// Ver estado de autenticación
console.log('Autenticado:', isAuthenticated);

// Ver token almacenado
console.log('Token:', apiService.getToken());

// Ver respuesta de API
console.log('Respuesta API:', response);
```

### DevTools

1. **Application > Local Storage** - Ver token guardado
2. **Network** - Monitorear peticiones HTTP
3. **Console** - Ver logs y errores
4. **React DevTools** - Ver estado de componentes

## ✅ Checklist de Testing

- [ ] Registro de nuevo usuario funciona
- [ ] Login con credenciales correctas funciona
- [ ] Login con credenciales incorrectas muestra error
- [ ] Logout limpia el token y regresa a login
- [ ] Navegación entre pantallas funciona
- [ ] Token persiste al recargar la página
- [ ] Estados de carga se muestran correctamente
- [ ] Errores se muestran al usuario
