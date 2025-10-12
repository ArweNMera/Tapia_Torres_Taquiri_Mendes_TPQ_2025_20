import React, { useEffect, useState } from 'react';
import { Eye, EyeOff, User, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Separator } from '../ui/separator';
import { motion } from 'motion/react';
import { useAuth } from '../../contexts/AuthContext';

interface LoginScreenProps {
  onLogin: () => void;
  onSignUp: () => void;
}

export function LoginScreen({ onLogin, onSignUp }: LoginScreenProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const {
    login,
    beginGoogleLogin,
    beginGithubLogin,
    beginFacebookLogin,
    beginMicrosoftLogin,
    isLoading,
    socialAuthError,
    clearSocialAuthError
  } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username.trim() || !password.trim()) {
      setError('Por favor, completa todos los campos');
      return;
    }

    const result = await login({
      usuario: username.trim(),
      contrasena: password
    });

    if (result.success) {
      onLogin();
    } else {
      setError(result.error || 'Error al iniciar sesión');
    }
  };

  const handleGoogleLogin = () => {
    setError('');
    beginGoogleLogin();
  };

  const handleGithubLogin = () => {
    setError('');
    beginGithubLogin();
  };

  const handleFacebookLogin = () => {
    setError('');
    beginFacebookLogin();
  };

  const handleMicrosoftLogin = () => {
    setError('');
    beginMicrosoftLogin();
  };
  useEffect(() => {
    if (socialAuthError) {
      setError(socialAuthError);
      clearSocialAuthError();
    }
  }, [socialAuthError, clearSocialAuthError]);

  const socialProviders = [
    {
      label: 'Google',
      onClick: handleGoogleLogin,
      icon: (
        <svg className="w-4 h-4" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
      ),
    },
    {
      label: 'GitHub',
      onClick: handleGithubLogin,
      icon: (
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.38 7.86 10.9.58.11.79-.26.79-.57 0-.28-.01-1.02-.02-2-3.2.69-3.88-1.54-3.88-1.54-.53-1.34-1.29-1.69-1.29-1.69-1.06-.73.08-.72.08-.72 1.17.08 1.78 1.2 1.78 1.2 1.04 1.78 2.73 1.26 3.4.96.11-.75.41-1.26.74-1.55-2.55-.29-5.23-1.27-5.23-5.63 0-1.24.44-2.26 1.16-3.05-.12-.29-.5-1.45.11-3.02 0 0 .96-.31 3.15 1.16a10.9 10.9 0 0 1 2.87-.39c.97 0 1.95.13 2.87.39 2.19-1.47 3.14-1.16 3.14-1.16.61 1.57.24 2.73.12 3.02.72.79 1.15 1.81 1.15 3.05 0 4.37-2.69 5.33-5.25 5.61.42.36.8 1.08.8 2.17 0 1.57-.01 2.83-.01 3.22 0 .31.21.68.8.57A10.51 10.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z"/>
        </svg>
      ),
    },
    {
      label: 'Facebook',
      onClick: handleFacebookLogin,
      icon: (
        <svg className="w-4 h-4" fill="#1877F2" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
      ),
    },
    {
      label: 'Microsoft',
      onClick: handleMicrosoftLogin,
      icon: (
        <svg className="w-4 h-4" viewBox="0 0 24 24" aria-hidden="true">
          <rect x="2" y="2" width="9.5" height="9.5" fill="#F35325" />
          <rect x="12.5" y="2" width="9.5" height="9.5" fill="#81BC06" />
          <rect x="2" y="12.5" width="9.5" height="9.5" fill="#05A6F0" />
          <rect x="12.5" y="12.5" width="9.5" height="9.5" fill="#FFBA08" />
        </svg>
      ),
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary/10 via-accent/5 to-primary/10 flex">
      {/* Desktop Layout */}
      <div className="hidden lg:flex w-full">
        {/* Left Side - Form */}
        <div className="w-1/2 flex items-center justify-center p-12">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="w-full max-w-md"
          >
            {/* Logo */}
            <div className="mb-8">
              <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center mb-4">
                <span className="text-white font-bold text-lg">NF</span>
              </div>
              <h1 className="text-3xl font-bold text-foreground mb-2">Iniciar Sesión</h1>
              <p className="text-muted-foreground">
                Accede a tu plan nutricional personalizado para toda la familia
              </p>
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <p className="text-sm text-destructive">{error}</p>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Usuario
                </label>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Ingresa tu usuario"
                  className="w-full h-12 bg-input-background border-border"
                  required
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Contraseña
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Ingresa tu contraseña"
                    className="w-full h-12 bg-input-background border-border pr-12"
                    required
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-4 flex items-center text-muted-foreground hover:text-foreground"
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full h-12 bg-primary hover:bg-primary-dark text-primary-foreground font-semibold"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Iniciando sesión...
                  </>
                ) : (
                  'Iniciar Sesión'
                )}
              </Button>
            </form>

            {/* Separator */}
            <div className="my-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <Separator className="w-full" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-background text-muted-foreground">O</span>
                </div>
              </div>
            </div>

            {/* Social Login */}
            <div className="grid grid-cols-2 gap-3">
              {socialProviders.map((provider) => (
                <Button
                  key={provider.label}
                  variant="outline"
                  className="flex h-12 items-center justify-center space-x-2 border-border hover:bg-muted"
                  type="button"
                  onClick={provider.onClick}
                  disabled={isLoading}
                >
                  {provider.icon}
                  <span>{provider.label}</span>
                </Button>
              ))}
            </div>
            <p className="text-xs text-center text-muted-foreground">
              Al continuar aceptas nuestros{' '}
              <a href="/terms" target="_blank" rel="noreferrer" className="text-primary underline">
                Términos de Servicio
              </a>{' '}
              y la{' '}
              <a href="/privacy" target="_blank" rel="noreferrer" className="text-primary underline">
                Política de Privacidad
              </a>
              .
            </p>

            {/* Sign up link */}
            <div className="mt-8 text-center">
              <p className="text-muted-foreground">
                ¿No tienes una cuenta?{' '}
                <button
                  onClick={onSignUp}
                  className="font-semibold text-primary hover:text-primary-dark transition-colors"
                >
                  Crear cuenta
                </button>
              </p>
            </div>
          </motion.div>
        </div>

        {/* Right Side - Image & Content */}
        <div className="w-1/2 relative overflow-hidden">
          <div
            className="absolute inset-0 bg-gradient-to-br from-primary/20 via-secondary/20 to-accent/20"
            style={{
              backgroundImage: `url('https://images.unsplash.com/photo-1601049455794-76a4d978639d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmcmVzaCUyMGZydWl0cyUyMHZlZ2V0YWJsZXMlMjBjb2xvcmZ1bCUyMGhlYWx0aHklMjBudXRyaXRpb258ZW58MXx8fHwxNzU3MzYyNDg1fDA&ixlib=rb-4.1.0&q=80&w=1080')`,
              backgroundSize: 'cover',
              backgroundPosition: 'center'
            }}
          >
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
          </div>

          {/* Content Overlay */}
          <div className="relative h-full flex flex-col justify-end p-12 text-white">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="mb-8"
            >
              <div className="flex items-center space-x-4 mb-6">
                <div className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full">
                  <span className="text-sm font-medium">🥗 Frutas & Vegetales</span>
                </div>
                <div className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full">
                  <span className="text-sm font-medium">🌱 Nutrición Natural</span>
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <blockquote className="text-xl font-medium mb-4">
                  "NutriFamily me ayudó a incluir más frutas y vegetales en la dieta de mis hijos.
                  Ahora comen colorido y saludable todos los días con recetas que realmente les gustan."
                </blockquote>
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-semibold">María Rodríguez</div>
                    <div className="text-sm text-white/80">Madre de familia</div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Mobile Layout */}
      <div className="lg:hidden w-full flex flex-col">
        {/* Top Image Section */}
        <div
          className="h-1/3 relative"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1601049455794-76a4d978639d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmcmVzaCUyMGZydWl0cyUyMHZlZ2V0YWJsZXMlMjBjb2xvcmZ1bCUyMGhlYWx0aHklMjBudXRyaXRpb258ZW58MXx8fHwxNzU3MzYyNDg1fDA&ixlib=rb-4.1.0&q=80&w=1080')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-4 left-4 text-white">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center mb-2">
              <span className="text-white font-bold">NF</span>
            </div>
            <h1 className="text-xl font-bold">NutriFamily</h1>
          </div>
        </div>

        {/* Bottom Form Section */}
        <div className="flex-1 p-6 bg-background">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-foreground mb-2">Iniciar Sesión</h2>
              <p className="text-muted-foreground text-sm">
                Accede a tu plan nutricional personalizado
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Usuario</label>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Ingresa tu usuario"
                  className="w-full h-11 bg-input-background"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Contraseña</label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Ingresa tu contraseña"
                    className="w-full h-11 bg-input-background pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-3 flex items-center text-muted-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                className="w-full h-11 bg-primary hover:bg-primary-dark text-primary-foreground"
              >
                Iniciar Sesión
              </Button>
            </form>

            <div className="my-4">
              <div className="relative">
                <Separator />
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="px-2 bg-background text-muted-foreground text-sm">O</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2">
              {socialProviders.map((provider) => (
                <Button
                  key={provider.label}
                  variant="outline"
                  className="h-11 justify-center space-x-2"
                  type="button"
                  onClick={provider.onClick}
                  disabled={isLoading}
                >
                  <span className="flex items-center space-x-2">
                    {provider.icon}
                    <span>{provider.label}</span>
                  </span>
                </Button>
              ))}
            </div>
            <p className="mt-4 text-center text-xs text-muted-foreground">
              Al continuar aceptas nuestros{' '}
              <a href="/terms" target="_blank" rel="noreferrer" className="text-primary underline">
                Términos de Servicio
              </a>{' '}
              y la{' '}
              <a href="/privacy" target="_blank" rel="noreferrer" className="text-primary underline">
                Política de Privacidad
              </a>
              .
            </p>

            <div className="mt-6 text-center">
              <p className="text-muted-foreground text-sm">
                ¿No tienes una cuenta?{' '}
                <button
                  onClick={onSignUp}
                  className="font-semibold text-primary hover:text-primary-dark"
                >
                  Crear cuenta
                </button>
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
