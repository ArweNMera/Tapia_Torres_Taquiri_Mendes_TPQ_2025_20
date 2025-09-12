import { UserLogin, UserRegister, Token, ApiResponse, RolInsert, RolResponse } from '../types/api';

class ApiService {
  private baseURL: string;
  private apiVersion: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    this.apiVersion = import.meta.env.VITE_API_VERSION || 'v1';
  }

  private getApiUrl(endpoint: string): string {
    return `${this.baseURL}/api/${this.apiVersion}${endpoint}`;
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

  // Roles
  async createRole(roleData: RolInsert): Promise<ApiResponse<RolResponse>> {
    return this.makeRequest<RolResponse>(
      this.getApiUrl('/usuarios/roles'),
      {
        method: 'POST',
        body: JSON.stringify(roleData),
      }
    );
  }

  // Métodos utilitarios para el token
  setToken(token: string): void {
    localStorage.setItem(import.meta.env.VITE_TOKEN_KEY || 'auth_token', token);
  }

  getToken(): string | null {
    return localStorage.getItem(import.meta.env.VITE_TOKEN_KEY || 'auth_token');
  }

  removeToken(): void {
    localStorage.removeItem(import.meta.env.VITE_TOKEN_KEY || 'auth_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export const apiService = new ApiService();
