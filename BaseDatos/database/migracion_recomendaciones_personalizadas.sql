USE nutricion;

-- ============================================================================
-- 1. PREFERENCIAS DE COMIDAS POR NIÑO
-- ============================================================================
-- Almacena las preferencias alimentarias del niño por tipo de comida
-- Ejemplo: Pedrito prefiere "Avena", "Huevos", "Frutas" para DESAYUNO

CREATE TABLE IF NOT EXISTS ninos_preferencias_comidas (
  npc_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id BIGINT UNSIGNED NOT NULL,
  npc_tipo_comida ENUM('DESAYUNO','ALMUERZO','CENA','SNACKS') NOT NULL,
  npc_preferencia VARCHAR(100) NOT NULL COMMENT 'Nombre de la preferencia: Avena, Huevos, Frutas, etc.',
  npc_activo BOOLEAN NOT NULL DEFAULT TRUE,

  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_npc_nino FOREIGN KEY (nin_id)
    REFERENCES ninos(nin_id) ON DELETE CASCADE,

  INDEX idx_npc_nino_tipo (nin_id, npc_tipo_comida),
  INDEX idx_npc_activo (npc_activo),
  INDEX idx_npc_tipo_comida (npc_tipo_comida)
) ENGINE=InnoDB COMMENT='Preferencias alimentarias por niño y tipo de comida';

-- ============================================================================
-- 2. PERFIL NUTRICIONAL DEL NIÑO
-- ============================================================================
-- Almacena los requerimientos nutricionales calculados para cada niño
-- basados en edad, peso, talla, clasificación nutricional

CREATE TABLE IF NOT EXISTS perfil_nutricional_nino (
  pnn_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id BIGINT UNSIGNED NOT NULL,

  -- Requerimientos diarios (macronutrientes)
  pnn_calorias_diarias INT NOT NULL COMMENT 'kcal/día según edad y clasificación',
  pnn_proteinas_g DECIMAL(6,2) NOT NULL COMMENT 'Gramos de proteína/día',
  pnn_carbohidratos_g DECIMAL(6,2) NOT NULL COMMENT 'Gramos de carbohidratos/día',
  pnn_grasas_g DECIMAL(6,2) NOT NULL COMMENT 'Gramos de grasa/día',

  -- Micronutrientes importantes (según OMS/FAO)
  pnn_hierro_mg DECIMAL(6,2) NULL COMMENT 'Hierro en mg/día',
  pnn_calcio_mg DECIMAL(6,2) NULL COMMENT 'Calcio en mg/día',
  pnn_vitamina_a_ug DECIMAL(6,2) NULL COMMENT 'Vitamina A en µg/día',
  pnn_vitamina_c_mg DECIMAL(6,2) NULL COMMENT 'Vitamina C en mg/día',
  pnn_zinc_mg DECIMAL(6,2) NULL COMMENT 'Zinc en mg/día',
  pnn_fibra_g DECIMAL(6,2) NULL COMMENT 'Fibra en g/día',

  -- Metadata del cálculo
  pnn_edad_meses SMALLINT UNSIGNED NOT NULL COMMENT 'Edad al momento del cálculo',
  pnn_peso_kg DECIMAL(5,2) NULL COMMENT 'Peso usado en el cálculo',
  pnn_talla_cm DECIMAL(5,2) NULL COMMENT 'Talla usada en el cálculo',
  pnn_clasificacion ENUM('DESNUTRICION_SEVERA','DESNUTRICION','RIESGO','NORMAL','SOBREPESO','OBESIDAD') NULL,
  pnn_metodo_calculo VARCHAR(50) NOT NULL DEFAULT 'OMS_FAO' COMMENT 'Método: OMS_FAO, HARRIS_BENEDICT, etc',
  pnn_factor_actividad DECIMAL(3,2) NULL DEFAULT 1.5 COMMENT 'Factor de actividad física',
  pnn_observaciones TEXT NULL,

  -- Control de vigencia
  pnn_vigente BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Solo un perfil vigente por niño',
  pnn_fecha_calculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_pnn_nino FOREIGN KEY (nin_id)
    REFERENCES ninos(nin_id) ON DELETE CASCADE,

  INDEX idx_pnn_nino_vigente (nin_id, pnn_vigente),
  INDEX idx_pnn_clasificacion (pnn_clasificacion)
) ENGINE=InnoDB COMMENT='Requerimientos nutricionales calculados por niño';


-- ============================================================================
-- 3. RESTRICCIONES ALIMENTARIAS POR NIÑO
-- ============================================================================
-- Complementa ninos_alergias con restricciones específicas de alimentos
-- Permite filtrar recetas que contengan ingredientes prohibidos

CREATE TABLE IF NOT EXISTS ninos_restricciones_alimentos (
  nra_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id BIGINT UNSIGNED NOT NULL,
  ali_id INT UNSIGNED NOT NULL COMMENT 'Alimento específico restringido',

  nra_tipo ENUM('ALERGIA','INTOLERANCIA','PREFERENCIA','CULTURAL','RELIGIOSA','MEDICA') NOT NULL,
  nra_severidad ENUM('LEVE','MODERADA','SEVERA') NOT NULL DEFAULT 'MODERADA',
  nra_notas TEXT NULL COMMENT 'Detalles adicionales de la restricción',
  nra_activo BOOLEAN NOT NULL DEFAULT TRUE,

  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uk_nino_alimento (nin_id, ali_id),
  CONSTRAINT fk_nra_nino FOREIGN KEY (nin_id)
    REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_nra_alimento FOREIGN KEY (ali_id)
    REFERENCES alimentos(ali_id) ON DELETE CASCADE,

  INDEX idx_nra_tipo (nra_tipo),
  INDEX idx_nra_activo (nra_activo)
) ENGINE=InnoDB COMMENT='Restricciones alimentarias específicas por niño';

-- ============================================================================
-- 4. FEEDBACK DE MENÚS (Para aprendizaje del sistema)
-- ============================================================================
-- Registra si el niño consumió la comida y cómo la calificó
-- Permite mejorar futuras recomendaciones

CREATE TABLE IF NOT EXISTS menus_feedback (
  mf_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  mei_id BIGINT UNSIGNED NOT NULL COMMENT 'Item del menú evaluado',
  nin_id BIGINT UNSIGNED NOT NULL,

  mf_completado BOOLEAN NOT NULL DEFAULT FALSE COMMENT '¿Se consumió la comida?',
  mf_porcentaje_consumido TINYINT NULL COMMENT '0-100% de lo que comió',
  mf_rating TINYINT NULL COMMENT 'Calificación 1-5 estrellas',
  mf_notas TEXT NULL COMMENT 'Comentarios del tutor o niño',
  mf_fecha_consumo DATE NOT NULL,
  mf_registrado_por BIGINT UNSIGNED NULL COMMENT 'Usuario que registró (tutor/nutricionista)',

  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uk_feedback_item (mei_id, mf_fecha_consumo),
  CONSTRAINT fk_mf_item FOREIGN KEY (mei_id)
    REFERENCES menus_items(mei_id) ON DELETE CASCADE,
  CONSTRAINT fk_mf_nino FOREIGN KEY (nin_id)
    REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_mf_usuario FOREIGN KEY (mf_registrado_por)
    REFERENCES usuarios(usr_id) ON DELETE SET NULL,

  INDEX idx_mf_nino_fecha (nin_id, mf_fecha_consumo),
  INDEX idx_mf_rating (mf_rating)
) ENGINE=InnoDB COMMENT='Feedback de consumo y preferencias de menús';


-- ============================================================================
-- 5. CACHE DE NUTRIENTES POR RECETA (Optimización)
-- ============================================================================
-- Pre-calcula los valores nutricionales totales de cada receta
-- Evita JOINs complejos al buscar recetas candidatas

CREATE TABLE IF NOT EXISTS recetas_nutrientes_cache (
  rec_id INT UNSIGNED NOT NULL,
  nutri_id SMALLINT UNSIGNED NOT NULL,
  rnc_cantidad_total DECIMAL(12,4) NOT NULL COMMENT 'Cantidad total del nutriente en la receta',
  rnc_cantidad_porcion DECIMAL(12,4) NULL COMMENT 'Por porción estándar (si aplica)',

  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (rec_id, nutri_id),
  CONSTRAINT fk_rnc_receta FOREIGN KEY (rec_id)
    REFERENCES recetas(rec_id) ON DELETE CASCADE,
  CONSTRAINT fk_rnc_nutriente FOREIGN KEY (nutri_id)
    REFERENCES nutrientes(nutri_id) ON DELETE CASCADE,

  INDEX idx_rnc_nutriente (nutri_id, rnc_cantidad_total)
) ENGINE=InnoDB COMMENT='Cache de valores nutricionales por receta';

-- ============================================================================
-- 6. MODIFICACIONES A TABLA ENTIDADES
-- ============================================================================
-- Agregar información geográfica para filtrado regional

ALTER TABLE entidades
  ADD COLUMN ent_poblacion_aprox INT NULL COMMENT 'Población aproximada del área' AFTER ent_zona;

-- ============================================================================
-- 7. ÍNDICES ADICIONALES PARA OPTIMIZACIÓN
-- ============================================================================

-- Índice para búsqueda rápida de recetas por tipo de comida
CREATE INDEX idx_rc_comida ON recetas_comidas(rc_comida);

-- Índice para búsqueda de menús activos por niño
CREATE INDEX idx_menus_nino_estado ON menus(nin_id, men_estado, men_inicio);

-- Índice para disponibilidad de alimentos por región y periodo
CREATE INDEX idx_dis_region_periodo ON disponibilidad_alimentos(dis_region, dis_periodo, dis_disponible);

-- Índice para ingredientes de recetas (búsqueda inversa)
CREATE INDEX idx_ri_alimento ON recetas_ingredientes(ali_id);



DELIMITER $$

DROP TRIGGER IF EXISTS trg_pnn_vigente_unico$$

CREATE TRIGGER trg_pnn_vigente_unico
BEFORE INSERT ON perfil_nutricional_nino
FOR EACH ROW
BEGIN
  -- Si el nuevo perfil es vigente, desactivar los anteriores del mismo niño
  IF NEW.pnn_vigente = TRUE THEN
    UPDATE perfil_nutricional_nino
    SET pnn_vigente = FALSE
    WHERE nin_id = NEW.nin_id AND pnn_vigente = TRUE;
  END IF;
END$$

DELIMITER ;


-- ============================================================================
-- 11. PROCEDIMIENTO: Obtener preferencias de un niño
-- ============================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_obtener_preferencias_nino$$

CREATE PROCEDURE sp_obtener_preferencias_nino(
  IN p_nin_id BIGINT UNSIGNED,
  IN p_tipo_comida ENUM('DESAYUNO','ALMUERZO','CENA','SNACKS')
)
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
END$$

DELIMITER ;

-- ============================================================================
-- 12. PROCEDIMIENTO: Guardar preferencias de un niño
-- ============================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_guardar_preferencias_nino$$

CREATE PROCEDURE sp_guardar_preferencias_nino(
  IN p_nin_id BIGINT UNSIGNED,
  IN p_tipo_comida ENUM('DESAYUNO','ALMUERZO','CENA','SNACKS'),
  IN p_preferencias JSON -- Array: ["Avena", "Huevos", "Frutas"]
)
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
END$$

DELIMITER ;

-- ============================================================================
-- 13. PROCEDIMIENTO: Calcular y guardar perfil nutricional
-- ============================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_calcular_perfil_nutricional$$

CREATE PROCEDURE sp_calcular_perfil_nutricional(
  IN p_nin_id BIGINT UNSIGNED
)
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

  -- Calcular requerimientos según edad (simplificado - ajustar según OMS/FAO)
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
    SET v_calorias = v_calorias * 1.2; -- +20% para recuperación
    SET v_proteinas = v_proteinas * 1.3; -- +30% proteína
  ELSEIF v_clasificacion = 'SOBREPESO' THEN
    SET v_calorias = v_calorias * 0.9; -- -10%
  ELSEIF v_clasificacion = 'OBESIDAD' THEN
    SET v_calorias = v_calorias * 0.8; -- -20%
  END IF;

  -- Calcular macronutrientes (distribución estándar)
  SET v_carbohidratos = (v_calorias * 0.55) / 4; -- 55% de calorías, 4 kcal/g
  SET v_grasas = (v_calorias * 0.30) / 9; -- 30% de calorías, 9 kcal/g

  -- Insertar perfil nutricional
  INSERT INTO perfil_nutricional_nino (
    nin_id, pnn_calorias_diarias, pnn_proteinas_g, pnn_carbohidratos_g, pnn_grasas_g,
    pnn_hierro_mg, pnn_calcio_mg, pnn_vitamina_a_ug, pnn_vitamina_c_mg, pnn_zinc_mg, pnn_fibra_g,
    pnn_edad_meses, pnn_peso_kg, pnn_talla_cm, pnn_clasificacion, pnn_vigente
  ) VALUES (
    p_nin_id, v_calorias, v_proteinas, v_carbohidratos, v_grasas,
    10, 800, 400, 25, 5, v_edad_meses / 3, -- Fibra: edad/3 (aprox)
    v_edad_meses, v_peso_kg, v_talla_cm, v_clasificacion, TRUE
  );

  SELECT 'Perfil nutricional calculado exitosamente' AS mensaje, LAST_INSERT_ID() AS pnn_id;
END$$

DELIMITER ;


-- ============================================================================
-- 14. PROCEDIMIENTO: Obtener recetas candidatas para un niño
-- ============================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_recetas_candidatas$$

CREATE PROCEDURE sp_recetas_candidatas(
  IN p_nin_id BIGINT UNSIGNED,
  IN p_tipo_comida ENUM('DESAYUNO','ALMUERZO','CENA','REFACCION'),
  IN p_ent_id INT UNSIGNED,
  IN p_periodo ENUM('Q1','Q2','Q3','Q4')
)
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
END$$

DELIMITER ;

-- ============================================================================
-- 15. PROCEDIMIENTO: Popular cache de nutrientes de recetas
-- ============================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_actualizar_cache_nutrientes$$

CREATE PROCEDURE sp_actualizar_cache_nutrientes(
  IN p_rec_id INT UNSIGNED
)
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
END$$

DELIMITER ;

-- ============================================================================
-- 16. VISTA: Resumen de preferencias por niño
-- ============================================================================

CREATE OR REPLACE VIEW v_preferencias_ninos AS
SELECT
  n.nin_id,
  n.nin_nombres,
  npc.npc_tipo_comida,
  GROUP_CONCAT(npc.npc_preferencia ORDER BY npc.creado_en SEPARATOR ', ') AS preferencias,
  COUNT(*) AS total_preferencias
FROM ninos n
INNER JOIN ninos_preferencias_comidas npc ON npc.nin_id = n.nin_id
WHERE npc.npc_activo = TRUE
GROUP BY n.nin_id, n.nin_nombres, npc.npc_tipo_comida;

-- ============================================================================
-- 17. VISTA: Resumen de perfiles nutricionales vigentes
-- ============================================================================

CREATE OR REPLACE VIEW v_perfiles_nutricionales_vigentes AS
SELECT
  n.nin_id,
  n.nin_nombres,
  TIMESTAMPDIFF(YEAR, n.nin_fecha_nac, CURDATE()) AS edad_anos,
  pnn.pnn_calorias_diarias,
  pnn.pnn_proteinas_g,
  pnn.pnn_carbohidratos_g,
  pnn.pnn_grasas_g,
  pnn.pnn_clasificacion,
  pnn.pnn_fecha_calculo,
  -- Contar restricciones activas
  COUNT(DISTINCT nra.nra_id) AS total_restricciones
FROM ninos n
INNER JOIN perfil_nutricional_nino pnn ON pnn.nin_id = n.nin_id AND pnn.pnn_vigente = TRUE
LEFT JOIN ninos_restricciones_alimentos nra ON nra.nin_id = n.nin_id AND nra.nra_activo = TRUE
GROUP BY n.nin_id, n.nin_nombres, pnn.pnn_id;



USE nutricion;

-- Llamar al procedimiento para cada receta existente
-- DESAYUNOS
CALL sp_actualizar_cache_nutrientes(200);
CALL sp_actualizar_cache_nutrientes(204);
CALL sp_actualizar_cache_nutrientes(212);
CALL sp_actualizar_cache_nutrientes(215);
CALL sp_actualizar_cache_nutrientes(216);
CALL sp_actualizar_cache_nutrientes(221);
CALL sp_actualizar_cache_nutrientes(229);

-- ALMUERZOS
CALL sp_actualizar_cache_nutrientes(201);
CALL sp_actualizar_cache_nutrientes(202);
CALL sp_actualizar_cache_nutrientes(205);
CALL sp_actualizar_cache_nutrientes(210);
CALL sp_actualizar_cache_nutrientes(211);
CALL sp_actualizar_cache_nutrientes(213);
CALL sp_actualizar_cache_nutrientes(214);
CALL sp_actualizar_cache_nutrientes(219);
CALL sp_actualizar_cache_nutrientes(220);
CALL sp_actualizar_cache_nutrientes(224);
CALL sp_actualizar_cache_nutrientes(225);
CALL sp_actualizar_cache_nutrientes(226);
CALL sp_actualizar_cache_nutrientes(217);
CALL sp_actualizar_cache_nutrientes(218);
CALL sp_actualizar_cache_nutrientes(208);

-- CENAS
CALL sp_actualizar_cache_nutrientes(203);
CALL sp_actualizar_cache_nutrientes(206);
CALL sp_actualizar_cache_nutrientes(207);
CALL sp_actualizar_cache_nutrientes(223);
CALL sp_actualizar_cache_nutrientes(227);
CALL sp_actualizar_cache_nutrientes(228);
CALL sp_actualizar_cache_nutrientes(222);

-- Verificar resultados
SELECT
    r.rec_id,
    r.rec_nombre,
    COUNT(DISTINCT rnc.nutri_id) AS nutrientes_calculados,
    SUM(CASE WHEN rnc.nutri_id = 1 THEN rnc.rnc_cantidad_total ELSE 0 END) AS calorias_totales
FROM recetas r
LEFT JOIN recetas_nutrientes_cache rnc ON rnc.rec_id = r.rec_id
WHERE r.rec_activo = 1
GROUP BY r.rec_id, r.rec_nombre
ORDER BY r.rec_id;

SELECT 'Cache de nutrientes poblado exitosamente' AS status;

select * from recetas_nutrientes_cache;
