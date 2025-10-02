import React, { useEffect, useState } from 'react';
import { Eye, EyeOff, ArrowLeft, Loader2, User } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Checkbox } from '../ui/checkbox';
import { Separator } from '../ui/separator';
import { motion } from 'motion/react';
import { useAuth } from '../../contexts/AuthContext';

interface RegisterScreenProps {
  onRegister: () => void;
  onBackToLogin: () => void;
}

export function RegisterScreen({ onRegister, onBackToLogin }: RegisterScreenProps) {
  const ROLE_OPTIONS = [
    { code: 'TUTOR', label: 'Tutor', registerName: 'Tutor', description: 'Responsable de menores y acompañamiento diario.' },
    { code: 'USR', label: 'Usuario', registerName: 'Usuario', description: 'Acceso personal sin responsabilidades adicionales.' },
    { code: 'PADRES', label: 'Padres', registerName: 'PADRES', description: 'Padres o madres que registran a sus hijos.' },
  ] as const;

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [selectedRole, setSelectedRole] = useState<typeof ROLE_OPTIONS[number]['code']>('PADRES');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState('');
  
  const { register: registerUser, beginGoogleLogin, isLoading, googleAuthError, clearGoogleAuthError } = useAuth();

  const handleInputChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validaciones
    if (!formData.firstName.trim() || !formData.lastName.trim() || 
        !formData.username.trim() || !formData.email.trim() || 
        !formData.password.trim()) {
      setError('Por favor, completa todos los campos');
      return;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }
    
    if (formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }
    
    if (!acceptTerms) {
      setError('Debes aceptar los términos y condiciones');
      return;
    }

    const roleDefinition = ROLE_OPTIONS.find(option => option.code === selectedRole) || ROLE_OPTIONS[0];

    const result = await registerUser({
      nombres: formData.firstName.trim(),
      apellidos: formData.lastName.trim(),
      usuario: formData.username.trim(),
      correo: formData.email.trim(),
      contrasena: formData.password,
      rol_nombre: roleDefinition.registerName
    }, selectedRole);

    if (result.success) {
      onRegister();
    } else {
      setError(result.error || 'Error al crear la cuenta');
    }
  };

  const handleGoogleLogin = () => {
    setError('');
    beginGoogleLogin(window.location.origin);
  };

  useEffect(() => {
    if (googleAuthError) {
      setError(googleAuthError);
      clearGoogleAuthError();
    }
  }, [googleAuthError, clearGoogleAuthError]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary/10 via-accent/5 to-primary/10 flex">
      {/* Desktop Layout */}
      <div className="hidden lg:flex w-full">
        {/* Left Side - Form */}
        <div className="w-1/2 flex items-center justify-center p-8">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="w-full max-w-md"
          >
            {/* Back Button */}
            <Button
              variant="ghost"
              onClick={onBackToLogin}
              className="mb-6 p-0 h-auto text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Volver al inicio de sesión
            </Button>

            {/* Logo */}
            <div className="mb-6">
              <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center mb-3">
                <span className="text-white font-bold text-lg">NF</span>
              </div>
              <h1 className="text-2xl font-bold text-foreground mb-2">Crear Cuenta</h1>
              <p className="text-muted-foreground text-sm">
                Únete a NutriFamily y comienza tu viaje hacia una alimentación más saludable
              </p>
            </div>

            {/* Register Form */}
            <form onSubmit={handleSubmit} className="space-y-3">
              {error && (
                <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <p className="text-sm text-destructive">{error}</p>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">
                    Nombres
                  </label>
                  <Input
                    type="text"
                    value={formData.firstName}
                    onChange={handleInputChange('firstName')}
                    placeholder="Tus nombres"
                    className="w-full h-10 bg-input-background border-border"
                    required
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">
                    Apellidos
                  </label>
                  <Input
                    type="text"
                    value={formData.lastName}
                    onChange={handleInputChange('lastName')}
                    placeholder="Tus apellidos"
                    className="w-full h-10 bg-input-background border-border"
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Usuario
                </label>
                <Input
                  type="text"
                  value={formData.username}
                  onChange={handleInputChange('username')}
                  placeholder="Elige un nombre de usuario"
                  className="w-full h-10 bg-input-background border-border"
                  required
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Email
                </label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                  placeholder="tu@email.com"
                  className="w-full h-10 bg-input-background border-border"
                  required
                  disabled={isLoading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Selecciona tu rol en la plataforma
                </label>
                <p className="text-xs text-muted-foreground mb-2">
                  Define cómo quieres utilizar App Saludable. Puedes actualizarlo luego en tu perfil.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {ROLE_OPTIONS.map(option => {
                    const isActive = selectedRole === option.code;
                    return (
                      <button
                        key={option.code}
                        type="button"
                        onClick={() => setSelectedRole(option.code)}
                        className={`text-left border rounded-lg p-3 transition-all ${
                          isActive
                            ? 'border-primary bg-primary/10 shadow-sm'
                            : 'border-border hover:border-primary/50 bg-background'
                        }`}
                        disabled={isLoading}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-sm text-foreground">{option.label}</span>
                          {isActive && <span className="text-xs text-primary font-semibold">Seleccionado</span>}
                        </div>
                        <p className="text-xs text-muted-foreground leading-snug">{option.description}</p>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Contraseña
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange('password')}
                    placeholder="Crea una contraseña segura (mín. 6 caracteres)"
                    className="w-full h-10 bg-input-background border-border pr-10"
                    required
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-3 flex items-center text-muted-foreground hover:text-foreground"
                    disabled={isLoading}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Confirmar Contraseña
                </label>
                <div className="relative">
                  <Input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={handleInputChange('confirmPassword')}
                    placeholder="Confirma tu contraseña"
                    className="w-full h-10 bg-input-background border-border pr-10"
                    required
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-3 flex items-center text-muted-foreground hover:text-foreground"
                    disabled={isLoading}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Terms checkbox */}
              <div className="flex items-start space-x-2 pt-1">
                <Checkbox
                  id="terms"
                  checked={acceptTerms}
                  onCheckedChange={(checked) => setAcceptTerms(checked as boolean)}
                  className="mt-0.5"
                  disabled={isLoading}
                />
                <label htmlFor="terms" className="text-xs text-muted-foreground leading-tight">
                  Acepto los{' '}
                  <a href="#" className="text-primary hover:text-primary-dark underline">
                    Términos de Servicio
                  </a>{' '}
                  y la{' '}
                  <a href="#" className="text-primary hover:text-primary-dark underline">
                    Política de Privacidad
                  </a>
                </label>
              </div>

              <Button 
                type="submit" 
                className="w-full h-10 bg-primary hover:bg-primary-dark text-primary-foreground font-semibold mt-4"
                disabled={!acceptTerms || isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creando cuenta...
                  </>
                ) : (
                  'Crear Cuenta'
                )}
              </Button>
            </form>

            {/* Separator */}
            <div className="my-4">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <Separator className="w-full" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-background text-muted-foreground">O regístrate con</span>
                </div>
              </div>
            </div>

            {/* Social Register */}
            <div className="grid grid-cols-2 gap-3">
              <Button 
                variant="outline" 
                className="w-full h-10 border-border hover:bg-muted"
                type="button"
                onClick={handleGoogleLogin}
                disabled={isLoading}
              >
                <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Google
              </Button>
              
              <Button 
                variant="outline" 
                className="w-full h-10 border-border hover:bg-muted"
                type="button"
              >
                <svg className="w-4 h-4 mr-2" fill="#1877F2" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Facebook
              </Button>
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
          <div className="relative h-full flex flex-col justify-end p-8 text-white">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="mb-6"
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full">
                  <span className="text-sm font-medium">🍎 Alimentación Colorida</span>
                </div>
                <div className="px-3 py-1 bg-white/20 backdrop-blur-sm rounded-full">
                  <span className="text-sm font-medium">🥕 Nutrición Completa</span>
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-5 border border-white/20">
                <blockquote className="text-lg font-medium mb-3">
                  "Gracias a NutriFamily, nuestros hijos ahora disfrutan comiendo frutas y vegetales frescos. 
                  Las recetas coloridas los motivaron a probar nuevos sabores y texturas saludables."
                </blockquote>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4" />
                  </div>
                  <div>
                    <div className="font-semibold text-sm">Carlos y Ana Mendoza</div>
                    <div className="text-xs text-white/80">Padres de 3 niños</div>
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
          className="h-1/4 relative"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1601049455794-76a4d978639d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmcmVzaCUyMGZydWl0cyUyMHZlZ2V0YWJsZXMlMjBjb2xvcmZ1bCUyMGhlYWx0aHklMjBudXRyaXRpb258ZW58MXx8fHwxNzU3MzYyNDg1fDA&ixlib=rb-4.1.0&q=80&w=1080')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute top-4 left-4">
            <Button
              variant="ghost"
              onClick={onBackToLogin}
              className="p-2 text-white hover:bg-white/20"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
          </div>
          <div className="absolute bottom-4 left-4 text-white">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center mb-2">
              <span className="text-white font-bold">NF</span>
            </div>
            <h1 className="text-xl font-bold">NutriFamily</h1>
          </div>
        </div>

        {/* Bottom Form Section */}
        <div className="flex-1 p-4 bg-background overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-4">
              <h2 className="text-xl font-bold text-foreground mb-1">Crear Cuenta</h2>
              <p className="text-muted-foreground text-sm">
                Únete a la familia NutriFamily
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Nombres</label>
                  <Input
                    type="text"
                    value={formData.firstName}
                    onChange={handleInputChange('firstName')}
                    placeholder="Nombres"
                    className="w-full h-9 bg-input-background text-sm"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Apellidos</label>
                  <Input
                    type="text"
                    value={formData.lastName}
                    onChange={handleInputChange('lastName')}
                    placeholder="Apellidos"
                    className="w-full h-9 bg-input-background text-sm"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">Usuario</label>
                <Input
                  type="text"
                  value={formData.username}
                  onChange={handleInputChange('username')}
                  placeholder="Nombre de usuario"
                  className="w-full h-9 bg-input-background text-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">Email</label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                  placeholder="tu@email.com"
                  className="w-full h-9 bg-input-background text-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">Contraseña</label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange('password')}
                    placeholder="Contraseña"
                    className="w-full h-9 bg-input-background pr-10 text-sm"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-2 flex items-center text-muted-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-1">Confirmar</label>
                <div className="relative">
                  <Input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={handleInputChange('confirmPassword')}
                    placeholder="Confirmar contraseña"
                    className="w-full h-9 bg-input-background pr-10 text-sm"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-2 flex items-center text-muted-foreground"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-start space-x-2 pt-1">
                <Checkbox
                  id="terms-mobile"
                  checked={acceptTerms}
                  onCheckedChange={(checked) => setAcceptTerms(checked as boolean)}
                  className="mt-0.5"
                />
                <label htmlFor="terms-mobile" className="text-xs text-muted-foreground leading-tight">
                  Acepto los{' '}
                  <a href="#" className="text-primary underline">Términos</a> y{' '}
                  <a href="#" className="text-primary underline">Política de Privacidad</a>
                </label>
              </div>

              <Button 
                type="submit" 
                className="w-full h-9 bg-primary hover:bg-primary-dark text-primary-foreground text-sm mt-3"
                disabled={!acceptTerms}
              >
                Crear Cuenta
              </Button>
            </form>

            <div className="my-3">
              <div className="relative">
                <Separator />
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="px-2 bg-background text-muted-foreground text-xs">O</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 mb-4">
              <Button 
                variant="outline" 
                className="w-full h-9 text-xs"
                onClick={handleGoogleLogin}
                disabled={isLoading}
              >
                <svg className="w-3 h-3 mr-1" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Google
              </Button>
              
              <Button variant="outline" className="w-full h-9 text-xs">
                <svg className="w-3 h-3 mr-1" fill="#1877F2" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Facebook  
              </Button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
