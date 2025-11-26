-- Migración: Actualizar columna pml_clasificacion para soportar 7 categorías del modelo ML
-- Fecha: 2025-11-26
-- Descripción: Cambiar ENUM de 4 categorías a 7 categorías nutricionales

USE nutricion_db;

-- Modificar la columna pml_clasificacion para incluir las 7 categorías del modelo
ALTER TABLE predicciones_ml
MODIFY COLUMN pml_clasificacion ENUM(
    'DESNUTRICION_SEVERA',
    'DESNUTRICION_MODERADA',
    'RIESGO_DESNUTRICION',
    'NORMAL',
    'RIESGO_SOBREPESO',
    'SOBREPESO',
    'OBESIDAD'
) NOT NULL COMMENT 'Clasificación nutricional predicha (7 categorías)';

-- Verificar el cambio
DESCRIBE predicciones_ml;
