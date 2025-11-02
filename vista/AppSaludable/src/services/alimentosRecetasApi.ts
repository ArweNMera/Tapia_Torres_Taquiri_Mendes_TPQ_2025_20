import {
  AlimentoResponse,
  AlimentoCreate,
  AlimentoUpdate,
  AlimentoConNutrientesResponse,
  RecetaResponse,
  RecetaCreate,
  RecetaUpdate,
  RecetaCompletaResponse,
  RecetaIngredienteCreate,
  RecetaIngredienteUpdate,
  NutrienteResponse,
  ApiResponse,
} from '../types/api';

import { getConfig } from '../config/environment';

class AlimentosRecetasApiService {
  private baseURL: string;
  private apiVersion: string;
  private tokenKey: string;

  constructor() {
    const config = getConfig();
    this.baseURL = config.API_BASE_URL;
    this.apiVersion = config.API_VERSION;
    this.tokenKey = config.TOKEN_KEY;

    // Debug: verificar qué URL se está usando
    console.log('🍔 Alimentos/Recetas API Base URL:', this.baseURL);
  }

  private getApiUrl(endpoint: string): string {
    const trimmedBase = this.baseURL.replace(/\/$/, '');
    const basePath = `${trimmedBase}/api`;
    const versionSegment = `/${this.apiVersion}`;
    // Asegurar que el endpoint comience con /
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${basePath}${versionSegment}${normalizedEndpoint}`;
  }

  private async makeRequest<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const token = localStorage.getItem(this.tokenKey);

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
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      console.error('API request failed:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // ========== MÉTODOS PARA ALIMENTOS ==========

  /**
   * Obtener lista de alimentos con búsqueda opcional
   */
  async getAlimentos(q?: string, limit: number = 100): Promise<ApiResponse<AlimentoResponse[]>> {
    const params = new URLSearchParams();
    if (q) params.append('q', q);
    params.append('limit', limit.toString());

    const url = this.getApiUrl(`/nutricion/alimentos?${params.toString()}`);
    return this.makeRequest<AlimentoResponse[]>(url);
  }

  /**
   * Obtener un alimento específico con sus nutrientes
   */
  async getAlimento(aliId: number): Promise<ApiResponse<AlimentoConNutrientesResponse>> {
    const url = this.getApiUrl(`/nutricion/alimentos/${aliId}`);
    return this.makeRequest<AlimentoConNutrientesResponse>(url);
  }

  /**
   * Crear un nuevo alimento
   */
  async createAlimento(alimentoData: AlimentoCreate): Promise<ApiResponse<AlimentoResponse>> {
    const url = this.getApiUrl('/nutricion/alimentos');
    return this.makeRequest<AlimentoResponse>(url, {
      method: 'POST',
      body: JSON.stringify(alimentoData),
    });
  }

  /**
   * Actualizar un alimento existente
   */
  async updateAlimento(aliId: number, alimentoData: AlimentoUpdate): Promise<ApiResponse<AlimentoResponse>> {
    const url = this.getApiUrl(`/nutricion/alimentos/${aliId}`);
    return this.makeRequest<AlimentoResponse>(url, {
      method: 'PUT',
      body: JSON.stringify(alimentoData),
    });
  }

  /**
   * Eliminar un alimento
   */
  async deleteAlimento(aliId: number): Promise<ApiResponse<{ message: string }>> {
    const url = this.getApiUrl(`/nutricion/alimentos/${aliId}`);
    return this.makeRequest<{ message: string }>(url, {
      method: 'DELETE',
    });
  }

  // ========== MÉTODOS PARA RECETAS ==========

  /**
   * Obtener lista de recetas con filtro opcional por tipo de comida
   */
  async getRecetas(tipoComida?: string, limit: number = 100): Promise<ApiResponse<RecetaResponse[]>> {
    const params = new URLSearchParams();
    if (tipoComida) params.append('tipo_comida', tipoComida);
    params.append('limit', limit.toString());

    const url = this.getApiUrl(`/nutricion/recetas?${params.toString()}`);
    return this.makeRequest<RecetaResponse[]>(url);
  }

  /**
   * Obtener una receta específica con ingredientes y información nutricional
   */
  async getReceta(recId: number): Promise<ApiResponse<RecetaCompletaResponse>> {
    const url = this.getApiUrl(`/nutricion/recetas/${recId}`);
    return this.makeRequest<RecetaCompletaResponse>(url);
  }

  /**
   * Crear una nueva receta
   */
  async createReceta(recetaData: RecetaCreate): Promise<ApiResponse<RecetaResponse>> {
    const url = this.getApiUrl('/nutricion/recetas');
    return this.makeRequest<RecetaResponse>(url, {
      method: 'POST',
      body: JSON.stringify(recetaData),
    });
  }

  /**
   * Actualizar una receta existente
   */
  async updateReceta(recId: number, recetaData: RecetaUpdate): Promise<ApiResponse<RecetaResponse>> {
    const url = this.getApiUrl(`/nutricion/recetas/${recId}`);
    return this.makeRequest<RecetaResponse>(url, {
      method: 'PUT',
      body: JSON.stringify(recetaData),
    });
  }

  /**
   * Eliminar una receta
   */
  async deleteReceta(recId: number): Promise<ApiResponse<{ message: string }>> {
    const url = this.getApiUrl(`/nutricion/recetas/${recId}`);
    return this.makeRequest<{ message: string }>(url, {
      method: 'DELETE',
    });
  }

  // ========== MÉTODOS PARA INGREDIENTES DE RECETAS ==========

  /**
   * Agregar un ingrediente a una receta
   */
  async addIngredienteToReceta(recId: number, ingredienteData: RecetaIngredienteCreate): Promise<ApiResponse<{ message: string }>> {
    const url = this.getApiUrl(`/nutricion/recetas/${recId}/ingredientes`);
    return this.makeRequest<{ message: string }>(url, {
      method: 'POST',
      body: JSON.stringify(ingredienteData),
    });
  }

  /**
   * Actualizar un ingrediente de una receta
   */
  async updateIngredienteReceta(recId: number, aliId: number, ingredienteData: RecetaIngredienteUpdate): Promise<ApiResponse<{ message: string }>> {
    const url = this.getApiUrl(`/nutricion/recetas/${recId}/ingredientes/${aliId}`);
    return this.makeRequest<{ message: string }>(url, {
      method: 'PUT',
      body: JSON.stringify(ingredienteData),
    });
  }

  /**
   * Eliminar un ingrediente de una receta
   */
  async deleteIngredienteFromReceta(recId: number, aliId: number): Promise<ApiResponse<{ message: string }>> {
    const url = this.getApiUrl(`/nutricion/recetas/${recId}/ingredientes/${aliId}`);
    return this.makeRequest<{ message: string }>(url, {
      method: 'DELETE',
    });
  }

  /**
   * Agregar tipo de comida a una receta
   */
  async addTipoComidaToReceta(recId: number, tipoComida: string): Promise<ApiResponse<{ message: string }>> {
    const url = this.getApiUrl(`/nutricion/recetas/${recId}/tipos-comida`);
    return this.makeRequest<{ message: string }>(url, {
      method: 'POST',
      body: JSON.stringify({ rec_id: recId, rc_comida: tipoComida }),
    });
  }

  /**
   * Eliminar tipo de comida de una receta
   */
  async deleteTipoComidaFromReceta(recId: number, tipoComida: string): Promise<ApiResponse<{ message: string }>> {
    const url = this.getApiUrl(`/nutricion/recetas/${recId}/tipos-comida/${tipoComida}`);
    return this.makeRequest<{ message: string }>(url, {
      method: 'DELETE',
    });
  }

  // ========== MÉTODOS PARA NUTRIENTES ==========

  // ========== MÉTODOS PARA NUTRIENTES DE ALIMENTOS ==========

  /**
   * Agregar nutriente a un alimento
   */
  async addNutrienteToAlimento(aliId: number, nutrienteData: { ali_id: number; nutri_id: number; an_cantidad_100: number; an_fuente?: string }): Promise<ApiResponse<{ message: string }>> {
    const url = this.getApiUrl(`/nutricion/alimentos/${aliId}/nutrientes`);
    return this.makeRequest<{ message: string }>(url, {
      method: 'POST',
      body: JSON.stringify(nutrienteData),
    });
  }

  /**
   * Eliminar nutriente de un alimento
   */
  async deleteNutrienteFromAlimento(aliId: number, nutriId: number): Promise<ApiResponse<{ message: string }>> {
    const url = this.getApiUrl(`/nutricion/alimentos/${aliId}/nutrientes/${nutriId}`);
    return this.makeRequest<{ message: string }>(url, {
      method: 'DELETE',
    });
  }

  // ========== MÉTODOS PARA NUTRIENTES ==========

  /**
   * Obtener lista de nutrientes
   */
  async getNutrientes(limit: number = 100): Promise<ApiResponse<NutrienteResponse[]>> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());

    const url = this.getApiUrl(`/nutricion/nutrientes?${params.toString()}`);
    return this.makeRequest<NutrienteResponse[]>(url);
  }

  /**
   * Buscar recetas (método de búsqueda avanzada)
   */
  async searchRecetas(query?: string, tipoComida?: string): Promise<ApiResponse<RecetaResponse[]>> {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (tipoComida) params.append('tipo_comida', tipoComida);

    const url = this.getApiUrl(`/planes-comidas/recetas/buscar?${params.toString()}`);
    return this.makeRequest<RecetaResponse[]>(url);
  }
}

export const alimentosRecetasApi = new AlimentosRecetasApiService();
