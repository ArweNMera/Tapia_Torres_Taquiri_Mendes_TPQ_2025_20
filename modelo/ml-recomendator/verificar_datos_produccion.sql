-- Script para verificar los datos disponibles en producción
-- Ejecuta estos queries en tu BD de producción

-- 1. Cantidad de niños con perfil nutricional
SELECT
    COUNT(DISTINCT n.nin_id) as total_ninos,
    COUNT(DISTINCT CASE WHEN pnn.pnn_calorias_diarias IS NOT NULL THEN n.nin_id END) as ninos_con_perfil
FROM ninos n
LEFT JOIN perfil_nutricional_nino pnn ON n.nin_id = pnn.nin_id AND pnn.pnn_vigente = 1;

-- 2. Cantidad de menús e items
SELECT
    COUNT(DISTINCT m.men_id) as total_menus,
    COUNT(DISTINCT mi.mei_id) as total_items_menu
FROM menus m
LEFT JOIN menus_items mi ON m.men_id = mi.men_id;

-- 3. Distribución de menús por niño
SELECT
    'Niños con menús' as concepto,
    COUNT(DISTINCT nin_id) as cantidad
FROM menus
UNION ALL
SELECT
    'Total menús',
    COUNT(DISTINCT men_id)
FROM menus
UNION ALL
SELECT
    'Items por menú (promedio)',
    CAST(AVG(items_count) AS SIGNED)
FROM (
    SELECT men_id, COUNT(*) as items_count
    FROM menus_items
    GROUP BY men_id
) t;

-- 4. ¿Hay feedback sintético en la tabla menus_feedback?
SELECT
    COUNT(*) as total_feedback,
    COUNT(DISTINCT nin_id) as ninos_con_feedback,
    COUNT(DISTINCT mei_id) as items_con_feedback,
    AVG(mf_rating) as rating_promedio,
    AVG(mf_porcentaje_consumido) as consumo_promedio
FROM menus_feedback;

-- 5. Simulación del query de entrenamiento (ver cuántos registros generaría)
SELECT COUNT(*) as registros_training
FROM ninos n
LEFT JOIN (
    SELECT nin_id, ant_peso_kg, ant_talla_cm, ant_z_imc,
           ROW_NUMBER() OVER (PARTITION BY nin_id ORDER BY ant_fecha DESC) as rn
    FROM antropometrias
) a ON n.nin_id = a.nin_id AND a.rn = 1
LEFT JOIN perfil_nutricional_nino pnn ON n.nin_id = pnn.nin_id AND pnn.pnn_vigente = 1
LEFT JOIN menus m ON n.nin_id = m.nin_id
LEFT JOIN menus_items mi ON m.men_id = mi.men_id
LEFT JOIN recetas r ON mi.rec_id = r.rec_id
WHERE pnn.pnn_calorias_diarias IS NOT NULL
  AND mi.mei_id IS NOT NULL;
