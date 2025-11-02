import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { useToast } from '../ui/use-toast';
import { Loader2, Plus, X, Heart, Search } from 'lucide-react';
import {
  obtenerComidasFavoritas,
  agregarComidaFavorita,
  eliminarComidaFavorita,
  buscarRecetas,
  obtenerRecetasPlanActual,
  registrarFeedbackComida,
  toggleComidaFavorita,
} from '../../services/mealPlanApi';
import { RatingStars } from './RatingStars';

interface ComidasFavoritasModalProps {
  open: boolean;
  onClose: (recargar?: boolean) => void;
  ninId: number;
  ninNombre: string;
}

interface ComidaFavorita {
  ncf_id: number;
  rec_id: number;
  rec_nombre: string;
  rec_tipo_comida: string;
  creado_en: string;
}

interface Receta {
  rec_id: number;
  rec_nombre: string;
  tipo_comida: string;
  kcal?: number;
  mei_id: number;
  es_favorita?: boolean;
  rating_actual?: number;
}

export const ComidasFavoritasModal: React.FC<ComidasFavoritasModalProps> = ({
  open,
  onClose,
  ninId,
  ninNombre,
}) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [favoritas, setFavoritas] = useState<ComidaFavorita[]>([]);
  const [busqueda, setBusqueda] = useState('');
  const [recetasEncontradas, setRecetasEncontradas] = useState<Receta[]>([]);
  const [buscando, setBuscando] = useState(false);
  const [agregando, setAgregando] = useState(false);
  const [cambiosRealizados, setCambiosRealizados] = useState(false);

  useEffect(() => {
    if (open) {
      cargarFavoritas();
      setCambiosRealizados(false);
    }
  }, [open, ninId]);

  // Búsqueda automática con debounce (como Gmail)
  useEffect(() => {
    if (!busqueda.trim()) {
      setRecetasEncontradas([]);
      return;
    }

    const timer = setTimeout(() => {
      handleBuscar();
    }, 500); // Espera 500ms después de que el usuario deja de escribir

    return () => clearTimeout(timer);
  }, [busqueda]);

  const cargarFavoritas = async () => {
    setLoading(true);
    try {
      const data = await obtenerComidasFavoritas(ninId);
      setFavoritas(data.favoritas || []);
    } catch (error: any) {
      if (!error.message?.includes('404')) {
        toast({
          title: 'Error',
          description: 'No se pudieron cargar las comidas favoritas',
          variant: 'destructive',
        });
      }
      setFavoritas([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBuscar = async () => {
    if (!busqueda.trim()) return;

    setBuscando(true);
    try {
      const data = await obtenerRecetasPlanActual(ninId, busqueda.trim());
      setRecetasEncontradas(data.recetas || []);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudieron buscar recetas',
        variant: 'destructive',
      });
      setRecetasEncontradas([]);
    } finally {
      setBuscando(false);
    }
  };

  const handleToggleFavorita = async (recId: number, recNombre: string) => {
    setAgregando(true);
    try {
      const result = await toggleComidaFavorita(ninId, recId);
      toast({
        title: result.accion === 'AGREGADA' ? 'Favorita agregada' : 'Favorita eliminada',
        description: `${recNombre} ${
          result.accion === 'AGREGADA' ? 'agregada a' : 'eliminada de'
        } favoritas`,
      });
      await cargarFavoritas();
      if (recetasEncontradas.length > 0) {
        await handleBuscar();
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo actualizar la favorita',
        variant: 'destructive',
      });
    } finally {
      setAgregando(false);
    }
  };

  const handleRating = async (receta: Receta, rating: number) => {
    try {
      await registrarFeedbackComida({
        mei_id: receta.mei_id,
        nin_id: ninId,
        mf_rating: rating,
        mf_completado: rating >= 3,
      });
      toast({
        title: 'Calificación guardada',
        description: `${receta.rec_nombre} calificada con ${rating} estrellas`,
      });
      await handleBuscar();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo guardar la calificación',
        variant: 'destructive',
      });
    }
  };

  const handleAgregar = async (recId: number, recNombre: string) => {
    setAgregando(true);
    try {
      await agregarComidaFavorita(ninId, recId);
      toast({
        title: 'Favorita agregada',
        description: `Se agregó "${recNombre}" a las favoritas de ${ninNombre}`,
      });
      setBusqueda('');
      setRecetasEncontradas([]);
      setCambiosRealizados(true);
      await cargarFavoritas();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo agregar la comida favorita',
        variant: 'destructive',
      });
    } finally {
      setAgregando(false);
    }
  };

  const handleEliminar = async (ncfId: number, recNombre: string) => {
    try {
      await eliminarComidaFavorita(ncfId);
      toast({
        title: 'Favorita eliminada',
        description: `Se eliminó "${recNombre}"`,
      });
      setCambiosRealizados(true);
      await cargarFavoritas();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudo eliminar la comida favorita',
        variant: 'destructive',
      });
    }
  };

  const esFavorita = (recId: number) => {
    return favoritas.some((f) => f.rec_id === recId);
  };

  const handleClose = () => {
    onClose(cambiosRealizados);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Heart className="w-5 h-5 text-red-600" />
            Comidas Favoritas de {ninNombre}
          </DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : (
          <div className="space-y-6">
            {/* Buscador de recetas */}
            <div className="border rounded-lg p-4 bg-gray-50">
              <h3 className="font-semibold text-gray-900 mb-3">Buscar Recetas</h3>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <Input
                  placeholder="Escribe para buscar recetas en tiempo real..."
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  className="pl-10 pr-10"
                />
                {buscando && (
                  <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 animate-spin text-blue-600" />
                )}
              </div>

              {/* Resultados de búsqueda */}
              {/* Resultados de búsqueda */}
              {busqueda.trim() && !buscando && recetasEncontradas.length === 0 && (
                <div className="mt-4 text-center py-8 text-gray-500">
                  <Search className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                  <p>No se encontraron recetas con "{busqueda}"</p>
                  <p className="text-sm mt-1">Intenta con otro término de búsqueda</p>
                </div>
              )}

              {recetasEncontradas.length > 0 && (
                <div className="mt-4 space-y-2 max-h-60 overflow-y-auto">
                  <p className="text-sm text-gray-600 mb-2">
                    {recetasEncontradas.length} receta{recetasEncontradas.length !== 1 ? 's' : ''} encontrada{recetasEncontradas.length !== 1 ? 's' : ''}
                  </p>
                  {recetasEncontradas.map((receta) => (
                    <div
                      key={`${receta.mei_id}-${receta.rec_id}`}
                      className="flex items-center justify-between p-3 bg-white rounded-lg border hover:border-blue-300 transition-colors"
                    >
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{receta.rec_nombre}</p>
                        <p className="text-sm text-gray-600">
                          {receta.tipo_comida}
                          {receta.kcal && ` • ${receta.kcal} kcal`}
                        </p>
                        <div className="mt-2 flex items-center gap-2">
                          <RatingStars
                            rating={receta.rating_actual || 0}
                            onChange={(rating) => handleRating(receta, rating)}
                            size="sm"
                          />
                          {(receta.rating_actual ?? 0) > 0 && (
                            <span className="text-xs text-gray-500">
                              ({(receta.rating_actual ?? 0).toFixed(1)})
                            </span>
                          )}
                        </div>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => handleToggleFavorita(receta.rec_id, receta.rec_nombre)}
                        disabled={agregando}
                        className={receta.es_favorita ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}
                        title={receta.es_favorita ? 'Quitar de favoritas' : 'Agregar a favoritas'}
                      >
                        <Heart className={receta.es_favorita ? 'w-4 h-4 fill-current' : 'w-4 h-4'} />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Lista de favoritas */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">
                Favoritas Registradas ({favoritas.length})
              </h3>
              {favoritas.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Heart className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                  <p>No hay comidas favoritas registradas</p>
                  <p className="text-sm">Busca y agrega las comidas favoritas del niño</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {favoritas.map((favorita) => (
                    <div
                      key={favorita.ncf_id}
                      className="flex items-center justify-between p-3 rounded-lg border bg-white hover:bg-gray-50"
                    >
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{favorita.rec_nombre}</p>
                        <p className="text-sm text-gray-600">{favorita.rec_tipo_comida}</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() =>
                          handleEliminar(favorita.ncf_id, favorita.rec_nombre)
                        }
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Botón cerrar */}
            <div className="flex justify-end pt-4 border-t">
              <Button onClick={handleClose} variant="outline">
                Cerrar
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
