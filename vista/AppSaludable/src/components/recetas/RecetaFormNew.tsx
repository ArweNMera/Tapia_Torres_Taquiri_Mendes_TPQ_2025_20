import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Switch } from '../ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { RecetaCreate, RecetaUpdate, RecetaResponse } from '../../types/api';
import { alimentosRecetasApi } from '../../services/alimentosRecetasApi';
import { Search, Plus, X, Calculator, Trash2 } from 'lucide-react';
import { useToast } from '../ui/use-toast';

interface Ingrediente {
  ali_id: number;
  ali_nombre: string;
  cantidad: number;
  unidad: string;
}

interface RecetaFormProps {
  initialData?: RecetaResponse;
  onSubmit: (data: any) => void;
  isEdit?: boolean;
}

const RecetaFormNew: React.FC<RecetaFormProps> = ({
  initialData,
  onSubmit,
  isEdit = false
}) => {
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    rec_nombre: initialData?.rec_nombre || '',
    rec_instrucciones: initialData?.rec_instrucciones || '',
    rec_activo: initialData?.rec_activo ?? true,
  });

  const [ingredientes, setIngredientes] = useState<Ingrediente[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const [selectedAlimento, setSelectedAlimento] = useState<any>(null);
  const [cantidad, setCantidad] = useState<string>('');
  const [unidad, setUnidad] = useState<string>('g');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isInputFocused, setIsInputFocused] = useState(false);

  // Cargar ingredientes si estamos editando
  useEffect(() => {
    if (isEdit && initialData?.rec_id) {
      loadIngredientes();
    }
  }, [isEdit, initialData]);

  const loadIngredientes = async () => {
    if (!initialData?.rec_id) return;

    try {
      const response = await alimentosRecetasApi.getReceta(initialData.rec_id);
      if (response.data?.ingredientes) {
        const ings = response.data.ingredientes.map((ing: any) => ({
          ali_id: ing.ali_id,
          ali_nombre: ing.ali_nombre || `Alimento ${ing.ali_id}`,
          cantidad: ing.ri_cantidad,
          unidad: ing.ri_unidad
        }));
        setIngredientes(ings);
      }
    } catch (error) {
      console.error('Error cargando ingredientes:', error);
    }
  };

  // Buscar alimentos con debounce
  useEffect(() => {
    if (searchTerm.length < 2) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setSearching(true);
        const response = await alimentosRecetasApi.getAlimentos(searchTerm, 10);
        setSearchResults(response.data || []);
      } catch (error) {
        console.error('Error buscando alimentos:', error);
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const ingredienteContainer = document.querySelector('#ingrediente-container');
      if (ingredienteContainer && !ingredienteContainer.contains(target)) {
        setIsInputFocused(false);
        setSearchResults([]);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectAlimento = (alimento: any) => {
    setSelectedAlimento(alimento);
    setSearchTerm(alimento.ali_nombre);
    setUnidad(alimento.ali_unidad || 'g');
    setSearchResults([]);
    setIsInputFocused(false); // Cerrar el dropdown
    // Focus en el campo de cantidad para mejor UX
    setTimeout(() => {
      document.getElementById('cantidad')?.focus();
    }, 100);
  };

  const handleAgregarIngrediente = () => {
    if (!selectedAlimento && searchTerm.trim()) {
      // Si no hay alimento seleccionado pero hay texto, crear uno temporal
      const tempId = -Date.now(); // ID temporal negativo
      const nuevoIngrediente = {
        ali_id: tempId,
        ali_nombre: searchTerm.trim(),
        cantidad: parseFloat(cantidad) || 0,
        unidad
      };

      if (nuevoIngrediente.cantidad <= 0) {
        toast({
          title: 'Error',
          description: 'Ingresa una cantidad válida',
          variant: 'destructive'
        });
        return;
      }

      setIngredientes([...ingredientes, nuevoIngrediente]);
      setSearchTerm('');
      setCantidad('');
      setUnidad('g');
      setSelectedAlimento(null);

      toast({
        title: 'Ingrediente agregado',
        description: `"${nuevoIngrediente.ali_nombre}" agregado correctamente`
      });
      return;
    }

    if (!selectedAlimento) {
      toast({
        title: 'Error',
        description: 'Escribe el nombre del ingrediente',
        variant: 'destructive'
      });
      return;
    }

    const cantidadNum = parseFloat(cantidad);
    if (!cantidadNum || cantidadNum <= 0) {
      toast({
        title: 'Error',
        description: 'Ingresa una cantidad válida',
        variant: 'destructive'
      });
      return;
    }

    // Verificar si ya existe
    if (ingredientes.some(ing => ing.ali_id === selectedAlimento.ali_id)) {
      toast({
        title: 'Advertencia',
        description: 'Este ingrediente ya fue agregado',
        variant: 'destructive'
      });
      return;
    }

    setIngredientes([...ingredientes, {
      ali_id: selectedAlimento.ali_id,
      ali_nombre: selectedAlimento.ali_nombre,
      cantidad: cantidadNum,
      unidad
    }]);

    // Limpiar formulario
    setSelectedAlimento(null);
    setSearchTerm('');
    setCantidad('');
    setUnidad('g');

    toast({
      title: 'Éxito',
      description: 'Ingrediente agregado',
    });
  };

  const handleEliminarIngrediente = (ali_id: number) => {
    setIngredientes(ingredientes.filter(ing => ing.ali_id !== ali_id));
    toast({
      title: 'Ingrediente eliminado',
    });
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.rec_nombre.trim()) {
      newErrors.rec_nombre = 'El nombre de la receta es obligatorio';
    }

    if (formData.rec_nombre.length > 200) {
      newErrors.rec_nombre = 'El nombre no puede exceder 200 caracteres';
    }

    if (formData.rec_instrucciones && formData.rec_instrucciones.length > 2000) {
      newErrors.rec_instrucciones = 'Las instrucciones no pueden exceder 2000 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const submitData = {
      ...formData,
      rec_instrucciones: formData.rec_instrucciones || undefined,
      ingredientes: ingredientes.map(ing => ({
        ali_id: ing.ali_id > 0 ? ing.ali_id : undefined,
        ali_nombre: ing.ali_nombre,
        cantidad: ing.cantidad,
        unidad: ing.unidad
      }))
    };

    onSubmit(submitData);
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Información básica */}
      <Card>
        <CardHeader>
          <CardTitle>Información Básica</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Nombre de la receta */}
          <div>
            <Label htmlFor="rec_nombre">
              Nombre de la receta <span className="text-red-500">*</span>
            </Label>
            <Input
              id="rec_nombre"
              value={formData.rec_nombre}
              onChange={(e) => handleInputChange('rec_nombre', e.target.value)}
              placeholder="Ej: Arroz con pollo"
              className={errors.rec_nombre ? 'border-red-500' : ''}
            />
            {errors.rec_nombre && (
              <p className="text-sm text-red-500 mt-1">{errors.rec_nombre}</p>
            )}
          </div>

          {/* Instrucciones */}
          <div>
            <Label htmlFor="rec_instrucciones">Instrucciones de preparación</Label>
            <Textarea
              id="rec_instrucciones"
              value={formData.rec_instrucciones}
              onChange={(e) => handleInputChange('rec_instrucciones', e.target.value)}
              placeholder="Describe paso a paso cómo preparar la receta..."
              rows={6}
              className={errors.rec_instrucciones ? 'border-red-500' : ''}
            />
            {errors.rec_instrucciones && (
              <p className="text-sm text-red-500 mt-1">{errors.rec_instrucciones}</p>
            )}
            <p className="text-sm text-gray-500 mt-1">
              {formData.rec_instrucciones.length}/2000 caracteres
            </p>
          </div>

          {/* Estado activo */}
          <div className="flex items-center space-x-2">
            <Switch
              id="rec_activo"
              checked={formData.rec_activo}
              onCheckedChange={(checked: boolean) => handleInputChange('rec_activo', checked)}
            />
            <Label htmlFor="rec_activo">Receta activa</Label>
          </div>
        </CardContent>
      </Card>

      {/* Ingredientes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="w-5 h-5" />
            Ingredientes ({ingredientes.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Formulario para agregar ingredientes */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-3 p-4 bg-gray-50 rounded-lg">
            <div className="md:col-span-5">
              <Label htmlFor="ingrediente">Ingrediente</Label>
              <div id="ingrediente-container" className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400 z-10" />
                <Input
                  id="ingrediente"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onFocus={() => setIsInputFocused(true)}
                  placeholder="Buscar ingrediente... (min 2 letras)"
                  className="pl-10"
                  autoComplete="off"
                />

                {/* Dropdown de resultados - aparece ENCIMA del input */}
                {isInputFocused && searching && searchTerm.length >= 2 && (
                  <div className="absolute left-0 right-0 bottom-full mb-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto z-50">
                    <div className="p-2 text-sm text-gray-500 text-center">
                      Buscando...
                    </div>
                  </div>
                )}

                {isInputFocused && !searching && searchResults.length > 0 && searchTerm.length >= 2 && (
                  <div className="absolute left-0 right-0 bottom-full mb-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto z-50">
                    {searchResults.map((alimento) => (
                      <button
                        key={alimento.ali_id}
                        type="button"
                        onClick={() => handleSelectAlimento(alimento)}
                        className="w-full text-left px-3 py-2 hover:bg-blue-50 focus:bg-blue-50 focus:outline-none border-b last:border-b-0"
                      >
                        <div className="font-medium text-sm">{alimento.ali_nombre}</div>
                        <div className="text-xs text-gray-500">
                          {alimento.ali_grupo} • {alimento.ali_unidad}
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {isInputFocused && !searching && searchResults.length === 0 && searchTerm.length >= 2 && (
                  <div className="absolute left-0 right-0 bottom-full mb-1 bg-white border border-gray-300 rounded-md shadow-lg z-50">
                    <div className="p-3 text-sm text-gray-500 text-center">
                      No se encontraron ingredientes
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="md:col-span-3">
              <Label htmlFor="cantidad">Cantidad</Label>
              <Input
                id="cantidad"
                type="number"
                step="0.01"
                min="0"
                value={cantidad}
                onChange={(e) => setCantidad(e.target.value)}
                placeholder="100"
              />
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="unidad">Unidad</Label>
              <select
                id="unidad"
                value={unidad}
                onChange={(e) => setUnidad(e.target.value)}
                className="w-full h-10 rounded-md border border-input bg-background px-3 py-2"
              >
                <option value="g">gramos (g)</option>
                <option value="ml">mililitros (ml)</option>
                <option value="unidad">unidades</option>
                <option value="taza">tazas</option>
                <option value="cdta">cucharadita</option>
                <option value="cda">cucharada</option>
              </select>
            </div>

            <div className="md:col-span-2 flex items-end">
              <Button
                type="button"
                onClick={handleAgregarIngrediente}
                className="w-full"
                style={{ backgroundColor: '#16a34a', color: 'white' }}
              >
                <Plus className="w-4 h-4 mr-1" />
                Agregar
              </Button>
            </div>
          </div>

          {/* Lista de ingredientes */}
          {ingredientes.length > 0 ? (
            <div className="space-y-2">
              {ingredientes.map((ingrediente, index) => (
                <div
                  key={`${ingrediente.ali_id}-${index}`}
                  className="flex items-center justify-between p-3 border rounded-lg bg-white hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <p className="font-medium text-sm">{ingrediente.ali_nombre}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-semibold text-blue-600">
                      {ingrediente.cantidad} {ingrediente.unidad}
                    </span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEliminarIngrediente(ingrediente.ali_id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Calculator className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>No hay ingredientes agregados</p>
              <p className="text-sm">Agrega ingredientes para calcular la información nutricional</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Botones de acción */}
      <div className="flex justify-end space-x-2 pt-4">
        <Button
          type="submit"
          style={{ backgroundColor: '#2563eb', color: 'white' }}
        >
          {isEdit ? 'Actualizar' : 'Crear'} Receta
        </Button>
      </div>
    </form>
  );
};

export default RecetaFormNew;
