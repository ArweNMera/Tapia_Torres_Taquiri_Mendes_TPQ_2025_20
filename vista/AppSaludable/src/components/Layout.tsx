import { ReactNode, useState } from 'react';
import { Home, User, BookOpen, BarChart, Settings, Menu, Calendar, Scan, Shield, Users, Trophy, X, LogOut, ChevronDown } from 'lucide-react';
import { Button } from './ui/button';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from './ui/sheet';
import { Badge } from './ui/badge';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from './ui/dropdown-menu';
import { motion, AnimatePresence } from 'motion/react';
import { useAuth } from '../contexts/AuthContext';

interface LayoutProps {
  children: ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export function Layout({ children, activeTab, onTabChange }: LayoutProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const { user, logout } = useAuth();

  const defaultAvatarUrl = 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face&auto=format&q=80';
  const resolvedAvatar = user?.avatar_url && user.avatar_url.trim().length > 0
    ? user.avatar_url.trim()
    : defaultAvatarUrl;
  const avatarKey = user?.avatar_url && user.avatar_url.trim().length > 0
    ? user.avatar_url.trim()
    : 'default-avatar';

  const handleLogout = () => {
    if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
      logout();
    }
  };

  // Generar iniciales del usuario
  const getUserInitials = () => {
    if (!user) return 'U';
    const nombres = user.usr_nombre || user.usr_usuario || '';
    const apellidos = user.usr_apellido || '';
    return `${nombres.charAt(0)}${apellidos.charAt(0)}`.toUpperCase();
  };

  const handleUserMenuClick = (action: string) => {
    setIsUserMenuOpen(false);
    if (action === 'profile') {
      onTabChange('profile');
    } else if (action === 'settings') {
      // Redirigir ajustes a perfil
      onTabChange('profile');
    } else if (action === 'logout') {
      handleLogout();
    }
  };

  const isAdmin = user?.rol_nombre === 'Administrador';

  // Debug: ver el rol del usuario
  console.log('Usuario actual:', user);
  console.log('Rol del usuario:', user?.rol_nombre);
  console.log('Es admin?:', isAdmin);

  const tabs = [
    { id: 'home', icon: Home, label: 'Inicio', category: 'principal' },
    { id: 'meal-plan', icon: Calendar, label: 'Plan de Comidas', category: 'planificacion' },
    { id: 'scan', icon: Scan, label: 'Escanear', category: 'herramientas' },
    { id: 'risk-prediction', icon: Shield, label: 'Análisis de Riesgos', category: 'herramientas' },
    { id: 'progress', icon: BarChart, label: 'Progreso', category: 'seguimiento' },
    { id: 'community', icon: Users, label: 'Comunidad', category: 'social' },
    { id: 'gamification', icon: Trophy, label: 'Logros', category: 'social' },
    { id: 'clinical', icon: BookOpen, label: 'Datos Clínicos', category: 'personal' },
    { id: 'profile', icon: User, label: 'Perfil', category: 'personal' },
    ...(isAdmin ? [{ id: 'admin', icon: Settings, label: '🛡️ Panel Admin', category: 'admin' }] : []),
  ];

  // Orden específico para el sidebar de escritorio: colocar "Datos Clínicos" debajo de Inicio
  const desktopSidebarOrder = [
    'home',
    'clinical',
    'meal-plan',
    'scan',
    'risk-prediction',
    'progress',
    'community',
    'gamification',
    'profile',
    ...(isAdmin ? ['admin'] : []),
  ];

  // Tabs principales para navegación inferior móvil
  const mainMobileTabs = tabs.filter(tab =>
    ['home', 'meal-plan', 'progress', 'profile'].includes(tab.id)
  );

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'principal': return 'Principal';
      case 'planificacion': return 'Planificación';
      case 'herramientas': return 'Herramientas IA';
      case 'seguimiento': return 'Seguimiento';
      case 'social': return 'Social';
      case 'personal': return 'Personal';
      case 'admin': return 'Administración';
      default: return 'Otros';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'principal': return 'bg-primary text-white';
      case 'planificacion': return 'bg-secondary text-white';
      case 'herramientas': return 'bg-accent text-accent-foreground';
      case 'seguimiento': return 'bg-info text-white';
      case 'social': return 'bg-success text-white';
      case 'personal': return 'bg-muted text-muted-foreground';
      case 'admin': return 'bg-red-600 text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  const groupedTabs = tabs.reduce((acc, tab) => {
    if (!acc[tab.category]) {
      acc[tab.category] = [];
    }
    acc[tab.category].push(tab);
    return acc;
  }, {} as Record<string, typeof tabs>);

  const handleMobileMenuItemClick = (tabId: string) => {
    onTabChange(tabId);
    setIsMobileMenuOpen(false);
  };

  return (
    <div className="h-screen bg-gradient-to-br from-green-50 to-orange-50">
      {/* Mobile Layout */}
      <div className="lg:hidden flex flex-col h-full max-w-md mx-auto relative">
        {/* Fixed Menu Button */}
        <div className="fixed top-4 left-4 z-50">
          <Sheet open={isMobileMenuOpen} onOpenChange={setIsMobileMenuOpen}>
            <SheetTrigger asChild>
              <div className="relative">
                <Button
                  size="icon"
                  className="bg-primary hover:bg-primary-dark text-white shadow-lg rounded-full w-12 h-12 transition-all duration-200 hover:scale-105"
                >
                  <Menu size={20} />
                </Button>
                {/* Indicador de notificación */}
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-secondary rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-bold">3</span>
                </div>
              </div>
            </SheetTrigger>

            {/* Fixed User Avatar - Mobile */}
            <div className="fixed top-4 right-4 z-50">
              <div className="relative">
                <Button
                  variant="ghost"
                  className="relative h-12 w-12 rounded-full p-0 bg-white shadow-lg hover:bg-gray-50"
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                >
                  <Avatar className="h-10 w-10 border-2 border-primary/20">
                    <AvatarImage
                      key={avatarKey}
                      src={resolvedAvatar}
                      alt={user?.usr_usuario || 'Usuario'}
                    />
                    <AvatarFallback className="bg-primary text-white font-semibold text-sm">
                      {getUserInitials()}
                    </AvatarFallback>
                  </Avatar>
                </Button>

                {/* Mobile Dropdown Menu */}
                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                    <div className="p-3 border-b border-gray-100">
                      <p className="font-medium text-sm text-gray-900">
                        {user?.usr_nombre ? `${user.usr_nombre} ${user.usr_apellido}` : user?.usr_usuario}
                      </p>
                      <p className="text-xs text-gray-500">
                        {user?.usr_correo}
                      </p>
                    </div>

                    <div className="py-1">
                      <button
                        onClick={() => handleUserMenuClick('profile')}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <User className="mr-2 h-4 w-4" />
                        Ver Perfil
                      </button>

                      <button
                        onClick={() => handleUserMenuClick('settings')}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        Configuración
                      </button>

                      <div className="border-t border-gray-100 my-1"></div>

                      <button
                        onClick={() => handleUserMenuClick('logout')}
                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        <LogOut className="mr-2 h-4 w-4" />
                        Cerrar Sesión
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <SheetContent
              side="left"
              className="w-[75%] p-0 bg-white border-r-2 border-primary/10"
            >
              <div className="flex flex-col h-full">
                {/* Header del menú */}
                <SheetHeader className="p-4 bg-gradient-to-r from-primary/5 to-secondary/5 border-b">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center shadow-sm">
                        <span className="text-white font-bold text-sm">NF</span>
                      </div>
                      <div>
                        <SheetTitle className="text-lg font-semibold text-left">NutriFamily</SheetTitle>
                        <p className="text-sm text-muted-foreground text-left">Menú Principal</p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      <X size={16} />
                    </Button>
                  </div>
                </SheetHeader>

                {/* Perfil del usuario */}
                <div className="p-4 border-b bg-muted/20">
                  <div className="flex items-center space-x-3">
                    <Avatar className="w-12 h-12 ring-2 ring-primary/20">
                      <AvatarImage key={`${avatarKey}-sheet`} src={resolvedAvatar} />
                      <AvatarFallback className="bg-primary text-white">{getUserInitials()}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <p className="font-semibold text-sm">{user?.usr_nombre} {user?.usr_apellido}</p>
                      <p className="text-xs text-muted-foreground">{user?.usr_correo}</p>
                      <div className="flex items-center mt-1">
                        <div className="w-2 h-2 bg-success rounded-full mr-2"></div>
                        <span className="text-xs text-success font-medium">Activa</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Navegación por categorías */}
                <div className="flex-1 overflow-y-auto py-2">
                  {Object.entries(groupedTabs).map(([category, categoryTabs], categoryIndex) => (
                    <motion.div
                      key={category}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: categoryIndex * 0.1 }}
                      className="py-3"
                    >
                      <div className="px-4 mb-3">
                        <Badge className={`text-xs px-3 py-1 ${getCategoryColor(category)}`}>
                          {getCategoryLabel(category)}
                        </Badge>
                      </div>

                      <div className="space-y-1 px-2">
                        {categoryTabs.map((tab, tabIndex) => {
                          const Icon = tab.icon;
                          const isActive = activeTab === tab.id;
                          const hasNotification = ['community', 'gamification', 'risk-prediction'].includes(tab.id);

                          return (
                            <motion.button
                              key={tab.id}
                              initial={{ opacity: 0, x: -20 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: (categoryIndex * 0.1) + (tabIndex * 0.05) }}
                              whileTap={{ scale: 0.95 }}
                              onClick={() => handleMobileMenuItemClick(tab.id)}
                              className={`w-full flex items-center space-x-3 px-3 py-3 rounded-lg text-left transition-all relative ${isActive
                                  ? 'bg-primary text-white shadow-md'
                                  : 'text-gray-600 hover:bg-gray-100 active:bg-gray-200'
                                }`}
                            >
                              <div className="relative">
                                <Icon size={20} />
                                {hasNotification && !isActive && (
                                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-secondary rounded-full"></div>
                                )}
                              </div>
                              <span className="font-medium text-sm">{tab.label}</span>
                              {isActive && (
                                <motion.div
                                  layoutId="activeIndicator"
                                  className="ml-auto w-2 h-2 bg-white rounded-full"
                                />
                              )}
                              {hasNotification && isActive && (
                                <div className="ml-auto w-2 h-2 bg-secondary rounded-full"></div>
                              )}
                            </motion.button>
                          );
                        })}
                      </div>
                    </motion.div>
                  ))}

                  {/* Acciones rápidas al final del menú */}
                  <div className="px-4 py-3 border-t mt-4">
                    <p className="text-xs text-muted-foreground mb-3 font-medium">Acciones Rápidas</p>
                    <div className="space-y-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full justify-start h-8 text-xs"
                        onClick={() => handleMobileMenuItemClick('scan')}
                      >
                        <Scan size={14} className="mr-2" />
                        Escanear Producto
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full justify-start h-8 text-xs"
                        onClick={() => handleMobileMenuItemClick('meal-plan')}
                      >
                        <Calendar size={14} className="mr-2" />
                        Ver Plan Hoy
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Footer del menú */}
                <div className="p-4 border-t bg-muted/30">
                  <div className="text-center">
                    <p className="text-xs text-muted-foreground">NutriFamily v2.1.0</p>
                    <p className="text-xs text-muted-foreground/70 mt-1">© 2024</p>
                  </div>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto pb-20 pt-4">
          {children}
        </div>

        {/* Bottom Navigation - Mobile Only (pestañas principales) */}
        <div className="absolute bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-2 py-2">
          <div className="flex justify-around items-center">
            {mainMobileTabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => onTabChange(tab.id)}
                  className={`flex flex-col items-center py-2 px-2 rounded-lg transition-colors ${isActive
                      ? 'text-primary bg-primary/10'
                      : 'text-gray-500 hover:text-primary'
                    }`}
                >
                  <Icon size={18} />
                  <span className="text-xs mt-1">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Desktop Layout */}
      <div className="hidden lg:flex h-full">
        {/* Sidebar - Desktop Only */}
        <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
          {/* Logo and Brand */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">NF</span>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-800">NutriFamily</h1>
                <p className="text-xs text-gray-500">Alimentación saludable</p>
              </div>
            </div>
          </div>

          {/* User Profile */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <Avatar className="w-10 h-10">
                <AvatarImage key={`${avatarKey}-sidebar`} src={resolvedAvatar} />
                <AvatarFallback>{getUserInitials()}</AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-800 truncate">{user?.usr_nombre} {user?.usr_apellido}</p>
                <p className="text-xs text-gray-500 truncate">{user?.usr_correo}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4">
            <div className="space-y-2">
              {desktopSidebarOrder.map((id) => {
                const tab = tabs.find((t) => t.id === id);
                if (!tab) return null;
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => onTabChange(tab.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${isActive
                        ? 'bg-green-100 text-green-700 border border-green-200'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                      }`}
                  >
                    <Icon size={20} />
                    <span className="text-sm font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="text-center">
              <p className="text-xs text-gray-500">NutriFamily v2.1.0</p>
              <p className="text-xs text-gray-400 mt-1">© 2025 Todos los derechos reservados</p>
            </div>
          </div>
        </div>

        {/* Main Content - Desktop */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Top Header - Desktop */}
          <header className="bg-white border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-800 capitalize">
                  {tabs.find(tab => tab.id === activeTab)?.label || 'NutriFamily'}
                </h2>
                <p className="text-sm text-gray-500">
                  {activeTab === 'home' && 'Panel principal de alimentación'}
                  {activeTab === 'meal-plan' && 'Plan personalizado de comidas y recetas'}
                  {activeTab === 'scan' && 'Análisis inteligente de alimentos'}
                  {activeTab === 'risk-prediction' && 'Predicción de riesgos nutricionales'}
                  {activeTab === 'progress' && 'Seguimiento nutricional'}
                  {activeTab === 'community' && 'Conecta con otras familias'}
                  {activeTab === 'gamification' && 'Logros y recompensas'}
                  {activeTab === 'clinical' && 'Antropometría, alergias y entidad'}
                  {activeTab === 'profile' && 'Configuración y perfil'}
                  {activeTab === 'admin' && 'Gestión de usuarios y contraseñas'}
                </p>
              </div>

              {/* User Avatar with Dropdown */}
              <div className="relative">
                <Button
                  variant="ghost"
                  className="relative h-10 w-10 rounded-full p-0 hover:bg-gray-100"
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                >
                  <Avatar className="h-10 w-10 border-2 border-primary/20">
                    <AvatarImage
                      key={`${avatarKey}-bottom`}
                      src={resolvedAvatar}
                      alt={user?.usr_usuario || 'Usuario'}
                    />
                    <AvatarFallback className="bg-primary text-white font-semibold">
                      {getUserInitials()}
                    </AvatarFallback>
                  </Avatar>
                  <ChevronDown className="absolute -bottom-1 -right-1 h-4 w-4 bg-white rounded-full p-0.5 text-gray-500" />
                </Button>

                {/* Dropdown Menu */}
                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                    <div className="p-3 border-b border-gray-100">
                      <p className="font-medium text-sm text-gray-900">
                        {user?.usr_nombre ? `${user.usr_nombre} ${user.usr_apellido}` : user?.usr_usuario}
                      </p>
                      <p className="text-xs text-gray-500">
                        {user?.usr_correo}
                      </p>
                    </div>

                    <div className="py-1">
                      <button
                        onClick={() => handleUserMenuClick('profile')}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <User className="mr-2 h-4 w-4" />
                        Ver Perfil
                      </button>

                      <button
                        onClick={() => handleUserMenuClick('settings')}
                        className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <Settings className="mr-2 h-4 w-4" />
                        Configuración
                      </button>

                      <div className="border-t border-gray-100 my-1"></div>

                      <button
                        onClick={() => handleUserMenuClick('logout')}
                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        <LogOut className="mr-2 h-4 w-4" />
                        Cerrar Sesión
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </header>

          {/* Content Area */}
          <main className="flex-1 overflow-y-auto bg-gradient-to-br from-green-50 to-orange-50">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
