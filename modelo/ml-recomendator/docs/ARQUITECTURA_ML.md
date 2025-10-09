# Arquitectura ML - Sistema de Evaluación Nutricional

## 1. Modelo Recomendado: Ensemble (Random Forest + Red Neuronal)

### Justificación Técnica

**Random Forest (70% peso):**
- ✅ Excelente con datos tabulares nutricionales
- ✅ Interpretable (feature importance)
- ✅ Robusto con datos faltantes
- ✅ No requiere normalización exhaustiva
- ✅ Funciona bien con datasets pequeños/medianos

**Red Neuronal (30% peso):**
- ✅ Captura patrones no lineales complejos
- ✅ Mejor para casos edge (desnutrición severa, obesidad)
- ✅ Aprende interacciones entre múltiples variables
- ✅ Escalable a más datos

### Comparación con Otras Opciones

| Modelo | Pros | Contras | Recomendación |
|--------|------|---------|---------------|
| **Random Forest** | Interpretable, robusto, rápido | Puede overfittear con muchas features | ✅ **SÍ - Base principal** |
| **Red Neuronal** | Captura complejidad, escalable | Caja negra, requiere más datos | ✅ **SÍ - Complemento** |
| Regresión Logística | Simple, rápido | Demasiado simple, asume linealidad | ❌ NO |
| Árboles Decisión | Interpretable | Inestable, overfitting fácil | ❌ NO |
| SVM | Bueno con alta dimensión | Lento, difícil interpretar | ❌ NO |
| XGBoost | Muy preciso | Más complejo de tunear | 🟡 Alternativa futura |

---

## 2. Arquitectura del Sistema

```
modelo/ml-recomendator/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py          # Interfaz abstracta
│   │   ├── rf_classifier.py       # Random Forest
│   │   ├── nn_classifier.py       # Red Neuronal (PyTorch/TF)
│   │   └── ensemble.py            # Ensemble RF+NN
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   ├── engineering.py         # Feature engineering
│   │   ├── who_calculator.py      # Cálculos OMS (BAZ, percentiles)
│   │   ├── temporal_features.py   # Features temporales
│   │   └── validators.py          # Validación de datos
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── preprocessor.py        # Limpieza y transformación
│   │   ├── trainer.py             # Entrenamiento
│   │   └── evaluator.py           # Métricas y validación
│   │
│   ├── inference/
│   │   ├── __init__.py
│   │   ├── predictor.py           # Predicción en producción
│   │   └── explainer.py           # Explicaciones (SHAP)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── db_connector.py        # Conexión a MySQL
│       └── metrics.py             # Métricas personalizadas
```

---

## 3. Features del Modelo

### 3.1 Features Existentes (desde SQL)

**Antropométricas básicas:**
- `age_months` - Edad en meses
- `sex` - Sexo (M/F)
- `weight_kg` - Peso en kg
- `height_cm` - Talla en cm
- `BMI` - Índice de masa corporal
- `baz` - Z-score BMI para edad (OMS)

**Contexto del niño:**
- `ent_id` - Entidad (hospital, clínica, etc.)
- `region` - Región geográfica
- `allergy_count` - Número de alergias

### 3.2 Features Nuevas a Implementar

#### A) Features Temporales (Tendencias)
- `bmi_velocity` - Cambio de IMC en últimos 3 meses
- `weight_velocity` - Cambio de peso en últimos 3 meses
- `height_velocity` - Cambio de talla en últimos 3 meses
- `baz_trend` - Tendencia del z-score (mejorando/empeorando)
- `measurements_count` - Número de mediciones históricas

#### B) Features de Adherencia
- `adherence_score` - Score de adherencia a menús (0-100)
- `adherence_consistency` - Consistencia en adherencia
- `menu_completion_rate` - % de menús completados

#### C) Features de Alergias
- `allergy_severity_max` - Severidad máxima de alergias (1-3)
- `food_allergy_count` - Alergias alimentarias específicas
- `has_severe_allergy` - Tiene alergia severa (bool)

#### D) Features Contextuales
- `altitude_m` - Altitud de la entidad (metros)
- `entity_type` - Tipo de entidad (hospital, clínica, etc.)
- `socioeconomic_proxy` - Proxy socioeconómico

#### E) Features de Síntomas
- `symptom_frequency` - Frecuencia de síntomas (últimos 30 días)
- `symptom_severity_avg` - Severidad promedio de síntomas
- `has_recent_symptoms` - Síntomas en últimos 7 días (bool)

#### F) Features Nutricionales
- `dietary_diversity_score` - Score de diversidad dietética
- `menu_kcal_avg` - Promedio de kcal en menús
- `protein_intake_score` - Score de ingesta proteica

---

## 4. Modificaciones a la Base de Datos

### 4.1 Nueva Tabla: `features_ml`

Tabla para almacenar features calculados para ML (evita recalcular constantemente).

```sql
CREATE TABLE features_ml (
  fml_id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id              BIGINT UNSIGNED NOT NULL,
  ant_id              BIGINT UNSIGNED NULL,
  
  -- Features temporales
  fml_bmi_velocity    DECIMAL(6,3) NULL COMMENT 'Cambio IMC últimos 3 meses',
  fml_weight_velocity DECIMAL(6,3) NULL COMMENT 'Cambio peso últimos 3 meses (kg)',
  fml_height_velocity DECIMAL(6,3) NULL COMMENT 'Cambio talla últimos 3 meses (cm)',
  fml_baz_trend       DECIMAL(6,3) NULL COMMENT 'Tendencia z-score',
  fml_measurements_count SMALLINT UNSIGNED NULL COMMENT 'Número de mediciones',
  
  -- Features de adherencia
  fml_adherence_score DECIMAL(5,2) NULL COMMENT 'Score adherencia 0-100',
  fml_adherence_consistency DECIMAL(5,2) NULL COMMENT 'Consistencia adherencia',
  fml_menu_completion_rate DECIMAL(5,2) NULL COMMENT '% menús completados',
  
  -- Features de alergias
  fml_allergy_count   SMALLINT UNSIGNED NULL COMMENT 'Total alergias',
  fml_allergy_severity_max TINYINT UNSIGNED NULL COMMENT '1=LEVE, 2=MODERADA, 3=SEVERA',
  fml_food_allergy_count SMALLINT UNSIGNED NULL COMMENT 'Alergias alimentarias',
  fml_has_severe_allergy BOOLEAN NULL COMMENT 'Tiene alergia severa',
  
  -- Features de síntomas
  fml_symptom_frequency SMALLINT UNSIGNED NULL COMMENT 'Síntomas últimos 30 días',
  fml_symptom_severity_avg DECIMAL(4,2) NULL COMMENT 'Severidad promedio síntomas',
  fml_has_recent_symptoms BOOLEAN NULL COMMENT 'Síntomas últimos 7 días',
  
  -- Features nutricionales
  fml_dietary_diversity_score DECIMAL(5,2) NULL COMMENT 'Score diversidad dietética',
  fml_menu_kcal_avg INT NULL COMMENT 'Promedio kcal menús',
  fml_protein_intake_score DECIMAL(5,2) NULL COMMENT 'Score ingesta proteica',
  
  -- Metadata
  fml_calculated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fml_version         VARCHAR(20) NOT NULL DEFAULT 'v1.0' COMMENT 'Versión del cálculo',
  
  CONSTRAINT fk_fml_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_fml_antropometria FOREIGN KEY (ant_id) REFERENCES antropometrias(ant_id) ON DELETE SET NULL,
  INDEX idx_fml_nino_fecha (nin_id, fml_calculated_at),
  INDEX idx_fml_version (fml_version)
) ENGINE=InnoDB COMMENT='Features calculados para ML';
```

### 4.2 Modificar Tabla: `entidades`

Agregar información geográfica para features contextuales.

```sql
ALTER TABLE entidades
  ADD COLUMN ent_altitud_m INT NULL COMMENT 'Altitud en metros sobre nivel del mar' AFTER ent_longitud,
  ADD COLUMN ent_zona ENUM('URBANA','RURAL','PERIURBANA') NULL COMMENT 'Tipo de zona' AFTER ent_altitud_m,
  ADD COLUMN ent_poblacion_aprox INT NULL COMMENT 'Población aproximada del área' AFTER ent_zona;

CREATE INDEX idx_entidades_zona ON entidades(ent_zona);
```

### 4.3 Modificar Tabla: `adherencias`

Agregar campos para calcular scores de adherencia.

```sql
ALTER TABLE adherencias
  ADD COLUMN adh_porcentaje DECIMAL(5,2) NULL COMMENT 'Porcentaje de adherencia 0-100' AFTER adh_estado,
  ADD COLUMN adh_comentario_tutor TEXT NULL COMMENT 'Comentario del tutor' AFTER adh_notas,
  ADD COLUMN adh_dificultad ENUM('NINGUNA','BAJA','MEDIA','ALTA') NULL COMMENT 'Dificultad reportada' AFTER adh_comentario_tutor;

CREATE INDEX idx_adh_nino_fecha ON adherencias(nin_id, adh_registrado_en);
```

### 4.4 Modificar Tabla: `sintomas`

Mejorar estructura para análisis ML.

```sql
ALTER TABLE sintomas
  ADD COLUMN sin_severidad ENUM('LEVE','MODERADO','SEVERO') NULL COMMENT 'Severidad del síntoma' AFTER sin_grado,
  ADD COLUMN sin_duracion_dias SMALLINT UNSIGNED NULL COMMENT 'Duración en días' AFTER sin_severidad,
  ADD COLUMN sin_relacionado_menu BOOLEAN NULL DEFAULT FALSE COMMENT 'Relacionado con menú' AFTER sin_duracion_dias;

CREATE INDEX idx_sin_nino_fecha ON sintomas(nin_id, sin_fecha);
```

### 4.5 Nueva Tabla: `menus_nutrientes`

Para calcular scores nutricionales de los menús.

```sql
CREATE TABLE menus_nutrientes (
  mn_id       BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  men_id      BIGINT UNSIGNED NOT NULL,
  
  -- Macronutrientes
  mn_kcal_total      INT NULL COMMENT 'Calorías totales',
  mn_proteina_g      DECIMAL(8,2) NULL COMMENT 'Proteína en gramos',
  mn_carbohidratos_g DECIMAL(8,2) NULL COMMENT 'Carbohidratos en gramos',
  mn_grasas_g        DECIMAL(8,2) NULL COMMENT 'Grasas en gramos',
  mn_fibra_g         DECIMAL(8,2) NULL COMMENT 'Fibra en gramos',
  
  -- Micronutrientes clave
  mn_hierro_mg       DECIMAL(8,2) NULL COMMENT 'Hierro en mg',
  mn_calcio_mg       DECIMAL(8,2) NULL COMMENT 'Calcio en mg',
  mn_vitamina_a_ug   DECIMAL(8,2) NULL COMMENT 'Vitamina A en µg',
  mn_vitamina_c_mg   DECIMAL(8,2) NULL COMMENT 'Vitamina C en mg',
  mn_zinc_mg         DECIMAL(8,2) NULL COMMENT 'Zinc en mg',
  
  -- Scores calculados
  mn_diversity_score DECIMAL(5,2) NULL COMMENT 'Score de diversidad 0-100',
  mn_quality_score   DECIMAL(5,2) NULL COMMENT 'Score de calidad nutricional 0-100',
  
  calculado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_mn_menu FOREIGN KEY (men_id) REFERENCES menus(men_id) ON DELETE CASCADE,
  UNIQUE KEY uk_menu_nutrientes (men_id)
) ENGINE=InnoDB COMMENT='Información nutricional calculada de menús';
```

### 4.6 Nueva Tabla: `predicciones_ml`

Para almacenar predicciones del modelo ML.

```sql
CREATE TABLE predicciones_ml (
  pml_id              BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id              BIGINT UNSIGNED NOT NULL,
  ant_id              BIGINT UNSIGNED NULL,
  fml_id              BIGINT UNSIGNED NULL,
  
  -- Predicción
  pml_clasificacion   ENUM('NORMAL','RIESGO','MODERADO','SEVERO') NOT NULL,
  pml_probabilidad    DECIMAL(5,4) NOT NULL COMMENT 'Probabilidad de la clase predicha',
  pml_score_riesgo    DECIMAL(6,4) NOT NULL COMMENT 'Score de riesgo 0-1',
  
  -- Probabilidades por clase
  pml_prob_normal     DECIMAL(5,4) NULL,
  pml_prob_riesgo     DECIMAL(5,4) NULL,
  pml_prob_moderado   DECIMAL(5,4) NULL,
  pml_prob_severo     DECIMAL(5,4) NULL,
  
  -- Metadata del modelo
  pml_modelo_tipo     VARCHAR(50) NOT NULL COMMENT 'rf, nn, ensemble',
  pml_modelo_version  VARCHAR(20) NOT NULL COMMENT 'Versión del modelo',
  pml_features_json   JSON NULL COMMENT 'Features usados en la predicción',
  pml_explicacion_json JSON NULL COMMENT 'SHAP values o feature importance',
  
  -- Validación
  pml_validado        BOOLEAN NULL COMMENT 'Validado por nutricionista',
  pml_validado_por    BIGINT UNSIGNED NULL COMMENT 'usr_id del nutricionista',
  pml_validado_en     DATETIME NULL,
  pml_feedback        TEXT NULL COMMENT 'Feedback del nutricionista',
  
  creado_en           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT fk_pml_nino FOREIGN KEY (nin_id) REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_pml_antropometria FOREIGN KEY (ant_id) REFERENCES antropometrias(ant_id) ON DELETE SET NULL,
  CONSTRAINT fk_pml_features FOREIGN KEY (fml_id) REFERENCES features_ml(fml_id) ON DELETE SET NULL,
  CONSTRAINT fk_pml_validador FOREIGN KEY (pml_validado_por) REFERENCES usuarios(usr_id) ON DELETE SET NULL,
  
  INDEX idx_pml_nino_fecha (nin_id, creado_en),
  INDEX idx_pml_clasificacion (pml_clasificacion),
  INDEX idx_pml_modelo (pml_modelo_tipo, pml_modelo_version)
) ENGINE=InnoDB COMMENT='Predicciones del modelo ML';
```

---

## 5. Procedimientos Almacenados Nuevos

### 5.1 `sp_calcular_features_ml`

Calcula todos los features ML para un niño.

```sql
CREATE PROCEDURE sp_calcular_features_ml(
  IN p_nin_id BIGINT UNSIGNED,
  IN p_ant_id BIGINT UNSIGNED
)
BEGIN
  DECLARE v_bmi_velocity DECIMAL(6,3);
  DECLARE v_weight_velocity DECIMAL(6,3);
  DECLARE v_adherence_score DECIMAL(5,2);
  DECLARE v_allergy_count SMALLINT;
  DECLARE v_symptom_frequency SMALLINT;
  
  -- Calcular velocidad de IMC (últimos 3 meses)
  SELECT 
    (a1.ant_peso_kg / POWER(a1.ant_talla_cm/100, 2)) - 
    (a2.ant_peso_kg / POWER(a2.ant_talla_cm/100, 2))
  INTO v_bmi_velocity
  FROM antropometrias a1
  LEFT JOIN antropometrias a2 ON a2.nin_id = a1.nin_id 
    AND a2.ant_fecha = DATE_SUB(a1.ant_fecha, INTERVAL 3 MONTH)
  WHERE a1.ant_id = p_ant_id;
  
  -- Calcular score de adherencia (últimos 30 días)
  SELECT AVG(
    CASE adh_estado
      WHEN 'OK' THEN 100
      WHEN 'PARCIAL' THEN 50
      WHEN 'NO' THEN 0
    END
  ) INTO v_adherence_score
  FROM adherencias
  WHERE nin_id = p_nin_id
    AND adh_registrado_en >= DATE_SUB(NOW(), INTERVAL 30 DAY);
  
  -- Contar alergias activas
  SELECT COUNT(*) INTO v_allergy_count
  FROM ninos_alergias
  WHERE nin_id = p_nin_id AND na_activo = 1;
  
  -- Frecuencia de síntomas (últimos 30 días)
  SELECT COUNT(*) INTO v_symptom_frequency
  FROM sintomas
  WHERE nin_id = p_nin_id
    AND sin_fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY);
  
  -- Insertar o actualizar features
  INSERT INTO features_ml (
    nin_id, ant_id,
    fml_bmi_velocity,
    fml_adherence_score,
    fml_allergy_count,
    fml_symptom_frequency,
    fml_calculated_at
  ) VALUES (
    p_nin_id, p_ant_id,
    v_bmi_velocity,
    v_adherence_score,
    v_allergy_count,
    v_symptom_frequency,
    NOW()
  )
  ON DUPLICATE KEY UPDATE
    fml_bmi_velocity = v_bmi_velocity,
    fml_adherence_score = v_adherence_score,
    fml_allergy_count = v_allergy_count,
    fml_symptom_frequency = v_symptom_frequency,
    fml_calculated_at = NOW();
    
  -- Retornar features calculados
  SELECT * FROM features_ml 
  WHERE nin_id = p_nin_id AND ant_id = p_ant_id
  ORDER BY fml_calculated_at DESC LIMIT 1;
END;
```

---

## 6. Plan de Implementación

### Fase 1: Preparación de Datos (Semana 1)
- [ ] Ejecutar migraciones de BD
- [ ] Crear procedimientos almacenados
- [ ] Implementar `features/engineering.py`
- [ ] Implementar `utils/db_connector.py`
- [ ] Extraer dataset histórico

### Fase 2: Baseline Random Forest (Semana 2)
- [ ] Implementar `models/base_model.py`
- [ ] Implementar `models/rf_classifier.py`
- [ ] Entrenar modelo baseline
- [ ] Evaluar métricas (accuracy, precision, recall, F1)
- [ ] Análisis de feature importance

### Fase 3: Red Neuronal (Semana 3)
- [ ] Implementar `models/nn_classifier.py`
- [ ] Arquitectura: [64, 32] con dropout 0.2
- [ ] Entrenar y validar
- [ ] Comparar con RF

### Fase 4: Ensemble (Semana 4)
- [ ] Implementar `models/ensemble.py`
- [ ] Optimizar pesos (RF: 70%, NN: 30%)
- [ ] Validación cruzada
- [ ] Selección de modelo final

### Fase 5: Explicabilidad (Semana 5)
- [ ] Implementar `inference/explainer.py`
- [ ] Integrar SHAP values
- [ ] Conectar con LLM para explicaciones
- [ ] Dashboard de interpretación

### Fase 6: Producción (Semana 6)
- [ ] Implementar `inference/predictor.py`
- [ ] Integrar con API FastAPI
- [ ] Tests de integración
- [ ] Monitoreo de predicciones
- [ ] Documentación

---

## 7. Métricas de Éxito

### Métricas Técnicas
- **Accuracy global**: ≥ 85%
- **Recall para casos SEVEROS**: ≥ 90% (crítico para salud)
- **Precision para NORMAL**: ≥ 80%
- **F1-Score promedio**: ≥ 0.83
- **AUC-ROC**: ≥ 0.88
- **Tiempo de inferencia**: < 100ms

### Métricas de Negocio
- **Reducción de falsos negativos**: -30% vs sistema actual
- **Satisfacción de nutricionistas**: ≥ 4/5
- **Adopción del sistema**: ≥ 70% de nutricionistas
- **Tiempo de evaluación**: -50% vs manual

---

## 8. Consideraciones Técnicas

### Manejo de Datos Desbalanceados
- Usar `class_weight='balanced'` en RF
- Oversampling (SMOTE) para clase minoritaria
- Focal Loss en NN para casos severos

### Validación
- K-Fold Cross-Validation (k=5)
- Stratified split para mantener distribución de clases
- Validación temporal (train en datos antiguos, test en recientes)

### Monitoreo en Producción
- Drift detection (distribución de features)
- Performance monitoring (métricas por semana)
- Feedback loop con nutricionistas
- Re-entrenamiento trimestral

---

## 9. Próximos Pasos

1. ✅ Revisar y aprobar arquitectura
2. ⏳ Ejecutar migraciones de BD
3. ⏳ Implementar feature engineering
4. ⏳ Entrenar modelo baseline
5. ⏳ Evaluar y iterar
