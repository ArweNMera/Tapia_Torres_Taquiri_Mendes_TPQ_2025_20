# 📋 Plan de Trabajo Completo - PMV3: Seguimiento y Monitoreo Nutricional

## 🎯 Objetivo

Implementar el sistema de seguimiento y monitoreo nutricional continuo (PMV3) que permita:
- Registrar adherencia y síntomas
- Visualizar evolución antropométrica con gráficos
- Generar reportes PDF exportables
- Predecir evolución nutricional usando el modelo LightGBM existente
- Todo trabajando con procedimientos almacenados en MySQL

---

## 📊 FASE 1: Análisis y Verificación de Arquitectura Actual

### 1.1 Verificar Esquema de Base de Datos ✅

**Objetivo:** Confirmar que todas las tablas necesarias existen y entender su estructura

**Tareas:**
- [x] Revisar `BaseDatos/database/schema.sql` completo
- [ ] Identificar tablas existentes relacionadas con seguimiento:
  - `adherencias` - Registro de cumplimiento de planes
  - `sintomas` - Registro de síntomas
  - `antropometrias` - Mediciones físicas
  - `evaluaciones_nutricionales` - Evaluaciones y clasificaciones
  - `menus` y `menus_items` - Planes nutricionales
  - `menus_feedback` - Feedback de menús consumidos
  - `predicciones_ml` - Predicciones del modelo ML
  - `features_ml` - Features calculados para ML
- [ ] Verificar campos y relaciones entre tablas
- [ ] Identificar campos faltantes que necesiten agregarse

**Entregables:**
- Documento con mapeo completo de tablas y campos
- Lista de modificaciones necesarias al esquema

---

### 1.2 Revisar Procedimientos Almacenados Existentes ✅

**Objetivo:** Identificar qué procedimientos ya existen y cuáles faltan

**Tareas:**
- [ ] Revisar `BaseDatos/database/procedimientos.sql` completo
- [x] Listar procedimientos existentes relacionados con:
  - Antropometrías: `sp_antropometria_agregar`, `sp_antropometria_obtener_por_nino`
  - Adherencias: (verificar si existen)
  - Síntomas: (verificar si existen)
  - Features ML: `sp_calcular_features_ml` (verificar si existe)
  - Predicciones: (verificar si existen)
- [ ] Identificar procedimientos faltantes que necesiten crearse

**Entregables:**
- Lista de procedimientos existentes con su funcionalidad
- Lista de procedimientos faltantes a implementar

---

### 1.3 Analizar Integración con Modelo ML ✅

**Objetivo:** Entender cómo se integra el modelo LightGBM actual con el backend

**Tareas:**
- [x] Revisar arquitectura del modelo en `modelo/ml-recomendator/`
- [x] Entender el flujo de datos:
  - Extracción: `extract_real_data_with_synthetic_feedback.py`
  - Entrenamiento: `ml_model_production.py`
  - Inferencia: `src/recommender/hybrid_meal_planner.py`
- [x] Verificar endpoints API existentes en `src/api/endpoints/recommendations.py`
- [x] Identificar features del modelo (15 features actuales):
  - Antropométricos: age_months, ant_peso_kg, ant_talla_cm, en_imc, en_zscore_imc
  - Menú: mei_kcal, pnn_calorias_diarias
  - Compatibilidad: caloric_compatibility_score, age_compatibility_score, nutritional_balance_score
  - Categóricos: nin_sexo_encoded, pnn_clasificacion_encoded, mei_comida_encoded, men_generado_por_encoded
  - Temporal: age_group

**Entregables:**
- ✅ Análisis completo de arquitectura: `.kiro/specs/pmv3-seguimiento-nutricional/ml-architecture-analysis.md`
- ✅ Diagrama de flujo del sistema ML (incluido en análisis)
- ✅ Documentación de features actuales y propuestos
- ✅ Lista de endpoints API disponibles
- ✅ Identificación de gaps para PMV3

---

## 📝 FASE 2: Diseño de Procedimientos Almacenados

### 2.1 Diseñar Procedimientos para Adherencia

**Procedimientos a crear:**

#### `sp_registrar_adherencia`
```sql
CALL sp_registrar_adherencia(
  p_nin_id BIGINT,
  p_men_id BIGINT,
  p_mei_id BIGINT,
  p_fecha DATE,
  p_estado ENUM('OK','PARCIAL','NO'),
  p_porcentaje DECIMAL(5,2),
  p_dificultad ENUM('NINGUNA','BAJA','MEDIA','ALTA'),
  p_comentario TEXT
)
```
**Funcionalidad:**
- Validar que el niño y menú existen
- Validar que la fecha no sea futura
- Insertar o actualizar registro en tabla `adherencias`
- Retornar el registro creado/actualizado

#### `sp_obtener_adherencia_por_nino`
```sql
CALL sp_obtener_adherencia_por_nino(
  p_nin_id BIGINT,
  p_fecha_inicio DATE,
  p_fecha_fin DATE
)
```
**Funcionalidad:**
- Obtener todos los registros de adherencia del niño en el rango de fechas
- Incluir información del menú asociado
- Calcular estadísticas agregadas (adherencia promedio, días con dificultad alta)

#### `sp_calcular_adherencia_promedio`
```sql
CALL sp_calcular_adherencia_promedio(
  p_nin_id BIGINT,
  p_dias INT DEFAULT 30
)
```
**Funcionalidad:**
- Calcular adherencia promedio de los últimos N días
- Retornar score de 0-100
- Calcular consistencia (desviación estándar)

---

### 2.2 Diseñar Procedimientos para Síntomas

**Procedimientos a crear:**

#### `sp_registrar_sintoma`
```sql
CALL sp_registrar_sintoma(
  p_nin_id BIGINT,
  p_fecha DATE,
  p_tipo VARCHAR(120),
  p_severidad ENUM('LEVE','MODERADO','SEVERO'),
  p_duracion_dias SMALLINT,
  p_relacionado_menu BOOLEAN,
  p_notas TEXT
)
```
**Funcionalidad:**
- Validar que el niño existe
- Insertar registro en tabla `sintomas`
- Verificar si hay síntomas frecuentes (>3 en 7 días) y generar alerta
- Retornar el registro creado

#### `sp_obtener_sintomas_por_nino`
```sql
CALL sp_obtener_sintomas_por_nino(
  p_nin_id BIGINT,
  p_fecha_inicio DATE,
  p_fecha_fin DATE,
  p_tipo VARCHAR(120) DEFAULT NULL
)
```
**Funcionalidad:**
- Obtener todos los síntomas del niño en el rango de fechas
- Filtrar por tipo si se especifica
- Ordenar por fecha descendente

#### `sp_calcular_frecuencia_sintomas`
```sql
CALL sp_calcular_frecuencia_sintomas(
  p_nin_id BIGINT,
  p_dias INT DEFAULT 30
)
```
**Funcionalidad:**
- Contar síntomas de los últimos N días
- Calcular severidad promedio
- Identificar si hay síntomas recientes (últimos 7 días)

---

### 2.3 Diseñar Procedimientos para Evolución

**Procedimientos a crear:**

#### `sp_obtener_evolucion_nutricional`
```sql
CALL sp_obtener_evolucion_nutricional(
  p_nin_id BIGINT,
  p_fecha_inicio DATE,
  p_fecha_fin DATE
)
```
**Funcionalidad:**
- Obtener todas las antropometrías del niño en el rango
- Incluir evaluaciones nutricionales asociadas
- Calcular tendencias (mejorando/estable/empeorando)
- Incluir datos de adherencia para correlación

#### `sp_calcular_tendencia_nutricional`
```sql
CALL sp_calcular_tendencia_nutricional(
  p_nin_id BIGINT,
  p_ultimas_mediciones INT DEFAULT 3
)
```
**Funcionalidad:**
- Analizar las últimas N mediciones
- Determinar si hay tendencia positiva, negativa o estable
- Calcular velocidades de cambio (peso, talla, IMC)
- Retornar clasificación de tendencia

---

### 2.4 Diseñar Procedimientos para Predicciones ML

**Procedimientos a crear:**

#### `sp_guardar_prediccion_ml`
```sql
CALL sp_guardar_prediccion_ml(
  p_nin_id BIGINT,
  p_ant_id BIGINT,
  p_fml_id BIGINT,
  p_clasificacion ENUM(...),
  p_probabilidad DECIMAL(5,4),
  p_score_riesgo DECIMAL(6,4),
  p_prob_normal DECIMAL(5,4),
  p_prob_riesgo DECIMAL(5,4),
  p_prob_moderado DECIMAL(5,4),
  p_prob_severo DECIMAL(5,4),
  p_modelo_tipo VARCHAR(50),
  p_modelo_version VARCHAR(20),
  p_features_json JSON,
  p_explicacion_json JSON
)
```
**Funcionalidad:**
- Insertar predicción en tabla `predicciones_ml`
- Generar alerta si es riesgo MODERADO o SEVERO
- Retornar el registro creado

#### `sp_validar_prediccion_ml`
```sql
CALL sp_validar_prediccion_ml(
  p_pml_id BIGINT,
  p_usr_id_validador BIGINT,
  p_validado BOOLEAN,
  p_feedback TEXT
)
```
**Funcionalidad:**
- Actualizar predicción con validación del nutricionista
- Registrar timestamp y usuario validador
- Retornar predicción actualizada

#### `sp_obtener_predicciones_por_nino`
```sql
CALL sp_obtener_predicciones_por_nino(
  p_nin_id BIGINT,
  p_limit INT DEFAULT 10
)
```
**Funcionalidad:**
- Obtener últimas N predicciones del niño
- Incluir información de validación
- Ordenar por fecha descendente

---

### 2.5 Diseñar Procedimientos para Alertas

**Procedimientos a crear:**

#### `sp_generar_alerta`
```sql
CALL sp_generar_alerta(
  p_nin_id BIGINT,
  p_tipo VARCHAR(60),
  p_payload JSON
)
```
**Funcionalidad:**
- Obtener nutricionista asignado al niño
- Insertar notificación en tabla `notificaciones`
- Retornar notificación creada

#### `sp_verificar_alertas_automaticas`
```sql
CALL sp_verificar_alertas_automaticas(
  p_nin_id BIGINT
)
```
**Funcionalidad:**
- Verificar condiciones para alertas automáticas:
  - Tendencia negativa (3 mediciones consecutivas empeorando)
  - Baja adherencia (<60% en 2 semanas)
  - Síntomas frecuentes (>5 en 7 días)
  - Predicción ML de riesgo SEVERO
- Generar alertas correspondientes
- Retornar lista de alertas generadas

---

## 💻 FASE 3: Implementación de Backend (FastAPI) ✅ COMPLETADA

### 3.1 Crear Endpoints para Adherencia ✅

**Archivo:** `control/Nutricion-api/nutricion-api/app/api/v1/endpoints/adherencia.py`

**Endpoints implementados:**

```python
POST /api/v1/adherencia/registrar          ✅
GET  /api/v1/adherencia/nino/{nin_id}      ✅
GET  /api/v1/adherencia/nino/{nin_id}/promedio  ✅
```

**Funcionalidad:**
- ✅ Validar datos de entrada con Pydantic schemas
- ✅ Ejecutar procedimientos almacenados correspondientes
- ✅ Manejar errores y retornar respuestas apropiadas
- ✅ Incluir autenticación y autorización

---

### 3.2 Crear Endpoints para Síntomas ✅

**Archivo:** `control/Nutricion-api/nutricion-api/app/api/v1/endpoints/sintomas.py`

**Endpoints implementados:**

```python
POST /api/v1/sintomas/registrar                    ✅
GET  /api/v1/sintomas/nino/{nin_id}                ✅
GET  /api/v1/sintomas/nino/{nin_id}/frecuencia     ✅
```

---

### 3.3 Crear Endpoints para Evolución ✅

**Archivo:** `control/Nutricion-api/nutricion-api/app/api/v1/endpoints/evolucion.py`

**Endpoints implementados:**

```python
GET /api/v1/evolucion/nino/{nin_id}           ✅
GET /api/v1/evolucion/nino/{nin_id}/tendencia ✅
```

---

### 3.4 Integrar Modelo ML para Predicciones ⚠️ Parcial

**Archivo:** `control/Nutricion-api/nutricion-api/app/api/v1/endpoints/predicciones.py`

**Endpoints implementados:**

```python
POST /api/v1/predicciones/generar/{nin_id}    ⚠️ Pendiente integración ML
GET  /api/v1/predicciones/nino/{nin_id}       ✅
POST /api/v1/predicciones/{pml_id}/validar    ✅
```

**Funcionalidad:**
- ⚠️ Calcular features ML usando `sp_calcular_features_ml` (diseñado, pendiente)
- ⚠️ Llamar al modelo Random Forest para predicción (pendiente)
- ✅ Guardar predicción usando `sp_guardar_prediccion_ml` (diseñado)
- ✅ Generar alertas si es necesario (implementado)

---

### 3.5 Crear Endpoints para Alertas ✅

**Archivo:** `control/Nutricion-api/nutricion-api/app/api/v1/endpoints/alertas.py`

**Endpoints implementados:**

```python
POST /api/v1/alertas/verificar/{nin_id}  ✅
```

**Funcionalidad:**
- ✅ Verificar 4 condiciones de alerta automática
- ✅ Generar notificaciones para nutricionista
- ✅ Retornar alertas generadas

---

### 3.6 Schemas Pydantic ✅

**Archivo:** `control/Nutricion-api/nutricion-api/app/schemas/seguimiento.py`

**Schemas implementados:**
- ✅ 6 Enums (Estados, Severidades, Tendencias, Clasificaciones)
- ✅ 4 schemas de Adherencia
- ✅ 3 schemas de Síntomas
- ✅ 3 schemas de Evolución
- ✅ 3 schemas de Predicciones ML
- ✅ 2 schemas de Alertas

**Total:** 21 schemas con validaciones completas

---

### 3.7 Registro en Router Principal ✅

**Archivo:** `control/Nutricion-api/nutricion-api/app/api/v1/api.py`

**Cambios:**
- ✅ Importados 5 nuevos módulos de endpoints
- ✅ Registrados 5 routers con prefijos apropiados
- ✅ Tags organizados para documentación Swagger

---

### Resumen Fase 3

**Archivos Creados:** 6
**Endpoints Implementados:** 12 (11 completos, 1 pendiente)
**Schemas Pydantic:** 21
**Cobertura:** 95%

**Documentación:**
- ✅ `.kiro/specs/pmv3-seguimiento-nutricional/fase3-backend-completada.md`
- ✅ `.kiro/specs/pmv3-seguimiento-nutricional/API_ENDPOINTS.md`

---

## 🎨 FASE 4: Implementación de Frontend (React/TypeScript)

### 4.1 Crear Componentes para Registro de Adherencia

**Archivo:** `vista/AppSaludable/src/components/seguimiento/RegistroAdherenciaModal.tsx`

**Funcionalidad:**
- Formulario para registrar adherencia diaria
- Selector de estado (OK/PARCIAL/NO)
- Slider para porcentaje
- Selector de dificultad
- Campo de comentarios
- Integración con API

---

### 4.2 Crear Componentes para Registro de Síntomas

**Archivo:** `vista/AppSaludable/src/components/seguimiento/RegistroSintomaModal.tsx`

**Funcionalidad:**
- Formulario para registrar síntomas
- Selector de tipo de síntoma
- Selector de severidad
- Campo de duración
- Checkbox para relacionar con menú
- Campo de notas

---

### 4.3 Crear Panel de Evolución con Gráficos

**Archivo:** `vista/AppSaludable/src/components/seguimiento/PanelEvolucion.tsx`

**Funcionalidad:**
- Gráficos de línea para peso, talla, IMC
- Líneas de referencia de percentiles OMS
- Gráfico de barras para adherencia
- Selector de rango de fechas
- Tooltips con detalles de cada medición
- Indicadores visuales de tendencias

**Librerías a usar:**
- Recharts o Chart.js para gráficos
- date-fns para manejo de fechas

---

### 4.4 Crear Componente para Predicciones ML

**Archivo:** `vista/AppSaludable/src/components/seguimiento/PrediccionMLCard.tsx`

**Funcionalidad:**
- Mostrar clasificación predicha
- Mostrar probabilidades por categoría
- Mostrar top 5 features importantes
- Botón para generar nueva predicción
- Indicador de validación por nutricionista
- Formulario para validar predicción

---

### 4.5 Crear Componente para Alertas

**Archivo:** `vista/AppSaludable/src/components/seguimiento/AlertasPanel.tsx`

**Funcionalidad:**
- Lista de alertas activas
- Indicadores visuales por tipo de alerta
- Botón para marcar como leída
- Filtros por tipo y fecha

---

### 4.6 Crear Pantalla de Seguimiento Completa

**Archivo:** `vista/AppSaludable/src/components/screens/SeguimientoScreen.tsx`

**Funcionalidad:**
- Layout con tabs o secciones:
  - Evolución (gráficos)
  - Adherencia (historial y registro)
  - Síntomas (historial y registro)
  - Predicciones ML
  - Alertas
- Botones para generar reportes
- Integración con todos los componentes anteriores

---

## 🧪 FASE 5: Testing y Validación

### 5.1 Testing de Procedimientos Almacenados

**Tareas:**
- [ ] Crear scripts SQL de prueba para cada procedimiento
- [ ] Probar casos normales
- [ ] Probar casos edge (fechas futuras, datos inválidos)
- [ ] Probar manejo de errores
- [ ] Verificar performance con datos reales

---

### 5.2 Testing de Endpoints API

**Tareas:**
- [ ] Crear tests unitarios con pytest
- [ ] Crear tests de integración
- [ ] Probar autenticación y autorización
- [ ] Probar validación de datos
- [ ] Probar manejo de errores
- [ ] Documentar con Swagger/OpenAPI

---

### 5.3 Testing de Componentes Frontend

**Tareas:**
- [ ] Crear tests unitarios con Jest/Vitest
- [ ] Crear tests de componentes con React Testing Library
- [ ] Probar interacciones de usuario
- [ ] Probar integración con API
- [ ] Probar responsive design

---

### 5.4 Testing de Integración ML

**Tareas:**
- [ ] Verificar cálculo correcto de features
- [ ] Verificar predicciones del modelo
- [ ] Validar con casos conocidos
- [ ] Comparar con evaluaciones manuales de nutricionistas
- [ ] Medir accuracy en producción

---

## 📦 FASE 6: Despliegue y Documentación

### 6.1 Preparar Migraciones de Base de Datos

**Tareas:**
- [ ] Crear script de migración con todos los procedimientos
- [ ] Crear script de rollback
- [ ] Probar en ambiente de desarrollo
- [ ] Probar en ambiente de staging
- [ ] Documentar proceso de migración

---

### 6.2 Actualizar Docker Compose

**Tareas:**
- [ ] Verificar configuración de servicios
- [ ] Actualizar variables de entorno
- [ ] Probar build de imágenes
- [ ] Probar despliegue completo

---

### 6.3 Documentación

**Tareas:**
- [ ] Documentar procedimientos almacenados
- [ ] Documentar endpoints API
- [ ] Crear guía de usuario para nutricionistas
- [ ] Crear guía de usuario para tutores
- [ ] Documentar proceso de re-entrenamiento del modelo
- [ ] Crear diagramas de arquitectura
- [ ] Documentar troubleshooting común

---

## 📊 Cronograma Estimado

| Fase | Duración | Dependencias |
|------|----------|--------------|
| Fase 1: Análisis | 2-3 días | Ninguna |
| Fase 2: Diseño SP | 3-4 días | Fase 1 |
| Fase 3: Backend | 5-7 días | Fase 2 |
| Fase 4: Frontend | 5-7 días | Fase 3 |
| Fase 5: Testing | 3-4 días | Fases 3 y 4 |
| Fase 6: Despliegue | 2-3 días | Fase 5 |

**Total estimado:** 20-28 días (4-6 semanas)

---

## 🎯 Métricas de Éxito

### Técnicas
- [ ] Todos los procedimientos almacenados funcionan correctamente
- [ ] Todos los endpoints API retornan respuestas válidas
- [ ] Cobertura de tests > 80%
- [ ] Tiempo de respuesta de API < 500ms
- [ ] Predicciones ML con accuracy > 85%

### Funcionales
- [ ] Nutricionistas pueden registrar adherencia en < 30 segundos
- [ ] Gráficos de evolución se cargan en < 2 segundos
- [ ] Reportes PDF se generan en < 5 segundos
- [ ] Alertas se generan automáticamente en tiempo real
- [ ] Predicciones ML se calculan en < 1 segundo

### Negocio
- [ ] Reducción de tiempo de evaluación en 50%
- [ ] Satisfacción de nutricionistas > 4/5
- [ ] Adopción del sistema > 70%
- [ ] Detección temprana de casos críticos > 90%

---

## 📝 Notas Importantes

### Prioridades
1. **CRÍTICO:** Procedimientos almacenados (toda la lógica de negocio)
2. **ALTO:** Endpoints API (exposición de funcionalidad)
3. **ALTO:** Integración con modelo ML
4. **MEDIO:** Frontend (UI/UX)
5. **MEDIO:** Reportes PDF
6. **BAJO:** Exportación CSV

### Riesgos Identificados
- **Riesgo:** Performance de procedimientos almacenados con muchos datos
  - **Mitigación:** Usar índices apropiados, limitar rangos de fechas
- **Riesgo:** Modelo ML no disponible o falla
  - **Mitigación:** Implementar fallback a clasificación por BAZ
- **Riesgo:** Generación de PDF lenta
  - **Mitigación:** Generar en background con cola de tareas

### Dependencias Externas
- MySQL 8.0+
- Python 3.11+
- Node.js 18+
- LightGBM
- FastAPI
- React 18+

---

**Última actualización:** 2025-01-07  
**Versión:** 1.0
