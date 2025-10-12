import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { AuthUser, UserLogin, UserRegister, UserResponse } from '../types/api';
import { apiService } from '../services/api';
import { firebaseAuth } from '../lib/firebase';
import {
  GoogleAuthProvider,
  GithubAuthProvider,
  FacebookAuthProvider,
  OAuthProvider,
  OAuthCredential,
  signInWithPopup,
  signOut,
  fetchSignInMethodsForEmail,
  linkWithCredential,
  UserCredential,
} from 'firebase/auth';
import { FirebaseError } from 'firebase/app';

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  login: (userData: UserLogin) => Promise<{ success: boolean; error?: string }>;
  beginGoogleLogin: () => Promise<void>;
  beginGithubLogin: () => Promise<void>;
  beginMicrosoftLogin: () => Promise<void>;
  beginFacebookLogin: () => Promise<void>;
  register: (userData: UserRegister, roleCode: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  socialAuthError: string | null;
  clearSocialAuthError: () => void;
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
  const [socialAuthError, setSocialAuthError] = useState<string | null>(null);

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

  // Verificar token y obtener el perfil real del usuario al cargar
  useEffect(() => {
    const bootstrap = async () => {
      setIsLoading(true);
      await hydrateUserFromProfile();
      setIsLoading(false);
    };
    bootstrap();
  }, [hydrateUserFromProfile]);

  // Escuchar eventos de token expirado/inválido
  useEffect(() => {
    const handleUnauthorized = () => {
      console.warn('Token expirado o inválido. Cerrando sesión...');
      setUser(null);
      apiService.removeToken();
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.removeItem('auth_avatar_hint');
        } catch (e) {
          console.warn('Error limpiando localStorage:', e);
        }
      }
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('auth:unauthorized', handleUnauthorized);
      return () => {
        window.removeEventListener('auth:unauthorized', handleUnauthorized);
      };
    }
  }, []);

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

  const completeFirebaseLogin = useCallback(
    async (credentialResult: UserCredential): Promise<boolean> => {
      const firebaseIdToken = await credentialResult.user.getIdToken(true);

      const response = await apiService.loginWithFirebase(firebaseIdToken);

      if (!response.success || !response.data) {
        const message = response.error || 'No se pudo validar la sesión con el servidor';
        setSocialAuthError(message);
        await signOut(firebaseAuth).catch(() => undefined);
        return false;
      }

      apiService.setToken(response.data.access_token);

      const avatar = credentialResult.user.photoURL;
      if (avatar && typeof window !== 'undefined') {
        try {
          window.localStorage.setItem('auth_avatar_hint', avatar);
        } catch (storageError) {
          console.warn('No se pudo almacenar el avatar recibido de Firebase:', storageError);
        }
        setUser((prev) =>
          prev
            ? { ...prev, avatar_url: avatar, token: response.data?.access_token ?? prev.token }
            : prev
        );
      }

      await hydrateUserFromProfile();
      return true;
    },
    [hydrateUserFromProfile]
  );

  const signInWithProvider = useCallback(
    async (providerName: 'google' | 'github' | 'facebook' | 'microsoft') => {
      setIsLoading(true);
      setSocialAuthError(null);
      try {
        const provider = (() => {
          switch (providerName) {
            case 'google': {
              const googleProvider = new GoogleAuthProvider();
              googleProvider.setCustomParameters({ prompt: 'select_account' });
              return googleProvider;
            }
            case 'github': {
              const githubProvider = new GithubAuthProvider();
              githubProvider.addScope('user:email');
              return githubProvider;
            }
            case 'facebook': {
              const facebookProvider = new FacebookAuthProvider();
              facebookProvider.addScope('email');
              return facebookProvider;
            }
            case 'microsoft': {
              const microsoftProvider = new OAuthProvider('microsoft.com');
              microsoftProvider.setCustomParameters({ prompt: 'select_account' });
              microsoftProvider.addScope('User.Read');
              return microsoftProvider;
            }
            default:
              throw new Error('Proveedor no soportado');
          }
        })();

        const result = await signInWithPopup(firebaseAuth, provider);
        await completeFirebaseLogin(result);
      } catch (error) {
        let message = 'No se pudo iniciar sesión con el proveedor seleccionado';
        if (error instanceof FirebaseError) {
          switch (error.code) {
            case 'auth/popup-closed-by-user':
              message = 'Se cerró la ventana de autenticación antes de completar el proceso.';
              break;
            case 'auth/cancelled-popup-request':
              message = 'Ya hay una ventana de autenticación en curso.';
              break;
            case 'auth/network-request-failed':
              message = 'Hubo problemas de conexión con el servicio de autenticación.';
              break;
            case 'auth/account-exists-with-different-credential': {
              const email = (error.customData?.email as string) || '';
              const pendingCredential: OAuthCredential | null = (() => {
                switch (providerName) {
                  case 'google':
                    return GoogleAuthProvider.credentialFromError(error);
                  case 'github':
                    return GithubAuthProvider.credentialFromError(error);
                  case 'facebook':
                    return FacebookAuthProvider.credentialFromError(error);
                  case 'microsoft':
                    return OAuthProvider.credentialFromError(error);
                  default:
                    return null;
                }
              })();

              if (email && pendingCredential) {
                try {
                  const methods = await fetchSignInMethodsForEmail(firebaseAuth, email);

                  const tryLinkingWithKnownProvider = async (method: string) => {
                    const providerForMethod = (() => {
                      switch (method) {
                        case 'google.com': {
                          const googleProvider = new GoogleAuthProvider();
                          googleProvider.setCustomParameters({ prompt: 'select_account' });
                          return googleProvider;
                        }
                        case 'github.com': {
                          const githubProvider = new GithubAuthProvider();
                          githubProvider.addScope('user:email');
                          return githubProvider;
                        }
                        case 'facebook.com': {
                          const facebookProvider = new FacebookAuthProvider();
                          facebookProvider.addScope('email');
                          return facebookProvider;
                        }
                        case 'microsoft.com': {
                          const microsoftProvider = new OAuthProvider('microsoft.com');
                          microsoftProvider.setCustomParameters({ prompt: 'select_account' });
                          microsoftProvider.addScope('User.Read');
                          return microsoftProvider;
                        }
                        default:
                          return null;
                      }
                    })();

                    if (!providerForMethod) {
                      return false;
                    }

                    const existingUserResult = await signInWithPopup(firebaseAuth, providerForMethod);
                    await linkWithCredential(existingUserResult.user, pendingCredential);

                    const success = await completeFirebaseLogin(existingUserResult);
                    if (success) {
                      setSocialAuthError(null);
                      return true;
                    }
                    return false;
                  };

                  for (const method of methods) {
                    if (await tryLinkingWithKnownProvider(method)) {
                      return;
                    }
                  }
                } catch (linkError) {
                  console.error('No se pudo vincular las credenciales con la cuenta existente:', linkError);
                }
              }

              message =
                'Ya existe una cuenta asociada a este correo. Inicia sesión con el método original y realiza la vinculación desde tu perfil.';
              break;
            }
            default:
              message = error.message;
          }
        } else if (error instanceof Error) {
          message = error.message;
        }
        console.error('Firebase login error:', error);
        setSocialAuthError(message);
      } finally {
        setIsLoading(false);
      }
    },
    [completeFirebaseLogin]
  );

  const beginGoogleLogin = useCallback(() => signInWithProvider('google'), [signInWithProvider]);
  const beginGithubLogin = useCallback(() => signInWithProvider('github'), [signInWithProvider]);
  const beginFacebookLogin = useCallback(() => signInWithProvider('facebook'), [signInWithProvider]);
  const beginMicrosoftLogin = useCallback(() => signInWithProvider('microsoft'), [signInWithProvider]);

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
      await signOut(firebaseAuth).catch(() => undefined);
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

  const clearSocialAuthError = useCallback(() => {
    setSocialAuthError(null);
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    beginGoogleLogin,
    beginGithubLogin,
    beginFacebookLogin,
    beginMicrosoftLogin,
    register,
    logout,
    isAuthenticated: !!user,
    socialAuthError,
    clearSocialAuthError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
