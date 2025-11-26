# Análisis de Arquitectura del Modelo ML

## Fecha de Análisis
**2025-01-XX** - Análisis completo de la arquitectura ML en `modelo/ml-recomendator/`

---

## 1. RESUMEN EJECUTIVO

### Modelo Implementado
- **Tipo**: LightGBM Ranker (Gradient Boosting Decision Tree)
- **Objetivo**: Recomendación de menús personalizados para niños
- **Accuracy Reportado**: 90.18% (con validación cruzada 5-fold)
- **NDCG Target**: 88% (Normalized Discounted Cumulative Gain)
- **Archivo del Modelo**: `models/production_menu_recommender.pkl` (44MB)

### Estado Actual
✅ **COMPLETAMENTE FUNCIONAL E INTEGRADO**
- Modelo entrenado y validado
- API FastAPI operativa
- Endpoints HTTP accesibles
- Documentación completa
- Sistema de re-entrenamiento implementado

---

## 2. ARQUITECTURA DEL SISTEMA

### 2.1 Estructura de Directorios

```
modelo/ml-recomendator/
├── src/
│   ├── domain/                    # Lógica de negocio ML
│   │   ├── interfaces/            # Contratos e interfaces
│   │   └── models/
│   │       ├── model_loader.py    # Carga de modelos LightGBM
│   │       └── ml_implementations.py  # Implementaciones concretas
│   │
│   ├── application/               # Servicios de aplicación
│   │   └── services/
│   │       ├── meal_recommender_service.py  # Orquestación de recomendaciones
│   │       └── model_training_service.py    # Orquestación de entrenamiento
│   │
│   ├── infrastructure/            # Acceso a datos
│   │   ├── database/              # Conexiones a BD
│   │   └── repositories/          # Repositorios de datos
│   │
│   ├── api/                       # Exposición HTTP (FastAPI)
│   │   ├── main.py                # Aplicación FastAPI
│   │   ├── schemas/               # Modelos Pydantic
│   │   └── endpoints/
│   │       ├── recommendations.py  # Planes semanales
│   │       ├── models_info.py      # Info de modelos
│   │       └── training.py         # Entrenamiento
│   │
│   ├── recommender/               # Lógica ML específica
│   │   ├── hybrid_meal_planner.py  # ⭐ CORE: Planes con LightGBM
│   │   ├── meal_planner.py         # Clase base
│   │   └── menu_recommender.py     # Recomendador de menús
│   │
│   ├── pipeline/                  # Pipeline de datos
│   │   ├── feature_engineering.py  # Generación de features
│   │   └── train_ranker.py         # Entrenamiento del ranker
│   │
│   └── utils/                     # Utilidades
│       ├── db_connector.py         # Conexión a MySQL
│       └── classification_mapper.py # Mapeo de clasificaciones
│
├── models/                        # Modelos entrenados
│   └── production_menu_recommender_*.pkl
│
├── data/                          # Datos
│   ├── raw/                       # Datos crudos
│   ├── processed/                 # Datos procesados
│   └── synthetic/                 # Datos sintéticos
│
├── docs/                          # Documentación
│   ├── ARQUITECTURA_ML.md
│   ├── API_ML.md
│   ├── INTEGRACION_BACKEND.md
│   └── PROCEDIMIENTOS_ML.sql
│
├── ml_model_production.py         # Script de entrenamiento
├── extract_real_data_with_synthetic_feedback.py  # Extracción de datos
└── run_ml_system_real_db.py       # Orquestador principal
```

### 2.2 Patrón de Arquitectura

**Clean Architecture / Hexagonal Architecture**

```
┌─────────────────────────────────────────────────┐
│              API Layer (FastAPI)                │
│  POST /api/v1/recommendations/weekly-plan       │
│  GET  /api/v1/models/info                       │
│  POST /api/v1/models/train                      │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│         Application Services                    │
│  - MealRecommenderService                       │
│  - ModelTrainingService                         │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│         Domain Layer (Business Logic)           │
│  - HybridMealPlanner (CORE)                     │
│  - ProductionMealRecommender                    │
│  - MLModelLoader                                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│         Infrastructure Layer                    │
│  - MySQL Database                               │
│  - File System (models/)                        │
│  - External APIs                                │
└─────────────────────────────────────────────────┘
```

---

## 3. COMPONENTES PRINCIPALES

### 3.1 HybridMealPlanner (CORE)
**Archivo**: `src/recommender/hybrid_meal_planner.py`

**Responsabilidad**: Generador principal de planes semanales usando LightGBM

**Funcionalidad**:
- Genera planes semanales completos (7 días × 3 comidas = 21 comidas)
- Usa modelo LightGBM para scoring de menús
- Filtra por alergias y restricciones
- Respeta preferencias del usuario
- Optimiza balance nutricional

**Método Principal**:
```python
def plan_semana_completa(
    self,
    child_id: str,
    nutrition_status: str,
    allergies: List[str],
    preferences: Dict[str, float]
) -> WeeklyMealPlan
```

**Flujo**:
1. Carga modelo LightGBM desde `models/production_menu_recommender.pkl`
2. Obtiene menús disponibles de la BD
3. Filtra por alergias/restricciones (filtro duro)
4. Calcula features para cada menú
5. Usa LightGBM para scoring
6. Selecciona top menús por slot (desayuno/almuerzo/cena)
7. Retorna plan semanal estructurado

### 3.2 ProductionMenuRecommender
**Archivo**: `ml_model_production.py`

**Responsabilidad**: Entrenamiento del modelo LightGBM

**Características**:
- Usa datos reales de producción
- Genera feedback sintético realista
- Regularización agresiva para evitar overfitting
- Validación cruzada con grupos (GroupKFold)
- Calcula NDCG realista (~88%)

**Parámetros del Modelo**:
```python
lgb_params = {
    "objective": "regression",
    "metric": "rmse",
    "boosting_type": "gbdt",
    "num_leaves": 5,           # Muy reducido
    "learning_rate": 0.005,    # Muy bajo
    "feature_fraction": 0.3,   # Muy reducido
    "lambda_l1": 10.0,         # Regularización alta
    "lambda_l2": 10.0,         # Regularización alta
    "max_depth": 3,            # Limitado
}
```

### 3.3 MLModelLoader
**Archivo**: `src/domain/models/model_loader.py`

**Responsabilidad**: Singleton para carga de modelos

**Funcionalidad**:
- Carga modelos .pkl de forma lazy
- Extrae y expone métricas
- Cachea modelos en memoria
- Maneja múltiples versiones de modelos

**Métricas Expuestas**:
- Accuracy: ~85%
- NDCG@5: ~0.80
- NDCG@10: ~0.82
- RMSE, F1-Score

### 3.4 API FastAPI
**Archivo**: `src/api/main.py`

**Endpoints Principales**:

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/recommendations/weekly-plan` | POST | Genera plan semanal (7 días × 3 comidas) |
| `/api/v1/models/status` | GET | Estado de modelos cargados |
| `/api/v1/models/info` | GET | Información detallada de modelos |
| `/api/v1/models/train` | POST | Entrena nuevo modelo |
| `/health` | GET | Health check |

**Ejemplo de Request**:
```json
POST /api/v1/recommendations/weekly-plan
{
  "child_id": "123",
  "nutrition_status": "DESNUTRICION",
  "allergies": ["maní", "huevo"],
  "preferences": {"menu_001": 5.0}
}
```

**Ejemplo de Response**:
```json
{
  "total_days": 7,
  "meals_per_day": 3,
  "total_meals": 21,
  "weekly_plan": [
    {
      "day": 1,
      "day_name": "Lunes",
      "meals": [
        {
          "slot": "Desayuno",
          "name": "Avena con plátano",
          "calories": 280,
          "score": 0.95,
          "reason": "Recomendado por LightGBM"
        },
        ...
      ]
    },
    ...
  ]
}
```

---

## 4. FEATURES DEL MODELO ML

### 4.1 Features Antropométricos (6)
- `edad_meses` - Edad en meses
- `ant_peso_kg` - Peso en kg
- `ant_talla_cm` - Talla en cm
- `en_imc` - Índice de masa corporal
- `en_zscore_imc` - Z-score del IMC (OMS)
- `pnn_calorias_diarias` - Calorías diarias requeridas

### 4.2 Features de Menú (1)
- `mei_kcal` - Calorías del ítem del menú

### 4.3 Features de Compatibilidad (3)
- `caloric_compatibility_score` - Compatibilidad calórica (0-1)
- `age_compatibility_score` - Compatibilidad por edad (0-1)
- `nutritional_balance_score` - Balance nutricional (0-1)

### 4.4 Features Categóricos Codificados (4+)
- `nin_sexo_encoded` - Sexo codificado
- `pnn_clasificacion_encoded` - Clasificación nutricional
- `mei_comida_encoded` - Tipo de comida (desayuno/almuerzo/cena)
- `men_generado_por_encoded` - Generador del menú

### 4.5 Features Temporales (1)
- `age_group` - Grupo etario (0-3)

**Total**: ~15 features

---

## 5. FLUJO DE DATOS

### 5.1 Flujo de Entrenamiento

```
┌─────────────────────────────────────────────────┐
│  1. Extracción de Datos                         │
│     extract_real_data_with_synthetic_feedback.py│
│     ├─ Conecta a MySQL                          │
│     ├─ Extrae niños, menús, antropometrías      │
│     ├─ Genera feedback sintético realista       │
│     └─ Guarda: training_dataset_real.csv        │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  2. Feature Engineering                         │
│     ml_model_production.py::engineer_features() │
│     ├─ Calcula IMC, Z-scores                    │
│     ├─ Codifica variables categóricas           │
│     ├─ Calcula scores de compatibilidad         │
│     └─ Normaliza features                       │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  3. Entrenamiento del Modelo                    │
│     ml_model_production.py::train_model()       │
│     ├─ GroupKFold cross-validation (3 folds)    │
│     ├─ Grid search de hiperparámetros           │
│     ├─ Entrena LightGBM con regularización      │
│     ├─ Calcula métricas (RMSE, Accuracy, NDCG)  │
│     └─ Selecciona mejor modelo                  │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  4. Guardado del Modelo                         │
│     ├─ Serializa modelo: .pkl                   │
│     ├─ Guarda metadata: .json                   │
│     ├─ Feature importance                       │
│     ├─ Label encoders                           │
│     └─ Métricas de entrenamiento                │
└─────────────────────────────────────────────────┘
```

### 5.2 Flujo de Inferencia (Predicción)

```
┌─────────────────────────────────────────────────┐
│  1. Request HTTP                                │
│     POST /api/v1/recommendations/weekly-plan    │
│     {child_id, nutrition_status, allergies}     │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  2. Carga de Modelo                             │
│     MLModelLoader.get_model()                   │
│     ├─ Carga production_menu_recommender.pkl    │
│     ├─ Cachea en memoria (singleton)            │
│     └─ Extrae metadata                          │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  3. Obtención de Datos                          │
│     ├─ Consulta BD: datos del niño              │
│     ├─ Consulta BD: menús disponibles           │
│     └─ Filtra por alergias (filtro duro)        │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  4. Feature Engineering                         │
│     ├─ Calcula features para cada menú          │
│     ├─ Aplica label encoders                    │
│     └─ Normaliza valores                        │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  5. Scoring con LightGBM                        │
│     model.predict(features)                     │
│     ├─ Calcula score para cada menú             │
│     ├─ Ordena por score descendente             │
│     └─ Selecciona top N por slot                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  6. Generación de Plan Semanal                  │
│     HybridMealPlanner.plan_semana_completa()    │
│     ├─ Lunes: Desayuno, Almuerzo, Cena          │
│     ├─ Martes: Desayuno, Almuerzo, Cena         │
│     ├─ ...                                      │
│     └─ Domingo: Desayuno, Almuerzo, Cena        │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  7. Response HTTP                               │
│     WeeklyMealPlanResponse (JSON)               │
│     {total_days: 7, meals_per_day: 3, ...}      │
└─────────────────────────────────────────────────┘
```

---

## 6. INTEGRACIÓN CON BASE DE DATOS

### 6.1 Tablas Utilizadas

**Tablas Existentes**:
- `ninos` - Datos de niños
- `antropometrias` - Mediciones físicas
- `evaluaciones_nutricionales` - Evaluaciones y clasificaciones
- `perfil_nutricional_nino` - Perfil nutricional
- `menus` - Menús generados
- `menus_items` - Ítems de menús
- `menus_feedback` - Feedback de consumo
- `ninos_alergias` - Alergias
- `ninos_restricciones_alimentos` - Restricciones

**Tablas Propuestas para PMV3** (no implementadas aún):
- `features_ml` - Features calculados para ML
- `predicciones_ml` - Predicciones del modelo
- `menus_nutrientes` - Información nutricional de menús

### 6.2 Procedimientos Almacenados

**Existentes**:
- `sp_antropometria_agregar` - Agregar antropometría
- `sp_antropometria_obtener_por_nino` - Obtener antropometrías

**Propuestos para PMV3** (no implementados):
- `sp_calcular_features_ml` - Calcular features ML
- `sp_guardar_prediccion_ml` - Guardar predicción
- `sp_obtener_evolucion_nutricional` - Obtener evolución
- `sp_registrar_adherencia` - Registrar adherencia
- `sp_registrar_sintoma` - Registrar síntoma

---

## 7. MÉTRICAS Y PERFORMANCE

### 7.1 Métricas del Modelo

**Métricas Reportadas** (según metadata):
- **RMSE**: ~0.8-1.2 (error cuadrático medio)
- **Accuracy**: ~85-90% (clasificación de ratings)
- **F1-Score**: ~0.85-0.90 (promedio ponderado)
- **NDCG**: ~0.88 (objetivo alcanzado)
- **NDCG@5**: ~0.80 (top 5 recomendaciones)
- **NDCG@10**: ~0.82 (top 10 recomendaciones)

### 7.2 Performance de Inferencia

**Tiempos Estimados**:
- Carga de modelo: ~100-200ms (primera vez)
- Predicción por menú: <1ms
- Plan semanal completo (21 menús): <50ms
- Request HTTP total: <500ms

### 7.3 Tamaño del Modelo

- **Archivo .pkl**: ~44MB
- **Metadata .json**: ~10KB
- **Features**: 15 features
- **Árboles**: ~100 (n_estimators)

---

## 8. FORTALEZAS Y LIMITACIONES

### 8.1 Fortalezas ✅

1. **Arquitectura Limpia**
   - Separación clara de responsabilidades
   - Fácil de mantener y extender
   - Bien documentado

2. **Modelo Robusto**
   - LightGBM es eficiente y preciso
   - Regularización agresiva evita overfitting
   - Validación cruzada con grupos

3. **API Completa**
   - Endpoints bien diseñados
   - Documentación Swagger
   - Manejo de errores

4. **Feedback Sintético Realista**
   - Patrones de comportamiento infantil
   - Variabilidad temporal
   - Factores psicológicos

5. **Sistema de Re-entrenamiento**
   - Pipeline automatizado
   - Fácil actualización del modelo
   - Versionado de modelos

### 8.2 Limitaciones ⚠️

1. **Features Limitados**
   - Solo 15 features
   - Faltan features temporales (velocidades)
   - No incluye síntomas ni adherencia histórica

2. **Datos Sintéticos**
   - Feedback generado artificialmente
   - Puede no reflejar comportamiento real
   - Necesita validación con datos reales

3. **Falta de Explicabilidad**
   - No hay SHAP values implementados
   - Difícil entender por qué se recomienda un menú
   - No hay explicaciones en lenguaje natural

4. **Sin Monitoreo en Producción**
   - No hay drift detection
   - No se rastrean métricas en tiempo real
   - No hay alertas automáticas

5. **Integración Parcial con PMV3**
   - Tablas propuestas no implementadas
   - Procedimientos almacenados faltantes
   - No hay endpoints para adherencia/síntomas

---

## 9. RECOMENDACIONES PARA PMV3

### 9.1 Prioridad ALTA 🔴

1. **Implementar Tablas ML en BD**
   - Crear `features_ml`
   - Crear `predicciones_ml`
   - Migrar esquema

2. **Crear Procedimientos Almacenados**
   - `sp_calcular_features_ml`
   - `sp_guardar_prediccion_ml`
   - `sp_obtener_evolucion_nutricional`

3. **Integrar Adherencia y Síntomas**
   - Endpoints para registro
   - Cálculo de features de adherencia
   - Incorporar en modelo ML

4. **Agregar Features Temporales**
   - `bmi_velocity` (velocidad de cambio de IMC)
   - `weight_velocity` (velocidad de cambio de peso)
   - `adherence_score` (score de adherencia)

### 9.2 Prioridad MEDIA 🟡

1. **Explicabilidad del Modelo**
   - Implementar SHAP values
   - Generar explicaciones con LLM
   - Mostrar top features en UI

2. **Validación con Datos Reales**
   - Recopilar feedback real de usuarios
   - Re-entrenar con datos reales
   - Comparar métricas

3. **Monitoreo en Producción**
   - Implementar drift detection
   - Dashboard de métricas
   - Alertas automáticas

4. **Optimización de Performance**
   - Cachear predicciones
   - Batch processing
   - Compresión del modelo

### 9.3 Prioridad BAJA 🟢

1. **Modelos Alternativos**
   - Probar XGBoost
   - Probar redes neuronales
   - Ensemble de modelos

2. **A/B Testing**
   - Framework para experimentos
   - Comparar modelos en producción
   - Métricas de negocio

3. **Personalización Avanzada**
   - Aprendizaje por refuerzo
   - Bandits contextuales
   - Feedback loop automático

---

## 10. PRÓXIMOS PASOS PARA IMPLEMENTACIÓN PMV3

### Fase 1: Preparación de BD (Semana 1)
1. Ejecutar migraciones para crear tablas ML
2. Crear procedimientos almacenados
3. Poblar datos históricos en nuevas tablas

### Fase 2: Endpoints de Seguimiento (Semana 2)
1. Crear endpoints para adherencia
2. Crear endpoints para síntomas
3. Crear endpoints para evolución

### Fase 3: Integración ML (Semana 3)
1. Calcular features ML con datos reales
2. Generar predicciones automáticas
3. Guardar predicciones en BD

### Fase 4: Frontend (Semana 4)
1. Panel de evolución con gráficos
2. Formularios de registro
3. Visualización de predicciones

### Fase 5: Testing y Validación (Semana 5)
1. Tests de integración
2. Validación con nutricionistas
3. Ajustes finales

---

## 11. CONCLUSIONES

### Estado Actual
El sistema ML está **completamente funcional** y listo para generar recomendaciones de menús. La arquitectura es sólida, el modelo está entrenado y validado, y la API está operativa.

### Gaps para PMV3
Para implementar el PMV3 completo, se necesita:
1. Crear infraestructura de BD para seguimiento (tablas y SPs)
2. Implementar endpoints de adherencia y síntomas
3. Integrar features temporales en el modelo
4. Desarrollar frontend para visualización

### Viabilidad
✅ **ALTA VIABILIDAD** - El sistema ML existente puede ser extendido para soportar PMV3 sin cambios arquitectónicos mayores. Solo se requiere:
- Agregar nuevos features al modelo
- Crear endpoints adicionales
- Implementar procedimientos almacenados

### Tiempo Estimado
- **Integración ML con PMV3**: 2-3 semanas
- **Frontend completo**: 2-3 semanas
- **Testing y validación**: 1-2 semanas
- **Total**: 5-8 semanas

---

## ANEXOS

### A. Comandos Útiles

```bash
# Re-entrenar modelo
cd modelo/ml-recomendator
python ml_model_production.py

# Ejecutar pipeline completo
python run_ml_system_real_db.py

# Iniciar API
uvicorn src.api.main:app --reload --port 8001

# Verificar modelo
python -c "import pickle; m=pickle.load(open('models/production_menu_recommender.pkl','rb')); print(m)"
```

### B. Referencias

- **Documentación ML**: `modelo/ml-recomendator/docs/`
- **README Principal**: `modelo/ml-recomendator/README.md`
- **Arquitectura Verificada**: `modelo/ml-recomendator/ARQUITECTURA_FINAL_VERIFICADA.md`
- **API Docs**: `modelo/ml-recomendator/docs/API_ML.md`

---

**Documento generado**: 2025-01-XX  
**Autor**: Análisis de Arquitectura ML  
**Versión**: 1.0
