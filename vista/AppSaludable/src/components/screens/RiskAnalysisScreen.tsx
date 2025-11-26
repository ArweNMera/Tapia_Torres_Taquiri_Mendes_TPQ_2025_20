import { useState, useEffect } from 'react';
import { Activity, AlertTriangle, Heart, TrendingUp, User } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { toast } from 'sonner';
import { motion } from 'motion/react';
import { apiService } from '../../services/api';

// Modales
import { AdherenciaModal } from '../risk-analysis/AdherenciaModal';
import { SintomasModal } from '../risk-analysis/SintomasModal';
import { PrediccionModal } from '../risk-analysis/PrediccionModal';
import { PerfilNutricionalModal } from '../meal-plan/PerfilNutricionalModal';

interface Child {
  nin_id: number;
  nin_nombres: string;
  nin_apellidos: string;
  nin_fecha_nac: string;
  nin_sexo: string;
  edad_anios: number;
  ultima_medicion?: {
    fecha: string;
    peso_kg: number;
    talla_cm: number;
    imc: number;
    clasificacion: string;
  };
}

export function RiskAnalysisScreen() {
  const [children, setChildren] = useState<Child[]>([]);
  const [filteredChildren, setFilteredChildren] = useState<Child[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  // Estados de modales
  const [selectedChild, setSelectedChild] = useState<Child | null>(null);
  const [adherenciaModalOpen, setAdherenciaModalOpen] = useState(false);
  const [sintomasModalOpen, setSintomasModalOpen] = useState(false);
  const [prediccionModalOpen, setPrediccionModalOpen] = useState(false);
  const [perfilModalOpen, setPerfilModalOpen] = useState(false);

  useEffect(() => {
    fetchChildren();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = children.filter(child =>
        `${child.nin_nombres} ${child.nin_apellidos}`.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredChildren(filtered);
    } else {
      setFilteredChildren(children);
    }
  }, [searchTerm, children]);

  const fetchChildren = async () => {
    try {
      setLoading(true);
      const response = await apiService.getNinos();
      if (response.success && response.data) {
        const childrenData = response.data.map(item => {
          const nino = item.nino;
          const edad = nino.nin_fecha_nac
            ? Math.floor((new Date().getTime() - new Date(nino.nin_fecha_nac).getTime()) / (365.25 * 24 * 60 * 60 * 1000))
            : 0;

          return {
            nin_id: nino.nin_id,
            nin_nombres: nino.nin_nombres,
            nin_apellidos: '', // NinoResponse no tiene apellidos
            nin_fecha_nac: nino.nin_fecha_nac,
            nin_sexo: nino.nin_sexo,
            edad_anios: edad,
            ultima_medicion: item.antropometrias && item.antropometrias.length > 0
              ? {
                  fecha: item.antropometrias[0].ant_fecha,
                  peso_kg: item.antropometrias[0].ant_peso_kg,
                  talla_cm: item.antropometrias[0].ant_talla_cm,
                  imc: item.antropometrias[0].ant_peso_kg / Math.pow(item.antropometrias[0].ant_talla_cm / 100, 2),
                  clasificacion: item.ultimo_estado_nutricional?.classification || 'SIN_EVALUACION'
                }
              : undefined
          };
        });
        setChildren(childrenData);
        setFilteredChildren(childrenData);
      }
    } catch (error) {
      console.error('Error fetching children:', error);
      toast.error('Error al cargar niños');
    } finally {
      setLoading(false);
    }
  };

  const getClasificacionColor = (clasificacion?: string) => {
    if (!clasificacion) return 'bg-gray-500';

    const lower = clasificacion.toLowerCase();
    if (lower.includes('severa') || lower.includes('obesidad')) return 'bg-red-500';
    if (lower.includes('moderada') || lower.includes('sobrepeso')) return 'bg-orange-500';
    if (lower.includes('riesgo')) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const getClasificacionText = (clasificacion?: string) => {
    if (!clasificacion) return 'Sin evaluación';
    return clasificacion.replace(/_/g, ' ');
  };

  const handleOpenAdherencia = (child: Child) => {
    setSelectedChild(child);
    setAdherenciaModalOpen(true);
  };

  const handleOpenSintomas = (child: Child) => {
    setSelectedChild(child);
    setSintomasModalOpen(true);
  };

  const handleOpenPrediccion = (child: Child) => {
    setSelectedChild(child);
    setPrediccionModalOpen(true);
  };

  const handleOpenPerfil = (child: Child) => {
    setSelectedChild(child);
    setPerfilModalOpen(true);
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Cargando niños...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Análisis de Riesgos</h1>
        <p className="text-muted-foreground mt-1">
          Predicción de riesgos nutricionales
        </p>
      </div>

      {/* Búsqueda */}
      <div className="flex items-center space-x-4">
        <Input
          placeholder="Buscar niño..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-md"
        />
        <Badge variant="outline">
          {filteredChildren.length} niño{filteredChildren.length !== 1 ? 's' : ''}
        </Badge>
      </div>

      {/* Grid de tarjetas 2x2 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredChildren.map((child, index) => (
          <motion.div
            key={child.nin_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                {/* Información del niño - Izquierda */}
                <div className="flex-1 space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                      <User className="text-primary" size={24} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">
                        {child.nin_nombres}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {child.edad_anios} año{child.edad_anios !== 1 ? 's' : ''} • {child.nin_sexo === 'M' ? 'Masculino' : 'Femenino'}
                      </p>
                    </div>
                  </div>

                  {/* Última medición */}
                  {child.ultima_medicion ? (
                    <div className="bg-muted/50 rounded-lg p-3 space-y-2">
                      <p className="text-xs text-muted-foreground">
                        Última medición: {new Date(child.ultima_medicion.fecha).toLocaleDateString()}
                      </p>
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div>
                          <p className="text-muted-foreground text-xs">Peso</p>
                          <p className="font-medium">{child.ultima_medicion.peso_kg} kg</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground text-xs">Talla</p>
                          <p className="font-medium">{child.ultima_medicion.talla_cm} cm</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground text-xs">IMC</p>
                          <p className="font-medium">{child.ultima_medicion.imc.toFixed(1)}</p>
                        </div>
                      </div>
                      <Badge className={`${getClasificacionColor(child.ultima_medicion.clasificacion)} text-white text-xs`}>
                        {getClasificacionText(child.ultima_medicion.clasificacion)}
                      </Badge>
                    </div>
                  ) : (
                    <div className="bg-muted/50 rounded-lg p-3">
                      <p className="text-sm text-muted-foreground">Sin mediciones recientes</p>
                    </div>
                  )}
                </div>

                {/* Botones de acción - Derecha */}
                <div className="ml-4 flex flex-col space-y-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleOpenPerfil(child)}
                    className="w-full justify-start"
                  >
                    <User size={16} className="mr-2" />
                    Perfil
                  </Button>

                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleOpenAdherencia(child)}
                    className="w-full justify-start"
                  >
                    <Activity size={16} className="mr-2" />
                    Adherencia
                  </Button>

                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleOpenSintomas(child)}
                    className="w-full justify-start"
                  >
                    <Heart size={16} className="mr-2" />
                    Síntomas
                  </Button>

                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleOpenPrediccion(child)}
                    className="w-full justify-start"
                  >
                    <TrendingUp size={16} className="mr-2" />
                    Predicción
                  </Button>
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Mensaje si no hay niños */}
      {filteredChildren.length === 0 && !loading && (
        <Card className="p-12 text-center">
          <AlertTriangle className="mx-auto text-muted-foreground mb-4" size={48} />
          <h3 className="text-lg font-semibold mb-2">No se encontraron niños</h3>
          <p className="text-muted-foreground">
            {searchTerm ? 'Intenta con otro término de búsqueda' : 'No tienes niños asignados'}
          </p>
        </Card>
      )}

      {/* Modales */}
      {selectedChild && (
        <>
          <AdherenciaModal
            open={adherenciaModalOpen}
            onClose={() => setAdherenciaModalOpen(false)}
            child={selectedChild}
          />

          <SintomasModal
            open={sintomasModalOpen}
            onClose={() => setSintomasModalOpen(false)}
            child={selectedChild}
          />

          <PrediccionModal
            open={prediccionModalOpen}
            onClose={() => setPrediccionModalOpen(false)}
            child={selectedChild}
          />

          <PerfilNutricionalModal
            open={perfilModalOpen}
            onClose={() => setPerfilModalOpen(false)}
            ninId={selectedChild.nin_id}
            ninNombre={selectedChild.nin_nombres}
          />
        </>
      )}
    </div>
  );
}
