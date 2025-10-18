/**
 * Tarjeta de niño con botones de acción
 */
import React from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { User, Calendar, Activity } from 'lucide-react';
import type { NinoConPreferencias } from '../../types/mealPlan';

interface ChildCardProps {
  nino: NinoConPreferencias;
  onPreferencias: () => void;
  onPerfil: () => void;
  onAlergias: () => void;
  onComidas: () => void;
  onGenerarPlan: () => void;
}

export const ChildCard: React.FC<ChildCardProps> = ({
  nino,
  onPreferencias,
  onPerfil,
  onAlergias,
  onComidas,
  onGenerarPlan,
}) => {
  const getClasificacionColor = (clasificacion?: string) => {
    switch (clasificacion) {
      case 'NORMAL':
        return 'bg-green-100 text-green-800';
      case 'SOBREPESO':
      case 'OBESIDAD':
        return 'bg-orange-100 text-orange-800';
      case 'DESNUTRICION':
      case 'DESNUTRICION_SEVERA':
        return 'bg-red-100 text-red-800';
      case 'RIESGO':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatClasificacion = (clasificacion?: string) => {
    if (!clasificacion) return 'Sin evaluar';
    return clasificacion.replace(/_/g, ' ').toLowerCase();
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          {/* Información del niño */}
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                <User className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {nino.nin_nombres}
                </h3>
                <p className="text-sm text-gray-500">
                  {nino.edad_anos} años • {nino.nin_sexo === 'M' ? 'Niño' : 'Niña'}
                </p>
              </div>
            </div>

            <div className="space-y-2 mb-4">
              {/* Clasificación */}
              {nino.clasificacion && (
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-gray-400" />
                  <Badge className={getClasificacionColor(nino.clasificacion)}>
                    {formatClasificacion(nino.clasificacion)}
                  </Badge>
                </div>
              )}

              {/* Última evaluación */}
              {nino.ultima_evaluacion && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Calendar className="w-4 h-4 text-gray-400" />
                  <span>
                    Última evaluación:{' '}
                    {new Date(nino.ultima_evaluacion).toLocaleDateString('es-PE')}
                  </span>
                </div>
              )}

              {/* Indicadores */}
              <div className="flex gap-2 mt-2">
                {nino.tiene_preferencias && (
                  <Badge variant="outline" className="text-xs">
                    ✓ Preferencias ({nino.total_preferencias})
                  </Badge>
                )}
                {nino.tiene_perfil && (
                  <Badge variant="outline" className="text-xs">
                    ✓ Perfil nutricional
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {/* Botones de acción */}
          <div className="flex flex-col gap-2 ml-4">
            <Button
              variant="outline"
              size="sm"
              onClick={onPerfil}
              className="w-full justify-start"
            >
              Perfil Nutricional
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onPreferencias}
              className="w-full justify-start"
            >
              Preferencias
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onAlergias}
              className="w-full justify-start"
            >
              Alergias
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onComidas}
              className="w-full justify-start"
            >
              Comidas Favoritas
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={onGenerarPlan}
              className="w-full justify-start bg-purple-600 hover:bg-purple-700"
            >
              🍽️ Comidas
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
