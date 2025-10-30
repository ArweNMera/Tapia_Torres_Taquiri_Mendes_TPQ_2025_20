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
} from '../../services/mealPlanApi';

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
  rec_tipo_comida: string;
  rec_kcal?: number;
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
      const data = await buscarRecetas(busqueda.trim());
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
              <div className="flex gap-3">
                <Input
                  placeholder="Buscar por nombre de receta..."
                  value={busqueda}
                  onChange={(e) => setBusqueda(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleBuscar()}
                  className="flex-1"
                />
                <Button
                  onClick={handleBuscar}
                  disabled={buscando || !busqueda.trim()}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {buscando ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                </Button>
              </div>

              {/* Resultados de búsqueda */}
              {recetasEncontradas.length > 0 && (
                <div className="mt-4 space-y-2 max-h-60 overflow-y-auto">
                  {recetasEncontradas.map((receta) => (
                    <div
                      key={receta.rec_id}
                      className="flex items-center justify-between p-3 bg-white rounded-lg border"
                    >
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{receta.rec_nombre}</p>
                        <p className="text-sm text-gray-600">
                          {receta.rec_tipo_comida}
                          {receta.rec_kcal && ` • ${receta.rec_kcal} kcal`}
                        </p>
                      </div>
                      {esFavorita(receta.rec_id) ? (
                        <span className="text-sm text-green-600 font-medium">
                          ✓ Ya es favorita
                        </span>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => handleAgregar(receta.rec_id, receta.rec_nombre)}
                          disabled={agregando}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          <Plus className="w-4 h-4" />
                        </Button>
                      )}
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
