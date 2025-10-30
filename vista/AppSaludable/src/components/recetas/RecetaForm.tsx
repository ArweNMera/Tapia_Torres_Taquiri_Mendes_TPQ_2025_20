import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Switch } from '../ui/switch';
import { RecetaCreate, RecetaUpdate, RecetaResponse } from '../../types/api';

interface RecetaFormProps {
  initialData?: RecetaResponse;
  onSubmit: (data: RecetaCreate | RecetaUpdate) => void;
  isEdit?: boolean;
}

const RecetaForm: React.FC<RecetaFormProps> = ({
  initialData,
  onSubmit,
  isEdit = false
}) => {
  const [formData, setFormData] = useState({
    rec_nombre: initialData?.rec_nombre || '',
    rec_instrucciones: initialData?.rec_instrucciones || '',
    rec_activo: initialData?.rec_activo ?? true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

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
    };

    onSubmit(submitData);
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
      <div className="space-y-4">
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
      </div>

      {/* Botones de acción */}
      <div className="flex justify-end space-x-2 pt-4">
        <Button type="submit">
          {isEdit ? 'Actualizar' : 'Crear'} Receta
        </Button>
      </div>
    </form>
  );
};

export default RecetaForm;
