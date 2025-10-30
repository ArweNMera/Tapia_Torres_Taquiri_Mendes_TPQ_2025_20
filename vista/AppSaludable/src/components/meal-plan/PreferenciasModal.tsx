import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { PreferenciasWizard } from './PreferenciasWizard';
import { useToast } from '../ui/use-toast';
import { Loader2 } from 'lucide-react';
import { obtenerPreferencias, guardarPreferencias } from '../../services/mealPlanApi';
import type { Preferencias } from '../../types/mealPlan';

interface PreferenciasModalProps {
  open: boolean;
  onClose: (recargar?: boolean) => void;
  ninId: number;
  ninNombre: string;
}

const PREFERENCIAS_VACIAS: Preferencias = {
  desayuno: [],
  almuerzo: [],
  cena: [],
  snacks: [],
};

export const PreferenciasModal: React.FC<PreferenciasModalProps> = ({
  open,
  onClose,
  ninId,
  ninNombre,
}) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [preferencias, setPreferencias] = useState<Preferencias>(PREFERENCIAS_VACIAS);

  useEffect(() => {
    if (open) {
      cargarPreferencias();
    }
  }, [open, ninId]);

  const cargarPreferencias = async () => {
    setLoading(true);
    try {
      const data = await obtenerPreferencias(ninId);
      console.log('📥 Datos recibidos del backend:', data);
      console.log('📋 Preferencias extraídas:', data.preferencias);
      setPreferencias(data.preferencias);
    } catch (error: any) {
      console.error('❌ Error cargando preferencias:', error);
      // Si no tiene preferencias, usar vacías
      if (error.message?.includes('404') || error.message?.includes('No se encontraron')) {
        setPreferencias(PREFERENCIAS_VACIAS);
      } else {
        toast({
          title: 'Error',
          description: 'No se pudieron cargar las preferencias',
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (nuevasPreferencias: Preferencias) => {
    setLoading(true);
    try {
      await guardarPreferencias(ninId, nuevasPreferencias);
      toast({
        title: 'Preferencias guardadas',
        description: `Las preferencias de ${ninNombre} se guardaron exitosamente`,
      });
      onClose(true);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudieron guardar las preferencias',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Preferencias de {ninNombre}</DialogTitle>
        </DialogHeader>

        {loading && !preferencias ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
          </div>
        ) : (
          <PreferenciasWizard
            preferenciasIniciales={preferencias}
            onSave={handleSave}
            onCancel={onClose}
          />
        )}
      </DialogContent>
    </Dialog>
  );
};
