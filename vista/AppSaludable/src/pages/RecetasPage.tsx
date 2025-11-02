import React, { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../components/ui/use-toast';
import { alimentosRecetasApi } from '../services/alimentosRecetasApi';
import { RecetaResponse, RecetaCreate, RecetaUpdate, RecetaCompletaResponse } from '../types/api';
import RecetaFormNew from '../components/recetas/RecetaFormNew';
import RecetaDetail from '../components/recetas/RecetaDetail';
import { Search, Plus, Edit, Trash2, Eye, ChefHat } from 'lucide-react';

const TIPOS_COMIDA = [
  'DESAYUNO',
  'ALMUERZO',
  'CENA',
  'SNACK',
  'POSTRE'
];

interface RecetasPageProps {
  embedded?: boolean;
}

const RecetasPage: React.FC<RecetasPageProps> = ({ embedded = false }) => {
  const { toast } = useToast();
  const [recetas, setRecetas] = useState<RecetaResponse[]>([]);
  const [filteredRecetas, setFilteredRecetas] = useState<RecetaResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTipoComida, setSelectedTipoComida] = useState<string>('');
  const [selectedReceta, setSelectedReceta] = useState<RecetaCompletaResponse | null>(null);
  const [editingReceta, setEditingReceta] = useState<RecetaResponse | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);

  useEffect(() => {
    loadRecetas();
  }, []);

  useEffect(() => {
    filterRecetas();
  }, [recetas, searchTerm, selectedTipoComida]);

  const loadRecetas = async () => {
    try {
      setLoading(true);
      const response = await alimentosRecetasApi.getRecetas(selectedTipoComida || undefined);
      setRecetas(response.data || []);
    } catch (error) {
      console.error('Error al cargar recetas:', error);
      toast({
        title: "Error",
        description: "No se pudieron cargar las recetas",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const filterRecetas = () => {
    let filtered = recetas;

    if (searchTerm) {
      filtered = filtered.filter(receta =>
        receta.rec_nombre.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredRecetas(filtered);
  };

  const handleCreateReceta = async (data: any) => {
    try {
      // Crear la receta
      const response = await alimentosRecetasApi.createReceta({
        rec_nombre: data.rec_nombre,
        rec_instrucciones: data.rec_instrucciones,
        rec_activo: data.rec_activo
      });

      if (response.data && data.ingredientes && data.ingredientes.length > 0) {
        // Agregar ingredientes uno por uno
        const recId = response.data.rec_id;
        for (const ing of data.ingredientes) {
          try {
            await alimentosRecetasApi.addIngredienteToReceta(recId, {
              rec_id: recId,
              ali_id: ing.ali_id > 0 ? ing.ali_id : undefined,
              ri_cantidad: ing.cantidad,
              ri_unidad: ing.unidad
            });
          } catch (error) {
            console.error(`Error agregando ingrediente ${ing.ali_nombre}:`, error);
          }
        }
      }

      toast({
        title: "Éxito",
        description: "Receta creada correctamente con sus ingredientes",
      });
      setIsCreateDialogOpen(false);
      loadRecetas();
    } catch (error) {
      console.error('Error al crear receta:', error);
      toast({
        title: "Error",
        description: "No se pudo crear la receta",
        variant: "destructive",
      });
    }
  };

  const handleUpdateReceta = async (data: any) => {
    if (!editingReceta) return;

    try {
      // Actualizar la receta
      await alimentosRecetasApi.updateReceta(editingReceta.rec_id, {
        rec_nombre: data.rec_nombre,
        rec_instrucciones: data.rec_instrucciones,
        rec_activo: data.rec_activo
      });

      // Actualizar ingredientes si se proporcionaron
      if (data.ingredientes) {
        // Aquí podrías implementar lógica más compleja para:
        // 1. Eliminar ingredientes que ya no están
        // 2. Agregar nuevos ingredientes
        // 3. Actualizar cantidades de ingredientes existentes

        // Por simplicidad, solo agregamos los nuevos
        for (const ing of data.ingredientes) {
          try {
            if (ing.ali_id > 0) {
              await alimentosRecetasApi.addIngredienteToReceta(editingReceta.rec_id, {
                rec_id: editingReceta.rec_id,
                ali_id: ing.ali_id,
                ri_cantidad: ing.cantidad,
                ri_unidad: ing.unidad
              });
            }
          } catch (error) {
            // Podría fallar si el ingrediente ya existe, está bien
            console.log(`Ingrediente ${ing.ali_nombre} ya existe o error:`, error);
          }
        }
      }

      toast({
        title: "Éxito",
        description: "Receta actualizada correctamente",
      });
      setIsEditDialogOpen(false);
      setEditingReceta(null);
      loadRecetas();
    } catch (error) {
      console.error('Error al actualizar receta:', error);
      toast({
        title: "Error",
        description: "No se pudo actualizar la receta",
        variant: "destructive",
      });
    }
  };

  const handleDeleteReceta = async (recetaId: number) => {
    if (!confirm('¿Estás seguro de que quieres eliminar esta receta?')) {
      return;
    }

    try {
      await alimentosRecetasApi.deleteReceta(recetaId);
      toast({
        title: "Éxito",
        description: "Receta eliminada correctamente",
      });
      loadRecetas();
    } catch (error) {
      console.error('Error al eliminar receta:', error);
      toast({
        title: "Error",
        description: "No se pudo eliminar la receta",
        variant: "destructive",
      });
    }
  };

  const handleViewReceta = async (recetaId: number) => {
    try {
      const response = await alimentosRecetasApi.getReceta(recetaId);
      setSelectedReceta(response.data || null);
      setIsDetailDialogOpen(true);
    } catch (error) {
      console.error('Error al cargar detalles de la receta:', error);
      toast({
        title: "Error",
        description: "No se pudieron cargar los detalles de la receta",
        variant: "destructive",
      });
    }
  };

  const handleTipoComidaChange = (value: string) => {
    setSelectedTipoComida(value === 'all' ? '' : value);
    loadRecetas(); // Recargar con el filtro aplicado
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <ChefHat className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          <p className="text-gray-500">Cargando recetas...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={embedded ? "space-y-6" : "container mx-auto p-6 space-y-6"}>
      {/* Header */}
      {!embedded && (
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestión de Recetas</h1>
            <p className="text-gray-600">Administra las recetas del sistema</p>
          </div>

          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Nueva Receta
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
              <DialogHeader>
                <DialogTitle>Crear Nueva Receta</DialogTitle>
                <DialogDescription>
                  Crea una nueva receta agregando ingredientes e instrucciones de preparación
                </DialogDescription>
              </DialogHeader>
              <div className="overflow-y-auto flex-1">
                <RecetaFormNew onSubmit={(data) => handleCreateReceta(data as RecetaCreate)} />
              </div>
            </DialogContent>
          </Dialog>
        </div>
      )}

      {/* Botón de crear en modo embebido */}
      {embedded && (
        <div className="flex justify-end">
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-green-600 hover:bg-green-700">
                <Plus className="h-4 w-4 mr-2" />
                Nueva Receta
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
              <DialogHeader>
                <DialogTitle>Crear Nueva Receta</DialogTitle>
                <DialogDescription>
                  Crea una nueva receta agregando ingredientes e instrucciones de preparación
                </DialogDescription>
              </DialogHeader>
              <div className="overflow-y-auto flex-1">
                <RecetaFormNew onSubmit={(data) => handleCreateReceta(data as RecetaCreate)} />
              </div>
            </DialogContent>
          </Dialog>
        </div>
      )}

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Buscar recetas por nombre..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <div className="w-full sm:w-48">
              <Select value={selectedTipoComida} onValueChange={handleTipoComidaChange}>
                <SelectTrigger>
                  <SelectValue placeholder="Tipo de comida" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los tipos</SelectItem>
                  {TIPOS_COMIDA.map((tipo) => (
                    <SelectItem key={tipo} value={tipo}>
                      {tipo}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de recetas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredRecetas.map((receta) => (
          <Card key={receta.rec_id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="truncate">{receta.rec_nombre}</span>
                <Badge variant={receta.rec_activo ? "default" : "secondary"}>
                  {receta.rec_activo ? "Activa" : "Inactiva"}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {receta.rec_instrucciones && (
                  <p className="text-sm text-gray-600 line-clamp-3">
                    {receta.rec_instrucciones}
                  </p>
                )}

                <div className="flex justify-between items-center pt-2">
                  <span className="text-xs text-gray-500">ID: {receta.rec_id}</span>

                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewReceta(receta.rec_id)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditingReceta(receta);
                        setIsEditDialogOpen(true);
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteReceta(receta.rec_id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Mensaje cuando no hay recetas */}
      {filteredRecetas.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <ChefHat className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No se encontraron recetas
            </h3>
            <p className="text-gray-500 mb-4">
              {searchTerm || selectedTipoComida
                ? 'Intenta ajustar los filtros de búsqueda'
                : 'Comienza creando tu primera receta'}
            </p>
            {!searchTerm && !selectedTipoComida && (
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Crear Primera Receta
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Dialog para editar receta */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>Editar Receta</DialogTitle>
            <DialogDescription>
              Modifica los ingredientes, instrucciones y tipos de comida de la receta
            </DialogDescription>
          </DialogHeader>
          <div className="overflow-y-auto flex-1">
            {editingReceta && (
              <RecetaFormNew
                initialData={editingReceta}
                onSubmit={(data) => handleUpdateReceta(data as RecetaUpdate)}
                isEdit={true}
              />
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Dialog para ver detalles de receta */}
      <Dialog open={isDetailDialogOpen} onOpenChange={setIsDetailDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Detalles de la Receta</DialogTitle>
            <DialogDescription>
              Visualiza todos los detalles, ingredientes e información nutricional de la receta
            </DialogDescription>
          </DialogHeader>
          {selectedReceta && <RecetaDetail receta={selectedReceta} />}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default RecetasPage;
