-- ============================================================================
-- TABLA: PREFERENCIAS DE COMIDAS POR NIÑO
-- Fecha: 2025-01-14
-- Descripción: Almacena las preferencias alimentarias del niño por tipo de comida
-- ============================================================================

USE nutricion;

-- ============================================================================
-- TABLA: ninos_preferencias_comidas
-- ============================================================================
-- Cada niño puede tener múltiples preferencias por tipo de comida
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
-- DATOS DE EJEMPLO
-- ============================================================================

-- Niño 1: Pedrito (5 años)
-- DESAYUNO: Avena, Huevos, Frutas
INSERT INTO ninos_preferencias_comidas (nin_id, npc_tipo_comida, npc_preferencia) VALUES
(1, 'DESAYUNO', 'Avena'),
(1, 'DESAYUNO', 'Huevos'),
(1, 'DESAYUNO', 'Frutas');

-- ALMUERZO: Arroz, Pollo, Pasta
INSERT INTO ninos_preferencias_comidas (nin_id, npc_tipo_comida, npc_preferencia) VALUES
(1, 'ALMUERZO', 'Arroz'),
(1, 'ALMUERZO', 'Pollo'),
(1, 'ALMUERZO', 'Pasta');

-- CENA: Sopa, Ensalada, Verduras cocidas
INSERT INTO ninos_preferencias_comidas (nin_id, npc_tipo_comida, npc_preferencia) VALUES
(1, 'CENA', 'Sopa'),
(1, 'CENA', 'Ensalada'),
(1, 'CENA', 'Verduras cocidas');

-- SNACKS: Frutas, Frutos secos
INSERT INTO ninos_preferencias_comidas (nin_id, npc_tipo_comida, npc_preferencia) VALUES
(1, 'SNACKS', 'Frutas'),
(1, 'SNACKS', 'Frutos secos');

-- ============================================================================
-- PROCEDIMIENTO: Obtener preferencias de un niño por tipo de comida
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
-- PROCEDIMIENTO: Guardar preferencias de un niño (reemplaza las existentes)
-- ============================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_guardar_preferencias_nino$$

CREATE PROCEDURE sp_guardar_preferencias_nino(
  IN p_nin_id BIGINT UNSIGNED,
  IN p_tipo_comida ENUM('DESAYUNO','ALMUERZO','CENA','SNACKS'),
  IN p_preferencias JSON -- Array de strings: ["Avena", "Huevos", "Frutas"]
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
-- VISTA: Resumen de preferencias por niño
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
-- TESTS
-- ============================================================================

-- Test 1: Obtener preferencias de desayuno
CALL sp_obtener_preferencias_nino(1, 'DESAYUNO');

-- Test 2: Guardar nuevas preferencias
CALL sp_guardar_preferencias_nino(1, 'DESAYUNO', '["Avena", "Pan tostado", "Yogurt"]');

-- Test 3: Ver resumen
SELECT * FROM v_preferencias_ninos WHERE nin_id = 1;

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

SELECT 'Tabla de preferencias creada exitosamente' AS status;
SELECT COUNT(*) AS total_preferencias FROM ninos_preferencias_comidas;
