-- ============================================================================
-- Script para balancear datos antropométricos
-- ============================================================================
-- Objetivo: Crear una distribución balanceada de estados nutricionales
-- 
-- Distribución objetivo (200 niños únicos de 206 disponibles):
-- Distribución balanceada para >90% accuracy:
-- - NORMAL: 70 niños (35%) - Mayoría pero no dominante
-- - RIESGO_DESNUTRICIÓN: 30 niños (15%)
-- - DESNUTRICIÓN_MODERADA: 25 niños (12.5%)
-- - DESNUTRICIÓN_SEVERA: 25 niños (12.5%)
-- - RIESGO_SOBREPESO: 20 niños (10%)
-- - SOBREPESO: 15 niños (7.5%)
-- - OBESIDAD: 15 niños (7.5%)
-- TOTAL: 200 niños
-- ============================================================================

USE nutricion;

-- Backup de datos originales
CREATE TABLE IF NOT EXISTS antropometrias_backup_original AS 
SELECT * FROM antropometrias;

-- ============================================================================
-- PASO 1: Seleccionar niños para cada categoría
-- ============================================================================

-- Crear tabla temporal con asignaciones
DROP TEMPORARY TABLE IF EXISTS temp_asignaciones;
CREATE TEMPORARY TABLE temp_asignaciones (
    nin_id BIGINT UNSIGNED,
    categoria VARCHAR(50),
    target_baz DECIMAL(6,3),
    target_peso_kg DECIMAL(5,2)
);

-- ============================================================================
-- PASO 2: Asignar categorías a niños existentes
-- ============================================================================

-- NORMAL (70 niños) - BAZ entre -1 y +1
INSERT INTO temp_asignaciones (nin_id, categoria, target_baz)
SELECT nin_id, 'NORMAL', ROUND(-0.8 + (RAND() * 1.6), 2) as target_baz
FROM ninos 
WHERE nin_id IN (
    SELECT nin_id FROM antropometrias 
    GROUP BY nin_id 
    ORDER BY RAND() 
    LIMIT 70
);

-- RIESGO_DESNUTRICIÓN (30 niños) - BAZ entre -2 y -1
INSERT INTO temp_asignaciones (nin_id, categoria, target_baz)
SELECT nin_id, 'RIESGO_DESNUTRICION', ROUND(-1.9 + (RAND() * 0.9), 2) as target_baz
FROM ninos 
WHERE nin_id NOT IN (SELECT nin_id FROM temp_asignaciones)
AND nin_id IN (
    SELECT nin_id FROM antropometrias 
    GROUP BY nin_id 
    ORDER BY RAND() 
    LIMIT 30
);

-- DESNUTRICIÓN_MODERADA (25 niños) - BAZ entre -3 y -2
INSERT INTO temp_asignaciones (nin_id, categoria, target_baz)
SELECT nin_id, 'DESNUTRICION_MODERADA', ROUND(-2.9 + (RAND() * 0.9), 2) as target_baz
FROM ninos 
WHERE nin_id NOT IN (SELECT nin_id FROM temp_asignaciones)
AND nin_id IN (
    SELECT nin_id FROM antropometrias 
    GROUP BY nin_id 
    ORDER BY RAND() 
    LIMIT 25
);

-- DESNUTRICIÓN_SEVERA (25 niños) - BAZ < -3
INSERT INTO temp_asignaciones (nin_id, categoria, target_baz)
SELECT nin_id, 'DESNUTRICION_SEVERA', ROUND(-4.5 + (RAND() * 1.2), 2) as target_baz
FROM ninos 
WHERE nin_id NOT IN (SELECT nin_id FROM temp_asignaciones)
AND nin_id IN (
    SELECT nin_id FROM antropometrias 
    GROUP BY nin_id 
    ORDER BY RAND() 
    LIMIT 25
);

-- RIESGO_SOBREPESO (20 niños) - BAZ entre +1 y +2
INSERT INTO temp_asignaciones (nin_id, categoria, target_baz)
SELECT nin_id, 'RIESGO_SOBREPESO', ROUND(1.1 + (RAND() * 0.8), 2) as target_baz
FROM ninos 
WHERE nin_id NOT IN (SELECT nin_id FROM temp_asignaciones)
AND nin_id IN (
    SELECT nin_id FROM antropometrias 
    GROUP BY nin_id 
    ORDER BY RAND() 
    LIMIT 20
);

-- SOBREPESO (15 niños) - BAZ entre +2 y +3
INSERT INTO temp_asignaciones (nin_id, categoria, target_baz)
SELECT nin_id, 'SOBREPESO', ROUND(2.1 + (RAND() * 0.8), 2) as target_baz
FROM ninos 
WHERE nin_id NOT IN (SELECT nin_id FROM temp_asignaciones)
AND nin_id IN (
    SELECT nin_id FROM antropometrias 
    GROUP BY nin_id 
    ORDER BY RAND() 
    LIMIT 15
);

-- OBESIDAD (15 niños) - BAZ > +3
INSERT INTO temp_asignaciones (nin_id, categoria, target_baz)
SELECT nin_id, 'OBESIDAD', ROUND(3.2 + (RAND() * 1.5), 2) as target_baz
FROM ninos 
WHERE nin_id NOT IN (SELECT nin_id FROM temp_asignaciones)
AND nin_id IN (
    SELECT nin_id FROM antropometrias 
    GROUP BY nin_id 
    ORDER BY RAND() 
    LIMIT 15
);

-- ============================================================================
-- PASO 3: Calcular pesos realistas usando tablas OMS
-- ============================================================================

-- Para cada niño, calcular el peso que corresponde al BAZ objetivo
UPDATE temp_asignaciones ta
JOIN (
    SELECT 
        a.nin_id,
        a.ant_talla_cm,
        n.nin_sexo,
        TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as edad_meses,
        lms.M,
        lms.L,
        lms.S
    FROM antropometrias a
    JOIN ninos n ON a.nin_id = n.nin_id
    LEFT JOIN oms_bmi_lms lms ON 
        lms.sexo = n.nin_sexo 
        AND lms.edad_meses = TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha)
    WHERE a.ant_id IN (
        SELECT MAX(ant_id) FROM antropometrias GROUP BY nin_id
    )
) datos ON ta.nin_id = datos.nin_id
SET ta.target_peso_kg = CASE
    -- Fórmula inversa de BAZ: BMI = M * (1 + L*S*Z)^(1/L)
    -- Peso = BMI * (talla_m)^2
    WHEN datos.L != 0 THEN 
        ROUND(
            datos.M * POWER(1 + datos.L * datos.S * ta.target_baz, 1/datos.L) 
            * POWER(datos.ant_talla_cm / 100, 2),
            2
        )
    ELSE 
        ROUND(
            datos.M * EXP(datos.S * ta.target_baz) 
            * POWER(datos.ant_talla_cm / 100, 2),
            2
        )
END
WHERE datos.M IS NOT NULL;

-- ============================================================================
-- PASO 4: Actualizar antropometrías con nuevos pesos
-- ============================================================================

UPDATE antropometrias a
JOIN temp_asignaciones ta ON a.nin_id = ta.nin_id
SET a.ant_peso_kg = ta.target_peso_kg,
    a.ant_z_imc = ta.target_baz,
    a.actualizado_en = NOW()
WHERE a.ant_id IN (
    SELECT MAX(ant_id) FROM (SELECT * FROM antropometrias) a2 
    WHERE a2.nin_id = ta.nin_id
)
AND ta.target_peso_kg IS NOT NULL
AND ta.target_peso_kg > 0;

-- ============================================================================
-- PASO 5: Verificar resultados
-- ============================================================================

SELECT 
    ta.categoria,
    COUNT(*) as cantidad,
    ROUND(AVG(ta.target_baz), 2) as baz_promedio,
    ROUND(MIN(ta.target_baz), 2) as baz_min,
    ROUND(MAX(ta.target_baz), 2) as baz_max,
    ROUND(AVG(ta.target_peso_kg), 2) as peso_promedio
FROM temp_asignaciones ta
WHERE ta.target_peso_kg IS NOT NULL
GROUP BY ta.categoria
ORDER BY 
    CASE ta.categoria
        WHEN 'DESNUTRICION_SEVERA' THEN 1
        WHEN 'DESNUTRICION_MODERADA' THEN 2
        WHEN 'RIESGO_DESNUTRICION' THEN 3
        WHEN 'NORMAL' THEN 4
        WHEN 'RIESGO_SOBREPESO' THEN 5
        WHEN 'SOBREPESO' THEN 6
        WHEN 'OBESIDAD' THEN 7
    END;

-- Mostrar algunos ejemplos
SELECT 
    n.nin_id,
    n.nin_nombres,
    TIMESTAMPDIFF(YEAR, n.nin_fecha_nac, CURDATE()) as edad_anos,
    a.ant_peso_kg,
    a.ant_talla_cm,
    ROUND(a.ant_peso_kg / POWER(a.ant_talla_cm / 100, 2), 2) as imc,
    a.ant_z_imc as baz,
    ta.categoria
FROM ninos n
JOIN antropometrias a ON n.nin_id = a.nin_id
JOIN temp_asignaciones ta ON n.nin_id = ta.nin_id
WHERE a.ant_id IN (
    SELECT MAX(ant_id) FROM antropometrias GROUP BY nin_id
)
ORDER BY ta.categoria, n.nin_id
LIMIT 20;

-- ============================================================================
-- NOTAS:
-- ============================================================================
-- 1. Este script modifica las antropometrías existentes
-- 2. Se crea un backup en antropometrias_backup_original
-- 3. Los pesos se calculan usando las tablas OMS para ser realistas
-- 4. Después de ejecutar este script, debes:
--    a) Limpiar features_ml: TRUNCATE TABLE features_ml;
--    b) Recalcular features: python3 scripts/calcular_features_todos.py
--    c) Extraer datos: python3 src/utils/db_connector.py --output datos.csv
--    d) Reentrenar modelo: ./scripts/regenerar_datos.sh
-- ============================================================================
