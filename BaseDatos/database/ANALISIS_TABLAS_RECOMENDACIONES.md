# 📊 ANÁLISIS DE TABLAS PARA SISTEMA DE RECOMENDACIONES PERSONALIZADAS

## ✅ TABLAS QUE YA TIENES (Y ESTÁN BIEN)

### 1. **ninos** ✅
```sql
- nin_id (PK)
- usr_id_tutor
- usr_id_propietario
- ent_id (entidad/región)
- nin_nombres
- nin_fecha_nac (para calcular edad)
- nin_sexo
```
**Estado:** COMPLETA - Tiene todo lo necesario

### 2. **menus** ✅
```sql
- men_id (PK)
- nin_id (FK) ← Relación 1:N con niños ✅
- men_generado_por (IA/NUTRICIONISTA)
- men_inicio, men_fin
- men_kcal_total
- men_estado (BORRADOR/APROBADO/ARCHIVADO)
```
**Estado:** COMPLETA - Ya maneja múltiples menús por niño

### 3. **menus_items** ✅
```sql
- mei_id (PK)
- men_id (FK)
- mei_dia_idx (día 1-7)
- mei_comida (DESAYUNO/ALMUERZO/CENA/REFACCION)
- rec_id (FK a recetas)
- mei_kcal
```
**Estado:** COMPLETA - Detalle de cada comida del plan

### 4. **recetas** ✅
```sql
- rec_id (PK)
- rec_nombre
- rec_instrucciones
- rec_activo
```
**Estado:** COMPLETA

### 5. **recetas_ingredientes** ✅
```sql
- rec_id, ali_id (PK compuesta)
- ri_cantidad
- ri_unidad
```
**Estado:** COMPLETA

### 6. **recetas_comidas** ✅
```sql
- rec_id, rc_comida (PK compuesta)
- rc_comida (DESAYUNO/ALMUERZO/CENA/REFACCION)
```
**Estado:** COMPLETA - Clasifica recetas por tipo de comida

### 7. **alimentos** + **alimentos_nutrientes** ✅
**Estado:** COMPLETAS - Información nutricional base

### 8. **disponibilidad_alimentos** ✅
```sql
- ali_id, ent_id
- dis_periodo (Q1-Q4)
- dis_disponible
- dis_region
```
**Estado:** COMPLETA - Filtrado regional

### 9. **antropometrias** + **evaluaciones_nutricionales** ✅
**Estado:** COMPLETAS - Para calcular requerimientos

### 10. **ninos_alergias** + **tipos_alergias** ✅
**Estado:** COMPLETAS - Restricciones alimentarias

---

## 🆕 TABLAS QUE NECESITAS AGREGAR

### 1. **perfil_nutricional_nino** (NUEVA) 🔴
**Propósito:** Almacenar los requerimientos nutricionales calculados para cada niño

```sql
CREATE TABLE perfil_nutricional_nino (
  pnn_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id BIGINT UNSIGNED NOT NULL,

  -- Requerimientos diarios
  pnn_calorias_diarias INT NOT NULL COMMENT 'kcal/día',
  pnn_proteinas_g DECIMAL(6,2) NOT NULL,
  pnn_carbohidratos_g DECIMAL(6,2) NOT NULL,
  pnn_grasas_g DECIMAL(6,2) NOT NULL,

  -- Micronutrientes importantes
  pnn_hierro_mg DECIMAL(6,2) NULL,
  pnn_calcio_mg DECIMAL(6,2) NULL,
  pnn_vitamina_a_ug DECIMAL(6,2) NULL,
  pnn_vitamina_c_mg DECIMAL(6,2) NULL,
  pnn_zinc_mg DECIMAL(6,2) NULL,
  pnn_fibra_g DECIMAL(6,2) NULL,

  -- Metadata
  pnn_edad_meses SMALLINT UNSIGNED NOT NULL,
  pnn_peso_kg DECIMAL(5,2) NULL,
  pnn_talla_cm DECIMAL(5,2) NULL,
  pnn_clasificacion ENUM('DESNUTRICION_SEVERA','DESNUTRICION','RIESGO','NORMAL','SOBREPESO','OBESIDAD') NULL,
  pnn_metodo_calculo VARCHAR(50) NOT NULL DEFAULT 'OMS_FAO' COMMENT 'Método usado para calcular',
  pnn_fecha_calculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  pnn_vigente BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Solo uno vigente por niño',

  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_pnn_nino FOREIGN KEY (nin_id)
    REFERENCES ninos(nin_id) ON DELETE CASCADE,

  INDEX idx_pnn_nino_vigente (nin_id, pnn_vigente)
) ENGINE=InnoDB;
```

**¿Por qué?**
- Evita recalcular requerimientos cada vez
- Histórico de cambios en requerimientos
- Base para generar planes personalizados

---

### 2. **ninos_restricciones_alimentos** (NUEVA) 🔴
**Propósito:** Restricciones específicas de alimentos (complementa ninos_alergias)

```sql
CREATE TABLE ninos_restricciones_alimentos (
  nra_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nin_id BIGINT UNSIGNED NOT NULL,
  ali_id INT UNSIGNED NOT NULL COMMENT 'Alimento restringido',

  nra_tipo ENUM('ALERGIA','INTOLERANCIA','PREFERENCIA','CULTURAL','RELIGIOSA') NOT NULL,
  nra_severidad ENUM('LEVE','MODERADA','SEVERA') NOT NULL DEFAULT 'MODERADA',
  nra_notas TEXT NULL,
  nra_activo BOOLEAN NOT NULL DEFAULT TRUE,

  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  UNIQUE KEY uk_nino_alimento (nin_id, ali_id),
  CONSTRAINT fk_nra_nino FOREIGN KEY (nin_id)
    REFERENCES ninos(nin_id) ON DELETE CASCADE,
  CONSTRAINT fk_nra_alimento FOREIGN KEY (ali_id)
    REFERENCES alimentos(ali_id) ON DELETE CASCADE
) ENGINE=InnoDB;
```

**¿Por qué?**
- Filtrar recetas que contengan alimentos prohibidos
- Más específico que alergias generales
- Ejemplo: niño alérgico a "leche" → excluir todas las recetas con leche

---

### 3. **menus_feedback** (NUEVA - OPCIONAL PERO RECOMENDADA) 🟡
**Propósito:** Aprender de las preferencias del niño para mejorar recomendaciones

```sql
CREATE TABLE menus_feedback (
  mf_id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  mei_id BIGINT UNSIGNED NOT NULL COMMENT 'Item del menú evaluado',
  nin_id BIGINT UNSIGNED NOT NULL,

  mf_completado BOOLEAN NOT NULL DEFAULT FALSE COMMENT '¿Se comió?',
  mf_rating TINYINT NULL COMMENT '1-5 estrellas',
  mf_notas TEXT NULL COMMENT 'Comentarios del tutor',
  mf_fecha_consumo DATE NOT NULL,

  creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_mf_item FOREIGN KEY (mei_id)
    REFERENCES menus_items(mei_id) ON DELETE CASCADE,
  CONSTRAINT fk_mf_nino FOREIGN KEY (nin_id)
    REFERENCES ninos(nin_id) ON DELETE CASCADE,

  INDEX idx_mf_nino_fecha (nin_id, mf_fecha_consumo)
) ENGINE=InnoDB;
```

**¿Por qué?**
- Mejorar recomendaciones futuras
- Detectar patrones de rechazo
- Ajustar el LLM con preferencias reales

---

### 4. **recetas_nutrientes_cache** (NUEVA - OPTIMIZACIÓN) 🟡
**Propósito:** Pre-calcular valores nutricionales totales de cada receta

```sql
CREATE TABLE recetas_nutrientes_cache (
  rec_id INT UNSIGNED NOT NULL,
  nutri_id SMALLINT UNSIGNED NOT NULL,
  rnc_cantidad_total DECIMAL(12,4) NOT NULL COMMENT 'Cantidad total en la receta',
  rnc_cantidad_porcion DECIMAL(12,4) NULL COMMENT 'Por porción estándar',

  actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (rec_id, nutri_id),
  CONSTRAINT fk_rnc_receta FOREIGN KEY (rec_id)
    REFERENCES recetas(rec_id) ON DELETE CASCADE,
  CONSTRAINT fk_rnc_nutriente FOREIGN KEY (nutri_id)
    REFERENCES nutrientes(nutri_id) ON DELETE CASCADE
) ENGINE=InnoDB;
```

**¿Por qué?**
- Acelerar búsqueda de recetas candidatas
- Evitar JOINs complejos en tiempo real
- Filtrar rápido por rangos nutricionales

---

### 5. **entidades** - AGREGAR CAMPOS (MODIFICACIÓN) 🟠
**Propósito:** Información geográfica para disponibilidad regional

```sql
ALTER TABLE entidades
  ADD COLUMN ent_altitud_m INT NULL COMMENT 'Altitud en metros' AFTER ent_longitud,
  ADD COLUMN ent_zona ENUM('URBANA','RURAL','PERIURBANA') NULL AFTER ent_altitud_m,
  ADD COLUMN ent_poblacion_aprox INT NULL AFTER ent_zona;
```

**¿Por qué?**
- Filtrar recetas por disponibilidad regional
- Considerar altitud para requerimientos calóricos
- Zona urbana/rural afecta acceso a alimentos

---

## 📋 RESUMEN DE PRIORIDADES

### 🔴 CRÍTICAS (Implementar YA)
1. ✅ **perfil_nutricional_nino** - Base del sistema
2. ✅ **ninos_restricciones_alimentos** - Seguridad alimentaria

### 🟡 IMPORTANTES (Implementar pronto)
3. **recetas_nutrientes_cache** - Performance
4. **menus_feedback** - Mejora continua
5. **entidades (modificación)** - Filtrado regional

### 🟢 OPCIONALES (Futuro)
- Tabla de "planes_favoritos" para reutilizar
- Tabla de "sustituciones_recetas" para alternativas
- Tabla de "historial_generacion_menus" para auditoría

---

## 🎯 TABLAS QUE **NO** NECESITAS

### ❌ planes_comidas (del ejemplo)
**Razón:** Ya tienes `menus` que hace exactamente lo mismo

### ❌ planes_comidas_detalle (del ejemplo)
**Razón:** Ya tienes `menus_items` que hace exactamente lo mismo

### ❌ Tabla separada de "perfil_nutricional_nino.restricciones"
**Razón:** Ya tienes `ninos_alergias` + la nueva `ninos_restricciones_alimentos`

---

## 🔄 MAPEO: EJEMPLO → TU SISTEMA

| Ejemplo Original | Tu Sistema Actual | Estado |
|-----------------|-------------------|--------|
| `planes_comidas` | `menus` | ✅ Ya existe |
| `planes_comidas_detalle` | `menus_items` | ✅ Ya existe |
| `pc_id` | `men_id` | ✅ Mismo concepto |
| `pcd_dia_semana` | `mei_dia_idx` | ✅ Mismo concepto |
| `pcd_tipo_comida` | `mei_comida` | ✅ Mismo concepto |
| `pcd_completado` | Nueva: `menus_feedback.mf_completado` | 🆕 Agregar |
| `pcd_rating` | Nueva: `menus_feedback.mf_rating` | 🆕 Agregar |
| `perfil_nutricional_nino` | No existe | 🆕 Agregar |
| `ninos_restricciones` | Parcial: `ninos_alergias` | 🆕 Complementar |

---

## 🚀 SIGUIENTE PASO

Crear el archivo SQL con:
1. Las 2 tablas críticas (perfil_nutricional_nino + ninos_restricciones_alimentos)
2. Las modificaciones a entidades
3. Los índices necesarios
4. Datos de ejemplo

¿Procedo a crear el archivo `migracion_recomendaciones_personalizadas.sql`?
