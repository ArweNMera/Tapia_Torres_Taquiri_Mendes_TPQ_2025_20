CREATE TABLE "adherencias" (
  "adh_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "men_id" bigint unsigned DEFAULT NULL,
  "mei_id" bigint unsigned DEFAULT NULL,
  "adh_registrado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "adh_estado" enum('OK','PARCIAL','NO') NOT NULL,
  "adh_porcentaje" decimal(5,2) DEFAULT NULL COMMENT 'Porcentaje de adherencia 0-100',
  "adh_notas" text,
  "adh_comentario_tutor" text COMMENT 'Comentario del tutor',
  "adh_dificultad" enum('NINGUNA','BAJA','MEDIA','ALTA') DEFAULT NULL COMMENT 'Dificultad reportada',
  PRIMARY KEY ("adh_id"),
  KEY "fk_adh_menu" ("men_id"),
  KEY "fk_adh_item" ("mei_id"),
  KEY "idx_adh_nino_fecha" ("nin_id","adh_registrado_en"),
  CONSTRAINT "fk_adh_item" FOREIGN KEY ("mei_id") REFERENCES "menus_items" ("mei_id") ON DELETE SET NULL,
  CONSTRAINT "fk_adh_menu" FOREIGN KEY ("men_id") REFERENCES "menus" ("men_id") ON DELETE SET NULL,
  CONSTRAINT "fk_adh_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE
)

CREATE TABLE "alimentos" (
  "ali_id" int unsigned NOT NULL AUTO_INCREMENT,
  "ali_nombre" varchar(150) NOT NULL,
  "ali_nombre_cientifico" varchar(150) DEFAULT NULL,
  "ali_grupo" varchar(60) DEFAULT NULL,
  "ali_unidad" varchar(16) NOT NULL,
  "ali_activo" tinyint(1) NOT NULL DEFAULT '1',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("ali_id"),
  FULLTEXT KEY "ft_ali_nombre" ("ali_nombre")
)

CREATE TABLE "alimentos_nutrientes" (
  "ali_id" int unsigned NOT NULL,
  "nutri_id" smallint unsigned NOT NULL,
  "an_cantidad_100" decimal(12,4) NOT NULL,
  "an_fuente" varchar(255) DEFAULT NULL,
  PRIMARY KEY ("ali_id","nutri_id"),
  KEY "fk_an_nutriente" ("nutri_id"),
  CONSTRAINT "fk_an_alimento" FOREIGN KEY ("ali_id") REFERENCES "alimentos" ("ali_id") ON DELETE CASCADE,
  CONSTRAINT "fk_an_nutriente" FOREIGN KEY ("nutri_id") REFERENCES "nutrientes" ("nutri_id") ON DELETE CASCADE
)

CREATE TABLE "antropometrias" (
  "ant_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "ant_fecha" date NOT NULL,
  "ant_edad_meses" smallint unsigned DEFAULT NULL,
  "ant_peso_kg" decimal(5,2) NOT NULL,
  "ant_talla_cm" decimal(5,2) NOT NULL,
  "ant_z_imc" decimal(6,3) DEFAULT NULL,
  "ant_z_peso_edad" decimal(6,3) DEFAULT NULL,
  "ant_z_talla_edad" decimal(6,3) DEFAULT NULL,
  "ant_fuente_json" json DEFAULT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("ant_id"),
  UNIQUE KEY "uk_ant_nino_fecha" ("nin_id","ant_fecha"),
  KEY "idx_ant_edad" ("ant_edad_meses"),
  CONSTRAINT "fk_antropometrias_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE,
  CONSTRAINT "chk_ant_edad_rango" CHECK ((`ant_edad_meses` between 0 and 228))
)

CREATE TABLE "consentimientos" (
  "con_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "usr_id" bigint unsigned NOT NULL,
  "con_alcance" varchar(120) NOT NULL,
  "con_aceptado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "con_revocado_en" datetime DEFAULT NULL,
  PRIMARY KEY ("con_id"),
  KEY "fk_con_usuario" ("usr_id"),
  CONSTRAINT "fk_con_usuario" FOREIGN KEY ("usr_id") REFERENCES "usuarios" ("usr_id") ON DELETE CASCADE
)

CREATE TABLE "disponibilidad_alimentos" (
  "dis_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "ali_id" int unsigned NOT NULL,
  "ent_id" int unsigned DEFAULT NULL,
  "dis_periodo" enum('Q1','Q2','Q3','Q4') NOT NULL,
  "dis_disponible" tinyint(1) NOT NULL,
  "dis_precio_promedio" decimal(10,2) DEFAULT NULL,
  "dis_region" varchar(120) DEFAULT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("dis_id"),
  KEY "fk_dis_alimento" ("ali_id"),
  KEY "fk_dis_entidad" ("ent_id"),
  KEY "idx_dis_region_periodo" ("dis_region","dis_periodo","dis_disponible"),
  CONSTRAINT "fk_dis_alimento" FOREIGN KEY ("ali_id") REFERENCES "alimentos" ("ali_id") ON DELETE CASCADE,
  CONSTRAINT "fk_dis_entidad" FOREIGN KEY ("ent_id") REFERENCES "entidades" ("ent_id") ON DELETE SET NULL
)

CREATE TABLE "entidad_tipos" (
  "entti_id" tinyint unsigned NOT NULL AUTO_INCREMENT,
  "entti_codigo" varchar(32) NOT NULL,
  "entti_nombre" varchar(80) NOT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("entti_id"),
  UNIQUE KEY "entti_codigo" ("entti_codigo")
)

CREATE TABLE "entidades" (
  "ent_id" int unsigned NOT NULL AUTO_INCREMENT,
  "entti_id" tinyint unsigned NOT NULL,
  "ent_codigo" varchar(40) DEFAULT NULL,
  "ent_nombre" varchar(150) NOT NULL,
  "ent_descripcion" varchar(255) DEFAULT NULL,
  "ent_direccion" varchar(180) DEFAULT NULL,
  "ent_referencia" varchar(180) DEFAULT NULL,
  "ent_departamento" varchar(60) DEFAULT NULL,
  "ent_provincia" varchar(60) DEFAULT NULL,
  "ent_distrito" varchar(60) DEFAULT NULL,
  "ent_ubigeo" varchar(6) DEFAULT NULL,
  "ent_latitud" decimal(9,6) DEFAULT NULL,
  "ent_longitud" decimal(9,6) DEFAULT NULL,
  "ent_altitud_m" int DEFAULT NULL COMMENT 'Altitud en metros sobre nivel del mar',
  "ent_zona" enum('URBANA','RURAL','PERIURBANA') DEFAULT NULL COMMENT 'Tipo de zona',
  "ent_poblacion_aprox" int DEFAULT NULL COMMENT 'Población aproximada del área',
  "ent_activo" tinyint(1) NOT NULL DEFAULT '1',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("ent_id"),
  UNIQUE KEY "ent_codigo" ("ent_codigo"),
  KEY "idx_entidades_tipo_activo" ("entti_id","ent_activo"),
  KEY "idx_entidades_zona" ("ent_zona"),
  CONSTRAINT "fk_entidades_tipo" FOREIGN KEY ("entti_id") REFERENCES "entidad_tipos" ("entti_id") ON DELETE RESTRICT
)

CREATE TABLE "evaluaciones_nutricionales" (
  "en_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "ant_id" bigint unsigned NOT NULL,
  "en_edad_meses" smallint unsigned NOT NULL,
  "en_imc" decimal(5,2) DEFAULT NULL COMMENT 'IMC calculado',
  "en_z_score_imc" decimal(5,2) DEFAULT NULL,
  "en_percentil_imc" decimal(5,2) DEFAULT NULL COMMENT 'Percentil calculado',
  "en_clasificacion" enum('DESNUTRICION_SEVERA','DESNUTRICION','RIESGO','NORMAL','SOBREPESO','OBESIDAD') NOT NULL,
  "en_nivel_riesgo" enum('BAJO','MODERADO','ALTO','CRITICO') NOT NULL,
  "en_observaciones" text,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("en_id"),
  UNIQUE KEY "uk_evaluacion_antropometria" ("ant_id"),
  KEY "idx_en_clasificacion" ("en_clasificacion"),
  KEY "idx_en_nino_creado" ("nin_id","creado_en" DESC),
  CONSTRAINT "fk_en_antropometria" FOREIGN KEY ("ant_id") REFERENCES "antropometrias" ("ant_id") ON DELETE CASCADE,
  CONSTRAINT "fk_en_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE
)

CREATE TABLE "evaluaciones_recomendaciones" (
  "er_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "en_id" bigint unsigned NOT NULL,
  "rt_id" smallint unsigned NOT NULL,
  "er_aplicada" tinyint(1) NOT NULL DEFAULT '0',
  "er_fecha_aplicacion" datetime DEFAULT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("er_id"),
  KEY "fk_er_evaluacion" ("en_id"),
  KEY "fk_er_recomendacion" ("rt_id"),
  CONSTRAINT "fk_er_evaluacion" FOREIGN KEY ("en_id") REFERENCES "evaluaciones_nutricionales" ("en_id") ON DELETE CASCADE,
  CONSTRAINT "fk_er_recomendacion" FOREIGN KEY ("rt_id") REFERENCES "recomendaciones_tipos" ("rt_id") ON DELETE RESTRICT
)

CREATE TABLE "eventos_auditoria" (
  "eau_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "usr_id" bigint unsigned DEFAULT NULL,
  "eau_entidad" varchar(80) NOT NULL,
  "eau_entidad_id" varchar(64) NOT NULL,
  "eau_accion" varchar(40) NOT NULL,
  "eau_ip" varchar(64) DEFAULT NULL,
  "eau_metadata" json DEFAULT NULL,
  "eau_fecha_hora" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("eau_id"),
  KEY "fk_eau_usuario" ("usr_id"),
  CONSTRAINT "fk_eau_usuario" FOREIGN KEY ("usr_id") REFERENCES "usuarios" ("usr_id") ON DELETE SET NULL
)

CREATE TABLE "features_ml" (
  "fml_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "ant_id" bigint unsigned DEFAULT NULL,
  "fml_bmi_velocity" decimal(6,3) DEFAULT NULL COMMENT 'Cambio IMC últimos 3 meses',
  "fml_weight_velocity" decimal(6,3) DEFAULT NULL COMMENT 'Cambio peso últimos 3 meses (kg)',
  "fml_height_velocity" decimal(6,3) DEFAULT NULL COMMENT 'Cambio talla últimos 3 meses (cm)',
  "fml_baz_trend" decimal(6,3) DEFAULT NULL COMMENT 'Tendencia z-score (positivo=mejora)',
  "fml_measurements_count" smallint unsigned DEFAULT NULL COMMENT 'Número de mediciones históricas',
  "fml_adherence_score" decimal(5,2) DEFAULT NULL COMMENT 'Score adherencia 0-100',
  "fml_adherence_consistency" decimal(5,2) DEFAULT NULL COMMENT 'Consistencia adherencia 0-100',
  "fml_menu_completion_rate" decimal(5,2) DEFAULT NULL COMMENT '% menús completados',
  "fml_allergy_count" smallint unsigned DEFAULT NULL COMMENT 'Total alergias activas',
  "fml_allergy_severity_max" tinyint unsigned DEFAULT NULL COMMENT '1=LEVE, 2=MODERADA, 3=SEVERA',
  "fml_food_allergy_count" smallint unsigned DEFAULT NULL COMMENT 'Alergias alimentarias',
  "fml_has_severe_allergy" tinyint(1) DEFAULT NULL COMMENT 'Tiene alergia severa',
  "fml_symptom_frequency" smallint unsigned DEFAULT NULL COMMENT 'Síntomas últimos 30 días',
  "fml_symptom_severity_avg" decimal(4,2) DEFAULT NULL COMMENT 'Severidad promedio síntomas',
  "fml_has_recent_symptoms" tinyint(1) DEFAULT NULL COMMENT 'Síntomas últimos 7 días',
  "fml_dietary_diversity_score" decimal(5,2) DEFAULT NULL COMMENT 'Score diversidad dietética 0-100',
  "fml_menu_kcal_avg" int DEFAULT NULL COMMENT 'Promedio kcal menús',
  "fml_protein_intake_score" decimal(5,2) DEFAULT NULL COMMENT 'Score ingesta proteica 0-100',
  "fml_calculated_at" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "fml_version" varchar(20) NOT NULL DEFAULT 'v1.0' COMMENT 'Versión del cálculo',
  PRIMARY KEY ("fml_id"),
  KEY "fk_fml_antropometria" ("ant_id"),
  KEY "idx_fml_nino_fecha" ("nin_id","fml_calculated_at"),
  KEY "idx_fml_version" ("fml_version"),
  CONSTRAINT "fk_fml_antropometria" FOREIGN KEY ("ant_id") REFERENCES "antropometrias" ("ant_id") ON DELETE SET NULL,
  CONSTRAINT "fk_fml_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE
)

CREATE TABLE "menus" (
  "men_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "men_generado_por" enum('IA','NUTRICIONISTA') NOT NULL,
  "men_inicio" date NOT NULL,
  "men_fin" date NOT NULL,
  "men_kcal_total" int DEFAULT NULL,
  "men_estado" enum('BORRADOR','APROBADO','ARCHIVADO') NOT NULL DEFAULT 'BORRADOR',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("men_id"),
  KEY "idx_menus_nino_estado" ("nin_id","men_estado","men_inicio"),
  CONSTRAINT "fk_menus_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE
)

CREATE TABLE "menus_items" (
  "mei_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "men_id" bigint unsigned NOT NULL,
  "mei_dia_idx" tinyint unsigned NOT NULL,
  "mei_comida" enum('DESAYUNO','ALMUERZO','CENA','REFACCION') NOT NULL,
  "rec_id" int unsigned NOT NULL,
  "mei_kcal" int DEFAULT NULL,
  "mei_score_ml" decimal(5,4) DEFAULT NULL COMMENT 'Score de confianza del modelo ML (0.0-1.0)',
  PRIMARY KEY ("mei_id"),
  KEY "fk_mei_menu" ("men_id"),
  KEY "fk_mei_receta" ("rec_id"),
  CONSTRAINT "fk_mei_menu" FOREIGN KEY ("men_id") REFERENCES "menus" ("men_id") ON DELETE CASCADE,
  CONSTRAINT "fk_mei_receta" FOREIGN KEY ("rec_id") REFERENCES "recetas" ("rec_id") ON DELETE RESTRICT
)

CREATE TABLE "menus_feedback" (
  "mf_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "mei_id" bigint unsigned NOT NULL COMMENT 'Item del menú evaluado',
  "nin_id" bigint unsigned NOT NULL,
  "mf_completado" tinyint(1) NOT NULL DEFAULT '0' COMMENT '¿Se consumió la comida?',
  "mf_porcentaje_consumido" tinyint DEFAULT NULL COMMENT '0-100% de lo que comió',
  "mf_rating" tinyint DEFAULT NULL COMMENT 'Calificación 1-5 estrellas',
  "mf_notas" text COMMENT 'Comentarios del tutor o niño',
  "mf_fecha_consumo" date NOT NULL,
  "mf_registrado_por" bigint unsigned DEFAULT NULL COMMENT 'Usuario que registró (tutor/nutricionista)',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("mf_id"),
  UNIQUE KEY "uk_feedback_item" ("mei_id","mf_fecha_consumo"),
  KEY "fk_mf_usuario" ("mf_registrado_por"),
  KEY "idx_mf_nino_fecha" ("nin_id","mf_fecha_consumo"),
  KEY "idx_mf_rating" ("mf_rating"),
  CONSTRAINT "fk_mf_item" FOREIGN KEY ("mei_id") REFERENCES "menus_items" ("mei_id") ON DELETE CASCADE,
  CONSTRAINT "fk_mf_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE,
  CONSTRAINT "fk_mf_usuario" FOREIGN KEY ("mf_registrado_por") REFERENCES "usuarios" ("usr_id") ON DELETE SET NULL
)

CREATE TABLE "menus_nutrientes" (
  "mn_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "men_id" bigint unsigned NOT NULL,
  "mn_kcal_total" int DEFAULT NULL COMMENT 'Calorías totales',
  "mn_proteina_g" decimal(8,2) DEFAULT NULL COMMENT 'Proteína en gramos',
  "mn_carbohidratos_g" decimal(8,2) DEFAULT NULL COMMENT 'Carbohidratos en gramos',
  "mn_grasas_g" decimal(8,2) DEFAULT NULL COMMENT 'Grasas en gramos',
  "mn_fibra_g" decimal(8,2) DEFAULT NULL COMMENT 'Fibra en gramos',
  "mn_hierro_mg" decimal(8,2) DEFAULT NULL COMMENT 'Hierro en mg',
  "mn_calcio_mg" decimal(8,2) DEFAULT NULL COMMENT 'Calcio en mg',
  "mn_vitamina_a_ug" decimal(8,2) DEFAULT NULL COMMENT 'Vitamina A en µg',
  "mn_vitamina_c_mg" decimal(8,2) DEFAULT NULL COMMENT 'Vitamina C en mg',
  "mn_zinc_mg" decimal(8,2) DEFAULT NULL COMMENT 'Zinc en mg',
  "mn_diversity_score" decimal(5,2) DEFAULT NULL COMMENT 'Score de diversidad 0-100',
  "mn_quality_score" decimal(5,2) DEFAULT NULL COMMENT 'Score de calidad nutricional 0-100',
  "calculado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("mn_id"),
  UNIQUE KEY "uk_menu_nutrientes" ("men_id"),
  CONSTRAINT "fk_mn_menu" FOREIGN KEY ("men_id") REFERENCES "menus" ("men_id") ON DELETE CASCADE
)

CREATE TABLE "ninos" (
  "nin_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "usr_id_tutor" bigint unsigned DEFAULT NULL,
  "usr_id_propietario" bigint unsigned DEFAULT NULL,
  "ent_id" int unsigned DEFAULT NULL,
  "nin_nombres" varchar(150) NOT NULL,
  "nin_fecha_nac" date NOT NULL,
  "nin_sexo" enum('M','F') NOT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("nin_id"),
  KEY "idx_ninos_tutor" ("usr_id_tutor"),
  KEY "idx_ninos_entidad" ("ent_id"),
  KEY "idx_ninos_propietario" ("usr_id_propietario"),
  FULLTEXT KEY "ft_nin_nombres" ("nin_nombres"),
  FULLTEXT KEY "idx_ft_nombres" ("nin_nombres"),
  CONSTRAINT "fk_ninos_entidad" FOREIGN KEY ("ent_id") REFERENCES "entidades" ("ent_id") ON DELETE SET NULL,
  CONSTRAINT "fk_ninos_propietario" FOREIGN KEY ("usr_id_propietario") REFERENCES "usuarios" ("usr_id") ON DELETE SET NULL,
  CONSTRAINT "fk_ninos_tutor" FOREIGN KEY ("usr_id_tutor") REFERENCES "usuarios" ("usr_id") ON DELETE RESTRICT
)

CREATE TABLE "ninos_alergias" (
  "na_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "ta_id" smallint unsigned NOT NULL,
  "na_severidad" enum('LEVE','MODERADA','SEVERA') NOT NULL DEFAULT 'LEVE',
  "na_activo" tinyint(1) NOT NULL DEFAULT '1',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("na_id"),
  UNIQUE KEY "uk_nino_alergia" ("nin_id","ta_id"),
  KEY "fk_na_tipo" ("ta_id"),
  CONSTRAINT "fk_na_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE,
  CONSTRAINT "fk_na_tipo" FOREIGN KEY ("ta_id") REFERENCES "tipos_alergias" ("ta_id") ON DELETE RESTRICT
)

CREATE TABLE "ninos_comidas_favoritas" (
  "ncf_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "rec_id" int unsigned NOT NULL,
  "ncf_notas" varchar(255) DEFAULT NULL COMMENT 'Notas sobre por qué le gusta',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("ncf_id"),
  UNIQUE KEY "uk_ncf_nino_receta" ("nin_id","rec_id"),
  KEY "idx_ncf_nino" ("nin_id"),
  KEY "idx_ncf_receta" ("rec_id"),
  CONSTRAINT "fk_ncf_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE,
  CONSTRAINT "fk_ncf_receta" FOREIGN KEY ("rec_id") REFERENCES "recetas" ("rec_id") ON DELETE CASCADE
)

CREATE TABLE "ninos_preferencias_comidas" (
  "npc_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "npc_tipo_comida" enum('DESAYUNO','ALMUERZO','CENA','SNACKS') NOT NULL,
  "npc_preferencia" varchar(100) NOT NULL COMMENT 'Nombre de la preferencia: Avena, Huevos, Frutas, etc.',
  "npc_activo" tinyint(1) NOT NULL DEFAULT '1',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("npc_id"),
  KEY "idx_npc_nino_tipo" ("nin_id","npc_tipo_comida"),
  KEY "idx_npc_activo" ("npc_activo"),
  KEY "idx_npc_tipo_comida" ("npc_tipo_comida"),
  CONSTRAINT "fk_npc_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE
)

CREATE TABLE "ninos_restricciones_alimentos" (
  "nra_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "ali_id" int unsigned NOT NULL COMMENT 'Alimento específico restringido',
  "nra_tipo" enum('ALERGIA','INTOLERANCIA','PREFERENCIA','CULTURAL','RELIGIOSA','MEDICA') NOT NULL,
  "nra_severidad" enum('LEVE','MODERADA','SEVERA') NOT NULL DEFAULT 'MODERADA',
  "nra_notas" text COMMENT 'Detalles adicionales de la restricción',
  "nra_activo" tinyint(1) NOT NULL DEFAULT '1',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("nra_id"),
  UNIQUE KEY "uk_nino_alimento" ("nin_id","ali_id"),
  KEY "fk_nra_alimento" ("ali_id"),
  KEY "idx_nra_tipo" ("nra_tipo"),
  KEY "idx_nra_activo" ("nra_activo"),
  CONSTRAINT "fk_nra_alimento" FOREIGN KEY ("ali_id") REFERENCES "alimentos" ("ali_id") ON DELETE CASCADE,
  CONSTRAINT "fk_nra_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE
)

CREATE TABLE "notificaciones" (
  "not_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "usr_id" bigint unsigned NOT NULL,
  "not_tipo" varchar(60) NOT NULL,
  "not_payload" json NOT NULL,
  "not_estado" enum('PENDIENTE','ENVIADO','FALLADO') NOT NULL DEFAULT 'PENDIENTE',
  "not_enviado_en" datetime DEFAULT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("not_id"),
  KEY "fk_not_usuario" ("usr_id"),
  CONSTRAINT "fk_not_usuario" FOREIGN KEY ("usr_id") REFERENCES "usuarios" ("usr_id") ON DELETE CASCADE
)

CREATE TABLE "nutricionistas" (
  "nut_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "usr_id" bigint unsigned NOT NULL,
  "ent_id" int unsigned DEFAULT NULL,
  "nut_colegiatura" varchar(40) DEFAULT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("nut_id"),
  KEY "idx_nut_usuario" ("usr_id"),
  KEY "idx_nut_entidad" ("ent_id"),
  CONSTRAINT "fk_nutricionistas_entidad" FOREIGN KEY ("ent_id") REFERENCES "entidades" ("ent_id") ON DELETE SET NULL,
  CONSTRAINT "fk_nutricionistas_usuario" FOREIGN KEY ("usr_id") REFERENCES "usuarios" ("usr_id") ON DELETE CASCADE
)

CREATE TABLE "nutrientes" (
  "nutri_id" smallint unsigned NOT NULL AUTO_INCREMENT,
  "nutri_codigo" varchar(32) NOT NULL,
  "nutri_nombre" varchar(120) NOT NULL,
  "nutri_unidad" varchar(16) NOT NULL,
  PRIMARY KEY ("nutri_id"),
  UNIQUE KEY "nutri_codigo" ("nutri_codigo")
)

CREATE TABLE "oms_bmi_lms" (
  "version" enum('OMS_2006','OMS_2007') NOT NULL,
  "sexo" enum('M','F') NOT NULL,
  "edad_meses" smallint unsigned NOT NULL,
  "L" decimal(8,4) NOT NULL,
  "M" decimal(8,4) NOT NULL,
  "S" decimal(8,4) NOT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("version","sexo","edad_meses"),
  CONSTRAINT "oms_bmi_lms_chk_1" CHECK ((`edad_meses` between 0 and 228))
)

CREATE TABLE "oms_bmi_percentiles" (
  "lms_version" enum('OMS_2006','OMS_2007') NOT NULL,
  "lms_sexo" enum('M','F') NOT NULL,
  "lms_edad_meses" smallint unsigned NOT NULL,
  "P01" decimal(6,2) DEFAULT NULL,
  "P1" decimal(6,2) DEFAULT NULL,
  "P3" decimal(6,2) DEFAULT NULL,
  "P5" decimal(6,2) DEFAULT NULL,
  "P10" decimal(6,2) DEFAULT NULL,
  "P15" decimal(6,2) DEFAULT NULL,
  "P25" decimal(6,2) DEFAULT NULL,
  "P50" decimal(6,2) DEFAULT NULL,
  "P75" decimal(6,2) DEFAULT NULL,
  "P85" decimal(6,2) DEFAULT NULL,
  "P90" decimal(6,2) DEFAULT NULL,
  "P95" decimal(6,2) DEFAULT NULL,
  "P97" decimal(6,2) DEFAULT NULL,
  "P99" decimal(6,2) DEFAULT NULL,
  "P999" decimal(6,2) DEFAULT NULL,
  "pct_1" decimal(6,2) DEFAULT NULL,
  "pct_3" decimal(6,2) DEFAULT NULL,
  "pct_5" decimal(6,2) DEFAULT NULL,
  "pct_15" decimal(6,2) DEFAULT NULL,
  "pct_25" decimal(6,2) DEFAULT NULL,
  "pct_50" decimal(6,2) DEFAULT NULL,
  "pct_75" decimal(6,2) DEFAULT NULL,
  "pct_85" decimal(6,2) DEFAULT NULL,
  "pct_95" decimal(6,2) DEFAULT NULL,
  "pct_97" decimal(6,2) DEFAULT NULL,
  "pct_99" decimal(6,2) DEFAULT NULL,
  PRIMARY KEY ("lms_version","lms_sexo","lms_edad_meses"),
  CONSTRAINT "fk_p_lms" FOREIGN KEY ("lms_version", "lms_sexo", "lms_edad_meses") REFERENCES "oms_bmi_lms" ("version", "sexo", "edad_meses") ON DELETE CASCADE
)

CREATE TABLE "oms_bmi_zscores" (
  "lms_version" enum('OMS_2006','OMS_2007') NOT NULL,
  "lms_sexo" enum('M','F') NOT NULL,
  "lms_edad_meses" smallint unsigned NOT NULL,
  "sd_m3" decimal(6,2) DEFAULT NULL,
  "sd_m2" decimal(6,2) DEFAULT NULL,
  "sd_m1" decimal(6,2) DEFAULT NULL,
  "median" decimal(6,2) DEFAULT NULL,
  "sd_p1" decimal(6,2) DEFAULT NULL,
  "sd_p2" decimal(6,2) DEFAULT NULL,
  "sd_p3" decimal(6,2) DEFAULT NULL,
  PRIMARY KEY ("lms_version","lms_sexo","lms_edad_meses"),
  CONSTRAINT "fk_z_lms" FOREIGN KEY ("lms_version", "lms_sexo", "lms_edad_meses") REFERENCES "oms_bmi_lms" ("version", "sexo", "edad_meses") ON DELETE CASCADE
)

CREATE TABLE "perfil_nutricional_nino" (
  "pnn_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "pnn_calorias_diarias" int NOT NULL COMMENT 'kcal/día según edad y clasificación',
  "pnn_proteinas_g" decimal(6,2) NOT NULL COMMENT 'Gramos de proteína/día',
  "pnn_carbohidratos_g" decimal(6,2) NOT NULL COMMENT 'Gramos de carbohidratos/día',
  "pnn_grasas_g" decimal(6,2) NOT NULL COMMENT 'Gramos de grasa/día',
  "pnn_hierro_mg" decimal(6,2) DEFAULT NULL COMMENT 'Hierro en mg/día',
  "pnn_calcio_mg" decimal(6,2) DEFAULT NULL COMMENT 'Calcio en mg/día',
  "pnn_vitamina_a_ug" decimal(6,2) DEFAULT NULL COMMENT 'Vitamina A en µg/día',
  "pnn_vitamina_c_mg" decimal(6,2) DEFAULT NULL COMMENT 'Vitamina C en mg/día',
  "pnn_zinc_mg" decimal(6,2) DEFAULT NULL COMMENT 'Zinc en mg/día',
  "pnn_fibra_g" decimal(6,2) DEFAULT NULL COMMENT 'Fibra en g/día',
  "pnn_edad_meses" smallint unsigned NOT NULL COMMENT 'Edad al momento del cálculo',
  "pnn_peso_kg" decimal(5,2) DEFAULT NULL COMMENT 'Peso usado en el cálculo',
  "pnn_talla_cm" decimal(5,2) DEFAULT NULL COMMENT 'Talla usada en el cálculo',
  "pnn_clasificacion" enum('DESNUTRICION_SEVERA','DESNUTRICION','RIESGO','NORMAL','SOBREPESO','OBESIDAD') DEFAULT NULL,
  "pnn_metodo_calculo" varchar(50) NOT NULL DEFAULT 'OMS_FAO' COMMENT 'Método: OMS_FAO, HARRIS_BENEDICT, etc',
  "pnn_factor_actividad" decimal(3,2) DEFAULT '1.50' COMMENT 'Factor de actividad física',
  "pnn_observaciones" text,
  "pnn_vigente" tinyint(1) NOT NULL DEFAULT '1' COMMENT 'Solo un perfil vigente por niño',
  "pnn_fecha_calculo" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("pnn_id"),
  KEY "idx_pnn_nino_vigente" ("nin_id","pnn_vigente"),
  KEY "idx_pnn_clasificacion" ("pnn_clasificacion"),
  CONSTRAINT "fk_pnn_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE
)

CREATE TABLE "predicciones_ml" (
  "pml_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "ant_id" bigint unsigned DEFAULT NULL,
  "fml_id" bigint unsigned DEFAULT NULL,
  "pml_clasificacion" enum('DESNUTRICION_SEVERA','DESNUTRICION_MODERADA','RIESGO_DESNUTRICION','NORMAL','RIESGO_SOBREPESO','SOBREPESO','OBESIDAD') NOT NULL COMMENT 'Clasificación nutricional predicha (7 categorías)',
  "pml_probabilidad" decimal(5,4) NOT NULL COMMENT 'Probabilidad de la clase predicha',
  "pml_score_riesgo" decimal(6,4) NOT NULL COMMENT 'Score de riesgo 0-1',
  "pml_prob_normal" decimal(5,4) DEFAULT NULL,
  "pml_prob_riesgo" decimal(5,4) DEFAULT NULL,
  "pml_prob_moderado" decimal(5,4) DEFAULT NULL,
  "pml_prob_severo" decimal(5,4) DEFAULT NULL,
  "pml_modelo_tipo" varchar(50) NOT NULL COMMENT 'rf, nn, ensemble',
  "pml_modelo_version" varchar(20) NOT NULL COMMENT 'Versión del modelo',
  "pml_features_json" json DEFAULT NULL COMMENT 'Features usados en la predicción',
  "pml_explicacion_json" json DEFAULT NULL COMMENT 'SHAP values o feature importance',
  "pml_validado" tinyint(1) DEFAULT NULL COMMENT 'Validado por nutricionista',
  "pml_validado_por" bigint unsigned DEFAULT NULL COMMENT 'usr_id del nutricionista',
  "pml_validado_en" datetime DEFAULT NULL,
  "pml_feedback" text COMMENT 'Feedback del nutricionista',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("pml_id"),
  KEY "fk_pml_antropometria" ("ant_id"),
  KEY "fk_pml_features" ("fml_id"),
  KEY "fk_pml_validador" ("pml_validado_por"),
  KEY "idx_pml_nino_fecha" ("nin_id","creado_en"),
  KEY "idx_pml_clasificacion" ("pml_clasificacion"),
  KEY "idx_pml_modelo" ("pml_modelo_tipo","pml_modelo_version"),
  CONSTRAINT "fk_pml_antropometria" FOREIGN KEY ("ant_id") REFERENCES "antropometrias" ("ant_id") ON DELETE SET NULL,
  CONSTRAINT "fk_pml_features" FOREIGN KEY ("fml_id") REFERENCES "features_ml" ("fml_id") ON DELETE SET NULL,
  CONSTRAINT "fk_pml_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE,
  CONSTRAINT "fk_pml_validador" FOREIGN KEY ("pml_validado_por") REFERENCES "usuarios" ("usr_id") ON DELETE SET NULL
)

CREATE TABLE "puntajes_riesgo" (
  "pri_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "pri_fecha_hora" datetime NOT NULL,
  "pri_version" varchar(32) NOT NULL,
  "pri_riesgo" decimal(6,4) NOT NULL,
  "pri_caracteristicas" json DEFAULT NULL,
  PRIMARY KEY ("pri_id"),
  KEY "fk_pri_nino" ("nin_id"),
  CONSTRAINT "fk_pri_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE
)

CREATE TABLE "recetas" (
  "rec_id" int unsigned NOT NULL AUTO_INCREMENT,
  "rec_nombre" varchar(150) NOT NULL,
  "rec_instrucciones" text NOT NULL,
  "rec_activo" tinyint(1) NOT NULL DEFAULT '1',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("rec_id")
)

CREATE TABLE "recetas_comidas" (
  "rec_id" int unsigned NOT NULL,
  "rc_comida" enum('DESAYUNO','ALMUERZO','CENA','REFACCION') NOT NULL,
  PRIMARY KEY ("rec_id","rc_comida"),
  KEY "idx_rc_comida" ("rc_comida"),
  CONSTRAINT "fk_rc_receta" FOREIGN KEY ("rec_id") REFERENCES "recetas" ("rec_id") ON DELETE CASCADE
)

CREATE TABLE "recetas_ingredientes" (
  "rec_id" int unsigned NOT NULL,
  "ali_id" int unsigned NOT NULL,
  "ri_cantidad" decimal(12,4) NOT NULL,
  "ri_unidad" varchar(16) NOT NULL,
  PRIMARY KEY ("rec_id","ali_id"),
  KEY "idx_ri_alimento" ("ali_id"),
  CONSTRAINT "fk_ri_alimento" FOREIGN KEY ("ali_id") REFERENCES "alimentos" ("ali_id") ON DELETE RESTRICT,
  CONSTRAINT "fk_ri_receta" FOREIGN KEY ("rec_id") REFERENCES "recetas" ("rec_id") ON DELETE CASCADE
)

CREATE TABLE "recetas_nutrientes_cache" (
  "rec_id" int unsigned NOT NULL,
  "nutri_id" smallint unsigned NOT NULL,
  "rnc_cantidad_total" decimal(12,4) NOT NULL COMMENT 'Cantidad total del nutriente en la receta',
  "rnc_cantidad_porcion" decimal(12,4) DEFAULT NULL COMMENT 'Por porción estándar (si aplica)',
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("rec_id","nutri_id"),
  KEY "idx_rnc_nutriente" ("nutri_id","rnc_cantidad_total"),
  CONSTRAINT "fk_rnc_nutriente" FOREIGN KEY ("nutri_id") REFERENCES "nutrientes" ("nutri_id") ON DELETE CASCADE,
  CONSTRAINT "fk_rnc_receta" FOREIGN KEY ("rec_id") REFERENCES "recetas" ("rec_id") ON DELETE CASCADE
)

CREATE TABLE "recomendaciones_tipos" (
  "rt_id" smallint unsigned NOT NULL AUTO_INCREMENT,
  "rt_codigo" varchar(30) NOT NULL,
  "rt_titulo" varchar(150) NOT NULL,
  "rt_descripcion" text NOT NULL,
  "rt_clasificacion" enum('DESNUTRICION_SEVERA','DESNUTRICION','RIESGO','NORMAL','SOBREPESO','OBESIDAD') NOT NULL,
  "rt_prioridad" tinyint unsigned NOT NULL DEFAULT '1',
  "rt_activo" tinyint(1) NOT NULL DEFAULT '1',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("rt_id"),
  UNIQUE KEY "rt_codigo" ("rt_codigo")
)

CREATE TABLE "roles" (
  "rol_id" smallint unsigned NOT NULL AUTO_INCREMENT,
  "rol_codigo" varchar(32) NOT NULL,
  "rol_nombre" varchar(80) NOT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("rol_id"),
  UNIQUE KEY "rol_codigo" ("rol_codigo")
)

CREATE TABLE "sintomas" (
  "sin_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "sin_fecha" date NOT NULL,
  "sin_tipo" varchar(120) NOT NULL,
  "sin_grado" tinyint unsigned DEFAULT NULL,
  "sin_severidad" enum('LEVE','MODERADO','SEVERO') DEFAULT NULL COMMENT 'Severidad del síntoma',
  "sin_duracion_dias" smallint unsigned DEFAULT NULL COMMENT 'Duración en días',
  "sin_relacionado_menu" tinyint(1) DEFAULT '0' COMMENT 'Relacionado con menú',
  "sin_notas" text,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("sin_id"),
  KEY "idx_sin_nino_fecha" ("nin_id","sin_fecha"),
  CONSTRAINT "fk_sintomas_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE
)

CREATE TABLE "tipos_alergias" (
  "ta_id" smallint unsigned NOT NULL AUTO_INCREMENT,
  "ta_codigo" varchar(20) NOT NULL,
  "ta_nombre" varchar(100) NOT NULL,
  "ta_categoria" enum('ALIMENTARIA','MEDICAMENTO','AMBIENTAL') NOT NULL,
  "ta_activo" tinyint(1) NOT NULL DEFAULT '1',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("ta_id"),
  UNIQUE KEY "ta_codigo" ("ta_codigo")
)

CREATE TABLE "tokens_revocados" (
  "jti" varchar(64) NOT NULL,
  "usuario" varchar(150) NOT NULL,
  "expira_en" datetime NOT NULL,
  "revocado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY ("jti"),
  KEY "idx_tokens_expira" ("expira_en")
)

CREATE TABLE "tutores" (
  "tut_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "usr_id" bigint unsigned NOT NULL,
  "tut_telefono" varchar(32) DEFAULT NULL,
  "tut_idioma" varchar(10) NOT NULL DEFAULT 'es-PE',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("tut_id"),
  UNIQUE KEY "usr_id" ("usr_id"),
  CONSTRAINT "fk_tutores_usuario" FOREIGN KEY ("usr_id") REFERENCES "usuarios" ("usr_id") ON DELETE CASCADE
)

CREATE TABLE "usuarios" (
  "usr_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "usr_dni" varchar(12) DEFAULT NULL,
  "usr_correo" varchar(190) NOT NULL,
  "usr_contrasena" varchar(255) NOT NULL,
  "usr_nombre" varchar(150) NOT NULL,
  "usr_apellido" varchar(150) NOT NULL,
  "usr_usuario" varchar(150) NOT NULL,
  "rol_id" smallint unsigned NOT NULL,
  "usr_activo" tinyint(1) NOT NULL DEFAULT '1',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  "eliminado_en" datetime DEFAULT NULL,
  PRIMARY KEY ("usr_id"),
  UNIQUE KEY "usr_correo" ("usr_correo"),
  UNIQUE KEY "uk_usuarios_dni" ("usr_dni"),
  KEY "idx_usuarios_rol" ("rol_id"),
  KEY "idx_usuarios_activo" ("usr_activo"),
  CONSTRAINT "fk_usuarios_roles" FOREIGN KEY ("rol_id") REFERENCES "roles" ("rol_id") ON DELETE RESTRICT
)

CREATE TABLE "usuarios_perfil" (
  "usrper_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "usr_id" bigint unsigned NOT NULL,
  "usrper_avatar_url" mediumtext,
  "usrper_telefono" varchar(20) NOT NULL,
  "usrper_direccion" varchar(180) DEFAULT NULL,
  "usrper_genero" enum('M','F','X') DEFAULT NULL,
  "usrper_fecha_nac" date DEFAULT NULL,
  "usrper_idioma" varchar(10) NOT NULL DEFAULT 'es-PE',
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  "eliminado_en" datetime DEFAULT NULL,
  PRIMARY KEY ("usrper_id"),
  UNIQUE KEY "usr_id" ("usr_id"),
  CONSTRAINT "fk_usrper_usuario" FOREIGN KEY ("usr_id") REFERENCES "usuarios" ("usr_id") ON DELETE CASCADE
)

CREATE TABLE "vinculos_nutricionista_nino" (
  "vnn_id" bigint unsigned NOT NULL AUTO_INCREMENT,
  "nin_id" bigint unsigned NOT NULL,
  "nut_id" bigint unsigned NOT NULL,
  "vnn_estado" enum('PENDIENTE','ACTIVO','RECHAZADO') NOT NULL DEFAULT 'PENDIENTE',
  "vnn_desde" date NOT NULL DEFAULT (curdate()),
  "vnn_hasta" date DEFAULT NULL,
  "creado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "actualizado_en" datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY ("vnn_id"),
  UNIQUE KEY "uk_vnn" ("nin_id","nut_id"),
  KEY "fk_vnn_nutri" ("nut_id"),
  CONSTRAINT "fk_vnn_nino" FOREIGN KEY ("nin_id") REFERENCES "ninos" ("nin_id") ON DELETE CASCADE,
  CONSTRAINT "fk_vnn_nutri" FOREIGN KEY ("nut_id") REFERENCES "nutricionistas" ("nut_id") ON DELETE CASCADE
)
