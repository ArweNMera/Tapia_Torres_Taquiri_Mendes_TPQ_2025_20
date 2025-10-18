/**
 * Página principal de Plan de Comidas
 */
import React, { useState, useEffect } from 'react';
import { ChildCard } from '../components/meal-plan/ChildCard';
import { PreferenciasModal } from '../components/meal-plan/PreferenciasModal';
import { PerfilNutricionalModal } from '../components/meal-plan/PerfilNutricionalModal';
import { AlergiasModal } from '../components/meal-plan/AlergiasModal';
import { ComidasFavoritasModal } from '../components/meal-plan/ComidasFavoritasModal';
import { GenerarPlanModal } from '../components/meal-plan/GenerarPlanModal';
import { useToast } from '../components/ui/use-toast';
import { Loader2, UtensilsCrossed } from 'lucide-react';
import { apiService } from '../services/api';
import { obtenerPerfilNutricional, obtenerPreferencias } from '../services/mealPlanApi';
import type { NinoConPreferencias } from '../types/mealPlan';

export const MealPlanPage: React.FC = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [ninos, setNinos] = useState<NinoConPreferencias[]>([]);

  // Estados de modales
  const [ninoSeleccionado, setNinoSeleccionado] = useState<NinoConPreferencias | null>(null);
  const [modalPreferencias, setModalPreferencias] = useState(false);
  const [modalPerfil, setModalPerfil] = useState(false);
  const [modalAlergias, setModalAlergias] = useState(false);
  const [modalComidas, setModalComidas] = useState(false);
  const [modalGenerarPlan, setModalGenerarPlan] = useState(false);

  useEffect(() => {
    cargarNinos();
  }, []);

  const cargarNinos = async () => {
    setLoading(true);
    try {
      const response = await apiService.getNinos();
      if (!response.success) {
        throw new Error(response.error || 'Error cargando niños');
      }
      const data = response.data || [];

      // Enriquecer con información de preferencias y perfil
      const ninosEnriquecidos = await Promise.all(
        data.map(async (item: any) => {
          // La estructura es { nino: {...}, antropometrias: [...] }
          const ninoData = item.nino || item;
          let tienePreferencias = false;
          let totalPreferencias = 0;
          let tienePerfil = false;

          try {
            const prefs = await obtenerPreferencias(ninoData.nin_id, true);
            const total = Object.values(prefs.preferencias).flat().length;
            tienePreferencias = total > 0;
            totalPreferencias = total;
          } catch (error: any) {
            // No tiene preferencias configuradas (esperado para niños nuevos)
          }

          try {
            await obtenerPerfilNutricional(ninoData.nin_id, true);
            tienePerfil = true;
          } catch (error: any) {
            // No tiene perfil calculado (esperado para niños nuevos)
          }

          return {
            ...ninoData,
            edad_anos: Math.floor(
              (new Date().getTime() - new Date(ninoData.nin_fecha_nac).getTime()) /
              (1000 * 60 * 60 * 24 * 365)
            ),
            tiene_preferencias: tienePreferencias,
            total_preferencias: totalPreferencias,
            tiene_perfil: tienePerfil,
            ultima_evaluacion: item.antropometrias?.[0]?.ant_fecha || null,
            clasificacion: item.antropometrias?.[0]?.clasificacion || null,
          };
        })
      );

      setNinos(ninosEnriquecidos);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los niños',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const abrirPreferencias = (nino: NinoConPreferencias) => {
    setNinoSeleccionado(nino);
    setModalPreferencias(true);
  };

  const abrirPerfil = (nino: NinoConPreferencias) => {
    setNinoSeleccionado(nino);
    setModalPerfil(true);
  };

  const abrirAlergias = (nino: NinoConPreferencias) => {
    setNinoSeleccionado(nino);
    setModalAlergias(true);
  };

  const abrirComidas = (nino: NinoConPreferencias) => {
    setNinoSeleccionado(nino);
    setModalComidas(true);
  };

  const abrirGenerarPlan = (nino: NinoConPreferencias) => {
    if (!nino.tiene_perfil) {
      toast({
        title: 'Configuración incompleta',
        description: 'Primero calcula el perfil nutricional del niño',
        variant: 'destructive',
      });
      return;
    }

    setNinoSeleccionado(nino);
    setModalGenerarPlan(true);
  };

  const cerrarModales = () => {
    setModalPreferencias(false);
    setModalPerfil(false);
    setModalAlergias(false);
    setModalComidas(false);
    setModalGenerarPlan(false);
    setNinoSeleccionado(null);
    // Recargar para actualizar estados
    cargarNinos();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}


      {/* Lista de niños */}
      {ninos.length === 0 ? (
        <div className="text-center py-12">
          <UtensilsCrossed className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            No hay niños registrados
          </h3>
          <p className="text-gray-600">
            Agrega un niño para comenzar a crear planes de comidas
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {ninos.map((nino) => (
            <ChildCard
              key={nino.nin_id}
              nino={nino}
              onPreferencias={() => abrirPreferencias(nino)}
              onPerfil={() => abrirPerfil(nino)}
              onAlergias={() => abrirAlergias(nino)}
              onComidas={() => abrirComidas(nino)}
              onGenerarPlan={() => abrirGenerarPlan(nino)}
            />
          ))}
        </div>
      )}

      {/* Modales */}
      {ninoSeleccionado && (
        <>
          <PreferenciasModal
            open={modalPreferencias}
            onClose={cerrarModales}
            ninId={ninoSeleccionado.nin_id}
            ninNombre={ninoSeleccionado.nin_nombres}
          />

          <PerfilNutricionalModal
            open={modalPerfil}
            onClose={cerrarModales}
            ninId={ninoSeleccionado.nin_id}
            ninNombre={ninoSeleccionado.nin_nombres}
          />

          <AlergiasModal
            open={modalAlergias}
            onClose={cerrarModales}
            ninId={ninoSeleccionado.nin_id}
            ninNombre={ninoSeleccionado.nin_nombres}
          />

          <ComidasFavoritasModal
            open={modalComidas}
            onClose={cerrarModales}
            ninId={ninoSeleccionado.nin_id}
            ninNombre={ninoSeleccionado.nin_nombres}
          />

          <GenerarPlanModal
            open={modalGenerarPlan}
            onClose={cerrarModales}
            ninId={ninoSeleccionado.nin_id}
            ninNombre={ninoSeleccionado.nin_nombres}
          />
        </>
      )}
    </div>
  );
};
