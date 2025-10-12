-- Script para limpiar clasificaciones antiguas de 4 categorías
-- y forzar re-evaluación con el nuevo modelo de 7 categorías

-- OPCIÓN 1: Eliminar todos los estados nutricionales antiguos
-- (Se volverán a calcular automáticamente cuando se consulten)
-- DELETE FROM estados_nutricionales;

-- OPCIÓN 2: Marcar como obsoletos los estados con clasificaciones antiguas
-- UPDATE estados_nutricionales
-- SET en_clasificacion = 'PENDIENTE_REEVALUACION'
-- WHERE en_clasificacion IN ('NORMAL', 'RIESGO', 'MODERADO', 'SEVERO');

-- OPCIÓN 3: Ver cuántos registros tienen clasificaciones antiguas
SELECT
    en_clasificacion,
    COUNT(*) as cantidad
FROM estados_nutricionales
GROUP BY en_clasificacion
ORDER BY cantidad DESC;

-- Para ejecutar:
-- psql -U postgres -d nutricion -f scripts/limpiar_clasificaciones_antiguas.sql
