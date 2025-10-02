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
  usrper_avatar_url      VARCHAR(255) NULL,
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
  usr_id_tutor   BIGINT UNSIGNED NOT NULL,
  ent_id         INT UNSIGNED NULL,
  nin_nombres    VARCHAR(150) NOT NULL,
  nin_fecha_nac  DATE NOT NULL,
  nin_sexo       ENUM('M','F') NOT NULL,
  nin_alergias   TEXT NULL,
  creado_en      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_ninos_tutor FOREIGN KEY (usr_id_tutor) REFERENCES usuarios(usr_id) ON DELETE RESTRICT,
  CONSTRAINT fk_ninos_entidad FOREIGN KEY (ent_id) REFERENCES entidades(ent_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_ninos_tutor ON ninos(usr_id_tutor);
CREATE INDEX idx_ninos_entidad ON ninos(ent_id);

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
  en_z_score_imc      DECIMAL(5,2) NULL,
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


select * from oms_bmi_percentiles;


ALTER TABLE ninos DROP COLUMN nin_fecha_nac;

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
ON DUPLICATE KEY UPDATE ta_nombre = VALUES(ta_nombre);


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

ALTER TABLE usuarios_perfil MODIFY COLUMN usrper_avatar_url MEDIUMTEXT;



select * from ninos;

select * from entidad_tipos;

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



INSERT INTO entidades
  (entti_id, ent_codigo, ent_nombre, ent_descripcion,
   ent_direccion, ent_referencia,
   ent_departamento, ent_provincia, ent_distrito, ent_ubigeo,
   ent_latitud, ent_longitud)
VALUES
-- Hospital público
(@HOSPITAL, 'HOSP_REB',
 'Hospital Nacional Edgardo Rebagliati Martins',
 'Hospital de alta complejidad perteneciente a EsSalud',
 'Av. Rebagliati s/n',
 'Frente al Parque de las Leyendas',
 'Lima', 'Lima', 'Jesús María', '150114',
 -12.0702, -77.0413),

-- Clínica privada
(@CLINICA, 'CLIN_INT_LIMA',
 'Clínica Internacional – Sede Lima',
 'Clínica privada con servicios de emergencia 24/7',
 'Av. Garcilaso de la Vega 1420',
 'Frente al Real Plaza Centro Cívico',
 'Lima', 'Lima', 'Cercado de Lima', '150101',
 -12.0464, -77.0428),

-- Puesto de salud rural
(@POSTA, 'POSTA_JAUJA',
 'Puesto de Salud El Mantaro',
 'Atención primaria y campañas de vacunación',
 'Calle Principal 115',
 'A 2 cuadras de la Plaza de Armas',
 'Junín', 'Jauja', 'Sausa', '120401',
 -11.7801, -75.5000),

-- ONG de nutrición
(@ONG, 'ONG_NUTRI',
 'NutriPerú',
 'ONG enfocada en programas de nutrición infantil',
 'Jr. Ricardo Palma 222',
 'Altura Puente Ricardo Palma',
 'Lima', 'Lima', 'Barranco', '150135',
 -12.1250, -77.0293),

-- Escuela pública
(@ESCUELA, 'ESC_LOS_ANDES',
 'IEP N.° 30546 “Los Andes”',
 'Escuela primaria estatal',
 'Jr. Túpac Amaru 350',
 'Frente al Coliseo Municipal',
 'Junín', 'Huancayo', 'El Tambo', '120117',
 -12.0605, -75.2136),

-- Centro comunitario
(@CENTRO_COMUNITARIO, 'CC_JARDINES',
 'Centro Comunitario “Jardines de la Paz”',
 'Clases y talleres para familias',
 'Av. Las Flores 510',
 'Espalda del parque zonal',
 'Lima', 'Lima', 'San Juan de Lurigancho', '150133',
 -12.0221, -76.9900),

-- Consulta privada
(@PRIVADO, 'CONS_RAMIREZ',
 'Consultorio Dr. Ramírez',
 'Pediatría y nutrición infantil',
 'Av. Ferrocarril 805, 2.º piso',
 'Edificio “Santa Elena”',
 'Cusco', 'Cusco', 'Wanchaq', '080102',
 -13.5281, -71.9436),

-- Plataforma virtual
(@VIRTUAL, 'VIRT_SALUDONLINE',
 'SaludOnline.pe',
 'Plataforma virtual de telemedicina',
 NULL, NULL,
 NULL, NULL, NULL, NULL,
 NULL, NULL);


select * from ninos;

select * from antropometrias;

select * from usuarios;

show create table usuarios_perfil;

show create table ninos;

show create table antropometrias;

show create table tutores;

DELETE FROM ninos
WHERE nin_id BETWEEN 70 AND 76;

show create table ninos_alergias;

show create table usuarios_perfil;

select * from oms_bmi_lms;

select * from ninos_alergias;

select * from tipos_alergias;

SELECT entti_id, entti_codigo, entti_nombre
FROM entidad_tipos
WHERE entti_codigo = 'HOSPITAL';

select * from entidades;

show create table entidades;


INSERT INTO entidades
  (entti_id, ent_codigo, ent_nombre, ent_descripcion,
   ent_direccion, ent_referencia,
   ent_departamento, ent_provincia, ent_distrito, ent_ubigeo,
   ent_latitud, ent_longitud)
VALUES
/* -------------  HOSPITALES (entti_id = 1) ------------- */
(1, 'HOSP_REB',       'Hospital Nacional Edgardo Rebagliati Martins',
     'Hospital de alta complejidad de ESSalud',
     'Av. Rebagliati s/n',                  'Frente al Parque de las Leyendas',
     'Lima',  'Lima',     'Jesús María',    '150114', -12.070200, -77.041300),
(1, 'HOSP_CUSCO',     'Hospital Regional del Cusco',
     'Hospital de referencia para la Macro Región Sur',
     'Av. La Cultura 700',                  'Alt. del óvalo Pachacútec',
     'Cusco', 'Cusco',    'Wanchaq',        '080102', -13.533540, -71.957280),

/* -------------  CLÍNICAS (entti_id = 2) ------------- */
(2, 'CLIN_INT_LIMA',  'Clínica Internacional – Sede Lima',
     'Clínica privada con emergencia 24/7',
     'Av. Garcilaso de la Vega 1420',       'Frente al Real Plaza Centro Cívico',
     'Lima',  'Lima',     'Cercado de Lima', '150101', -12.046400, -77.042800),
(2, 'CLIN_SANPABLO',  'Clínica San Pablo Surco',
     'Clínica especializada en oncología y maternidad',
     'Av. El Polo 290',                     'Frente al Jockey Plaza',
     'Lima',  'Lima',     'Santiago de Surco','150140', -12.109800, -76.977000),

/* -------------  POSTAS (entti_id = 3) ------------- */
(3, 'POSTA_JAUJA',    'Puesto de Salud El Mantaro',
     'Atención primaria y campañas de vacunación',
     'Calle Principal 115',                 'A 2 cuadras de la plaza',
     'Junín', 'Jauja',    'Sausa',          '120401', -11.780100, -75.500000),
(3, 'POSTA_PUNO',     'Posta de Salud Titicaca',
     'Atención materno-infantil y control prenatal',
     'Jr. Los Incas 450',                   'Espalda del mercado central',
     'Puno',  'Puno',     'Puno',           '210101', -15.842920, -70.025910),

/* -------------  ONG (entti_id = 4) ------------- */
(4, 'ONG_NUTRIPERU',  'NutriPerú',
     'ONG enfocada en programas de nutrición infantil',
     'Jr. Ricardo Palma 222',               'Alt. puente Ricardo Palma',
     'Lima',  'Lima',     'Barranco',       '150135', -12.125000, -77.029300),
(4, 'ONG_SONRISAS',   'Sonrisas Saludables',
     'ONG que brinda odontología preventiva en zonas rurales',
     'Av. Los Héroes 180',                  'Frente al colegio Fe y Alegría',
     'Ayacucho','Huamanga','Ayacucho',      '050101', -13.157800, -74.223200),

/* -------------  ESCUELAS (entti_id = 5) ------------- */
(5, 'ESC_LOSANDES',   'IEP N.° 30546 “Los Andes”',
     'Escuela primaria estatal multigrado',
     'Jr. Túpac Amaru 350',                 'Frente al coliseo municipal',
     'Junín', 'Huancayo','El Tambo',        '120117', -12.060500, -75.213600),
(5, 'ESC_BELEN',      'IE N.° 6012 Virgen de Belén',
     'Institución educativa inicial y primaria',
     'Av. Pedro Miotta 1020',               'Costado del parque Zonal',
     'Lima',  'Lima',     'San Juan de Miraflores','150132', -12.155300, -76.972300),

/* -------------  CENTROS COMUNITARIOS (entti_id = 6) ------------- */
(6, 'CC_JARDINES',    'Centro Comunitario “Jardines de la Paz”',
     'Talleres de oficios y comedor popular',
     'Av. Las Flores 510',                  'Espalda del parque zonal',
     'Lima',  'Lima',     'San Juan de Lurigancho','150133', -12.022100, -76.990000),
(6, 'CC_WARMI',       'Centro Comunitario Warmi Wasi',
     'Programas de empoderamiento femenino',
     'Prolong. Ayacucho s/n',               'Frente al mercado modelo',
     'Apurímac','Abancay','Abancay',        '030101', -13.636000, -72.879000),

/* -------------  CONSULTAS PRIVADAS (entti_id = 7) ------------- */
(7, 'CONS_RAMIREZ',   'Consultorio Dr. Ramírez',
     'Pediatría y nutrición infantil',
     'Av. Ferrocarril 805, 2.º piso',       'Edificio Santa Elena',
     'Cusco', 'Cusco',    'Wanchaq',        '080102', -13.528100, -71.943600),
(7, 'CONS_CARDIO',    'CardioLife – Dr. Huamán',
     'Cardiología preventiva',
     'Jr. Amazonas 310',                    'A media cuadra de la catedral',
     'La Libertad','Trujillo','Trujillo',   '130101', -8.113200, -79.029800),

/* -------------  PLATAFORMAS VIRTUALES (entti_id = 8) ------------- */
(8, 'VIRT_SALUDON',   'SaludOnline.pe',
     'Plataforma virtual de telemedicina multiespecialidad',
     NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(8, 'VIRT_MI_DOC',    'MiDoctorEnCasa',
     'Consultas por videollamada y chat 24/7',
     NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),

/* -------------  MÁS EJEMPLOS RÁPIDOS (opcional) ------------- */
(2, 'CLIN_ANGAMOS',   'Clínica Angamos',
     'Clínica traumato-ortopédica',
     'Av. Angamos Este 100',                'Alt. cuadra 1 Av. Arequipa',
     'Lima','Lima','Surquillo','150141', -12.115900, -77.022400),
(1, 'HOSP_PIURA',     'Hospital Santa Rosa de Piura',
     'Hospital de alta complejidad nivel II-2',
     'Av. San Martín 150',                  'Frente al colegio San Miguel',
     'Piura','Piura','Piura','200101', -5.185630, -80.640000),
(3, 'POSTA_IQUITOS',  'Puesto de Salud Bellavista Nanay',
     'Atención de zonas peri-rurales',
     'Calle 9 de Octubre s/n',              'Ribera del río Nanay',
     'Loreto','Maynas','Iquitos','160101', -3.743670, -73.251630),
(4, 'ONG_AZUL',       'Manos Azules',
     'ONG dedicada a salud mental comunitaria',
     'Av. Grau 620',                        'Frente a la casa de la cultura',
     'Tacna','Tacna','Tacna','230101', -18.006420, -70.246560);


select * from evaluaciones_nutricionales;
select * from evaluaciones_recomendaciones;
select * from recomendaciones_tipos;

select * from antropometrias;

select * from ninos;

select * from oms_bmi_lms;

select * from roles;

call sp_roles_insertar('pafam','PADRES');

show create table ninos;

show create table usuarios;

show create table usuarios_perfil;

show create table roles;

select * from usuarios;

select * from usuarios_perfil;

select * from antropometrias;

select * from entidades;

select * from ninos;

select * from antropometrias;

select * from tutores;

select * from usuarios;

select * from antropometrias;

use nutricion;

create
    definer = root@`%` procedure sp_roles_get_codigo_by_id(IN p_rol_id bigint unsigned)
BEGIN
  SELECT rol_codigo
  FROM roles
  WHERE rol_id = p_rol_id
  LIMIT 1;
END;

-- Procedimiento: sp_usuarios_existe_username
-- Descripción: Verifica si un nombre de usuario ya existe
create
    definer = root@`%` procedure sp_usuarios_existe_username(IN p_username varchar(50))
BEGIN
  SELECT EXISTS(
    SELECT 1
    FROM usuarios
    WHERE usr_usuario = p_username
  ) as existe;
END;

-- Procedimiento: sp_usuarios_perfil_actualizar_avatar
-- Descripción: Actualiza o crea el perfil del usuario con su avatar y datos básicos
create
    definer = root@`%` procedure sp_usuarios_perfil_actualizar_avatar(
    IN p_usr_id bigint unsigned,
    IN p_avatar_url mediumtext,
    IN p_telefono varchar(20),
    IN p_idioma varchar(10)
)
BEGIN
  DECLARE v_telefono VARCHAR(20);
  DECLARE v_idioma VARCHAR(10);

  -- Valores por defecto
  SET v_telefono = COALESCE(NULLIF(TRIM(p_telefono), ''), '000000000');
  SET v_idioma = COALESCE(NULLIF(TRIM(p_idioma), ''), 'es-PE');

  -- Insertar o actualizar el perfil
  INSERT INTO usuarios_perfil (
    usr_id,
    usrper_avatar_url,
    usrper_telefono,
    usrper_idioma
  ) VALUES (
    p_usr_id,
    p_avatar_url,
    v_telefono,
    v_idioma
  )
  ON DUPLICATE KEY UPDATE
    usrper_avatar_url = VALUES(usrper_avatar_url),
    actualizado_en = NOW();
END;


-- Procedimiento: sp_tipos_alergias_buscar
-- Descripción: Busca tipos de alergias por código o nombre
create
    definer = root@`%` procedure sp_tipos_alergias_buscar(
    IN p_query varchar(100),
    IN p_limit int
)
BEGIN
  DECLARE v_limit INT DEFAULT 50;

  -- Establecer límite (máximo 100)
  IF p_limit IS NOT NULL AND p_limit > 0 AND p_limit <= 100 THEN
    SET v_limit = p_limit;
  END IF;

  -- Si no hay query, retornar todos los activos
  IF p_query IS NULL OR TRIM(p_query) = '' THEN
    SELECT
      ta_id,
      ta_codigo,
      ta_nombre,
      ta_categoria,
      ta_activo,
      creado_en
    FROM tipos_alergias
    WHERE ta_activo = 1
    ORDER BY ta_nombre
    LIMIT v_limit;
  ELSE
    -- Buscar por código o nombre
    SELECT
      ta_id,
      ta_codigo,
      ta_nombre,
      ta_categoria,
      ta_activo,
      creado_en
    FROM tipos_alergias
    WHERE ta_activo = 1
      AND (
        ta_codigo LIKE CONCAT('%', p_query, '%')
        OR ta_nombre LIKE CONCAT('%', p_query, '%')
      )
    ORDER BY
      CASE
        WHEN ta_codigo = p_query THEN 1
        WHEN ta_nombre = p_query THEN 2
        WHEN ta_codigo LIKE CONCAT(p_query, '%') THEN 3
        WHEN ta_nombre LIKE CONCAT(p_query, '%') THEN 4
        ELSE 5
      END,
      ta_nombre
    LIMIT v_limit;
  END IF;
END;

-- Procedimiento: sp_entidades_buscar
-- Descripción: Busca entidades por código, nombre o tipo
create
    definer = root@`%` procedure sp_entidades_buscar(
    IN p_query varchar(100),
    IN p_limit int
)
BEGIN
  DECLARE v_limit INT DEFAULT 20;

  -- Establecer límite (máximo 100)
  IF p_limit IS NOT NULL AND p_limit > 0 AND p_limit <= 100 THEN
    SET v_limit = p_limit;
  END IF;

  -- Si no hay query, retornar todos
  IF p_query IS NULL OR TRIM(p_query) = '' THEN
    SELECT
      e.ent_id,
      e.ent_codigo,
      e.ent_nombre,
      e.ent_descripcion,
      e.ent_direccion,
      e.ent_departamento,
      e.ent_provincia,
      e.ent_distrito,
      e.entti_id,
      t.entti_codigo,
      t.entti_nombre,
      e.creado_en
    FROM entidades e
    JOIN entidad_tipos t ON e.entti_id = t.entti_id
    ORDER BY e.ent_nombre
    LIMIT v_limit;
  ELSE
    -- Buscar por código, nombre o tipo
    SELECT
      e.ent_id,
      e.ent_codigo,
      e.ent_nombre,
      e.ent_descripcion,
      e.ent_direccion,
      e.ent_departamento,
      e.ent_provincia,
      e.ent_distrito,
      e.entti_id,
      t.entti_codigo,
      t.entti_nombre,
      e.creado_en
    FROM entidades e
    JOIN entidad_tipos t ON e.entti_id = t.entti_id
    WHERE
      e.ent_codigo LIKE CONCAT('%', p_query, '%')
      OR e.ent_nombre LIKE CONCAT('%', p_query, '%')
      OR t.entti_nombre LIKE CONCAT('%', p_query, '%')
    ORDER BY
      CASE
        WHEN e.ent_codigo = p_query THEN 1
        WHEN e.ent_nombre = p_query THEN 2
        WHEN e.ent_codigo LIKE CONCAT(p_query, '%') THEN 3
        WHEN e.ent_nombre LIKE CONCAT(p_query, '%') THEN 4
        ELSE 5
      END,
      e.ent_nombre
    LIMIT v_limit;
  END IF;
END;

-- Procedimiento: sp_entidad_tipos_listar
-- Descripción: Lista todos los tipos de entidades
create
    definer = root@`%` procedure sp_entidad_tipos_listar()
BEGIN
  SELECT
    entti_id,
    entti_codigo,
    entti_nombre,
    creado_en
  FROM entidad_tipos
  ORDER BY entti_nombre;
END;

create
    definer = root@`%` procedure sp_usuarios_obtener_por_id(IN p_usr_id bigint unsigned)
BEGIN
  SELECT
    u.usr_id,
    u.usr_usuario,
    u.usr_correo,
    u.usr_nombre,
    u.usr_apellido,
    u.rol_id,
    u.usr_activo,
    u.usr_contrasena AS password_hash,
    u.creado_en,
    u.actualizado_en
  FROM usuarios u
  WHERE u.usr_id = p_usr_id
  LIMIT 1;
END;

-- Procedimiento: sp_usuarios_obtener_por_email
-- Descripción: Obtener usuario completo por correo electrónico
create
    definer = root@`%` procedure sp_usuarios_obtener_por_email(IN p_correo varchar(255))
BEGIN
  SELECT
    u.usr_id,
    u.usr_usuario,
    u.usr_correo,
    u.usr_nombre,
    u.usr_apellido,
    u.rol_id,
    u.usr_activo,
    u.usr_contrasena AS password_hash,
    u.creado_en,
    u.actualizado_en
  FROM usuarios u
  WHERE u.usr_correo = p_correo
  LIMIT 1;
END;

create
    definer = root@`%` procedure sp_ninos_eliminar_alergia(IN p_na_id bigint unsigned, IN p_nin_id bigint unsigned)
BEGIN
  -- Validar que la alergia existe y pertenece al niño especificado
  IF NOT EXISTS(SELECT 1 FROM ninos_alergias WHERE na_id = p_na_id AND nin_id = p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Alergia no encontrada para este niño';
  END IF;

  -- Soft delete: marcar como inactiva en lugar de eliminar
  UPDATE ninos_alergias
  SET na_activo = 0
  WHERE na_id = p_na_id AND nin_id = p_nin_id;

  -- Retornar las alergias activas restantes del niño
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
    up.usrper_idioma      AS idioma_resp,
    -- Campos adicionales requeridos por NinoResponse
    fn_edad_meses(n.nin_fecha_nac) AS edad_meses,
    n.creado_en,
    n.actualizado_en,
    -- Información de la entidad (si existe)
    e.ent_nombre,
    e.ent_codigo,
    e.ent_direccion,
    e.ent_departamento,
    e.ent_provincia,
    e.ent_distrito
  FROM ninos n
  JOIN usuarios u             ON u.usr_id = COALESCE(n.usr_id_propietario, n.usr_id_tutor)
  LEFT JOIN usuarios_perfil up ON up.usr_id = u.usr_id
  LEFT JOIN entidades e ON e.ent_id = n.ent_id
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
    up.usrper_idioma      AS idioma_resp,
    -- Campos adicionales requeridos por NinoResponse
    fn_edad_meses(n.nin_fecha_nac) AS edad_meses,
    n.creado_en,
    n.actualizado_en,
    -- Información de la entidad (si existe)
    e.ent_nombre,
    e.ent_codigo,
    e.ent_direccion,
    e.ent_departamento,
    e.ent_provincia,
    e.ent_distrito
  FROM ninos n
  JOIN usuarios u             ON u.usr_id = COALESCE(n.usr_id_propietario, n.usr_id_tutor)
  LEFT JOIN usuarios_perfil up ON up.usr_id = u.usr_id
  LEFT JOIN entidades e ON e.ent_id = n.ent_id
  WHERE n.nin_id = p_nin_id;
END;

DELIMITER $$
CREATE FUNCTION fn_edad_meses(p_fecha_nac DATE)
RETURNS INT
DETERMINISTIC
BEGIN
  RETURN TIMESTAMPDIFF(MONTH, p_fecha_nac, CURDATE());
END$$
DELIMITER ;

select * from ninos;

select * from usuarios;

CALL sp_ninos_get(184);

create
    definer = root@`%` procedure sp_ninos_eliminar(IN p_nin_id bigint unsigned)
BEGIN
  DECLARE v_filas_afectadas INT DEFAULT 0;

  -- Verificar si el niño existe
  IF NOT EXISTS(SELECT 1 FROM ninos WHERE nin_id = p_nin_id) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El niño no existe';
  END IF;

  -- Eliminar el niño (hard delete)
  DELETE FROM ninos WHERE nin_id = p_nin_id;

  SET v_filas_afectadas = ROW_COUNT();

  SELECT v_filas_afectadas AS filas_afectadas, 'OK' AS msg;
END;


create
    definer = root@`%` procedure sp_ninos_obtener_por_tutor(IN p_usr_id_tutor bigint unsigned)
BEGIN
  SELECT
    n.nin_id,
    n.usr_id_tutor,
    n.ent_id,
    n.nin_nombres,                                          
    n.nin_fecha_nac,                                        
    n.nin_sexo,                                             
    e.ent_nombre,                                           
    e.ent_codigo,                                           
    e.ent_direccion,                                        
    e.ent_departamento,                                     
    e.ent_provincia,                                        
    e.ent_distrito,                                         
    fn_edad_meses(n.nin_fecha_nac) as edad_meses,          
    n.creado_en,
    n.actualizado_en
  FROM ninos n
  JOIN usuarios u ON n.usr_id_tutor = u.usr_id
  LEFT JOIN entidades e ON n.ent_id = e.ent_id             
  WHERE n.usr_id_tutor = p_usr_id_tutor AND u.usr_activo = 1
  ORDER BY n.creado_en DESC;
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

