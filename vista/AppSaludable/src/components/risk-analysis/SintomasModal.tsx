import { useState } from 'react';
import { X, Calendar, AlertTriangle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Checkbox } from '../ui/checkbox';
import { toast } from 'sonner';
import { apiService } from '../../services/api';

interface Child {
  nin_id: number;
  nin_nombres: string;
  nin_apellidos: string;
}

interface SintomasModalProps {
  open: boolean;
  onClose: () => void;
  child: Child;
}

type Severidad = 'LEVE' | 'MODERADO' | 'SEVERO';

export function SintomasModal({ open, onClose, child }: SintomasModalProps) {
  const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0]);
  const [tipo, setTipo] = useState('');
  const [severidad, setSeveridad] = useState<Severidad>('LEVE');
  const [duracionDias, setDuracionDias] = useState(1);
  const [relacionadoMenu, setRelacionadoMenu] = useState(false);
  const [notas, setNotas] = useState('');
  const [loading, setLoading] = useState(false);

  const sintomasComunes = [
    'Dolor abdominal',
    'Náuseas',
    'Vómito',
    'Diarrea',
    'Estreñimiento',
    'Falta de apetito',
    'Dolor de cabeza',
    'Fatiga',
    'Mareos',
    'Otro'
  ];

  const handleSubmit = async () => {
    if (!tipo.trim()) {
      toast.error('Por favor ingresa el tipo de síntoma');
      return;
    }

    try {
      setLoading(true);

      const response = await apiService.registrarSintoma({
        nin_id: child.nin_id,
        fecha,
        tipo: tipo.trim(),
        severidad,
        duracion_dias: duracionDias,
        relacionado_menu: relacionadoMenu,
        notas: notas || null
      });

      if (!response.success) {
        throw new Error(response.error || 'Error al registrar síntoma');
      }

      toast.success('Síntoma registrado exitosamente');
      onClose();

      // Reset form
      setFecha(new Date().toISOString().split('T')[0]);
      setTipo('');
      setSeveridad('LEVE');
      setDuracionDias(1);
      setRelacionadoMenu(false);
      setNotas('');

    } catch (error: any) {
      console.error('Error registrando síntoma:', error);
      toast.error(error.response?.data?.detail || 'Error al registrar síntoma');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Registrar Síntoma - {child.nin_nombres}</span>
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
              <span>Fecha del Síntoma</span>
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

          {/* Tipo de síntoma */}
          <div className="space-y-3">
            <Label htmlFor="tipo">Tipo de Síntoma</Label>
            <div className="grid grid-cols-2 gap-2 mb-3">
              {sintomasComunes.map((sintoma) => (
                <Button
                  key={sintoma}
                  type="button"
                  variant={tipo === sintoma ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setTipo(sintoma)}
                  className="justify-start"
                >
                  {sintoma}
                </Button>
              ))}
            </div>
            <Input
              id="tipo"
              value={tipo}
              onChange={(e) => setTipo(e.target.value)}
              placeholder="O escribe otro síntoma..."
            />
          </div>

          {/* Severidad */}
          <div className="space-y-3">
            <Label className="flex items-center space-x-2">
              <AlertTriangle size={16} />
              <span>Severidad</span>
            </Label>
            <RadioGroup value={severidad} onValueChange={(value) => setSeveridad(value as Severidad)}>
              <div className="grid grid-cols-3 gap-3">
                <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="LEVE" id="leve" />
                  <Label htmlFor="leve" className="cursor-pointer flex-1">
                    <p className="font-medium">Leve</p>
                    <p className="text-xs text-muted-foreground">Molestia menor</p>
                  </Label>
                </div>

                <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="MODERADO" id="moderado" />
                  <Label htmlFor="moderado" className="cursor-pointer flex-1">
                    <p className="font-medium">Moderado</p>
                    <p className="text-xs text-muted-foreground">Afecta actividades</p>
                  </Label>
                </div>

                <div className="flex items-center space-x-2 p-3 border rounded-lg hover:bg-muted/50 cursor-pointer">
                  <RadioGroupItem value="SEVERO" id="severo" />
                  <Label htmlFor="severo" className="cursor-pointer flex-1">
                    <p className="font-medium">Severo</p>
                    <p className="text-xs text-muted-foreground">Requiere atención</p>
                  </Label>
                </div>
              </div>
            </RadioGroup>
          </div>

          {/* Duración */}
          <div className="space-y-2">
            <Label htmlFor="duracion">Duración (días)</Label>
            <Input
              id="duracion"
              type="number"
              min={1}
              max={30}
              value={duracionDias}
              onChange={(e) => setDuracionDias(parseInt(e.target.value) || 1)}
            />
          </div>

          {/* Relacionado con menú */}
          <div className="flex items-center space-x-2 p-4 border rounded-lg">
            <Checkbox
              id="relacionado"
              checked={relacionadoMenu}
              onCheckedChange={(checked) => setRelacionadoMenu(checked as boolean)}
            />
            <Label htmlFor="relacionado" className="cursor-pointer">
              ¿Relacionado con el plan de comidas?
            </Label>
          </div>

          {/* Notas */}
          <div className="space-y-2">
            <Label htmlFor="notas">Notas Adicionales (opcional)</Label>
            <Textarea
              id="notas"
              value={notas}
              onChange={(e) => setNotas(e.target.value)}
              placeholder="Detalles adicionales sobre el síntoma..."
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
            {loading ? 'Guardando...' : 'Guardar Síntoma'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
