// Tipos para autenticación
export interface UserLogin {
  usuario: string;
  contrasena: string;
}

export interface GoogleLogin {
  id_token: string;
  access_token?: string;
}

export interface UserRegister {
  nombres: string;
  apellidos: string;
  usuario: string;
  correo: string;
  contrasena: string;
  rol_nombre: string;
}

export interface UserProfile {
  dni?: string;
  nombres?: string;
  apellidos?: string;
  avatar_url?: string;
  telefono?: string;
  direccion?: string;
  genero?: 'M' | 'F' | 'X';
  fecha_nac?: string; // ISO date string
  idioma?: string;
}

export interface UserRegisterResponse {
  usr_id: number;
  msg: string;
}

export interface UserRoleChangeRequest {
  rol_codigo: string;
}

export interface UserRoleChangeResponse {
  usr_id: number;
  rol_id: number;
  rol_codigo: string;
  rol_nombre: string;
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
  // Campos adicionales del perfil
  dni?: string;
  avatar_url?: string;
  telefono?: string;
  direccion?: string;
  genero?: 'M' | 'F' | 'X';
  fecha_nac?: string;
  idioma?: string;
  creado_en?: string;
}

// Tipos para niños
export interface NinoCreate {
  nin_nombres: string;
  nin_fecha_nac: string; // ISO date string
  nin_sexo: 'M' | 'F';
  ent_id?: number;
}

export interface NinoUpdate {
  nin_nombres?: string;
  ent_id?: number;
  nin_fecha_nac?: string;
}

export interface NinoResponse {
  nin_id: number;
  nin_nombres: string;
  nin_fecha_nac: string;
  nin_sexo: string;
  ent_id?: number;
  ent_nombre?: string | null;
  ent_codigo?: string | null;
  ent_direccion?: string | null;
  ent_departamento?: string | null;
  ent_provincia?: string | null;
  ent_distrito?: string | null;
  edad_meses: number;
  creado_en: string;
  actualizado_en: string;
}

// Tipos para antropometría
export interface AnthropometryCreate {
  ant_peso_kg: number;
  ant_talla_cm: number;
  ant_fecha?: string; // ISO date string
}

export interface AnthropometryResponse {
  ant_id: number;
  nin_id: number;
  ant_fecha: string;
  ant_edad_meses?: number;
  ant_peso_kg: number;
  ant_talla_cm: number;
  ant_z_imc?: number;
  ant_z_peso_edad?: number;
  ant_z_talla_edad?: number;
  imc?: number;
  creado_en: string;
}

// Tipos para evaluación nutricional
export interface NutritionalStatusResponse {
  imc: number;
  z_score_imc?: number;
  classification: string;
  percentile?: number;
  recommendations: string[];
  risk_level: string;
}

// Tipos para alergias
export interface AlergiaCreate {
  ta_codigo: string;
  severidad?: 'LEVE' | 'MODERADA' | 'SEVERA';
}

export interface AlergiaResponse {
  na_id: number;
  nin_id: number;
  ta_codigo: string;
  ta_nombre: string;
  ta_categoria: string;
  na_severidad: string;
  creado_en: string;
}

export interface TipoAlergiaCreate {
  ta_codigo: string;
  ta_nombre: string;
  ta_categoria: 'ALIMENTARIA' | 'MEDICAMENTO' | 'AMBIENTAL';
}

export interface TipoAlergiaResponse {
  ta_id: number;
  ta_codigo: string;
  ta_nombre: string;
  ta_categoria: string;
  ta_activo: boolean;
  creado_en: string;
}

// Tipos combinados
export interface NinoWithAnthropometry {
  nino: NinoResponse;
  antropometrias: AnthropometryResponse[];
  alergias: AlergiaResponse[];
  ultimo_estado_nutricional?: NutritionalStatusResponse;
}

export interface CreateChildProfileRequest {
  nino: NinoCreate;
  antropometria: AnthropometryCreate;
}

export interface CreateChildProfileResponse {
  nino: NinoResponse;
  antropometria: AnthropometryResponse;
  estado_nutricional: NutritionalStatusResponse;
  message: string;
}

export interface AssignTutorRequest {
  usr_id_tutor: number;
}

// Tipos para respuestas de API
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  detail?: string;
  success?: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
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
  success?: boolean;
  data?: T;
  message?: string;
  error?: string;
  detail?: string;
}

// Contexto de usuario autenticado
export interface AuthUser {
  usr_id: number;
  usr_usuario: string;
  usr_correo: string;
  usr_nombre: string;
  usr_apellido: string;
  rol_id: number;
  avatar_url?: string;
  token: string;
}
