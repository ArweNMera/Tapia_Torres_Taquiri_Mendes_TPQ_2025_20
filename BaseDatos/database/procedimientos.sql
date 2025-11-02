DROP PROCEDURE IF EXISTS sp_actualizar_cache_nutrientes;

create
    procedure sp_actualizar_cache_nutrientes(IN p_rec_id int unsigned)
BEGIN
  -- Eliminar cache anterior
  DELETE FROM recetas_nutrientes_cache WHERE rec_id = p_rec_id;

  -- Calcular y guardar valores nutricionales
  INSERT INTO recetas_nutrientes_cache (rec_id, nutri_id, rnc_cantidad_total)
  SELECT
    ri.rec_id,
    an.nutri_id,
    SUM((ri.ri_cantidad / 100) * an.an_cantidad_100) AS cantidad_total
  FROM recetas_ingredientes ri
  INNER JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id
  WHERE ri.rec_id = p_rec_id
  GROUP BY ri.rec_id, an.nutri_id;

  SELECT CONCAT('Cache actualizado para receta ', p_rec_id) AS mensaje;
END;

DROP PROCEDURE IF EXISTS sp_admin_resetear_contrasena;

create
    procedure sp_admin_resetear_contrasena(IN p_usr_id bigint unsigned, IN p_password_hash varchar(255))
BEGIN
  IF NOT EXISTS (SELECT 1 FROM usuarios WHERE usr_id = p_usr_id AND eliminado_en IS NULL) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuario no encontrado';
  END IF;

  UPDATE usuarios
     SET usr_contrasena = p_password_hash,
         actualizado_en = CURRENT_TIMESTAMP
   WHERE usr_id = p_usr_id;

  SELECT ROW_COUNT() AS affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_admin_toggle_usuario;

create
    procedure sp_admin_toggle_usuario(IN p_usr_id bigint unsigned, IN p_actor_id bigint unsigned)
BEGIN
  DECLARE v_usr_activo TINYINT(1);
  DECLARE v_usr_usuario VARCHAR(255);

  IF p_usr_id = p_actor_id THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No puedes desactivar tu propia cuenta';
  END IF;

  SELECT usr_activo, usr_usuario
    INTO v_usr_activo, v_usr_usuario
    FROM usuarios
   WHERE usr_id = p_usr_id
     AND eliminado_en IS NULL
   LIMIT 1;

  IF v_usr_usuario IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuario no encontrado';
  END IF;

  UPDATE usuarios
     SET usr_activo = NOT v_usr_activo,
         actualizado_en = CURRENT_TIMESTAMP
   WHERE usr_id = p_usr_id;

  SELECT ROW_COUNT() AS affected_rows,
         v_usr_usuario AS usr_usuario,
         NOT v_usr_activo AS usr_activo;
END;

DROP PROCEDURE IF EXISTS sp_admin_usuarios_listar;

create
    procedure sp_admin_usuarios_listar()
BEGIN
  SELECT
    u.usr_id,
    u.usr_usuario,
    u.usr_nombre,
    u.usr_apellido,
    u.usr_correo,
    u.usr_dni,
    r.rol_nombre,
    u.usr_activo,
    u.creado_en
  FROM usuarios u
  JOIN roles r ON r.rol_id = u.rol_id
  WHERE u.eliminado_en IS NULL
  ORDER BY u.creado_en DESC;
END;

DROP PROCEDURE IF EXISTS sp_alimentos_actualizar;

create
    procedure sp_alimentos_actualizar(IN p_ali_id int unsigned, IN p_ali_nombre varchar(150),
                                                         IN p_ali_nombre_cientifico varchar(150),
                                                         IN p_ali_grupo varchar(60), IN p_ali_unidad varchar(16),
                                                         IN p_ali_activo tinyint(1))
BEGIN
  UPDATE alimentos
  SET ali_nombre = p_ali_nombre,
      ali_nombre_cientifico = p_ali_nombre_cientifico,
      ali_grupo = p_ali_grupo,
      ali_unidad = p_ali_unidad,
      ali_activo = p_ali_activo,
      actualizado_en = NOW()
  WHERE ali_id = p_ali_id;

  SELECT ali_id, ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad,
         ali_activo, creado_en, actualizado_en
  FROM alimentos
  WHERE ali_id = p_ali_id;
END;

DROP PROCEDURE IF EXISTS sp_alimentos_con_nutrientes_obtener;

create
    procedure sp_alimentos_con_nutrientes_obtener(IN p_ali_id int unsigned)
BEGIN
  -- Información del alimento
  SELECT a.ali_id, a.ali_nombre, a.ali_nombre_cientifico, a.ali_grupo,
         a.ali_unidad, a.ali_activo, a.creado_en, a.actualizado_en
  FROM alimentos a
  WHERE a.ali_id = p_ali_id;

  -- Nutrientes del alimento
  SELECT an.ali_id, an.nutri_id, an.an_cantidad_100, an.an_fuente,
         n.nutri_codigo, n.nutri_nombre, n.nutri_unidad
  FROM alimentos_nutrientes an
  JOIN nutrientes n ON an.nutri_id = n.nutri_id
  WHERE an.ali_id = p_ali_id
  ORDER BY n.nutri_nombre;
END;

DROP PROCEDURE IF EXISTS sp_alimentos_crear;

create
    procedure sp_alimentos_crear(IN p_ali_nombre varchar(150),
                                                    IN p_ali_nombre_cientifico varchar(150), IN p_ali_grupo varchar(60),
                                                    IN p_ali_unidad varchar(16))
BEGIN
  INSERT INTO alimentos (ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad, ali_activo)
  VALUES (p_ali_nombre, p_ali_nombre_cientifico, p_ali_grupo, p_ali_unidad, 1);

  SELECT ali_id, ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad,
         ali_activo, creado_en, actualizado_en
  FROM alimentos
  WHERE ali_id = LAST_INSERT_ID();
END;

DROP PROCEDURE IF EXISTS sp_alimentos_eliminar;

create
    procedure sp_alimentos_eliminar(IN p_ali_id int unsigned)
BEGIN
  -- Soft delete: marcar como inactivo
  UPDATE alimentos SET ali_activo = 0 WHERE ali_id = p_ali_id;
  SELECT ROW_COUNT() as affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_alimentos_listar;

create
    procedure sp_alimentos_listar(IN p_query varchar(100), IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 50;

  IF p_limit IS NOT NULL AND p_limit > 0 AND p_limit <= 200 THEN
    SET v_limit = p_limit;
  END IF;

  IF p_query IS NULL OR TRIM(p_query) = '' THEN
    SELECT ali_id, ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad,
           ali_activo, creado_en, actualizado_en
    FROM alimentos
    WHERE ali_activo = 1
    ORDER BY ali_nombre
    LIMIT v_limit;
  ELSE
    SELECT ali_id, ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad,
           ali_activo, creado_en, actualizado_en
    FROM alimentos
    WHERE ali_activo = 1
      AND (ali_nombre LIKE CONCAT('%', p_query, '%')
       OR ali_nombre_cientifico LIKE CONCAT('%', p_query, '%')
       OR ali_grupo LIKE CONCAT('%', p_query, '%'))
    ORDER BY ali_nombre
    LIMIT v_limit;
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_alimentos_nutrientes_actualizar;

create
    procedure sp_alimentos_nutrientes_actualizar(IN p_ali_id int unsigned,
                                                                    IN p_nutri_id smallint unsigned,
                                                                    IN p_an_cantidad_100 decimal(12, 4),
                                                                    IN p_an_fuente varchar(255))
BEGIN
  UPDATE alimentos_nutrientes
  SET an_cantidad_100 = p_an_cantidad_100,
      an_fuente = p_an_fuente
  WHERE ali_id = p_ali_id AND nutri_id = p_nutri_id;

  SELECT an.ali_id, an.nutri_id, an.an_cantidad_100, an.an_fuente,
         n.nutri_codigo, n.nutri_nombre, n.nutri_unidad
  FROM alimentos_nutrientes an
  JOIN nutrientes n ON an.nutri_id = n.nutri_id
  WHERE an.ali_id = p_ali_id AND an.nutri_id = p_nutri_id;
END;

DROP PROCEDURE IF EXISTS sp_alimentos_nutrientes_crear;

create
    procedure sp_alimentos_nutrientes_crear(IN p_ali_id int unsigned,
                                                               IN p_nutri_id smallint unsigned,
                                                               IN p_an_cantidad_100 decimal(12, 4),
                                                               IN p_an_fuente varchar(255))
BEGIN
  INSERT INTO alimentos_nutrientes (ali_id, nutri_id, an_cantidad_100, an_fuente)
  VALUES (p_ali_id, p_nutri_id, p_an_cantidad_100, p_an_fuente);

  SELECT an.ali_id, an.nutri_id, an.an_cantidad_100, an.an_fuente,
         n.nutri_codigo, n.nutri_nombre, n.nutri_unidad
  FROM alimentos_nutrientes an
  JOIN nutrientes n ON an.nutri_id = n.nutri_id
  WHERE an.ali_id = p_ali_id AND an.nutri_id = p_nutri_id;
END;

DROP PROCEDURE IF EXISTS sp_alimentos_nutrientes_eliminar;

create
    procedure sp_alimentos_nutrientes_eliminar(IN p_ali_id int unsigned, IN p_nutri_id smallint unsigned)
BEGIN
  DELETE FROM alimentos_nutrientes
  WHERE ali_id = p_ali_id AND nutri_id = p_nutri_id;
  SELECT ROW_COUNT() as affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_alimentos_obtener;

create
    procedure sp_alimentos_obtener(IN p_ali_id int unsigned)
BEGIN
  SELECT ali_id, ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad,
         ali_activo, creado_en, actualizado_en
  FROM alimentos
  WHERE ali_id = p_ali_id;
END;

DROP PROCEDURE IF EXISTS sp_antropometria_agregar;

create
    procedure sp_antropometria_agregar(IN p_nin_id bigint unsigned, IN p_fecha date,
                                                          IN p_peso_kg decimal(5, 2), IN p_talla_cm decimal(5, 2))
BEGIN
  DECLARE v_edad_meses INT;
  DECLARE v_ant_id BIGINT UNSIGNED;
  DECLARE v_talla_cm DECIMAL(5,2);

  -- Validar que el niño existe
  IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado';
  END IF;

  -- Calcular edad en meses a la fecha de medición
  SELECT TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, p_fecha) INTO v_edad_meses
  FROM ninos n
  WHERE n.nin_id = p_nin_id;

  -- Normalizar talla: si viene en metros (<=3), convertir a centímetros
  SET v_talla_cm = CASE WHEN p_talla_cm <= 3 THEN ROUND(p_talla_cm * 100, 2) ELSE p_talla_cm END;

  -- Insertar o actualizar antropometría (evitar duplicado por fecha)
  INSERT INTO antropometrias(
    nin_id, ant_fecha, ant_edad_meses, ant_peso_kg, ant_talla_cm
  ) VALUES (
    p_nin_id, p_fecha, v_edad_meses, p_peso_kg, v_talla_cm
  )
  ON DUPLICATE KEY UPDATE
    ant_edad_meses = VALUES(ant_edad_meses),
    ant_peso_kg    = VALUES(ant_peso_kg),
    ant_talla_cm   = VALUES(ant_talla_cm),
    actualizado_en = NOW();

  -- Obtener ID de la antropometría insertada/actualizada
  SET v_ant_id = (SELECT ant_id FROM antropometrias WHERE nin_id = p_nin_id AND ant_fecha = p_fecha);

  -- Retornar la antropometría creada
  SELECT
    ant_id,
    nin_id,
    ant_fecha,
    ant_edad_meses,
    ant_peso_kg,
    ant_talla_cm,
    ant_z_imc,
    ant_z_peso_edad,
    ant_z_talla_edad,
    ROUND(ant_peso_kg / POWER(ant_talla_cm / 100, 2), 2) as imc,
    creado_en
  FROM antropometrias
  WHERE ant_id = v_ant_id;
END;

DROP PROCEDURE IF EXISTS sp_antropometria_obtener_por_nino;

create
    procedure sp_antropometria_obtener_por_nino(IN p_nin_id bigint unsigned, IN p_limit int)
BEGIN
  DECLARE v_sql TEXT;

  SET v_sql = CONCAT(
    'SELECT ant_id, nin_id, ant_fecha, ant_edad_meses, ant_peso_kg, ant_talla_cm, ',
    'ant_z_imc, ant_z_peso_edad, ant_z_talla_edad, ',
    'ROUND(ant_peso_kg / POWER((ant_talla_cm / 100), 2), 2) as imc_calculado, ',
    'creado_en FROM antropometrias WHERE nin_id = ', p_nin_id,
    ' ORDER BY ant_fecha DESC, creado_en DESC'
  );

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_sql = CONCAT(v_sql, ' LIMIT ', p_limit);
  END IF;

  SET @sql = v_sql;
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;
END;

DROP PROCEDURE IF EXISTS sp_calcular_features_ml;

create
    procedure sp_calcular_features_ml(IN p_nin_id bigint unsigned, IN p_ant_id bigint unsigned)
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

END;

DROP PROCEDURE IF EXISTS sp_calcular_perfil_nutricional;

create
    procedure sp_calcular_perfil_nutricional(IN p_nin_id bigint unsigned)
BEGIN
    DECLARE v_edad_meses INT;
    DECLARE v_peso_kg DECIMAL(5,2);
    DECLARE v_talla_cm DECIMAL(5,2);
    DECLARE v_sexo ENUM('M','F');
    DECLARE v_clasificacion VARCHAR(50);
    DECLARE v_calorias INT;
    DECLARE v_proteinas DECIMAL(6,2);
    DECLARE v_carbohidratos DECIMAL(6,2);
    DECLARE v_grasas DECIMAL(6,2);
    DECLARE v_pnn_id BIGINT UNSIGNED;

    -- Obtener datos del niño y última antropometría
    SELECT
        TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE()),
        a.ant_peso_kg,
        a.ant_talla_cm,
        n.nin_sexo,
        COALESCE(en.en_clasificacion, 'NORMAL')
    INTO v_edad_meses, v_peso_kg, v_talla_cm, v_sexo, v_clasificacion
    FROM ninos n
    LEFT JOIN antropometrias a ON a.nin_id = n.nin_id
    LEFT JOIN evaluaciones_nutricionales en ON en.ant_id = a.ant_id
    WHERE n.nin_id = p_nin_id
    ORDER BY a.ant_fecha DESC
    LIMIT 1;

    -- Validar que tiene datos
    IF v_peso_kg IS NULL OR v_talla_cm IS NULL THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño no tiene datos antropométricos';
    END IF;

    -- Calcular requerimientos según edad
    IF v_edad_meses BETWEEN 0 AND 11 THEN
        SET v_calorias = 850;
        SET v_proteinas = 11;
    ELSEIF v_edad_meses BETWEEN 12 AND 35 THEN
        SET v_calorias = 1200;
        SET v_proteinas = 13;
    ELSEIF v_edad_meses BETWEEN 36 AND 71 THEN
        SET v_calorias = 1400;
        SET v_proteinas = 19;
    ELSEIF v_edad_meses BETWEEN 72 AND 119 THEN
        SET v_calorias = 1600;
        SET v_proteinas = 24;
    ELSE
        SET v_calorias = 2000;
        SET v_proteinas = 34;
    END IF;

    -- Ajustar por clasificación nutricional
    IF v_clasificacion IN ('DESNUTRICION_SEVERA', 'DESNUTRICION') THEN
        SET v_calorias = v_calorias * 1.2;
        SET v_proteinas = v_proteinas * 1.3;
    ELSEIF v_clasificacion = 'SOBREPESO' THEN
        SET v_calorias = v_calorias * 0.9;
    ELSEIF v_clasificacion = 'OBESIDAD' THEN
        SET v_calorias = v_calorias * 0.8;
    END IF;

    -- Calcular macronutrientes
    SET v_carbohidratos = (v_calorias * 0.55) / 4;
    SET v_grasas = (v_calorias * 0.30) / 9;

    -- Primero: Insertar nuevo perfil con vigente = FALSE temporalmente
    INSERT INTO perfil_nutricional_nino (
        nin_id, pnn_calorias_diarias, pnn_proteinas_g, pnn_carbohidratos_g, pnn_grasas_g,
        pnn_hierro_mg, pnn_calcio_mg, pnn_vitamina_a_ug, pnn_vitamina_c_mg, pnn_zinc_mg, pnn_fibra_g,
        pnn_edad_meses, pnn_peso_kg, pnn_talla_cm, pnn_clasificacion, pnn_vigente
    ) VALUES (
        p_nin_id, v_calorias, v_proteinas, v_carbohidratos, v_grasas,
        10, 800, 400, 25, 5, v_edad_meses / 3,
        v_edad_meses, v_peso_kg, v_talla_cm, v_clasificacion, FALSE
    );

    SET v_pnn_id = LAST_INSERT_ID();

    -- Segundo: Desactivar todos los perfiles anteriores
    UPDATE perfil_nutricional_nino
    SET pnn_vigente = FALSE
    WHERE nin_id = p_nin_id;

    -- Tercero: Activar solo el nuevo perfil
    UPDATE perfil_nutricional_nino
    SET pnn_vigente = TRUE
    WHERE pnn_id = v_pnn_id;

    -- Retornar el perfil creado
    SELECT
        v_pnn_id AS pnn_id,
        p_nin_id AS nin_id,
        v_calorias AS pnn_calorias_diarias,
        v_clasificacion AS pnn_clasificacion,
        TRUE AS pnn_vigente,
        NOW() AS creado_en;

END;

DROP PROCEDURE IF EXISTS sp_comidas_favoritas_agregar;

create
    procedure sp_comidas_favoritas_agregar(IN p_nin_id bigint unsigned, IN p_rec_id int unsigned)
BEGIN
  IF NOT EXISTS (SELECT 1 FROM recetas WHERE rec_id = p_rec_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Receta no encontrada';
  END IF;

  INSERT INTO ninos_comidas_favoritas (nin_id, rec_id)
  VALUES (p_nin_id, p_rec_id)
  ON DUPLICATE KEY UPDATE actualizado_en = CURRENT_TIMESTAMP;

  SELECT ROW_COUNT() AS affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_comidas_favoritas_eliminar;

create
    procedure sp_comidas_favoritas_eliminar(IN p_ncf_id bigint unsigned)
BEGIN
  DELETE FROM ninos_comidas_favoritas WHERE ncf_id = p_ncf_id;
  SELECT ROW_COUNT() AS affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_comidas_favoritas_listar;

create
    procedure sp_comidas_favoritas_listar(IN p_nin_id bigint unsigned)
BEGIN
  SELECT
    ncf.ncf_id,
    ncf.nin_id,
    ncf.rec_id,
    r.rec_nombre,
    GROUP_CONCAT(DISTINCT rc.rc_comida) AS rec_tipo_comida,
    ncf.creado_en,
    ncf.actualizado_en
  FROM ninos_comidas_favoritas ncf
  JOIN recetas r ON r.rec_id = ncf.rec_id
  LEFT JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
  WHERE ncf.nin_id = p_nin_id
  GROUP BY ncf.ncf_id, ncf.nin_id, ncf.rec_id, r.rec_nombre, ncf.creado_en, ncf.actualizado_en
  ORDER BY ncf.creado_en DESC;
END;

DROP PROCEDURE IF EXISTS sp_disponibilidad_actualizar;

create
    procedure sp_disponibilidad_actualizar(IN p_dis_id bigint unsigned,
                                                              IN p_dis_disponible tinyint(1),
                                                              IN p_dis_precio_promedio decimal(10, 2))
BEGIN
  UPDATE disponibilidad_alimentos
  SET dis_disponible = p_dis_disponible,
      dis_precio_promedio = p_dis_precio_promedio,
      actualizado_en = NOW()
  WHERE dis_id = p_dis_id;

  SELECT da.dis_id, da.ali_id, da.ent_id, da.dis_periodo,
         da.dis_disponible, da.dis_precio_promedio, da.dis_region,
         da.creado_en, da.actualizado_en,
         a.ali_nombre, a.ali_grupo
  FROM disponibilidad_alimentos da
  JOIN alimentos a ON da.ali_id = a.ali_id
  WHERE da.dis_id = p_dis_id;
END;

DROP PROCEDURE IF EXISTS sp_disponibilidad_crear;

create
    procedure sp_disponibilidad_crear(IN p_ali_id int unsigned, IN p_ent_id int unsigned,
                                                         IN p_dis_periodo enum ('Q1', 'Q2', 'Q3', 'Q4'),
                                                         IN p_dis_disponible tinyint(1),
                                                         IN p_dis_precio_promedio decimal(10, 2),
                                                         IN p_dis_region varchar(120))
BEGIN
  INSERT INTO disponibilidad_alimentos (
    ali_id, ent_id, dis_periodo, dis_disponible, dis_precio_promedio, dis_region
  )
  VALUES (
    p_ali_id, p_ent_id, p_dis_periodo, p_dis_disponible, p_dis_precio_promedio, p_dis_region
  );

  SELECT da.dis_id, da.ali_id, da.ent_id, da.dis_periodo,
         da.dis_disponible, da.dis_precio_promedio, da.dis_region,
         da.creado_en, da.actualizado_en,
         a.ali_nombre, a.ali_grupo
  FROM disponibilidad_alimentos da
  JOIN alimentos a ON da.ali_id = a.ali_id
  WHERE da.dis_id = LAST_INSERT_ID();
END;

DROP PROCEDURE IF EXISTS sp_disponibilidad_eliminar;

create
    procedure sp_disponibilidad_eliminar(IN p_dis_id bigint unsigned)
BEGIN
  DELETE FROM disponibilidad_alimentos WHERE dis_id = p_dis_id;
  SELECT ROW_COUNT() as affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_disponibilidad_listar;

create
    procedure sp_disponibilidad_listar(IN p_region varchar(120),
                                                          IN p_periodo enum ('Q1', 'Q2', 'Q3', 'Q4'), IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 100;

  IF p_limit IS NOT NULL AND p_limit > 0 AND p_limit <= 500 THEN
    SET v_limit = p_limit;
  END IF;

  IF p_region IS NULL AND p_periodo IS NULL THEN
    -- Sin filtros
    SELECT da.dis_id, da.ali_id, da.ent_id, da.dis_periodo,
           da.dis_disponible, da.dis_precio_promedio, da.dis_region,
           da.creado_en, da.actualizado_en,
           a.ali_nombre, a.ali_grupo
    FROM disponibilidad_alimentos da
    JOIN alimentos a ON da.ali_id = a.ali_id
    ORDER BY da.dis_region, da.dis_periodo, a.ali_nombre
    LIMIT v_limit;
  ELSEIF p_region IS NOT NULL AND p_periodo IS NULL THEN
    -- Solo filtro por región
    SELECT da.dis_id, da.ali_id, da.ent_id, da.dis_periodo,
           da.dis_disponible, da.dis_precio_promedio, da.dis_region,
           da.creado_en, da.actualizado_en,
           a.ali_nombre, a.ali_grupo
    FROM disponibilidad_alimentos da
    JOIN alimentos a ON da.ali_id = a.ali_id
    WHERE da.dis_region = p_region
    ORDER BY da.dis_periodo, a.ali_nombre
    LIMIT v_limit;
  ELSEIF p_region IS NULL AND p_periodo IS NOT NULL THEN
    -- Solo filtro por periodo
    SELECT da.dis_id, da.ali_id, da.ent_id, da.dis_periodo,
           da.dis_disponible, da.dis_precio_promedio, da.dis_region,
           da.creado_en, da.actualizado_en,
           a.ali_nombre, a.ali_grupo
    FROM disponibilidad_alimentos da
    JOIN alimentos a ON da.ali_id = a.ali_id
    WHERE da.dis_periodo = p_periodo
    ORDER BY da.dis_region, a.ali_nombre
    LIMIT v_limit;
  ELSE
    -- Ambos filtros
    SELECT da.dis_id, da.ali_id, da.ent_id, da.dis_periodo,
           da.dis_disponible, da.dis_precio_promedio, da.dis_region,
           da.creado_en, da.actualizado_en,
           a.ali_nombre, a.ali_grupo
    FROM disponibilidad_alimentos da
    JOIN alimentos a ON da.ali_id = a.ali_id
    WHERE da.dis_region = p_region AND da.dis_periodo = p_periodo
    ORDER BY a.ali_nombre
    LIMIT v_limit;
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_disponibilidad_obtener;

create
    procedure sp_disponibilidad_obtener(IN p_dis_id bigint unsigned)
BEGIN
  SELECT da.dis_id, da.ali_id, da.ent_id, da.dis_periodo,
         da.dis_disponible, da.dis_precio_promedio, da.dis_region,
         da.creado_en, da.actualizado_en,
         a.ali_nombre, a.ali_grupo
  FROM disponibilidad_alimentos da
  JOIN alimentos a ON da.ali_id = a.ali_id
  WHERE da.dis_id = p_dis_id;
END;

DROP PROCEDURE IF EXISTS sp_entidad_tipos_listar;

create
    procedure sp_entidad_tipos_listar()
BEGIN
  SELECT
    entti_id,
    entti_codigo,
    entti_nombre,
    creado_en
  FROM entidad_tipos
  ORDER BY entti_nombre;
END;

DROP PROCEDURE IF EXISTS sp_entidades_buscar;

create
    procedure sp_entidades_buscar(IN p_query varchar(100), IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 20;

  -- Establecer límite (máximo 100)
  IF p_limit IS NOT NULL AND p_limit > 0 AND p_limit <= 100 THEN
    SET v_limit = p_limit;
  END IF;

  -- Si no hay query, retornar todos
  IF p_query IS NULL OR TRIM(p_query) = '' THEN
    SELECT
      e.ent_id,
      e.ent_codigo,
      e.ent_nombre,
      e.ent_descripcion,
      e.ent_direccion,
      e.ent_departamento,
      e.ent_provincia,
      e.ent_distrito,
      e.entti_id,
      t.entti_codigo,
      t.entti_nombre,
      e.creado_en
    FROM entidades e
    JOIN entidad_tipos t ON e.entti_id = t.entti_id
    ORDER BY e.ent_nombre
    LIMIT v_limit;
  ELSE
    -- Buscar por código, nombre o tipo
    SELECT
      e.ent_id,
      e.ent_codigo,
      e.ent_nombre,
      e.ent_descripcion,
      e.ent_direccion,
      e.ent_departamento,
      e.ent_provincia,
      e.ent_distrito,
      e.entti_id,
      t.entti_codigo,
      t.entti_nombre,
      e.creado_en
    FROM entidades e
    JOIN entidad_tipos t ON e.entti_id = t.entti_id
    WHERE
      e.ent_codigo LIKE CONCAT('%', p_query, '%')
      OR e.ent_nombre LIKE CONCAT('%', p_query, '%')
      OR t.entti_nombre LIKE CONCAT('%', p_query, '%')
    ORDER BY
      CASE
        WHEN e.ent_codigo = p_query THEN 1
        WHEN e.ent_nombre = p_query THEN 2
        WHEN e.ent_codigo LIKE CONCAT(p_query, '%') THEN 3
        WHEN e.ent_nombre LIKE CONCAT(p_query, '%') THEN 4
        ELSE 5
      END,
      e.ent_nombre
    LIMIT v_limit;
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_evaluaciones_recomendaciones;

create
    procedure sp_evaluaciones_recomendaciones(IN p_en_id bigint unsigned, IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 5;

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 10);
  END IF;

  SELECT
    rt.rt_codigo,
    rt.rt_titulo,
    rt.rt_descripcion
  FROM evaluaciones_recomendaciones er
  JOIN recomendaciones_tipos rt ON rt.rt_id = er.rt_id
  WHERE er.en_id = p_en_id
  ORDER BY rt.rt_prioridad ASC, rt.rt_id ASC
  LIMIT v_limit;
END;

DROP PROCEDURE IF EXISTS sp_evaluar_estado_nutricional;

create
    procedure sp_evaluar_estado_nutricional(IN p_nin_id bigint unsigned)
BEGIN
  DECLARE v_ant_id BIGINT UNSIGNED;
  DECLARE v_ant_fecha DATE;
  DECLARE v_peso_kg DECIMAL(6,2);
  DECLARE v_talla_cm DECIMAL(6,2);
  DECLARE v_edad_meses INT;
  DECLARE v_imc DECIMAL(6,2);
  DECLARE v_zscore DECIMAL(6,3);
  DECLARE v_zscore_prev DECIMAL(6,3);
  DECLARE v_percentil DECIMAL(6,2);
  DECLARE v_clasificacion VARCHAR(30);
  DECLARE v_nivel_riesgo VARCHAR(10);
  DECLARE v_riesgo_porcentaje DECIMAL(6,2);
  DECLARE v_lms_json JSON;
  DECLARE v_l DECIMAL(10,4);
  DECLARE v_m DECIMAL(10,4);
  DECLARE v_s DECIMAL(10,4);
  DECLARE v_lms_found BOOLEAN DEFAULT FALSE;
  DECLARE v_en_id BIGINT UNSIGNED;
  DECLARE v_fecha_nac DATE;
  DECLARE v_sexo ENUM('M','F');
  DECLARE v_has_fn INT DEFAULT 0;
  DECLARE v_has_fn_z INT DEFAULT 0;
  DECLARE v_has_fn_pct INT DEFAULT 0;
  DECLARE v_has_fn_cls INT DEFAULT 0;

  -- Obtener datos básicos del niño
  SELECT
    COALESCE(n.nin_fecha_nac, up.usrper_fecha_nac),
    COALESCE(n.nin_sexo, up.usrper_genero)
  INTO v_fecha_nac, v_sexo
  FROM ninos n
  LEFT JOIN usuarios u ON u.usr_id = COALESCE(n.usr_id_propietario, n.usr_id_tutor)
  LEFT JOIN usuarios_perfil up ON u.usr_id = up.usr_id
  WHERE n.nin_id = p_nin_id;

  IF v_fecha_nac IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado o sin datos de perfil';
  END IF;

  -- Última antropometría registrada
  SELECT
    a.ant_id,
    a.ant_fecha,
    a.ant_peso_kg,
    a.ant_talla_cm,
    a.ant_edad_meses,
    a.ant_z_imc
  INTO
    v_ant_id,
    v_ant_fecha,
    v_peso_kg,
    v_talla_cm,
    v_edad_meses,
    v_zscore_prev
  FROM antropometrias a
  WHERE a.nin_id = p_nin_id
  ORDER BY a.ant_fecha DESC, a.creado_en DESC
  LIMIT 1;

  IF v_ant_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay datos antropométricos para este niño';
  END IF;

  IF v_edad_meses IS NULL THEN
    SET v_edad_meses = TIMESTAMPDIFF(MONTH, v_fecha_nac, v_ant_fecha);
  END IF;

  -- Calcular IMC
  SET v_imc = v_peso_kg / POWER((v_talla_cm / 100), 2);

  -- Intentar obtener parámetros OMS
  SELECT COUNT(*) INTO v_has_fn
  FROM information_schema.routines
  WHERE routine_schema = DATABASE() AND routine_type = 'FUNCTION' AND routine_name = 'fn_obtener_lms_oms';

  IF v_has_fn > 0 THEN
    SET v_lms_json = fn_obtener_lms_oms(v_edad_meses, v_sexo);
    SET v_lms_found = JSON_EXTRACT(v_lms_json, '$.found');
  ELSE
    SET v_lms_found = FALSE;
  END IF;

  IF v_lms_found THEN
    SELECT COUNT(*) INTO v_has_fn_z
    FROM information_schema.routines
    WHERE routine_schema = DATABASE() AND routine_type = 'FUNCTION' AND routine_name = 'fn_calcular_zscore_lms';
    SELECT COUNT(*) INTO v_has_fn_pct
    FROM information_schema.routines
    WHERE routine_schema = DATABASE() AND routine_type = 'FUNCTION' AND routine_name = 'fn_calcular_percentil';
    SELECT COUNT(*) INTO v_has_fn_cls
    FROM information_schema.routines
    WHERE routine_schema = DATABASE() AND routine_type = 'FUNCTION' AND routine_name = 'fn_clasificar_estado_nutricional';

    IF v_has_fn_z > 0 THEN
      SET v_l = JSON_EXTRACT(v_lms_json, '$.L');
      SET v_m = JSON_EXTRACT(v_lms_json, '$.M');
      SET v_s = JSON_EXTRACT(v_lms_json, '$.S');
      SET v_zscore = fn_calcular_zscore_lms(v_imc, v_l, v_m, v_s);
    END IF;

    IF v_zscore IS NOT NULL AND v_has_fn_pct > 0 THEN
      SET v_percentil = fn_calcular_percentil(v_zscore);
    ELSEIF v_zscore IS NOT NULL THEN
      SET v_percentil = 50 + (v_zscore * 15);
      SET v_percentil = GREATEST(0.1, LEAST(99.9, v_percentil));
    END IF;
  ELSE
    SET v_zscore = v_zscore_prev;
  END IF;

  -- Clasificación y percentil cuando no hubo datos OMS
  IF v_zscore IS NULL THEN
    SET v_percentil = NULL;

    IF v_edad_meses < 24 THEN
      IF v_imc < 14 THEN SET v_clasificacion = 'DESNUTRICION_SEVERA';
      ELSEIF v_imc < 15 THEN SET v_clasificacion = 'DESNUTRICION';
      ELSEIF v_imc < 16 THEN SET v_clasificacion = 'RIESGO';
      ELSEIF v_imc <= 18 THEN SET v_clasificacion = 'NORMAL';
      ELSEIF v_imc <= 20 THEN SET v_clasificacion = 'SOBREPESO';
      ELSE SET v_clasificacion = 'OBESIDAD';
      END IF;
    ELSE
      IF v_imc < 13.5 THEN SET v_clasificacion = 'DESNUTRICION_SEVERA';
      ELSEIF v_imc < 14.5 THEN SET v_clasificacion = 'DESNUTRICION';
      ELSEIF v_imc < 15.5 THEN SET v_clasificacion = 'RIESGO';
      ELSEIF v_imc <= 17.5 THEN SET v_clasificacion = 'NORMAL';
      ELSEIF v_imc <= 19.5 THEN SET v_clasificacion = 'SOBREPESO';
      ELSE SET v_clasificacion = 'OBESIDAD';
      END IF;
    END IF;
  ELSE
    IF v_has_fn_cls > 0 THEN
      SET v_clasificacion = fn_clasificar_estado_nutricional(v_zscore);
    ELSE
      IF v_zscore < -3 THEN SET v_clasificacion = 'DESNUTRICION_SEVERA';
      ELSEIF v_zscore < -2 THEN SET v_clasificacion = 'DESNUTRICION';
      ELSEIF v_zscore < -1 THEN SET v_clasificacion = 'RIESGO';
      ELSEIF v_zscore <= 1 THEN SET v_clasificacion = 'NORMAL';
      ELSEIF v_zscore <= 2 THEN SET v_clasificacion = 'SOBREPESO';
      ELSE SET v_clasificacion = 'OBESIDAD';
      END IF;
    END IF;
  END IF;

  -- Nivel de riesgo y porcentaje
  CASE v_clasificacion
    WHEN 'DESNUTRICION_SEVERA' THEN
      SET v_nivel_riesgo = 'CRITICO';
      SET v_riesgo_porcentaje = 95;
    WHEN 'DESNUTRICION' THEN
      SET v_nivel_riesgo = 'ALTO';
      SET v_riesgo_porcentaje = 85;
    WHEN 'RIESGO' THEN
      SET v_nivel_riesgo = 'MODERADO';
      SET v_riesgo_porcentaje = 65;
    WHEN 'SOBREPESO' THEN
      SET v_nivel_riesgo = 'MODERADO';
      SET v_riesgo_porcentaje = 70;
    WHEN 'OBESIDAD' THEN
      SET v_nivel_riesgo = 'ALTO';
      SET v_riesgo_porcentaje = 90;
    ELSE
      SET v_nivel_riesgo = 'BAJO';
      SET v_riesgo_porcentaje = 20;
  END CASE;

  IF v_zscore IS NOT NULL THEN
    SET v_riesgo_porcentaje = ROUND(LEAST(1, ABS(v_zscore) / 3) * 100, 1);
  END IF;

  -- Guardar evaluación
  INSERT INTO evaluaciones_nutricionales(
    nin_id, ant_id, en_edad_meses, en_imc, en_z_score_imc,
    en_percentil_imc, en_clasificacion, en_nivel_riesgo
  ) VALUES (
    p_nin_id, v_ant_id, v_edad_meses, v_imc, v_zscore,
    v_percentil, v_clasificacion, v_nivel_riesgo
  )
  ON DUPLICATE KEY UPDATE
    en_edad_meses = VALUES(en_edad_meses),
    en_imc = VALUES(en_imc),
    en_z_score_imc = VALUES(en_z_score_imc),
    en_percentil_imc = VALUES(en_percentil_imc),
    en_clasificacion = VALUES(en_clasificacion),
    en_nivel_riesgo = VALUES(en_nivel_riesgo);

  SET v_en_id = LAST_INSERT_ID();
  IF v_en_id = 0 THEN
    SELECT en_id INTO v_en_id
    FROM evaluaciones_nutricionales
    WHERE ant_id = v_ant_id;
  END IF;

  IF v_en_id IS NULL THEN
    SELECT en_id INTO v_en_id
    FROM evaluaciones_nutricionales
    WHERE nin_id = p_nin_id
    ORDER BY creado_en DESC
    LIMIT 1;
  END IF;

  IF v_en_id IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'No se pudo registrar evaluación nutricional (en_id no disponible)';
  END IF;

  -- Actualizar antropometría con z-score calculado
  UPDATE antropometrias
  SET ant_z_imc = v_zscore,
      actualizado_en = NOW()
  WHERE ant_id = v_ant_id;

  -- Actualizar recomendaciones asociadas a la evaluación (máximo 5 según prioridad)
  DELETE FROM evaluaciones_recomendaciones
  WHERE en_id = v_en_id;

  IF v_en_id IS NOT NULL AND v_en_id > 0 THEN
    INSERT INTO evaluaciones_recomendaciones (en_id, rt_id)
    SELECT en.en_id, rt.rt_id
    FROM evaluaciones_nutricionales en
    JOIN recomendaciones_tipos rt ON rt.rt_clasificacion = v_clasificacion AND rt.rt_activo = TRUE
    WHERE en.en_id = v_en_id
    ORDER BY rt.rt_prioridad ASC, rt.rt_id ASC
    LIMIT 5;
  END IF;

  -- Resultado
  SELECT
    v_en_id AS en_id,
    p_nin_id AS nin_id,
    v_ant_id AS ant_id,
    v_ant_fecha AS ant_fecha,
    v_edad_meses AS en_edad_meses,
    v_peso_kg AS peso_kg,
    v_talla_cm AS talla_cm,
    v_imc AS imc_calculado,
    v_zscore AS en_z_score_imc,
    v_percentil AS percentil_calculado,
    v_clasificacion AS en_clasificacion,
    v_nivel_riesgo AS en_nivel_riesgo,
    v_riesgo_porcentaje AS riesgo_porcentaje,
    v_lms_found AS oms_usado,
    NOW() AS evaluado_en;
END;

DROP PROCEDURE IF EXISTS sp_favorita_toggle;

create
    procedure sp_favorita_toggle(IN p_nin_id bigint unsigned, IN p_rec_id int unsigned,
                                                    OUT p_accion varchar(20))
BEGIN
    DECLARE v_existing_id BIGINT UNSIGNED DEFAULT NULL;

    -- Verificar si ya existe
    SELECT ncf_id INTO v_existing_id
    FROM ninos_comidas_favoritas
    WHERE nin_id = p_nin_id AND rec_id = p_rec_id
    LIMIT 1;

    IF v_existing_id IS NOT NULL THEN
        -- Ya existe, eliminar
        DELETE FROM ninos_comidas_favoritas WHERE ncf_id = v_existing_id;
        SET p_accion = 'ELIMINADA';
    ELSE
        -- No existe, agregar
        INSERT INTO ninos_comidas_favoritas (nin_id, rec_id)
        VALUES (p_nin_id, p_rec_id);
        SET p_accion = 'AGREGADA';
    END IF;

    -- Retornar la acción realizada
    SELECT p_accion AS accion;
END;

DROP PROCEDURE IF EXISTS sp_feedback_listar_nino;

create
    procedure sp_feedback_listar_nino(IN p_nin_id bigint unsigned, IN p_fecha_desde date,
                                                         IN p_fecha_hasta date)
BEGIN
    SELECT
        mf.mf_id,
        mf.mei_id,
        mf.mf_completado,
        mf.mf_porcentaje_consumido,
        mf.mf_rating,
        mf.mf_notas,
        mf.mf_fecha_consumo,
        mf.creado_en,
        -- Datos de la receta
        r.rec_id,
        r.rec_nombre,
        mi.mei_comida AS tipo_comida,
        mi.mei_kcal AS kcal,
        -- Datos del menú
        m.men_id,
        m.men_inicio,
        m.men_fin
    FROM menus_feedback mf
    INNER JOIN menus_items mi ON mf.mei_id = mi.mei_id
    INNER JOIN recetas r ON mi.rec_id = r.rec_id
    INNER JOIN menus m ON mi.men_id = m.men_id
    WHERE mf.nin_id = p_nin_id
      AND mf.mf_fecha_consumo BETWEEN COALESCE(p_fecha_desde, '2000-01-01')
                                  AND COALESCE(p_fecha_hasta, CURDATE())
    ORDER BY mf.mf_fecha_consumo DESC, mf.creado_en DESC;
END;

DROP PROCEDURE IF EXISTS sp_feedback_obtener;

create
    procedure sp_feedback_obtener(IN p_mei_id bigint unsigned, IN p_mf_fecha_consumo date)
BEGIN
    SELECT
        mf.mf_id,
        mf.mei_id,
        mf.nin_id,
        mf.mf_completado,
        mf.mf_porcentaje_consumido,
        mf.mf_rating,
        mf.mf_notas,
        mf.mf_fecha_consumo,
        mf.mf_registrado_por,
        mf.creado_en,
        -- Datos de la receta
        r.rec_id,
        r.rec_nombre,
        mi.mei_comida AS tipo_comida,
        mi.mei_kcal AS kcal
    FROM menus_feedback mf
    INNER JOIN menus_items mi ON mf.mei_id = mi.mei_id
    INNER JOIN recetas r ON mi.rec_id = r.rec_id
    WHERE mf.mei_id = p_mei_id
      AND mf.mf_fecha_consumo = COALESCE(p_mf_fecha_consumo, CURDATE())
    LIMIT 1;
END;

DROP PROCEDURE IF EXISTS sp_feedback_registrar;

create
    procedure sp_feedback_registrar(IN p_mei_id bigint unsigned, IN p_nin_id bigint unsigned,
                                                       IN p_mf_rating tinyint, IN p_mf_porcentaje_consumido tinyint,
                                                       IN p_mf_completado tinyint(1), IN p_mf_notas text,
                                                       IN p_mf_fecha_consumo date,
                                                       IN p_mf_registrado_por bigint unsigned,
                                                       OUT p_mf_id bigint unsigned)
BEGIN
    DECLARE v_existing_id BIGINT UNSIGNED DEFAULT NULL;

    -- Si no se proporciona fecha, usar la fecha actual
    IF p_mf_fecha_consumo IS NULL THEN
        SET p_mf_fecha_consumo = CURDATE();
    END IF;

    -- Verificar si ya existe feedback para este item + fecha
    SELECT mf_id INTO v_existing_id
    FROM menus_feedback
    WHERE mei_id = p_mei_id
      AND mf_fecha_consumo = p_mf_fecha_consumo
    LIMIT 1;

    IF v_existing_id IS NOT NULL THEN
        -- Actualizar existente
        UPDATE menus_feedback SET
            mf_rating = COALESCE(p_mf_rating, mf_rating),
            mf_porcentaje_consumido = COALESCE(p_mf_porcentaje_consumido, mf_porcentaje_consumido),
            mf_completado = p_mf_completado,
            mf_notas = COALESCE(p_mf_notas, mf_notas),
            mf_registrado_por = COALESCE(p_mf_registrado_por, mf_registrado_por)
        WHERE mf_id = v_existing_id;

        SET p_mf_id = v_existing_id;
    ELSE
        -- Insertar nuevo
        INSERT INTO menus_feedback (
            mei_id, nin_id, mf_completado, mf_porcentaje_consumido,
            mf_rating, mf_notas, mf_fecha_consumo, mf_registrado_por
        ) VALUES (
            p_mei_id, p_nin_id, p_mf_completado, p_mf_porcentaje_consumido,
            p_mf_rating, p_mf_notas, p_mf_fecha_consumo, p_mf_registrado_por
        );

        SET p_mf_id = LAST_INSERT_ID();
    END IF;

    -- Retornar el ID
    SELECT p_mf_id AS mf_id;
END;

DROP PROCEDURE IF EXISTS sp_guardar_preferencias_nino;

create
    procedure sp_guardar_preferencias_nino(IN p_nin_id bigint unsigned,
                                                              IN p_tipo_comida enum ('DESAYUNO', 'ALMUERZO', 'CENA', 'SNACKS'),
                                                              IN p_preferencias json)
BEGIN
  DECLARE i INT DEFAULT 0;
  DECLARE total INT;
  DECLARE preferencia VARCHAR(100);

  -- Desactivar preferencias anteriores
  UPDATE ninos_preferencias_comidas
  SET npc_activo = FALSE
  WHERE nin_id = p_nin_id AND npc_tipo_comida = p_tipo_comida;

  -- Insertar nuevas preferencias
  SET total = JSON_LENGTH(p_preferencias);

  WHILE i < total DO
    SET preferencia = JSON_UNQUOTE(JSON_EXTRACT(p_preferencias, CONCAT('$[', i, ']')));

    INSERT INTO ninos_preferencias_comidas (nin_id, npc_tipo_comida, npc_preferencia, npc_activo)
    VALUES (p_nin_id, p_tipo_comida, preferencia, TRUE);

    SET i = i + 1;
  END WHILE;

  SELECT CONCAT('Preferencias guardadas: ', total, ' items') AS mensaje;
END;

DROP PROCEDURE IF EXISTS sp_login_get_hash;

create
    procedure sp_login_get_hash(IN p_usuario varchar(150))
BEGIN
  DECLARE v_count INT DEFAULT 0;

  SELECT COUNT(*) INTO v_count FROM usuarios WHERE usr_usuario = p_usuario LIMIT 1;
  IF v_count = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuario no encontrado';
  END IF;

  -- Devolvemos SOLO una fila (si hubiese duplicados, es problema de datos)
  SELECT
    u.usr_id,
    u.usr_usuario,
    u.usr_correo,
    u.usr_nombre,
    u.usr_apellido,
    u.rol_id,
    u.usr_activo,
    u.usr_contrasena AS password_hash
  FROM usuarios u
  WHERE u.usr_usuario = p_usuario
  LIMIT 1;
END;

DROP PROCEDURE IF EXISTS sp_menus_actualizar_kcal;

create
    procedure sp_menus_actualizar_kcal(IN p_men_id bigint unsigned, IN p_kcal_total int)
BEGIN
  UPDATE menus
     SET men_kcal_total = p_kcal_total
   WHERE men_id = p_men_id;

  SELECT ROW_COUNT() AS affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_menus_cambiar_estado;

create
    procedure sp_menus_cambiar_estado(IN p_men_id bigint unsigned,
                                                         IN p_estado enum ('BORRADOR', 'APROBADO', 'ARCHIVADO'))
BEGIN
  UPDATE menus
     SET men_estado = p_estado
   WHERE men_id = p_men_id;

  SELECT ROW_COUNT() AS affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_menus_crear;

create
    procedure sp_menus_crear(IN p_nin_id bigint unsigned,
                                                IN p_generado_por enum ('IA', 'NUTRICIONISTA'), IN p_inicio date,
                                                IN p_fin date)
BEGIN
  INSERT INTO menus (nin_id, men_generado_por, men_inicio, men_fin, men_estado)
  VALUES (p_nin_id, p_generado_por, p_inicio, p_fin, 'BORRADOR');

  SELECT LAST_INSERT_ID() AS men_id;
END;

DROP PROCEDURE IF EXISTS sp_menus_detalle;

create
    procedure sp_menus_detalle(IN p_men_id bigint unsigned)
BEGIN
  SELECT m.*, n.nin_nombres
    FROM menus m
    JOIN ninos n ON n.nin_id = m.nin_id
   WHERE m.men_id = p_men_id;
END;

DROP PROCEDURE IF EXISTS sp_menus_items_agregar;

create
    procedure sp_menus_items_agregar(IN p_men_id bigint unsigned, IN p_dia_idx tinyint unsigned,
                                                        IN p_comida enum ('DESAYUNO', 'ALMUERZO', 'CENA', 'REFACCION'),
                                                        IN p_rec_id int unsigned, IN p_kcal int)
BEGIN
  INSERT INTO menus_items (men_id, mei_dia_idx, mei_comida, rec_id, mei_kcal)
  VALUES (p_men_id, p_dia_idx, p_comida, p_rec_id, p_kcal);

  SELECT LAST_INSERT_ID() AS mei_id;
END;

DROP PROCEDURE IF EXISTS sp_menus_items_listar;

create
    procedure sp_menus_items_listar(IN p_men_id bigint unsigned)
BEGIN
  SELECT
    mi.*,
    r.rec_nombre,
    r.rec_instrucciones
  FROM menus_items mi
  JOIN recetas r ON r.rec_id = mi.rec_id
  WHERE mi.men_id = p_men_id
  ORDER BY mi.mei_dia_idx,
           FIELD(mi.mei_comida,'DESAYUNO','ALMUERZO','CENA','REFACCION');
END;

DROP PROCEDURE IF EXISTS sp_menus_items_listar_para_pdf;

create
    procedure sp_menus_items_listar_para_pdf(IN p_men_id bigint unsigned)
BEGIN

    SELECT
        mi.mei_id,
        mi.men_id,
        mi.rec_id,
        mi.mei_dia_idx,
        mi.mei_comida AS mei_tipo_comida,
        mi.mei_kcal,
        -- Datos de la receta
        r.rec_nombre,
        r.rec_instrucciones,
        r.rec_activo,
        -- Usar mei_kcal directamente (ya está calculado en la tabla)
        COALESCE(mi.mei_kcal, 0) AS kcal,
        -- Calcular macronutrientes estimados basados en proporciones estándar
        -- Proteínas: ~15% de calorías totales, 1g proteína = 4 kcal
        COALESCE(ROUND(mi.mei_kcal * 0.15 / 4, 1), 0) AS proteina_g,
        -- Carbohidratos: ~55% de calorías totales, 1g carbs = 4 kcal
        COALESCE(ROUND(mi.mei_kcal * 0.55 / 4, 1), 0) AS carbohidratos_g,
        -- Grasas: ~30% de calorías totales, 1g grasa = 9 kcal
        COALESCE(ROUND(mi.mei_kcal * 0.30 / 9, 1), 0) AS grasa_g
    FROM menus_items mi
    INNER JOIN recetas r ON r.rec_id = mi.rec_id
    WHERE mi.men_id = p_men_id
    ORDER BY
        mi.mei_dia_idx,
        FIELD(mi.mei_comida, 'DESAYUNO', 'ALMUERZO', 'CENA', 'REFACCION');
END;

DROP PROCEDURE IF EXISTS sp_menus_listar;

create
    procedure sp_menus_listar(IN p_nin_id bigint unsigned,
                                                 IN p_estado enum ('BORRADOR', 'APROBADO', 'ARCHIVADO'), IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 10;

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 100);
  END IF;

  SELECT *
    FROM menus
   WHERE nin_id = p_nin_id
     AND (p_estado IS NULL OR p_estado = '' OR men_estado = p_estado)
   ORDER BY men_inicio DESC
   LIMIT v_limit;
END;

DROP PROCEDURE IF EXISTS sp_ninos_actualizar;

create
    procedure sp_ninos_actualizar(IN p_nin_id bigint unsigned, IN p_nin_nombres varchar(150),
                                                     IN p_ent_id smallint unsigned, IN p_nin_fecha_nac date)
BEGIN
  -- Validar que el niño existe
  IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado';
  END IF;

  -- Actualizar datos (sin alergias)
  UPDATE ninos SET
    nin_nombres = COALESCE(p_nin_nombres, nin_nombres),
    ent_id = COALESCE(p_ent_id, ent_id),
    nin_fecha_nac = COALESCE(p_nin_fecha_nac, nin_fecha_nac),
    actualizado_en = NOW()
  WHERE nin_id = p_nin_id;

  -- Retornar el niño actualizado
  SELECT
    nin_id,
    usr_id_tutor,
    ent_id,
    nin_nombres,
    nin_fecha_nac,
    nin_sexo,
    TIMESTAMPDIFF(MONTH, nin_fecha_nac, CURDATE()) as edad_meses,
    creado_en,
    actualizado_en
  FROM ninos
  WHERE nin_id = p_nin_id;
END;

DROP PROCEDURE IF EXISTS sp_ninos_agregar_alergia;

create
    procedure sp_ninos_agregar_alergia(IN p_nin_id bigint unsigned, IN p_ta_codigo varchar(20),
                                                          IN p_severidad enum ('LEVE', 'MODERADA', 'SEVERA'))
BEGIN
  DECLARE v_ta_id SMALLINT UNSIGNED;

  -- Validar que el niño existe
  IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado';
  END IF;

  -- Obtener ID del tipo de alergia
  SELECT ta_id INTO v_ta_id FROM tipos_alergias WHERE ta_codigo = p_ta_codigo AND ta_activo = 1;

  IF v_ta_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tipo de alergia no encontrado';
  END IF;

  -- Insertar o actualizar alergia
  INSERT INTO ninos_alergias(nin_id, ta_id, na_severidad, na_activo)
  VALUES (p_nin_id, v_ta_id, COALESCE(p_severidad, 'LEVE'), 1)
  ON DUPLICATE KEY UPDATE
    na_severidad = COALESCE(p_severidad, na_severidad),
    na_activo = 1;

  -- Retornar alergias del niño
  SELECT
    na.na_id,
    na.nin_id,
    ta.ta_codigo,
    ta.ta_nombre,
    ta.ta_categoria,
    na.na_severidad,
    na.creado_en
  FROM ninos_alergias na
  JOIN tipos_alergias ta ON na.ta_id = ta.ta_id
  WHERE na.nin_id = p_nin_id AND na.na_activo = 1
  ORDER BY na.creado_en DESC;
END;

DROP PROCEDURE IF EXISTS sp_ninos_alergia_eliminar;

create
    procedure sp_ninos_alergia_eliminar(IN p_na_id bigint unsigned, IN p_nin_id bigint unsigned)
BEGIN
  IF p_nin_id IS NULL OR p_nin_id = 0 THEN
    DELETE FROM ninos_alergias WHERE na_id = p_na_id;
  ELSE
    DELETE FROM ninos_alergias WHERE na_id = p_na_id AND nin_id = p_nin_id;
  END IF;

  SELECT ROW_COUNT() AS affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_ninos_cambiar_responsable;

create
    procedure sp_ninos_cambiar_responsable(IN p_nin_id bigint unsigned, IN p_autogestion tinyint(1),
                                                              IN p_usr_id_responsable bigint unsigned)
BEGIN
  IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id=p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='nin_id no existe';
  END IF;
  IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id_responsable) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_responsable no existe';
  END IF;

  IF p_autogestion = 1 THEN
    UPDATE ninos
       SET usr_id_propietario = p_usr_id_responsable,
           usr_id_tutor       = NULL
     WHERE nin_id = p_nin_id;
  ELSE
    UPDATE ninos
       SET usr_id_tutor       = p_usr_id_responsable,
           usr_id_propietario = NULL
     WHERE nin_id = p_nin_id;
  END IF;

  CALL sp_ninos_get(p_nin_id); -- devuelve el estado actualizado
END;

DROP PROCEDURE IF EXISTS sp_ninos_crear;

create
    procedure sp_ninos_crear(IN p_nin_nombres varchar(150), IN p_nin_fecha_nac date,
                                                IN p_nin_sexo char, IN p_ent_id int unsigned,
                                                IN p_usr_id_tutor bigint unsigned,
                                                IN p_usr_id_propietario bigint unsigned)
BEGIN
  DECLARE v_edad INT;
  DECLARE v_autogestion TINYINT(1);

  IF p_nin_nombres IS NULL OR p_nin_fecha_nac IS NULL OR p_nin_sexo IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='nombres/fecha_nac/sexo requeridos';
  END IF;

  SET v_edad = fn_edad_anios(p_nin_fecha_nac);
  IF v_edad < 0 OR v_edad > 19 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='La edad debe estar entre 0 y 19 años';
  END IF;

  IF v_edad >= 13 THEN
    SET v_autogestion = 1;
    IF p_usr_id_propietario IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_propietario requerido para >=13';
    END IF;
    IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id_propietario) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_propietario no existe';
    END IF;
  ELSE
    SET v_autogestion = 0;
    IF p_usr_id_tutor IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_tutor requerido para <13';
    END IF;
    IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id_tutor) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_tutor no existe';
    END IF;
  END IF;

  INSERT INTO ninos(
    usr_id_tutor, usr_id_propietario, ent_id,
    nin_nombres, nin_fecha_nac, nin_sexo
  ) VALUES (
    CASE WHEN v_autogestion=0 THEN p_usr_id_tutor ELSE NULL END,
    CASE WHEN v_autogestion=1 THEN p_usr_id_propietario ELSE NULL END,
    p_ent_id, p_nin_nombres, p_nin_fecha_nac, p_nin_sexo
  );

  SELECT LAST_INSERT_ID() AS nin_id,
         v_edad AS edad_anios,
         v_autogestion AS nin_autogestion,
         'OK' AS msg;
END;

DROP PROCEDURE IF EXISTS sp_ninos_datos_basicos;

create
    procedure sp_ninos_datos_basicos(IN p_nin_id bigint unsigned)
BEGIN
  SELECT
    n.nin_id,
    n.nin_nombres,
    n.nin_fecha_nac,
    n.nin_sexo,
    n.ent_id,
    TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE()) AS edad_meses,
    e.ent_nombre,
    e.ent_distrito
  FROM ninos n
  LEFT JOIN entidades e ON e.ent_id = n.ent_id
  WHERE n.nin_id = p_nin_id;
END;

DROP PROCEDURE IF EXISTS sp_ninos_eliminar;

create
    procedure sp_ninos_eliminar(IN p_nin_id bigint unsigned)
BEGIN
              DECLARE v_filas_afectadas INT DEFAULT 0;

              -- Verificar si el niño existe
              IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El niño no existe';
              END IF;

              -- Eliminar el niño (hard delete)
              DELETE FROM ninos WHERE nin_id = p_nin_id;

              SET v_filas_afectadas = ROW_COUNT();

              SELECT v_filas_afectadas AS filas_afectadas, 'OK' AS msg;
            END;

DROP PROCEDURE IF EXISTS sp_ninos_eliminar_alergia;

create
    procedure sp_ninos_eliminar_alergia(IN p_na_id bigint unsigned, IN p_nin_id bigint unsigned)
BEGIN
  -- Validar que la alergia existe y pertenece al niño especificado
  IF NOT EXISTS(SELECT 1 FROM ninos_alergias WHERE na_id = p_na_id AND nin_id = p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Alergia no encontrada para este niño';
  END IF;

  -- Soft delete: marcar como inactiva en lugar de eliminar
  UPDATE ninos_alergias
  SET na_activo = 0
  WHERE na_id = p_na_id AND nin_id = p_nin_id;

  -- Retornar las alergias activas restantes del niño
  SELECT
    na.na_id,
    na.nin_id,
    ta.ta_codigo,
    ta.ta_nombre,
    ta.ta_categoria,
    na.na_severidad,
    na.creado_en
  FROM ninos_alergias na
  JOIN tipos_alergias ta ON na.ta_id = ta.ta_id
  WHERE na.nin_id = p_nin_id AND na.na_activo = 1
  ORDER BY na.creado_en DESC;
END;

DROP PROCEDURE IF EXISTS sp_ninos_get;

create
    procedure sp_ninos_get(IN p_nin_id bigint unsigned)
BEGIN
              SELECT
                n.nin_id, n.ent_id,
                n.nin_nombres, n.nin_fecha_nac, n.nin_sexo,
                n.usr_id_tutor, n.usr_id_propietario,
                (n.usr_id_propietario IS NOT NULL) AS nin_autogestion,
                COALESCE(n.usr_id_propietario, n.usr_id_tutor) AS usr_id_responsable,
                u.usr_nombre, u.usr_apellido, u.usr_dni, u.usr_correo,
                up.usrper_telefono    AS telefono_resp,
                up.usrper_direccion   AS direccion_resp,
                up.usrper_genero      AS genero_resp,
                up.usrper_idioma      AS idioma_resp,
                fn_edad_meses(n.nin_fecha_nac) AS edad_meses,
                n.creado_en,
                n.actualizado_en,
                e.ent_nombre,
                e.ent_codigo,
                e.ent_direccion,
                e.ent_departamento,
                e.ent_provincia,
                e.ent_distrito
              FROM ninos n
              JOIN usuarios u ON u.usr_id = COALESCE(n.usr_id_propietario, n.usr_id_tutor)
              LEFT JOIN usuarios_perfil up ON up.usr_id = u.usr_id
              LEFT JOIN entidades e ON e.ent_id = n.ent_id
              WHERE n.nin_id = p_nin_id;
            END;

DROP PROCEDURE IF EXISTS sp_ninos_obtener_alergias;

create
    procedure sp_ninos_obtener_alergias(IN p_nin_id bigint unsigned)
BEGIN
  SELECT
    na.na_id,
    na.nin_id,
    ta.ta_codigo,
    ta.ta_nombre,
    ta.ta_categoria,
    na.na_severidad,
    na.creado_en
  FROM ninos_alergias na
  JOIN tipos_alergias ta ON na.ta_id = ta.ta_id
  WHERE na.nin_id = p_nin_id AND na.na_activo = 1
  ORDER BY ta.ta_categoria, ta.ta_nombre;
END;


DROP PROCEDURE IF EXISTS sp_ninos_obtener_por_id;

create
    procedure sp_ninos_obtener_por_id(IN p_nin_id bigint unsigned)
BEGIN
  SELECT
    n.nin_id,
    n.usr_id_tutor,
    n.ent_id,
    CONCAT(u.usr_nombre, ' ', u.usr_apellido) as nin_nombres, -- Desde usuarios
    up.usrper_fecha_nac as nin_fecha_nac,
    up.usrper_genero as nin_sexo,
    TIMESTAMPDIFF(MONTH, up.usrper_fecha_nac, CURDATE()) as edad_meses,
    n.creado_en,
    n.actualizado_en,
    u.usr_dni as tutor_dni,
    u.usr_correo as tutor_correo,
    up.usrper_telefono as tutor_telefono
  FROM ninos n
  JOIN usuarios u ON n.usr_id_tutor = u.usr_id
  LEFT JOIN usuarios_perfil up ON u.usr_id = up.usr_id
  WHERE n.nin_id = p_nin_id;

  IF ROW_COUNT() = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado';
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_ninos_obtener_por_tutor;

create
    procedure sp_ninos_obtener_por_tutor(IN p_usr_id_tutor bigint unsigned)
BEGIN
  -- ✅ ARREGLADO: Ahora busca tanto por usr_id_tutor como usr_id_propietario
  SELECT
    n.nin_id,
    n.usr_id_tutor,
    n.usr_id_propietario,
    n.ent_id,
    n.nin_nombres,
    n.nin_fecha_nac,
    n.nin_sexo,
    e.ent_nombre,
    e.ent_codigo,
    e.ent_direccion,
    e.ent_departamento,
    e.ent_provincia,
    e.ent_distrito,
    fn_edad_meses(n.nin_fecha_nac) as edad_meses,
    n.creado_en,
    n.actualizado_en
  FROM ninos n
  LEFT JOIN entidades e ON n.ent_id = e.ent_id
  WHERE (
    -- Buscar por tutor (menores de 13 años)
    n.usr_id_tutor = p_usr_id_tutor
    OR
    -- Buscar por propietario (autogestionados, mayores de 13 años)
    n.usr_id_propietario = p_usr_id_tutor
  )
  ORDER BY n.creado_en DESC;
END;

DROP PROCEDURE IF EXISTS sp_nutrientes_actualizar;

create
    procedure sp_nutrientes_actualizar(IN p_nutri_id smallint unsigned,
                                                          IN p_nutri_codigo varchar(32), IN p_nutri_nombre varchar(120),
                                                          IN p_nutri_unidad varchar(16))
BEGIN
  UPDATE nutrientes
  SET nutri_codigo = p_nutri_codigo,
      nutri_nombre = p_nutri_nombre,
      nutri_unidad = p_nutri_unidad
  WHERE nutri_id = p_nutri_id;

  SELECT nutri_id, nutri_codigo, nutri_nombre, nutri_unidad
  FROM nutrientes
  WHERE nutri_id = p_nutri_id;
END;

DROP PROCEDURE IF EXISTS sp_nutrientes_crear;

create
    procedure sp_nutrientes_crear(IN p_nutri_codigo varchar(32), IN p_nutri_nombre varchar(120),
                                                     IN p_nutri_unidad varchar(16))
BEGIN
  INSERT INTO nutrientes (nutri_codigo, nutri_nombre, nutri_unidad)
  VALUES (p_nutri_codigo, p_nutri_nombre, p_nutri_unidad);

  SELECT nutri_id, nutri_codigo, nutri_nombre, nutri_unidad
  FROM nutrientes
  WHERE nutri_id = LAST_INSERT_ID();
END;

DROP PROCEDURE IF EXISTS sp_nutrientes_eliminar;

create
    procedure sp_nutrientes_eliminar(IN p_nutri_id smallint unsigned)
BEGIN
  DELETE FROM nutrientes WHERE nutri_id = p_nutri_id;
  SELECT ROW_COUNT() as affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_nutrientes_listar;

create
    procedure sp_nutrientes_listar(IN p_query varchar(100), IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 50;

  IF p_limit IS NOT NULL AND p_limit > 0 AND p_limit <= 200 THEN
    SET v_limit = p_limit;
  END IF;

  IF p_query IS NULL OR TRIM(p_query) = '' THEN
    SELECT nutri_id, nutri_codigo, nutri_nombre, nutri_unidad
    FROM nutrientes
    ORDER BY nutri_nombre
    LIMIT v_limit;
  ELSE
    SELECT nutri_id, nutri_codigo, nutri_nombre, nutri_unidad
    FROM nutrientes
    WHERE nutri_nombre LIKE CONCAT('%', p_query, '%')
       OR nutri_codigo LIKE CONCAT('%', p_query, '%')
    ORDER BY nutri_nombre
    LIMIT v_limit;
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_nutrientes_obtener;

create
    procedure sp_nutrientes_obtener(IN p_nutri_id smallint unsigned)
BEGIN
  SELECT nutri_id, nutri_codigo, nutri_nombre, nutri_unidad
  FROM nutrientes
  WHERE nutri_id = p_nutri_id;
END;

DROP PROCEDURE IF EXISTS sp_obtener_datos_para_ml;

create
    procedure sp_obtener_datos_para_ml(IN p_nin_id bigint unsigned)
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

END;

DROP PROCEDURE IF EXISTS sp_obtener_preferencias_nino;

create
    procedure sp_obtener_preferencias_nino(IN p_nin_id bigint unsigned,
                                                              IN p_tipo_comida enum ('DESAYUNO', 'ALMUERZO', 'CENA', 'SNACKS'))
BEGIN
  SELECT
    npc_id,
    npc_preferencia,
    npc_activo,
    creado_en
  FROM ninos_preferencias_comidas
  WHERE nin_id = p_nin_id
    AND npc_tipo_comida = p_tipo_comida
    AND npc_activo = TRUE
  ORDER BY creado_en ASC;
END;

DROP PROCEDURE IF EXISTS sp_perfil_nutricional_vigente;

create
    procedure sp_perfil_nutricional_vigente(IN p_nin_id bigint unsigned)
BEGIN
  SELECT *
  FROM perfil_nutricional_nino
  WHERE nin_id = p_nin_id
    AND pnn_vigente = TRUE
  ORDER BY creado_en DESC
  LIMIT 1;
END;

DROP PROCEDURE IF EXISTS sp_preferencias_desactivar;

create
    procedure sp_preferencias_desactivar(IN p_npc_id bigint unsigned)
BEGIN
  UPDATE ninos_preferencias_comidas
     SET npc_activo = FALSE
   WHERE npc_id = p_npc_id;

  SELECT ROW_COUNT() AS affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_preferencias_listar;

create
    procedure sp_preferencias_listar(IN p_nin_id bigint unsigned,
                                                        IN p_tipo_comida enum ('DESAYUNO', 'ALMUERZO', 'CENA', 'SNACKS'))
BEGIN
  IF p_tipo_comida IS NULL OR TRIM(p_tipo_comida) = '' THEN
    SELECT npc_id,
           npc_tipo_comida,
           npc_preferencia,
           creado_en
      FROM ninos_preferencias_comidas
     WHERE nin_id = p_nin_id
       AND npc_activo = TRUE
     ORDER BY npc_tipo_comida, creado_en ASC;
  ELSE
    SELECT npc_id,
           npc_preferencia,
           creado_en
      FROM ninos_preferencias_comidas
     WHERE nin_id = p_nin_id
       AND npc_tipo_comida = p_tipo_comida
       AND npc_activo = TRUE
     ORDER BY creado_en ASC;
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_preferencias_resumen;

create
    procedure sp_preferencias_resumen(IN p_usr_id bigint unsigned)
BEGIN
  SELECT
    n.nin_id,
    n.nin_nombres,
    COUNT(CASE WHEN npc.npc_activo = TRUE THEN npc.npc_id END) > 0 AS tiene_preferencias,
    COUNT(CASE WHEN npc.npc_activo = TRUE THEN npc.npc_id END) AS total_preferencias,
    MAX(npc.actualizado_en) AS ultima_actualizacion
  FROM ninos n
  LEFT JOIN ninos_preferencias_comidas npc
         ON npc.nin_id = n.nin_id AND npc.npc_activo = TRUE
  WHERE n.usr_id_propietario = p_usr_id OR n.usr_id_tutor = p_usr_id
  GROUP BY n.nin_id, n.nin_nombres
  ORDER BY n.nin_nombres;
END;


DROP PROCEDURE IF EXISTS sp_recetas_actualizar;

create
    procedure sp_recetas_actualizar(IN p_rec_id int unsigned, IN p_rec_nombre varchar(150),
                                                       IN p_rec_instrucciones text, IN p_rec_activo tinyint(1))
BEGIN
  UPDATE recetas
  SET rec_nombre = p_rec_nombre,
      rec_instrucciones = p_rec_instrucciones,
      rec_activo = p_rec_activo,
      actualizado_en = NOW()
  WHERE rec_id = p_rec_id;

  SELECT rec_id, rec_nombre, rec_instrucciones, rec_activo,
         creado_en, actualizado_en
  FROM recetas
  WHERE rec_id = p_rec_id;
END;


DROP PROCEDURE IF EXISTS sp_recetas_aleatorias;

create
    procedure sp_recetas_aleatorias(IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 21;

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 50);
  END IF;

  SELECT
    r.rec_id,
    r.rec_nombre,
    rc.rc_comida
  FROM recetas r
  JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
  WHERE r.rec_activo = 1
  ORDER BY RAND()
  LIMIT v_limit;
END;

DROP PROCEDURE IF EXISTS sp_recetas_buscar;

create
    procedure sp_recetas_buscar(IN p_query varchar(255),
                                                   IN p_tipo_comida enum ('DESAYUNO', 'ALMUERZO', 'CENA', 'REFACCION'),
                                                   IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 20;
  DECLARE v_query VARCHAR(255);

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 100);
  END IF;

  SET v_query = CONCAT('%', COALESCE(p_query, ''), '%');

  IF p_tipo_comida IS NULL OR TRIM(p_tipo_comida) = '' THEN
    SELECT
      r.rec_id,
      r.rec_nombre,
      GROUP_CONCAT(DISTINCT rc.rc_comida) AS rec_tipo_comida,
      COALESCE(SUM(an.an_cantidad_100 * ri.ri_cantidad / 100), 0) AS rec_kcal
    FROM recetas r
    LEFT JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
    LEFT JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
    LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id AND an.nutri_id = 1
    WHERE r.rec_activo = 1 AND r.rec_nombre LIKE v_query
    GROUP BY r.rec_id, r.rec_nombre
    LIMIT v_limit;
  ELSE
    SELECT
      r.rec_id,
      r.rec_nombre,
      GROUP_CONCAT(DISTINCT rc.rc_comida) AS rec_tipo_comida,
      COALESCE(SUM(an.an_cantidad_100 * ri.ri_cantidad / 100), 0) AS rec_kcal
    FROM recetas r
    LEFT JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
    LEFT JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
    LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id AND an.nutri_id = 1
    WHERE r.rec_activo = 1
      AND r.rec_nombre LIKE v_query
      AND rc.rc_comida = p_tipo_comida
    GROUP BY r.rec_id, r.rec_nombre
    LIMIT v_limit;
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_recetas_candidatas;

create
    procedure sp_recetas_candidatas(IN p_nin_id bigint unsigned,
                                                       IN p_tipo_comida enum ('DESAYUNO', 'ALMUERZO', 'CENA', 'REFACCION'),
                                                       IN p_ent_id int unsigned,
                                                       IN p_periodo enum ('Q1', 'Q2', 'Q3', 'Q4'))
BEGIN
  -- Obtiene recetas que:
  -- 1. Son del tipo de comida solicitado
  -- 2. NO contienen alimentos restringidos para el niño
  -- 3. Tienen ingredientes disponibles en la región/periodo

  SELECT DISTINCT
    r.rec_id,
    r.rec_nombre,
    r.rec_instrucciones,
    -- Calcular calorías totales de la receta
    COALESCE(SUM(
      (ri.ri_cantidad / 100) * an.an_cantidad_100
    ), 0) AS rec_calorias_totales,
    -- Contar ingredientes disponibles
    COUNT(DISTINCT da.ali_id) AS ingredientes_disponibles,
    COUNT(DISTINCT ri.ali_id) AS ingredientes_totales
  FROM recetas r
  INNER JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
  INNER JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
  LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id AND an.nutri_id = 1 -- Energía
  LEFT JOIN disponibilidad_alimentos da ON da.ali_id = ri.ali_id
    AND da.ent_id = p_ent_id
    AND da.dis_periodo = p_periodo
    AND da.dis_disponible = 1
  WHERE
    rc.rc_comida = p_tipo_comida
    AND r.rec_activo = 1
    -- Excluir recetas con alimentos restringidos
    AND NOT EXISTS (
      SELECT 1
      FROM ninos_restricciones_alimentos nra
      INNER JOIN recetas_ingredientes ri2 ON ri2.ali_id = nra.ali_id
      WHERE nra.nin_id = p_nin_id
        AND nra.nra_activo = 1
        AND ri2.rec_id = r.rec_id
    )
  GROUP BY r.rec_id, r.rec_nombre, r.rec_instrucciones
  HAVING ingredientes_disponibles >= (ingredientes_totales * 0.7) -- Al menos 70% disponible
  ORDER BY ingredientes_disponibles DESC, rec_calorias_totales DESC
  LIMIT 20;
END;

DROP PROCEDURE IF EXISTS sp_recetas_comidas_crear;

create
    procedure sp_recetas_comidas_crear(IN p_rec_id int unsigned,
                                                          IN p_rc_comida enum ('DESAYUNO', 'ALMUERZO', 'CENA', 'REFACCION'))
BEGIN
    -- Insertar la asociación (ignorar si ya existe)
    INSERT IGNORE INTO recetas_comidas (rec_id, rc_comida)
    VALUES (p_rec_id, p_rc_comida);

    -- Retornar la asociación creada o existente
    SELECT rc.rec_id, rc.rc_comida, r.rec_nombre
    FROM recetas_comidas rc
    JOIN recetas r ON rc.rec_id = r.rec_id
    WHERE rc.rec_id = p_rec_id
      AND rc.rc_comida = p_rc_comida;
END;

DROP PROCEDURE IF EXISTS sp_recetas_comidas_eliminar;

create
    procedure sp_recetas_comidas_eliminar(IN p_rec_id int unsigned,
                                                             IN p_rc_comida enum ('DESAYUNO', 'ALMUERZO', 'CENA', 'REFACCION'))
BEGIN
    -- Eliminar la asociación
    DELETE FROM recetas_comidas
    WHERE rec_id = p_rec_id
      AND rc_comida = p_rc_comida;

    -- Retornar filas afectadas
    SELECT ROW_COUNT() AS affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_recetas_completa_obtener;

create
    procedure sp_recetas_completa_obtener(IN p_rec_id int unsigned)
BEGIN
    -- Información básica de la receta
    SELECT rec_id, rec_nombre, rec_instrucciones, rec_activo,
           creado_en, actualizado_en
    FROM recetas
    WHERE rec_id = p_rec_id;

    -- Ingredientes de la receta
    SELECT ri.rec_id, ri.ali_id, ri.ri_cantidad, ri.ri_unidad,
           a.ali_nombre, a.ali_nombre_cientifico, a.ali_grupo, a.ali_unidad
    FROM recetas_ingredientes ri
    JOIN alimentos a ON ri.ali_id = a.ali_id
    WHERE ri.rec_id = p_rec_id
    ORDER BY a.ali_nombre;

    -- Tipos de comida asociados
    SELECT rc.rec_id, rc.rc_comida
    FROM recetas_comidas rc
    WHERE rc.rec_id = p_rec_id;
END;

DROP PROCEDURE IF EXISTS sp_recetas_crear;

create
    procedure sp_recetas_crear(IN p_rec_nombre varchar(150), IN p_rec_instrucciones text)
BEGIN
  INSERT INTO recetas (rec_nombre, rec_instrucciones, rec_activo)
  VALUES (p_rec_nombre, p_rec_instrucciones, 1);

  SELECT rec_id, rec_nombre, rec_instrucciones, rec_activo,
         creado_en, actualizado_en
  FROM recetas
  WHERE rec_id = LAST_INSERT_ID();
END;

DROP PROCEDURE IF EXISTS sp_recetas_detalle;

create
    procedure sp_recetas_detalle(IN p_rec_id int unsigned)
BEGIN
  SELECT
    r.rec_id,
    r.rec_nombre,
    r.rec_instrucciones,
    r.rec_activo
  FROM recetas r
  WHERE r.rec_id = p_rec_id;
END;

DROP PROCEDURE IF EXISTS sp_recetas_disponibles;

create
    procedure sp_recetas_disponibles(IN p_ent_id bigint unsigned, IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 100;

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 200);
  END IF;

  SELECT
    r.rec_id,
    r.rec_nombre,
    r.rec_instrucciones,
    GROUP_CONCAT(DISTINCT rc.rc_comida) AS tipos_comida,
    COALESCE(SUM(an.an_cantidad_100 * ri.ri_cantidad / 100), 0) AS calorias_aprox
  FROM recetas r
  LEFT JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
  LEFT JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
  LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id AND an.nutri_id = 1
  WHERE r.rec_activo = 1
  GROUP BY r.rec_id, r.rec_nombre, r.rec_instrucciones
  LIMIT v_limit;
END;

DROP PROCEDURE IF EXISTS sp_recetas_eliminar;

create
    procedure sp_recetas_eliminar(IN p_rec_id int unsigned)
BEGIN
  -- Soft delete: marcar como inactivo
  UPDATE recetas SET rec_activo = 0 WHERE rec_id = p_rec_id;
  SELECT ROW_COUNT() as affected_rows;
END;


DROP PROCEDURE IF EXISTS sp_recetas_ingredientes;

create
    procedure sp_recetas_ingredientes(IN p_rec_id int unsigned)
BEGIN
  SELECT
    a.ali_nombre,
    ri.ri_cantidad AS cantidad,
    ri.ri_unidad   AS unidad
  FROM recetas_ingredientes ri
  INNER JOIN alimentos a ON a.ali_id = ri.ali_id
  WHERE ri.rec_id = p_rec_id
  ORDER BY ri.ali_id;
END;

DROP PROCEDURE IF EXISTS sp_recetas_ingredientes_actualizar;

create
    procedure sp_recetas_ingredientes_actualizar(IN p_rec_id int unsigned, IN p_ali_id int unsigned,
                                                                    IN p_ri_cantidad decimal(12, 4),
                                                                    IN p_ri_unidad varchar(16))
BEGIN
  UPDATE recetas_ingredientes
  SET ri_cantidad = p_ri_cantidad,
      ri_unidad = p_ri_unidad
  WHERE rec_id = p_rec_id AND ali_id = p_ali_id;

  SELECT ri.rec_id, ri.ali_id, ri.ri_cantidad, ri.ri_unidad,
         a.ali_nombre, a.ali_grupo
  FROM recetas_ingredientes ri
  JOIN alimentos a ON ri.ali_id = a.ali_id
  WHERE ri.rec_id = p_rec_id AND ri.ali_id = p_ali_id;
END;


DROP PROCEDURE IF EXISTS sp_recetas_ingredientes_crear;

create
    procedure sp_recetas_ingredientes_crear(IN p_rec_id int unsigned, IN p_ali_id int unsigned,
                                                               IN p_ri_cantidad decimal(12, 4),
                                                               IN p_ri_unidad varchar(16))
BEGIN
  INSERT INTO recetas_ingredientes (rec_id, ali_id, ri_cantidad, ri_unidad)
  VALUES (p_rec_id, p_ali_id, p_ri_cantidad, p_ri_unidad);

  SELECT ri.rec_id, ri.ali_id, ri.ri_cantidad, ri.ri_unidad,
         a.ali_nombre, a.ali_grupo
  FROM recetas_ingredientes ri
  JOIN alimentos a ON ri.ali_id = a.ali_id
  WHERE ri.rec_id = p_rec_id AND ri.ali_id = p_ali_id;
END;

DROP PROCEDURE IF EXISTS sp_recetas_ingredientes_eliminar;

create
    procedure sp_recetas_ingredientes_eliminar(IN p_rec_id int unsigned, IN p_ali_id int unsigned)
BEGIN
  DELETE FROM recetas_ingredientes
  WHERE rec_id = p_rec_id AND ali_id = p_ali_id;
  SELECT ROW_COUNT() as affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_recetas_listar;

create
    procedure sp_recetas_listar(IN p_query varchar(100), IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 50;

  IF p_limit IS NOT NULL AND p_limit > 0 AND p_limit <= 200 THEN
    SET v_limit = p_limit;
  END IF;

  IF p_query IS NULL OR TRIM(p_query) = '' THEN
    SELECT rec_id, rec_nombre, rec_instrucciones, rec_activo,
           creado_en, actualizado_en
    FROM recetas
    WHERE rec_activo = 1
    ORDER BY rec_nombre
    LIMIT v_limit;
  ELSE
    SELECT rec_id, rec_nombre, rec_instrucciones, rec_activo,
           creado_en, actualizado_en
    FROM recetas
    WHERE rec_activo = 1
      AND (rec_nombre LIKE CONCAT('%', p_query, '%')
       OR rec_instrucciones LIKE CONCAT('%', p_query, '%'))
    ORDER BY rec_nombre
    LIMIT v_limit;
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_recetas_nutrientes;

create
    procedure sp_recetas_nutrientes(IN p_rec_id int unsigned)
BEGIN
  SELECT
    SUM(CASE WHEN an.nutri_id = 1 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS kcal,
    SUM(CASE WHEN an.nutri_id = 2 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS proteina_g,
    SUM(CASE WHEN an.nutri_id = 3 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS carbohidratos_g,
    SUM(CASE WHEN an.nutri_id = 4 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS grasa_g,
    SUM(CASE WHEN an.nutri_id = 5 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS fibra_g,
    SUM(CASE WHEN an.nutri_id = 6 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS hierro_mg
  FROM recetas_ingredientes ri
  LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id
  WHERE ri.rec_id = p_rec_id;
END;


DROP PROCEDURE IF EXISTS sp_recetas_obtener;

create
    procedure sp_recetas_obtener(IN p_rec_id int unsigned)
BEGIN
  SELECT rec_id, rec_nombre, rec_instrucciones, rec_activo,
         creado_en, actualizado_en
  FROM recetas
  WHERE rec_id = p_rec_id;
END;

DROP PROCEDURE IF EXISTS sp_recetas_plan_actual;

create
    procedure sp_recetas_plan_actual(IN p_nin_id bigint unsigned, IN p_busqueda varchar(255))
BEGIN
    -- Buscar el menú más reciente del niño (últimos 30 días o futuro cercano)
    SELECT DISTINCT
        r.rec_id,
        r.rec_nombre,
        mi.mei_comida AS tipo_comida,
        mi.mei_kcal AS kcal,
        mi.mei_id,
        m.men_id,
        m.men_inicio,
        m.men_fin,
        -- Verificar si ya está en favoritas
        IF(ncf.ncf_id IS NOT NULL, TRUE, FALSE) AS es_favorita,
        -- Verificar si tiene feedback (rating)
        COALESCE(mf.mf_rating, 0) AS rating_actual
    FROM menus m
    INNER JOIN menus_items mi ON m.men_id = mi.men_id
    INNER JOIN recetas r ON mi.rec_id = r.rec_id
    LEFT JOIN ninos_comidas_favoritas ncf ON ncf.nin_id = m.nin_id AND ncf.rec_id = r.rec_id
    LEFT JOIN menus_feedback mf ON mf.mei_id = mi.mei_id AND mf.nin_id = m.nin_id
    WHERE m.nin_id = p_nin_id
      AND m.men_estado IN ('APROBADO', 'BORRADOR', 'ACTIVO', 'GENERADO')
      AND r.rec_activo = 1
      AND (p_busqueda = '' OR r.rec_nombre LIKE CONCAT('%', p_busqueda, '%'))
      -- Buscar menús recientes o futuros (últimos 30 días o próximos 30 días)
      AND m.men_inicio >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
      AND m.men_inicio <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
    ORDER BY m.men_inicio DESC, r.rec_nombre
    LIMIT 100;
END;

DROP PROCEDURE IF EXISTS sp_recetas_por_tipo_comida_listar;

create
    procedure sp_recetas_por_tipo_comida_listar(IN p_tipo_comida enum ('DESAYUNO', 'ALMUERZO', 'CENA', 'REFACCION'),
                                                                   IN p_limit int)
BEGIN
    DECLARE v_limit INT DEFAULT 50;

    IF p_limit IS NOT NULL AND p_limit > 0 THEN
        SET v_limit = p_limit;
    END IF;

    SELECT DISTINCT r.rec_id, r.rec_nombre, r.rec_instrucciones,
           r.rec_activo, r.creado_en, r.actualizado_en
    FROM recetas r
    JOIN recetas_comidas rc ON r.rec_id = rc.rec_id
    WHERE r.rec_activo = 1
      AND rc.rc_comida = p_tipo_comida
    ORDER BY r.rec_nombre
    LIMIT v_limit;
END;

DROP PROCEDURE IF EXISTS sp_registrar_autogestionado;

create
    procedure sp_registrar_autogestionado(IN p_nombres varchar(150), IN p_apellidos varchar(150),
                                                             IN p_usuario varchar(150), IN p_correo varchar(190),
                                                             IN p_contrasena_hash varchar(255),
                                                             IN p_usr_dni varchar(12), IN p_avatar_url varchar(255),
                                                             IN p_telefono varchar(20), IN p_direccion varchar(180),
                                                             IN p_genero_usr char, IN p_idioma varchar(10),
                                                             IN p_fecha_nac_nino date, IN p_sexo_nino char,
                                                             IN p_ent_id int unsigned)
BEGIN
  DECLARE v_rol_id SMALLINT UNSIGNED;
  DECLARE v_usr_id BIGINT UNSIGNED;
  DECLARE v_nin_id BIGINT UNSIGNED;

  -- Rol base
  SELECT rol_id INTO v_rol_id
  FROM roles
  WHERE rol_codigo IN ('ADOLESCENTE','USR','USUARIO')
  ORDER BY rol_id LIMIT 1;

  IF v_rol_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Configura un rol base (ADOLESCENTE/USUARIO)';
  END IF;

  INSERT INTO usuarios(usr_dni, usr_correo, usr_contrasena, usr_nombre, usr_apellido, usr_usuario, rol_id, usr_activo)
  VALUES (p_usr_dni, p_correo, p_contrasena_hash, p_nombres, p_apellidos, p_usuario, v_rol_id, 1);
  SET v_usr_id = LAST_INSERT_ID();

  CALL sp_usuarios_perfil_guardar(
    v_usr_id, p_usr_dni, p_nombres, p_apellidos,
    p_avatar_url, p_telefono, p_direccion, p_genero_usr, NULL, p_idioma
  );

  CALL sp_ninos_crear(CONCAT(p_nombres,' ',p_apellidos), p_fecha_nac_nino, p_sexo_nino,
                      p_ent_id, NULL, v_usr_id);

  -- Devuelve todo
  SELECT v_usr_id AS usr_id, (SELECT LAST_INSERT_ID()) AS nin_id, 'OK' AS msg;
END;

DROP PROCEDURE IF EXISTS sp_registrar_menor_con_tutor;

create
    procedure sp_registrar_menor_con_tutor(IN p_usr_id_tutor bigint unsigned,
                                                              IN p_nin_nombres varchar(150), IN p_fecha_nac date,
                                                              IN p_sexo_nino char, IN p_ent_id int unsigned)
BEGIN
  IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id_tutor) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Tutor no existe';
  END IF;

  CALL sp_ninos_crear(p_nin_nombres, p_fecha_nac, p_sexo_nino, p_ent_id, p_usr_id_tutor, NULL);
END;

DROP PROCEDURE IF EXISTS sp_roles_get_codigo_by_id;

create
    procedure sp_roles_get_codigo_by_id(IN p_rol_id bigint unsigned)
BEGIN
  SELECT rol_codigo
  FROM roles
  WHERE rol_id = p_rol_id
  LIMIT 1;
END;

DROP PROCEDURE IF EXISTS sp_roles_insertar;

create
    procedure sp_roles_insertar(IN p_rol_codigo varchar(32), IN p_rol_nombre varchar(80))
BEGIN
  DECLARE v_id SMALLINT UNSIGNED;

  -- ¿ya existe por código o nombre?
  SELECT rol_id INTO v_id
  FROM roles
  WHERE rol_codigo = p_rol_codigo OR rol_nombre = p_rol_nombre
  LIMIT 1;

  IF v_id IS NULL THEN
    INSERT INTO roles(rol_codigo, rol_nombre)
    VALUES (p_rol_codigo, p_rol_nombre);
    SET v_id = LAST_INSERT_ID();
  END IF;

  -- Resultado uniforme
  SELECT v_id AS rol_id, 'OK' AS msg;
END;

DROP PROCEDURE IF EXISTS sp_roles_nombre_por_id;

create
    procedure sp_roles_nombre_por_id(IN p_rol_id int)
BEGIN
  SELECT rol_nombre
    FROM roles
   WHERE rol_id = p_rol_id
   LIMIT 1;
END;

DROP PROCEDURE IF EXISTS sp_tipos_alergias_buscar;

create
    procedure sp_tipos_alergias_buscar(IN p_query varchar(100), IN p_limit int)
BEGIN
  DECLARE v_limit INT DEFAULT 50;

  -- Establecer límite (máximo 100)
  IF p_limit IS NOT NULL AND p_limit > 0 AND p_limit <= 100 THEN
    SET v_limit = p_limit;
  END IF;

  -- Si no hay query, retornar todos los activos
  IF p_query IS NULL OR TRIM(p_query) = '' THEN
    SELECT
      ta_id,
      ta_codigo,
      ta_nombre,
      ta_categoria,
      ta_activo,
      creado_en
    FROM tipos_alergias
    WHERE ta_activo = 1
    ORDER BY ta_nombre
    LIMIT v_limit;
  ELSE
    -- Buscar por código o nombre
    SELECT
      ta_id,
      ta_codigo,
      ta_nombre,
      ta_categoria,
      ta_activo,
      creado_en
    FROM tipos_alergias
    WHERE ta_activo = 1
      AND (
        ta_codigo LIKE CONCAT('%', p_query, '%')
        OR ta_nombre LIKE CONCAT('%', p_query, '%')
      )
    ORDER BY
      CASE
        WHEN ta_codigo = p_query THEN 1
        WHEN ta_nombre = p_query THEN 2
        WHEN ta_codigo LIKE CONCAT(p_query, '%') THEN 3
        WHEN ta_nombre LIKE CONCAT(p_query, '%') THEN 4
        ELSE 5
      END,
      ta_nombre
    LIMIT v_limit;
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_top_recetas_por_nombre;

create
    procedure sp_top_recetas_por_nombre(IN p_q_nombre varchar(150), IN p_rc_comida varchar(10),
                                                           IN p_n_top int)
BEGIN
  DECLARE v_nin_id  BIGINT DEFAULT NULL;
  DECLARE v_rc      VARCHAR(10);
  DECLARE v_limit   INT;

  -- Normaliza comida y límite
  SET v_rc = CASE UPPER(COALESCE(p_rc_comida,'DESAYUNO'))
               WHEN 'ALMUERZO' THEN 'ALMUERZO'
               WHEN 'CENA'     THEN 'CENA'
               ELSE 'DESAYUNO'
             END;
  SET v_limit = IFNULL(p_n_top, 3);

  -- 1) Resolver niño por nombre: exacto > fulltext > like (sin CTE)
  SELECT cand.nin_id
    INTO v_nin_id
  FROM (
    SELECT n.nin_id, n.nin_nombres AS nm, 3 AS peso
    FROM ninos n
    WHERE n.nin_nombres COLLATE utf8mb4_0900_ai_ci = p_q_nombre

    UNION ALL
    SELECT n.nin_id, n.nin_nombres AS nm,
           MATCH(n.nin_nombres) AGAINST (p_q_nombre IN NATURAL LANGUAGE MODE) AS peso
    FROM ninos n
    WHERE MATCH(n.nin_nombres) AGAINST (p_q_nombre IN NATURAL LANGUAGE MODE)

    UNION ALL
    SELECT n.nin_id, n.nin_nombres AS nm, 1 AS peso
    FROM ninos n
    WHERE n.nin_nombres COLLATE utf8mb4_0900_ai_ci LIKE CONCAT('%', p_q_nombre, '%')
  ) AS cand
  ORDER BY cand.peso DESC, CHAR_LENGTH(cand.nm) DESC
  LIMIT 1;

  -- 2) Si no hay match, devuelve 1 fila “NO_MATCH”
  IF v_nin_id IS NULL THEN
    SELECT 'NO_MATCH' AS status,
           p_q_nombre AS q_nombre,
           v_rc       AS rc_comida,
           NULL AS rec_id, NULL AS rec_nombre,
           NULL AS kcal, NULL AS proteina_g, NULL AS hierro_mg, NULL AS fibra_g,
           NULL AS costo_soles_aprox, NULL AS score,
           NULL AS en_clasificacion, NULL AS nin_id;
  ELSE
    -- 3) Top-N para ese niño y tipo de comida
    SELECT
      'OK' AS status,
      t.nin_nombres, t.en_clasificacion, t.rc_comida,
      t.rec_id, t.rec_nombre,
      t.kcal, t.proteina_g, t.hierro_mg, t.fibra_g,
      t.costo_soles_aprox, t.score,
      t.nin_id
    FROM v_recetas_scores_por_nino t
    WHERE t.nin_id = v_nin_id
      AND t.rc_comida = v_rc
    ORDER BY t.score DESC
    LIMIT v_limit;
  END IF;
END;

DROP PROCEDURE IF EXISTS sp_usuarios_anonimizar;

create
    procedure sp_usuarios_anonimizar(IN p_usr_id bigint unsigned, IN p_usuario_temp varchar(255),
                                                        IN p_correo_temp varchar(255), IN p_password_hash varchar(255),
                                                        IN p_telefono varchar(20))
BEGIN
  UPDATE usuarios
     SET usr_correo = p_correo_temp,
         usr_contrasena = p_password_hash,
         usr_nombre = 'Cuenta eliminada',
         usr_apellido = 'NutriFamily',
         usr_usuario = p_usuario_temp,
         usr_activo = 0,
         eliminado_en = NOW()
   WHERE usr_id = p_usr_id;

  UPDATE usuarios_perfil
     SET usrper_avatar_url = NULL,
         usrper_telefono   = p_telefono,
         usrper_direccion  = NULL,
         usrper_genero     = NULL,
         usrper_fecha_nac  = NULL,
         usrper_idioma     = 'es-PE',
         eliminado_en      = NOW()
   WHERE usr_id = p_usr_id;

  SELECT ROW_COUNT() AS affected_rows;
END;

DROP PROCEDURE IF EXISTS sp_usuarios_existe_username;

create
    procedure sp_usuarios_existe_username(IN p_username varchar(50))
BEGIN
  SELECT EXISTS(
    SELECT 1
    FROM usuarios
    WHERE usr_usuario = p_username
  ) as existe;
END;


DROP PROCEDURE IF EXISTS sp_usuarios_obtener_por_email;

create
    procedure sp_usuarios_obtener_por_email(IN p_correo varchar(255))
BEGIN
  SELECT
    u.usr_id,
    u.usr_usuario,
    u.usr_correo,
    u.usr_nombre AS usr_nombre,
    u.usr_apellido AS usr_apellido,
    u.rol_id,
    r.rol_nombre,
    u.usr_activo,
    u.usr_contrasena AS password_hash
  FROM usuarios u
  LEFT JOIN roles r ON u.rol_id = r.rol_id
  WHERE u.usr_correo = p_correo
  LIMIT 1;
END;



DROP PROCEDURE IF EXISTS sp_usuarios_obtener_por_id;

create
    procedure sp_usuarios_obtener_por_id(IN p_usr_id bigint unsigned)
BEGIN
  SELECT
    u.usr_id,
    u.usr_usuario,
    u.usr_correo,
    u.usr_nombre AS usr_nombre,
    u.usr_apellido AS usr_apellido,
    u.rol_id,
    r.rol_nombre,
    u.usr_activo,
    u.usr_contrasena AS password_hash
  FROM usuarios u
  LEFT JOIN roles r ON u.rol_id = r.rol_id
  WHERE u.usr_id = p_usr_id
  LIMIT 1;
END;


DROP PROCEDURE IF EXISTS sp_usuarios_perfil_actualizar_avatar;

create
    procedure sp_usuarios_perfil_actualizar_avatar(IN p_usr_id bigint unsigned,
                                                                      IN p_avatar_url mediumtext,
                                                                      IN p_telefono varchar(20),
                                                                      IN p_idioma varchar(10))
BEGIN
  DECLARE v_telefono VARCHAR(20);
  DECLARE v_idioma VARCHAR(10);

  -- Valores por defecto
  SET v_telefono = COALESCE(NULLIF(TRIM(p_telefono), ''), '000000000');
  SET v_idioma = COALESCE(NULLIF(TRIM(p_idioma), ''), 'es-PE');

  -- Insertar o actualizar el perfil
  INSERT INTO usuarios_perfil (
    usr_id,
    usrper_avatar_url,
    usrper_telefono,
    usrper_idioma
  ) VALUES (
    p_usr_id,
    p_avatar_url,
    v_telefono,
    v_idioma
  )
  ON DUPLICATE KEY UPDATE
    usrper_avatar_url = VALUES(usrper_avatar_url),
    actualizado_en = NOW();
END;


DROP PROCEDURE IF EXISTS sp_usuarios_perfil_get;

create
    procedure sp_usuarios_perfil_get(IN p_usr_id bigint unsigned)
BEGIN
  SELECT
    u.usr_id, u.usr_nombre, u.usr_apellido, u.usr_dni, u.usr_correo,
    up.usrper_avatar_url  AS avatar,
    up.usrper_telefono    AS telefono,
    up.usrper_direccion   AS direccion,
    up.usrper_genero      AS genero,
    up.usrper_fecha_nac   AS fecha_nac,
    up.usrper_idioma      AS idioma
  FROM usuarios u
  LEFT JOIN usuarios_perfil up ON up.usr_id = u.usr_id
  WHERE u.usr_id = p_usr_id;
END;


DROP PROCEDURE IF EXISTS sp_usuarios_perfil_guardar;

create
    procedure sp_usuarios_perfil_guardar(IN p_usr_id bigint unsigned, IN p_usr_dni varchar(12),
                                                            IN p_nombres varchar(150), IN p_apellidos varchar(150),
                                                            IN p_avatar_url mediumtext, IN p_telefono varchar(20),
                                                            IN p_direccion varchar(180), IN p_genero char,
                                                            IN p_fecha_nac date, IN p_idioma varchar(10))
BEGIN
  IF p_usr_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id requerido';
  END IF;

  IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El usuario no existe';
  END IF;

  -- Actualiza tabla usuarios (DNI, nombres y apellidos si vienen)
  UPDATE usuarios
     SET usr_dni     = COALESCE(NULLIF(p_usr_dni,''), usr_dni),
         usr_nombre  = COALESCE(NULLIF(p_nombres,''), usr_nombre),
         usr_apellido= COALESCE(NULLIF(p_apellidos,''), usr_apellido)
   WHERE usr_id = p_usr_id;

  -- Upsert en usuarios_perfil
  IF EXISTS(SELECT 1 FROM usuarios_perfil WHERE usr_id=p_usr_id) THEN
    UPDATE usuarios_perfil
       SET usrper_avatar_url = COALESCE(p_avatar_url, usrper_avatar_url),
           usrper_telefono   = COALESCE(p_telefono, usrper_telefono),
           usrper_direccion  = COALESCE(p_direccion, usrper_direccion),
           usrper_genero     = COALESCE(p_genero, usrper_genero),
           usrper_fecha_nac  = COALESCE(p_fecha_nac, usrper_fecha_nac),
           usrper_idioma     = COALESCE(p_idioma, usrper_idioma)
     WHERE usr_id = p_usr_id;
  ELSE
    INSERT INTO usuarios_perfil(
      usr_id, usrper_avatar_url, usrper_telefono, usrper_direccion,
      usrper_genero, usrper_fecha_nac, usrper_idioma
    ) VALUES(
      p_usr_id, p_avatar_url, p_telefono, p_direccion,
      p_genero, p_fecha_nac, COALESCE(p_idioma,'es-PE')
    );
  END IF;

  -- Devuelve perfil completo
  SELECT
    u.usr_id, u.usr_nombre, u.usr_apellido, u.usr_dni, u.usr_correo,
    up.usrper_avatar_url  AS avatar,
    up.usrper_telefono    AS telefono,
    up.usrper_direccion   AS direccion,
    up.usrper_genero      AS genero,
    up.usrper_fecha_nac   AS fecha_nac,
    up.usrper_idioma      AS idioma
  FROM usuarios u
  LEFT JOIN usuarios_perfil up ON up.usr_id = u.usr_id
  WHERE u.usr_id = p_usr_id;
END;


DROP PROCEDURE IF EXISTS sp_usuarios_registrar;

create
    procedure sp_usuarios_registrar(IN p_nombres varchar(150), IN p_apellidos varchar(150),
                                                       IN p_usuario varchar(150), IN p_correo varchar(190),
                                                       IN p_contrasena_hash varchar(255), IN p_rol_nombre varchar(80))
BEGIN
  DECLARE v_rol_id SMALLINT UNSIGNED;
  DECLARE v_usr_id BIGINT UNSIGNED;
  DECLARE v_exists INT DEFAULT 0;

  -- rol por nombre
  SELECT rol_id INTO v_rol_id FROM roles WHERE rol_nombre = p_rol_nombre LIMIT 1;
  IF v_rol_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El rol no existe: use sp_roles_insertar primero';
  END IF;

  -- duplicados
  SELECT COUNT(*) INTO v_exists FROM usuarios WHERE usr_correo = p_correo;
  IF v_exists > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Correo ya registrado';
  END IF;

  SELECT COUNT(*) INTO v_exists FROM usuarios WHERE usr_usuario = p_usuario;
  IF v_exists > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuario ya registrado';
  END IF;

  -- inserción
  INSERT INTO usuarios(
    usr_dni, usr_correo, usr_contrasena, usr_nombre, usr_apellido, usr_usuario,
    rol_id, usr_activo
  ) VALUES (
    NULL, p_correo, p_contrasena_hash, p_nombres, p_apellidos, p_usuario,
    v_rol_id, 1
  );

  SET v_usr_id = LAST_INSERT_ID();

  -- resultado
  SELECT v_usr_id AS usr_id, 'OK' AS msg;
END;
