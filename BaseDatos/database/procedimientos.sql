create
    definer = root@`%` procedure sp_antropometria_agregar(IN p_nin_id bigint unsigned, IN p_fecha date,
                                                          IN p_peso_kg decimal(5, 2), IN p_talla_cm decimal(5, 2))
BEGIN
  DECLARE v_edad_meses INT;
  DECLARE v_ant_id BIGINT UNSIGNED;
  DECLARE v_talla_cm DECIMAL(5,2);

  -- Validar que el niño existe
  IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado';
  END IF;

  -- Calcular edad en meses a la fecha de medición
  SELECT TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, p_fecha) INTO v_edad_meses
  FROM ninos n
  WHERE n.nin_id = p_nin_id;

  -- Normalizar talla: si viene en metros (<=3), convertir a centímetros
  SET v_talla_cm = CASE WHEN p_talla_cm <= 3 THEN ROUND(p_talla_cm * 100, 2) ELSE p_talla_cm END;

  -- Insertar o actualizar antropometría (evitar duplicado por fecha)
  INSERT INTO antropometrias(
    nin_id, ant_fecha, ant_edad_meses, ant_peso_kg, ant_talla_cm
  ) VALUES (
    p_nin_id, p_fecha, v_edad_meses, p_peso_kg, v_talla_cm
  )
  ON DUPLICATE KEY UPDATE
    ant_edad_meses = VALUES(ant_edad_meses),
    ant_peso_kg    = VALUES(ant_peso_kg),
    ant_talla_cm   = VALUES(ant_talla_cm),
    actualizado_en = NOW();

  -- Obtener ID de la antropometría insertada/actualizada
  SET v_ant_id = (SELECT ant_id FROM antropometrias WHERE nin_id = p_nin_id AND ant_fecha = p_fecha);

  -- Retornar la antropometría creada
  SELECT
    ant_id,
    nin_id,
    ant_fecha,
    ant_edad_meses,
    ant_peso_kg,
    ant_talla_cm,
    ant_z_imc,
    ant_z_peso_edad,
    ant_z_talla_edad,
    ROUND(ant_peso_kg / POWER(ant_talla_cm / 100, 2), 2) as imc,
    creado_en
  FROM antropometrias
  WHERE ant_id = v_ant_id;
END;

create
    definer = root@`%` procedure sp_antropometria_obtener_por_nino(IN p_nin_id bigint unsigned, IN p_limit int)
BEGIN
  DECLARE v_sql TEXT;

  SET v_sql = CONCAT(
    'SELECT ant_id, nin_id, ant_fecha, ant_edad_meses, ant_peso_kg, ant_talla_cm, ',
    'ant_z_imc, ant_z_peso_edad, ant_z_talla_edad, ',
    'ROUND(ant_peso_kg / POWER((ant_talla_cm / 100), 2), 2) as imc_calculado, ',
    'creado_en FROM antropometrias WHERE nin_id = ', p_nin_id,
    ' ORDER BY ant_fecha DESC, creado_en DESC'
  );

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_sql = CONCAT(v_sql, ' LIMIT ', p_limit);
  END IF;

  SET @sql = v_sql;
  PREPARE stmt FROM @sql;
  EXECUTE stmt;
  DEALLOCATE PREPARE stmt;
END;

create
    definer = root@`%` procedure sp_evaluar_estado_nutricional(IN p_nin_id bigint unsigned)
BEGIN
  DECLARE v_ant_id BIGINT UNSIGNED;
  DECLARE v_fecha_nac DATE;
  DECLARE v_sexo ENUM('M','F');
  DECLARE v_ant_fecha DATE;
  DECLARE v_peso_kg DECIMAL(5,2);
  DECLARE v_talla_cm DECIMAL(5,2);
  DECLARE v_edad_meses INT;
  DECLARE v_imc DECIMAL(5,2);
  DECLARE v_lms_json JSON;
  DECLARE v_l, v_m, v_s DECIMAL(8,4);
  DECLARE v_zscore DECIMAL(5,2);
  DECLARE v_percentil DECIMAL(5,2);
  DECLARE v_clasificacion VARCHAR(30);
  DECLARE v_nivel_riesgo VARCHAR(10);
  DECLARE v_lms_found BOOLEAN;
  DECLARE v_en_id BIGINT UNSIGNED;
  DECLARE v_has_fn INT DEFAULT 0;
  DECLARE v_has_fn_z INT DEFAULT 0;
  DECLARE v_has_fn_pct INT DEFAULT 0;

  -- Obtener datos del niño: priorizar columnas de ninos; si faltan, intentar desde perfil del responsable
  SELECT
    COALESCE(n.nin_fecha_nac, up.usrper_fecha_nac),
    COALESCE(n.nin_sexo, up.usrper_genero)
  INTO v_fecha_nac, v_sexo
  FROM ninos n
  LEFT JOIN usuarios u ON u.usr_id = COALESCE(n.usr_id_propietario, n.usr_id_tutor)
  LEFT JOIN usuarios_perfil up ON u.usr_id = up.usr_id
  WHERE n.nin_id = p_nin_id;

  IF v_fecha_nac IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado o sin datos de perfil';
  END IF;

  -- Obtener última antropometría
  SELECT ant_id, ant_fecha, ant_peso_kg, ant_talla_cm, ant_edad_meses
  INTO v_ant_id, v_ant_fecha, v_peso_kg, v_talla_cm, v_edad_meses
  FROM antropometrias
  WHERE nin_id = p_nin_id
  ORDER BY ant_fecha DESC, creado_en DESC
  LIMIT 1;

  IF v_ant_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No hay datos antropométricos para este niño';
  END IF;

  -- Usar edad de antropometría si existe, sino calcular
  IF v_edad_meses IS NULL THEN
    SET v_edad_meses = TIMESTAMPDIFF(MONTH, v_fecha_nac, v_ant_fecha);
  END IF;

  -- Calcular IMC
  SET v_imc = v_peso_kg / POWER((v_talla_cm / 100), 2);

  -- Verificar existencia de funciones LMS; si no existen, usar fallback simple
  SELECT COUNT(*) INTO v_has_fn
  FROM information_schema.routines
  WHERE routine_schema = DATABASE() AND routine_type = 'FUNCTION' AND routine_name = 'fn_obtener_lms_oms';

  IF v_has_fn > 0 THEN
    SET v_lms_json = fn_obtener_lms_oms(v_edad_meses, v_sexo);
    SET v_lms_found = JSON_EXTRACT(v_lms_json, '$.found');
  ELSE
    SET v_lms_found = FALSE;
  END IF;

  IF v_lms_found THEN
    -- Verificar funciones auxiliares antes de usarlas
    SELECT COUNT(*) INTO v_has_fn_z
    FROM information_schema.routines
    WHERE routine_schema = DATABASE() AND routine_type = 'FUNCTION' AND routine_name = 'fn_calcular_zscore_lms';
    SELECT COUNT(*) INTO v_has_fn_pct
    FROM information_schema.routines
    WHERE routine_schema = DATABASE() AND routine_type = 'FUNCTION' AND routine_name = 'fn_calcular_percentil';

    IF v_has_fn_z > 0 AND v_has_fn_pct > 0 THEN
      -- Extraer parámetros LMS
      SET v_l = JSON_EXTRACT(v_lms_json, '$.L');
      SET v_m = JSON_EXTRACT(v_lms_json, '$.M');
      SET v_s = JSON_EXTRACT(v_lms_json, '$.S');
      -- Calcular Z-score y percentil
      SET v_zscore = fn_calcular_zscore_lms(v_imc, v_l, v_m, v_s);
      SET v_percentil = fn_calcular_percentil(v_zscore);
    ELSE
      SET v_lms_found = FALSE;
    END IF;
  END IF;

  IF NOT v_lms_found THEN
    -- Sin datos OMS, usar clasificación simple
    SET v_zscore = NULL;
    SET v_percentil = NULL;
  END IF;

  -- Clasificar estado nutricional
  IF v_zscore IS NOT NULL THEN
    SET v_clasificacion = fn_clasificar_estado_nutricional(v_zscore);
  ELSE
    -- Fallback simple por IMC
    IF v_edad_meses < 24 THEN
      IF v_imc < 14 THEN SET v_clasificacion = 'DESNUTRICION_SEVERA';
      ELSEIF v_imc < 15 THEN SET v_clasificacion = 'DESNUTRICION';
      ELSEIF v_imc < 16 THEN SET v_clasificacion = 'RIESGO';
      ELSEIF v_imc <= 18 THEN SET v_clasificacion = 'NORMAL';
      ELSEIF v_imc <= 20 THEN SET v_clasificacion = 'SOBREPESO';
      ELSE SET v_clasificacion = 'OBESIDAD';
      END IF;
    ELSE
      IF v_imc < 13.5 THEN SET v_clasificacion = 'DESNUTRICION_SEVERA';
      ELSEIF v_imc < 14.5 THEN SET v_clasificacion = 'DESNUTRICION';
      ELSEIF v_imc < 15.5 THEN SET v_clasificacion = 'RIESGO';
      ELSEIF v_imc <= 17.5 THEN SET v_clasificacion = 'NORMAL';
      ELSEIF v_imc <= 19.5 THEN SET v_clasificacion = 'SOBREPESO';
      ELSE SET v_clasificacion = 'OBESIDAD';
      END IF;
    END IF;
  END IF;

  -- Determinar nivel de riesgo
  CASE v_clasificacion
    WHEN 'DESNUTRICION_SEVERA' THEN SET v_nivel_riesgo = 'CRITICO';
    WHEN 'DESNUTRICION' THEN SET v_nivel_riesgo = 'ALTO';
    WHEN 'RIESGO' THEN SET v_nivel_riesgo = 'MODERADO';
    WHEN 'NORMAL' THEN SET v_nivel_riesgo = 'BAJO';
    WHEN 'SOBREPESO' THEN SET v_nivel_riesgo = 'MODERADO';
    WHEN 'OBESIDAD' THEN SET v_nivel_riesgo = 'ALTO';
    ELSE SET v_nivel_riesgo = 'BAJO';
  END CASE;

  -- Insertar o actualizar evaluación nutricional (campos corregidos según tabla real)
  INSERT INTO evaluaciones_nutricionales(
    nin_id, ant_id, en_edad_meses, en_z_score_imc,
    en_clasificacion, en_nivel_riesgo
  ) VALUES (
    p_nin_id, v_ant_id, v_edad_meses, v_zscore,
    v_clasificacion, v_nivel_riesgo
  )
  ON DUPLICATE KEY UPDATE
    en_edad_meses = v_edad_meses,
    en_z_score_imc = v_zscore,
    en_clasificacion = v_clasificacion,
    en_nivel_riesgo = v_nivel_riesgo;

  SET v_en_id = LAST_INSERT_ID();
  IF v_en_id = 0 THEN
    -- Fue un UPDATE, obtener el ID existente
    SELECT en_id INTO v_en_id
    FROM evaluaciones_nutricionales
    WHERE ant_id = v_ant_id;
  END IF;

  -- Retornar resultado de la evaluación
  SELECT
    v_en_id as en_id,
    p_nin_id as nin_id,
    v_ant_id as ant_id,
    v_edad_meses as en_edad_meses,
    v_imc as imc_calculado,
    v_zscore as en_z_score_imc,
    v_percentil as percentil_calculado,
    v_clasificacion as en_clasificacion,
    v_nivel_riesgo as en_nivel_riesgo,
    v_lms_found as oms_usado,
    NOW() as evaluado_en;
END;

create
    definer = root@`%` procedure sp_login_get_hash(IN p_usuario varchar(150))
BEGIN
  DECLARE v_count INT DEFAULT 0;

  SELECT COUNT(*) INTO v_count FROM usuarios WHERE usr_usuario = p_usuario LIMIT 1;
  IF v_count = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuario no encontrado';
  END IF;

  -- Devolvemos SOLO una fila (si hubiese duplicados, es problema de datos)
  SELECT
    u.usr_id,
    u.usr_usuario,
    u.usr_correo,
    u.usr_nombre,
    u.usr_apellido,
    u.rol_id,
    u.usr_activo,
    u.usr_contrasena AS password_hash
  FROM usuarios u
  WHERE u.usr_usuario = p_usuario
  LIMIT 1;
END;
create
    definer = root@`%` procedure sp_ninos_actualizar(IN p_nin_id bigint unsigned, IN p_nin_nombres varchar(150),
                                                     IN p_ent_id smallint unsigned)
BEGIN
  -- Validar que el niño existe
  IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado';
  END IF;

  -- Actualizar datos (sin alergias)
  UPDATE ninos SET
    nin_nombres = COALESCE(p_nin_nombres, nin_nombres),
    ent_id = COALESCE(p_ent_id, ent_id),
    actualizado_en = NOW()
  WHERE nin_id = p_nin_id;

  -- Retornar el niño actualizado
  SELECT
    nin_id,
    usr_id_tutor,
    ent_id,
    nin_nombres,
    nin_fecha_nac,
    nin_sexo,
    TIMESTAMPDIFF(MONTH, nin_fecha_nac, CURDATE()) as edad_meses,
    creado_en,
    actualizado_en
  FROM ninos
  WHERE nin_id = p_nin_id;
END;
create
    definer = root@`%` procedure sp_ninos_agregar_alergia(IN p_nin_id bigint unsigned, IN p_ta_codigo varchar(20),
                                                          IN p_severidad enum ('LEVE', 'MODERADA', 'SEVERA'))
BEGIN
  DECLARE v_ta_id SMALLINT UNSIGNED;

  -- Validar que el niño existe
  IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado';
  END IF;

  -- Obtener ID del tipo de alergia
  SELECT ta_id INTO v_ta_id FROM tipos_alergias WHERE ta_codigo = p_ta_codigo AND ta_activo = 1;

  IF v_ta_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tipo de alergia no encontrado';
  END IF;

  -- Insertar o actualizar alergia
  INSERT INTO ninos_alergias(nin_id, ta_id, na_severidad, na_activo)
  VALUES (p_nin_id, v_ta_id, COALESCE(p_severidad, 'LEVE'), 1)
  ON DUPLICATE KEY UPDATE
    na_severidad = COALESCE(p_severidad, na_severidad),
    na_activo = 1;

  -- Retornar alergias del niño
  SELECT
    na.na_id,
    na.nin_id,
    ta.ta_codigo,
    ta.ta_nombre,
    ta.ta_categoria,
    na.na_severidad,
    na.creado_en
  FROM ninos_alergias na
  JOIN tipos_alergias ta ON na.ta_id = ta.ta_id
  WHERE na.nin_id = p_nin_id AND na.na_activo = 1
  ORDER BY na.creado_en DESC;
END;

create
    definer = root@`%` procedure sp_ninos_cambiar_responsable(IN p_nin_id bigint unsigned, IN p_autogestion tinyint(1),
                                                              IN p_usr_id_responsable bigint unsigned)
BEGIN
  IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id=p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='nin_id no existe';
  END IF;
  IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id_responsable) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_responsable no existe';
  END IF;

  IF p_autogestion = 1 THEN
    UPDATE ninos
       SET usr_id_propietario = p_usr_id_responsable,
           usr_id_tutor       = NULL
     WHERE nin_id = p_nin_id;
  ELSE
    UPDATE ninos
       SET usr_id_tutor       = p_usr_id_responsable,
           usr_id_propietario = NULL
     WHERE nin_id = p_nin_id;
  END IF;

  CALL sp_ninos_get(p_nin_id); -- devuelve el estado actualizado
END;

create
    definer = root@`%` procedure sp_ninos_crear(IN p_nin_nombres varchar(150), IN p_nin_fecha_nac date,
                                                IN p_nin_sexo char, IN p_ent_id int unsigned,
                                                IN p_usr_id_tutor bigint unsigned,
                                                IN p_usr_id_propietario bigint unsigned)
BEGIN
  DECLARE v_edad INT;
  DECLARE v_autogestion TINYINT(1);

  IF p_nin_nombres IS NULL OR p_nin_fecha_nac IS NULL OR p_nin_sexo IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='nombres/fecha_nac/sexo requeridos';
  END IF;

  SET v_edad = fn_edad_anios(p_nin_fecha_nac);
  IF v_edad < 0 OR v_edad > 19 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='La edad debe estar entre 0 y 19 años';
  END IF;

  IF v_edad >= 13 THEN
    SET v_autogestion = 1;
    IF p_usr_id_propietario IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_propietario requerido para >=13';
    END IF;
    IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id_propietario) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_propietario no existe';
    END IF;
  ELSE
    SET v_autogestion = 0;
    IF p_usr_id_tutor IS NULL THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_tutor requerido para <13';
    END IF;
    IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id_tutor) THEN
      SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id_tutor no existe';
    END IF;
  END IF;

  INSERT INTO ninos(
    usr_id_tutor, usr_id_propietario, ent_id,
    nin_nombres, nin_fecha_nac, nin_sexo
  ) VALUES (
    CASE WHEN v_autogestion=0 THEN p_usr_id_tutor ELSE NULL END,
    CASE WHEN v_autogestion=1 THEN p_usr_id_propietario ELSE NULL END,
    p_ent_id, p_nin_nombres, p_nin_fecha_nac, p_nin_sexo
  );

  SELECT LAST_INSERT_ID() AS nin_id,
         v_edad AS edad_anios,
         v_autogestion AS nin_autogestion,
         'OK' AS msg;
END;

create
    definer = root@`%` procedure sp_ninos_get(IN p_nin_id bigint unsigned)
BEGIN
  SELECT
    n.nin_id, n.ent_id,
    n.nin_nombres, n.nin_fecha_nac, n.nin_sexo,
    n.usr_id_tutor, n.usr_id_propietario,
    (n.usr_id_propietario IS NOT NULL) AS nin_autogestion,
    COALESCE(n.usr_id_propietario, n.usr_id_tutor) AS usr_id_responsable,
    u.usr_nombre, u.usr_apellido, u.usr_dni, u.usr_correo,
    up.usrper_telefono    AS telefono_resp,
    up.usrper_direccion   AS direccion_resp,
    up.usrper_genero      AS genero_resp,
    up.usrper_idioma      AS idioma_resp
  FROM ninos n
  JOIN usuarios u             ON u.usr_id = COALESCE(n.usr_id_propietario, n.usr_id_tutor)
  LEFT JOIN usuarios_perfil up ON up.usr_id = u.usr_id
  WHERE n.nin_id = p_nin_id;
END;

create
    definer = root@`%` procedure sp_ninos_obtener_alergias(IN p_nin_id bigint unsigned)
BEGIN
  SELECT
    na.na_id,
    na.nin_id,
    ta.ta_codigo,
    ta.ta_nombre,
    ta.ta_categoria,
    na.na_severidad,
    na.creado_en
  FROM ninos_alergias na
  JOIN tipos_alergias ta ON na.ta_id = ta.ta_id
  WHERE na.nin_id = p_nin_id AND na.na_activo = 1
  ORDER BY ta.ta_categoria, ta.ta_nombre;
END;

create
    definer = root@`%` procedure sp_ninos_obtener_por_id(IN p_nin_id bigint unsigned)
BEGIN
  SELECT
    n.nin_id,
    n.usr_id_tutor,
    n.ent_id,
    CONCAT(u.usr_nombre, ' ', u.usr_apellido) as nin_nombres, -- Desde usuarios
    up.usrper_fecha_nac as nin_fecha_nac,
    up.usrper_genero as nin_sexo,
    TIMESTAMPDIFF(MONTH, up.usrper_fecha_nac, CURDATE()) as edad_meses,
    n.creado_en,
    n.actualizado_en,
    u.usr_dni as tutor_dni,
    u.usr_correo as tutor_correo,
    up.usrper_telefono as tutor_telefono
  FROM ninos n
  JOIN usuarios u ON n.usr_id_tutor = u.usr_id
  LEFT JOIN usuarios_perfil up ON u.usr_id = up.usr_id
  WHERE n.nin_id = p_nin_id;

  IF ROW_COUNT() = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Niño no encontrado';
  END IF;
END;

create
    definer = root@`%` procedure sp_ninos_obtener_por_tutor(IN p_usr_id_tutor bigint unsigned)
BEGIN
  SELECT
    n.nin_id,
    n.usr_id_tutor,
    n.ent_id,
    CONCAT(u.usr_nombre, ' ', u.usr_apellido) as nin_nombres, -- Desde usuarios
    up.usrper_fecha_nac as nin_fecha_nac,
    up.usrper_genero as nin_sexo,
    TIMESTAMPDIFF(MONTH, up.usrper_fecha_nac, CURDATE()) as edad_meses,
    n.creado_en,
    n.actualizado_en
  FROM ninos n
  JOIN usuarios u ON n.usr_id_tutor = u.usr_id
  LEFT JOIN usuarios_perfil up ON u.usr_id = up.usr_id
  WHERE n.usr_id_tutor = p_usr_id_tutor AND u.usr_activo = 1
  ORDER BY n.creado_en DESC;
END;

create
    definer = root@`%` procedure sp_registrar_autogestionado(IN p_nombres varchar(150), IN p_apellidos varchar(150),
                                                             IN p_usuario varchar(150), IN p_correo varchar(190),
                                                             IN p_contrasena_hash varchar(255),
                                                             IN p_usr_dni varchar(12), IN p_avatar_url varchar(255),
                                                             IN p_telefono varchar(20), IN p_direccion varchar(180),
                                                             IN p_genero_usr char, IN p_idioma varchar(10),
                                                             IN p_fecha_nac_nino date, IN p_sexo_nino char,
                                                             IN p_ent_id int unsigned)
BEGIN
  DECLARE v_rol_id SMALLINT UNSIGNED;
  DECLARE v_usr_id BIGINT UNSIGNED;
  DECLARE v_nin_id BIGINT UNSIGNED;

  -- Rol base
  SELECT rol_id INTO v_rol_id
  FROM roles
  WHERE rol_codigo IN ('ADOLESCENTE','USR','USUARIO')
  ORDER BY rol_id LIMIT 1;

  IF v_rol_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Configura un rol base (ADOLESCENTE/USUARIO)';
  END IF;

  INSERT INTO usuarios(usr_dni, usr_correo, usr_contrasena, usr_nombre, usr_apellido, usr_usuario, rol_id, usr_activo)
  VALUES (p_usr_dni, p_correo, p_contrasena_hash, p_nombres, p_apellidos, p_usuario, v_rol_id, 1);
  SET v_usr_id = LAST_INSERT_ID();

  CALL sp_usuarios_perfil_guardar(
    v_usr_id, p_usr_dni, p_nombres, p_apellidos,
    p_avatar_url, p_telefono, p_direccion, p_genero_usr, NULL, p_idioma
  );

  CALL sp_ninos_crear(CONCAT(p_nombres,' ',p_apellidos), p_fecha_nac_nino, p_sexo_nino,
                      p_ent_id, NULL, v_usr_id);

  -- Devuelve todo
  SELECT v_usr_id AS usr_id, (SELECT LAST_INSERT_ID()) AS nin_id, 'OK' AS msg;
END;

create
    definer = root@`%` procedure sp_registrar_menor_con_tutor(IN p_usr_id_tutor bigint unsigned,
                                                              IN p_nin_nombres varchar(150), IN p_fecha_nac date,
                                                              IN p_sexo_nino char, IN p_ent_id int unsigned)
BEGIN
  IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id_tutor) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Tutor no existe';
  END IF;

  CALL sp_ninos_crear(p_nin_nombres, p_fecha_nac, p_sexo_nino, p_ent_id, p_usr_id_tutor, NULL);
END;

create
    definer = root@`%` procedure sp_roles_insertar(IN p_rol_codigo varchar(32), IN p_rol_nombre varchar(80))
BEGIN
  DECLARE v_id SMALLINT UNSIGNED;

  -- ¿ya existe por código o nombre?
  SELECT rol_id INTO v_id
  FROM roles
  WHERE rol_codigo = p_rol_codigo OR rol_nombre = p_rol_nombre
  LIMIT 1;

  IF v_id IS NULL THEN
    INSERT INTO roles(rol_codigo, rol_nombre)
    VALUES (p_rol_codigo, p_rol_nombre);
    SET v_id = LAST_INSERT_ID();
  END IF;

  -- Resultado uniforme
  SELECT v_id AS rol_id, 'OK' AS msg;
END;

create
    definer = root@`%` procedure sp_usuarios_perfil_get(IN p_usr_id bigint unsigned)
BEGIN
  SELECT
    u.usr_id, u.usr_nombre, u.usr_apellido, u.usr_dni, u.usr_correo,
    up.usrper_avatar_url  AS avatar,
    up.usrper_telefono    AS telefono,
    up.usrper_direccion   AS direccion,
    up.usrper_genero      AS genero,
    up.usrper_fecha_nac   AS fecha_nac,
    up.usrper_idioma      AS idioma
  FROM usuarios u
  LEFT JOIN usuarios_perfil up ON up.usr_id = u.usr_id
  WHERE u.usr_id = p_usr_id;
END;

create
    definer = root@`%` procedure sp_usuarios_perfil_guardar(IN p_usr_id bigint unsigned, IN p_usr_dni varchar(12),
                                                            IN p_nombres varchar(150), IN p_apellidos varchar(150),
                                                            IN p_avatar_url mediumtext, IN p_telefono varchar(20),
                                                            IN p_direccion varchar(180), IN p_genero char,
                                                            IN p_fecha_nac date, IN p_idioma varchar(10))
BEGIN
  IF p_usr_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='usr_id requerido';
  END IF;

  IF NOT EXISTS(SELECT 1 FROM usuarios WHERE usr_id=p_usr_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='El usuario no existe';
  END IF;

  -- Actualiza tabla usuarios (DNI, nombres y apellidos si vienen)
  UPDATE usuarios
     SET usr_dni     = COALESCE(NULLIF(p_usr_dni,''), usr_dni),
         usr_nombre  = COALESCE(NULLIF(p_nombres,''), usr_nombre),
         usr_apellido= COALESCE(NULLIF(p_apellidos,''), usr_apellido)
   WHERE usr_id = p_usr_id;

  -- Upsert en usuarios_perfil
  IF EXISTS(SELECT 1 FROM usuarios_perfil WHERE usr_id=p_usr_id) THEN
    UPDATE usuarios_perfil
       SET usrper_avatar_url = COALESCE(p_avatar_url, usrper_avatar_url),
           usrper_telefono   = COALESCE(p_telefono, usrper_telefono),
           usrper_direccion  = COALESCE(p_direccion, usrper_direccion),
           usrper_genero     = COALESCE(p_genero, usrper_genero),
           usrper_fecha_nac  = COALESCE(p_fecha_nac, usrper_fecha_nac),
           usrper_idioma     = COALESCE(p_idioma, usrper_idioma)
     WHERE usr_id = p_usr_id;
  ELSE
    INSERT INTO usuarios_perfil(
      usr_id, usrper_avatar_url, usrper_telefono, usrper_direccion,
      usrper_genero, usrper_fecha_nac, usrper_idioma
    ) VALUES(
      p_usr_id, p_avatar_url, p_telefono, p_direccion,
      p_genero, p_fecha_nac, COALESCE(p_idioma,'es-PE')
    );
  END IF;

  -- Devuelve perfil completo
  SELECT
    u.usr_id, u.usr_nombre, u.usr_apellido, u.usr_dni, u.usr_correo,
    up.usrper_avatar_url  AS avatar,
    up.usrper_telefono    AS telefono,
    up.usrper_direccion   AS direccion,
    up.usrper_genero      AS genero,
    up.usrper_fecha_nac   AS fecha_nac,
    up.usrper_idioma      AS idioma
  FROM usuarios u
  LEFT JOIN usuarios_perfil up ON up.usr_id = u.usr_id
  WHERE u.usr_id = p_usr_id;
END;

create
    definer = root@`%` procedure sp_usuarios_registrar(IN p_nombres varchar(150), IN p_apellidos varchar(150),
                                                       IN p_usuario varchar(150), IN p_correo varchar(190),
                                                       IN p_contrasena_hash varchar(255), IN p_rol_nombre varchar(80))
BEGIN
  DECLARE v_rol_id SMALLINT UNSIGNED;
  DECLARE v_usr_id BIGINT UNSIGNED;
  DECLARE v_exists INT DEFAULT 0;

  -- rol por nombre
  SELECT rol_id INTO v_rol_id FROM roles WHERE rol_nombre = p_rol_nombre LIMIT 1;
  IF v_rol_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El rol no existe: use sp_roles_insertar primero';
  END IF;

  -- duplicados
  SELECT COUNT(*) INTO v_exists FROM usuarios WHERE usr_correo = p_correo;
  IF v_exists > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Correo ya registrado';
  END IF;

  SELECT COUNT(*) INTO v_exists FROM usuarios WHERE usr_usuario = p_usuario;
  IF v_exists > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuario ya registrado';
  END IF;

  -- inserción
  INSERT INTO usuarios(
    usr_dni, usr_correo, usr_contrasena, usr_nombre, usr_apellido, usr_usuario,
    rol_id, usr_activo
  ) VALUES (
    NULL, p_correo, p_contrasena_hash, p_nombres, p_apellidos, p_usuario,
    v_rol_id, 1
  );

  SET v_usr_id = LAST_INSERT_ID();

  -- resultado
  SELECT v_usr_id AS usr_id, 'OK' AS msg;
END;



