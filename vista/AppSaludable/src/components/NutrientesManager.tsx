import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Plus, Trash2, Edit } from 'lucide-react';
import { toast } from 'sonner';
import { alimentosRecetasApi } from '../services/alimentosRecetasApi';
import { NutrienteResponse, AlimentoNutrienteResponse } from '../types/api';

interface NutrientesManagerProps {
  nutrientes: AlimentoNutrienteResponse[];
  onNutrientesChange: (nutrientes: AlimentoNutrienteResponse[]) => void;
  alimentoId?: number;
  disabled?: boolean;
}

interface NutrienteFormData {
  nutri_id: number;
  an_cantidad_100: number;
  an_fuente?: string;
}

export const NutrientesManager: React.FC<NutrientesManagerProps> = ({
  nutrientes,
  onNutrientesChange,
  alimentoId,
  disabled = false,
}) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [availableNutrientes, setAvailableNutrientes] = useState<NutrienteResponse[]>([]);
  const [editingNutriente, setEditingNutriente] = useState<AlimentoNutrienteResponse | null>(null);
  const [formData, setFormData] = useState<NutrienteFormData>({
    nutri_id: 0,
    an_cantidad_100: 0,
    an_fuente: '',
  });
  const [isLoading, setIsLoading] = useState(false);

  // Cargar nutrientes disponibles
  useEffect(() => {
    loadNutrientes();
  }, []);

  const loadNutrientes = async () => {
    try {
      const response = await alimentosRecetasApi.getNutrientes();
      if (response.success && response.data) {
        setAvailableNutrientes(response.data);
      } else {
        toast.error('Error al cargar nutrientes');
      }
    } catch (error) {
      toast.error('Error al cargar nutrientes');
    }
  };

  const handleOpenDialog = (nutriente?: AlimentoNutrienteResponse) => {
    if (nutriente) {
      setEditingNutriente(nutriente);
      setFormData({
        nutri_id: nutriente.nutri_id,
        an_cantidad_100: nutriente.an_cantidad_100,
        an_fuente: nutriente.an_fuente || '',
      });
    } else {
      setEditingNutriente(null);
      setFormData({
        nutri_id: 0,
        an_cantidad_100: 0,
        an_fuente: '',
      });
    }
    setIsDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation(); // Evitar que el evento se propague al formulario padre

    if (formData.nutri_id === 0) {
      toast.error('Selecciona un nutriente');
      return;
    }

    if (formData.an_cantidad_100 <= 0) {
      toast.error('La cantidad debe ser mayor a 0');
      return;
    }

    // Verificar si el nutriente ya existe (solo para nuevos)
    if (!editingNutriente) {
      const exists = nutrientes.some(n => n.nutri_id === formData.nutri_id);
      if (exists) {
        toast.error('Este nutriente ya está agregado');
        return;
      }
    }

    setIsLoading(true);

    try {
      // Solo hacer llamadas a la API si el alimento ya existe (tiene alimentoId)
      if (alimentoId) {
        if (editingNutriente) {
          // Editar nutriente existente - eliminar y agregar de nuevo
          await alimentosRecetasApi.deleteNutrienteFromAlimento(alimentoId, editingNutriente.nutri_id);
          await alimentosRecetasApi.addNutrienteToAlimento(alimentoId, {
            ali_id: alimentoId,
            ...formData,
          });
        } else {
          // Agregar nuevo nutriente a alimento existente
          await alimentosRecetasApi.addNutrienteToAlimento(alimentoId, {
            ali_id: alimentoId,
            ...formData,
          });
        }
      }

      // Actualizar la lista local (tanto para alimentos existentes como nuevos)
      const newNutriente: AlimentoNutrienteResponse = {
        ali_id: alimentoId || 0,
        nutri_id: formData.nutri_id,
        an_cantidad_100: formData.an_cantidad_100,
        an_fuente: formData.an_fuente,
      };

      let updatedNutrientes;
      if (editingNutriente) {
        updatedNutrientes = nutrientes.map(n =>
          n.nutri_id === editingNutriente.nutri_id ? newNutriente : n
        );
      } else {
        updatedNutrientes = [...nutrientes, newNutriente];
      }

      onNutrientesChange(updatedNutrientes);
      setIsDialogOpen(false);

      // Mensaje diferente según si es un alimento nuevo o existente
      if (alimentoId) {
        toast.success(editingNutriente ? 'Nutriente actualizado' : 'Nutriente agregado');
      } else {
        toast.success(editingNutriente ? 'Nutriente actualizado en el formulario' : 'Nutriente agregado al formulario');
      }
    } catch (error) {
      toast.error('Error al guardar nutriente');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (nutriente: AlimentoNutrienteResponse) => {
    // Solo hacer llamada a la API si el alimento ya existe
    if (alimentoId) {
      try {
        await alimentosRecetasApi.deleteNutrienteFromAlimento(alimentoId, nutriente.nutri_id);
        toast.success('Nutriente eliminado');
      } catch (error) {
        toast.error('Error al eliminar nutriente');
        return;
      }
    } else {
      // Para alimentos nuevos, solo mostrar mensaje local
      toast.success('Nutriente eliminado del formulario');
    }

    const updatedNutrientes = nutrientes.filter(n => n.nutri_id !== nutriente.nutri_id);
    onNutrientesChange(updatedNutrientes);
  };

  const getNutrienteNombre = (nutriId: number) => {
    return availableNutrientes.find(n => n.nutri_id === nutriId)?.nutri_nombre || 'Desconocido';
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Label className="text-sm font-medium">Información Nutricional</Label>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => handleOpenDialog()}
              disabled={disabled}
            >
              <Plus className="h-4 w-4 mr-2" />
              Agregar Nutriente
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingNutriente ? 'Editar Nutriente' : 'Agregar Nutriente'}
              </DialogTitle>
              <DialogDescription>
                {editingNutriente
                  ? 'Modifica la cantidad y fuente del nutriente seleccionado'
                  : 'Agrega información nutricional para este alimento (cantidad por 100g/100ml)'}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="nutriente">Nutriente</Label>
                <Select
                  value={formData.nutri_id.toString()}
                  onValueChange={(value: string) => setFormData({ ...formData, nutri_id: parseInt(value) })}
                  disabled={!!editingNutriente}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecciona un nutriente" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableNutrientes.map((nutriente) => (
                      <SelectItem key={nutriente.nutri_id} value={nutriente.nutri_id.toString()}>
                        {nutriente.nutri_nombre} ({nutriente.nutri_unidad})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="cantidad">Cantidad por 100g/100ml</Label>
                <Input
                  id="cantidad"
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.an_cantidad_100}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, an_cantidad_100: parseFloat(e.target.value) || 0 })}
                  required
                />
              </div>

              <div>
                <Label htmlFor="fuente">Fuente (opcional)</Label>
                <Input
                  id="fuente"
                  value={formData.an_fuente}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFormData({ ...formData, an_fuente: e.target.value })}
                  placeholder="Ej: USDA, Tabla de composición..."
                />
              </div>

              <div className="flex justify-end space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsDialogOpen(false)}
                  disabled={isLoading}
                >
                  Cancelar
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? 'Guardando...' : editingNutriente ? 'Actualizar' : 'Agregar'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {nutrientes.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nutriente</TableHead>
              <TableHead>Cantidad/100g</TableHead>
              <TableHead>Unidad</TableHead>
              <TableHead>Fuente</TableHead>
              <TableHead className="w-20">Acciones</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {nutrientes.map((nutriente) => {
              const nutrienteInfo = availableNutrientes.find(n => n.nutri_id === nutriente.nutri_id);
              return (
                <TableRow key={nutriente.nutri_id}>
                  <TableCell>{nutrienteInfo?.nutri_nombre || getNutrienteNombre(nutriente.nutri_id)}</TableCell>
                  <TableCell>{nutriente.an_cantidad_100}</TableCell>
                  <TableCell>{nutrienteInfo?.nutri_unidad || '-'}</TableCell>
                  <TableCell>{nutriente.an_fuente || '-'}</TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={(e: React.MouseEvent) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleOpenDialog(nutriente);
                        }}
                        disabled={disabled}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={(e: React.MouseEvent) => {
                          e.preventDefault();
                          e.stopPropagation();
                          handleDelete(nutriente);
                        }}
                        disabled={disabled}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      ) : (
        <div className="text-center py-8 text-gray-500">
          No hay nutrientes agregados
        </div>
      )}
    </div>
  );
};
