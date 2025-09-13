import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { AuthUser, UserLogin, UserRegister, UserResponse } from '../types/api';
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

  // Verificar token y obtener el perfil real del usuario al cargar
  useEffect(() => {
    const bootstrap = async () => {
      const token = apiService.getToken();
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const me = await apiService.getProfile();
        if (me.success && me.data) {
          const u = me.data as unknown as UserResponse;
          setUser({
            usr_id: u.usr_id,
            usr_usuario: u.usr_usuario,
            usr_correo: u.usr_correo,
            usr_nombre: u.usr_nombre,
            usr_apellido: u.usr_apellido,
            rol_id: u.rol_id,
            avatar_url: u.avatar_url,
            token,
          });
        } else {
          // Fallback: decodificar JWT para al menos tener usuario
          const payload = JSON.parse(atob(token.split('.')[1]));
          setUser({
            usr_id: 0,
            usr_usuario: payload.sub || '',
            usr_correo: '',
            usr_nombre: '',
            usr_apellido: '',
            rol_id: 0,
            token,
          });
        }
      } catch (error) {
        console.error('Error cargando perfil:', error);
        apiService.removeToken();
      } finally {
        setIsLoading(false);
      }
    };
    bootstrap();
  }, []);

  const login = async (userData: UserLogin): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    try {
      const response = await apiService.login(userData);
      
      if (response.success && response.data) {
        const token = response.data.access_token;
        apiService.setToken(token);
        
        // Obtener el perfil real inmediatamente después del login
        const me = await apiService.getProfile();
        if (me.success && me.data) {
          const u = me.data as unknown as UserResponse;
          setUser({
            usr_id: u.usr_id,
            usr_usuario: u.usr_usuario || userData.usuario,
            usr_correo: u.usr_correo,
            usr_nombre: u.usr_nombre,
            usr_apellido: u.usr_apellido,
            rol_id: u.rol_id,
            avatar_url: u.avatar_url,
            token,
          });
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
