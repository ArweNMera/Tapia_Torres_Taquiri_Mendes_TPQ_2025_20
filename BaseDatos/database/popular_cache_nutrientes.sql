-- ============================================================================
-- SCRIPT: Popular cache de nutrientes para todas las recetas
-- Descripción: Calcula y guarda los valores nutricionales de cada receta
-- ============================================================================

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
