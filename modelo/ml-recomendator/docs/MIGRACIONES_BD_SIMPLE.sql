-- ============================================================================
-- MIGRACIONES DE BASE DE DATOS PARA ML - VERSIÓN SIMPLE
-- Sistema de Evaluación Nutricional con Machine Learning
--
-- INSTRUCCIONES:
-- 1. Ejecutar este script en la base de datos 'nutricion'
-- 2. Si una columna ya existe, simplemente ignorar el error y continuar
-- 3. Las tablas nuevas se crearán solo si no existen
-- ============================================================================

USE nutricion;

-- ============================================================================
-- 1. TABLA: features_ml (NUEVA)
-- ============================================================================

CREATE TABLE IF NOT EXISTS features_ml (
  fml_id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id              BIGINT UNSIGNED NOT NULL,
  ant_id              BIGINT UNSIGNED NULL,

  -- Features temporales
  fml_bmi_velocity    DECIMAL(6,3) NULL COMMENT 'Cambio IMC últimos 3 meses',
  fml_weight_velocity DECIMAL(6,3) NULL COMMENT 'Cambio peso últimos 3 meses (kg)',
  fml_height_velocity DECIMAL(6,3) NULL COMMENT 'Cambio talla últimos 3 meses (cm)',
  fml_baz_trend       DECIMAL(6,3) NULL COMMENT 'Tendencia z-score (positivo=mejora)',
  fml_measurements_count SMALLINT UNSIGNED NULL COMMENT 'Número de mediciones históricas',

  -- Features de adherencia
  fml_adherence_score DECIMAL(5,2) NULL COMMENT 'Score adherencia 0-100',
  fml_adherence_consistency DECIMAL(5,2) NULL COMMENT 'Consistencia adherencia 0-100',
  fml_menu_completion_rate DECIMAL(5,2) NULL COMMENT '% menús completados',

  -- Features de alergias
  fml_allergy_count   SMALLINT UNSIGNED NULL COMMENT 'Total alergias activas',
  fml_allergy_severity_max TINYINT UNSIGNED NULL COMMENT '1=LEVE, 2=MODERADA, 3=SEVERA',
  fml_food_allergy_count SMALLINT UNSIGNED NULL COMMENT 'Alergias alimentarias',
  fml_has_severe_allergy BOOLEAN NULL COMMENT 'Tiene alergia severa',

  -- Features de síntomas
  fml_symptom_frequency SMALLINT UNSIGNED NULL COMMENT 'Síntomas últimos 30 días',
  fml_symptom_severity_avg DECIMAL(4,2) NULL COMMENT 'Severidad promedio síntomas',
  fml_has_recent_symptoms BOOLEAN NULL COMMENT 'Síntomas últimos 7 días',

  -- Features nutricionales
  fml_dietary_diversity_score DECIMAL(5,2) NULL COMMENT 'Score diversidad dietética 0-100',
  fml_menu_kcal_avg INT NULL COMMENT 'Promedio kcal menús',
  fml_protein_intake_score DECIMAL(5,2) NULL COMMENT 'Score ingesta proteica 0-100',

  -- Metadata
  fml_calculated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fml_version         VARCHAR(20) NOT NULL DEFAULT 'v1.0' COMMENT 'Versión del cálculo',

  CONSTRAINT fk_fml_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_fml_antropometria FOREIGN KEY (ant_id) REFERENCES antropometrias(ant_id) ON DELETE SET NULL,
  INDEX idx_fml_nino_fecha (nin_id, fml_calculated_at),
  INDEX idx_fml_version (fml_version)
) ENGINE=InnoDB COMMENT='Features calculados para ML';


-- ============================================================================
-- 2. TABLA: menus_nutrientes (NUEVA)
-- ============================================================================

CREATE TABLE IF NOT EXISTS menus_nutrientes (
  mn_id       BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  men_id      BIGINT UNSIGNED NOT NULL,

  -- Macronutrientes
  mn_kcal_total      INT NULL COMMENT 'Calorías totales',
  mn_proteina_g      DECIMAL(8,2) NULL COMMENT 'Proteína en gramos',
  mn_carbohidratos_g DECIMAL(8,2) NULL COMMENT 'Carbohidratos en gramos',
  mn_grasas_g        DECIMAL(8,2) NULL COMMENT 'Grasas en gramos',
  mn_fibra_g         DECIMAL(8,2) NULL COMMENT 'Fibra en gramos',

  -- Micronutrientes clave
  mn_hierro_mg       DECIMAL(8,2) NULL COMMENT 'Hierro en mg',
  mn_calcio_mg       DECIMAL(8,2) NULL COMMENT 'Calcio en mg',
  mn_vitamina_a_ug   DECIMAL(8,2) NULL COMMENT 'Vitamina A en µg',
  mn_vitamina_c_mg   DECIMAL(8,2) NULL COMMENT 'Vitamina C en mg',
  mn_zinc_mg         DECIMAL(8,2) NULL COMMENT 'Zinc en mg',

  -- Scores calculados
  mn_diversity_score DECIMAL(5,2) NULL COMMENT 'Score de diversidad 0-100',
  mn_quality_score   DECIMAL(5,2) NULL COMMENT 'Score de calidad nutricional 0-100',

  calculado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_mn_menu FOREIGN KEY (men_id) REFERENCES menus(men_id) ON DELETE CASCADE,
  UNIQUE KEY uk_menu_nutrientes (men_id)
) ENGINE=InnoDB COMMENT='Información nutricional calculada de menús';


-- ============================================================================
-- 3. TABLA: predicciones_ml (NUEVA)
-- ============================================================================

CREATE TABLE IF NOT EXISTS predicciones_ml (
  pml_id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id              BIGINT UNSIGNED NOT NULL,
  ant_id              BIGINT UNSIGNED NULL,
  fml_id              BIGINT UNSIGNED NULL,

  -- Predicción
  pml_clasificacion   ENUM('NORMAL','RIESGO','MODERADO','SEVERO') NOT NULL,
  pml_probabilidad    DECIMAL(5,4) NOT NULL COMMENT 'Probabilidad de la clase predicha',
  pml_score_riesgo    DECIMAL(6,4) NOT NULL COMMENT 'Score de riesgo 0-1',

  -- Probabilidades por clase
  pml_prob_normal     DECIMAL(5,4) NULL,
  pml_prob_riesgo     DECIMAL(5,4) NULL,
  pml_prob_moderado   DECIMAL(5,4) NULL,
  pml_prob_severo     DECIMAL(5,4) NULL,

  -- Metadata del modelo
  pml_modelo_tipo     VARCHAR(50) NOT NULL COMMENT 'rf, nn, ensemble',
  pml_modelo_version  VARCHAR(20) NOT NULL COMMENT 'Versión del modelo',
  pml_features_json   JSON NULL COMMENT 'Features usados en la predicción',
  pml_explicacion_json JSON NULL COMMENT 'SHAP values o feature importance',

  -- Validación por nutricionista
  pml_validado        BOOLEAN NULL COMMENT 'Validado por nutricionista',
  pml_validado_por    BIGINT UNSIGNED NULL COMMENT 'usr_id del nutricionista',
  pml_validado_en     DATETIME NULL,
  pml_feedback        TEXT NULL COMMENT 'Feedback del nutricionista',

  creado_en           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_pml_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_pml_antropometria FOREIGN KEY (ant_id) REFERENCES antropometrias(ant_id) ON DELETE SET NULL,
  CONSTRAINT fk_pml_features FOREIGN KEY (fml_id) REFERENCES features_ml(fml_id) ON DELETE SET NULL,
  CONSTRAINT fk_pml_validador FOREIGN KEY (pml_validado_por) REFERENCES usuarios(usr_id) ON DELETE SET NULL,

  INDEX idx_pml_nino_fecha (nin_id, creado_en),
  INDEX idx_pml_clasificacion (pml_clasificacion),
  INDEX idx_pml_modelo (pml_modelo_tipo, pml_modelo_version)
) ENGINE=InnoDB COMMENT='Predicciones del modelo ML';


-- ============================================================================
-- 4. MODIFICAR TABLA: entidades
-- ============================================================================

-- Nota: Si alguna columna ya existe, el ALTER TABLE fallará pero puedes continuar
-- Ejecuta cada ALTER TABLE por separado si es necesario

-- Agregar ent_altitud_m
ALTER TABLE entidades
ADD COLUMN ent_altitud_m INT NULL
COMMENT 'Altitud en metros sobre nivel del mar'
AFTER ent_longitud;

-- Agregar ent_zona
ALTER TABLE entidades
ADD COLUMN ent_zona ENUM('URBANA','RURAL','PERIURBANA') NULL
COMMENT 'Tipo de zona'
AFTER ent_altitud_m;

-- Agregar ent_poblacion_aprox
ALTER TABLE entidades
ADD COLUMN ent_poblacion_aprox INT NULL
COMMENT 'Población aproximada del área'
AFTER ent_zona;

-- Crear índice
CREATE INDEX idx_entidades_zona ON entidades(ent_zona);


-- ============================================================================
-- 5. MODIFICAR TABLA: adherencias
-- ============================================================================

-- Agregar adh_porcentaje
ALTER TABLE adherencias
ADD COLUMN adh_porcentaje DECIMAL(5,2) NULL
COMMENT 'Porcentaje de adherencia 0-100'
AFTER adh_estado;

-- Agregar adh_comentario_tutor
ALTER TABLE adherencias
ADD COLUMN adh_comentario_tutor TEXT NULL
COMMENT 'Comentario del tutor'
AFTER adh_notas;

-- Agregar adh_dificultad
ALTER TABLE adherencias
ADD COLUMN adh_dificultad ENUM('NINGUNA','BAJA','MEDIA','ALTA') NULL
COMMENT 'Dificultad reportada'
AFTER adh_comentario_tutor;

-- Crear índice
CREATE INDEX idx_adh_nino_fecha ON adherencias(nin_id, adh_registrado_en);


-- ============================================================================
-- 6. MODIFICAR TABLA: sintomas
-- ============================================================================

-- Agregar sin_severidad
ALTER TABLE sintomas
ADD COLUMN sin_severidad ENUM('LEVE','MODERADO','SEVERO') NULL
COMMENT 'Severidad del síntoma'
AFTER sin_grado;

-- Agregar sin_duracion_dias
ALTER TABLE sintomas
ADD COLUMN sin_duracion_dias SMALLINT UNSIGNED NULL
COMMENT 'Duración en días'
AFTER sin_severidad;

-- Agregar sin_relacionado_menu
ALTER TABLE sintomas
ADD COLUMN sin_relacionado_menu BOOLEAN NULL DEFAULT FALSE
COMMENT 'Relacionado con menú'
AFTER sin_duracion_dias;

-- Crear índice
CREATE INDEX idx_sin_nino_fecha ON sintomas(nin_id, sin_fecha);


-- ============================================================================
-- 7. MODIFICAR TABLA: antropometrias
-- ============================================================================

-- Agregar ant_edad_meses
ALTER TABLE antropometrias
ADD COLUMN ant_edad_meses SMALLINT UNSIGNED NULL
COMMENT 'Edad en meses al momento de la medición'
AFTER ant_fecha;


-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

-- Verificar tablas creadas
SELECT 'Verificando tablas nuevas...' AS mensaje;

SELECT
  CASE
    WHEN COUNT(*) = 3 THEN '✅ Todas las tablas nuevas creadas correctamente'
    ELSE '⚠️ Faltan tablas por crear'
  END AS resultado
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'nutricion'
  AND TABLE_NAME IN ('features_ml', 'menus_nutrientes', 'predicciones_ml');

-- Verificar columnas agregadas a entidades
SELECT
  CASE
    WHEN COUNT(*) >= 3 THEN '✅ Columnas de entidades agregadas'
    ELSE '⚠️ Faltan columnas en entidades'
  END AS resultado
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'nutricion'
  AND TABLE_NAME = 'entidades'
  AND COLUMN_NAME IN ('ent_altitud_m', 'ent_zona', 'ent_poblacion_aprox');

-- Verificar columnas agregadas a adherencias
SELECT
  CASE
    WHEN COUNT(*) >= 3 THEN '✅ Columnas de adherencias agregadas'
    ELSE '⚠️ Faltan columnas en adherencias'
  END AS resultado
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'nutricion'
  AND TABLE_NAME = 'adherencias'
  AND COLUMN_NAME IN ('adh_porcentaje', 'adh_comentario_tutor', 'adh_dificultad');

-- Verificar columnas agregadas a sintomas
SELECT
  CASE
    WHEN COUNT(*) >= 3 THEN '✅ Columnas de sintomas agregadas'
    ELSE '⚠️ Faltan columnas en sintomas'
  END AS resultado
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'nutricion'
  AND TABLE_NAME = 'sintomas'
  AND COLUMN_NAME IN ('sin_severidad', 'sin_duracion_dias', 'sin_relacionado_menu');

-- Verificar columna agregada a antropometrias
SELECT
  CASE
    WHEN COUNT(*) >= 1 THEN '✅ Columna de antropometrias agregada'
    ELSE '⚠️ Falta columna en antropometrias'
  END AS resultado
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'nutricion'
  AND TABLE_NAME = 'antropometrias'
  AND COLUMN_NAME = 'ant_edad_meses';

SELECT '✅ Migraciones completadas. Revisa los resultados arriba.' AS mensaje;


-- ============================================================================
-- FIN DE MIGRACIONES
-- ============================================================================
