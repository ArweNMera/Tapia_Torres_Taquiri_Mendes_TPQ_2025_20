import { useState } from 'react';
import { Eye, EyeOff, User, ArrowLeft } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Separator } from '../ui/separator';
import { Checkbox } from '../ui/checkbox';
import { motion } from 'motion/react';

interface RegisterScreenProps {
  onRegister: () => void;
  onBackToLogin: () => void;
}

export function RegisterScreen({ onRegister, onBackToLogin }: RegisterScreenProps) {
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
  const [acceptTerms, setAcceptTerms] = useState(false);

  const handleInputChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [field]: e.target.value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert('Las contraseñas no coinciden');
      return;
    }
    if (!acceptTerms) {
      alert('Debes aceptar los términos y condiciones');
      return;
    }
    onRegister();
  };

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
            <div className="mb-8">
              <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center mb-4">
                <span className="text-white font-bold text-lg">NF</span>
              </div>
              <h1 className="text-3xl font-bold text-foreground mb-2">Crear Cuenta</h1>
              <p className="text-muted-foreground">
                Únete a NutriFamily y comienza tu viaje hacia una alimentación más saludable
              </p>
            </div>

            {/* Register Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Nombres
                  </label>
                  <Input
                    type="text"
                    value={formData.firstName}
                    onChange={handleInputChange('firstName')}
                    placeholder="Tus nombres"
                    className="w-full h-12 bg-input-background border-border"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Apellidos
                  </label>
                  <Input
                    type="text"
                    value={formData.lastName}
                    onChange={handleInputChange('lastName')}
                    placeholder="Tus apellidos"
                    className="w-full h-12 bg-input-background border-border"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Usuario
                </label>
                <Input
                  type="text"
                  value={formData.username}
                  onChange={handleInputChange('username')}
                  placeholder="Elige un nombre de usuario"
                  className="w-full h-12 bg-input-background border-border"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Email
                </label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                  placeholder="tu@email.com"
                  className="w-full h-12 bg-input-background border-border"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Contraseña
                </label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange('password')}
                    placeholder="Crea una contraseña segura"
                    className="w-full h-12 bg-input-background border-border pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-4 flex items-center text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Confirmar Contraseña
                </label>
                <div className="relative">
                  <Input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={handleInputChange('confirmPassword')}
                    placeholder="Confirma tu contraseña"
                    className="w-full h-12 bg-input-background border-border pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-4 flex items-center text-muted-foreground hover:text-foreground"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Terms checkbox */}
              <div className="flex items-start space-x-3">
                <Checkbox
                  id="terms"
                  checked={acceptTerms}
                  onCheckedChange={(checked) => setAcceptTerms(checked as boolean)}
                  className="mt-1"
                />
                <label htmlFor="terms" className="text-sm text-muted-foreground leading-relaxed">
                  Acepto los{' '}
                  <a href="#" className="text-primary hover:text-primary-dark underline">
                    Términos de Servicio
                  </a>{' '}
                  y la{' '}
                  <a href="#" className="text-primary hover:text-primary-dark underline">
                    Política de Privacidad
                  </a>{' '}
                  de NutriFamily
                </label>
              </div>

              <Button
                type="submit"
                className="w-full h-12 bg-primary hover:bg-primary-dark text-primary-foreground font-semibold"
                disabled={!acceptTerms}
              >
                Crear Cuenta
              </Button>
            </form>

            {/* Separator */}
            <div className="my-6">
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
            <div className="space-y-3">
              <Button
                variant="outline"
                className="w-full h-12 border-border hover:bg-muted"
                type="button"
              >
                <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Continuar con Google
              </Button>

              <Button
                variant="outline"
                className="w-full h-12 border-border hover:bg-muted"
                type="button"
              >
                <svg className="w-5 h-5 mr-3" fill="#1877F2" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
                Continuar con Facebook
              </Button>
            </div>
          </motion.div>
        </div>

        {/* Right Side - Image & Content */}
        <div className="w-1/2 relative overflow-hidden">
          <div
            className="absolute inset-0 bg-gradient-to-br from-primary/20 via-secondary/20 to-accent/20"
            style={{
              backgroundImage: `url('https://images.unsplash.com/photo-1628191079582-f982c2fe327b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFsdGh5JTIwZmFtaWx5JTIwY29va2luZyUyMG51dHJpdGlvbiUyMGNoaWxkcmVufGVufDF8fHx8MTc1NzM2MTYxOXww&ixlib=rb-4.1.0&q=80&w=1080')`,
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
                  <span className="text-sm font-medium">Familia Saludable</span>
                </div>
                <div className="px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full">
                  <span className="text-sm font-medium">Planes Personalizados</span>
                </div>
              </div>

              <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
                <blockquote className="text-xl font-medium mb-4">
                  "Con NutriFamily descubrimos que alimentar sanamente a nuestros hijos puede ser
                  fácil y divertido. Los planes personalizados nos ahorraron tiempo y mejoraron nuestra salud."
                </blockquote>
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="font-semibold">Carlos y Ana Mendoza</div>
                    <div className="text-sm text-white/80">Padres de 3 niños</div>
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
            backgroundImage: `url('https://images.unsplash.com/photo-1628191079582-f982c2fe327b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxoZWFsdGh5JTIwZmFtaWx5JTIwY29va2luZyUyMG51dHJpdGlvbiUyMGNoaWxkcmVufGVufDF8fHx8MTc1NzM2MTYxOXww&ixlib=rb-4.1.0&q=80&w=1080')`,
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
        <div className="flex-1 p-6 bg-background overflow-y-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-foreground mb-2">Crear Cuenta</h2>
              <p className="text-muted-foreground text-sm">
                Únete a la familia NutriFamily
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">Nombres</label>
                  <Input
                    type="text"
                    value={formData.firstName}
                    onChange={handleInputChange('firstName')}
                    placeholder="Nombres"
                    className="w-full h-11 bg-input-background"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">Apellidos</label>
                  <Input
                    type="text"
                    value={formData.lastName}
                    onChange={handleInputChange('lastName')}
                    placeholder="Apellidos"
                    className="w-full h-11 bg-input-background"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Usuario</label>
                <Input
                  type="text"
                  value={formData.username}
                  onChange={handleInputChange('username')}
                  placeholder="Nombre de usuario"
                  className="w-full h-11 bg-input-background"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Email</label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange('email')}
                  placeholder="tu@email.com"
                  className="w-full h-11 bg-input-background"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Contraseña</label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={handleInputChange('password')}
                    placeholder="Contraseña"
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

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Confirmar</label>
                <div className="relative">
                  <Input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.confirmPassword}
                    onChange={handleInputChange('confirmPassword')}
                    placeholder="Confirmar contraseña"
                    className="w-full h-11 bg-input-background pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-3 flex items-center text-muted-foreground"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Checkbox
                  id="terms-mobile"
                  checked={acceptTerms}
                  onCheckedChange={(checked) => setAcceptTerms(checked as boolean)}
                  className="mt-1"
                />
                <label htmlFor="terms-mobile" className="text-xs text-muted-foreground leading-relaxed">
                  Acepto los{' '}
                  <a href="#" className="text-primary underline">Términos</a> y{' '}
                  <a href="#" className="text-primary underline">Política de Privacidad</a>
                </label>
              </div>

              <Button
                type="submit"
                className="w-full h-11 bg-primary hover:bg-primary-dark text-primary-foreground"
                disabled={!acceptTerms}
              >
                Crear Cuenta
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

            <div className="space-y-3 mb-6">
              <Button variant="outline" className="w-full h-11">
                <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                Google
              </Button>

              <Button variant="outline" className="w-full h-11">
                <svg className="w-4 h-4 mr-2" fill="#1877F2" viewBox="0 0 24 24">
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
