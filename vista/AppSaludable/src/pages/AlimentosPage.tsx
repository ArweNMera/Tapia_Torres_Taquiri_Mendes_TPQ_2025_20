import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Eye, Filter } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../components/ui/use-toast';
import { alimentosRecetasApi } from '../services/alimentosRecetasApi';
import { AlimentoResponse, AlimentoCreate, AlimentoUpdate, AlimentoConNutrientesResponse, AlimentoNutrienteResponse } from '../types/api';
import AlimentoForm from '../components/alimentos/AlimentoForm';
import AlimentoDetail from '../components/alimentos/AlimentoDetail';

interface AlimentosPageProps {
  embedded?: boolean;
}

const AlimentosPage: React.FC<AlimentosPageProps> = ({ embedded = false }) => {
  const [alimentos, setAlimentos] = useState<AlimentoResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filtroGrupo, setFiltroGrupo] = useState<string>('');
  const [selectedAlimento, setSelectedAlimento] = useState<AlimentoResponse | null>(null);
  const [alimentoDetalle, setAlimentoDetalle] = useState<AlimentoConNutrientesResponse | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const { toast } = useToast();

  // Obtener grupos únicos para el filtro
  const gruposUnicos = Array.from(new Set(alimentos.map(a => a.ali_grupo).filter(Boolean)));

  useEffect(() => {
    loadAlimentos();
  }, []);

  const loadAlimentos = async () => {
    setLoading(true);
    try {
      const response = await alimentosRecetasApi.getAlimentos(searchQuery || undefined, 200);
      if (response.success && response.data) {
        setAlimentos(response.data);
      } else {
        toast({
          title: 'Error',
          description: 'No se pudieron cargar los alimentos',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al conectar con el servidor',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    loadAlimentos();
  };

  const handleCreateAlimento = async (alimentoData: AlimentoCreate) => {
    try {
      const response = await alimentosRecetasApi.createAlimento(alimentoData);
      if (response.success) {
        toast({
          title: 'Éxito',
          description: 'Alimento creado correctamente',
        });
        setIsCreateDialogOpen(false);
        loadAlimentos();
      } else {
        toast({
          title: 'Error',
          description: response.error || 'Error al crear el alimento',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al crear el alimento',
        variant: 'destructive',
      });
    }
  };

  const handleUpdateAlimento = async (alimentoData: AlimentoUpdate) => {
    if (!selectedAlimento) return;

    try {
      const response = await alimentosRecetasApi.updateAlimento(selectedAlimento.ali_id, alimentoData);
      if (response.success) {
        toast({
          title: 'Éxito',
          description: 'Alimento actualizado correctamente',
        });
        setIsEditDialogOpen(false);
        setSelectedAlimento(null);
        loadAlimentos();
      } else {
        toast({
          title: 'Error',
          description: response.error || 'Error al actualizar el alimento',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al actualizar el alimento',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteAlimento = async (aliId: number) => {
    if (!confirm('¿Estás seguro de que deseas eliminar este alimento?')) return;

    try {
      const response = await alimentosRecetasApi.deleteAlimento(aliId);
      if (response.success) {
        toast({
          title: 'Éxito',
          description: 'Alimento eliminado correctamente',
        });
        loadAlimentos();
      } else {
        toast({
          title: 'Error',
          description: response.error || 'Error al eliminar el alimento',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al eliminar el alimento',
        variant: 'destructive',
      });
    }
  };

  const loadAlimentoDetalle = async (aliId: number) => {
    try {
      const response = await alimentosRecetasApi.getAlimento(aliId);
      if (response.success && response.data) {
        setAlimentoDetalle(response.data);
        setIsDetailDialogOpen(true);
      } else {
        toast({
          title: 'Error',
          description: 'No se pudieron cargar los detalles del alimento',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al cargar los detalles del alimento',
        variant: 'destructive',
      });
    }
   };

  const handleCreateAlimentoWrapper = async (alimentoData: AlimentoCreate | AlimentoUpdate, nutrientes?: AlimentoNutrienteResponse[]) => {
    try {
      const response = await alimentosRecetasApi.createAlimento(alimentoData as AlimentoCreate);
      if (response.success && response.data && nutrientes && nutrientes.length > 0) {
        // Agregar nutrientes al alimento creado
        for (const nutriente of nutrientes) {
           await alimentosRecetasApi.addNutrienteToAlimento(response.data.ali_id, {
             ali_id: response.data.ali_id,
             nutri_id: nutriente.nutri_id,
             an_cantidad_100: nutriente.an_cantidad_100,
             an_fuente: nutriente.an_fuente
           });
         }
      }

      if (response.success) {
        toast({
          title: 'Éxito',
          description: 'Alimento creado correctamente',
        });
        setIsCreateDialogOpen(false);
        loadAlimentos();
      } else {
        toast({
          title: 'Error',
          description: response.error || 'Error al crear el alimento',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al crear el alimento',
        variant: 'destructive',
      });
    }
  };

  const handleUpdateAlimentoWrapper = async (alimentoData: AlimentoCreate | AlimentoUpdate, nutrientes?: AlimentoNutrienteResponse[]) => {
    if (!selectedAlimento) return;

    try {
      const response = await alimentosRecetasApi.updateAlimento(selectedAlimento.ali_id, alimentoData as AlimentoUpdate);

      if (response.success) {
        toast({
          title: 'Éxito',
          description: 'Alimento actualizado correctamente',
        });
        setIsEditDialogOpen(false);
        setSelectedAlimento(null);
        loadAlimentos();
      } else {
        toast({
          title: 'Error',
          description: response.error || 'Error al actualizar el alimento',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Error al actualizar el alimento',
        variant: 'destructive',
      });
    }
  };

  const alimentosFiltrados = alimentos.filter(alimento => {
    const matchesSearch = !searchQuery ||
      alimento.ali_nombre.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (alimento.ali_nombre_cientifico && alimento.ali_nombre_cientifico.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesGrupo = !filtroGrupo || filtroGrupo === 'all' || alimento.ali_grupo === filtroGrupo;

    return matchesSearch && matchesGrupo;
  });

  return (
    <div className={embedded ? "space-y-6" : "container mx-auto p-6 space-y-6"}>
      {/* Header */}
      {/* Header */}
      {!embedded && (
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestión de Alimentos</h1>
            <p className="text-gray-600 mt-1">Administra el catálogo de alimentos del sistema</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2">
                <Plus className="h-4 w-4" />
                Nuevo Alimento
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Crear Nuevo Alimento</DialogTitle>
                <DialogDescription>
                  Completa la información del nuevo alimento y agrega sus valores nutricionales
                </DialogDescription>
              </DialogHeader>
              <AlimentoForm onSubmit={handleCreateAlimentoWrapper} />
            </DialogContent>
          </Dialog>
        </div>
      )}

      {/* Botón de crear en modo embebido */}
      {embedded && (
        <div className="flex justify-end">
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="flex items-center gap-2 bg-green-600 hover:bg-green-700">
                <Plus className="h-4 w-4" />
                Nuevo Alimento
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Crear Nuevo Alimento</DialogTitle>
                <DialogDescription>
                  Completa la información del nuevo alimento y agrega sus valores nutricionales
                </DialogDescription>
              </DialogHeader>
              <AlimentoForm onSubmit={handleCreateAlimentoWrapper} />
            </DialogContent>
          </Dialog>
        </div>
      )}

      {/* Filtros y búsqueda */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Buscar alimentos por nombre o nombre científico..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Select value={filtroGrupo} onValueChange={setFiltroGrupo}>
                <SelectTrigger className="w-48">
                  <Filter className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="Filtrar por grupo" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos los grupos</SelectItem>
                  {gruposUnicos.map(grupo => (
                    <SelectItem key={grupo} value={grupo!}>
                      {grupo}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button onClick={handleSearch} variant="outline">
                <Search className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de alimentos */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Alimentos ({alimentosFiltrados.length})</span>
            {loading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : alimentosFiltrados.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No se encontraron alimentos</p>
              {searchQuery && (
                <Button
                  variant="link"
                  onClick={() => {
                    setSearchQuery('');
                    setFiltroGrupo('');
                    loadAlimentos();
                  }}
                >
                  Limpiar filtros
                </Button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {alimentosFiltrados.map((alimento) => (
                <Card key={alimento.ali_id} className="hover:shadow-md transition-shadow">
                  <CardContent className="pt-4">
                    <div className="space-y-3">
                      <div>
                        <h3 className="font-semibold text-lg text-gray-900 line-clamp-2">
                          {alimento.ali_nombre}
                        </h3>
                        {alimento.ali_nombre_cientifico && (
                          <p className="text-sm text-gray-600 italic">
                            {alimento.ali_nombre_cientifico}
                          </p>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {alimento.ali_grupo && (
                          <Badge variant="secondary">{alimento.ali_grupo}</Badge>
                        )}
                        <Badge variant="outline">{alimento.ali_unidad || 'g'}</Badge>
                        <Badge variant={alimento.ali_activo ? "default" : "destructive"}>
                          {alimento.ali_activo ? 'Activo' : 'Inactivo'}
                        </Badge>
                      </div>

                      <div className="flex justify-end gap-2 pt-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => loadAlimentoDetalle(alimento.ali_id)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedAlimento(alimento);
                            setIsEditDialogOpen(true);
                          }}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteAlimento(alimento.ali_id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog para editar alimento */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Editar Alimento</DialogTitle>
            <DialogDescription>
              Modifica la información del alimento y sus valores nutricionales
            </DialogDescription>
          </DialogHeader>
          {selectedAlimento && (
            <AlimentoForm
              initialData={selectedAlimento}
              onSubmit={handleUpdateAlimentoWrapper}
              isEdit
              alimentoId={selectedAlimento.ali_id}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Dialog para ver detalle del alimento */}
      <Dialog open={isDetailDialogOpen} onOpenChange={setIsDetailDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Detalle del Alimento</DialogTitle>
            <DialogDescription>
              Visualiza toda la información y valores nutricionales del alimento
            </DialogDescription>
          </DialogHeader>
          {alimentoDetalle && (
            <AlimentoDetail alimento={alimentoDetalle} />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default AlimentosPage;
