import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthUser, UserLogin, UserRegister } from '../types/api';
import { apiService } from '../services/api';

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  login: (userData: UserLogin) => Promise<{ success: boolean; error?: string }>;
  register: (userData: UserRegister) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Verificar si hay un token guardado al cargar la aplicación
  useEffect(() => {
    const token = apiService.getToken();
    if (token) {
      // TODO: Aquí podrías hacer una llamada al backend para verificar el token
      // y obtener los datos del usuario. Por ahora, asumimos que el token es válido.
      try {
        // Decodificar el token JWT para obtener información básica del usuario
        const payload = JSON.parse(atob(token.split('.')[1]));
        // Este es un placeholder - en una aplicación real deberías hacer una llamada
        // al backend para obtener los datos completos del usuario
        setUser({
          usr_id: 0,
          usr_usuario: payload.sub || '',
          usr_correo: '',
          usr_nombre: '',
          usr_apellido: '',
          rol_id: 0,
          token: token
        });
      } catch (error) {
        console.error('Error decoding token:', error);
        apiService.removeToken();
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (userData: UserLogin): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    try {
      const response = await apiService.login(userData);
      
      if (response.success && response.data) {
        const token = response.data.access_token;
        apiService.setToken(token);
        
        // Decodificar el token para obtener información del usuario
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          setUser({
            usr_id: 0, // Se debería obtener del backend
            usr_usuario: payload.sub || userData.usuario,
            usr_correo: '',
            usr_nombre: '',
            usr_apellido: '',
            rol_id: 0,
            token: token
          });
        } catch (error) {
          console.error('Error decoding token:', error);
        }
        
        return { success: true };
      } else {
        return { success: false, error: response.error || 'Error en el login' };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Error desconocido' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: UserRegister): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    try {
      const response = await apiService.register(userData);
      
      if (response.success && response.data) {
        const token = response.data.access_token;
        apiService.setToken(token);
        
        // Crear el usuario con los datos del registro
        setUser({
          usr_id: 0, // Se obtendría del response en una implementación completa
          usr_usuario: userData.usuario,
          usr_correo: userData.correo,
          usr_nombre: userData.nombres,
          usr_apellido: userData.apellidos,
          rol_id: 0, // Se obtendría del backend
          token: token
        });
        
        return { success: true };
      } else {
        return { success: false, error: response.error || 'Error en el registro' };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Error desconocido' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Intentar hacer logout en el backend
      await apiService.logout();
    } catch (error) {
      console.error('Error en logout del backend:', error);
      // Continuar con el logout local incluso si falla el backend
    } finally {
      // Siempre limpiar el estado local
      apiService.removeToken();
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
