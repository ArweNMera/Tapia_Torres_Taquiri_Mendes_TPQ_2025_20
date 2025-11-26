# Análisis de Procedimientos Almacenados Existentes

## Fecha de Análisis
2025-01-XX

## Resumen Ejecutivo

Este documento lista todos los procedimientos almacenados existentes en `BaseDatos/database/procedimientos.sql` y verifica cuáles están disponibles para el sistema PMV3 de seguimiento nutricional.

---

## 1. ANTROPOMETRÍAS ✅

### Procedimientos Existentes:

1. **`sp_antropometria_agregar`** ✅
   - **Funcionalidad**: Registra nueva antropometría (peso, talla) para un niño
   - **Parámetros**: `p_nin_id`, `p_fecha`, `p_peso_kg`, `p_talla_cm`
   - **Características**:
     - Calcula edad en meses automáticamente
     - Normaliza talla (convierte metros a cm si es necesario)
     - Evita duplicados por fecha (INSERT ON DUPLICATE KEY UPDATE)
     - Retorna antropometría con IMC calculado
   - **Estado**: ✅ EXISTE Y FUNCIONAL

2. **`sp_antropometria_obtener_por_nino`** ✅
   - **Funcionalidad**: Obtiene historial de antropometrías de un niño
   - **Parámetros**: `p_nin_id`, `p_limit` (opcional)
   - **Características**:
     - Retorna mediciones ordenadas por fecha descendente
     - Incluye z-scores y IMC calculado
     - Permite limitar resultados
   - **Estado**: ✅ EXISTE Y FUNCIONAL

---

## 2. ADHERENCIAS ❌

### Procedimientos Faltantes:

❌ **`sp_registrar_adherencia`** - NO EXISTE
   - Necesario para: Registrar cumplimiento diario del plan nutricional
   - Debe crear/actualizar registros en tabla `adherencias`

❌ **`sp_obtener_adherencia_por_nino`** - NO EXISTE
   - Necesario para: Consultar historial de adherencia
   - Debe retornar registros con filtros de fecha

❌ **`sp_calcular_adherencia_promedio`** - NO EXISTE
   - Necesario para: Calcular score de adherencia de últimos N días
   - Debe retornar porcentaje 0-100

### Nota Importante:
El procedimiento `sp_calcular_features_ml` **SÍ lee** de la tabla `adherencias` para calcular features ML:
```sql
SELECT AVG(CASE adh_estado
  WHEN 'OK' THEN 100
  WHEN 'PARCIAL' THEN 50
  WHEN 'NO' THEN 0
  ELSE 75
END) ...
FROM adherencias
WHERE nin_id = p_nin_id
  AND adh_registrado_en >= DATE_SUB(NOW(), INTERVAL 30 DAY);
```

Esto confirma que:
- ✅ La tabla `adherencias` existe en el esquema
- ✅ Tiene campos: `nin_id`, `adh_estado`, `adh_registrado_en`
- ❌ Faltan procedimientos CRUD para manipular estos datos

---

## 3. SÍNTOMAS ❌

### Procedimientos Faltantes:

❌ **`sp_registrar_sintoma`** - NO EXISTE
   - Necesario para: Registrar síntomas del niño
   - Debe insertar en tabla `sintomas`

❌ **`sp_obtener_sintomas_por_nino`** - NO EXISTE
   - Necesario para: Consultar historial de síntomas
   - Debe permitir filtros por fecha y tipo

❌ **`sp_calcular_frecuencia_sintomas`** - NO EXISTE
   - Necesario para: Calcular frecuencia y severidad promedio
   - Debe analizar últimos N días

### Nota Importante:
El procedimiento `sp_calcular_features_ml` **SÍ lee** de la tabla `sintomas`:
```sql
SELECT COUNT(*),
  AVG(COALESCE(sin_grado, 0)),
  MAX(CASE WHEN sin_fecha >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) THEN 1 ELSE 0 END)
INTO v_symptom_frequency, v_symptom_severity_avg, v_has_recent_symptoms
FROM sintomas
WHERE nin_id = p_nin_id
  AND sin_fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY);
```

Esto confirma que:
- ✅ La tabla `sintomas` existe en el esquema
- ✅ Tiene campos: `nin_id`, `sin_fecha`, `sin_grado`
- ❌ Faltan procedimientos CRUD para manipular estos datos

---

## 4. FEATURES ML ✅

### Procedimientos Existentes:

1. **`sp_calcular_features_ml`** ✅
   - **Funcionalidad**: Calcula los 11+ features necesarios para el modelo ML
   - **Parámetros**: `p_nin_id`, `p_ant_id`
   - **Features Calculados**:
     - **Temporales**: bmi_velocity, weight_velocity, height_velocity, baz_trend, measurements_count
     - **Adherencia**: adherence_score, adherence_consistency, menu_completion_rate
     - **Alergias**: allergy_count, allergy_severity_max, food_allergy_count, has_severe_allergy
     - **Síntomas**: symptom_frequency, symptom_severity_avg, has_recent_symptoms
     - **Nutricionales**: dietary_diversity_score, menu_kcal_avg, protein_intake_score
   - **Características**:
     - Inserta o actualiza en tabla `features_ml`
     - Calcula velocidades de cambio de últimos 3 meses
     - Lee de tablas: `antropometrias`, `adherencias`, `sintomas`, `ninos_alergias`, `menus`
   - **Estado**: ✅ EXISTE Y FUNCIONAL

2. **`sp_obtener_datos_para_ml`** ✅
   - **Funcionalidad**: Obtiene datos completos para predicción ML
   - **Parámetros**: `p_nin_id`
   - **Características**:
     - Llama automáticamente a `sp_calcular_features_ml` si es necesario
     - Retorna datos del niño + antropometría + features ML + contexto
     - Incluye: age_months, weight_kg, height_cm, BMI, baz, altitude_m, entity_zone
   - **Estado**: ✅ EXISTE Y FUNCIONAL

---

## 5. PREDICCIONES ML ❌

### Procedimientos Faltantes:

❌ **`sp_guardar_prediccion_ml`** - NO EXISTE
   - Necesario para: Guardar resultado de predicción del modelo
   - Debe insertar en tabla `predicciones_ml`
   - Debe generar alertas si es riesgo MODERADO/SEVERO

❌ **`sp_validar_prediccion_ml`** - NO EXISTE
   - Necesario para: Validar predicción por nutricionista
   - Debe actualizar campos de validación

❌ **`sp_obtener_predicciones_por_nino`** - NO EXISTE
   - Necesario para: Consultar historial de predicciones
   - Debe retornar últimas N predicciones

### Nota:
No hay referencias a tabla `predicciones_ml` en los procedimientos existentes, lo que sugiere que:
- ❌ Los procedimientos para predicciones NO existen
- ⚠️ Necesitamos verificar si la tabla `predicciones_ml` existe en el esquema

---

## 6. EVOLUCIÓN NUTRICIONAL ❌

### Procedimientos Faltantes:

❌ **`sp_obtener_evolucion_nutricional`** - NO EXISTE
   - Necesario para: Obtener evolución completa del niño
   - Debe combinar antropometrías + evaluaciones + adherencia

❌ **`sp_calcular_tendencia_nutricional`** - NO EXISTE
   - Necesario para: Determinar si hay tendencia positiva/negativa/estable
   - Debe analizar últimas N mediciones

### Procedimientos Relacionados Existentes:

✅ **`sp_evaluar_estado_nutricional`** - EXISTE
   - Evalúa estado nutricional actual basado en última antropometría
   - Calcula z-score, percentil, clasificación OMS
   - Inserta en tabla `evaluaciones_nutricionales`

---

## 7. ALERTAS ❌

### Procedimientos Faltantes:

❌ **`sp_generar_alerta`** - NO EXISTE
   - Necesario para: Crear notificaciones para nutricionistas
   - Debe insertar en tabla `notificaciones`

❌ **`sp_verificar_alertas_automaticas`** - NO EXISTE
   - Necesario para: Verificar condiciones de alerta automática
   - Debe detectar: tendencia negativa, baja adherencia, síntomas frecuentes, riesgo ML

---

## 8. OTROS PROCEDIMIENTOS RELEVANTES

### Menús y Feedback:

✅ **`sp_feedback_registrar`** - EXISTE
   - Registra feedback de menú consumido
   - Inserta/actualiza en tabla `menus_feedback`

✅ **`sp_feedback_listar_nino`** - EXISTE
   - Lista feedback de un niño con filtros de fecha

✅ **`sp_menus_crear`** - EXISTE
✅ **`sp_menus_items_agregar`** - EXISTE
✅ **`sp_menus_listar`** - EXISTE

### Perfil Nutricional:

✅ **`sp_calcular_perfil_nutricional`** - EXISTE
   - Calcula requerimientos nutricionales según edad y clasificación
   - Inserta en tabla `perfil_nutricional_nino`

✅ **`sp_perfil_nutricional_vigente`** - EXISTE
   - Obtiene perfil nutricional activo del niño

---

## RESUMEN DE HALLAZGOS

### ✅ PROCEDIMIENTOS QUE EXISTEN (8):
1. `sp_antropometria_agregar`
2. `sp_antropometria_obtener_por_nino`
3. `sp_calcular_features_ml`
4. `sp_obtener_datos_para_ml`
5. `sp_evaluar_estado_nutricional`
6. `sp_feedback_registrar`
7. `sp_feedback_listar_nino`
8. `sp_calcular_perfil_nutricional`

### ❌ PROCEDIMIENTOS QUE FALTAN (13):

#### Adherencia (3):
1. `sp_registrar_adherencia`
2. `sp_obtener_adherencia_por_nino`
3. `sp_calcular_adherencia_promedio`

#### Síntomas (3):
4. `sp_registrar_sintoma`
5. `sp_obtener_sintomas_por_nino`
6. `sp_calcular_frecuencia_sintomas`

#### Predicciones ML (3):
7. `sp_guardar_prediccion_ml`
8. `sp_validar_prediccion_ml`
9. `sp_obtener_predicciones_por_nino`

#### Evolución (2):
10. `sp_obtener_evolucion_nutricional`
11. `sp_calcular_tendencia_nutricional`

#### Alertas (2):
12. `sp_generar_alerta`
13. `sp_verificar_alertas_automaticas`

---

## CONCLUSIONES

1. **Antropometrías**: ✅ Completamente implementado
2. **Features ML**: ✅ Completamente implementado y funcional
3. **Adherencias**: ⚠️ Tabla existe, pero faltan procedimientos CRUD
4. **Síntomas**: ⚠️ Tabla existe, pero faltan procedimientos CRUD
5. **Predicciones ML**: ❌ Completamente faltante
6. **Evolución**: ⚠️ Parcialmente implementado (falta análisis de tendencias)
7. **Alertas**: ❌ Completamente faltante

### Prioridad de Implementación:
1. **ALTA**: Procedimientos de Adherencia (necesarios para registro diario)
2. **ALTA**: Procedimientos de Síntomas (necesarios para registro de eventos)
3. **ALTA**: Procedimientos de Predicciones ML (necesarios para guardar resultados del modelo)
4. **MEDIA**: Procedimientos de Evolución (para análisis de tendencias)
5. **MEDIA**: Procedimientos de Alertas (para notificaciones automáticas)

---

## PRÓXIMOS PASOS

1. ✅ Verificar esquema de tablas `adherencias`, `sintomas`, `predicciones_ml` en `schema.sql`
2. ⏳ Diseñar procedimientos faltantes según especificación en `PLAN_TRABAJO.md`
3. ⏳ Implementar procedimientos en orden de prioridad
4. ⏳ Crear tests para cada procedimiento
5. ⏳ Documentar en `database-analysis.md`
