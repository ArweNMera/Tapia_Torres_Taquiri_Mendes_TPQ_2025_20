-- ============================================================================
-- PROCEDIMIENTOS ALMACENADOS PMV3: SEGUIMIENTO Y MONITOREO NUTRICIONAL
-- ============================================================================
-- Fecha de Creación: 2025-01-XX
-- Versión: 1.0
-- Descripción: Procedimientos almacenados para el sistema de seguimiento
--              y monitoreo nutricional continuo (PMV3)
-- ============================================================================

DELIMITER $$

-- ============================================================================
-- SECCIÓN 1: PROCEDIMIENTOS DE ADHERENCIA
-- ============================================================================

-- ----------------------------------------------------------------------------
-- sp_registrar_adherencia
-- ----------------------------------------------------------------------------
-- Descripción: Registra o actualiza la adherencia diaria al plan nutricional
-- Parámetros:
--   p_nin_id: ID del niño
--   p_men_id: ID del menú
--   p_mei_id: ID del ítem del menú (opcional)
--   p_fecha: Fecha del registro
--   p_estado: Estado (OK, PARCIAL, NO)
--   p_porcentaje: Porcentaje de cumplimiento (0-100)
--   p_dificultad: Nivel de dificultad (NINGUNA, BAJA, MEDIA, ALTA)
--   p_comentario: Comentario del tutor
-- Retorna: Registro de adherencia creado/actualizado
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_registrar_adherencia$$
CREATE PROCEDURE sp_registrar_adherencia(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_men_id BIGINT UNSIGNED,
    IN p_mei_id BIGINT UNSIGNED,
    IN p_fecha DATE,
    IN p_estado ENUM('OK','PARCIAL','NO'),
    IN p_porcentaje DECIMAL(5,2),
    IN p_dificultad ENUM('NINGUNA','BAJA','MEDIA','ALTA'),
    IN p_comentario TEXT
)
BEGIN
    DECLARE v_adh_id BIGINT UNSIGNED;
    DECLARE v_error_msg VARCHAR(255);

    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Validar que el menú existe
    IF NOT EXISTS (SELECT 1 FROM menus WHERE men_id = p_men_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El menú especificado no existe';
    END IF;

    -- Validar que la fecha no sea futura
    IF p_fecha > CURDATE() THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se puede registrar adherencia para fechas futuras';
    END IF;

    -- Validar porcentaje
    IF p_porcentaje < 0 OR p_porcentaje > 100 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El porcentaje debe estar entre 0 y 100';
    END IF;

    -- Insertar o actualizar adherencia
    INSERT INTO adherencias (
        nin_id,
        men_id,
        mei_id,
        adh_registrado_en,
        adh_estado,
        adh_porcentaje,
        adh_dificultad,
        adh_comentario_tutor
    ) VALUES (
        p_nin_id,
        p_men_id,
        p_mei_id,
        p_fecha,
        p_estado,
        p_porcentaje,
        p_dificultad,
        p_comentario
    )
    ON DUPLICATE KEY UPDATE
        adh_estado = p_estado,
        adh_porcentaje = p_porcentaje,
        adh_dificultad = p_dificultad,
        adh_comentario_tutor = p_comentario;

    SET v_adh_id = LAST_INSERT_ID();

    -- Retornar el registro creado/actualizado
    SELECT
        a.*,
        m.men_inicio,
        m.men_fin,
        mi.mei_comida,
        mi.mei_kcal
    FROM adherencias a
    LEFT JOIN menus m ON a.men_id = m.men_id
    LEFT JOIN menus_items mi ON a.mei_id = mi.mei_id
    WHERE a.adh_id = v_adh_id;

END$$

-- ----------------------------------------------------------------------------
-- sp_obtener_adherencia_por_nino
-- ----------------------------------------------------------------------------
-- Descripción: Obtiene el historial de adherencia de un niño
-- Parámetros:
--   p_nin_id: ID del niño
--   p_fecha_inicio: Fecha de inicio del rango (opcional)
--   p_fecha_fin: Fecha de fin del rango (opcional)
-- Retorna: Lista de registros de adherencia con estadísticas
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_obtener_adherencia_por_nino$$
CREATE PROCEDURE sp_obtener_adherencia_por_nino(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE
)
BEGIN
    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Si no se especifican fechas, usar últimos 30 días
    IF p_fecha_inicio IS NULL THEN
        SET p_fecha_inicio = DATE_SUB(CURDATE(), INTERVAL 30 DAY);
    END IF;

    IF p_fecha_fin IS NULL THEN
        SET p_fecha_fin = CURDATE();
    END IF;

    -- Retornar registros de adherencia
    SELECT
        a.adh_id,
        a.nin_id,
        a.men_id,
        a.mei_id,
        a.adh_registrado_en AS fecha,
        a.adh_estado AS estado,
        a.adh_porcentaje AS porcentaje,
        a.adh_dificultad AS dificultad,
        a.adh_comentario_tutor AS comentario,
        m.men_inicio,
        m.men_fin,
        mi.mei_comida,
        mi.mei_kcal,
        -- Estadísticas agregadas
        (SELECT AVG(adh_porcentaje)
         FROM adherencias
         WHERE nin_id = p_nin_id
           AND adh_registrado_en BETWEEN p_fecha_inicio AND p_fecha_fin
        ) AS adherencia_promedio,
        (SELECT COUNT(*)
         FROM adherencias
         WHERE nin_id = p_nin_id
           AND adh_registrado_en BETWEEN p_fecha_inicio AND p_fecha_fin
           AND adh_dificultad = 'ALTA'
        ) AS dias_dificultad_alta
    FROM adherencias a
    LEFT JOIN menus m ON a.men_id = m.men_id
    LEFT JOIN menus_items mi ON a.mei_id = mi.mei_id
    WHERE a.nin_id = p_nin_id
      AND a.adh_registrado_en BETWEEN p_fecha_inicio AND p_fecha_fin
    ORDER BY a.adh_registrado_en DESC;

END$$

-- ----------------------------------------------------------------------------
-- sp_calcular_adherencia_promedio
-- ----------------------------------------------------------------------------
-- Descripción: Calcula el score de adherencia promedio de los últimos N días
-- Parámetros:
--   p_nin_id: ID del niño
--   p_dias: Número de días a considerar (default: 30)
-- Retorna: Score de adherencia (0-100) y consistencia
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_calcular_adherencia_promedio$$
CREATE PROCEDURE sp_calcular_adherencia_promedio(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_dias INT
)
BEGIN
    DECLARE v_adherencia_promedio DECIMAL(5,2);
    DECLARE v_consistencia DECIMAL(5,2);
    DECLARE v_total_registros INT;

    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Default a 30 días si no se especifica
    IF p_dias IS NULL OR p_dias <= 0 THEN
        SET p_dias = 30;
    END IF;

    -- Calcular adherencia promedio
    SELECT
        AVG(adh_porcentaje),
        STDDEV(adh_porcentaje),
        COUNT(*)
    INTO
        v_adherencia_promedio,
        v_consistencia,
        v_total_registros
    FROM adherencias
    WHERE nin_id = p_nin_id
      AND adh_registrado_en >= DATE_SUB(CURDATE(), INTERVAL p_dias DAY);

    -- Si no hay registros, retornar NULL
    IF v_total_registros = 0 THEN
        SELECT
            NULL AS adherencia_promedio,
            NULL AS consistencia,
            0 AS total_registros,
            p_dias AS dias_analizados;
    ELSE
        -- Calcular consistencia (inverso de desviación estándar normalizada)
        SET v_consistencia = 100 - LEAST(v_consistencia, 100);

        SELECT
            ROUND(v_adherencia_promedio, 2) AS adherencia_promedio,
            ROUND(v_consistencia, 2) AS consistencia,
            v_total_registros AS total_registros,
            p_dias AS dias_analizados;
    END IF;

END$$

-- ============================================================================
-- SECCIÓN 2: PROCEDIMIENTOS DE SÍNTOMAS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- sp_registrar_sintoma
-- ----------------------------------------------------------------------------
-- Descripción: Registra un síntoma experimentado por el niño
-- Parámetros:
--   p_nin_id: ID del niño
--   p_fecha: Fecha del síntoma
--   p_tipo: Tipo de síntoma
--   p_severidad: Severidad (LEVE, MODERADO, SEVERO)
--   p_duracion_dias: Duración en días
--   p_relacionado_menu: Si está relacionado con el menú
--   p_notas: Notas adicionales
-- Retorna: Registro del síntoma creado
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_registrar_sintoma$$
CREATE PROCEDURE sp_registrar_sintoma(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_fecha DATE,
    IN p_tipo VARCHAR(120),
    IN p_severidad ENUM('LEVE','MODERADO','SEVERO'),
    IN p_duracion_dias SMALLINT UNSIGNED,
    IN p_relacionado_menu BOOLEAN,
    IN p_notas TEXT
)
BEGIN
    DECLARE v_sin_id BIGINT UNSIGNED;
    DECLARE v_sintomas_recientes INT;
    DECLARE v_grado TINYINT;

    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Convertir severidad a grado numérico
    SET v_grado = CASE p_severidad
        WHEN 'LEVE' THEN 1
        WHEN 'MODERADO' THEN 2
        WHEN 'SEVERO' THEN 3
        ELSE 1
    END;

    -- Insertar síntoma
    INSERT INTO sintomas (
        nin_id,
        sin_fecha,
        sin_tipo,
        sin_grado,
        sin_severidad,
        sin_duracion_dias,
        sin_relacionado_menu,
        sin_notas
    ) VALUES (
        p_nin_id,
        p_fecha,
        p_tipo,
        v_grado,
        p_severidad,
        p_duracion_dias,
        p_relacionado_menu,
        p_notas
    );

    SET v_sin_id = LAST_INSERT_ID();

    -- Verificar si hay síntomas frecuentes (>3 en 7 días)
    SELECT COUNT(*) INTO v_sintomas_recientes
    FROM sintomas
    WHERE nin_id = p_nin_id
      AND sin_fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);

    -- Si hay síntomas frecuentes, generar alerta
    IF v_sintomas_recientes > 3 THEN
        -- Obtener nutricionista asignado
        INSERT INTO notificaciones (usr_id, not_tipo, not_payload, not_estado)
        SELECT
            n.usr_id,
            'SINTOMAS_FRECUENTES',
            JSON_OBJECT(
                'nin_id', p_nin_id,
                'sintomas_recientes', v_sintomas_recientes,
                'ultimo_sintoma', p_tipo,
                'severidad', p_severidad
            ),
            'PENDIENTE'
        FROM vinculos_nutricionista_nino vnn
        INNER JOIN nutricionistas n ON vnn.nut_id = n.nut_id
        WHERE vnn.nin_id = p_nin_id
          AND vnn.vnn_estado = 'ACTIVO'
        LIMIT 1;
    END IF;

    -- Retornar el síntoma registrado
    SELECT * FROM sintomas WHERE sin_id = v_sin_id;

END$$

-- ----------------------------------------------------------------------------
-- sp_obtener_sintomas_por_nino
-- ----------------------------------------------------------------------------
-- Descripción: Obtiene el historial de síntomas de un niño
-- Parámetros:
--   p_nin_id: ID del niño
--   p_fecha_inicio: Fecha de inicio del rango (opcional)
--   p_fecha_fin: Fecha de fin del rango (opcional)
--   p_tipo: Filtrar por tipo de síntoma (opcional)
-- Retorna: Lista de síntomas
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_obtener_sintomas_por_nino$$
CREATE PROCEDURE sp_obtener_sintomas_por_nino(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE,
    IN p_tipo VARCHAR(120)
)
BEGIN
    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Si no se especifican fechas, usar últimos 30 días
    IF p_fecha_inicio IS NULL THEN
        SET p_fecha_inicio = DATE_SUB(CURDATE(), INTERVAL 30 DAY);
    END IF;

    IF p_fecha_fin IS NULL THEN
        SET p_fecha_fin = CURDATE();
    END IF;

    -- Retornar síntomas
    SELECT
        sin_id,
        nin_id,
        sin_fecha AS fecha,
        sin_tipo AS tipo,
        sin_severidad AS severidad,
        sin_grado AS grado,
        sin_duracion_dias AS duracion_dias,
        sin_relacionado_menu AS relacionado_menu,
        sin_notas AS notas,
        creado_en
    FROM sintomas
    WHERE nin_id = p_nin_id
      AND sin_fecha BETWEEN p_fecha_inicio AND p_fecha_fin
      AND (p_tipo IS NULL OR sin_tipo = p_tipo)
    ORDER BY sin_fecha DESC;

END$$

-- ----------------------------------------------------------------------------
-- sp_calcular_frecuencia_sintomas
-- ----------------------------------------------------------------------------
-- Descripción: Calcula la frecuencia y severidad promedio de síntomas
-- Parámetros:
--   p_nin_id: ID del niño
--   p_dias: Número de días a considerar (default: 30)
-- Retorna: Frecuencia, severidad promedio y síntomas recientes
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_calcular_frecuencia_sintomas$$
CREATE PROCEDURE sp_calcular_frecuencia_sintomas(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_dias INT
)
BEGIN
    DECLARE v_frecuencia INT;
    DECLARE v_severidad_promedio DECIMAL(4,2);
    DECLARE v_sintomas_recientes INT;

    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Default a 30 días si no se especifica
    IF p_dias IS NULL OR p_dias <= 0 THEN
        SET p_dias = 30;
    END IF;

    -- Calcular frecuencia y severidad promedio
    SELECT
        COUNT(*),
        AVG(COALESCE(sin_grado, 0))
    INTO
        v_frecuencia,
        v_severidad_promedio
    FROM sintomas
    WHERE nin_id = p_nin_id
      AND sin_fecha >= DATE_SUB(CURDATE(), INTERVAL p_dias DAY);

    -- Calcular síntomas recientes (últimos 7 días)
    SELECT COUNT(*) INTO v_sintomas_recientes
    FROM sintomas
    WHERE nin_id = p_nin_id
      AND sin_fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);

    -- Retornar resultados
    SELECT
        v_frecuencia AS frecuencia_total,
        ROUND(v_severidad_promedio, 2) AS severidad_promedio,
        v_sintomas_recientes AS sintomas_recientes_7dias,
        p_dias AS dias_analizados,
        CASE
            WHEN v_sintomas_recientes > 0 THEN TRUE
            ELSE FALSE
        END AS tiene_sintomas_recientes;

END$$

-- ============================================================================
-- SECCIÓN 3: PROCEDIMIENTOS DE EVOLUCIÓN NUTRICIONAL
-- ============================================================================

-- ----------------------------------------------------------------------------
-- sp_obtener_evolucion_nutricional
-- ----------------------------------------------------------------------------
-- Descripción: Obtiene la evolución nutricional completa del niño
-- Parámetros:
--   p_nin_id: ID del niño
--   p_fecha_inicio: Fecha de inicio del rango (opcional)
--   p_fecha_fin: Fecha de fin del rango (opcional)
-- Retorna: Antropometrías con evaluaciones y adherencia
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_obtener_evolucion_nutricional$$
CREATE PROCEDURE sp_obtener_evolucion_nutricional(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_fecha_inicio DATE,
    IN p_fecha_fin DATE
)
BEGIN
    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Si no se especifican fechas, usar últimos 6 meses
    IF p_fecha_inicio IS NULL THEN
        SET p_fecha_inicio = DATE_SUB(CURDATE(), INTERVAL 6 MONTH);
    END IF;

    IF p_fecha_fin IS NULL THEN
        SET p_fecha_fin = CURDATE();
    END IF;

    -- Retornar evolución completa
    SELECT
        a.ant_id,
        a.ant_fecha AS fecha,
        a.ant_edad_meses AS edad_meses,
        a.ant_peso_kg AS peso_kg,
        a.ant_talla_cm AS talla_cm,
        a.ant_z_imc AS z_score_imc,
        a.ant_z_peso_edad AS z_score_peso,
        a.ant_z_talla_edad AS z_score_talla,
        (a.ant_peso_kg / POWER(a.ant_talla_cm/100, 2)) AS imc,
        en.en_clasificacion AS clasificacion,
        en.en_nivel_riesgo AS nivel_riesgo,
        en.en_percentil_imc AS percentil_imc,
        -- Adherencia promedio del período
        (SELECT AVG(adh_porcentaje)
         FROM adherencias
         WHERE nin_id = p_nin_id
           AND adh_registrado_en BETWEEN
               DATE_SUB(a.ant_fecha, INTERVAL 7 DAY) AND a.ant_fecha
        ) AS adherencia_7dias,
        -- Síntomas en el período
        (SELECT COUNT(*)
         FROM sintomas
         WHERE nin_id = p_nin_id
           AND sin_fecha BETWEEN
               DATE_SUB(a.ant_fecha, INTERVAL 7 DAY) AND a.ant_fecha
        ) AS sintomas_7dias
    FROM antropometrias a
    LEFT JOIN evaluaciones_nutricionales en ON a.ant_id = en.ant_id
    WHERE a.nin_id = p_nin_id
      AND a.ant_fecha BETWEEN p_fecha_inicio AND p_fecha_fin
    ORDER BY a.ant_fecha ASC;

END$$

-- ----------------------------------------------------------------------------
-- sp_calcular_tendencia_nutricional
-- ----------------------------------------------------------------------------
-- Descripción: Calcula la tendencia nutricional basada en últimas mediciones
-- Parámetros:
--   p_nin_id: ID del niño
--   p_ultimas_mediciones: Número de mediciones a analizar (default: 3)
-- Retorna: Tendencia (MEJORANDO, ESTABLE, EMPEORANDO) y velocidades
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_calcular_tendencia_nutricional$$
CREATE PROCEDURE sp_calcular_tendencia_nutricional(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_ultimas_mediciones INT
)
BEGIN
    DECLARE v_tendencia VARCHAR(20);
    DECLARE v_bmi_velocity DECIMAL(6,3);
    DECLARE v_weight_velocity DECIMAL(6,3);
    DECLARE v_height_velocity DECIMAL(6,3);
    DECLARE v_z_score_trend DECIMAL(6,3);
    DECLARE v_mediciones_count INT;

    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Default a 3 mediciones si no se especifica
    IF p_ultimas_mediciones IS NULL OR p_ultimas_mediciones <= 0 THEN
        SET p_ultimas_mediciones = 3;
    END IF;

    -- Contar mediciones disponibles
    SELECT COUNT(*) INTO v_mediciones_count
    FROM antropometrias
    WHERE nin_id = p_nin_id;

    -- Si no hay suficientes mediciones, retornar NULL
    IF v_mediciones_count < 2 THEN
        SELECT
            'INSUFICIENTES_DATOS' AS tendencia,
            NULL AS bmi_velocity,
            NULL AS weight_velocity,
            NULL AS height_velocity,
            NULL AS z_score_trend,
            v_mediciones_count AS mediciones_disponibles;
    ELSE
        -- Calcular velocidades usando las últimas mediciones
        WITH ultimas_mediciones AS (
            SELECT
                ant_id,
                ant_fecha,
                ant_peso_kg,
                ant_talla_cm,
                ant_z_imc,
                (ant_peso_kg / POWER(ant_talla_cm/100, 2)) AS imc,
                ROW_NUMBER() OVER (ORDER BY ant_fecha DESC) AS rn
            FROM antropometrias
            WHERE nin_id = p_nin_id
            ORDER BY ant_fecha DESC
            LIMIT p_ultimas_mediciones
        ),
        primera_medicion AS (
            SELECT * FROM ultimas_mediciones WHERE rn = p_ultimas_mediciones
        ),
        ultima_medicion AS (
            SELECT * FROM ultimas_mediciones WHERE rn = 1
        )
        SELECT
            -- Velocidad de IMC (cambio por mes)
            (u.imc - p.imc) / GREATEST(DATEDIFF(u.ant_fecha, p.ant_fecha) / 30, 1),
            -- Velocidad de peso (kg por mes)
            (u.ant_peso_kg - p.ant_peso_kg) / GREATEST(DATEDIFF(u.ant_fecha, p.ant_fecha) / 30, 1),
            -- Velocidad de talla (cm por mes)
            (u.ant_talla_cm - p.ant_talla_cm) / GREATEST(DATEDIFF(u.ant_fecha, p.ant_fecha) / 30, 1),
            -- Tendencia de z-score
            (u.ant_z_imc - p.ant_z_imc) / GREATEST(DATEDIFF(u.ant_fecha, p.ant_fecha) / 30, 1)
        INTO
            v_bmi_velocity,
            v_weight_velocity,
            v_height_velocity,
            v_z_score_trend
        FROM ultima_medicion u, primera_medicion p;

        -- Determinar tendencia basada en z-score
        SET v_tendencia = CASE
            WHEN v_z_score_trend > 0.1 THEN 'MEJORANDO'
            WHEN v_z_score_trend < -0.1 THEN 'EMPEORANDO'
            ELSE 'ESTABLE'
        END;

        -- Retornar resultados
        SELECT
            v_tendencia AS tendencia,
            ROUND(v_bmi_velocity, 3) AS bmi_velocity,
            ROUND(v_weight_velocity, 3) AS weight_velocity,
            ROUND(v_height_velocity, 3) AS height_velocity,
            ROUND(v_z_score_trend, 3) AS z_score_trend,
            v_mediciones_count AS mediciones_disponibles,
            p_ultimas_mediciones AS mediciones_analizadas;
    END IF;

END$$

-- ============================================================================
-- SECCIÓN 4: PROCEDIMIENTOS DE PREDICCIONES ML
-- ============================================================================

-- ----------------------------------------------------------------------------
-- sp_guardar_prediccion_ml
-- ----------------------------------------------------------------------------
-- Descripción: Guarda una predicción del modelo ML
-- Parámetros:
--   p_nin_id: ID del niño
--   p_ant_id: ID de la antropometría
--   p_fml_id: ID de los features ML
--   p_clasificacion: Clasificación predicha
--   p_probabilidad: Probabilidad de la clase predicha
--   p_score_riesgo: Score de riesgo (0-1)
--   p_prob_normal, p_prob_riesgo, p_prob_moderado, p_prob_severo: Probabilidades
--   p_modelo_tipo: Tipo de modelo (rf, nn, ensemble)
--   p_modelo_version: Versión del modelo
--   p_features_json: Features usados (JSON)
--   p_explicacion_json: Explicación SHAP (JSON)
-- Retorna: Registro de predicción creado
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_guardar_prediccion_ml$$
CREATE PROCEDURE sp_guardar_prediccion_ml(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_ant_id BIGINT UNSIGNED,
    IN p_fml_id BIGINT UNSIGNED,
    IN p_clasificacion ENUM('DESNUTRICION_SEVERA','DESNUTRICION_MODERADA','RIESGO_DESNUTRICION','NORMAL','RIESGO_SOBREPESO','SOBREPESO','OBESIDAD'),
    IN p_probabilidad DECIMAL(5,4),
    IN p_score_riesgo DECIMAL(6,4),
    IN p_prob_normal DECIMAL(5,4),
    IN p_prob_riesgo DECIMAL(5,4),
    IN p_prob_moderado DECIMAL(5,4),
    IN p_prob_severo DECIMAL(5,4),
    IN p_modelo_tipo VARCHAR(50),
    IN p_modelo_version VARCHAR(20),
    IN p_features_json JSON,
    IN p_explicacion_json JSON
)
BEGIN
    DECLARE v_pml_id BIGINT UNSIGNED;
    DECLARE v_generar_alerta BOOLEAN DEFAULT FALSE;

    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Insertar predicción
    INSERT INTO predicciones_ml (
        nin_id,
        ant_id,
        fml_id,
        pml_clasificacion,
        pml_probabilidad,
        pml_score_riesgo,
        pml_prob_normal,
        pml_prob_riesgo,
        pml_prob_moderado,
        pml_prob_severo,
        pml_modelo_tipo,
        pml_modelo_version,
        pml_features_json,
        pml_explicacion_json
    ) VALUES (
        p_nin_id,
        p_ant_id,
        p_fml_id,
        p_clasificacion,
        p_probabilidad,
        p_score_riesgo,
        p_prob_normal,
        p_prob_riesgo,
        p_prob_moderado,
        p_prob_severo,
        p_modelo_tipo,
        p_modelo_version,
        p_features_json,
        p_explicacion_json
    );

    SET v_pml_id = LAST_INSERT_ID();

    -- Generar alerta si es riesgo MODERADO o SEVERO
    IF p_clasificacion IN ('DESNUTRICION_SEVERA', 'DESNUTRICION_MODERADA', 'OBESIDAD') THEN
        SET v_generar_alerta = TRUE;
    END IF;

    IF v_generar_alerta THEN
        -- Obtener nutricionista asignado y generar alerta
        INSERT INTO notificaciones (usr_id, not_tipo, not_payload, not_estado)
        SELECT
            n.usr_id,
            'RIESGO_CRITICO_ML',
            JSON_OBJECT(
                'nin_id', p_nin_id,
                'pml_id', v_pml_id,
                'clasificacion', p_clasificacion,
                'probabilidad', p_probabilidad,
                'score_riesgo', p_score_riesgo
            ),
            'PENDIENTE'
        FROM vinculos_nutricionista_nino vnn
        INNER JOIN nutricionistas n ON vnn.nut_id = n.nut_id
        WHERE vnn.nin_id = p_nin_id
          AND vnn.vnn_estado = 'ACTIVO'
        LIMIT 1;
    END IF;

    -- Retornar la predicción creada
    SELECT * FROM predicciones_ml WHERE pml_id = v_pml_id;

END$$

-- ----------------------------------------------------------------------------
-- sp_validar_prediccion_ml
-- ----------------------------------------------------------------------------
-- Descripción: Valida una predicción ML por parte del nutricionista
-- Parámetros:
--   p_pml_id: ID de la predicción
--   p_usr_id_validador: ID del usuario validador
--   p_validado: Si la predicción es correcta
--   p_feedback: Comentarios del nutricionista
-- Retorna: Predicción actualizada
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_validar_prediccion_ml$$
CREATE PROCEDURE sp_validar_prediccion_ml(
    IN p_pml_id BIGINT UNSIGNED,
    IN p_usr_id_validador BIGINT UNSIGNED,
    IN p_validado BOOLEAN,
    IN p_feedback TEXT
)
BEGIN
    -- Validar que la predicción existe
    IF NOT EXISTS (SELECT 1 FROM predicciones_ml WHERE pml_id = p_pml_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'La predicción especificada no existe';
    END IF;

    -- Validar que el usuario existe
    IF NOT EXISTS (SELECT 1 FROM usuarios WHERE usr_id = p_usr_id_validador) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El usuario validador no existe';
    END IF;

    -- Actualizar predicción
    UPDATE predicciones_ml
    SET
        pml_validado = p_validado,
        pml_validado_por = p_usr_id_validador,
        pml_validado_en = CURRENT_TIMESTAMP,
        pml_feedback = p_feedback
    WHERE pml_id = p_pml_id;

    -- Retornar predicción actualizada
    SELECT
        p.*,
        u.usr_nombre AS validador_nombre,
        u.usr_apellido AS validador_apellido
    FROM predicciones_ml p
    LEFT JOIN usuarios u ON p.pml_validado_por = u.usr_id
    WHERE p.pml_id = p_pml_id;

END$$

-- ----------------------------------------------------------------------------
-- sp_obtener_predicciones_por_nino
-- ----------------------------------------------------------------------------
-- Descripción: Obtiene el historial de predicciones ML de un niño
-- Parámetros:
--   p_nin_id: ID del niño
--   p_limit: Número máximo de predicciones a retornar (default: 10)
-- Retorna: Lista de predicciones ordenadas por fecha
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_obtener_predicciones_por_nino$$
CREATE PROCEDURE sp_obtener_predicciones_por_nino(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_limit INT
)
BEGIN
    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Default a 10 si no se especifica
    IF p_limit IS NULL OR p_limit <= 0 THEN
        SET p_limit = 10;
    END IF;

    -- Retornar predicciones
    SELECT
        p.pml_id,
        p.nin_id,
        p.ant_id,
        p.fml_id,
        p.pml_clasificacion AS clasificacion,
        p.pml_probabilidad AS probabilidad,
        p.pml_score_riesgo AS score_riesgo,
        p.pml_prob_normal AS prob_normal,
        p.pml_prob_riesgo AS prob_riesgo,
        p.pml_prob_moderado AS prob_moderado,
        p.pml_prob_severo AS prob_severo,
        p.pml_modelo_tipo AS modelo_tipo,
        p.pml_modelo_version AS modelo_version,
        p.pml_validado AS validado,
        p.pml_validado_por AS validado_por,
        p.pml_validado_en AS validado_en,
        p.pml_feedback AS feedback,
        p.creado_en,
        a.ant_fecha AS fecha_antropometria,
        a.ant_peso_kg AS peso_kg,
        a.ant_talla_cm AS talla_cm,
        a.ant_z_imc AS z_score_imc,
        u.usr_nombre AS validador_nombre,
        u.usr_apellido AS validador_apellido
    FROM predicciones_ml p
    LEFT JOIN antropometrias a ON p.ant_id = a.ant_id
    LEFT JOIN usuarios u ON p.pml_validado_por = u.usr_id
    WHERE p.nin_id = p_nin_id
    ORDER BY p.creado_en DESC
    LIMIT p_limit;

END$$

-- ============================================================================
-- SECCIÓN 5: PROCEDIMIENTOS DE ALERTAS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- sp_generar_alerta
-- ----------------------------------------------------------------------------
-- Descripción: Genera una alerta/notificación para el nutricionista
-- Parámetros:
--   p_nin_id: ID del niño
--   p_tipo: Tipo de alerta
--   p_payload: Datos de la alerta (JSON)
-- Retorna: Notificación creada
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_generar_alerta$$
CREATE PROCEDURE sp_generar_alerta(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_tipo VARCHAR(60),
    IN p_payload JSON
)
BEGIN
    DECLARE v_not_id BIGINT UNSIGNED;
    DECLARE v_usr_id BIGINT UNSIGNED;

    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Obtener nutricionista asignado
    SELECT n.usr_id INTO v_usr_id
    FROM vinculos_nutricionista_nino vnn
    INNER JOIN nutricionistas n ON vnn.nut_id = n.nut_id
    WHERE vnn.nin_id = p_nin_id
      AND vnn.vnn_estado = 'ACTIVO'
    LIMIT 1;

    -- Si no hay nutricionista asignado, no generar alerta
    IF v_usr_id IS NULL THEN
        SELECT
            NULL AS not_id,
            'NO_NUTRICIONISTA_ASIGNADO' AS mensaje;
    ELSE
        -- Insertar notificación
        INSERT INTO notificaciones (
            usr_id,
            not_tipo,
            not_payload,
            not_estado
        ) VALUES (
            v_usr_id,
            p_tipo,
            p_payload,
            'PENDIENTE'
        );

        SET v_not_id = LAST_INSERT_ID();

        -- Retornar notificación creada
        SELECT * FROM notificaciones WHERE not_id = v_not_id;
    END IF;

END$$

-- ----------------------------------------------------------------------------
-- sp_verificar_alertas_automaticas
-- ----------------------------------------------------------------------------
-- Descripción: Verifica condiciones para generar alertas automáticas
-- Parámetros:
--   p_nin_id: ID del niño
-- Retorna: Lista de alertas generadas
-- ----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_verificar_alertas_automaticas$$
CREATE PROCEDURE sp_verificar_alertas_automaticas(
    IN p_nin_id BIGINT UNSIGNED
)
BEGIN
    DECLARE v_tendencia VARCHAR(20);
    DECLARE v_adherencia_promedio DECIMAL(5,2);
    DECLARE v_sintomas_frecuentes INT;
    DECLARE v_ultima_prediccion VARCHAR(50);
    DECLARE v_alertas_generadas INT DEFAULT 0;
    DECLARE v_z_score_1 DECIMAL(6,3);
    DECLARE v_z_score_2 DECIMAL(6,3);
    DECLARE v_z_score_3 DECIMAL(6,3);
    DECLARE v_mediciones_count INT;

    -- Validar que el niño existe
    IF NOT EXISTS (SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El niño especificado no existe';
    END IF;

    -- Crear tabla temporal para almacenar alertas generadas
    CREATE TEMPORARY TABLE IF NOT EXISTS temp_alertas (
        tipo VARCHAR(60),
        payload JSON,
        generada BOOLEAN DEFAULT FALSE
    );

    -- 1. Verificar tendencia negativa (últimas 3 mediciones)
    -- Obtener las últimas 3 mediciones de z-score
    SELECT COUNT(*) INTO v_mediciones_count
    FROM antropometrias
    WHERE nin_id = p_nin_id;

    IF v_mediciones_count >= 3 THEN
        -- Obtener los 3 últimos z-scores
        SELECT ant_z_imc INTO v_z_score_1
        FROM antropometrias
        WHERE nin_id = p_nin_id
        ORDER BY ant_fecha DESC
        LIMIT 1;

        SELECT ant_z_imc INTO v_z_score_2
        FROM antropometrias
        WHERE nin_id = p_nin_id
        ORDER BY ant_fecha DESC
        LIMIT 1 OFFSET 1;

        SELECT ant_z_imc INTO v_z_score_3
        FROM antropometrias
        WHERE nin_id = p_nin_id
        ORDER BY ant_fecha DESC
        LIMIT 1 OFFSET 2;

        -- Verificar si hay tendencia negativa (2 de 3 mediciones empeorando)
        IF (v_z_score_1 < v_z_score_2 AND v_z_score_2 < v_z_score_3) OR
           (v_z_score_1 < v_z_score_2 AND v_z_score_1 < v_z_score_3) THEN
            SET v_tendencia = 'EMPEORANDO';
        ELSE
            SET v_tendencia = 'ESTABLE';
        END IF;

        IF v_tendencia = 'EMPEORANDO' THEN
            INSERT INTO temp_alertas (tipo, payload)
            VALUES (
                'TENDENCIA_NEGATIVA',
                JSON_OBJECT('nin_id', p_nin_id, 'descripcion', 'Tendencia negativa detectada en últimas 3 mediciones')
            );
            SET v_alertas_generadas = v_alertas_generadas + 1;
        END IF;
    END IF;

    -- 2. Verificar baja adherencia (<60% en 2 semanas)
    SELECT AVG(adh_porcentaje) INTO v_adherencia_promedio
    FROM adherencias
    WHERE nin_id = p_nin_id
      AND adh_registrado_en >= DATE_SUB(CURDATE(), INTERVAL 14 DAY);

    IF v_adherencia_promedio IS NOT NULL AND v_adherencia_promedio < 60 THEN
        INSERT INTO temp_alertas (tipo, payload)
        VALUES (
            'BAJA_ADHERENCIA',
            JSON_OBJECT('nin_id', p_nin_id, 'adherencia_promedio', v_adherencia_promedio)
        );
        SET v_alertas_generadas = v_alertas_generadas + 1;
    END IF;

    -- 3. Verificar síntomas frecuentes (>5 en 7 días)
    SELECT COUNT(*) INTO v_sintomas_frecuentes
    FROM sintomas
    WHERE nin_id = p_nin_id
      AND sin_fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);

    IF v_sintomas_frecuentes > 5 THEN
        INSERT INTO temp_alertas (tipo, payload)
        VALUES (
            'SINTOMAS_FRECUENTES',
            JSON_OBJECT('nin_id', p_nin_id, 'sintomas_7dias', v_sintomas_frecuentes)
        );
        SET v_alertas_generadas = v_alertas_generadas + 1;
    END IF;

    -- 4. Verificar predicción ML de riesgo SEVERO
    SELECT pml_clasificacion INTO v_ultima_prediccion
    FROM predicciones_ml
    WHERE nin_id = p_nin_id
    ORDER BY creado_en DESC
    LIMIT 1;

    IF v_ultima_prediccion IN ('DESNUTRICION_SEVERA', 'OBESIDAD') THEN
        INSERT INTO temp_alertas (tipo, payload)
        VALUES (
            'RIESGO_CRITICO_ML',
            JSON_OBJECT('nin_id', p_nin_id, 'clasificacion', v_ultima_prediccion)
        );
        SET v_alertas_generadas = v_alertas_generadas + 1;
    END IF;

    -- Generar todas las alertas detectadas
    IF v_alertas_generadas > 0 THEN
        -- Insertar alertas en la tabla de notificaciones
        -- Obtener usr_id del nutricionista a través del vínculo
        INSERT INTO notificaciones (usr_id, not_tipo, not_payload, not_estado)
        SELECT
            n.usr_id,
            ta.tipo,
            ta.payload,
            'PENDIENTE'
        FROM temp_alertas ta
        CROSS JOIN vinculos_nutricionista_nino vnn
        INNER JOIN nutricionistas n ON vnn.nut_id = n.nut_id
        WHERE vnn.nin_id = p_nin_id
          AND vnn.vnn_estado = 'ACTIVO'
        LIMIT 1;

        -- Marcar alertas como generadas solo si se insertaron
        UPDATE temp_alertas SET generada = TRUE
        WHERE EXISTS (
            SELECT 1
            FROM vinculos_nutricionista_nino vnn
            WHERE vnn.nin_id = p_nin_id
              AND vnn.vnn_estado = 'ACTIVO'
        );
    END IF;

    -- Retornar resumen de alertas
    SELECT
        tipo,
        payload,
        generada,
        v_alertas_generadas AS total_alertas
    FROM temp_alertas;

    -- Limpiar tabla temporal
    DROP TEMPORARY TABLE IF EXISTS temp_alertas;

END$$

DELIMITER ;

-- ============================================================================
-- FIN DE PROCEDIMIENTOS ALMACENADOS PMV3
-- ============================================================================
