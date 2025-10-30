CREATE OR REPLACE VIEW v_receta_nutrientes AS
SELECT
  r.rec_id,
  r.rec_nombre,
  COALESCE(SUM(CASE WHEN an.nutri_id = 1  THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS kcal,
  COALESCE(SUM(CASE WHEN an.nutri_id = 2  THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS proteina_g,
  COALESCE(SUM(CASE WHEN an.nutri_id = 3  THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS carbohidratos_g,
  COALESCE(SUM(CASE WHEN an.nutri_id = 4  THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS grasas_g,
  COALESCE(SUM(CASE WHEN an.nutri_id = 5  THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS fibra_g,
  COALESCE(SUM(CASE WHEN an.nutri_id = 6  THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS hierro_mg,
  COALESCE(SUM(CASE WHEN an.nutri_id = 7  THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS calcio_mg,
  COALESCE(SUM(CASE WHEN an.nutri_id = 8  THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS vitamina_a_ug,
  COALESCE(SUM(CASE WHEN an.nutri_id = 9  THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS vitamina_c_mg,
  COALESCE(SUM(CASE WHEN an.nutri_id = 10 THEN an.an_cantidad_100 * ri.ri_cantidad/100 END),0) AS zinc_mg
FROM recetas r
JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id
GROUP BY r.rec_id, r.rec_nombre;

CREATE OR REPLACE VIEW v_precio_alimento_chilca AS
SELECT
  ali_id,
  AVG(dis_precio_promedio) AS precio_promedio_soles
FROM disponibilidad_alimentos
WHERE ent_id IN (101,102)
  AND dis_disponible = 1
  AND dis_precio_promedio IS NOT NULL
GROUP BY ali_id;

CREATE OR REPLACE VIEW v_receta_costo_chilca AS
SELECT
  r.rec_id,
  r.rec_nombre,
  ROUND(SUM(
    (COALESCE(p.precio_promedio_soles,0) / 1000.0) *
    CASE
      WHEN a.ali_unidad IN ('g','ml') THEN ri.ri_cantidad
      ELSE ri.ri_cantidad
    END
  ), 2) AS costo_soles_aprox
FROM recetas r
JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
JOIN alimentos a ON a.ali_id = ri.ali_id
LEFT JOIN v_precio_alimento_chilca p ON p.ali_id = ri.ali_id
GROUP BY r.rec_id, r.rec_nombre;

CREATE OR REPLACE VIEW v_recetas_chilca AS
SELECT
  rc.rc_comida,
  r.rec_id,
  r.rec_nombre,
  vn.kcal, vn.proteina_g, vn.carbohidratos_g, vn.grasas_g,
  vn.fibra_g, vn.hierro_mg, vn.calcio_mg, vn.vitamina_a_ug, vn.vitamina_c_mg, vn.zinc_mg,
  COALESCE(vc.costo_soles_aprox, 0) AS costo_soles_aprox
FROM recetas r
JOIN recetas_comidas rc      ON rc.rec_id = r.rec_id
JOIN v_receta_nutrientes vn  ON vn.rec_id = r.rec_id
LEFT JOIN v_receta_costo_chilca vc ON vc.rec_id = r.rec_id;

CREATE OR REPLACE VIEW v_estados_clasificacion AS
SELECT 'DESNUTRICION_SEVERA' AS en_clasificacion UNION ALL
SELECT 'DESNUTRICION'        UNION ALL
SELECT 'RIESGO'              UNION ALL
SELECT 'NORMAL'              UNION ALL
SELECT 'SOBREPESO'           UNION ALL
SELECT 'OBESIDAD';

CREATE OR REPLACE VIEW v_recetas_scores_por_estado AS
SELECT
  e.en_clasificacion,
  r.rc_comida,
  r.rec_id,
  r.rec_nombre,
  r.kcal, r.proteina_g, r.carbohidratos_g, r.grasas_g,
  r.fibra_g, r.hierro_mg, r.calcio_mg, r.vitamina_a_ug, r.vitamina_c_mg, r.zinc_mg,
  r.costo_soles_aprox,
  CASE
    WHEN e.en_clasificacion IN ('DESNUTRICION_SEVERA','DESNUTRICION') THEN
      (r.proteina_g*2.0 + r.hierro_mg*1.5 + LEAST(r.vitamina_c_mg,30)*0.05 + r.kcal*0.02)
      - (r.costo_soles_aprox*0.30)
    WHEN e.en_clasificacion = 'RIESGO' THEN
      (r.proteina_g*1.5 + r.hierro_mg*1.0 + r.kcal*0.015 + r.fibra_g*0.5)
      - (r.costo_soles_aprox*0.20)
    WHEN e.en_clasificacion = 'NORMAL' THEN
      (r.proteina_g*1.0 + r.fibra_g*0.5 + r.vitamina_c_mg*0.05 + r.zinc_mg*0.2)
      - (GREATEST(ABS(r.kcal-450),0)*0.01)
      - (r.costo_soles_aprox*0.15)
    WHEN e.en_clasificacion = 'SOBREPESO' THEN
      (r.fibra_g*1.0 + r.proteina_g*0.8)
      - (GREATEST(r.kcal-500,0)*0.02)
      - (r.grasas_g*0.5)
      - (r.costo_soles_aprox*0.10)
    WHEN e.en_clasificacion = 'OBESIDAD' THEN
      (r.fibra_g*1.2 + r.proteina_g*0.6)
      - (GREATEST(r.kcal-450,0)*0.03)
      - (r.grasas_g*0.7)
      - (r.costo_soles_aprox*0.10)
    ELSE 0
  END AS score
FROM v_estados_clasificacion e
CROSS JOIN v_recetas_chilca r;

CREATE OR REPLACE VIEW v_nino_estado_actual AS
SELECT
  e.nin_id,
  n.nin_nombres,
  n.nin_sexo,
  n.ent_id,
  e.en_id,
  e.ant_id,
  e.en_edad_meses,
  e.en_imc,
  e.en_z_score_imc,
  e.en_percentil_imc,
  e.en_clasificacion,
  e.en_nivel_riesgo,
  e.en_observaciones,
  e.creado_en AS evaluado_en
FROM (
  SELECT en.*,
         ROW_NUMBER() OVER (PARTITION BY en.nin_id ORDER BY en.creado_en DESC, en.en_id DESC) AS rn
  FROM evaluaciones_nutricionales en
) e
JOIN ninos n ON n.nin_id = e.nin_id
WHERE e.rn = 1;

CREATE OR REPLACE VIEW v_recetas_scores_por_nino AS
SELECT
  na.nin_id,
  na.nin_nombres,
  na.en_clasificacion,
  s.rc_comida,
  s.rec_id,
  s.rec_nombre,
  s.kcal, s.proteina_g, s.carbohidratos_g, s.grasas_g,
  s.fibra_g, s.hierro_mg, s.calcio_mg, s.vitamina_a_ug, s.vitamina_c_mg, s.zinc_mg,
  s.costo_soles_aprox,
  s.score
FROM v_nino_estado_actual na
JOIN v_recetas_scores_por_estado s
  ON s.en_clasificacion = na.en_clasificacion;


CREATE OR REPLACE VIEW v_top_recetas_por_nino AS
SELECT
  s.nin_id, s.nin_nombres, s.en_clasificacion, s.rc_comida,
  s.rec_id, s.rec_nombre,
  s.kcal, s.proteina_g, s.hierro_mg, s.fibra_g,
  s.costo_soles_aprox, s.score,
  ROW_NUMBER() OVER (PARTITION BY s.nin_id, s.rc_comida ORDER BY s.score DESC) AS rn
FROM v_recetas_scores_por_nino s;
