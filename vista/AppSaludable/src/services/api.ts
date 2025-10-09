/// <reference types="vite/client" />

import { 
  UserLogin, 
  GoogleLogin,
  UserRegister, 
  UserProfile,
  UserRegisterResponse,
  Token, 
  UserResponse,
  NinoCreate,
  NinoUpdate,
  NinoResponse,
  AnthropometryCreate,
  AnthropometryResponse,
  NutritionalStatusResponse,
  AlergiaCreate,
  AlergiaResponse,
  TipoAlergiaCreate,
  TipoAlergiaResponse,
  NinoWithAnthropometry,
  CreateChildProfileRequest,
  CreateChildProfileResponse,
  ApiResponse,
  PaginatedResponse,
  UserRoleChangeRequest,
  UserRoleChangeResponse,
  AssignTutorRequest
} from '../types/api';

class ApiService {
  private baseURL: string;
  private apiVersion: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    this.apiVersion = import.meta.env.VITE_API_VERSION || 'v1';
  }

  private getApiUrl(endpoint: string): string {
    const trimmedBase = this.baseURL.replace(/\/$/, '');
    const hasApiSegment = /\/api$/i.test(trimmedBase);
    const basePath = hasApiSegment ? trimmedBase : `${trimmedBase}/api`;
    const versionSegment = this.apiVersion ? `/${this.apiVersion}` : '';

    return `${basePath}${versionSegment}${endpoint}`;
  }

  private async makeRequest<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const token = localStorage.getItem(import.meta.env.VITE_TOKEN_KEY || 'auth_token');
      
      const config: RequestInit = {
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
          ...options.headers,
        },
        ...options,
      };

      const response = await fetch(url, config);
      
      if (!response.ok) {
        // Si el token expiró o es inválido (401), disparar evento de logout
        if (response.status === 401) {
          this.handleUnauthorized();
        }
        
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      return {
        success: true,
        data,
      };
    } catch (error) {
      console.error('API request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  private handleUnauthorized(): void {
    // Limpiar token y datos locales
    this.removeToken();
    if (typeof window !== 'undefined') {
      try {
        window.localStorage.removeItem('auth_avatar_hint');
      } catch (e) {
        console.warn('Error limpiando localStorage:', e);
      }
      
      // Disparar evento personalizado para que AuthContext lo maneje
      window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      
      // Redirigir al login después de un pequeño delay
      setTimeout(() => {
        window.location.href = '/login';
      }, 100);
    }
  }

  // Autenticación
  async login(userData: UserLogin): Promise<ApiResponse<Token>> {
    return this.makeRequest<Token>(
      this.getApiUrl('/auth/login'),
      {
        method: 'POST',
        body: JSON.stringify(userData),
      }
    );
  }

  async register(userData: UserRegister): Promise<ApiResponse<Token>> {
    return this.makeRequest<Token>(
      this.getApiUrl('/usuarios/register'),
      {
        method: 'POST',
        body: JSON.stringify(userData),
      }
    );
  }

  async logout(): Promise<ApiResponse<{ detail: string }>> {
    return this.makeRequest<{ detail: string }>(
      this.getApiUrl('/auth/logout'),
      {
        method: 'POST',
      }
    );
  }

  async loginWithGoogle(googleData: GoogleLogin): Promise<ApiResponse<Token>> {
    return this.makeRequest<Token>(
      this.getApiUrl('/auth/google'),
      {
        method: 'POST',
        body: JSON.stringify(googleData),
      }
    );
  }

  getGoogleAuthStartUrl(redirectTo: string): string {
    const baseUrl = this.getApiUrl('/auth/google/start');
    const url = new URL(baseUrl);
    url.searchParams.set('redirect_to', redirectTo);
    return url.toString();
  }

  // Métodos utilitarios para el token
  setToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  removeToken(): void {
    localStorage.removeItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // ===== MÉTODOS PARA NIÑOS =====

  // Crear un nuevo niño
  async createNino(ninoData: NinoCreate): Promise<ApiResponse<NinoResponse>> {
    return this.makeRequest<NinoResponse>(
      this.getApiUrl('/ninos'),
      {
        method: 'POST',
        body: JSON.stringify(ninoData),
      }
    );
  }

  // Obtener todos los niños del usuario actual
  async getNinos(): Promise<ApiResponse<NinoWithAnthropometry[]>> {
    return this.makeRequest<NinoWithAnthropometry[]>(
      this.getApiUrl('/ninos/')
    );
  }

  // Obtener un niño por ID
  async getNino(ninoId: number): Promise<ApiResponse<NinoResponse>> {
    return this.makeRequest<NinoResponse>(
      this.getApiUrl(`/ninos/${ninoId}`)
    );
  }

  // Actualizar un niño
  async updateNino(ninoId: number, ninoData: NinoUpdate): Promise<ApiResponse<NinoResponse>> {
    return this.makeRequest<NinoResponse>(
      this.getApiUrl(`/ninos/${ninoId}`),
      {
        method: 'PUT',
        body: JSON.stringify(ninoData),
      }
    );
  }

  // Eliminar un niño
  async deleteNino(ninoId: number): Promise<ApiResponse<{ message: string }>> {
    return this.makeRequest<{ message: string }>(
      this.getApiUrl(`/ninos/${ninoId}`),
      {
        method: 'DELETE',
      }
    );
  }

  async assignTutorToChild(ninoId: number, payload: AssignTutorRequest): Promise<ApiResponse<NinoResponse>> {
    return this.makeRequest<NinoResponse>(
      this.getApiUrl(`/ninos/${ninoId}/assign-tutor`),
      {
        method: 'POST',
        body: JSON.stringify(payload),
      }
    );
  }

  // ===== MÉTODOS PARA ANTROPOMETRÍA =====

  // Agregar nueva medición antropométrica
  async addAnthropometry(ninoId: number, data: AnthropometryCreate): Promise<ApiResponse<AnthropometryResponse>> {
    return this.makeRequest<AnthropometryResponse>(
      this.getApiUrl(`/ninos/${ninoId}/anthropometry`),
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  // Obtener historial antropométrico de un niño
  async getAnthropometryHistory(ninoId: number): Promise<ApiResponse<AnthropometryResponse[]>> {
    return this.makeRequest<AnthropometryResponse[]>(
      this.getApiUrl(`/ninos/${ninoId}/anthropometry`)
    );
  }

  // ===== MÉTODOS PARA EVALUACIÓN NUTRICIONAL =====

  // Evaluar estado nutricional
  async evaluateNutritionalStatus(ninoId: number): Promise<ApiResponse<NutritionalStatusResponse>> {
    return this.makeRequest<NutritionalStatusResponse>(
      this.getApiUrl(`/ninos/${ninoId}/nutritional-status`)
    );
  }

  // ===== MÉTODOS PARA ALERGIAS =====

  // Agregar alergia a un niño
  async addAllergy(ninoId: number, allergiaData: AlergiaCreate): Promise<ApiResponse<AlergiaResponse>> {
    return this.makeRequest<AlergiaResponse>(
      this.getApiUrl(`/ninos/${ninoId}/alergias`),
      {
        method: 'POST',
        body: JSON.stringify(allergiaData),
      }
    );
  }

  // Obtener alergias de un niño
  async getAllergies(ninoId: number): Promise<ApiResponse<AlergiaResponse[]>> {
    return this.makeRequest<AlergiaResponse[]>(
      this.getApiUrl(`/ninos/${ninoId}/alergias`)
    );
  }

  // Eliminar alergia de un niño
  async removeAllergy(ninoId: number, allergiaId: number): Promise<ApiResponse<{ message: string }>> {
    return this.makeRequest<{ message: string }>(
      this.getApiUrl(`/ninos/${ninoId}/alergias/${allergiaId}`),
      {
        method: 'DELETE',
      }
    );
  }

  // ===== MÉTODOS PARA TIPOS DE ALERGIAS =====

  // Obtener todos los tipos de alergias disponibles
  async getAllergyTypes(q?: string, limit: number = 50): Promise<ApiResponse<TipoAlergiaResponse[]>> {
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (limit) params.set('limit', String(limit));
    const url = this.getApiUrl(`/alergias/tipos${params.toString() ? `?${params.toString()}` : ''}`);
    return this.makeRequest<TipoAlergiaResponse[]>(url);
  }

  // Crear nuevo tipo de alergia (solo admin)
  async createAllergyType(tipoData: TipoAlergiaCreate): Promise<ApiResponse<TipoAlergiaResponse>> {
    return this.makeRequest<TipoAlergiaResponse>(
      this.getApiUrl('/alergias/tipos'),
      {
        method: 'POST',
        body: JSON.stringify(tipoData),
      }
    );
  }

  // ===== ENTIDADES =====
  async searchEntities(q?: string, limit: number = 20): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams();
    if (q) params.set('q', q);
    if (limit) params.set('limit', String(limit));
    const url = this.getApiUrl(`/entidades${params.toString() ? `?${params.toString()}` : ''}`);
    return this.makeRequest<any[]>(url);
  }

  async getEntityTypes(): Promise<ApiResponse<any[]>> {
    return this.makeRequest<any[]>(
      this.getApiUrl('/entidades/tipos')
    );
  }

  // ===== MÉTODOS PARA PERFIL DE USUARIO =====

  // Actualizar perfil de usuario
  async updateProfile(profileData: UserProfile): Promise<ApiResponse<UserResponse>> {
    return this.makeRequest<UserResponse>(
      this.getApiUrl('/usuarios/profile'),
      {
        method: 'PUT',
        body: JSON.stringify(profileData),
      }
    );
  }

  // Obtener perfil de usuario actual
  async getProfile(): Promise<ApiResponse<UserResponse>> {
    return this.makeRequest<UserResponse>(
      this.getApiUrl('/usuarios/me')
    );
  }

  async changeUserRole(usrId: number, payload: UserRoleChangeRequest): Promise<ApiResponse<UserRoleChangeResponse>> {
    return this.makeRequest<UserRoleChangeResponse>(
      this.getApiUrl(`/usuarios/${usrId}/role`),
      {
        method: 'PUT',
        body: JSON.stringify(payload),
      }
    );
  }

  // ===== MÉTODOS COMBINADOS =====

  // Crear perfil completo de niño (niño + antropometría + evaluación)
  async createChildProfile(data: CreateChildProfileRequest): Promise<ApiResponse<CreateChildProfileResponse>> {
    try {
      // 1. Crear el niño
      const ninoResponse = await this.createNino(data.nino);
      if (!ninoResponse.data) {
        throw new Error('Error creando el niño');
      }

      const ninoId = ninoResponse.data.nin_id;

      // 2. Agregar antropometría
      const antropometriaResponse = await this.addAnthropometry(ninoId, data.antropometria);
      if (!antropometriaResponse.data) {
        throw new Error('Error agregando antropometría');
      }

      // 3. Evaluar estado nutricional
      const evaluacionResponse = await this.evaluateNutritionalStatus(ninoId);
      if (!evaluacionResponse.data) {
        throw new Error('Error evaluando estado nutricional');
      }

      return {
        success: true,
        data: {
          nino: ninoResponse.data,
          antropometria: antropometriaResponse.data,
          estado_nutricional: evaluacionResponse.data,
          message: 'Perfil del niño creado exitosamente'
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error creando perfil del niño'
      };
    }
  }

  // Obtener información completa de un niño
  async getChildWithData(ninoId: number): Promise<ApiResponse<NinoWithAnthropometry>> {
    try {
      const [ninoResponse, antropometriasResponse, alergiasResponse] = await Promise.all([
        this.getNino(ninoId),
        this.getAnthropometryHistory(ninoId),
        this.getAllergies(ninoId),
      ]);

      if (!ninoResponse.data) {
        throw new Error('Error obteniendo información del niño');
      }

      const rawNinoData: any = ninoResponse.data;

      let nino: NinoResponse;
      let antropometrias: AnthropometryResponse[] = Array.isArray(antropometriasResponse?.data)
        ? antropometriasResponse.data
        : [];
      let alergias: AlergiaResponse[] = Array.isArray(alergiasResponse?.data)
        ? alergiasResponse.data
        : [];
      let ultimoEstadoNutricional: NutritionalStatusResponse | undefined;

      if (rawNinoData && typeof rawNinoData === 'object' && 'nino' in rawNinoData) {
        nino = rawNinoData.nino as NinoResponse;

        if (!antropometrias.length && Array.isArray(rawNinoData.antropometrias)) {
          antropometrias = rawNinoData.antropometrias;
        }

        if (!alergias.length && Array.isArray(rawNinoData.alergias)) {
          alergias = rawNinoData.alergias;
        }

        if (rawNinoData.ultimo_estado_nutricional) {
          ultimoEstadoNutricional = rawNinoData.ultimo_estado_nutricional as NutritionalStatusResponse;
        }
      } else {
        nino = rawNinoData as NinoResponse;
      }

      if (!ultimoEstadoNutricional) {
        try {
          const evaluacionResponse = await this.evaluateNutritionalStatus(ninoId);
          ultimoEstadoNutricional = evaluacionResponse.data;
        } catch (error) {
          // Si no hay datos suficientes para evaluar, continuamos sin la evaluación
          console.warn('No se pudo obtener evaluación nutricional:', error);
        }
      }

      return {
        success: true,
        data: {
          nino,
          antropometrias,
          alergias,
          ultimo_estado_nutricional: ultimoEstadoNutricional,
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Error obteniendo datos del niño',
      };
    }
  }

  // ===== ANTROPOMETRÍA PERSONAL (SELF) =====
  async getSelfChild(): Promise<ApiResponse<NinoResponse>> {
    return this.makeRequest<NinoResponse>(
      this.getApiUrl('/children/self')
    );
  }

  async addSelfAnthropometry(data: AnthropometryCreate): Promise<ApiResponse<AnthropometryResponse>> {
    const selfChild = await this.getSelfChild();
    if (!selfChild.data) {
      return { success: false, error: 'No se pudo obtener/crear el perfil personal' };
    }
    const ninId = selfChild.data.nin_id;
    return this.makeRequest<AnthropometryResponse>(
      this.getApiUrl(`/children/${ninId}/anthropometry`),
      { method: 'POST', body: JSON.stringify(data) }
    );
  }

  async getSelfAnthropometryHistory(): Promise<ApiResponse<AnthropometryResponse[]>> {
    const selfChild = await this.getSelfChild();
    if (!selfChild.data) {
      return { success: false, error: 'No se pudo obtener el perfil personal' };
    }
    const ninId = selfChild.data.nin_id;
    return this.makeRequest<AnthropometryResponse[]>(
      this.getApiUrl(`/children/${ninId}/anthropometry`)
    );
  }

  async getSelfNutritionalStatus(): Promise<ApiResponse<NutritionalStatusResponse>> {
    const selfChild = await this.getSelfChild();
    if (!selfChild.data) {
      return { success: false, error: 'No se pudo obtener el perfil personal' };
    }
    const ninId = selfChild.data.nin_id;
    return this.makeRequest<NutritionalStatusResponse>(
      this.getApiUrl(`/children/${ninId}/nutritional-status`)
    );
  }
}

export const apiService = new ApiService();
