import React, { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Switch } from '../ui/switch';
import { AlimentoCreate, AlimentoUpdate, AlimentoResponse, AlimentoNutrienteResponse } from '../../types/api';
import { NutrientesManager } from '../NutrientesManager';
import { alimentosRecetasApi } from '../../services/alimentosRecetasApi';
import { toast } from 'sonner';

interface AlimentoFormProps {
  initialData?: AlimentoResponse;
  onSubmit: (data: AlimentoCreate | AlimentoUpdate, nutrientes?: AlimentoNutrienteResponse[]) => void;
  isEdit?: boolean;
  alimentoId?: number;
}

const GRUPOS_ALIMENTOS = [
  'Cereales y derivados',
  'Verduras y hortalizas',
  'Frutas',
  'Lácteos y derivados',
  'Carnes y derivados',
  'Pescados y mariscos',
  'Huevos',
  'Legumbres',
  'Frutos secos',
  'Aceites y grasas',
  'Azúcares y dulces',
  'Bebidas',
  'Condimentos y especias',
  'Otros'
];

const UNIDADES = [
  'g',
  'ml',
  'kg',
  'l',
  'unidad',
  'taza',
  'cucharada',
  'cucharadita',
  'porción'
];

const AlimentoForm: React.FC<AlimentoFormProps> = ({
  initialData,
  onSubmit,
  isEdit = false,
  alimentoId
}) => {
  const [formData, setFormData] = useState({
    ali_nombre: initialData?.ali_nombre || '',
    ali_nombre_cientifico: initialData?.ali_nombre_cientifico || '',
    ali_grupo: initialData?.ali_grupo || '',
    ali_unidad: initialData?.ali_unidad || 'g',
    ali_activo: initialData?.ali_activo ?? true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [nutrientes, setNutrientes] = useState<AlimentoNutrienteResponse[]>([]);

  // Cargar nutrientes existentes cuando se edita un alimento
  useEffect(() => {
    const loadNutrientesExistentes = async () => {
      if (isEdit && alimentoId) {
        try {
          const response = await alimentosRecetasApi.getAlimento(alimentoId);
          if (response.success && response.data && response.data.nutrientes) {
            // Convertir los nutrientes del formato de respuesta al formato esperado
            const nutrientesFormateados = response.data.nutrientes.map(nutriente => ({
              ali_id: alimentoId,
              nutri_id: nutriente.nutri_id,
              an_cantidad_100: nutriente.an_cantidad_100,
              an_fuente: nutriente.an_fuente
            }));
            setNutrientes(nutrientesFormateados);
          }
        } catch (error) {
          console.error('Error al cargar nutrientes existentes:', error);
          toast.error('Error al cargar los nutrientes del alimento');
        }
      }
    };

    loadNutrientesExistentes();
  }, [isEdit, alimentoId]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.ali_nombre.trim()) {
      newErrors.ali_nombre = 'El nombre del alimento es obligatorio';
    }

    if (formData.ali_nombre.length > 200) {
      newErrors.ali_nombre = 'El nombre no puede exceder 200 caracteres';
    }

    if (formData.ali_nombre_cientifico && formData.ali_nombre_cientifico.length > 200) {
      newErrors.ali_nombre_cientifico = 'El nombre científico no puede exceder 200 caracteres';
    }

    if (formData.ali_grupo && formData.ali_grupo.length > 100) {
      newErrors.ali_grupo = 'El grupo no puede exceder 100 caracteres';
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
      ali_nombre_cientifico: formData.ali_nombre_cientifico || undefined,
      ali_grupo: (formData.ali_grupo && formData.ali_grupo !== 'placeholder') ? formData.ali_grupo : undefined,
    };

    onSubmit(submitData, nutrientes);
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Limpiar error del campo cuando el usuario empiece a escribir
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Nombre del alimento */}
        <div className="md:col-span-2">
          <Label htmlFor="ali_nombre">
            Nombre del alimento <span className="text-red-500">*</span>
          </Label>
          <Input
            id="ali_nombre"
            value={formData.ali_nombre}
            onChange={(e) => handleInputChange('ali_nombre', e.target.value)}
            placeholder="Ej: Arroz blanco cocido"
            className={errors.ali_nombre ? 'border-red-500' : ''}
          />
          {errors.ali_nombre && (
            <p className="text-sm text-red-500 mt-1">{errors.ali_nombre}</p>
          )}
        </div>

        {/* Nombre científico */}
        <div className="md:col-span-2">
          <Label htmlFor="ali_nombre_cientifico">Nombre científico</Label>
          <Input
            id="ali_nombre_cientifico"
            value={formData.ali_nombre_cientifico}
            onChange={(e) => handleInputChange('ali_nombre_cientifico', e.target.value)}
            placeholder="Ej: Oryza sativa"
            className={errors.ali_nombre_cientifico ? 'border-red-500' : ''}
          />
          {errors.ali_nombre_cientifico && (
            <p className="text-sm text-red-500 mt-1">{errors.ali_nombre_cientifico}</p>
          )}
        </div>

        {/* Grupo alimentario */}
        <div>
          <Label htmlFor="ali_grupo">Grupo alimentario</Label>
          <Select
            value={formData.ali_grupo}
            onValueChange={(value: string) => handleInputChange('ali_grupo', value)}
          >
            <SelectTrigger className={errors.ali_grupo ? 'border-red-500' : ''}>
              <SelectValue placeholder="Seleccionar grupo" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="placeholder">Seleccionar grupo</SelectItem>
              {GRUPOS_ALIMENTOS.map((grupo) => (
                <SelectItem key={grupo} value={grupo}>
                  {grupo}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.ali_grupo && (
            <p className="text-sm text-red-500 mt-1">{errors.ali_grupo}</p>
          )}
        </div>

        {/* Unidad de medida */}
        <div>
          <Label htmlFor="ali_unidad">Unidad de medida</Label>
          <Select
            value={formData.ali_unidad}
            onValueChange={(value: string) => handleInputChange('ali_unidad', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Seleccionar unidad" />
            </SelectTrigger>
            <SelectContent>
              {UNIDADES.map((unidad) => (
                <SelectItem key={unidad} value={unidad}>
                  {unidad}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Estado activo */}
        <div className="md:col-span-2 flex items-center space-x-2">
          <Switch
            id="ali_activo"
            checked={formData.ali_activo}
            onCheckedChange={(checked: boolean) => handleInputChange('ali_activo', checked)}
          />
          <Label htmlFor="ali_activo">Alimento activo</Label>
        </div>
      </div>

      {/* Gestión de nutrientes */}
      <div className="border-t pt-6">
        <NutrientesManager
          alimentoId={alimentoId}
          nutrientes={nutrientes}
          onNutrientesChange={setNutrientes}
          disabled={false}
        />
      </div>

      {/* Botones de acción */}
      <div className="flex justify-end space-x-2 pt-4">
        <Button type="submit">
          {isEdit ? 'Actualizar' : 'Crear'} Alimento
        </Button>
      </div>
    </form>
  );
};

export default AlimentoForm;
