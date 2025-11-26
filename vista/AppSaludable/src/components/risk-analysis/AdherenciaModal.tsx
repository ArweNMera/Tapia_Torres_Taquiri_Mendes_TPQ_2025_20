import { useState } from 'react';
import { X, Calendar, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Slider } from '../ui/slider';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { toast } from 'sonner';
import { apiService } from '../../services/api';

interface Child {
  nin_id: number;
  nin_nombres: string;
  nin_apellidos: string;
}

interface AdherenciaModalProps {
  open: boolean;
  onClose: () => void;
  child: Child;
}

type Estado = 'OK' | 'PARCIAL' | 'NO';
type Dificultad = 'NINGUNA' | 'BAJA' | 'MEDIA' | 'ALTA';

export function AdherenciaModal({ open, onClose, child }: AdherenciaModalProps) {
  const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0]);
  const [estado, setEstado] = useState<Estado>('OK');
  const [porcentaje, setPorcentaje] = useState([75]);
  const [dificultad, setDificultad] = useState<Dificultad>('NINGUNA');
  const [comentario, setComentario] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);

      const response = await apiService.registrarAdherencia({
        nin_id: child.nin_id,
        men_id: 1, // TODO: Obtener del plan activo
        mei_id: null,
        fecha,
        estado,
        porcentaje: porcentaje[0],
        dificultad,
        comentario: comentario || null
      });

      if (!response.success) {
        throw new Error(response.error || 'Error al registrar adherencia');
      }

      toast.success('Adherencia registrada exitosamente');
      onClose();

      // Reset form
      setFecha(new Date().toISOString().split('T')[0]);
      setEstado('OK');
      setPorcentaje([75]);
      setDificultad('NINGUNA');
      setComentario('');

    } catch (error: any) {
      console.error('Error registrando adherencia:', error);
      toast.error(error.response?.data?.detail || 'Error al registrar adherencia');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Registrar Adherencia - {child.nin_nombres}</span>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X size={20} />
            </Button>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Fecha */}
          <div className="space-y-2">
            <Label htmlFor="fecha" className="flex items-center space-x-2">
              <Calendar size={16} />
              <span>Fecha</span>
            </Label>
            <input
              id="fecha"
              type="date"
              value={fecha}
              onChange={(e) => setFecha(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>

          {/* Estado */}
          <div className="space-y-3">
            <Label>Estado de Cumplimiento</Label>
            <RadioGroup value={estado} onValueChange={(value) => setEstado(value as Estado)}>
              <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                <RadioGroupItem value="OK" id="ok" />
                <Label htmlFor="ok" className="flex items-center space-x-2 cursor-pointer flex-1">
                  <CheckCircle className="text-green-500" size={20} />
                  <div>
                    <p className="font-medium">Completado</p>
                    <p className="text-sm text-muted-foreground">Siguió el plan completamente</p>
                  </div>
                </Label>
              </div>

              <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                <RadioGroupItem value="PARCIAL" id="parcial" />
                <Label htmlFor="parcial" className="flex items-center space-x-2 cursor-pointer flex-1">
                  <AlertCircle className="text-yellow-500" size={20} />
                  <div>
                    <p className="font-medium">Parcial</p>
                    <p className="text-sm text-muted-foreground">Siguió el plan parcialmente</p>
                  </div>
                </Label>
              </div>

              <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                <RadioGroupItem value="NO" id="no" />
                <Label htmlFor="no" className="flex items-center space-x-2 cursor-pointer flex-1">
                  <XCircle className="text-red-500" size={20} />
                  <div>
                    <p className="font-medium">No Completado</p>
                    <p className="text-sm text-muted-foreground">No siguió el plan</p>
                  </div>
                </Label>
              </div>
            </RadioGroup>
          </div>

          {/* Porcentaje */}
          <div className="space-y-3">
            <Label>Porcentaje de Adherencia: {porcentaje[0]}%</Label>
            <Slider
              value={porcentaje}
              onValueChange={setPorcentaje}
              min={0}
              max={100}
              step={5}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Dificultad */}
          <div className="space-y-3">
            <Label>Nivel de Dificultad</Label>
            <RadioGroup value={dificultad} onValueChange={(value) => setDificultad(value as Dificultad)}>
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="NINGUNA" id="ninguna" />
                  <Label htmlFor="ninguna" className="cursor-pointer">Ninguna</Label>
                </div>
                <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="BAJA" id="baja" />
                  <Label htmlFor="baja" className="cursor-pointer">Baja</Label>
                </div>
                <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="MEDIA" id="media" />
                  <Label htmlFor="media" className="cursor-pointer">Media</Label>
                </div>
                <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="ALTA" id="alta" />
                  <Label htmlFor="alta" className="cursor-pointer">Alta</Label>
                </div>
              </div>
            </RadioGroup>
          </div>

          {/* Comentarios */}
          <div className="space-y-2">
            <Label htmlFor="comentario">Comentarios (opcional)</Label>
            <Textarea
              id="comentario"
              value={comentario}
              onChange={(e) => setComentario(e.target.value)}
              placeholder="Observaciones sobre la adherencia..."
              rows={4}
            />
          </div>
        </div>

        {/* Acciones */}
        <div className="flex justify-end space-x-3 pt-4 border-t">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancelar
          </Button>
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? 'Guardando...' : 'Guardar Adherencia'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
