-- =====================================================
-- PROCEDIMIENTOS ALMACENADOS PARA MÓDULO DE NUTRICIÓN
-- CORREGIDOS CON NOMBRES DE COLUMNAS REALES DEL SCHEMA
-- =====================================================

DELIMITER $$

-- =====================================================
-- NUTRIENTES - CRUD
-- Tabla: nutrientes (nutri_id, nutri_codigo, nutri_nombre, nutri_unidad)
-- =====================================================

DROP PROCEDURE IF EXISTS sp_nutrientes_listar$$
CREATE PROCEDURE sp_nutrientes_listar(
  IN p_query VARCHAR(100),
  IN p_limit INT
)
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
END$$

DROP PROCEDURE IF EXISTS sp_nutrientes_obtener$$
CREATE PROCEDURE sp_nutrientes_obtener(IN p_nutri_id SMALLINT UNSIGNED)
BEGIN
  SELECT nutri_id, nutri_codigo, nutri_nombre, nutri_unidad
  FROM nutrientes
  WHERE nutri_id = p_nutri_id;
END$$

DROP PROCEDURE IF EXISTS sp_nutrientes_crear$$
CREATE PROCEDURE sp_nutrientes_crear(
  IN p_nutri_codigo VARCHAR(32),
  IN p_nutri_nombre VARCHAR(120),
  IN p_nutri_unidad VARCHAR(16)
)
BEGIN
  INSERT INTO nutrientes (nutri_codigo, nutri_nombre, nutri_unidad)
  VALUES (p_nutri_codigo, p_nutri_nombre, p_nutri_unidad);

  SELECT nutri_id, nutri_codigo, nutri_nombre, nutri_unidad
  FROM nutrientes
  WHERE nutri_id = LAST_INSERT_ID();
END$$

DROP PROCEDURE IF EXISTS sp_nutrientes_actualizar$$
CREATE PROCEDURE sp_nutrientes_actualizar(
  IN p_nutri_id SMALLINT UNSIGNED,
  IN p_nutri_codigo VARCHAR(32),
  IN p_nutri_nombre VARCHAR(120),
  IN p_nutri_unidad VARCHAR(16)
)
BEGIN
  UPDATE nutrientes
  SET nutri_codigo = p_nutri_codigo,
      nutri_nombre = p_nutri_nombre,
      nutri_unidad = p_nutri_unidad
  WHERE nutri_id = p_nutri_id;

  SELECT nutri_id, nutri_codigo, nutri_nombre, nutri_unidad
  FROM nutrientes
  WHERE nutri_id = p_nutri_id;
END$$

DROP PROCEDURE IF EXISTS sp_nutrientes_eliminar$$
CREATE PROCEDURE sp_nutrientes_eliminar(IN p_nutri_id SMALLINT UNSIGNED)
BEGIN
  DELETE FROM nutrientes WHERE nutri_id = p_nutri_id;
  SELECT ROW_COUNT() as affected_rows;
END$$

-- =====================================================
-- ALIMENTOS - CRUD
-- Tabla: alimentos (ali_id, ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad, ali_activo, creado_en, actualizado_en)
-- =====================================================

DROP PROCEDURE IF EXISTS sp_alimentos_listar$$
CREATE PROCEDURE sp_alimentos_listar(
  IN p_query VARCHAR(100),
  IN p_limit INT
)
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
END$$

DROP PROCEDURE IF EXISTS sp_alimentos_obtener$$
CREATE PROCEDURE sp_alimentos_obtener(IN p_ali_id INT UNSIGNED)
BEGIN
  SELECT ali_id, ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad,
         ali_activo, creado_en, actualizado_en
  FROM alimentos
  WHERE ali_id = p_ali_id;
END$$

DROP PROCEDURE IF EXISTS sp_alimentos_crear$$
CREATE PROCEDURE sp_alimentos_crear(
  IN p_ali_nombre VARCHAR(150),
  IN p_ali_nombre_cientifico VARCHAR(150),
  IN p_ali_grupo VARCHAR(60),
  IN p_ali_unidad VARCHAR(16)
)
BEGIN
  INSERT INTO alimentos (ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad, ali_activo)
  VALUES (p_ali_nombre, p_ali_nombre_cientifico, p_ali_grupo, p_ali_unidad, 1);

  SELECT ali_id, ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad,
         ali_activo, creado_en, actualizado_en
  FROM alimentos
  WHERE ali_id = LAST_INSERT_ID();
END$$

DROP PROCEDURE IF EXISTS sp_alimentos_actualizar$$
CREATE PROCEDURE sp_alimentos_actualizar(
  IN p_ali_id INT UNSIGNED,
  IN p_ali_nombre VARCHAR(150),
  IN p_ali_nombre_cientifico VARCHAR(150),
  IN p_ali_grupo VARCHAR(60),
  IN p_ali_unidad VARCHAR(16),
  IN p_ali_activo TINYINT(1)
)
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
END$$

DROP PROCEDURE IF EXISTS sp_alimentos_eliminar$$
CREATE PROCEDURE sp_alimentos_eliminar(IN p_ali_id INT UNSIGNED)
BEGIN
  -- Soft delete: marcar como inactivo
  UPDATE alimentos SET ali_activo = 0 WHERE ali_id = p_ali_id;
  SELECT ROW_COUNT() as affected_rows;
END$$

DROP PROCEDURE IF EXISTS sp_alimentos_con_nutrientes_obtener$$
CREATE PROCEDURE sp_alimentos_con_nutrientes_obtener(IN p_ali_id INT UNSIGNED)
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
END$$

-- =====================================================
-- ALIMENTOS_NUTRIENTES - Relación
-- Tabla: alimentos_nutrientes (ali_id, nutri_id, an_cantidad_100, an_fuente)
-- =====================================================

DROP PROCEDURE IF EXISTS sp_alimentos_nutrientes_crear$$
CREATE PROCEDURE sp_alimentos_nutrientes_crear(
  IN p_ali_id INT UNSIGNED,
  IN p_nutri_id SMALLINT UNSIGNED,
  IN p_an_cantidad_100 DECIMAL(12,4),
  IN p_an_fuente VARCHAR(255)
)
BEGIN
  -- Insertar o actualizar si ya existe (UPSERT)
  INSERT INTO alimentos_nutrientes (ali_id, nutri_id, an_cantidad_100, an_fuente)
  VALUES (p_ali_id, p_nutri_id, p_an_cantidad_100, p_an_fuente)
  ON DUPLICATE KEY UPDATE
    an_cantidad_100 = VALUES(an_cantidad_100),
    an_fuente = VALUES(an_fuente);

  SELECT an.ali_id, an.nutri_id, an.an_cantidad_100, an.an_fuente,
         n.nutri_codigo, n.nutri_nombre, n.nutri_unidad
  FROM alimentos_nutrientes an
  JOIN nutrientes n ON an.nutri_id = n.nutri_id
  WHERE an.ali_id = p_ali_id AND an.nutri_id = p_nutri_id;
END$$

DROP PROCEDURE IF EXISTS sp_alimentos_nutrientes_actualizar$$
CREATE PROCEDURE sp_alimentos_nutrientes_actualizar(
  IN p_ali_id INT UNSIGNED,
  IN p_nutri_id SMALLINT UNSIGNED,
  IN p_an_cantidad_100 DECIMAL(12,4),
  IN p_an_fuente VARCHAR(255)
)
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
END$$

DROP PROCEDURE IF EXISTS sp_alimentos_nutrientes_eliminar$$
CREATE PROCEDURE sp_alimentos_nutrientes_eliminar(
  IN p_ali_id INT UNSIGNED,
  IN p_nutri_id SMALLINT UNSIGNED
)
BEGIN
  DELETE FROM alimentos_nutrientes
  WHERE ali_id = p_ali_id AND nutri_id = p_nutri_id;
  SELECT ROW_COUNT() as affected_rows;
END$$

-- =====================================================
-- RECETAS - CRUD
-- Tabla: recetas (rec_id, rec_nombre, rec_instrucciones, rec_activo, creado_en, actualizado_en)
-- =====================================================

DROP PROCEDURE IF EXISTS sp_recetas_listar$$
CREATE PROCEDURE sp_recetas_listar(
  IN p_query VARCHAR(100),
  IN p_limit INT
)
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
END$$

DROP PROCEDURE IF EXISTS sp_recetas_obtener$$
CREATE PROCEDURE sp_recetas_obtener(IN p_rec_id INT UNSIGNED)
BEGIN
  SELECT rec_id, rec_nombre, rec_instrucciones, rec_activo,
         creado_en, actualizado_en
  FROM recetas
  WHERE rec_id = p_rec_id;
END$$

DROP PROCEDURE IF EXISTS sp_recetas_crear$$
CREATE PROCEDURE sp_recetas_crear(
  IN p_rec_nombre VARCHAR(150),
  IN p_rec_instrucciones TEXT
)
BEGIN
  INSERT INTO recetas (rec_nombre, rec_instrucciones, rec_activo)
  VALUES (p_rec_nombre, p_rec_instrucciones, 1);

  SELECT rec_id, rec_nombre, rec_instrucciones, rec_activo,
         creado_en, actualizado_en
  FROM recetas
  WHERE rec_id = LAST_INSERT_ID();
END$$

DROP PROCEDURE IF EXISTS sp_recetas_actualizar$$
CREATE PROCEDURE sp_recetas_actualizar(
  IN p_rec_id INT UNSIGNED,
  IN p_rec_nombre VARCHAR(150),
  IN p_rec_instrucciones TEXT,
  IN p_rec_activo TINYINT(1)
)
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
END$$

DROP PROCEDURE IF EXISTS sp_recetas_eliminar$$
CREATE PROCEDURE sp_recetas_eliminar(IN p_rec_id INT UNSIGNED)
BEGIN
  -- Soft delete: marcar como inactivo
  UPDATE recetas SET rec_activo = 0 WHERE rec_id = p_rec_id;
  SELECT ROW_COUNT() as affected_rows;
END$$

DROP PROCEDURE IF EXISTS sp_recetas_completa_obtener$$
CREATE PROCEDURE sp_recetas_completa_obtener(IN p_rec_id INT UNSIGNED)
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
END$$

-- =====================================================
-- RECETAS_INGREDIENTES - Relación
-- Tabla: recetas_ingredientes (rec_id, ali_id, ri_cantidad, ri_unidad)
-- =====================================================

DROP PROCEDURE IF EXISTS sp_recetas_ingredientes_crear$$
CREATE PROCEDURE sp_recetas_ingredientes_crear(
  IN p_rec_id INT UNSIGNED,
  IN p_ali_id INT UNSIGNED,
  IN p_ri_cantidad DECIMAL(12,4),
  IN p_ri_unidad VARCHAR(16)
)
BEGIN
  -- Insertar o actualizar si ya existe (UPSERT)
  INSERT INTO recetas_ingredientes (rec_id, ali_id, ri_cantidad, ri_unidad)
  VALUES (p_rec_id, p_ali_id, p_ri_cantidad, p_ri_unidad)
  ON DUPLICATE KEY UPDATE
    ri_cantidad = VALUES(ri_cantidad),
    ri_unidad = VALUES(ri_unidad);

  SELECT ri.rec_id, ri.ali_id, ri.ri_cantidad, ri.ri_unidad,
         a.ali_nombre, a.ali_grupo
  FROM recetas_ingredientes ri
  JOIN alimentos a ON ri.ali_id = a.ali_id
  WHERE ri.rec_id = p_rec_id AND ri.ali_id = p_ali_id;
END$$

DROP PROCEDURE IF EXISTS sp_recetas_ingredientes_actualizar$$
CREATE PROCEDURE sp_recetas_ingredientes_actualizar(
  IN p_rec_id INT UNSIGNED,
  IN p_ali_id INT UNSIGNED,
  IN p_ri_cantidad DECIMAL(12,4),
  IN p_ri_unidad VARCHAR(16)
)
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
END$$

DROP PROCEDURE IF EXISTS sp_recetas_ingredientes_eliminar$$
CREATE PROCEDURE sp_recetas_ingredientes_eliminar(
  IN p_rec_id INT UNSIGNED,
  IN p_ali_id INT UNSIGNED
)
BEGIN
  DELETE FROM recetas_ingredientes
  WHERE rec_id = p_rec_id AND ali_id = p_ali_id;
  SELECT ROW_COUNT() as affected_rows;
END$$

-- =====================================================
-- DISPONIBILIDAD_ALIMENTOS - CRUD
-- Tabla: disponibilidad_alimentos (dis_id, ali_id, ent_id, dis_periodo, dis_disponible, dis_precio_promedio, dis_region, creado_en, actualizado_en)
-- =====================================================

DROP PROCEDURE IF EXISTS sp_disponibilidad_listar$$
CREATE PROCEDURE sp_disponibilidad_listar(
  IN p_region VARCHAR(120),
  IN p_periodo ENUM('Q1','Q2','Q3','Q4'),
  IN p_limit INT
)
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
END$$

DROP PROCEDURE IF EXISTS sp_disponibilidad_obtener$$
CREATE PROCEDURE sp_disponibilidad_obtener(IN p_dis_id BIGINT UNSIGNED)
BEGIN
  SELECT da.dis_id, da.ali_id, da.ent_id, da.dis_periodo,
         da.dis_disponible, da.dis_precio_promedio, da.dis_region,
         da.creado_en, da.actualizado_en,
         a.ali_nombre, a.ali_grupo
  FROM disponibilidad_alimentos da
  JOIN alimentos a ON da.ali_id = a.ali_id
  WHERE da.dis_id = p_dis_id;
END$$

DROP PROCEDURE IF EXISTS sp_disponibilidad_crear$$
CREATE PROCEDURE sp_disponibilidad_crear(
  IN p_ali_id INT UNSIGNED,
  IN p_ent_id INT UNSIGNED,
  IN p_dis_periodo ENUM('Q1','Q2','Q3','Q4'),
  IN p_dis_disponible TINYINT(1),
  IN p_dis_precio_promedio DECIMAL(10,2),
  IN p_dis_region VARCHAR(120)
)
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
END$$

DROP PROCEDURE IF EXISTS sp_disponibilidad_actualizar$$
CREATE PROCEDURE sp_disponibilidad_actualizar(
  IN p_dis_id BIGINT UNSIGNED,
  IN p_dis_disponible TINYINT(1),
  IN p_dis_precio_promedio DECIMAL(10,2)
)
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
END$$

DROP PROCEDURE IF EXISTS sp_disponibilidad_eliminar$$
CREATE PROCEDURE sp_disponibilidad_eliminar(IN p_dis_id BIGINT UNSIGNED)
BEGIN
  DELETE FROM disponibilidad_alimentos WHERE dis_id = p_dis_id;
  SELECT ROW_COUNT() as affected_rows;
END$$

DELIMITER ;

-- =====================================================
-- VERIFICACIÓN DE PROCEDIMIENTOS CREADOS
-- =====================================================
-- Para verificar que todos los procedimientos se crearon correctamente:
-- SHOW PROCEDURE STATUS WHERE Db = 'nutrifam_db' AND Name LIKE 'sp_%';
