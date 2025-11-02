-- =========================================================
-- RECETAS ADICIONALES PARA AUMENTAR VARIEDAD
-- Total: 21 nuevas (7 desayunos, 7 almuerzos, 7 cenas)
-- =========================================================

-- =========================================================
-- DESAYUNOS ADICIONALES (7 nuevos) - IDs 230-236
-- =========================================================
INSERT INTO recetas (rec_id, rec_nombre, rec_instrucciones, rec_activo) VALUES
(230,'Arroz con leche y mango','Cocer arroz con leche; servir con mango picado.',1),
(231,'Tostadas de pan integral con huevo','Tostar pan; servir con huevo revuelto.',1),
(232,'Batido de papaya con avena','Licuar papaya con avena y leche.',1),
(233,'Choclo con queso fresco','Hervir choclo; servir con queso fresco.',1),
(234,'Quinua con yogurt y fresa','Mezclar quinua cocida con yogurt y fresas.',1),
(235,'Camote dulce con leche','Hervir camote; servir con leche tibia.',1),
(236,'Pan con palta y tomate','Untar pan con palta; agregar rodajas de tomate.',1);

-- =========================================================
-- ALMUERZOS ADICIONALES (7 nuevos) - IDs 237-243
-- =========================================================
INSERT INTO recetas (rec_id, rec_nombre, rec_instrucciones, rec_activo) VALUES
(237,'Arroz con huevo frito y espinaca','Saltear arroz; coronar con huevo frito y espinaca.',1),
(238,'Guiso de garbanzo con zanahoria','Cocer garbanzo; agregar zanahoria en cubos.',1),
(239,'Pollo guisado con papa y tomate','Guisar pollo con papa; agregar tomate.',1),
(240,'Yuca frita con anchoveta','Freír yuca; acompañar con anchoveta a la plancha.',1),
(241,'Lentejas con camote','Cocer lentejas; servir con camote en cubos.',1),
(242,'Quinua con pollo deshilachado','Mezclar quinua con pollo deshilachado y cebolla.',1),
(243,'Arroz con bonito y brócoli','Saltear bonito; mezclar con arroz y brócoli.',1);

-- =========================================================
-- CENAS ADICIONALES (7 nuevas) - IDs 244-250
-- =========================================================
INSERT INTO recetas (rec_id, rec_nombre, rec_instrucciones, rec_activo) VALUES
(244,'Crema de zanahoria','Licuar zanahoria cocida con leche; calentar.',1),
(245,'Ensalada de quinua con palta','Mezclar quinua fría con palta y tomate.',1),
(246,'Huevo revuelto con brócoli','Saltear brócoli; agregar huevo batido.',1),
(247,'Choclo con yogurt','Servir choclo cocido con yogurt natural.',1),
(248,'Papa rellena con queso','Hervir papa; rellenar con queso fresco.',1),
(249,'Sopa de lentejas ligera','Hervir lentejas con zanahoria; servir caldo.',1),
(250,'Ensalada de frutas (mango, papaya, plátano)','Cortar frutas; mezclar sin azúcar.',1);

-- =========================================================
-- INGREDIENTES PARA DESAYUNOS NUEVOS (230-236)
-- =========================================================
INSERT INTO recetas_ingredientes VALUES
-- 230: Arroz con leche y mango (550 kcal)
(230,16,120.0000,'g'),(230,5,200.0000,'ml'),(230,27,100.0000,'g'),

-- 231: Tostadas de pan integral con huevo (380 kcal)
(231,30,80.0000,'g'),(231,7,100.0000,'g'),

-- 232: Batido de papaya con avena (340 kcal)
(232,28,150.0000,'g'),(232,15,30.0000,'g'),(232,5,150.0000,'ml'),

-- 233: Choclo con queso fresco (380 kcal)
(233,18,180.0000,'g'),(233,20,40.0000,'g'),

-- 234: Quinua con yogurt y fresa (420 kcal)
(234,1,140.0000,'g'),(234,19,200.0000,'ml'),(234,29,80.0000,'g'),

-- 235: Camote dulce con leche (380 kcal)
(235,17,180.0000,'g'),(235,5,200.0000,'ml'),

-- 236: Pan con palta y tomate (350 kcal)
(236,30,90.0000,'g'),(236,13,50.0000,'g'),(236,25,60.0000,'g');

-- =========================================================
-- INGREDIENTES PARA ALMUERZOS NUEVOS (237-243)
-- =========================================================
INSERT INTO recetas_ingredientes VALUES
-- 237: Arroz con huevo frito y espinaca (480 kcal)
(237,16,150.0000,'g'),(237,7,80.0000,'g'),(237,3,80.0000,'g'),

-- 238: Guiso de garbanzo con zanahoria (520 kcal)
(238,23,180.0000,'g'),(238,4,100.0000,'g'),

-- 239: Pollo guisado con papa y tomate (580 kcal)
(239,2,140.0000,'g'),(239,10,150.0000,'g'),(239,25,80.0000,'g'),

-- 240: Yuca frita con anchoveta (620 kcal)
(240,14,180.0000,'g'),(240,11,100.0000,'g'),

-- 241: Lentejas con camote (450 kcal)
(241,6,150.0000,'g'),(241,17,140.0000,'g'),

-- 242: Quinua con pollo deshilachado (540 kcal)
(242,1,160.0000,'g'),(242,2,120.0000,'g'),(242,26,50.0000,'g'),

-- 243: Arroz con bonito y brócoli (620 kcal)
(243,16,150.0000,'g'),(243,21,130.0000,'g'),(243,12,80.0000,'g');

-- =========================================================
-- INGREDIENTES PARA CENAS NUEVAS (244-250)
-- =========================================================
INSERT INTO recetas_ingredientes VALUES
-- 244: Crema de zanahoria (280 kcal)
(244,4,200.0000,'g'),(244,5,150.0000,'ml'),

-- 245: Ensalada de quinua con palta (420 kcal)
(245,1,150.0000,'g'),(245,13,60.0000,'g'),(245,25,60.0000,'g'),

-- 246: Huevo revuelto con brócoli (300 kcal)
(246,7,100.0000,'g'),(246,12,100.0000,'g'),

-- 247: Choclo con yogurt (320 kcal)
(247,18,140.0000,'g'),(247,19,150.0000,'ml'),

-- 248: Papa rellena con queso (380 kcal)
(248,10,180.0000,'g'),(248,20,50.0000,'g'),

-- 249: Sopa de lentejas ligera (260 kcal)
(249,6,100.0000,'g'),(249,4,80.0000,'g'),

-- 250: Ensalada de frutas (220 kcal)
(250,27,80.0000,'g'),(250,28,80.0000,'g'),(250,8,80.0000,'g');

-- =========================================================
-- CLASIFICACIÓN POR TIPO DE COMIDA
-- =========================================================
INSERT INTO recetas_comidas (rec_id, rc_comida) VALUES
-- DESAYUNOS (230-236)
(230,'DESAYUNO'),
(231,'DESAYUNO'),
(232,'DESAYUNO'),
(233,'DESAYUNO'),
(234,'DESAYUNO'),
(235,'DESAYUNO'),
(236,'DESAYUNO'),

-- ALMUERZOS (237-243)
(237,'ALMUERZO'),
(238,'ALMUERZO'),
(239,'ALMUERZO'),
(240,'ALMUERZO'),
(241,'ALMUERZO'),
(242,'ALMUERZO'),
(243,'ALMUERZO'),

-- CENAS (244-250)
(244,'CENA'),
(245,'CENA'),
(246,'CENA'),
(247,'CENA'),
(248,'CENA'),
(249,'CENA'),
(250,'CENA');

-- =========================================================
-- RESUMEN DE RECETAS TOTALES:
-- =========================================================
-- DESAYUNOS: 7 originales (200,204,212,215,216,221,229) + 7 nuevos (230-236) = 14 total
-- ALMUERZOS: 15 originales (201,202,205,208,210,211,213,214,217-220,224-226) + 7 nuevos (237-243) = 22 total
-- CENAS: 7 originales (203,206,207,222,223,227,228) + 7 nuevos (244-250) = 14 total
-- TOTAL: 50 recetas (29 originales + 21 nuevas)
-- =========================================================

-- =========================================================
-- PERFIL CALÓRICO DE LAS NUEVAS RECETAS:
-- =========================================================
-- DESAYUNOS (320-550 kcal): Variedad de bajo a alto
--   - Bajo: 232 (340), 236 (350)
--   - Medio: 231 (380), 233 (380), 235 (380)
--   - Alto: 234 (420), 230 (550)

-- ALMUERZOS (450-620 kcal): Más variedad
--   - Medio: 241 (450), 237 (480), 238 (520), 242 (540)
--   - Alto: 239 (580), 240 (620), 243 (620)

-- CENAS (220-420 kcal): Ligeras a moderadas
--   - Ligero: 250 (220), 249 (260), 244 (280)
--   - Medio: 246 (300), 247 (320), 248 (380)
--   - Moderado: 245 (420)
-- =========================================================
