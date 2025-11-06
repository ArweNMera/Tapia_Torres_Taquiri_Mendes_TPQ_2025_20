/**
 * Página principal de Plan de Comidas
 */
import React, { useState, useEffect, useCallback } from 'react';
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
import { apiCache } from '../utils/cache';

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

  const cargarNinos = useCallback(async () => {
    setLoading(true);
    try {
      // OPTIMIZACIÓN: Verificar caché primero
      const cacheKey = 'ninos-list';
      const cached = apiCache.get<NinoConPreferencias[]>(cacheKey);

      if (cached) {
        setNinos(cached);
        setLoading(false);
        return; // Usar datos cacheados
      }

      const response = await apiService.getNinos();
      if (!response.success) {
        throw new Error(response.error || 'Error cargando niños');
      }
      const data = response.data || [];

      // OPTIMIZACIÓN: Cargar datos básicos primero, detalles después (lazy loading)
      const ninosBasicos = data.map((item: any) => {
        const ninoData = item.nino || item;
        return {
          ...ninoData,
          edad_anos: Math.floor(
            (new Date().getTime() - new Date(ninoData.nin_fecha_nac).getTime()) /
            (1000 * 60 * 60 * 24 * 365)
          ),
          tiene_preferencias: false, // Se carga después
          total_preferencias: 0,
          tiene_perfil: false, // Se carga después
          ultima_evaluacion: item.antropometrias?.[0]?.ant_fecha || null,
          clasificacion: item.antropometrias?.[0]?.clasificacion || null,
        };
      });

      setNinos(ninosBasicos);
      setLoading(false);

      // Cargar detalles en background (sin bloquear UI)
      const detallesPromises = ninosBasicos.map(async (nino, index) => {
        // Verificar caché individual
        const prefKey = `preferencias-${nino.nin_id}`;
        const perfilKey = `perfil-${nino.nin_id}`;

        let tienePreferencias = false;
        let totalPreferencias = 0;
        let tienePerfil = false;

        try {
          const cachedPref = apiCache.get<any>(prefKey);
          if (cachedPref) {
            const total = Object.values(cachedPref.preferencias || {}).flat().length;
            tienePreferencias = total > 0;
            totalPreferencias = total;
          } else {
            const prefs = await obtenerPreferencias(nino.nin_id, true);
            apiCache.set(prefKey, prefs);
            const total = Object.values(prefs.preferencias).flat().length;
            tienePreferencias = total > 0;
            totalPreferencias = total;
          }
        } catch (error: any) {
          // No tiene preferencias
        }

        try {
          const cachedPerfil = apiCache.get(perfilKey);
          if (cachedPerfil) {
            tienePerfil = true;
          } else {
            const perfil = await obtenerPerfilNutricional(nino.nin_id, true);
            apiCache.set(perfilKey, perfil);
            tienePerfil = true;
          }
        } catch (error: any) {
          // No tiene perfil
        }

        return { index, tienePreferencias, totalPreferencias, tienePerfil };
      });

      // Actualizar conforme se completan las promesas
      detallesPromises.forEach(promesa => {
        promesa.then(resultado => {
          setNinos(prev => {
            const nuevos = [...prev];
            nuevos[resultado.index] = {
              ...nuevos[resultado.index],
              tiene_preferencias: resultado.tienePreferencias,
              total_preferencias: resultado.totalPreferencias,
              tiene_perfil: resultado.tienePerfil,
            };
            // Cachear resultado final
            apiCache.set(cacheKey, nuevos);
            return nuevos;
          });
        });
      });

    } catch (error) {
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los niños',
        variant: 'destructive',
      });
      setLoading(false);
    }
  }, [toast]);

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

  const cerrarModales = useCallback((recargar: boolean = false) => {
    setModalPreferencias(false);
    setModalPerfil(false);
    setModalAlergias(false);
    setModalComidas(false);
    setModalGenerarPlan(false);
    setNinoSeleccionado(null);

    // OPTIMIZACIÓN: Invalidar caché cuando hay cambios
    if (recargar) {
      // Invalidar caché del niño específico y lista general
      if (ninoSeleccionado) {
        apiCache.invalidatePattern(`preferencias-${ninoSeleccionado.nin_id}`);
        apiCache.invalidatePattern(`perfil-${ninoSeleccionado.nin_id}`);
      }
      apiCache.invalidate('ninos-list');
      cargarNinos();
    }
  }, [ninoSeleccionado, cargarNinos]);

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
