-- ============================================================================
-- Actualización de Procedimiento Almacenado para 7 Categorías OMS
-- ============================================================================
-- Este script actualiza sp_evaluar_estado_nutricional para usar las 7 categorías
-- en lugar de las 4 categorías antiguas (NORMAL, RIESGO, MODERADO, SEVERO)
-- ============================================================================

USE nutricion;

DROP PROCEDURE IF EXISTS sp_evaluar_estado_nutricional;

DELIMITER $$

CREATE PROCEDURE sp_evaluar_estado_nutricional(
    IN p_nin_id INT
)
BEGIN
    DECLARE v_ant_id INT;
    DECLARE v_peso_kg DECIMAL(5,2);
    DECLARE v_talla_cm DECIMAL(5,2);
    DECLARE v_edad_meses INT;
    DECLARE v_imc DECIMAL(5,2);
    DECLARE v_z_score DECIMAL(5,2);
    DECLARE v_percentil DECIMAL(5,2);
    DECLARE v_clasificacion VARCHAR(50);
    DECLARE v_nivel_riesgo VARCHAR(20);
    
    -- Obtener última antropometría
    SELECT 
        a.ant_id,
        a.ant_peso_kg,
        a.ant_talla_cm,
        TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as edad_meses,
        a.ant_z_imc
    INTO 
        v_ant_id,
        v_peso_kg,
        v_talla_cm,
        v_edad_meses,
        v_z_score
    FROM antropometrias a
    JOIN ninos n ON a.nin_id = n.nin_id
    WHERE a.nin_id = p_nin_id
    ORDER BY a.ant_fecha DESC, a.creado_en DESC
    LIMIT 1;
    
    -- Si no hay antropometría, retornar NULL
    IF v_ant_id IS NULL THEN
        SELECT NULL as en_id, NULL as nin_id, NULL as ant_id, NULL as en_edad_meses,
               NULL as imc_calculado, NULL as en_z_score_imc, NULL as percentil_calculado,
               NULL as en_clasificacion, NULL as en_nivel_riesgo, NULL as oms_usado, NULL as evaluado_en;
    ELSE
    
    -- Calcular IMC
    SET v_imc = v_peso_kg / POW(v_talla_cm / 100, 2);
    
    -- Si no hay z-score, usar el IMC para estimarlo (simplificado)
    IF v_z_score IS NULL THEN
        -- Estimación simple basada en IMC (no es preciso, solo fallback)
        SET v_z_score = (v_imc - 16) / 2;  -- Aproximación muy simple
    END IF;
    
    -- Calcular percentil aproximado desde z-score
    -- Aproximación: percentil ≈ 50 + (z_score * 15)
    SET v_percentil = 50 + (v_z_score * 15);
    IF v_percentil < 0.1 THEN SET v_percentil = 0.1; END IF;
    IF v_percentil > 99.9 THEN SET v_percentil = 99.9; END IF;
    
    -- Clasificar según 7 categorías OMS
    IF v_z_score < -3.0 THEN
        SET v_clasificacion = 'DESNUTRICION_SEVERA';
        SET v_nivel_riesgo = 'ALTO';
    ELSEIF v_z_score >= -3.0 AND v_z_score < -2.0 THEN
        SET v_clasificacion = 'DESNUTRICION_MODERADA';
        SET v_nivel_riesgo = 'MEDIO';
    ELSEIF v_z_score >= -2.0 AND v_z_score < -1.0 THEN
        SET v_clasificacion = 'RIESGO_DESNUTRICION';
        SET v_nivel_riesgo = 'MEDIO';
    ELSEIF v_z_score >= -1.0 AND v_z_score <= 1.0 THEN
        SET v_clasificacion = 'NORMAL';
        SET v_nivel_riesgo = 'BAJO';
    ELSEIF v_z_score > 1.0 AND v_z_score <= 2.0 THEN
        SET v_clasificacion = 'RIESGO_SOBREPESO';
        SET v_nivel_riesgo = 'MEDIO';
    ELSEIF v_z_score > 2.0 AND v_z_score <= 3.0 THEN
        SET v_clasificacion = 'SOBREPESO';
        SET v_nivel_riesgo = 'MEDIO';
    ELSE  -- v_z_score > 3.0
        SET v_clasificacion = 'OBESIDAD';
        SET v_nivel_riesgo = 'ALTO';
    END IF;
    
        -- Retornar resultado
        SELECT 
            NULL as en_id,
            p_nin_id as nin_id,
            v_ant_id as ant_id,
            v_edad_meses as en_edad_meses,
            v_imc as imc_calculado,
            v_z_score as en_z_score_imc,
            v_percentil as percentil_calculado,
            v_clasificacion as en_clasificacion,
            v_nivel_riesgo as en_nivel_riesgo,
            TRUE as oms_usado,
            NOW() as evaluado_en;
    END IF;
        
END$$

DELIMITER ;

-- ============================================================================
-- Verificación
-- ============================================================================
SELECT '✅ Procedimiento sp_evaluar_estado_nutricional actualizado con 7 categorías OMS' as status;

-- Probar con un niño de ejemplo (ajustar el ID según tu BD)
-- CALL sp_evaluar_estado_nutricional(69);
