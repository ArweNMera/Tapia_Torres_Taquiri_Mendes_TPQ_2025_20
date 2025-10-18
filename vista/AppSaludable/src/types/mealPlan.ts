/**
 * Tipos para el sistema de planes de comidas
 */

export type TipoComida = 'DESAYUNO' | 'ALMUERZO' | 'CENA' | 'SNACKS';

export interface Preferencias {
  desayuno: string[];
  almuerzo: string[];
  cena: string[];
  snacks: string[];
}

export interface PreferenciaItem {
  npc_id: number;
  npc_preferencia: string;
  creado_en: string;
}

export interface PreferenciasResponse {
  nin_id: number;
  nin_nombres: string;
  preferencias: Preferencias;
  actualizado_en?: string;
}

export interface PerfilNutricional {
  pnn_id: number;
  nin_id: number;
  pnn_calorias_diarias: number;
  pnn_proteinas_g: number;
  pnn_carbohidratos_g: number;
  pnn_grasas_g: number;
  pnn_hierro_mg?: number;
  pnn_calcio_mg?: number;
  pnn_vitamina_a_ug?: number;
  pnn_vitamina_c_mg?: number;
  pnn_zinc_mg?: number;
  pnn_fibra_g?: number;
  pnn_edad_meses: number;
  pnn_peso_kg?: number;
  pnn_talla_cm?: number;
  pnn_clasificacion?: string;
  pnn_metodo_calculo: string;
  pnn_fecha_calculo: string;
  pnn_vigente: boolean;
}

export interface IngredienteReceta {
  ali_nombre: string;
  cantidad: number;
  unidad: string;
}

export interface ComidaPlan {
  mei_id?: number;
  rec_id: number;
  rec_nombre: string;
  rec_instrucciones: string;
  mei_kcal: number;
  ingredientes: IngredienteReceta[];
  match_preferencias: string[];
}

export interface DiaPlan {
  dia_idx: number;
  dia_nombre: string;
  fecha: string;
  desayuno: ComidaPlan;
  almuerzo: ComidaPlan;
  cena: ComidaPlan;
  total_dia: number;
}

export interface ResumenPlan {
  calorias_promedio_dia: number;
  preferencias_respetadas: number;
  preferencias_totales: number;
  porcentaje_match: number;
}

export interface PlanSemanal {
  men_id: number;
  nin_id: number;
  men_inicio: string;
  men_fin: string;
  men_kcal_total: number;
  men_estado: string;
  dias: DiaPlan[];
  resumen: ResumenPlan;
}

export interface MenuListItem {
  men_id: number;
  men_inicio: string;
  men_fin: string;
  men_kcal_total?: number;
  men_estado: string;
  men_generado_por: string;
  creado_en: string;
}

export interface NinoConPreferencias {
  nin_id: number;
  nin_nombres: string;
  nin_fecha_nac: string;
  nin_sexo: 'M' | 'F';
  edad_anos: number;
  clasificacion?: string;
  tiene_preferencias: boolean;
  total_preferencias: number;
  tiene_perfil: boolean;
  ultima_evaluacion?: string;
}
