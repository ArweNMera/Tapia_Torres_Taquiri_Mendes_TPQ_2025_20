import { useState } from 'react';
import { Camera, Edit, Baby, Scale, Ruler, Calendar, AlertTriangle, Utensils } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { Badge } from '../ui/badge';
import { Separator } from '../ui/separator';

export function ProfileScreen() {
  const [isEditing, setIsEditing] = useState(false);
  const [childData, setChildData] = useState({
    name: 'Sofía González',
    birthDate: '2021-08-15',
    weight: '12.5',
    height: '85',
    allergies: ['Nueces', 'Mariscos'],
    restrictions: ['Vegetariano'],
    favoriteFood: 'Puré de calabaza'
  });

  const calculateAge = (birthDate: string) => {
    const today = new Date();
    const birth = new Date(birthDate);
    const age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      return age - 1;
    }
    return age;
  };

  const handleSave = () => {
    setIsEditing(false);
    // Here you would save the data
  };

  return (
    <div className="p-4 lg:p-6 space-y-6 lg:max-w-4xl lg:mx-auto">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-2xl font-semibold text-gray-800 mb-2">Perfil de Sofía</h1>
        <p className="text-sm text-gray-600">Información nutricional y preferencias</p>
      </div>

      {/* Profile Picture & Basic Info */}
      <Card className="p-6">
        <div className="flex flex-col items-center">
          <div className="relative mb-4">
            <Avatar className="w-24 h-24">
              <AvatarImage src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150" />
              <AvatarFallback className="bg-pink-100 text-pink-600">SG</AvatarFallback>
            </Avatar>
            <Button
              size="icon"
              className="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-green-600 hover:bg-green-700"
            >
              <Camera size={16} />
            </Button>
          </div>

          {isEditing ? (
            <div className="w-full space-y-3">
              <Input
                value={childData.name}
                onChange={(e) => setChildData({...childData, name: e.target.value})}
                className="text-center"
              />
              <Input
                type="date"
                value={childData.birthDate}
                onChange={(e) => setChildData({...childData, birthDate: e.target.value})}
              />
            </div>
          ) : (
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-800">{childData.name}</h2>
              <p className="text-gray-600 mt-1">
                {calculateAge(childData.birthDate)} años • Nació el {new Date(childData.birthDate).toLocaleDateString('es-ES')}
              </p>
            </div>
          )}
        </div>
      </Card>

      {/* Physical Data */}
      <Card className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-800 flex items-center">
            <Scale size={20} className="mr-2 text-green-600" />
            Datos Físicos
          </h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsEditing(!isEditing)}
          >
            <Edit size={16} />
          </Button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <Scale size={24} className="mx-auto text-blue-600 mb-2" />
            <p className="text-sm text-gray-600">Peso</p>
            {isEditing ? (
              <Input
                value={childData.weight}
                onChange={(e) => setChildData({...childData, weight: e.target.value})}
                className="text-center mt-1"
                placeholder="kg"
              />
            ) : (
              <p className="text-lg font-semibold text-gray-800">{childData.weight} kg</p>
            )}
          </div>

          <div className="text-center p-3 bg-green-50 rounded-lg">
            <Ruler size={24} className="mx-auto text-green-600 mb-2" />
            <p className="text-sm text-gray-600">Altura</p>
            {isEditing ? (
              <Input
                value={childData.height}
                onChange={(e) => setChildData({...childData, height: e.target.value})}
                className="text-center mt-1"
                placeholder="cm"
              />
            ) : (
              <p className="text-lg font-semibold text-gray-800">{childData.height} cm</p>
            )}
          </div>
        </div>

        <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
          <div className="flex items-center text-yellow-800">
            <Baby size={16} className="mr-1" />
            <span className="text-sm font-medium">IMC: Normal (Percentil 65)</span>
          </div>
        </div>
      </Card>

      {/* Allergies & Restrictions */}
      <Card className="p-4">
        <h3 className="font-semibold text-gray-800 flex items-center mb-4">
          <AlertTriangle size={20} className="mr-2 text-red-600" />
          Alergias y Restricciones
        </h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Alergias alimentarias
            </label>
            <div className="flex flex-wrap gap-2">
              {childData.allergies.map((allergy, index) => (
                <Badge key={index} className="bg-red-100 text-red-800">
                  {allergy}
                  {isEditing && (
                    <button
                      className="ml-1 text-red-600 hover:text-red-800"
                      onClick={() => {
                        const newAllergies = childData.allergies.filter((_, i) => i !== index);
                        setChildData({...childData, allergies: newAllergies});
                      }}
                    >
                      ×
                    </button>
                  )}
                </Badge>
              ))}
              {isEditing && (
                <Button size="sm" variant="outline" className="text-red-600 border-red-200">
                  + Agregar
                </Button>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Restricciones dietéticas
            </label>
            <div className="flex flex-wrap gap-2">
              {childData.restrictions.map((restriction, index) => (
                <Badge key={index} className="bg-orange-100 text-orange-800">
                  {restriction}
                  {isEditing && (
                    <button
                      className="ml-1 text-orange-600 hover:text-orange-800"
                      onClick={() => {
                        const newRestrictions = childData.restrictions.filter((_, i) => i !== index);
                        setChildData({...childData, restrictions: newRestrictions});
                      }}
                    >
                      ×
                    </button>
                  )}
                </Badge>
              ))}
              {isEditing && (
                <Button size="sm" variant="outline" className="text-orange-600 border-orange-200">
                  + Agregar
                </Button>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Preferences */}
      <Card className="p-4">
        <h3 className="font-semibold text-gray-800 flex items-center mb-4">
          <Utensils size={20} className="mr-2 text-green-600" />
          Preferencias Alimentarias
        </h3>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Comida favorita
          </label>
          {isEditing ? (
            <Input
              value={childData.favoriteFood}
              onChange={(e) => setChildData({...childData, favoriteFood: e.target.value})}
              placeholder="Ej: Puré de calabaza"
            />
          ) : (
            <p className="text-gray-800 bg-green-50 p-3 rounded-lg">{childData.favoriteFood}</p>
          )}
        </div>
      </Card>

      {/* Growth Chart Button */}
      <Card className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
        <div className="text-center">
          <h3 className="font-semibold text-gray-800 mb-2">📈 Gráfica de Crecimiento</h3>
          <p className="text-sm text-gray-600 mb-3">
            Visualiza el desarrollo de Sofía comparado con estándares de crecimiento
          </p>
          <Button className="bg-purple-600 hover:bg-purple-700 text-white">
            Ver Gráfica Completa
          </Button>
        </div>
      </Card>

      {/* Save/Cancel Buttons */}
      {isEditing && (
        <div className="flex gap-3">
          <Button
            onClick={handleSave}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white"
          >
            Guardar Cambios
          </Button>
          <Button
            onClick={() => setIsEditing(false)}
            variant="outline"
            className="flex-1"
          >
            Cancelar
          </Button>
        </div>
      )}
    </div>
  );
}
