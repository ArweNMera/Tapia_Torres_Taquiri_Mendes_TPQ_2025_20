-- ============================================================================
-- MIGRACIÓN: Tablas de Alergias y Comidas Favoritas
-- ============================================================================
USE nutricion;

-- ============================================================================
-- TABLA: ninos_alergias
-- Almacena las alergias alimentarias de cada niño
-- ============================================================================
CREATE TABLE IF NOT EXISTS ninos_alergias (
  nal_id         BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id         BIGINT UNSIGNED NOT NULL,
  nal_alergeno   VARCHAR(150) NOT NULL COMMENT 'Nombre del alérgeno (ej: maní, leche, huevo)',
  nal_severidad  ENUM('LEVE', 'MODERADA', 'SEVERA') NOT NULL DEFAULT 'MODERADA',
  nal_notas      TEXT NULL COMMENT 'Notas adicionales sobre la alergia',
  creado_en      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_nal_nino
    FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,

  INDEX idx_nal_nino (nin_id),
  INDEX idx_nal_severidad (nal_severidad)
) ENGINE=InnoDB COMMENT='Alergias alimentarias de los niños';

-- ============================================================================
-- TABLA: ninos_comidas_favoritas
-- Almacena las comidas favoritas de cada niño (referencia a recetas)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ninos_comidas_favoritas (
  ncf_id         BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id         BIGINT UNSIGNED NOT NULL,
  rec_id         INT UNSIGNED NOT NULL,
  ncf_notas      VARCHAR(255) NULL COMMENT 'Notas sobre por qué le gusta',
  creado_en      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_ncf_nino
    FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_ncf_receta
    FOREIGN KEY (rec_id) REFERENCES recetas(rec_id) ON DELETE CASCADE,

  UNIQUE KEY uk_ncf_nino_receta (nin_id, rec_id),
  INDEX idx_ncf_nino (nin_id),
  INDEX idx_ncf_receta (rec_id)
) ENGINE=InnoDB COMMENT='Comidas favoritas de los niños';

-- ============================================================================
-- PROCEDIMIENTOS ALMACENADOS
-- ============================================================================

-- Obtener alergias de un niño
DELIMITER $$
DROP PROCEDURE IF EXISTS sp_obtener_alergias_nino$$
CREATE PROCEDURE sp_obtener_alergias_nino(
  IN p_nin_id BIGINT UNSIGNED
)
BEGIN
  SELECT
    nal_id,
    nin_id,
    nal_alergeno,
    nal_severidad,
    nal_notas,
    creado_en,
    actualizado_en
  FROM ninos_alergias
  WHERE nin_id = p_nin_id
  ORDER BY nal_severidad DESC, nal_alergeno ASC;
END$$

-- Agregar alergia
DROP PROCEDURE IF EXISTS sp_agregar_alergia$$
CREATE PROCEDURE sp_agregar_alergia(
  IN p_nin_id BIGINT UNSIGNED,
  IN p_alergeno VARCHAR(150),
  IN p_severidad ENUM('LEVE', 'MODERADA', 'SEVERA'),
  IN p_notas TEXT
)
BEGIN
  INSERT INTO ninos_alergias (nin_id, nal_alergeno, nal_severidad, nal_notas)
  VALUES (p_nin_id, p_alergeno, p_severidad, p_notas);

  SELECT LAST_INSERT_ID() AS nal_id;
END$$

-- Eliminar alergia
DROP PROCEDURE IF EXISTS sp_eliminar_alergia$$
CREATE PROCEDURE sp_eliminar_alergia(
  IN p_nal_id BIGINT UNSIGNED
)
BEGIN
  DELETE FROM ninos_alergias WHERE nal_id = p_nal_id;
  SELECT ROW_COUNT() AS filas_afectadas;
END$$

-- Obtener comidas favoritas de un niño
DROP PROCEDURE IF EXISTS sp_obtener_favoritas_nino$$
CREATE PROCEDURE sp_obtener_favoritas_nino(
  IN p_nin_id BIGINT UNSIGNED
)
BEGIN
  SELECT
    ncf.ncf_id,
    ncf.nin_id,
    ncf.rec_id,
    r.rec_nombre,
    r.rec_tipo_comida,
    ncf.ncf_notas,
    ncf.creado_en,
    ncf.actualizado_en
  FROM ninos_comidas_favoritas ncf
  INNER JOIN recetas r ON ncf.rec_id = r.rec_id
  WHERE ncf.nin_id = p_nin_id
  ORDER BY ncf.creado_en DESC;
END$$

-- Agregar comida favorita
DROP PROCEDURE IF EXISTS sp_agregar_favorita$$
CREATE PROCEDURE sp_agregar_favorita(
  IN p_nin_id BIGINT UNSIGNED,
  IN p_rec_id INT UNSIGNED,
  IN p_notas VARCHAR(255)
)
BEGIN
  INSERT INTO ninos_comidas_favoritas (nin_id, rec_id, ncf_notas)
  VALUES (p_nin_id, p_rec_id, p_notas)
  ON DUPLICATE KEY UPDATE
    ncf_notas = VALUES(ncf_notas),
    actualizado_en = CURRENT_TIMESTAMP;

  SELECT LAST_INSERT_ID() AS ncf_id;
END$$

-- Eliminar comida favorita
DROP PROCEDURE IF EXISTS sp_eliminar_favorita$$
CREATE PROCEDURE sp_eliminar_favorita(
  IN p_ncf_id BIGINT UNSIGNED
)
BEGIN
  DELETE FROM ninos_comidas_favoritas WHERE ncf_id = p_ncf_id;
  SELECT ROW_COUNT() AS filas_afectadas;
END$$

-- Buscar recetas por nombre (para el buscador)
DROP PROCEDURE IF EXISTS sp_buscar_recetas$$
CREATE PROCEDURE sp_buscar_recetas(
  IN p_query VARCHAR(255),
  IN p_limit INT
)
BEGIN
  SELECT
    rec_id,
    rec_nombre,
    rec_tipo_comida,
    rec_kcal,
    rec_tiempo_prep_min
  FROM recetas
  WHERE rec_activo = 1
    AND (
      rec_nombre LIKE CONCAT('%', p_query, '%')
      OR rec_descripcion LIKE CONCAT('%', p_query, '%')
    )
  ORDER BY rec_nombre ASC
  LIMIT p_limit;
END$$

DELIMITER ;

-- ============================================================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ============================================================================

-- Puedes descomentar esto para agregar datos de prueba
/*
INSERT INTO ninos_alergias (nin_id, nal_alergeno, nal_severidad, nal_notas)
VALUES
  (1, 'Maní', 'SEVERA', 'Reacción anafiláctica'),
  (1, 'Leche', 'MODERADA', 'Intolerancia a la lactosa'),
  (2, 'Huevo', 'LEVE', 'Leve irritación cutánea');

INSERT INTO ninos_comidas_favoritas (nin_id, rec_id, ncf_notas)
VALUES
  (1, 1, 'Le encanta el desayuno'),
  (1, 5, 'Siempre pide esta comida'),
  (2, 3, 'Su favorita absoluta');
*/

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================
SELECT 'Tablas creadas exitosamente' AS status;
SELECT COUNT(*) AS total_alergias FROM ninos_alergias;
SELECT COUNT(*) AS total_favoritas FROM ninos_comidas_favoritas;
