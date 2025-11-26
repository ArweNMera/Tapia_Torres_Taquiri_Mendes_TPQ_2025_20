import { useState, useEffect } from 'react';
import { X, Calendar, AlertTriangle, History } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Checkbox } from '../ui/checkbox';
import { Badge } from '../ui/badge';
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

interface SintomaHistorial {
  sin_id: number;
  sin_fecha: string;
  sin_tipo: string;
  sin_severidad: string;
  sin_duracion_dias: number;
  sin_relacionado_menu: boolean;
}

export function SintomasModal({ open, onClose, child }: SintomasModalProps) {
  const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0]);
  const [tipo, setTipo] = useState('');
  const [severidad, setSeveridad] = useState<Severidad>('LEVE');
  const [duracionDias, setDuracionDias] = useState(1);
  const [relacionadoMenu, setRelacionadoMenu] = useState(false);
  const [notas, setNotas] = useState('');
  const [loading, setLoading] = useState(false);
  const [historial, setHistorial] = useState<SintomaHistorial[]>([]);
  const [loadingHistorial, setLoadingHistorial] = useState(false);
  const [mostrarHistorial, setMostrarHistorial] = useState(false);

  useEffect(() => {
    if (open && mostrarHistorial) {
      cargarHistorial();
    }
  }, [open, mostrarHistorial]);

  const cargarHistorial = async () => {
    try {
      setLoadingHistorial(true);
      const response = await apiService.obtenerSintomasPorNino(child.nin_id);
      if (response.success && response.data) {
        setHistorial(response.data);
      }
    } catch (error) {
      console.error('Error cargando historial:', error);
    } finally {
      setLoadingHistorial(false);
    }
  };

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

      // Reset form
      setFecha(new Date().toISOString().split('T')[0]);
      setTipo('');
      setSeveridad('LEVE');
      setDuracionDias(1);
      setRelacionadoMenu(false);
      setNotas('');

      // Recargar historial si está visible
      if (mostrarHistorial) {
        cargarHistorial();
      }

    } catch (error: any) {
      console.error('Error registrando síntoma:', error);
      toast.error(error.response?.data?.detail || 'Error al registrar síntoma');
    } finally {
      setLoading(false);
    }
  };

  const getSeveridadColor = (severidad: string) => {
    if (severidad === 'LEVE') return 'bg-yellow-100 text-yellow-800';
    if (severidad === 'MODERADO') return 'bg-orange-100 text-orange-800';
    return 'bg-red-100 text-red-800';
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Registrar Síntoma - {child.nin_nombres}</span>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setMostrarHistorial(!mostrarHistorial)}
              >
                <History size={16} className="mr-2" />
                {mostrarHistorial ? 'Ocultar' : 'Ver'} Historial
              </Button>
              <Button variant="ghost" size="icon" onClick={onClose}>
                <X size={20} />
              </Button>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Historial */}
          {mostrarHistorial && (
            <div className="border rounded-lg p-4 bg-muted/30">
              <h3 className="font-medium mb-3 flex items-center space-x-2">
                <History size={16} />
                <span>Historial de Síntomas</span>
              </h3>
              {loadingHistorial ? (
                <p className="text-sm text-muted-foreground">Cargando...</p>
              ) : historial.length === 0 ? (
                <p className="text-sm text-muted-foreground">No hay registros previos</p>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {historial.slice(0, 10).map((sin) => (
                    <div key={sin.sin_id} className="flex items-center justify-between p-2 bg-background rounded border text-sm">
                      <div className="flex items-center space-x-2">
                        <AlertTriangle size={14} className="text-orange-500" />
                        <span>{new Date(sin.sin_fecha).toLocaleDateString()}</span>
                        <span className="font-medium">{sin.sin_tipo}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getSeveridadColor(sin.sin_severidad)}>
                          {sin.sin_severidad}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{sin.sin_duracion_dias}d</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
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
