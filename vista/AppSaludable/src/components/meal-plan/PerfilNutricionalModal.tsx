import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { useToast } from '../ui/use-toast';
import { Loader2, RefreshCw, Activity, TrendingUp } from 'lucide-react';
import {
  obtenerPerfilNutricional,
  calcularPerfilNutricional,
} from '../../services/mealPlanApi';
import type { PerfilNutricional } from '../../types/mealPlan';

interface PerfilNutricionalModalProps {
  open: boolean;
  onClose: (recargar?: boolean) => void;
  ninId: number;
  ninNombre: string;
}

export const PerfilNutricionalModal: React.FC<PerfilNutricionalModalProps> = ({
  open,
  onClose,
  ninId,
  ninNombre,
}) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [calculando, setCalculando] = useState(false);
  const [perfil, setPerfil] = useState<PerfilNutricional | null>(null);

  useEffect(() => {
    if (open) {
      cargarPerfil();
    }
  }, [open, ninId]);

  const cargarPerfil = async () => {
    setLoading(true);
    try {
      const data = await obtenerPerfilNutricional(ninId);
      setPerfil(data);
    } catch (error: any) {
      if (error.response?.status === 404) {
        setPerfil(null);
      } else {
        toast({
          title: 'Error',
          description: 'No se pudo cargar el perfil nutricional',
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCalcular = async () => {
    setCalculando(true);
    try {
      await calcularPerfilNutricional(ninId);
      toast({
        title: 'Perfil calculado',
        description: 'El perfil nutricional se calculó exitosamente',
      });
      await cargarPerfil();
      onClose(true);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo calcular el perfil. Verifica que el niño tenga antropometría.',
        variant: 'destructive',
      });
    } finally {
      setCalculando(false);
    }
  };

  const formatClasificacion = (clasificacion?: string) => {
    if (!clasificacion) return 'Sin clasificar';
    return clasificacion.replace(/_/g, ' ');
  };

  const getClasificacionColor = (clasificacion?: string) => {
    switch (clasificacion) {
      case 'NORMAL':
        return 'text-green-600 bg-green-50';
      case 'SOBREPESO':
      case 'OBESIDAD':
        return 'text-orange-600 bg-orange-50';
      case 'DESNUTRICION':
      case 'DESNUTRICION_SEVERA':
        return 'text-red-600 bg-red-50';
      case 'RIESGO':
        return 'text-yellow-600 bg-yellow-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Perfil Nutricional de {ninNombre}</DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : !perfil ? (
          <div className="text-center py-12">
            <Activity className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No hay perfil nutricional
            </h3>
            <p className="text-gray-600 mb-6">
              Calcula el perfil nutricional basado en la última antropometría del niño
            </p>
            <Button
              onClick={handleCalcular}
              disabled={calculando}
              className="bg-green-600 hover:bg-green-700"
            >
              {calculando ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Calculando...
                </>
              ) : (
                <>
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Calcular Perfil
                </>
              )}
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Header con clasificación */}
            <Card className={getClasificacionColor(perfil.pnn_clasificacion)}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">Clasificación Nutricional</p>
                    <p className="text-2xl font-bold">
                      {formatClasificacion(perfil.pnn_clasificacion)}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCalcular}
                    disabled={calculando}
                  >
                    {calculando ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Requerimientos diarios */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Requerimientos Diarios</h3>
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-600">Calorías</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {perfil.pnn_calorias_diarias}
                      <span className="text-sm font-normal text-gray-500 ml-1">kcal</span>
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-600">Proteínas</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {perfil.pnn_proteinas_g.toFixed(1)}
                      <span className="text-sm font-normal text-gray-500 ml-1">g</span>
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-600">Carbohidratos</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {perfil.pnn_carbohidratos_g.toFixed(1)}
                      <span className="text-sm font-normal text-gray-500 ml-1">g</span>
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <p className="text-sm text-gray-600">Grasas</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {perfil.pnn_grasas_g.toFixed(1)}
                      <span className="text-sm font-normal text-gray-500 ml-1">g</span>
                    </p>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Micronutrientes */}
            {(perfil.pnn_hierro_mg ||
              perfil.pnn_calcio_mg ||
              perfil.pnn_vitamina_c_mg ||
              perfil.pnn_fibra_g) && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Micronutrientes</h3>
                <div className="grid grid-cols-2 gap-3">
                  {perfil.pnn_hierro_mg && (
                    <div className="flex justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-600">Hierro</span>
                      <span className="text-sm font-medium">
                        {perfil.pnn_hierro_mg.toFixed(1)} mg
                      </span>
                    </div>
                  )}
                  {perfil.pnn_calcio_mg && (
                    <div className="flex justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-600">Calcio</span>
                      <span className="text-sm font-medium">
                        {perfil.pnn_calcio_mg.toFixed(0)} mg
                      </span>
                    </div>
                  )}
                  {perfil.pnn_vitamina_c_mg && (
                    <div className="flex justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-600">Vitamina C</span>
                      <span className="text-sm font-medium">
                        {perfil.pnn_vitamina_c_mg.toFixed(1)} mg
                      </span>
                    </div>
                  )}
                  {perfil.pnn_fibra_g && (
                    <div className="flex justify-between p-3 bg-gray-50 rounded-lg">
                      <span className="text-sm text-gray-600">Fibra</span>
                      <span className="text-sm font-medium">
                        {perfil.pnn_fibra_g.toFixed(1)} g
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Información adicional */}
            <div className="text-sm text-gray-600 space-y-1">
              <p>
                <span className="font-medium">Edad:</span> {perfil.pnn_edad_meses} meses (
                {Math.floor(perfil.pnn_edad_meses / 12)} años)
              </p>
              {perfil.pnn_peso_kg && (
                <p>
                  <span className="font-medium">Peso:</span> {perfil.pnn_peso_kg} kg
                </p>
              )}
              {perfil.pnn_talla_cm && (
                <p>
                  <span className="font-medium">Talla:</span> {perfil.pnn_talla_cm} cm
                </p>
              )}
              <p>
                <span className="font-medium">Método:</span> {perfil.pnn_metodo_calculo}
              </p>
              <p>
                <span className="font-medium">Calculado:</span>{' '}
                {new Date(perfil.pnn_fecha_calculo).toLocaleDateString('es-PE')}
              </p>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
