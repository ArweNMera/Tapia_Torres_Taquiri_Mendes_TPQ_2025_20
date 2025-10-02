import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { AuthUser, UserLogin, UserRegister, UserResponse } from '../types/api';
import { apiService } from '../services/api';

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  login: (userData: UserLogin) => Promise<{ success: boolean; error?: string }>;
  beginGoogleLogin: (redirectTo?: string) => void;
  register: (userData: UserRegister, roleCode: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  isAuthenticated: boolean;
  googleAuthError: string | null;
  clearGoogleAuthError: () => void;
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
  const [googleAuthError, setGoogleAuthError] = useState<string | null>(null);

  const hydrateUserFromProfile = useCallback(async (): Promise<UserResponse | null> => {
    const token = apiService.getToken();
    if (!token) {
      setUser(null);
      return null;
    }

    const avatarHint = typeof window === 'undefined'
      ? null
      : window.localStorage.getItem('auth_avatar_hint');

    try {
      const me = await apiService.getProfile();
      if (me.success && me.data) {
        const u = me.data as unknown as UserResponse;
        const resolvedAvatar = u.avatar_url && u.avatar_url.trim().length > 0
          ? u.avatar_url.trim()
          : avatarHint || undefined;

        if (resolvedAvatar && typeof window !== 'undefined') {
          try {
            window.localStorage.setItem('auth_avatar_hint', resolvedAvatar);
          } catch (storageError) {
            console.warn('No se pudo almacenar el avatar en caché:', storageError);
          }
        }

        setUser({
          usr_id: u.usr_id,
          usr_usuario: u.usr_usuario,
          usr_correo: u.usr_correo,
          usr_nombre: u.usr_nombre,
          usr_apellido: u.usr_apellido,
          rol_id: u.rol_id,
          avatar_url: resolvedAvatar,
          token,
        });
        return u;
      }
    } catch (error) {
      console.error('Error cargando perfil:', error);
    }

    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUser({
        usr_id: 0,
        usr_usuario: payload.sub || '',
        usr_correo: '',
        usr_nombre: '',
        usr_apellido: '',
        rol_id: 0,
        avatar_url: avatarHint || undefined,
        token,
      });
    } catch (decodeError) {
      console.error('No se pudo decodificar el token JWT:', decodeError);
      setUser(null);
    }

    return null;
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const url = new URL(window.location.href);
    const tokenFromUrl = url.searchParams.get('google_token');
    const tokenTypeParam = url.searchParams.get('token_type');
    const errorFromUrl = url.searchParams.get('google_error');
    const avatarFromUrl = url.searchParams.get('google_avatar');

    if (errorFromUrl) {
      setGoogleAuthError(errorFromUrl);
    }

    if (tokenFromUrl) {
      apiService.setToken(tokenFromUrl);
    }

    if (avatarFromUrl && typeof window !== 'undefined') {
      try {
        window.localStorage.setItem('auth_avatar_hint', avatarFromUrl);
      } catch (storageError) {
        console.warn('No se pudo almacenar el avatar recibido de Google:', storageError);
      }
      setUser((prev) => (prev ? { ...prev, avatar_url: avatarFromUrl } : prev));
    }

    if (tokenFromUrl || tokenTypeParam || errorFromUrl || avatarFromUrl) {
      url.searchParams.delete('google_token');
      url.searchParams.delete('token_type');
      url.searchParams.delete('google_error');
      url.searchParams.delete('google_avatar');
      const cleanedPath = `${url.pathname}${url.search}${url.hash}`;
      window.history.replaceState({}, document.title, cleanedPath);
    }

    if (tokenFromUrl) {
      hydrateUserFromProfile();
    }
  }, [hydrateUserFromProfile]);

  // Verificar token y obtener el perfil real del usuario al cargar
  useEffect(() => {
    const bootstrap = async () => {
      setIsLoading(true);
      await hydrateUserFromProfile();
      setIsLoading(false);
    };
    bootstrap();
  }, [hydrateUserFromProfile]);

  const login = async (userData: UserLogin): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    try {
      const response = await apiService.login(userData);

      if (response.success && response.data) {
        apiService.setToken(response.data.access_token);
        await hydrateUserFromProfile();
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

  const beginGoogleLogin = (redirectOverride?: string) => {
    setGoogleAuthError(null);
    const target = redirectOverride 
      || import.meta.env.VITE_GOOGLE_POST_LOGIN_REDIRECT 
      || window.location.origin;
    const authorizationUrl = apiService.getGoogleAuthStartUrl(target);
    window.location.href = authorizationUrl;
  };

  const register = async (userData: UserRegister, roleCode: string): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);
    try {
      const registerPayload: UserRegister = {
        ...userData,
        rol_nombre: roleCode === 'TUTOR' ? userData.rol_nombre : 'TUTOR',
      };

      const response = await apiService.register(registerPayload);

      if (response.success && response.data) {
        apiService.setToken(response.data.access_token);

        let profile: UserResponse | null = null;
        const profileResponse = await apiService.getProfile();
        if (profileResponse.success && profileResponse.data) {
          profile = profileResponse.data;

          if (roleCode && roleCode !== 'TUTOR' && profile.usr_id) {
            try {
              const roleChange = await apiService.changeUserRole(profile.usr_id, { rol_codigo: roleCode });
              if (roleChange.success) {
                const refreshedProfile = await apiService.getProfile();
                if (refreshedProfile.success && refreshedProfile.data) {
                  profile = refreshedProfile.data;
                }
              }
            } catch (error) {
              console.error('No se pudo asignar el rol seleccionado:', error);
            }
          }
        }

        if (profile) {
          setUser({
            usr_id: profile.usr_id,
            usr_usuario: profile.usr_usuario || userData.usuario,
            usr_correo: profile.usr_correo,
            usr_nombre: profile.usr_nombre,
            usr_apellido: profile.usr_apellido,
            rol_id: profile.rol_id,
            avatar_url: profile.avatar_url,
            token: apiService.getToken() || response.data.access_token,
          });
        } else {
          await hydrateUserFromProfile();
        }

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
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.removeItem('auth_avatar_hint');
        } catch (storageError) {
          console.warn('No se pudo limpiar el avatar en caché:', storageError);
        }
      }
      setUser(null);
    }
  };

  const clearGoogleAuthError = useCallback(() => {
    setGoogleAuthError(null);
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    beginGoogleLogin,
    register,
    logout,
    isAuthenticated: !!user,
    googleAuthError,
    clearGoogleAuthError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
