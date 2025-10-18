-- Procedimiento para calcular el perfil nutricional de un niño
-- Basado en su última antropometría y clasificación nutricional
-- IMPORTANTE: Primero eliminar el trigger con: DROP TRIGGER IF EXISTS trg_pnn_vigente_unico;

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

END$$

DELIMITER ;
