// Tipos para autenticación
export interface UserLogin {
  usuario: string;
  contrasena: string;
}

export interface UserRegister {
  nombres: string;
  apellidos: string;
  usuario: string;
  correo: string;
  contrasena: string;
  rol_nombre: string;
}

export interface UserRegisterResponse {
  usr_id: number;
  msg: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  usr_id: number;
  usr_usuario: string;
  usr_correo: string;
  usr_nombre: string;
  usr_apellido: string;
  rol_id: number;
  usr_activo: boolean;
  password_hash?: string;
}

// Tipos para roles
export interface RolInsert {
  rol_codigo: string;
  rol_nombre: string;
}

export interface RolResponse {
  rol_id: number;
  msg: string;
}

// Tipos para respuestas de API
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

// Contexto de usuario autenticado
export interface AuthUser {
  usr_id: number;
  usr_usuario: string;
  usr_correo: string;
  usr_nombre: string;
  usr_apellido: string;
  rol_id: number;
  token: string;
}
