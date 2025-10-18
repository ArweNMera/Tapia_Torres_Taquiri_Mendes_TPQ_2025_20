/**
 * Modal para ver y generar plan de comidas completo (Lunes-Domingo, Desayuno-Cena)
 * Ahora redirige al VerPlanModal para mostrar el plan
 */
import React, { useState, useEffect } from 'react';
import { listarMenusNino } from '../../services/mealPlanApi';
import { VerPlanModal } from './VerPlanModal';

interface GenerarPlanModalProps {
  open: boolean;
  onClose: () => void;
  ninId: number;
  ninNombre: string;
}

export const GenerarPlanModal: React.FC<GenerarPlanModalProps> = ({
  open,
  onClose,
  ninId,
  ninNombre,
}) => {
  const [menId, setMenId] = useState<number | undefined>();
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    if (open) {
      cargarPlanExistente();
    }
  }, [open, ninId]);

  const cargarPlanExistente = async () => {
    setCargando(true);
    try {
      const data = await listarMenusNino(ninId, 'BORRADOR', 1);
      if (data.menus && data.menus.length > 0) {
        setMenId(data.menus[0].men_id);
      } else {
        setMenId(undefined);
      }
    } catch (error) {
      setMenId(undefined);
    } finally {
      setCargando(false);
    }
  };

  // Simplemente redirigir al VerPlanModal
  return (
    <VerPlanModal
      open={open}
      onClose={onClose}
      ninId={ninId}
      ninNombre={ninNombre}
      menId={menId}
    />
  );
};
