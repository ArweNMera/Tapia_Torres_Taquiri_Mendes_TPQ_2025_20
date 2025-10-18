-- =====================================================
-- SCRIPT DE PRUEBA: PROCEDIMIENTOS ALMACENADOS NUTRICIÓN
-- =====================================================
-- Este script prueba todos los procedimientos almacenados
-- del módulo de nutrición con datos de ejemplo

USE nutrifam_db;

-- =====================================================
-- 1. PRUEBAS DE NUTRIENTES
-- =====================================================
SELECT '=== PRUEBA 1: NUTRIENTES ===' AS Test;

-- Crear nutrientes
CALL sp_nutrientes_crear('Proteína', 'g');
CALL sp_nutrientes_crear('Carbohidratos', 'g');
CALL sp_nutrientes_crear('Hierro', 'mg');
CALL sp_nutrientes_crear('Calcio', 'mg');
CALL sp_nutrientes_crear('Vitamina A', 'μg');
CALL sp_nutrientes_crear('Vitamina C', 'mg');
CALL sp_nutrientes_crear('Fibra', 'g');
CALL sp_nutrientes_crear('Grasas totales', 'g');

-- Listar todos los nutrientes
SELECT 'Listado de todos los nutrientes:' AS Info;
CALL sp_nutrientes_listar(NULL, 50);

-- Buscar nutriente específico
SELECT 'Buscar "Vitamina":' AS Info;
CALL sp_nutrientes_listar('Vitamina', 10);

-- Obtener por ID
SELECT 'Obtener nutriente ID 1:' AS Info;
CALL sp_nutrientes_obtener(1);

-- Actualizar nutriente
SELECT 'Actualizar nutriente ID 1:' AS Info;
CALL sp_nutrientes_actualizar(1, 'Proteína total', 'gramos');

-- =====================================================
-- 2. PRUEBAS DE ALIMENTOS
-- =====================================================
SELECT '=== PRUEBA 2: ALIMENTOS ===' AS Test;

-- Crear alimentos peruanos
CALL sp_alimentos_crear('Quinua cocida', 'Cereales', '1 taza (185g)', 2.50);
CALL sp_alimentos_crear('Papa amarilla', 'Tubérculos', '1 unidad mediana (150g)', 1.00);
CALL sp_alimentos_crear('Camote', 'Tubérculos', '1 unidad mediana (130g)', 1.20);
CALL sp_alimentos_crear('Leche fresca', 'Lácteos', '1 vaso (240ml)', 2.00);
CALL sp_alimentos_crear('Huevo', 'Proteínas', '1 unidad grande (50g)', 0.50);
CALL sp_alimentos_crear('Pollo', 'Proteínas', '100g', 8.00);
CALL sp_alimentos_crear('Zanahoria', 'Verduras', '1 unidad mediana (60g)', 0.80);
CALL sp_alimentos_crear('Espinaca', 'Verduras', '1 taza (30g)', 1.50);
CALL sp_alimentos_crear('Naranja', 'Frutas', '1 unidad mediana (130g)', 1.00);
CALL sp_alimentos_crear('Plátano', 'Frutas', '1 unidad mediana (120g)', 0.80);

-- Listar todos los alimentos
SELECT 'Listado de todos los alimentos:' AS Info;
CALL sp_alimentos_listar(NULL, 50);

-- Buscar alimentos
SELECT 'Buscar "papa":' AS Info;
CALL sp_alimentos_listar('papa', 10);

-- Buscar por categoría
SELECT 'Buscar "Tubérculos":' AS Info;
CALL sp_alimentos_listar('Tubérculos', 10);

-- Obtener por ID
SELECT 'Obtener alimento ID 1:' AS Info;
CALL sp_alimentos_obtener(1);

-- Actualizar alimento
SELECT 'Actualizar alimento ID 1:' AS Info;
CALL sp_alimentos_actualizar(1, 'Quinua perlada cocida', 'Cereales', '1 taza (185g)', 2.80);

-- =====================================================
-- 3. PRUEBAS DE ALIMENTOS-NUTRIENTES
-- =====================================================
SELECT '=== PRUEBA 3: ALIMENTOS-NUTRIENTES ===' AS Test;

-- Asociar nutrientes con Quinua (ali_id=1)
SELECT 'Agregar nutrientes a Quinua:' AS Info;
CALL sp_alimentos_nutrientes_crear(1, 1, 8.14);   -- Proteína
CALL sp_alimentos_nutrientes_crear(1, 2, 39.41);  -- Carbohidratos
CALL sp_alimentos_nutrientes_crear(1, 3, 2.76);   -- Hierro
CALL sp_alimentos_nutrientes_crear(1, 7, 5.18);   -- Fibra

-- Asociar nutrientes con Huevo (ali_id=5)
SELECT 'Agregar nutrientes a Huevo:' AS Info;
CALL sp_alimentos_nutrientes_crear(5, 1, 6.28);   -- Proteína
CALL sp_alimentos_nutrientes_crear(5, 3, 0.88);   -- Hierro
CALL sp_alimentos_nutrientes_crear(5, 4, 28.00);  -- Calcio
CALL sp_alimentos_nutrientes_crear(5, 5, 160.00); -- Vitamina A

-- Asociar nutrientes con Naranja (ali_id=9)
SELECT 'Agregar nutrientes a Naranja:' AS Info;
CALL sp_alimentos_nutrientes_crear(9, 2, 11.75);  -- Carbohidratos
CALL sp_alimentos_nutrientes_crear(9, 6, 53.20);  -- Vitamina C
CALL sp_alimentos_nutrientes_crear(9, 7, 2.40);   -- Fibra

-- Ver alimento con sus nutrientes
SELECT 'Ver Quinua con nutrientes:' AS Info;
CALL sp_alimentos_con_nutrientes_obtener(1);

SELECT 'Ver Huevo con nutrientes:' AS Info;
CALL sp_alimentos_con_nutrientes_obtener(5);

-- =====================================================
-- 4. PRUEBAS DE RECETAS
-- =====================================================
SELECT '=== PRUEBA 4: RECETAS ===' AS Test;

-- Crear recetas peruanas
CALL sp_recetas_crear(
  'Quinua con verduras',
  'Plato nutritivo con quinua y verduras frescas de temporada',
  '1. Cocinar la quinua en agua con sal por 15 minutos\n2. Saltear las verduras en aceite de oliva\n3. Mezclar quinua con verduras\n4. Servir caliente',
  30,
  4,
  10.50
);

CALL sp_recetas_crear(
  'Tortilla de papa',
  'Tortilla española con papa amarilla peruana',
  '1. Cortar papas en rodajas finas\n2. Freír papas hasta dorar\n3. Batir huevos con sal\n4. Mezclar papas con huevos\n5. Cocinar en sartén por ambos lados',
  25,
  3,
  8.00
);

CALL sp_recetas_crear(
  'Jugo de naranja natural',
  'Jugo fresco de naranja recién exprimido',
  '1. Exprimir las naranjas\n2. Colar si es necesario\n3. Servir inmediatamente',
  5,
  2,
  3.00
);

CALL sp_recetas_crear(
  'Ensalada nutritiva',
  'Ensalada con verduras frescas y pollo',
  '1. Lavar y cortar todas las verduras\n2. Cocinar el pollo a la plancha\n3. Mezclar todo en un bowl\n4. Aliñar con limón y aceite de oliva',
  20,
  2,
  12.00
);

-- Listar todas las recetas
SELECT 'Listado de todas las recetas:' AS Info;
CALL sp_recetas_listar(NULL, 50);

-- Buscar recetas
SELECT 'Buscar "quinua":' AS Info;
CALL sp_recetas_listar('quinua', 10);

-- Obtener receta por ID
SELECT 'Obtener receta ID 1:' AS Info;
CALL sp_recetas_obtener(1);

-- Actualizar receta
SELECT 'Actualizar receta ID 1:' AS Info;
CALL sp_recetas_actualizar(
  1,
  'Quinua con verduras al vapor',
  'Plato nutritivo con quinua y verduras al vapor',
  '1. Cocinar la quinua\n2. Cocinar verduras al vapor\n3. Mezclar\n4. Servir',
  35,
  4,
  11.00
);

-- =====================================================
-- 5. PRUEBAS DE RECETAS-INGREDIENTES
-- =====================================================
SELECT '=== PRUEBA 5: RECETAS-INGREDIENTES ===' AS Test;

-- Agregar ingredientes a "Quinua con verduras" (rec_id=1)
SELECT 'Agregar ingredientes a Quinua con verduras:' AS Info;
CALL sp_recetas_ingredientes_crear(1, 1, 200, 'gramos');  -- Quinua
CALL sp_recetas_ingredientes_crear(1, 7, 100, 'gramos');  -- Zanahoria
CALL sp_recetas_ingredientes_crear(1, 8, 50, 'gramos');   -- Espinaca

-- Agregar ingredientes a "Tortilla de papa" (rec_id=2)
SELECT 'Agregar ingredientes a Tortilla de papa:' AS Info;
CALL sp_recetas_ingredientes_crear(2, 2, 300, 'gramos');  -- Papa
CALL sp_recetas_ingredientes_crear(2, 5, 4, 'unidades');  -- Huevo

-- Agregar ingredientes a "Jugo de naranja" (rec_id=3)
SELECT 'Agregar ingredientes a Jugo de naranja:' AS Info;
CALL sp_recetas_ingredientes_crear(3, 9, 3, 'unidades');  -- Naranja

-- Agregar ingredientes a "Ensalada nutritiva" (rec_id=4)
SELECT 'Agregar ingredientes a Ensalada:' AS Info;
CALL sp_recetas_ingredientes_crear(4, 6, 150, 'gramos');  -- Pollo
CALL sp_recetas_ingredientes_crear(4, 7, 80, 'gramos');   -- Zanahoria
CALL sp_recetas_ingredientes_crear(4, 8, 60, 'gramos');   -- Espinaca

-- Actualizar ingrediente
SELECT 'Actualizar ingrediente:' AS Info;
CALL sp_recetas_ingredientes_actualizar(1, 250, 'gramos');

-- =====================================================
-- 6. PRUEBAS DE RECETAS-COMIDAS
-- =====================================================
SELECT '=== PRUEBA 6: RECETAS-COMIDAS ===' AS Test;

-- Asociar recetas con tipos de comida
SELECT 'Asociar recetas con tipos de comida:' AS Info;

-- Quinua con verduras -> ALMUERZO, CENA
CALL sp_recetas_comidas_crear(1, 'ALMUERZO');
CALL sp_recetas_comidas_crear(1, 'CENA');

-- Tortilla de papa -> DESAYUNO, CENA
CALL sp_recetas_comidas_crear(2, 'DESAYUNO');
CALL sp_recetas_comidas_crear(2, 'CENA');

-- Jugo de naranja -> DESAYUNO, SNACK
CALL sp_recetas_comidas_crear(3, 'DESAYUNO');
CALL sp_recetas_comidas_crear(3, 'SNACK');

-- Ensalada -> ALMUERZO
CALL sp_recetas_comidas_crear(4, 'ALMUERZO');

-- Listar recetas por tipo de comida
SELECT 'Recetas para DESAYUNO:' AS Info;
CALL sp_recetas_por_tipo_comida_listar('DESAYUNO', 50);

SELECT 'Recetas para ALMUERZO:' AS Info;
CALL sp_recetas_por_tipo_comida_listar('ALMUERZO', 50);

SELECT 'Recetas para CENA:' AS Info;
CALL sp_recetas_por_tipo_comida_listar('CENA', 50);

SELECT 'Recetas para SNACK:' AS Info;
CALL sp_recetas_por_tipo_comida_listar('SNACK', 50);

-- =====================================================
-- 7. PRUEBAS DE RECETA COMPLETA
-- =====================================================
SELECT '=== PRUEBA 7: RECETA COMPLETA ===' AS Test;

-- Ver receta completa (con ingredientes y tipos de comida)
SELECT 'Receta completa ID 1 (Quinua con verduras):' AS Info;
CALL sp_recetas_completa_obtener(1);

SELECT 'Receta completa ID 2 (Tortilla de papa):' AS Info;
CALL sp_recetas_completa_obtener(2);

-- =====================================================
-- 8. PRUEBAS DE DISPONIBILIDAD
-- =====================================================
SELECT '=== PRUEBA 8: DISPONIBILIDAD DE ALIMENTOS ===' AS Test;

-- Crear disponibilidad para diferentes departamentos y meses
SELECT 'Crear disponibilidad de alimentos:' AS Info;

-- Quinua (disponible todo el año en Cusco, Puno)
CALL sp_disponibilidad_crear(1, 'Cusco', 1, TRUE);
CALL sp_disponibilidad_crear(1, 'Cusco', 2, TRUE);
CALL sp_disponibilidad_crear(1, 'Cusco', 6, TRUE);
CALL sp_disponibilidad_crear(1, 'Puno', 1, TRUE);
CALL sp_disponibilidad_crear(1, 'Puno', 6, TRUE);

-- Papa (disponible mayo-julio en Cusco)
CALL sp_disponibilidad_crear(2, 'Cusco', 5, TRUE);
CALL sp_disponibilidad_crear(2, 'Cusco', 6, TRUE);
CALL sp_disponibilidad_crear(2, 'Cusco', 7, TRUE);
CALL sp_disponibilidad_crear(2, 'Lima', 1, TRUE);

-- Naranja (disponible junio-octubre en Lima)
CALL sp_disponibilidad_crear(9, 'Lima', 6, TRUE);
CALL sp_disponibilidad_crear(9, 'Lima', 7, TRUE);
CALL sp_disponibilidad_crear(9, 'Lima', 8, TRUE);
CALL sp_disponibilidad_crear(9, 'Lima', 9, TRUE);
CALL sp_disponibilidad_crear(9, 'Lima', 10, TRUE);

-- Listar toda la disponibilidad
SELECT 'Toda la disponibilidad:' AS Info;
CALL sp_disponibilidad_listar(NULL, NULL, 100);

-- Filtrar por departamento
SELECT 'Disponibilidad en Cusco:' AS Info;
CALL sp_disponibilidad_listar('Cusco', NULL, 100);

-- Filtrar por mes
SELECT 'Disponibilidad en mes 6 (Junio):' AS Info;
CALL sp_disponibilidad_listar(NULL, 6, 100);

-- Filtrar por departamento y mes
SELECT 'Disponibilidad en Cusco en Junio:' AS Info;
CALL sp_disponibilidad_listar('Cusco', 6, 100);

-- Actualizar disponibilidad
SELECT 'Actualizar disponibilidad:' AS Info;
CALL sp_disponibilidad_actualizar(1, FALSE);

-- Obtener disponibilidad por ID
SELECT 'Obtener disponibilidad ID 1:' AS Info;
CALL sp_disponibilidad_obtener(1);

-- =====================================================
-- 9. PRUEBAS DE ELIMINACIÓN (CUIDADO!)
-- =====================================================
SELECT '=== PRUEBA 9: ELIMINACIONES (COMENTADO POR SEGURIDAD) ===' AS Test;

-- DESCOMENTAR SOLO SI DESEAS PROBAR ELIMINACIONES

-- Eliminar disponibilidad
-- CALL sp_disponibilidad_eliminar(1);

-- Eliminar asociación receta-comida
-- CALL sp_recetas_comidas_eliminar(1);

-- Eliminar ingrediente de receta
-- CALL sp_recetas_ingredientes_eliminar(1);

-- Eliminar relación alimento-nutriente
-- CALL sp_alimentos_nutrientes_eliminar(1);

-- Eliminar receta (esto eliminará en cascada ingredientes y asociaciones)
-- CALL sp_recetas_eliminar(1);

-- Eliminar alimento (esto eliminará en cascada nutrientes y disponibilidad)
-- CALL sp_alimentos_eliminar(1);

-- Eliminar nutriente (esto eliminará en cascada las asociaciones)
-- CALL sp_nutrientes_eliminar(1);

-- =====================================================
-- 10. RESUMEN DE PRUEBAS
-- =====================================================
SELECT '=== RESUMEN DE PRUEBAS ===' AS Test;

SELECT 'Total de nutrientes:' AS Info;
SELECT COUNT(*) as total FROM nutrientes;

SELECT 'Total de alimentos:' AS Info;
SELECT COUNT(*) as total FROM alimentos;

SELECT 'Total de alimentos-nutrientes:' AS Info;
SELECT COUNT(*) as total FROM alimentos_nutrientes;

SELECT 'Total de recetas:' AS Info;
SELECT COUNT(*) as total FROM recetas;

SELECT 'Total de ingredientes:' AS Info;
SELECT COUNT(*) as total FROM recetas_ingredientes;

SELECT 'Total de recetas-comidas:' AS Info;
SELECT COUNT(*) as total FROM recetas_comidas;

SELECT 'Total de disponibilidad:' AS Info;
SELECT COUNT(*) as total FROM disponibilidad_alimentos;

SELECT '✅ ¡PRUEBAS COMPLETADAS!' AS Status;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================
