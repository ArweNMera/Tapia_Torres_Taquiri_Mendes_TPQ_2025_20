-- ============================================================================
-- PROCEDIMIENTOS ALMACENADOS PARA ML
-- Sistema de Evaluación Nutricional
-- ============================================================================

USE nutricion;

DELIMITER $$

-- ============================================================================
-- sp_calcular_features_ml
-- Calcula todos los features ML para un niño específico
-- ============================================================================

DROP PROCEDURE IF EXISTS sp_calcular_features_ml$$

CREATE PROCEDURE sp_calcular_features_ml(
  IN p_nin_id BIGINT UNSIGNED,
  IN p_ant_id BIGINT UNSIGNED
)
BEGIN
  DECLARE v_bmi_velocity DECIMAL(6,3) DEFAULT 0;
  DECLARE v_weight_velocity DECIMAL(6,3) DEFAULT 0;
  DECLARE v_height_velocity DECIMAL(6,3) DEFAULT 0;
  DECLARE v_baz_trend DECIMAL(6,3) DEFAULT 0;
  DECLARE v_measurements_count SMALLINT DEFAULT 0;
  
  DECLARE v_adherence_score DECIMAL(5,2) DEFAULT 75.0;
  DECLARE v_adherence_consistency DECIMAL(5,2) DEFAULT 70.0;
  DECLARE v_menu_completion_rate DECIMAL(5,2) DEFAULT 80.0;
  
  DECLARE v_allergy_count SMALLINT DEFAULT 0;
  DECLARE v_allergy_severity_max TINYINT DEFAULT 0;
  DECLARE v_food_allergy_count SMALLINT DEFAULT 0;
  DECLARE v_has_severe_allergy BOOLEAN DEFAULT FALSE;
  
  DECLARE v_symptom_frequency SMALLINT DEFAULT 0;
  DECLARE v_symptom_severity_avg DECIMAL(4,2) DEFAULT 0;
  DECLARE v_has_recent_symptoms BOOLEAN DEFAULT FALSE;
  
  DECLARE v_dietary_diversity_score DECIMAL(5,2) DEFAULT 60.0;
  DECLARE v_menu_kcal_avg INT DEFAULT 1500;
  DECLARE v_protein_intake_score DECIMAL(5,2) DEFAULT 65.0;
  
  DECLARE v_ant_fecha DATE;
  DECLARE v_ant_fecha_anterior DATE;
  DECLARE v_bmi_actual DECIMAL(5,2);
  DECLARE v_bmi_anterior DECIMAL(5,2);
  DECLARE v_peso_actual DECIMAL(5,2);
  DECLARE v_peso_anterior DECIMAL(5,2);
  DECLARE v_talla_actual DECIMAL(5,2);
  DECLARE v_talla_anterior DECIMAL(5,2);
  DECLARE v_baz_actual DECIMAL(6,3);
  DECLARE v_baz_anterior DECIMAL(6,3);
  DECLARE v_meses_diff INT;
  
  -- ========================================
  -- 1. FEATURES TEMPORALES (Velocidades y Tendencias)
  -- ========================================
  
  -- Obtener datos de antropometría actual
  SELECT 
    ant_fecha,
    ant_peso_kg,
    ant_talla_cm,
    ant_peso_kg / POWER(ant_talla_cm / 100, 2) as bmi,
    COALESCE(ant_z_imc, 0)
  INTO 
    v_ant_fecha,
    v_peso_actual,
    v_talla_actual,
    v_bmi_actual,
    v_baz_actual
  FROM antropometrias
  WHERE ant_id = p_ant_id;
  
  -- Contar mediciones históricas
  SELECT COUNT(*) INTO v_measurements_count
  FROM antropometrias
  WHERE nin_id = p_nin_id;
  
  -- Obtener antropometría de hace 3 meses (aproximadamente)
  SELECT 
    ant_fecha,
    ant_peso_kg,
    ant_talla_cm,
    ant_peso_kg / POWER(ant_talla_cm / 100, 2) as bmi,
    COALESCE(ant_z_imc, 0)
  INTO 
    v_ant_fecha_anterior,
    v_peso_anterior,
    v_talla_anterior,
    v_bmi_anterior,
    v_baz_anterior
  FROM antropometrias
  WHERE nin_id = p_nin_id
    AND ant_fecha < v_ant_fecha
    AND ant_fecha >= DATE_SUB(v_ant_fecha, INTERVAL 4 MONTH)
  ORDER BY ant_fecha DESC
  LIMIT 1;
  
  -- Calcular velocidades si hay datos anteriores
  IF v_ant_fecha_anterior IS NOT NULL THEN
    SET v_meses_diff = TIMESTAMPDIFF(MONTH, v_ant_fecha_anterior, v_ant_fecha);
    
    IF v_meses_diff > 0 THEN
      SET v_bmi_velocity = (v_bmi_actual - v_bmi_anterior) / v_meses_diff * 3;
      SET v_weight_velocity = (v_peso_actual - v_peso_anterior) / v_meses_diff * 3;
      SET v_height_velocity = (v_talla_actual - v_talla_anterior) / v_meses_diff * 3;
      SET v_baz_trend = (v_baz_actual - v_baz_anterior) / v_meses_diff * 3;
    END IF;
  END IF;
  
  -- ========================================
  -- 2. FEATURES DE ADHERENCIA
  -- ========================================
  
  -- Calcular score de adherencia (últimos 30 días)
  SELECT 
    AVG(CASE adh_estado
      WHEN 'OK' THEN 100
      WHEN 'PARCIAL' THEN 50
      WHEN 'NO' THEN 0
      ELSE 75
    END),
    STDDEV(CASE adh_estado
      WHEN 'OK' THEN 100
      WHEN 'PARCIAL' THEN 50
      WHEN 'NO' THEN 0
      ELSE 75
    END),
    COUNT(*)
  INTO 
    v_adherence_score,
    v_adherence_consistency,
    v_menu_completion_rate
  FROM adherencias
  WHERE nin_id = p_nin_id
    AND adh_registrado_en >= DATE_SUB(NOW(), INTERVAL 30 DAY);
  
  -- Ajustar valores por defecto si no hay datos
  SET v_adherence_score = COALESCE(v_adherence_score, 75.0);
  SET v_adherence_consistency = COALESCE(100 - v_adherence_consistency, 70.0);
  SET v_menu_completion_rate = COALESCE(v_menu_completion_rate * 10, 80.0);
  
  -- ========================================
  -- 3. FEATURES DE ALERGIAS
  -- ========================================
  
  -- Contar alergias activas
  SELECT 
    COUNT(*),
    MAX(CASE na_severidad
      WHEN 'LEVE' THEN 1
      WHEN 'MODERADA' THEN 2
      WHEN 'SEVERA' THEN 3
      ELSE 0
    END),
    SUM(CASE 
      WHEN ta.ta_categoria = 'ALIMENTARIA' THEN 1 
      ELSE 0 
    END),
    MAX(CASE 
      WHEN na_severidad = 'SEVERA' THEN 1 
      ELSE 0 
    END)
  INTO 
    v_allergy_count,
    v_allergy_severity_max,
    v_food_allergy_count,
    v_has_severe_allergy
  FROM ninos_alergias na
  JOIN tipos_alergias ta ON na.ta_id = ta.ta_id
  WHERE na.nin_id = p_nin_id 
    AND na.na_activo = 1;
  
  SET v_allergy_count = COALESCE(v_allergy_count, 0);
  SET v_allergy_severity_max = COALESCE(v_allergy_severity_max, 0);
  SET v_food_allergy_count = COALESCE(v_food_allergy_count, 0);
  SET v_has_severe_allergy = COALESCE(v_has_severe_allergy, FALSE);
  
  -- ========================================
  -- 4. FEATURES DE SÍNTOMAS
  -- ========================================
  
  -- Frecuencia de síntomas (últimos 30 días)
  SELECT 
    COUNT(*),
    AVG(COALESCE(sin_grado, 0)),
    MAX(CASE 
      WHEN sin_fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 
      ELSE 0 
    END)
  INTO 
    v_symptom_frequency,
    v_symptom_severity_avg,
    v_has_recent_symptoms
  FROM sintomas
  WHERE nin_id = p_nin_id
    AND sin_fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY);
  
  SET v_symptom_frequency = COALESCE(v_symptom_frequency, 0);
  SET v_symptom_severity_avg = COALESCE(v_symptom_severity_avg, 0);
  SET v_has_recent_symptoms = COALESCE(v_has_recent_symptoms, FALSE);
  
  -- ========================================
  -- 5. FEATURES NUTRICIONALES
  -- ========================================
  
  -- Calcular promedio de kcal de menús activos
  SELECT 
    AVG(COALESCE(men_kcal_total, 1500))
  INTO 
    v_menu_kcal_avg
  FROM menus
  WHERE nin_id = p_nin_id
    AND men_estado IN ('APROBADO', 'BORRADOR')
    AND men_fin >= CURDATE();
  
  SET v_menu_kcal_avg = COALESCE(v_menu_kcal_avg, 1500);
  
  -- Scores nutricionales (simplificados por ahora)
  -- TODO: Calcular desde menus_nutrientes cuando esté poblado
  SET v_dietary_diversity_score = 60.0;
  SET v_protein_intake_score = 65.0;
  
  -- ========================================
  -- 6. INSERTAR O ACTUALIZAR FEATURES
  -- ========================================
  
  INSERT INTO features_ml (
    nin_id,
    ant_id,
    fml_bmi_velocity,
    fml_weight_velocity,
    fml_height_velocity,
    fml_baz_trend,
    fml_measurements_count,
    fml_adherence_score,
    fml_adherence_consistency,
    fml_menu_completion_rate,
    fml_allergy_count,
    fml_allergy_severity_max,
    fml_food_allergy_count,
    fml_has_severe_allergy,
    fml_symptom_frequency,
    fml_symptom_severity_avg,
    fml_has_recent_symptoms,
    fml_dietary_diversity_score,
    fml_menu_kcal_avg,
    fml_protein_intake_score,
    fml_calculated_at,
    fml_version
  ) VALUES (
    p_nin_id,
    p_ant_id,
    v_bmi_velocity,
    v_weight_velocity,
    v_height_velocity,
    v_baz_trend,
    v_measurements_count,
    v_adherence_score,
    v_adherence_consistency,
    v_menu_completion_rate,
    v_allergy_count,
    v_allergy_severity_max,
    v_food_allergy_count,
    v_has_severe_allergy,
    v_symptom_frequency,
    v_symptom_severity_avg,
    v_has_recent_symptoms,
    v_dietary_diversity_score,
    v_menu_kcal_avg,
    v_protein_intake_score,
    NOW(),
    'v1.0'
  )
  ON DUPLICATE KEY UPDATE
    fml_bmi_velocity = v_bmi_velocity,
    fml_weight_velocity = v_weight_velocity,
    fml_height_velocity = v_height_velocity,
    fml_baz_trend = v_baz_trend,
    fml_measurements_count = v_measurements_count,
    fml_adherence_score = v_adherence_score,
    fml_adherence_consistency = v_adherence_consistency,
    fml_menu_completion_rate = v_menu_completion_rate,
    fml_allergy_count = v_allergy_count,
    fml_allergy_severity_max = v_allergy_severity_max,
    fml_food_allergy_count = v_food_allergy_count,
    fml_has_severe_allergy = v_has_severe_allergy,
    fml_symptom_frequency = v_symptom_frequency,
    fml_symptom_severity_avg = v_symptom_severity_avg,
    fml_has_recent_symptoms = v_has_recent_symptoms,
    fml_dietary_diversity_score = v_dietary_diversity_score,
    fml_menu_kcal_avg = v_menu_kcal_avg,
    fml_protein_intake_score = v_protein_intake_score,
    fml_calculated_at = NOW();
  
  -- Retornar features calculados
  SELECT 
    fml_id,
    nin_id,
    ant_id,
    fml_bmi_velocity,
    fml_weight_velocity,
    fml_height_velocity,
    fml_baz_trend,
    fml_measurements_count,
    fml_adherence_score,
    fml_adherence_consistency,
    fml_menu_completion_rate,
    fml_allergy_count,
    fml_allergy_severity_max,
    fml_food_allergy_count,
    fml_has_severe_allergy,
    fml_symptom_frequency,
    fml_symptom_severity_avg,
    fml_has_recent_symptoms,
    fml_dietary_diversity_score,
    fml_menu_kcal_avg,
    fml_protein_intake_score,
    fml_calculated_at,
    fml_version
  FROM features_ml
  WHERE nin_id = p_nin_id 
    AND ant_id = p_ant_id
  ORDER BY fml_calculated_at DESC
  LIMIT 1;
  
END$$


-- ============================================================================
-- sp_obtener_datos_para_ml
-- Obtiene todos los datos necesarios para hacer predicción ML
-- ============================================================================

DROP PROCEDURE IF EXISTS sp_obtener_datos_para_ml$$

CREATE PROCEDURE sp_obtener_datos_para_ml(
  IN p_nin_id BIGINT UNSIGNED
)
BEGIN
  -- Obtener última antropometría y calcular features si no existen
  DECLARE v_ant_id BIGINT UNSIGNED;
  
  SELECT ant_id INTO v_ant_id
  FROM antropometrias
  WHERE nin_id = p_nin_id
  ORDER BY ant_fecha DESC, creado_en DESC
  LIMIT 1;
  
  IF v_ant_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay datos antropométricos para este niño';
  END IF;
  
  -- Calcular features si no existen o están desactualizados
  IF NOT EXISTS(
    SELECT 1 FROM features_ml 
    WHERE nin_id = p_nin_id 
      AND ant_id = v_ant_id
      AND fml_calculated_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)
  ) THEN
    CALL sp_calcular_features_ml(p_nin_id, v_ant_id);
  END IF;
  
  -- Retornar datos completos para ML
  SELECT 
    -- Datos del niño
    n.nin_id,
    n.nin_nombres,
    n.nin_fecha_nac,
    n.nin_sexo,
    TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE()) as age_months,
    
    -- Antropometría actual
    a.ant_id,
    a.ant_fecha,
    a.ant_peso_kg as weight_kg,
    a.ant_talla_cm as height_cm,
    a.ant_peso_kg / POWER(a.ant_talla_cm / 100, 2) as BMI,
    COALESCE(a.ant_z_imc, 0) as baz,
    
    -- Features ML
    f.fml_bmi_velocity as bmi_velocity,
    f.fml_weight_velocity as weight_velocity,
    f.fml_height_velocity as height_velocity,
    f.fml_baz_trend as baz_trend,
    f.fml_measurements_count as measurements_count,
    f.fml_adherence_score as adherence_score,
    f.fml_adherence_consistency as adherence_consistency,
    f.fml_menu_completion_rate as menu_completion_rate,
    f.fml_allergy_count as allergy_count,
    f.fml_allergy_severity_max as allergy_severity_max,
    f.fml_food_allergy_count as food_allergy_count,
    f.fml_has_severe_allergy as has_severe_allergy,
    f.fml_symptom_frequency as symptom_frequency,
    f.fml_symptom_severity_avg as symptom_severity_avg,
    f.fml_has_recent_symptoms as has_recent_symptoms,
    f.fml_dietary_diversity_score as dietary_diversity_score,
    f.fml_menu_kcal_avg as menu_kcal_avg,
    f.fml_protein_intake_score as protein_intake_score,
    
    -- Contexto
    COALESCE(e.ent_altitud_m, 0) as altitude_m,
    e.ent_zona as entity_zone,
    et.entti_codigo as entity_type
    
  FROM ninos n
  JOIN antropometrias a ON n.nin_id = a.nin_id AND a.ant_id = v_ant_id
  LEFT JOIN features_ml f ON n.nin_id = f.nin_id AND a.ant_id = f.ant_id
  LEFT JOIN entidades e ON n.ent_id = e.ent_id
  LEFT JOIN entidad_tipos et ON e.entti_id = et.entti_id
  WHERE n.nin_id = p_nin_id;
  
END$$

DELIMITER ;


-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

SELECT '✅ Procedimientos almacenados creados correctamente' AS mensaje;

-- Listar procedimientos creados
SELECT 
  ROUTINE_NAME as procedimiento,
  CREATED as fecha_creacion
FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA = 'nutricion'
  AND ROUTINE_TYPE = 'PROCEDURE'
  AND ROUTINE_NAME LIKE 'sp_%ml%'
ORDER BY ROUTINE_NAME;
