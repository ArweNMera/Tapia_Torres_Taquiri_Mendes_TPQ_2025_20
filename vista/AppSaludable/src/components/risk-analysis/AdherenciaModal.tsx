import { useState, useEffect } from 'react';
import { X, Calendar, CheckCircle, AlertCircle, XCircle, History } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../ui/dialog';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Textarea } from '../ui/textarea';
import { Slider } from '../ui/slider';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import { Badge } from '../ui/badge';
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

interface AdherenciaHistorial {
  adh_id: number;
  adh_registrado_en: string;
  adh_estado: string;
  adh_porcentaje: number;
  adh_dificultad: string;
}

export function AdherenciaModal({ open, onClose, child }: AdherenciaModalProps) {
  const [fecha, setFecha] = useState(new Date().toISOString().split('T')[0]);
  const [estado, setEstado] = useState<Estado>('OK');
  const [porcentaje, setPorcentaje] = useState([75]);
  const [dificultad, setDificultad] = useState<Dificultad>('NINGUNA');
  const [comentario, setComentario] = useState('');
  const [loading, setLoading] = useState(false);
  const [historial, setHistorial] = useState<AdherenciaHistorial[]>([]);
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
      const response = await apiService.obtenerAdherenciaPorNino(child.nin_id);
      if (response.success && response.data) {
        setHistorial(response.data.registros || []);
      }
    } catch (error) {
      console.error('Error cargando historial:', error);
    } finally {
      setLoadingHistorial(false);
    }
  };

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

      // Reset form
      setFecha(new Date().toISOString().split('T')[0]);
      setEstado('OK');
      setPorcentaje([75]);
      setDificultad('NINGUNA');
      setComentario('');

      // Recargar historial si está visible
      if (mostrarHistorial) {
        cargarHistorial();
      }

    } catch (error: any) {
      console.error('Error registrando adherencia:', error);
      toast.error(error.response?.data?.detail || 'Error al registrar adherencia');
    } finally {
      setLoading(false);
    }
  };

  const getEstadoIcon = (estado: string) => {
    if (estado === 'OK') return <CheckCircle className="text-green-500" size={16} />;
    if (estado === 'PARCIAL') return <AlertCircle className="text-yellow-500" size={16} />;
    return <XCircle className="text-red-500" size={16} />;
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Registrar Adherencia - {child.nin_nombres}</span>
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
                <span>Historial de Adherencia</span>
              </h3>
              {loadingHistorial ? (
                <p className="text-sm text-muted-foreground">Cargando...</p>
              ) : historial.length === 0 ? (
                <p className="text-sm text-muted-foreground">No hay registros previos</p>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {historial.slice(0, 10).map((reg) => (
                    <div key={reg.adh_id} className="flex items-center justify-between p-2 bg-background rounded border text-sm">
                      <div className="flex items-center space-x-2">
                        {getEstadoIcon(reg.adh_estado)}
                        <span>{new Date(reg.adh_registrado_en).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="font-medium">{reg.adh_porcentaje}%</span>
                        <Badge variant="outline" className="text-xs">{reg.adh_dificultad}</Badge>
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
