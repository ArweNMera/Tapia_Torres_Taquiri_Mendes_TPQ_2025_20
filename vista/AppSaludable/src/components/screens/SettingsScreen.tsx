import { useState } from 'react';
import { 
  Bell, 
  Globe, 
  Moon, 
  Shield, 
  HelpCircle, 
  LogOut, 
  ChevronRight,
  Smartphone,
  Volume2,
  Eye
} from 'lucide-react';
import { Card } from '../ui/card';
import { Switch } from '../ui/switch';
import { Button } from '../ui/button';
import { Separator } from '../ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { useAuth } from '../../contexts/AuthContext';

export function SettingsScreen() {
  const { logout, user } = useAuth();
  const [notifications, setNotifications] = useState({
    meals: true,
    progress: true,
    tips: false,
    reminders: true
  });
  
  const [preferences, setPreferences] = useState({
    darkMode: false,
    language: 'es',
    units: 'metric',
    sound: true
  });

  const handleLogout = () => {
    if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
      logout();
    }
  };

  const settingSections = [
    {
      title: 'Notificaciones',
      icon: Bell,
      items: [
        {
          label: 'Recordatorios de comida',
          description: 'Alertas para las horas de alimentación',
          key: 'meals',
          type: 'switch'
        },
        {
          label: 'Actualizaciones de progreso',
          description: 'Notificaciones sobre el crecimiento',
          key: 'progress',
          type: 'switch'
        },
        {
          label: 'Consejos nutricionales',
          description: 'Tips diarios sobre alimentación',
          key: 'tips',
          type: 'switch'
        },
        {
          label: 'Recordatorios de peso',
          description: 'Recordatorios semanales de medición',
          key: 'reminders',
          type: 'switch'
        }
      ]
    },
    {
      title: 'Apariencia y Idioma',
      icon: Globe,
      items: [
        {
          label: 'Modo oscuro',
          description: 'Cambia la apariencia de la aplicación',
          key: 'darkMode',
          type: 'switch'
        },
        {
          label: 'Idioma',
          description: 'Cambiar idioma de la aplicación',
          key: 'language',
          type: 'select',
          options: [
            { value: 'es', label: 'Español' },
            { value: 'en', label: 'English' },
            { value: 'pt', label: 'Português' }
          ]
        },
        {
          label: 'Unidades',
          description: 'Sistema de medidas',
          key: 'units',
          type: 'select',
          options: [
            { value: 'metric', label: 'Métrico (kg, cm)' },
            { value: 'imperial', label: 'Imperial (lb, in)' }
          ]
        }
      ]
    },
    {
      title: 'Accesibilidad',
      icon: Eye,
      items: [
        {
          label: 'Sonidos',
          description: 'Reproducir sonidos en la aplicación',
          key: 'sound',
          type: 'switch'
        },
        {
          label: 'Tamaño de texto',
          description: 'Ajustar el tamaño de la fuente',
          key: 'fontSize',
          type: 'button',
          action: 'Configurar'
        },
        {
          label: 'Alto contraste',
          description: 'Mejorar la visibilidad del contenido',
          key: 'contrast',
          type: 'button',
          action: 'Activar'
        }
      ]
    }
  ];

  const handleNotificationChange = (key: string, value: boolean) => {
    setNotifications(prev => ({ ...prev, [key]: value }));
  };

  const handlePreferenceChange = (key: string, value: any) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="p-4 lg:p-6 space-y-6 lg:max-w-4xl lg:mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-800 mb-2">Configuración</h1>
        <p className="text-gray-600">Personaliza tu experiencia en NutriFamily</p>
      </div>

      {/* Profile Summary */}
      <Card className="p-4 bg-gradient-to-r from-green-50 to-green-100">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-gray-800">Cuenta Familiar</h3>
            <p className="text-sm text-gray-600">maria.gonzalez@email.com</p>
            <p className="text-xs text-green-600 mt-1">Plan Premium • Vence 15/03/2025</p>
          </div>
          <Button variant="outline" size="sm">
            Ver Perfil
          </Button>
        </div>
      </Card>

      {/* Settings Sections */}
      {settingSections.map((section, sectionIndex) => {
        const SectionIcon = section.icon;
        return (
          <Card key={sectionIndex} className="p-4">
            <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
              <SectionIcon size={20} className="mr-2 text-green-600" />
              {section.title}
            </h3>
            <div className="space-y-4">
              {section.items.map((item, itemIndex) => (
                <div key={itemIndex}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-800">{item.label}</h4>
                      <p className="text-sm text-gray-600">{item.description}</p>
                    </div>
                    <div className="ml-4">
                      {item.type === 'switch' && (
                        <Switch
                          checked={section.title === 'Notificaciones' 
                            ? notifications[item.key as keyof typeof notifications]
                            : preferences[item.key as keyof typeof preferences] as boolean
                          }
                          onCheckedChange={(checked) =>
                            section.title === 'Notificaciones'
                              ? handleNotificationChange(item.key, checked)
                              : handlePreferenceChange(item.key, checked)
                          }
                        />
                      )}
                      {item.type === 'select' && item.options && (
                        <Select
                          value={preferences[item.key as keyof typeof preferences] as string}
                          onValueChange={(value) => handlePreferenceChange(item.key, value)}
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {item.options.map((option) => (
                              <SelectItem key={option.value} value={option.value}>
                                {option.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      )}
                      {item.type === 'button' && (
                        <Button variant="outline" size="sm">
                          {item.action}
                          <ChevronRight size={16} className="ml-1" />
                        </Button>
                      )}
                    </div>
                  </div>
                  {itemIndex < section.items.length - 1 && <Separator className="mt-4" />}
                </div>
              ))}
            </div>
          </Card>
        );
      })}

      {/* Quick Actions */}
      <Card className="p-4">
        <h3 className="font-semibold text-gray-800 mb-4 flex items-center">
          <Smartphone size={20} className="mr-2 text-blue-600" />
          Acciones Rápidas
        </h3>
        <div className="space-y-3">
          <Button 
            variant="outline" 
            className="w-full justify-between text-left"
          >
            <div className="flex items-center">
              <HelpCircle size={18} className="mr-3 text-gray-600" />
              <div>
                <p className="font-medium">Centro de Ayuda</p>
                <p className="text-sm text-gray-600">Preguntas frecuentes y soporte</p>
              </div>
            </div>
            <ChevronRight size={16} />
          </Button>
          
          <Button 
            variant="outline" 
            className="w-full justify-between text-left"
          >
            <div className="flex items-center">
              <Shield size={18} className="mr-3 text-gray-600" />
              <div>
                <p className="font-medium">Privacidad y Seguridad</p>
                <p className="text-sm text-gray-600">Configurar datos y privacidad</p>
              </div>
            </div>
            <ChevronRight size={16} />
          </Button>
          
          <Button 
            variant="outline" 
            className="w-full justify-between text-left"
          >
            <div className="flex items-center">
              <Volume2 size={18} className="mr-3 text-gray-600" />
              <div>
                <p className="font-medium">Contactar Nutricionista</p>
                <p className="text-sm text-gray-600">Chat directo con especialistas</p>
              </div>
            </div>
            <ChevronRight size={16} />
          </Button>
        </div>
      </Card>

      {/* App Info */}
      <Card className="p-4 bg-gray-50">
        <div className="text-center space-y-2">
          <h3 className="font-semibold text-gray-800">NutriFamily</h3>
          <p className="text-sm text-gray-600">Versión 2.1.0</p>
          <div className="flex justify-center space-x-4 text-xs text-gray-500">
            <button className="hover:text-green-600">Términos de Servicio</button>
            <span>•</span>
            <button className="hover:text-green-600">Política de Privacidad</button>
          </div>
        </div>
      </Card>

      {/* Logout */}
      <Button 
        variant="outline" 
        className="w-full text-red-600 border-red-200 hover:bg-red-50"
        onClick={handleLogout}
      >
        <LogOut size={18} className="mr-2" />
        Cerrar Sesión
      </Button>

      {/* Info adicional */}
      <div className="text-center text-xs text-muted-foreground">
        También puedes cerrar sesión desde tu avatar en la parte superior
      </div>

      {/* Bottom spacing for navigation */}
      <div className="h-4"></div>
    </div>
  );
}