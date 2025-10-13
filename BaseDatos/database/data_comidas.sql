INSERT INTO entidad_tipos (entti_id, entti_codigo, entti_nombre) VALUES
(9,'MUNI','Municipalidad'),
(10,'CS','Centro de Salud');

-- =========================================================
-- 2) ENTIDADES (SOLO Chilca - Huancayo)
-- =========================================================
INSERT INTO entidades (
  ent_id, entti_id, ent_codigo, ent_nombre, ent_descripcion,
  ent_direccion, ent_referencia, ent_departamento, ent_provincia, ent_distrito,
  ent_ubigeo, ent_latitud, ent_longitud, ent_altitud_m, ent_zona, ent_poblacion_aprox, ent_activo
) VALUES
(101,9,'MUNI-CHILCA','Municipalidad Distrital de Chilca (Huancayo)','Gobierno local.',
 'Av. Principal s/n','Plaza de Armas','Junín','Huancayo','Chilca',NULL,NULL,NULL,3240,'URBANA',85000,1),
(102,10,'CS-CHILCA','Centro de Salud Chilca','Primer nivel.',
 'Jr. Salud 123','A 2 cuadras de la muni','Junín','Huancayo','Chilca',NULL,NULL,NULL,3240,'URBANA',0,1);

-- =========================================================
-- 3) NUTRIENTES (catálogo base)
-- =========================================================
INSERT INTO nutrientes (nutri_id, nutri_codigo, nutri_nombre, nutri_unidad) VALUES
(1,'EN','Energía','kcal'),
(2,'PRO','Proteína','g'),
(3,'CHO','Carbohidratos','g'),
(4,'GRA','Grasa','g'),
(5,'FIB','Fibra','g'),
(6,'FE','Hierro','mg'),
(7,'CA','Calcio','mg'),
(8,'VA','Vitamina A','µg'),
(9,'VC','Vitamina C','mg'),
(10,'ZN','Zinc','mg');

-- =========================================================
-- 4) ALIMENTOS (30 ítems)
-- =========================================================
INSERT INTO alimentos (ali_id, ali_nombre, ali_nombre_cientifico, ali_grupo, ali_unidad, ali_activo) VALUES
(1,'Quinua cocida','Chenopodium quinoa','CEREAL/PSEUDOCEREAL','g',1),
(2,'Pechuga de pollo','Gallus gallus domesticus','CARNES','g',1),
(3,'Espinaca','Spinacia oleracea','VERDURAS','g',1),
(4,'Zanahoria','Daucus carota','VERDURAS','g',1),
(5,'Leche entera',NULL,'LÁCTEOS','ml',1),
(6,'Lentejas cocidas','Lens culinaris','LEGUMINOSAS','g',1),
(7,'Huevo','Gallus gallus','HUEVOS','g',1),
(8,'Plátano','Musa paradisiaca','FRUTAS','g',1),
(9,'Naranja','Citrus sinensis','FRUTAS','g',1),
(10,'Papa cocida','Solanum tuberosum','TUBÉRCULOS','g',1),
(11,'Anchoveta','Engraulis ringens','PESCADOS','g',1),
(12,'Brócoli','Brassica oleracea','VERDURAS','g',1),
(13,'Palta','Persea americana','FRUTAS','g',1),
(14,'Yuca cocida','Manihot esculenta','TUBÉRCULOS','g',1),
(15,'Avena','Avena sativa','CEREALES','g',1),
(16,'Arroz blanco cocido','Oryza sativa','CEREALES','g',1),
(17,'Camote cocido','Ipomoea batatas','TUBÉRCULOS','g',1),
(18,'Maíz choclo','Zea mays','CEREALES','g',1),
(19,'Yogurt natural',NULL,'LÁCTEOS','ml',1),
(20,'Queso fresco',NULL,'LÁCTEOS','g',1),
(21,'Bonito','Sarda sarda','PESCADOS','g',1),
(22,'Hígado de pollo',NULL,'VÍSCERAS','g',1),
(23,'Garbanzo cocido','Cicer arietinum','LEGUMINOSAS','g',1),
(24,'Frejol canario cocido','Phaseolus vulgaris','LEGUMINOSAS','g',1),
(25,'Tomate','Solanum lycopersicum','VERDURAS','g',1),
(26,'Cebolla','Allium cepa','VERDURAS','g',1),
(27,'Mango','Mangifera indica','FRUTAS','g',1),
(28,'Papaya','Carica papaya','FRUTAS','g',1),
(29,'Fresa','Fragaria × ananassa','FRUTAS','g',1),
(30,'Pan integral',NULL,'CEREALES','g',1);

-- =========================================================
-- 5) ALIMENTOS_NUTRIENTES (por 100 g o 100 ml)
-- =========================================================
-- 1 Quinua cocida
INSERT INTO alimentos_nutrientes VALUES
(1,1,120.0000,'USDA'),(1,2,4.4000,'USDA'),(1,3,21.3000,'USDA'),(1,4,1.9000,'USDA'),
(1,6,1.5000,'USDA'),(1,7,17.0000,'USDA');
-- 2 Pechuga de pollo
INSERT INTO alimentos_nutrientes VALUES
(2,1,165.0000,'USDA'),(2,2,31.0000,'USDA'),(2,3,0.0000,'USDA'),(2,4,3.6000,'USDA'),
(2,6,1.0000,'USDA'),(2,7,12.0000,'USDA');
-- 3 Espinaca
INSERT INTO alimentos_nutrientes VALUES
(3,1,23.0000,'USDA'),(3,2,2.9000,'USDA'),(3,3,3.6000,'USDA'),(3,4,0.4000,'USDA'),
(3,6,2.7000,'USDA'),(3,7,99.0000,'USDA'),(3,8,469.0000,'USDA'),(3,9,28.1000,'USDA');
-- 4 Zanahoria
INSERT INTO alimentos_nutrientes VALUES
(4,1,41.0000,'USDA'),(4,2,0.9000,'USDA'),(4,3,9.6000,'USDA'),(4,4,0.2000,'USDA'),
(4,6,0.3000,'USDA'),(4,7,33.0000,'USDA'),(4,8,835.0000,'USDA');
-- 5 Leche entera (100 ml)
INSERT INTO alimentos_nutrientes VALUES
(5,1,61.0000,'USDA'),(5,2,3.2000,'USDA'),(5,3,4.7000,'USDA'),(5,4,3.3000,'USDA'),
(5,6,0.0300,'USDA'),(5,7,113.0000,'USDA');
-- 6 Lentejas
INSERT INTO alimentos_nutrientes VALUES
(6,1,116.0000,'USDA'),(6,2,9.0000,'USDA'),(6,3,20.1000,'USDA'),(6,4,0.4000,'USDA'),
(6,6,3.3000,'USDA'),(6,7,19.0000,'USDA');
-- 7 Huevo
INSERT INTO alimentos_nutrientes VALUES
(7,1,155.0000,'USDA'),(7,2,13.0000,'USDA'),(7,3,1.1000,'USDA'),(7,4,11.0000,'USDA'),
(7,6,1.2000,'USDA'),(7,7,50.0000,'USDA');
-- 8 Plátano
INSERT INTO alimentos_nutrientes VALUES
(8,1,89.0000,'USDA'),(8,2,1.1000,'USDA'),(8,3,22.8000,'USDA'),(8,4,0.3000,'USDA'),
(8,6,0.2600,'USDA'),(8,7,5.0000,'USDA'),(8,9,8.7000,'USDA');
-- 9 Naranja
INSERT INTO alimentos_nutrientes VALUES
(9,1,47.0000,'USDA'),(9,2,0.9000,'USDA'),(9,3,11.8000,'USDA'),(9,4,0.1000,'USDA'),
(9,6,0.1000,'USDA'),(9,7,40.0000,'USDA'),(9,9,53.2000,'USDA');
-- 10 Papa
INSERT INTO alimentos_nutrientes VALUES
(10,1,87.0000,'USDA'),(10,2,1.9000,'USDA'),(10,3,20.1000,'USDA'),(10,4,0.1000,'USDA'),
(10,6,0.3000,'USDA'),(10,7,5.0000,'USDA');
-- 11 Anchoveta
INSERT INTO alimentos_nutrientes VALUES
(11,1,131.0000,'FAO'),(11,2,20.4000,'FAO'),(11,3,0.0000,'FAO'),(11,4,4.8000,'FAO'),
(11,6,1.6000,'FAO'),(11,7,147.0000,'FAO');
-- 12 Brócoli
INSERT INTO alimentos_nutrientes VALUES
(12,1,34.0000,'USDA'),(12,2,2.8000,'USDA'),(12,3,6.6000,'USDA'),(12,4,0.4000,'USDA'),
(12,6,0.7000,'USDA'),(12,7,47.0000,'USDA'),(12,9,89.2000,'USDA');
-- 13 Palta
INSERT INTO alimentos_nutrientes VALUES
(13,1,160.0000,'USDA'),(13,2,2.0000,'USDA'),(13,3,8.5000,'USDA'),(13,4,14.7000,'USDA'),
(13,6,0.6000,'USDA'),(13,7,12.0000,'USDA');
-- 14 Yuca
INSERT INTO alimentos_nutrientes VALUES
(14,1,160.0000,'USDA'),(14,2,1.4000,'USDA'),(14,3,38.1000,'USDA'),(14,4,0.3000,'USDA'),
(14,6,0.2700,'USDA'),(14,7,16.0000,'USDA');
-- 15 Avena (cruda)
INSERT INTO alimentos_nutrientes VALUES
(15,1,389.0000,'USDA'),(15,2,16.9000,'USDA'),(15,3,66.3000,'USDA'),(15,4,6.9000,'USDA'),
(15,6,4.7000,'USDA'),(15,7,54.0000,'USDA');
-- 16 Arroz cocido
INSERT INTO alimentos_nutrientes VALUES
(16,1,130.0000,'USDA'),(16,2,2.4000,'USDA'),(16,3,28.0000,'USDA'),(16,4,0.3000,'USDA'),
(16,6,0.2000,'USDA'),(16,7,10.0000,'USDA');
-- 17 Camote
INSERT INTO alimentos_nutrientes VALUES
(17,1,86.0000,'USDA'),(17,2,1.6000,'USDA'),(17,3,20.1000,'USDA'),(17,4,0.1000,'USDA'),
(17,6,0.3000,'USDA'),(17,7,30.0000,'USDA'),(17,8,709.0000,'USDA');
-- 18 Choclo
INSERT INTO alimentos_nutrientes VALUES
(18,1,96.0000,'USDA'),(18,2,3.4000,'USDA'),(18,3,21.0000,'USDA'),(18,4,1.5000,'USDA'),
(18,6,0.5000,'USDA'),(18,7,2.0000,'USDA');
-- 19 Yogurt (100 ml)
INSERT INTO alimentos_nutrientes VALUES
(19,1,61.0000,'USDA'),(19,2,3.5000,'USDA'),(19,3,4.7000,'USDA'),(19,4,3.3000,'USDA'),
(19,6,0.0500,'USDA'),(19,7,121.0000,'USDA');
-- 20 Queso fresco
INSERT INTO alimentos_nutrientes VALUES
(20,1,264.0000,'USDA'),(20,2,14.0000,'USDA'),(20,3,3.0000,'USDA'),(20,4,21.0000,'USDA'),
(20,6,0.3000,'USDA'),(20,7,500.0000,'USDA');
-- 21 Bonito
INSERT INTO alimentos_nutrientes VALUES
(21,1,143.0000,'USDA'),(21,2,29.0000,'USDA'),(21,3,0.0000,'USDA'),(21,4,3.0000,'USDA'),
(21,6,1.1000,'USDA'),(21,7,12.0000,'USDA');
-- 22 Hígado de pollo
INSERT INTO alimentos_nutrientes VALUES
(22,1,167.0000,'USDA'),(22,2,24.0000,'USDA'),(22,3,1.0000,'USDA'),(22,4,6.0000,'USDA'),
(22,6,9.0000,'USDA'),(22,7,12.0000,'USDA');
-- 23 Garbanzo
INSERT INTO alimentos_nutrientes VALUES
(23,1,164.0000,'USDA'),(23,2,8.9000,'USDA'),(23,3,27.4000,'USDA'),(23,4,2.6000,'USDA'),
(23,6,2.9000,'USDA'),(23,7,49.0000,'USDA');
-- 24 Frejol canario
INSERT INTO alimentos_nutrientes VALUES
(24,1,127.0000,'USDA'),(24,2,8.7000,'USDA'),(24,3,22.8000,'USDA'),(24,4,0.5000,'USDA'),
(24,6,2.1000,'USDA'),(24,7,46.0000,'USDA');
-- 25 Tomate
INSERT INTO alimentos_nutrientes VALUES
(25,1,18.0000,'USDA'),(25,2,0.9000,'USDA'),(25,3,3.9000,'USDA'),(25,4,0.2000,'USDA'),
(25,6,0.2700,'USDA'),(25,7,10.0000,'USDA'),(25,9,13.7000,'USDA');
-- 26 Cebolla
INSERT INTO alimentos_nutrientes VALUES
(26,1,40.0000,'USDA'),(26,2,1.1000,'USDA'),(26,3,9.3000,'USDA'),(26,4,0.1000,'USDA'),
(26,6,0.2100,'USDA'),(26,7,23.0000,'USDA');
-- 27 Mango
INSERT INTO alimentos_nutrientes VALUES
(27,1,60.0000,'USDA'),(27,2,0.8000,'USDA'),(27,3,15.0000,'USDA'),(27,4,0.4000,'USDA'),
(27,6,0.1600,'USDA'),(27,7,11.0000,'USDA'),(27,9,36.4000,'USDA');
-- 28 Papaya
INSERT INTO alimentos_nutrientes VALUES
(28,1,43.0000,'USDA'),(28,2,0.5000,'USDA'),(28,3,10.8000,'USDA'),(28,4,0.3000,'USDA'),
(28,6,0.1000,'USDA'),(28,7,20.0000,'USDA'),(28,9,60.9000,'USDA');
-- 29 Fresa
INSERT INTO alimentos_nutrientes VALUES
(29,1,32.0000,'USDA'),(29,2,0.7000,'USDA'),(29,3,7.7000,'USDA'),(29,4,0.3000,'USDA'),
(29,6,0.4100,'USDA'),(29,7,16.0000,'USDA'),(29,9,58.8000,'USDA');
-- 30 Pan integral
INSERT INTO alimentos_nutrientes VALUES
(30,1,247.0000,'USDA'),(30,2,9.3000,'USDA'),(30,3,41.0000,'USDA'),(30,4,4.2000,'USDA'),
(30,6,2.5000,'USDA'),(30,7,107.0000,'USDA');

-- =========================================================
-- 6) RECETAS (29: 7 DES, 15 ALM, 7 CEN)
-- =========================================================
INSERT INTO recetas (rec_id, rec_nombre, rec_instrucciones, rec_activo) VALUES
-- DESAYUNOS (7)
(200,'Quinua con leche y plátano','Hervir quinua con leche; servir con plátano.',1),
(204,'Avena con yogurt y fresa','Cocer avena; mezclar con yogurt; agregar fresa.',1),
(212,'Sandwich de pan integral con pollo y palta','Armar con pan, pollo deshilachado y palta.',1),
(215,'Yogurt con mango y avena','Mezclar yogurt, mango y avena hidratada.',1),
(216,'Papaya con queso fresco','Servir cubos de papaya con queso fresco.',1),
(221,'Camote con huevo revuelto','Saltear camote en cubos; añadir huevo.',1),
(229,'Avena con plátano y naranja','Cocer avena en leche; añadir plátano y gajos de naranja.',1),

-- ALMUERZOS (15)
(201,'Pollo a la plancha con ensalada','Sellar pollo; acompañar con espinaca, zanahoria y tomate.',1),
(202,'Guiso de lentejas con papa','Sofreír; añadir lentejas y papa; hervir 12–15 min.',1),
(205,'Arroz con pollo y brócoli','Saltear pollo; añadir arroz y brócoli.',1),
(210,'Garbanzo salteado con cebolla y tomate','Saltear cebolla/tomate; agregar garbanzo cocido.',1),
(211,'Sopa de verduras (brócoli, zanahoria, papa)','Hervir verduras; sazonar suave.',1),
(213,'Arroz con lentejas y plátano salteado','Mezclar arroz/lentejas; servir con plátano salteado.',1),
(214,'Bonito a la plancha con choclo','Plancha bonito; servir con maíz choclo.',1),
(219,'Hígado de pollo encebollado','Saltear hígado con cebolla; cocción completa.',1),
(220,'Guiso de frejol canario con arroz','Cocer frejol; servir con arroz.',1),
(224,'Arroz con anchoveta y espinaca','Saltear anchoveta; mezclar con arroz y espinaca.',1),
(225,'Lentejas con hígado en dados','Agregar dados de hígado a lentejas cocidas.',1),
(226,'Brócoli salteado con queso fresco','Saltear brócoli; finalizar con queso fresco en cubos.',1),
(217,'Ensalada de tomate y cebolla','Cortar y mezclar; aliño suave.',1),
(218,'Quinua salteada con brócoli','Saltear quinua cocida con brócoli.',1),
(208,'Camote al horno con queso fresco','Hornear camote; coronar con queso fresco.',1),

-- CENAS (7)
(203,'Anchoveta al horno con yuca','Hornear anchoveta 15 min; servir con yuca cocida.',1),
(206,'Puré de papa con huevo','Puré de papa; servir con huevo sancochado.',1),
(207,'Ensalada de palta y zanahoria','Mezclar palta en cubos con zanahoria rallada.',1),
(223,'Sopa de pollo con verduras','Hervir pollo con zanahoria y papa.',1),
(227,'Tazón de frutas (naranja, papaya, fresa)','Cortar frutas y mezclar.',1),
(228,'Maíz choclo con queso fresco','Servir choclo cocido con queso.',1),
(222,'Palta con tomate sobre pan integral','Untar pan; colocar palta y tomate.',1);

-- =========================================================
-- 7) RECETAS_INGREDIENTES (para esas 29 recetas)
-- =========================================================
-- DESAYUNOS
INSERT INTO recetas_ingredientes VALUES
(200,1,150.0000,'g'),(200,5,200.0000,'ml'),(200,8,100.0000,'g'),
(204,15,40.0000,'g'),(204,19,200.0000,'ml'),(204,29,80.0000,'g'),
(212,30,90.0000,'g'),(212,2,80.0000,'g'),(212,13,60.0000,'g'),
(215,19,200.0000,'ml'),(215,27,100.0000,'g'),(215,15,30.0000,'g'),
(216,28,140.0000,'g'),(216,20,40.0000,'g'),
(221,17,160.0000,'g'),(221,7,80.0000,'g'),
(229,15,40.0000,'g'),(229,8,100.0000,'g'),(229,9,80.0000,'g');

-- ALMUERZOS
INSERT INTO recetas_ingredientes VALUES
(201,2,120.0000,'g'),(201,3,60.0000,'g'),(201,4,50.0000,'g'),(201,25,60.0000,'g'),
(202,6,150.0000,'g'),(202,10,120.0000,'g'),
(205,16,150.0000,'g'),(205,2,100.0000,'g'),(205,12,80.0000,'g'),
(210,23,160.0000,'g'),(210,26,50.0000,'g'),(210,25,60.0000,'g'),
(211,12,80.0000,'g'),(211,4,60.0000,'g'),(211,10,100.0000,'g'),
(213,16,130.0000,'g'),(213,6,120.0000,'g'),(213,8,80.0000,'g'),
(214,21,140.0000,'g'),(214,18,120.0000,'g'),
(219,22,120.0000,'g'),(219,26,70.0000,'g'),
(220,24,180.0000,'g'),(220,16,120.0000,'g'),
(224,16,140.0000,'g'),(224,11,100.0000,'g'),(224,3,60.0000,'g'),
(225,6,160.0000,'g'),(225,22,80.0000,'g'),
(226,12,120.0000,'g'),(226,20,50.0000,'g'),
(217,25,100.0000,'g'),(217,26,60.0000,'g'),
(218,1,180.0000,'g'),(218,12,80.0000,'g'),
(208,17,200.0000,'g'),(208,20,40.0000,'g');

-- CENAS
INSERT INTO recetas_ingredientes VALUES
(203,11,120.0000,'g'),(203,14,150.0000,'g'),
(206,10,200.0000,'g'),(206,7,60.0000,'g'),
(207,13,70.0000,'g'),(207,4,60.0000,'g'),
(223,2,80.0000,'g'),(223,4,60.0000,'g'),(223,10,100.0000,'g'),
(227,9,80.0000,'g'),(227,28,80.0000,'g'),(227,29,80.0000,'g'),
(228,18,150.0000,'g'),(228,20,50.0000,'g'),
(222,30,90.0000,'g'),(222,13,60.0000,'g'),(222,25,60.0000,'g');

-- =========================================================
-- 8) RECETAS_COMIDAS (7 DES, 15 ALM, 7 CEN)
-- =========================================================
INSERT INTO recetas_comidas (rec_id, rc_comida) VALUES
-- DESAYUNO (7)
(200,'DESAYUNO'),
(204,'DESAYUNO'),
(212,'DESAYUNO'),
(215,'DESAYUNO'),
(216,'DESAYUNO'),
(221,'DESAYUNO'),
(229,'DESAYUNO'),

-- ALMUERZO (15)
(201,'ALMUERZO'),
(202,'ALMUERZO'),
(205,'ALMUERZO'),
(210,'ALMUERZO'),
(211,'ALMUERZO'),
(213,'ALMUERZO'),
(214,'ALMUERZO'),
(219,'ALMUERZO'),
(220,'ALMUERZO'),
(224,'ALMUERZO'),
(225,'ALMUERZO'),
(226,'ALMUERZO'),
(217,'ALMUERZO'),
(218,'ALMUERZO'),
(208,'ALMUERZO'),

-- CENA (7)
(203,'CENA'),
(206,'CENA'),
(207,'CENA'),
(223,'CENA'),
(227,'CENA'),
(228,'CENA'),
(222,'CENA');

-- =========================================================
-- 9) DISPONIBILIDAD_ALIMENTOS (SOLO Chilca - Huancayo)
-- =========================================================
INSERT INTO disponibilidad_alimentos
(ali_id, ent_id, dis_periodo, dis_disponible, dis_precio_promedio, dis_region) VALUES
-- Municipalidad de Chilca (101)
(6,101,'Q1',1,7.20,'Chilca - Huancayo'),
(6,101,'Q2',1,7.40,'Chilca - Huancayo'),
(10,101,'Q1',1,2.50,'Chilca - Huancayo'),
(10,101,'Q3',1,2.80,'Chilca - Huancayo'),
(1,101,'Q2',1,7.20,'Chilca - Huancayo'),
(11,101,'Q1',1,8.50,'Chilca - Huancayo'),

-- Centro de Salud Chilca (102)
(8,102,'Q2',1,3.20,'Chilca - Huancayo'),
(17,102,'Q3',1,2.70,'Chilca - Huancayo'),
(20,102,'Q2',1,12.00,'Chilca - Huancayo');

INSERT INTO alimentos_nutrientes (ali_id, nutri_id, an_cantidad_100, an_fuente) VALUES
(1,5,2.80,'USDA'),(2,5,0.00,'USDA'),(3,5,2.20,'USDA'),(4,5,2.80,'USDA'),(5,5,0.00,'USDA'),
(6,5,7.90,'USDA'),(7,5,0.00,'USDA'),(8,5,2.60,'USDA'),(9,5,2.40,'USDA'),(10,5,2.20,'USDA'),
(11,5,0.00,'USDA'),(12,5,2.60,'USDA'),(13,5,6.70,'USDA'),(14,5,1.80,'USDA'),(15,5,10.60,'USDA'),
(16,5,0.40,'USDA'),(17,5,3.00,'USDA'),(18,5,2.40,'USDA'),(19,5,0.00,'USDA'),(20,5,0.00,'USDA'),
(21,5,0.00,'USDA'),(22,5,0.00,'USDA'),(23,5,7.60,'USDA'),(24,5,8.70,'USDA'),(25,5,1.20,'USDA'),
(26,5,1.70,'USDA'),(27,5,1.60,'USDA'),(28,5,1.70,'USDA'),(29,5,2.00,'USDA'),(30,5,6.50,'USDA')
ON DUPLICATE KEY UPDATE
  an_cantidad_100 = VALUES(an_cantidad_100),
  an_fuente = VALUES(an_fuente);