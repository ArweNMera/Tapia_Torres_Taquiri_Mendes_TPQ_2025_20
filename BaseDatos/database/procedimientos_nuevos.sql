DELIMITER $$

CREATE PROCEDURE sp_perfil_nutricional_vigente(IN p_nin_id BIGINT UNSIGNED)
BEGIN
  SELECT *
  FROM perfil_nutricional_nino
  WHERE nin_id = p_nin_id
    AND pnn_vigente = TRUE
  ORDER BY creado_en DESC
  LIMIT 1;
END$$

CREATE PROCEDURE sp_menus_crear(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_generado_por ENUM('IA','NUTRICIONISTA'),
    IN p_inicio DATE,
    IN p_fin DATE
)
BEGIN
  INSERT INTO menus (nin_id, men_generado_por, men_inicio, men_fin, men_estado)
  VALUES (p_nin_id, p_generado_por, p_inicio, p_fin, 'BORRADOR');

  SELECT LAST_INSERT_ID() AS men_id;
END$$

CREATE PROCEDURE sp_menus_items_agregar(
    IN p_men_id BIGINT UNSIGNED,
    IN p_dia_idx TINYINT UNSIGNED,
    IN p_comida ENUM('DESAYUNO','ALMUERZO','CENA','REFACCION'),
    IN p_rec_id INT UNSIGNED,
    IN p_kcal INT
)
BEGIN
  INSERT INTO menus_items (men_id, mei_dia_idx, mei_comida, rec_id, mei_kcal)
  VALUES (p_men_id, p_dia_idx, p_comida, p_rec_id, p_kcal);

  SELECT LAST_INSERT_ID() AS mei_id;
END$$

CREATE PROCEDURE sp_menus_actualizar_kcal(
    IN p_men_id BIGINT UNSIGNED,
    IN p_kcal_total INT
)
BEGIN
  UPDATE menus
     SET men_kcal_total = p_kcal_total
   WHERE men_id = p_men_id;

  SELECT ROW_COUNT() AS affected_rows;
END$$

CREATE PROCEDURE sp_ninos_datos_basicos(IN p_nin_id BIGINT UNSIGNED)
BEGIN
  SELECT
    n.nin_id,
    n.nin_nombres,
    n.nin_fecha_nac,
    n.nin_sexo,
    n.ent_id,
    TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE()) AS edad_meses,
    e.ent_nombre,
    e.ent_distrito
  FROM ninos n
  LEFT JOIN entidades e ON e.ent_id = n.ent_id
  WHERE n.nin_id = p_nin_id;
END$$

CREATE PROCEDURE sp_recetas_ingredientes(IN p_rec_id INT UNSIGNED)
BEGIN
  SELECT
    a.ali_nombre,
    ri.ri_cantidad AS cantidad,
    ri.ri_unidad   AS unidad
  FROM recetas_ingredientes ri
  INNER JOIN alimentos a ON a.ali_id = ri.ali_id
  WHERE ri.rec_id = p_rec_id
  ORDER BY ri.ali_id;
END$$

CREATE PROCEDURE sp_menus_listar(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_estado ENUM('BORRADOR','APROBADO','ARCHIVADO'),
    IN p_limit INT
)
BEGIN
  DECLARE v_limit INT DEFAULT 10;

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 100);
  END IF;

  SELECT *
    FROM menus
   WHERE nin_id = p_nin_id
     AND (p_estado IS NULL OR p_estado = '' OR men_estado = p_estado)
   ORDER BY men_inicio DESC
   LIMIT v_limit;
END$$

CREATE PROCEDURE sp_menus_detalle(IN p_men_id BIGINT UNSIGNED)
BEGIN
  SELECT m.*, n.nin_nombres
    FROM menus m
    JOIN ninos n ON n.nin_id = m.nin_id
   WHERE m.men_id = p_men_id;
END$$

CREATE PROCEDURE sp_menus_items_listar(IN p_men_id BIGINT UNSIGNED)
BEGIN
  SELECT
    mi.*,
    r.rec_nombre,
    r.rec_instrucciones
  FROM menus_items mi
  JOIN recetas r ON r.rec_id = mi.rec_id
  WHERE mi.men_id = p_men_id
  ORDER BY mi.mei_dia_idx,
           FIELD(mi.mei_comida,'DESAYUNO','ALMUERZO','CENA','REFACCION');
END$$

CREATE PROCEDURE sp_menus_cambiar_estado(
    IN p_men_id BIGINT UNSIGNED,
    IN p_estado ENUM('BORRADOR','APROBADO','ARCHIVADO')
)
BEGIN
  UPDATE menus
     SET men_estado = p_estado
   WHERE men_id = p_men_id;

  SELECT ROW_COUNT() AS affected_rows;
END$$

CREATE PROCEDURE sp_recetas_disponibles(
    IN p_ent_id BIGINT UNSIGNED,
    IN p_limit INT
)
BEGIN
  DECLARE v_limit INT DEFAULT 100;

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 200);
  END IF;

  SELECT
    r.rec_id,
    r.rec_nombre,
    r.rec_instrucciones,
    GROUP_CONCAT(DISTINCT rc.rc_comida) AS tipos_comida,
    COALESCE(SUM(an.an_cantidad_100 * ri.ri_cantidad / 100), 0) AS calorias_aprox
  FROM recetas r
  LEFT JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
  LEFT JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
  LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id AND an.nutri_id = 1
  WHERE r.rec_activo = 1
  GROUP BY r.rec_id, r.rec_nombre, r.rec_instrucciones
  LIMIT v_limit;
END$$

CREATE PROCEDURE sp_recetas_aleatorias(IN p_limit INT)
BEGIN
  DECLARE v_limit INT DEFAULT 21;

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 50);
  END IF;

  SELECT
    r.rec_id,
    r.rec_nombre,
    rc.rc_comida
  FROM recetas r
  JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
  WHERE r.rec_activo = 1
  ORDER BY RAND()
  LIMIT v_limit;
END$$

CREATE PROCEDURE sp_recetas_detalle(IN p_rec_id INT UNSIGNED)
BEGIN
  SELECT
    r.rec_id,
    r.rec_nombre,
    r.rec_instrucciones,
    r.rec_activo
  FROM recetas r
  WHERE r.rec_id = p_rec_id;
END$$

CREATE PROCEDURE sp_recetas_nutrientes(IN p_rec_id INT UNSIGNED)
BEGIN
  SELECT
    SUM(CASE WHEN an.nutri_id = 1 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS kcal,
    SUM(CASE WHEN an.nutri_id = 2 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS proteina_g,
    SUM(CASE WHEN an.nutri_id = 3 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS carbohidratos_g,
    SUM(CASE WHEN an.nutri_id = 4 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS grasa_g,
    SUM(CASE WHEN an.nutri_id = 5 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS fibra_g,
    SUM(CASE WHEN an.nutri_id = 6 THEN an.an_cantidad_100 * ri.ri_cantidad / 100 ELSE 0 END) AS hierro_mg
  FROM recetas_ingredientes ri
  LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id
  WHERE ri.rec_id = p_rec_id;
END$$

CREATE PROCEDURE sp_preferencias_listar(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_tipo_comida ENUM('DESAYUNO','ALMUERZO','CENA','SNACKS')
)
BEGIN
  IF p_tipo_comida IS NULL OR TRIM(p_tipo_comida) = '' THEN
    SELECT npc_id,
           npc_tipo_comida,
           npc_preferencia,
           creado_en
      FROM ninos_preferencias_comidas
     WHERE nin_id = p_nin_id
       AND npc_activo = TRUE
     ORDER BY npc_tipo_comida, creado_en ASC;
  ELSE
    SELECT npc_id,
           npc_preferencia,
           creado_en
      FROM ninos_preferencias_comidas
     WHERE nin_id = p_nin_id
       AND npc_tipo_comida = p_tipo_comida
       AND npc_activo = TRUE
     ORDER BY creado_en ASC;
  END IF;
END$$

CREATE PROCEDURE sp_preferencias_desactivar(IN p_npc_id BIGINT UNSIGNED)
BEGIN
  UPDATE ninos_preferencias_comidas
     SET npc_activo = FALSE
   WHERE npc_id = p_npc_id;

  SELECT ROW_COUNT() AS affected_rows;
END$$

CREATE PROCEDURE sp_preferencias_resumen(IN p_usr_id BIGINT UNSIGNED)
BEGIN
  SELECT
    n.nin_id,
    n.nin_nombres,
    COUNT(CASE WHEN npc.npc_activo = TRUE THEN npc.npc_id END) > 0 AS tiene_preferencias,
    COUNT(CASE WHEN npc.npc_activo = TRUE THEN npc.npc_id END) AS total_preferencias,
    MAX(npc.actualizado_en) AS ultima_actualizacion
  FROM ninos n
  LEFT JOIN ninos_preferencias_comidas npc
         ON npc.nin_id = n.nin_id AND npc.npc_activo = TRUE
  WHERE n.usr_id_propietario = p_usr_id OR n.usr_id_tutor = p_usr_id
  GROUP BY n.nin_id, n.nin_nombres
  ORDER BY n.nin_nombres;
END$$

CREATE PROCEDURE sp_usuarios_anonimizar(
    IN p_usr_id BIGINT UNSIGNED,
    IN p_usuario_temp VARCHAR(255),
    IN p_correo_temp VARCHAR(255),
    IN p_password_hash VARCHAR(255),
    IN p_telefono VARCHAR(20)
)
BEGIN
  UPDATE usuarios
     SET usr_correo = p_correo_temp,
         usr_contrasena = p_password_hash,
         usr_nombre = 'Cuenta eliminada',
         usr_apellido = 'NutriFamily',
         usr_usuario = p_usuario_temp,
         usr_activo = 0,
         eliminado_en = NOW()
   WHERE usr_id = p_usr_id;

  UPDATE usuarios_perfil
     SET usrper_avatar_url = NULL,
         usrper_telefono   = p_telefono,
         usrper_direccion  = NULL,
         usrper_genero     = NULL,
         usrper_fecha_nac  = NULL,
         usrper_idioma     = 'es-PE',
         eliminado_en      = NOW()
   WHERE usr_id = p_usr_id;

  SELECT ROW_COUNT() AS affected_rows;
END$$

CREATE PROCEDURE sp_roles_nombre_por_id(IN p_rol_id INT)
BEGIN
  SELECT rol_nombre
    FROM roles
   WHERE rol_id = p_rol_id
   LIMIT 1;
END$$

CREATE PROCEDURE sp_evaluaciones_recomendaciones(
    IN p_en_id BIGINT UNSIGNED,
    IN p_limit INT
)
BEGIN
  DECLARE v_limit INT DEFAULT 5;

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 10);
  END IF;

  SELECT
    rt.rt_codigo,
    rt.rt_titulo,
    rt.rt_descripcion
  FROM evaluaciones_recomendaciones er
  JOIN recomendaciones_tipos rt ON rt.rt_id = er.rt_id
  WHERE er.en_id = p_en_id
  ORDER BY rt.rt_prioridad ASC, rt.rt_id ASC
  LIMIT v_limit;
END$$

CREATE PROCEDURE sp_ninos_alergia_eliminar(
    IN p_na_id BIGINT UNSIGNED,
    IN p_nin_id BIGINT UNSIGNED
)
BEGIN
  IF p_nin_id IS NULL OR p_nin_id = 0 THEN
    DELETE FROM ninos_alergias WHERE na_id = p_na_id;
  ELSE
    DELETE FROM ninos_alergias WHERE na_id = p_na_id AND nin_id = p_nin_id;
  END IF;

  SELECT ROW_COUNT() AS affected_rows;
END$$

-- Si NO tienes aún la tabla ninos_comidas_favoritas, créala primero:

-- CREATE TABLE ninos_comidas_favoritas (
--   ncf_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
--   nin_id BIGINT UNSIGNED NOT NULL,
--   rec_id INT UNSIGNED NOT NULL,
--   ncf_notas VARCHAR(255) NULL,
--   creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
--   actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
--   UNIQUE KEY uk_ncf_nino_receta (nin_id, rec_id),
--   CONSTRAINT fk_ncf_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
--   CONSTRAINT fk_ncf_receta FOREIGN KEY (rec_id) REFERENCES recetas(rec_id) ON DELETE CASCADE
-- ) ENGINE=InnoDB;

CREATE PROCEDURE sp_comidas_favoritas_listar(IN p_nin_id BIGINT UNSIGNED)
BEGIN
  SELECT
    ncf.ncf_id,
    ncf.nin_id,
    ncf.rec_id,
    r.rec_nombre,
    GROUP_CONCAT(DISTINCT rc.rc_comida) AS rec_tipo_comida,
    ncf.creado_en,
    ncf.actualizado_en
  FROM ninos_comidas_favoritas ncf
  JOIN recetas r ON r.rec_id = ncf.rec_id
  LEFT JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
  WHERE ncf.nin_id = p_nin_id
  GROUP BY ncf.ncf_id, ncf.nin_id, ncf.rec_id, r.rec_nombre, ncf.creado_en, ncf.actualizado_en
  ORDER BY ncf.creado_en DESC;
END$$

CREATE PROCEDURE sp_comidas_favoritas_agregar(
    IN p_nin_id BIGINT UNSIGNED,
    IN p_rec_id INT UNSIGNED
)
BEGIN
  IF NOT EXISTS (SELECT 1 FROM recetas WHERE rec_id = p_rec_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Receta no encontrada';
  END IF;

  INSERT INTO ninos_comidas_favoritas (nin_id, rec_id)
  VALUES (p_nin_id, p_rec_id)
  ON DUPLICATE KEY UPDATE actualizado_en = CURRENT_TIMESTAMP;

  SELECT ROW_COUNT() AS affected_rows;
END$$

CREATE PROCEDURE sp_comidas_favoritas_eliminar(IN p_ncf_id BIGINT UNSIGNED)
BEGIN
  DELETE FROM ninos_comidas_favoritas WHERE ncf_id = p_ncf_id;
  SELECT ROW_COUNT() AS affected_rows;
END$$

CREATE PROCEDURE sp_recetas_buscar(
    IN p_query VARCHAR(255),
    IN p_tipo_comida ENUM('DESAYUNO','ALMUERZO','CENA','REFACCION'),
    IN p_limit INT
)
BEGIN
  DECLARE v_limit INT DEFAULT 20;
  DECLARE v_query VARCHAR(255);

  IF p_limit IS NOT NULL AND p_limit > 0 THEN
    SET v_limit = LEAST(p_limit, 100);
  END IF;

  SET v_query = CONCAT('%', COALESCE(p_query, ''), '%');

  IF p_tipo_comida IS NULL OR TRIM(p_tipo_comida) = '' THEN
    SELECT
      r.rec_id,
      r.rec_nombre,
      GROUP_CONCAT(DISTINCT rc.rc_comida) AS rec_tipo_comida,
      COALESCE(SUM(an.an_cantidad_100 * ri.ri_cantidad / 100), 0) AS rec_kcal
    FROM recetas r
    LEFT JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
    LEFT JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
    LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id AND an.nutri_id = 1
    WHERE r.rec_activo = 1 AND r.rec_nombre LIKE v_query
    GROUP BY r.rec_id, r.rec_nombre
    LIMIT v_limit;
  ELSE
    SELECT
      r.rec_id,
      r.rec_nombre,
      GROUP_CONCAT(DISTINCT rc.rc_comida) AS rec_tipo_comida,
      COALESCE(SUM(an.an_cantidad_100 * ri.ri_cantidad / 100), 0) AS rec_kcal
    FROM recetas r
    LEFT JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
    LEFT JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
    LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id AND an.nutri_id = 1
    WHERE r.rec_activo = 1
      AND r.rec_nombre LIKE v_query
      AND rc.rc_comida = p_tipo_comida
    GROUP BY r.rec_id, r.rec_nombre
    LIMIT v_limit;
  END IF;
END$$

CREATE PROCEDURE sp_admin_usuarios_listar()
BEGIN
  SELECT
    u.usr_id,
    u.usr_usuario,
    u.usr_nombre,
    u.usr_apellido,
    u.usr_correo,
    u.usr_dni,
    r.rol_nombre,
    u.usr_activo,
    u.creado_en
  FROM usuarios u
  JOIN roles r ON r.rol_id = u.rol_id
  WHERE u.eliminado_en IS NULL
  ORDER BY u.creado_en DESC;
END$$

CREATE PROCEDURE sp_admin_resetear_contrasena(
    IN p_usr_id BIGINT UNSIGNED,
    IN p_password_hash VARCHAR(255)
)
BEGIN
  IF NOT EXISTS (SELECT 1 FROM usuarios WHERE usr_id = p_usr_id AND eliminado_en IS NULL) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuario no encontrado';
  END IF;

  UPDATE usuarios
     SET usr_contrasena = p_password_hash,
         actualizado_en = CURRENT_TIMESTAMP
   WHERE usr_id = p_usr_id;

  SELECT ROW_COUNT() AS affected_rows;
END$$

CREATE PROCEDURE sp_admin_toggle_usuario(
    IN p_usr_id BIGINT UNSIGNED,
    IN p_actor_id BIGINT UNSIGNED
)
BEGIN
  DECLARE v_usr_activo TINYINT(1);
  DECLARE v_usr_usuario VARCHAR(255);

  IF p_usr_id = p_actor_id THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No puedes desactivar tu propia cuenta';
  END IF;

  SELECT usr_activo, usr_usuario
    INTO v_usr_activo, v_usr_usuario
    FROM usuarios
   WHERE usr_id = p_usr_id
     AND eliminado_en IS NULL
   LIMIT 1;

  IF v_usr_usuario IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Usuario no encontrado';
  END IF;

  UPDATE usuarios
     SET usr_activo = NOT v_usr_activo,
         actualizado_en = CURRENT_TIMESTAMP
   WHERE usr_id = p_usr_id;

  SELECT ROW_COUNT() AS affected_rows,
         v_usr_usuario AS usr_usuario,
         NOT v_usr_activo AS usr_activo;
END$$

DELIMITER ;
