/**
 * API para gestión de planes de comidas y preferencias
 */
import { apiService } from './api';
import type {
  Preferencias,
  PreferenciasResponse,
  PerfilNutricional,
  MenuListItem,
} from '../types/mealPlan';

// ============================================================================
// PREFERENCIAS
// ============================================================================

export const guardarPreferencias = async (
  ninId: number,
  preferencias: Preferencias
): Promise<{ mensaje: string; nin_id: number; total_preferencias: number }> => {
  const response = await apiService['makeRequest']<{
    mensaje: string;
    nin_id: number;
    total_preferencias: number;
  }>(`${(apiService as any).getApiUrl(`/preferencias/ninos/${ninId}`)}`, {
    method: 'POST',
    body: JSON.stringify(preferencias),
  });

  if (!response.success) {
    throw new Error(response.error || 'Error guardando preferencias');
  }

  return response.data!;
};

export const obtenerPreferencias = async (
  ninId: number,
  silentErrors: boolean = false
): Promise<PreferenciasResponse> => {
  const response = await apiService['makeRequest']<PreferenciasResponse>(
    `${(apiService as any).getApiUrl(`/preferencias/ninos/${ninId}`)}`,
    { method: 'GET', silentErrors }
  );

  console.log('🔍 Respuesta del API para preferencias:', response);

  if (!response.success) {
    throw new Error(response.error || 'Error obteniendo preferencias');
  }

  console.log('✅ Datos de preferencias:', response.data);
  return response.data!;
};

export const obtenerPreferenciasPorTipo = async (
  ninId: number,
  tipoComida: string
): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/preferencias/ninos/${ninId}/${tipoComida}`)}`,
    { method: 'GET' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error obteniendo preferencias por tipo');
  }

  return response.data!;
};

export const eliminarPreferencia = async (
  npcId: number
): Promise<{ mensaje: string }> => {
  const response = await apiService['makeRequest']<{ mensaje: string }>(
    `${(apiService as any).getApiUrl(`/preferencias/items/${npcId}`)}`,
    { method: 'DELETE' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error eliminando preferencia');
  }

  return response.data!;
};

export const obtenerResumenPreferencias = async (): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl('/preferencias/usuarios/me/resumen')}`,
    { method: 'GET' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error obteniendo resumen');
  }

  return response.data!;
};

// ============================================================================
// PERFIL NUTRICIONAL
// ============================================================================

export const obtenerPerfilNutricional = async (
  ninId: number,
  silentErrors: boolean = false
): Promise<PerfilNutricional> => {
  const response = await apiService['makeRequest']<PerfilNutricional>(
    `${(apiService as any).getApiUrl(`/planes-comidas/ninos/${ninId}/perfil-nutricional`)}`,
    { method: 'GET', silentErrors }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error obteniendo perfil nutricional');
  }

  return response.data!;
};

export const calcularPerfilNutricional = async (
  ninId: number
): Promise<{
  mensaje: string;
  pnn_id: number;
  nin_id: number;
  pnn_calorias_diarias: number;
  pnn_clasificacion: string;
}> => {
  const response = await apiService['makeRequest']<{
    mensaje: string;
    pnn_id: number;
    nin_id: number;
    pnn_calorias_diarias: number;
    pnn_clasificacion: string;
  }>(`${(apiService as any).getApiUrl(`/planes-comidas/ninos/${ninId}/calcular-perfil`)}`, {
    method: 'POST',
  });

  if (!response.success) {
    throw new Error(response.error || 'Error calculando perfil nutricional');
  }

  return response.data!;
};

// ============================================================================
// PLANES DE COMIDAS
// ============================================================================

export const generarPlanSemanal = async (
  ninId: number,
  fechaInicio: string,
  incluirRefacciones: boolean = false
): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl('/planes-comidas/generar')}`,
    {
      method: 'POST',
      body: JSON.stringify({
        nin_id: ninId,
        fecha_inicio: fechaInicio,
        incluir_refacciones: incluirRefacciones,
      }),
    }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error generando plan semanal');
  }

  return response.data!;
};

export const listarMenusNino = async (
  ninId: number,
  estado?: string,
  limit: number = 10
): Promise<{ nin_id: number; total: number; menus: MenuListItem[] }> => {
  const params = new URLSearchParams();
  if (estado) params.append('estado', estado);
  params.append('limit', limit.toString());

  const response = await apiService['makeRequest']<{
    nin_id: number;
    total: number;
    menus: MenuListItem[];
  }>(
    `${(apiService as any).getApiUrl(`/planes-comidas/ninos/${ninId}/menus`)}?${params.toString()}`,
    { method: 'GET' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error listando menús');
  }

  return response.data!;
};

export const obtenerDetalleMenu = async (menId: number): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/planes-comidas/menus/${menId}`)}`,
    { method: 'GET' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error obteniendo detalle del menú');
  }

  return response.data!;
};

export const actualizarEstadoMenu = async (
  menId: number,
  estado: string
): Promise<{ mensaje: string; men_id: number; men_estado: string }> => {
  const response = await apiService['makeRequest']<{
    mensaje: string;
    men_id: number;
    men_estado: string;
  }>(`${(apiService as any).getApiUrl(`/planes-comidas/menus/${menId}/estado`)}`, {
    method: 'PATCH',
    body: JSON.stringify({ estado }),
  });

  if (!response.success) {
    throw new Error(response.error || 'Error actualizando estado del menú');
  }

  return response.data!;
};

// ============================================================================
// ALERGIAS
// ============================================================================

export const obtenerAlergias = async (ninId: number): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/planes-comidas/ninos/${ninId}/alergias`)}`,
    { method: 'GET' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error obteniendo alergias');
  }

  return response.data!;
};

export const agregarAlergia = async (
  ninId: number,
  alergeno: string,
  severidad: string
): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/planes-comidas/ninos/${ninId}/alergias`)}`,
    {
      method: 'POST',
      body: JSON.stringify({ alergeno, severidad }),
    }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error agregando alergia');
  }

  return response.data!;
};

export const eliminarAlergia = async (nalId: number): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/planes-comidas/alergias/${nalId}`)}`,
    { method: 'DELETE' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error eliminando alergia');
  }

  return response.data!;
};

// ============================================================================
// COMIDAS FAVORITAS
// ============================================================================

export const obtenerComidasFavoritas = async (ninId: number): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/planes-comidas/ninos/${ninId}/favoritas`)}`,
    { method: 'GET' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error obteniendo comidas favoritas');
  }

  return response.data!;
};

export const agregarComidaFavorita = async (
  ninId: number,
  recId: number
): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/planes-comidas/ninos/${ninId}/favoritas`)}`,
    {
      method: 'POST',
      body: JSON.stringify({ rec_id: recId }),
    }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error agregando comida favorita');
  }

  return response.data!;
};

export const eliminarComidaFavorita = async (ncfId: number): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/planes-comidas/favoritas/${ncfId}`)}`,
    { method: 'DELETE' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error eliminando comida favorita');
  }

  return response.data!;
};

// ============================================================================
// BÚSQUEDA DE RECETAS
// ============================================================================

export const buscarRecetas = async (query: string): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/planes-comidas/recetas/buscar?q=${encodeURIComponent(query)}`)}`,
    { method: 'GET' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error buscando recetas');
  }

  return response.data!;
};

// ============================================================================
// GENERACIÓN DE PLAN COMPLETO CON LLM
// ============================================================================

export const generarPlanCompletoConLLM = async (
  ninId: number,
  fechaInicio: string
): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl('/planes-comidas/generar')}`,
    {
      method: 'POST',
      body: JSON.stringify({
        nin_id: ninId,
        fecha_inicio: fechaInicio,
        incluir_refacciones: false,
      }),
    }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error generando plan completo');
  }

  return response.data!;
};

// ============================================================================
// DETALLE DE RECETA
// ============================================================================

export const obtenerDetalleReceta = async (recId: number): Promise<any> => {
  const response = await apiService['makeRequest']<any>(
    `${(apiService as any).getApiUrl(`/planes-comidas/recetas/${recId}`)}`,
    { method: 'GET' }
  );

  if (!response.success) {
    throw new Error(response.error || 'Error obteniendo detalle de receta');
  }

  return response.data!;
};
