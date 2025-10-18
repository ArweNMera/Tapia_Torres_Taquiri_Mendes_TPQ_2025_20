-- Tabla para almacenar el perfil nutricional calculado de cada niño
-- Basado en su edad, peso, talla y clasificación nutricional

CREATE TABLE IF NOT EXISTS perfil_nutricional_nino (
    pnn_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nin_id BIGINT UNSIGNED NOT NULL,

    -- Requerimientos nutricionales diarios
    pnn_calorias_diarias INT NOT NULL COMMENT 'Calorías diarias requeridas (kcal)',
    pnn_proteinas_g DECIMAL(6,2) DEFAULT NULL COMMENT 'Proteínas diarias (gramos)',
    pnn_carbohidratos_g DECIMAL(6,2) DEFAULT NULL COMMENT 'Carbohidratos diarios (gramos)',
    pnn_grasas_g DECIMAL(6,2) DEFAULT NULL COMMENT 'Grasas diarias (gramos)',

    -- Micronutrientes
    pnn_hierro_mg DECIMAL(6,2) DEFAULT NULL COMMENT 'Hierro diario (mg)',
    pnn_calcio_mg DECIMAL(6,2) DEFAULT NULL COMMENT 'Calcio diario (mg)',
    pnn_vitamina_a_ug DECIMAL(6,2) DEFAULT NULL COMMENT 'Vitamina A diaria (µg)',
    pnn_vitamina_c_mg DECIMAL(6,2) DEFAULT NULL COMMENT 'Vitamina C diaria (mg)',
    pnn_zinc_mg DECIMAL(6,2) DEFAULT NULL COMMENT 'Zinc diario (mg)',
    pnn_fibra_g DECIMAL(6,2) DEFAULT NULL COMMENT 'Fibra diaria (gramos)',

    -- Datos de referencia al momento del cálculo
    pnn_edad_meses INT DEFAULT NULL COMMENT 'Edad en meses al calcular',
    pnn_peso_kg DECIMAL(5,2) DEFAULT NULL COMMENT 'Peso en kg al calcular',
    pnn_talla_cm DECIMAL(5,2) DEFAULT NULL COMMENT 'Talla en cm al calcular',
    pnn_clasificacion VARCHAR(50) DEFAULT NULL COMMENT 'Clasificación nutricional',

    -- Control de vigencia
    pnn_vigente BOOLEAN DEFAULT TRUE COMMENT 'Si es el perfil activo',

    -- Auditoría
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Índices y restricciones
    FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
    INDEX idx_nin_vigente (nin_id, pnn_vigente),
    INDEX idx_creado (creado_en)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Perfil nutricional calculado para cada niño';
