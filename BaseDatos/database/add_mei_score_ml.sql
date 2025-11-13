-- Migración: Agregar campo mei_score_ml a la tabla menus_items
-- Fecha: 2025-11-05
-- Descripción: Almacena el score de confianza del modelo ML para cada recomendación (0.0-1.0)

USE nutrifamily;

-- Agregar columna mei_score_ml
ALTER TABLE menus_items
ADD COLUMN mei_score_ml DECIMAL(5,4) DEFAULT NULL COMMENT 'Score de confianza del modelo ML (0.0-1.0)'
AFTER mei_kcal;

-- Verificar que se agregó correctamente
DESCRIBE menus_items;
