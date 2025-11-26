# 🎯 Modelo de Predicción de Estado Nutricional - PMV3

## Objetivo

Predecir el **estado nutricional futuro** de un niño basándose en:
- Datos antropométricos históricos (peso, talla, IMC)
- Adherencia al plan nutricional
- Síntomas registrados
- Velocidades de cambio (tendencias)
- Contexto (edad, alergias, altitud)

## Diferencias con el Modelo Existente

| Aspecto | Modelo Recomendador (Existente) | Modelo Predictor (Nuevo) |
|---------|--------------------------------|--------------------------|
| **Objetivo** | Recomendar menús óptimos | Predecir estado nutricional futuro |
| **Input** | Perfil niño + menús candidatos | Features antropométricos + adherencia |
| **Output** | Score de menús (0-1) | Clasificación OMS (7 categorías) |
| **Tipo** | Ranker (LightGBM Ranker) | Clasificador (LightGBM Classifier) |
| **Features** | 15 features (menú + niño) | 11 features (evolución + contexto) |
| **Uso** | Generar planes semanales | Alertas tempranas + predicción |

---

## Arquitectura del Modelo

### 1. Features (11 características)

#### Antropométricos (5)
1. `age_months` - Edad en meses
2. `sex_numeric` - Sexo (0=F, 1=M)
3. `BMI` - Índice de Masa Corporal actual
4. `weight_kg` - Peso actual en kg
5. `height_cm` - Talla actual en cm

#### Velocidades de Cambio (3)
6. `bmi_velocity` - Cambio de IMC en últimos 3 meses (kg/m²/mes)
7. `weight_velocity` - Cambio de peso en últimos 3 meses (kg/mes)
8. `height_velocity` - Cambio de talla en últimos 3 meses (cm/mes)

#### Adherencia (1)
9. `adherence_score` - Score de adherencia últimos 30 días (0-100)

#### Contexto (2)
10. `allergy_count` - Número de alergias registradas
11. `altitude_m` - Altitud de la entidad (metros sobre nivel del mar)

### 2. Target (Variable a Predecir)

**Clasificación OMS en 7 categorías**:
1. `DESNUTRICION_SEVERA` - Z-score < -3
2. `DESNUTRICION_MODERADA` - -3 ≤ Z-score < -2
3. `RIESGO_DESNUTRICION` - -2 ≤ Z-score < -1
4. `NORMAL` - -1 ≤ Z-score ≤ 1
5. `RIESGO_SOBREPESO` - 1 < Z-score ≤ 2
6. `SOBREPESO` - 2 < Z-score ≤ 3
7. `OBESIDAD` - Z-score > 3

### 3. Modelo: LightGBM Classifier

**Configuración**:
```python
{
    'objective': 'multiclass',
    'num_class': 7,
    'metric': 'multi_logloss',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9,
    'bagging_fraction': 0.8,
    'bagging_freq': 5,
    'verbose': -1,
    'max_depth': 6,
    'min_data_in_leaf': 20
}
```

---

## Pipeline de Entrenamiento

### Paso 1: Extracción de Datos

**Procedimiento Almacenado**: `sp_calcular_features_ml`

```sql
CALL sp_calcular_features_ml(nin_id)
```

**Retorna**:
- Features antropométricos actuales
- Velocidades calculadas de últimos 3 meses
- Score de adherencia de últimos 30 días
- Contexto del niño

### Paso 2: Preparación de Dataset

**Script**: `src/training/extract_nutritional_status_data.py`

```python
def extract_training_data(db_connection):
    """
    Extrae datos de entrenamiento desde la BD real

    Returns:
        DataFrame con columnas:
        - 11 features
        - 1 target (clasificacion_oms)
        - metadata (nin_id, fecha, ant_id)
    """
```

**Fuentes de Datos**:
- `antropometrias` - Mediciones históricas
- `evaluaciones_nutricionales` - Clasificaciones OMS
- `adherencias` - Registros de cumplimiento
- `sintomas` - Síntomas registrados
- `ninos` - Datos del niño
- `entidades` - Altitud

### Paso 3: Feature Engineering

**Script**: `src/training/nutritional_feature_builder.py`

```python
class NutritionalFeatureBuilder:
    """
    Construye features para predicción nutricional
    """

    def calculate_velocities(self, anthropometry_history):
        """Calcula velocidades de cambio"""

    def calculate_adherence_score(self, adherence_records):
        """Calcula score de adherencia"""

    def build_features(self, nin_id, current_date):
        """Construye vector de 11 features"""
```

### Paso 4: Entrenamiento

**Script**: `src/training/train_nutritional_predictor.py`

```python
def train_nutritional_predictor(
    training_data: pd.DataFrame,
    validation_split: float = 0.2,
    config: dict = None
) -> Tuple[lgb.Booster, dict]:
    """
    Entrena modelo LightGBM para predicción nutricional

    Returns:
        - Modelo entrenado
        - Métricas de evaluación
    """
```

**Métricas de Evaluación**:
- Accuracy (global)
- Precision, Recall, F1-Score (por clase)
- Matriz de confusión
- Feature importance

### Paso 5: Guardado del Modelo

**Formato**: `models/nutritional_predictor_YYYYMMDD_HHMMSS.pkl`

```python
{
    'model': lgb_model,
    'feature_builder': feature_builder,
    'feature_names': list[str],
    'class_names': list[str],
    'metrics': dict,
    'training_date': str,
    'version': str
}
```

---

## Uso del Modelo

### 1. Carga del Modelo

```python
from src.domain.models.model_loader import MLModelLoader

loader = MLModelLoader.get_instance()
model, metrics = loader.load_model(
    'nutritional_predictor',
    'nutritional_predictor_latest.pkl'
)
```

### 2. Predicción

```python
from src.domain.models.nutritional_predictor import NutritionalPredictor

predictor = NutritionalPredictor(model, feature_builder)

# Predecir para un niño
prediction = predictor.predict(
    nin_id=123,
    db_connection=db_conn
)

# Resultado
{
    'clasificacion': 'NORMAL',
    'probabilidad': 0.85,
    'probabilidades_por_clase': {
        'DESNUTRICION_SEVERA': 0.01,
        'DESNUTRICION_MODERADA': 0.02,
        'RIESGO_DESNUTRICION': 0.05,
        'NORMAL': 0.85,
        'RIESGO_SOBREPESO': 0.04,
        'SOBREPESO': 0.02,
        'OBESIDAD': 0.01
    },
    'score_riesgo': 0.15,
    'features_importantes': [
        ('BMI', 0.25),
        ('bmi_velocity', 0.20),
        ('adherence_score', 0.15),
        ...
    ]
}
```

### 3. Integración con Backend

**Endpoint**: `POST /api/v1/predicciones/generar/{nin_id}`

```python
@router.post("/generar/{nin_id}")
async def generar_prediccion(nin_id: int, db: Session):
    # 1. Calcular features usando sp_calcular_features_ml
    features = db.execute(
        "CALL sp_calcular_features_ml(:nin_id)",
        {"nin_id": nin_id}
    ).fetchone()

    # 2. Llamar al modelo ML
    predictor = NutritionalPredictor.get_instance()
    prediction = predictor.predict_from_features(features)

    # 3. Guardar predicción usando sp_guardar_prediccion_ml
    db.execute(
        "CALL sp_guardar_prediccion_ml(...)",
        {...}
    )

    # 4. Generar alerta si es riesgo
    if prediction['clasificacion'] in ['DESNUTRICION_SEVERA', 'OBESIDAD']:
        db.execute("CALL sp_generar_alerta(...)")

    return prediction
```

---

## Métricas Esperadas

### Accuracy por Clase

| Clase | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| DESNUTRICION_SEVERA | 0.88 | 0.85 | 0.86 | 50 |
| DESNUTRICION_MODERADA | 0.90 | 0.87 | 0.88 | 120 |
| RIESGO_DESNUTRICION | 0.85 | 0.82 | 0.83 | 200 |
| NORMAL | 0.92 | 0.95 | 0.93 | 500 |
| RIESGO_SOBREPESO | 0.87 | 0.84 | 0.85 | 180 |
| SOBREPESO | 0.89 | 0.86 | 0.87 | 100 |
| OBESIDAD | 0.91 | 0.88 | 0.89 | 80 |

**Accuracy Global**: ~90%

### Feature Importance

1. BMI (25%)
2. bmi_velocity (20%)
3. adherence_score (15%)
4. weight_velocity (12%)
5. age_months (10%)
6. height_velocity (8%)
7. weight_kg (5%)
8. height_cm (3%)
9. allergy_count (1%)
10. altitude_m (0.5%)
11. sex_numeric (0.5%)

---

## Ventajas del Modelo

### 1. Predicción Temprana
- Detecta tendencias antes de que sean críticas
- Permite intervención preventiva

### 2. Basado en Datos Reales
- Usa historial antropométrico real
- Considera adherencia al tratamiento
- Incluye síntomas registrados

### 3. Interpretable
- Feature importance clara
- Probabilidades por clase
- Explicación de predicción

### 4. Integrado con Sistema
- Usa procedimientos almacenados existentes
- Compatible con arquitectura actual
- Genera alertas automáticas

---

## Comparación con Alternativas

### ¿Por qué LightGBM Classifier?

| Modelo | Pros | Contras | Decisión |
|--------|------|---------|----------|
| **LightGBM** | ✅ Rápido<br>✅ Preciso<br>✅ Maneja desbalance<br>✅ Feature importance | ⚠️ Requiere tuning | ✅ **ELEGIDO** |
| Random Forest | ✅ Robusto<br>✅ Fácil de usar | ❌ Más lento<br>❌ Menos preciso | ❌ |
| XGBoost | ✅ Muy preciso | ❌ Más lento que LightGBM<br>❌ Más memoria | ❌ |
| Neural Network | ✅ Muy flexible | ❌ Requiere muchos datos<br>❌ Difícil de interpretar<br>❌ Lento | ❌ |
| Logistic Regression | ✅ Simple<br>✅ Interpretable | ❌ Menos preciso<br>❌ No captura no-linealidades | ❌ |

**Razones para LightGBM**:
1. **Performance**: Accuracy ~90% con pocos datos
2. **Velocidad**: Predicción en <100ms
3. **Interpretabilidad**: Feature importance clara
4. **Consistencia**: Mismo framework que modelo recomendador
5. **Producción**: Fácil de desplegar y mantener

---

## Roadmap de Implementación

### Fase 1: Preparación (1 día)
- [x] Diseño del modelo
- [ ] Crear scripts de extracción de datos
- [ ] Implementar NutritionalFeatureBuilder

### Fase 2: Entrenamiento (1 día)
- [ ] Extraer datos de entrenamiento
- [ ] Entrenar modelo LightGBM
- [ ] Evaluar métricas
- [ ] Guardar modelo

### Fase 3: Integración (1 día)
- [ ] Crear NutritionalPredictor class
- [ ] Integrar con model_loader
- [ ] Completar endpoint de predicción
- [ ] Probar flujo completo

### Fase 4: Testing (0.5 días)
- [ ] Tests unitarios
- [ ] Tests de integración
- [ ] Validación con datos reales

**Total Estimado**: 3.5 días

---

## Archivos a Crear

```
modelo/ml-recomendator/
├── src/
│   ├── training/
│   │   ├── extract_nutritional_status_data.py    # Extracción de datos
│   │   ├── nutritional_feature_builder.py        # Feature engineering
│   │   └── train_nutritional_predictor.py        # Entrenamiento
│   │
│   ├── domain/
│   │   └── models/
│   │       └── nutritional_predictor.py          # Clase predictor
│   │
│   └── api/
│       └── endpoints/
│           └── nutritional_predictions.py        # Endpoints HTTP
│
└── models/
    └── nutritional_predictor_latest.pkl          # Modelo entrenado
```

---

## Conclusión

Este modelo complementa el sistema PMV3 proporcionando:
- ✅ Predicción temprana de deterioro nutricional
- ✅ Alertas automáticas para intervención
- ✅ Explicabilidad de predicciones
- ✅ Integración con arquitectura existente

**Siguiente paso**: Implementar scripts de entrenamiento
