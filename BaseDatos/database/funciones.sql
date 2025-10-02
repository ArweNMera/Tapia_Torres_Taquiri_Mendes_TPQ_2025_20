create
    definer = root@`%` function fn_calcular_percentil(p_zscore decimal(5, 2)) returns decimal(5, 2) deterministic
BEGIN
  DECLARE v_percentil DECIMAL(8,4);
  SET v_percentil = 50 + (p_zscore * 15);
  SET v_percentil = GREATEST(0.1, LEAST(99.9, v_percentil));
  RETURN ROUND(v_percentil, 1);
END;

create
    definer = root@`%` function fn_calcular_zscore_lms(p_valor decimal(8, 4), p_l decimal(8, 4), p_m decimal(8, 4),
                                                       p_s decimal(8, 4)) returns decimal(5, 2) deterministic
BEGIN
  DECLARE v_zscore DECIMAL(8,4);
  IF ABS(p_l) < 0.0001 THEN
    SET v_zscore = LN(p_valor / p_m) / p_s;
  ELSE
    SET v_zscore = (POWER(p_valor / p_m, p_l) - 1) / (p_l * p_s);
  END IF;
  SET v_zscore = GREATEST(-5.0, LEAST(5.0, v_zscore));
  RETURN ROUND(v_zscore, 2);
END;

create
    definer = root@`%` function fn_clasificar_estado_nutricional(p_zscore decimal(5, 2)) returns varchar(20)
    deterministic
BEGIN
  IF p_zscore < -3.0 THEN
    RETURN 'DESNUTRICION_SEVERA';
  ELSEIF p_zscore < -2.0 THEN
    RETURN 'DESNUTRICION';
  ELSEIF p_zscore < -1.0 THEN
    RETURN 'RIESGO';
  ELSEIF p_zscore <= 1.0 THEN
    RETURN 'NORMAL';
  ELSEIF p_zscore <= 2.0 THEN
    RETURN 'SOBREPESO';
  ELSE
    RETURN 'OBESIDAD';
  END IF;
END;

create
    definer = root@`%` function fn_edad_anios(p_fecha_nac date) returns int deterministic
BEGIN
  RETURN TIMESTAMPDIFF(YEAR, p_fecha_nac, CURDATE());
END;

create
    definer = root@`%` function fn_edad_meses(p_fecha_nac date) returns int deterministic
BEGIN
  RETURN TIMESTAMPDIFF(MONTH, p_fecha_nac, CURDATE());
END;

create
    definer = root@`%` function fn_obtener_lms_oms(p_edad_meses smallint unsigned, p_sexo enum ('M', 'F')) returns json
    deterministic
    reads sql data
BEGIN
  DECLARE v_version ENUM('OMS_2006','OMS_2007');
  DECLARE v_l, v_m, v_s DECIMAL(8,4);
  DECLARE v_found BOOLEAN DEFAULT FALSE;

  -- Determinar versión según edad
  IF p_edad_meses < 60 THEN
    SET v_version = 'OMS_2006';
  ELSE
    SET v_version = 'OMS_2007';
  END IF;

  -- Buscar parámetros LMS más cercanos (evita overflow UNSIGNED)
  SELECT L, M, S INTO v_l, v_m, v_s
  FROM oms_bmi_lms
  WHERE version = v_version
    AND sexo = p_sexo
  ORDER BY ABS(CAST(edad_meses AS SIGNED) - CAST(p_edad_meses AS SIGNED))
  LIMIT 1;

  IF v_l IS NOT NULL THEN
    SET v_found = TRUE;
  END IF;

  RETURN JSON_OBJECT(
    'found', v_found,
    'version', v_version,
    'L', v_l,
    'M', v_m,
    'S', v_s
  );
END;

