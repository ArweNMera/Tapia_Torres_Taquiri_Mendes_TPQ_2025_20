-- ============================================================================
-- BASE DE DATOS
-- ============================================================================
CREATE DATABASE IF NOT EXISTS nutricion
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE nutricion;


-- ============================================================================
-- TABLAS BÁSICAS DE SEGURIDAD
-- ============================================================================
CREATE TABLE roles (
  rol_id         SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  rol_codigo     VARCHAR(32)  NOT NULL UNIQUE,   -- ADMIN, NUTRI, TUTOR
  rol_nombre     VARCHAR(80)  NOT NULL,
  creado_en      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE usuarios (
  usr_id          BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  usr_dni         VARCHAR(12)  NULL,
  usr_correo      VARCHAR(190) NOT NULL UNIQUE,
  usr_contrasena  CHAR(60)     NOT NULL,
  usr_nombre      VARCHAR(150) NOT NULL,
  usr_apellido    VARCHAR(150) NOT NULL,
  usr_usuario     VARCHAR(150) NOT NULL,
  rol_id          SMALLINT UNSIGNED NOT NULL,
  usr_activo      TINYINT(1)   NOT NULL DEFAULT 1,
  creado_en       DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  eliminado_en    DATETIME     NULL,
  CONSTRAINT fk_usuarios_roles
    FOREIGN KEY (rol_id) REFERENCES roles(rol_id) ON DELETE RESTRICT,
  CONSTRAINT uk_usuarios_dni UNIQUE (usr_dni)
) ENGINE=InnoDB;

CREATE INDEX idx_usuarios_rol    ON usuarios(rol_id);
CREATE INDEX idx_usuarios_activo ON usuarios(usr_activo);

CREATE TABLE usuarios_perfil (
  usrper_id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  usr_id                 BIGINT UNSIGNED NOT NULL UNIQUE,
  usrper_avatar_url      MEDIUMTEXT NULL,
  usrper_telefono        VARCHAR(20)  NOT NULL,
  usrper_direccion       VARCHAR(180) NULL,
  usrper_genero          ENUM('M','F','X') NULL,
  usrper_fecha_nac       DATE NULL,
  usrper_idioma          VARCHAR(10)  NOT NULL DEFAULT 'es-PE',
  creado_en              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  eliminado_en           DATETIME NULL,
  CONSTRAINT fk_usrper_usuario
    FOREIGN KEY (usr_id) REFERENCES usuarios(usr_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- ENTIDADES (Hospitales, Clínicas, Postas, ONGs, etc.)
-- ============================================================================
CREATE TABLE entidad_tipos (
  entti_id       TINYINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  entti_codigo   VARCHAR(32)  NOT NULL UNIQUE,  -- HOSPITAL, CLINICA, POSTA, ONG, ESCUELA, CENTRO_COMUNITARIO
  entti_nombre   VARCHAR(80)  NOT NULL,
  creado_en      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE entidades (
  ent_id           INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  entti_id         TINYINT UNSIGNED NOT NULL,
  ent_codigo       VARCHAR(40)  NULL UNIQUE,
  ent_nombre       VARCHAR(150) NOT NULL,
  ent_descripcion  VARCHAR(255) NULL,
  ent_direccion    VARCHAR(180) NULL,
  ent_referencia   VARCHAR(180) NULL,
  ent_departamento VARCHAR(60)  NULL,
  ent_provincia    VARCHAR(60)  NULL,
  ent_distrito     VARCHAR(60)  NULL,
  ent_ubigeo       VARCHAR(6)   NULL,
  ent_latitud      DECIMAL(9,6) NULL,
  ent_longitud     DECIMAL(9,6) NULL,
  ent_activo       TINYINT(1)   NOT NULL DEFAULT 1,
  creado_en        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_entidades_tipo FOREIGN KEY (entti_id) REFERENCES entidad_tipos(entti_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_entidades_tipo_activo ON entidades(entti_id, ent_activo);

-- ============================================================================
-- NUTRICIONISTAS / TUTORES
-- ============================================================================
CREATE TABLE nutricionistas (
  nut_id          BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  usr_id          BIGINT UNSIGNED NOT NULL,
  ent_id          INT UNSIGNED NULL,
  nut_colegiatura VARCHAR(40) NULL,
  creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_nutricionistas_usuario FOREIGN KEY (usr_id) REFERENCES usuarios(usr_id) ON DELETE CASCADE,
  CONSTRAINT fk_nutricionistas_entidad FOREIGN KEY (ent_id) REFERENCES entidades(ent_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_nut_usuario ON nutricionistas(usr_id);
CREATE INDEX idx_nut_entidad ON nutricionistas(ent_id);

CREATE TABLE tutores (
  tut_id         BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  usr_id         BIGINT UNSIGNED NOT NULL UNIQUE,
  tut_telefono   VARCHAR(32) NULL,
  tut_idioma     VARCHAR(10) NOT NULL DEFAULT 'es-PE',
  creado_en      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_tutores_usuario
    FOREIGN KEY (usr_id) REFERENCES usuarios(usr_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- NIÑOS / ANTROPOMETRÍA / VÍNCULOS
-- ============================================================================
CREATE TABLE ninos (
  nin_id         BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  usrper_id      BIGINT UNSIGNED NOT NULL,
  usr_id_tutor   BIGINT UNSIGNED NOT NULL,
  ent_id         INT UNSIGNED NULL,
  creado_en      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_ninos_tutor FOREIGN KEY (usr_id_tutor) REFERENCES usuarios(usr_id) ON DELETE RESTRICT,
  CONSTRAINT fk_ninos_entidad FOREIGN KEY (ent_id) REFERENCES entidades(ent_id) ON DELETE SET NULL,
  CONSTRAINT fk_ninos_usrper FOREIGN KEY (usrper_id) REFERENCES usuarios_perfil(usrper_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_ninos_tutor ON ninos(usr_id_tutor);
CREATE INDEX idx_ninos_entidad ON ninos(ent_id);

ALTER TABLE ninos
  ADD COLUMN nin_nombres    VARCHAR(150) NOT NULL AFTER ent_id,
  ADD COLUMN nin_fecha_nac  DATE         NOT NULL AFTER nin_nombres,
  ADD COLUMN nin_sexo       ENUM('M','F') NOT NULL AFTER nin_fecha_nac;

ALTER TABLE ninos
  MODIFY COLUMN usr_id_tutor BIGINT UNSIGNED NULL;

ALTER TABLE ninos
  ADD COLUMN usr_id_propietario BIGINT UNSIGNED NULL AFTER usr_id_tutor,
  ADD CONSTRAINT fk_ninos_propietario
    FOREIGN KEY (usr_id_propietario) REFERENCES usuarios(usr_id) ON DELETE SET NULL;

CREATE INDEX idx_ninos_propietario ON ninos(usr_id_propietario);

CREATE TABLE antropometrias (
  ant_id         BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id         BIGINT UNSIGNED NOT NULL,
  ant_fecha      DATE NOT NULL,
  ant_peso_kg    DECIMAL(5,2) NOT NULL,
  ant_talla_cm   DECIMAL(5,2) NOT NULL,
  ant_z_imc      DECIMAL(6,3) NULL,
  ant_z_peso_edad DECIMAL(6,3) NULL,
  ant_z_talla_edad DECIMAL(6,3) NULL,
  ant_fuente_json JSON NULL,
  creado_en      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_ant_nino_fecha (nin_id, ant_fecha),
  CONSTRAINT fk_antropometrias_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE vinculos_nutricionista_nino (
  vnn_id        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id        BIGINT UNSIGNED NOT NULL,
  nut_id        BIGINT UNSIGNED NOT NULL,
  vnn_estado    ENUM('PENDIENTE','ACTIVO','RECHAZADO') NOT NULL DEFAULT 'PENDIENTE',
  vnn_desde     DATE NOT NULL DEFAULT (CURRENT_DATE),
  vnn_hasta     DATE NULL,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uk_vnn (nin_id, nut_id),
  CONSTRAINT fk_vnn_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_vnn_nutri FOREIGN KEY (nut_id) REFERENCES nutricionistas(nut_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- ALIMENTOS / NUTRIENTES / RECETAS / DISPONIBILIDAD
-- ============================================================================
CREATE TABLE alimentos (
  ali_id        INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  ali_nombre    VARCHAR(150) NOT NULL,
  ali_nombre_cientifico VARCHAR(150) NULL,
  ali_grupo     VARCHAR(60)  NULL,
  ali_unidad    VARCHAR(16)  NOT NULL,
  ali_activo    TINYINT(1) NOT NULL DEFAULT 1,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FULLTEXT KEY ft_ali_nombre (ali_nombre)
) ENGINE=InnoDB;

CREATE TABLE nutrientes (
  nutri_id      SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nutri_codigo  VARCHAR(32) NOT NULL UNIQUE,
  nutri_nombre  VARCHAR(120) NOT NULL,
  nutri_unidad  VARCHAR(16)  NOT NULL
) ENGINE=InnoDB;

CREATE TABLE alimentos_nutrientes (
  ali_id        INT UNSIGNED NOT NULL,
  nutri_id      SMALLINT UNSIGNED NOT NULL,
  an_cantidad_100 DECIMAL(12,4) NOT NULL,
  an_fuente     VARCHAR(255) NULL,
  PRIMARY KEY (ali_id, nutri_id),
  CONSTRAINT fk_an_alimento FOREIGN KEY (ali_id) REFERENCES alimentos(ali_id) ON DELETE CASCADE,
  CONSTRAINT fk_an_nutriente FOREIGN KEY (nutri_id) REFERENCES nutrientes(nutri_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE disponibilidad_alimentos (
  dis_id       BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  ali_id       INT UNSIGNED NOT NULL,
  ent_id       INT UNSIGNED NULL,
  dis_periodo  ENUM('Q1','Q2','Q3','Q4') NOT NULL,
  dis_disponible TINYINT(1) NOT NULL,
  dis_precio_promedio DECIMAL(10,2) NULL,
  dis_region   VARCHAR(120) NULL,
  creado_en    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_dis_alimento FOREIGN KEY (ali_id) REFERENCES alimentos(ali_id) ON DELETE CASCADE,
  CONSTRAINT fk_dis_entidad FOREIGN KEY (ent_id) REFERENCES entidades(ent_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================================
-- RECETAS / MENÚS / ADHERENCIA / SÍNTOMAS
-- ============================================================================
CREATE TABLE recetas (
  rec_id        INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  rec_nombre    VARCHAR(150) NOT NULL,
  rec_instrucciones TEXT NOT NULL,
  rec_activo    TINYINT(1) NOT NULL DEFAULT 1,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE recetas_ingredientes (
  rec_id       INT UNSIGNED NOT NULL,
  ali_id       INT UNSIGNED NOT NULL,
  ri_cantidad  DECIMAL(12,4) NOT NULL,
  ri_unidad    VARCHAR(16) NOT NULL,
  PRIMARY KEY (rec_id, ali_id),
  CONSTRAINT fk_ri_receta   FOREIGN KEY (rec_id) REFERENCES recetas(rec_id) ON DELETE CASCADE,
  CONSTRAINT fk_ri_alimento FOREIGN KEY (ali_id) REFERENCES alimentos(ali_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE menus (
  men_id          BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id          BIGINT UNSIGNED NOT NULL,
  men_generado_por ENUM('IA','NUTRICIONISTA') NOT NULL,
  men_inicio      DATE NOT NULL,
  men_fin         DATE NOT NULL,
  men_kcal_total  INT NULL,
  men_estado      ENUM('BORRADOR','APROBADO','ARCHIVADO') NOT NULL DEFAULT 'BORRADOR',
  creado_en       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_menus_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE menus_items (
  mei_id       BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  men_id       BIGINT UNSIGNED NOT NULL,
  mei_dia_idx  TINYINT UNSIGNED NOT NULL,
  mei_comida   ENUM('DESAYUNO','ALMUERZO','CENA','REFACCION') NOT NULL,
  rec_id       INT UNSIGNED NOT NULL,
  mei_kcal     INT NULL,
  CONSTRAINT fk_mei_menu   FOREIGN KEY (men_id) REFERENCES menus(men_id) ON DELETE CASCADE,
  CONSTRAINT fk_mei_receta FOREIGN KEY (rec_id) REFERENCES recetas(rec_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE adherencias (
  adh_id        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id        BIGINT UNSIGNED NOT NULL,
  men_id        BIGINT UNSIGNED NULL,
  mei_id        BIGINT UNSIGNED NULL,
  adh_registrado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  adh_estado    ENUM('OK','PARCIAL','NO') NOT NULL,
  adh_notas     TEXT NULL,
  CONSTRAINT fk_adh_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_adh_menu FOREIGN KEY (men_id) REFERENCES menus(men_id) ON DELETE SET NULL,
  CONSTRAINT fk_adh_item FOREIGN KEY (mei_id) REFERENCES menus_items(mei_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE sintomas (
  sin_id        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id        BIGINT UNSIGNED NOT NULL,
  sin_fecha     DATE NOT NULL,
  sin_tipo      VARCHAR(120) NOT NULL,
  sin_grado     TINYINT UNSIGNED NULL,
  sin_notas     TEXT NULL,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_sintomas_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================================
-- RIESGO / NOTIFICACIONES / CONSENTIMIENTOS / AUDITORÍA
-- ============================================================================
CREATE TABLE puntajes_riesgo (
  pri_id         BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id         BIGINT UNSIGNED NOT NULL,
  pri_fecha_hora DATETIME NOT NULL,
  pri_version    VARCHAR(32) NOT NULL,
  pri_riesgo     DECIMAL(6,4) NOT NULL,
  pri_caracteristicas JSON NULL,
  CONSTRAINT fk_pri_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE notificaciones (
  not_id        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  usr_id        BIGINT UNSIGNED NOT NULL,
  not_tipo      VARCHAR(60) NOT NULL,
  not_payload   JSON NOT NULL,
  not_estado    ENUM('PENDIENTE','ENVIADO','FALLADO') NOT NULL DEFAULT 'PENDIENTE',
  not_enviado_en DATETIME NULL,
  creado_en     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_not_usuario FOREIGN KEY (usr_id) REFERENCES usuarios(usr_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE consentimientos (
  con_id        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  usr_id        BIGINT UNSIGNED NOT NULL,
  con_alcance   VARCHAR(120) NOT NULL,
  con_aceptado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  con_revocado_en DATETIME NULL,
  CONSTRAINT fk_con_usuario FOREIGN KEY (usr_id) REFERENCES usuarios(usr_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE eventos_auditoria (
  eau_id        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  usr_id        BIGINT UNSIGNED NULL,
  eau_entidad   VARCHAR(80) NOT NULL,
  eau_entidad_id VARCHAR(64) NOT NULL,
  eau_accion    VARCHAR(40) NOT NULL,
  eau_ip        VARCHAR(64) NULL,
  eau_metadata  JSON NULL,
  eau_fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_eau_usuario FOREIGN KEY (usr_id) REFERENCES usuarios(usr_id) ON DELETE SET NULL
) ENGINE=InnoDB;

ALTER TABLE usuarios MODIFY usr_contrasena VARCHAR(255) NOT NULL;

CREATE TABLE tipos_alergias (
  ta_id       SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  ta_codigo   VARCHAR(20) NOT NULL UNIQUE,
  ta_nombre   VARCHAR(100) NOT NULL,
  ta_categoria ENUM('ALIMENTARIA','MEDICAMENTO','AMBIENTAL') NOT NULL,
  ta_activo   BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Seeds de entidad_tipos (idempotentes)
INSERT INTO entidad_tipos (entti_codigo, entti_nombre) VALUES
('HOSPITAL', 'Hospital'),
('CLINICA', 'Clínica'),
('POSTA', 'Posta de Salud'),
('ONG', 'Organización No Gubernamental'),
('ESCUELA', 'Escuela'),
('CENTRO_COMUNITARIO', 'Centro Comunitario'),
('PRIVADO', 'Consulta Privada'),
('VIRTUAL', 'Plataforma Virtual')
ON DUPLICATE KEY UPDATE entti_nombre = VALUES(entti_nombre);

-- Seeds de tipos_alergias (idempotentes)
INSERT INTO tipos_alergias (ta_codigo, ta_nombre, ta_categoria, ta_activo) VALUES
-- Alergias alimentarias
('ALM_LECHE', 'Leche y productos lácteos', 'ALIMENTARIA', 1),
('ALM_HUEVO', 'Huevo', 'ALIMENTARIA', 1),
('ALM_GLUTEN', 'Gluten / Trigo', 'ALIMENTARIA', 1),
('ALM_FRUTOS_SECOS', 'Frutos secos', 'ALIMENTARIA', 1),
('ALM_MANI', 'Maní / Cacahuetes', 'ALIMENTARIA', 1),
('ALM_SOJA', 'Soja', 'ALIMENTARIA', 1),
('ALM_PESCADO', 'Pescado', 'ALIMENTARIA', 1),
('ALM_MARISCOS', 'Mariscos', 'ALIMENTARIA', 1),
('ALM_AJONJOLI', 'Ajonjolí / Sésamo', 'ALIMENTARIA', 1),
('ALM_CITRICOS', 'Cítricos', 'ALIMENTARIA', 1),
('ALM_CHOCOLATE', 'Chocolate', 'ALIMENTARIA', 1),
('ALM_FRESA', 'Fresas', 'ALIMENTARIA', 1),
-- Alergias a medicamentos
('MED_PENICILINA', 'Penicilina', 'MEDICAMENTO', 1),
('MED_ASPIRINA', 'Aspirina / AAS', 'MEDICAMENTO', 1),
('MED_IBUPROFENO', 'Ibuprofeno', 'MEDICAMENTO', 1),
('MED_SULFA', 'Sulfamidas', 'MEDICAMENTO', 1),
('MED_ANESTESIA', 'Anestésicos locales', 'MEDICAMENTO', 1),
('MED_YODO', 'Yodo / Contrastes', 'MEDICAMENTO', 1),
-- Alergias ambientales
('AMB_POLEN', 'Polen de plantas', 'AMBIENTAL', 1),
('AMB_POLVO', 'Ácaros del polvo', 'AMBIENTAL', 1),
('AMB_PELO_ANIMAL', 'Pelo de animales', 'AMBIENTAL', 1),
('AMB_LATEX', 'Látex', 'AMBIENTAL', 1),
('AMB_HONGOS', 'Hongos / Moho', 'AMBIENTAL', 1),
('AMB_PICADURAS', 'Picaduras de insectos', 'AMBIENTAL', 1)
ON DUPLICATE KEY UPDATE ta_nombre = VALUES(ta_nombre), ta_categoria = VALUES(ta_categoria), ta_activo = VALUES(ta_activo);

-- Relación niño-alergias
CREATE TABLE ninos_alergias (
  na_id       BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id      BIGINT UNSIGNED NOT NULL,
  ta_id       SMALLINT UNSIGNED NOT NULL,
  na_severidad ENUM('LEVE','MODERADA','SEVERA') NOT NULL DEFAULT 'LEVE',
  na_activo   BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_nino_alergia (nin_id, ta_id),
  CONSTRAINT fk_na_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_na_tipo FOREIGN KEY (ta_id) REFERENCES tipos_alergias(ta_id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE evaluaciones_nutricionales (
  en_id               BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id              BIGINT UNSIGNED NOT NULL,
  ant_id              BIGINT UNSIGNED NOT NULL,
  en_edad_meses       SMALLINT UNSIGNED NOT NULL,
  en_imc              DECIMAL(5,2) NULL, -- IMC calculado
  en_z_score_imc      DECIMAL(5,2) NULL,
  en_percentil_imc    DECIMAL(5,2) NULL, -- Percentil calculado
  en_clasificacion    ENUM('DESNUTRICION_SEVERA','DESNUTRICION','RIESGO','NORMAL','SOBREPESO','OBESIDAD') NOT NULL,
  en_nivel_riesgo     ENUM('BAJO','MODERADO','ALTO','CRITICO') NOT NULL,
  en_observaciones    TEXT NULL,
  creado_en           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_evaluacion_antropometria (ant_id),
  CONSTRAINT fk_en_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_en_antropometria FOREIGN KEY (ant_id) REFERENCES antropometrias(ant_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE recomendaciones_tipos (
  rt_id       SMALLINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  rt_codigo   VARCHAR(30) NOT NULL UNIQUE,
  rt_titulo   VARCHAR(150) NOT NULL,
  rt_descripcion TEXT NOT NULL,
  rt_clasificacion ENUM('DESNUTRICION_SEVERA','DESNUTRICION','RIESGO','NORMAL','SOBREPESO','OBESIDAD') NOT NULL,
  rt_prioridad TINYINT UNSIGNED NOT NULL DEFAULT 1, -- 1=alta, 2=media, 3=baja
  rt_activo   BOOLEAN NOT NULL DEFAULT TRUE,
  creado_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE evaluaciones_recomendaciones (
  er_id       BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  en_id       BIGINT UNSIGNED NOT NULL,
  rt_id       SMALLINT UNSIGNED NOT NULL,
  er_aplicada BOOLEAN NOT NULL DEFAULT FALSE,
  er_fecha_aplicacion DATETIME NULL,
  creado_en   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_er_evaluacion FOREIGN KEY (en_id) REFERENCES evaluaciones_nutricionales(en_id) ON DELETE CASCADE,
  CONSTRAINT fk_er_recomendacion FOREIGN KEY (rt_id) REFERENCES recomendaciones_tipos(rt_id) ON DELETE RESTRICT
) ENGINE=InnoDB;


-- LMS base
CREATE TABLE IF NOT EXISTS oms_bmi_lms (
  version      ENUM('OMS_2006','OMS_2007') NOT NULL,
  sexo         ENUM('M','F') NOT NULL,
  edad_meses   SMALLINT UNSIGNED NOT NULL,
  L            DECIMAL(8,4) NOT NULL,
  M            DECIMAL(8,4) NOT NULL,
  S            DECIMAL(8,4) NOT NULL,
  creado_en    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (version, sexo, edad_meses),
  CHECK (edad_meses BETWEEN 0 AND 228)
) ENGINE=InnoDB;

-- Z-scores
CREATE TABLE IF NOT EXISTS oms_bmi_zscores (
  lms_version    ENUM('OMS_2006','OMS_2007') NOT NULL,
  lms_sexo       ENUM('M','F') NOT NULL,
  lms_edad_meses SMALLINT UNSIGNED NOT NULL,
  sd_m3  DECIMAL(6,2), sd_m2 DECIMAL(6,2), sd_m1 DECIMAL(6,2),
  median DECIMAL(6,2), sd_p1 DECIMAL(6,2), sd_p2 DECIMAL(6,2), sd_p3 DECIMAL(6,2),
  PRIMARY KEY (lms_version, lms_sexo, lms_edad_meses),
  CONSTRAINT fk_z_lms FOREIGN KEY (lms_version, lms_sexo, lms_edad_meses)
    REFERENCES oms_bmi_lms(version, sexo, edad_meses) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Percentiles (0–5 y 5–19)
CREATE TABLE IF NOT EXISTS oms_bmi_percentiles (
  lms_version    ENUM('OMS_2006','OMS_2007') NOT NULL,
  lms_sexo       ENUM('M','F') NOT NULL,
  lms_edad_meses SMALLINT UNSIGNED NOT NULL,
  -- 0–5
  P01 DECIMAL(6,2), P1 DECIMAL(6,2), P3 DECIMAL(6,2), P5 DECIMAL(6,2),
  P10 DECIMAL(6,2), P15 DECIMAL(6,2), P25 DECIMAL(6,2), P50 DECIMAL(6,2),
  P75 DECIMAL(6,2), P85 DECIMAL(6,2), P90 DECIMAL(6,2), P95 DECIMAL(6,2),
  P97 DECIMAL(6,2), P99 DECIMAL(6,2), P999 DECIMAL(6,2),
  -- 5–19
  pct_1 DECIMAL(6,2), pct_3 DECIMAL(6,2), pct_5 DECIMAL(6,2), pct_15 DECIMAL(6,2),
  pct_25 DECIMAL(6,2), pct_50 DECIMAL(6,2), pct_75 DECIMAL(6,2), pct_85 DECIMAL(6,2),
  pct_95 DECIMAL(6,2), pct_97 DECIMAL(6,2), pct_99 DECIMAL(6,2),
  PRIMARY KEY (lms_version, lms_sexo, lms_edad_meses),
  CONSTRAINT fk_p_lms FOREIGN KEY (lms_version, lms_sexo, lms_edad_meses)
    REFERENCES oms_bmi_lms(version, sexo, edad_meses) ON DELETE CASCADE
) ENGINE=InnoDB;


-- A) Hacer opcional el tutor (para autogestionados)
ALTER TABLE ninos
  MODIFY COLUMN usr_id_tutor BIGINT UNSIGNED NULL;

-- ============================================================================
-- MODIFICACIONES PARA AUTOGESTIÓN DE PERFILES
-- ============================================================================

-- A) Hacer opcional el tutor (para autogestionados)
ALTER TABLE ninos
  MODIFY COLUMN usr_id_tutor BIGINT UNSIGNED NULL;

-- B) Agregar propietario (el usuario que se autogestiona)
ALTER TABLE ninos
  ADD COLUMN usr_id_propietario BIGINT UNSIGNED NULL AFTER usr_id_tutor,
  ADD CONSTRAINT fk_ninos_propietario
    FOREIGN KEY (usr_id_propietario) REFERENCES usuarios(usr_id) ON DELETE SET NULL;

CREATE INDEX idx_ninos_propietario ON ninos(usr_id_propietario);

-- C) Agregar campos propios del perfil del niño (necesarios para OMS)
ALTER TABLE ninos
  ADD COLUMN nin_nombres    VARCHAR(150) NOT NULL AFTER ent_id,
  ADD COLUMN nin_fecha_nac  DATE         NOT NULL AFTER nin_nombres,
  ADD COLUMN nin_sexo       ENUM('M','F') NOT NULL AFTER nin_fecha_nac;

-- D) Agregar campos faltantes a evaluaciones_nutricionales
ALTER TABLE evaluaciones_nutricionales
  ADD COLUMN en_imc DECIMAL(5,2) NULL COMMENT 'IMC calculado' AFTER en_edad_meses,
  ADD COLUMN en_percentil_imc DECIMAL(5,2) NULL COMMENT 'Percentil calculado' AFTER en_z_score_imc;



