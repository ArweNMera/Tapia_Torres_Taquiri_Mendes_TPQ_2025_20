# 📊 Diagrama de Flujo del Sistema ML

## 🔄 Flujo Completo: Desde Datos hasta Predicción

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BASE DE DATOS MySQL                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  ninos   │  │antropo-  │  │adherencias│  │ sintomas │           │
│  │          │  │metrias   │  │          │  │          │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ alergias │  │  menus   │  │entidades │  │features_ │           │
│  │          │  │          │  │          │  │   ml     │ ← NUEVA   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTRACCIÓN Y PREPARACIÓN                          │
│                                                                      │
│  1. Extraer datos históricos                                        │
│     └─> sp_calcular_features_ml(nin_id, ant_id)                    │
│                                                                      │
│  2. Calcular features ML                                            │
│     ├─> Temporales (velocidades, tendencias)                        │
│     ├─> Adherencia (scores, consistencia)                           │
│     ├─> Alergias (conteo, severidad)                                │
│     ├─> Síntomas (frecuencia, severidad)                            │
│     └─> Nutricionales (diversidad, calorías)                        │
│                                                                      │
│  3. Etiquetar con OMS                                               │
│     └─> label_dataset.py --in surveys --who who --out labeled.csv  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         ENTRENAMIENTO                                │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  train_model.py --model ensemble --data labeled.csv        │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────┐         ┌─────────────────┐                   │
│  │  Random Forest  │         │ Red Neuronal    │                   │
│  │                 │         │                 │                   │
│  │  • 300 árboles  │         │  • [64, 32]     │                   │
│  │  • Balanced     │         │  • Dropout 0.2  │                   │
│  │  • Max depth    │         │  • Adam lr=0.001│                   │
│  │                 │         │  • 50 epochs    │                   │
│  └────────┬────────┘         └────────┬────────┘                   │
│           │                           │                             │
│           │    Peso 70%      Peso 30% │                             │
│           └───────────┬───────────────┘                             │
│                       ▼                                             │
│              ┌─────────────────┐                                    │
│              │    ENSEMBLE     │                                    │
│              │                 │                                    │
│              │  Combina ambos │                                    │
│              │  modelos con    │                                    │
│              │  pesos óptimos  │                                    │
│              └─────────────────┘                                    │
│                       │                                             │
│                       ▼                                             │
│              ┌─────────────────┐                                    │
│              │ Modelo guardado │                                    │
│              │ ensemble.pkl    │                                    │
│              └─────────────────┘                                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          PREDICCIÓN                                  │
│                                                                      │
│  1. Usuario solicita evaluación de niño                             │
│     └─> POST /ml/predict_nutrition?nin_id=123                      │
│                                                                      │
│  2. Sistema carga features desde BD                                 │
│     ├─> Datos antropométricos actuales                              │
│     ├─> Features ML calculados (features_ml)                        │
│     └─> Contexto (alergias, adherencia, síntomas)                   │
│                                                                      │
│  3. Feature Engineering                                             │
│     └─> FeatureEngineer.create_features(data)                      │
│                                                                      │
│  4. Modelo predice                                                  │
│     ├─> Random Forest: 70% peso                                     │
│     ├─> Red Neuronal: 30% peso                                      │
│     └─> Ensemble combina predicciones                               │
│                                                                      │
│  5. Resultado                                                       │
│     ├─> Clasificación: NORMAL/RIESGO/MODERADO/SEVERO               │
│     ├─> Probabilidades por clase                                    │
│     ├─> Score de riesgo (0-1)                                       │
│     └─> Feature importance (qué influyó más)                        │
│                                                                      │
│  6. Guardar en BD                                                   │
│     └─> INSERT INTO predicciones_ml (...)                          │
│                                                                      │
│  7. Generar explicación                                             │
│     ├─> SHAP values (interpretabilidad)                             │
│     └─> LLM (lenguaje natural)                                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      VALIDACIÓN Y FEEDBACK                           │
│                                                                      │
│  1. Nutricionista revisa predicción                                 │
│     └─> ¿Está de acuerdo?                                          │
│                                                                      │
│  2. Validación                                                      │
│     └─> UPDATE predicciones_ml SET pml_validado=TRUE, ...          │
│                                                                      │
│  3. Feedback loop                                                   │
│     ├─> Casos validados → Nuevo dataset                             │
│     └─> Re-entrenamiento trimestral                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Flujo de Predicción Detallado

```
┌──────────────┐
│   Usuario    │
│  (Frontend)  │
└──────┬───────┘
       │
       │ POST /ml/predict_nutrition
       │ { "nin_id": 123 }
       ▼
┌──────────────────────────────────────────┐
│         API FastAPI                      │
│                                          │
│  1. Validar nin_id existe                │
│  2. Cargar datos del niño                │
│     ├─> Antropometría actual             │
│     ├─> Features ML (features_ml)        │
│     └─> Contexto (alergias, etc)         │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│    FeatureEngineer                       │
│                                          │
│  create_features(data)                   │
│  ├─> Básicos (BMI, edad, sexo)          │
│  ├─> Temporales (velocidades)            │
│  ├─> Adherencia (scores)                 │
│  ├─> Alergias (conteo, severidad)        │
│  ├─> Síntomas (frecuencia)               │
│  └─> Nutricionales (diversidad)          │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│    DataValidator                         │
│                                          │
│  validate_features(data)                 │
│  ├─> ¿Todos los features presentes?     │
│  ├─> ¿Rangos válidos?                    │
│  └─> ¿Outliers extremos?                 │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│    EnsembleNutritionClassifier           │
│                                          │
│  predict_with_metadata(features)         │
│                                          │
│  ┌────────────────┐  ┌────────────────┐ │
│  │ Random Forest  │  │ Red Neuronal   │ │
│  │                │  │                │ │
│  │ predict_proba()│  │ predict_proba()│ │
│  │      ↓         │  │      ↓         │ │
│  │ [0.2, 0.6,     │  │ [0.15, 0.65,   │ │
│  │  0.15, 0.05]   │  │  0.15, 0.05]   │ │
│  └────────┬───────┘  └────────┬───────┘ │
│           │                    │         │
│           │  Peso 0.7  Peso 0.3│         │
│           └──────┬─────────────┘         │
│                  ▼                       │
│         Ensemble Proba:                  │
│         [0.185, 0.615, 0.15, 0.05]      │
│                  │                       │
│                  ▼                       │
│         Clase predicha: 1 (RIESGO)      │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│    Explicabilidad                        │
│                                          │
│  1. Feature Importance (RF)              │
│     ├─> baz: 0.25                        │
│     ├─> adherence_score: 0.18            │
│     ├─> bmi_velocity: 0.12               │
│     └─> ...                              │
│                                          │
│  2. SHAP Values (opcional)               │
│     └─> Contribución de cada feature     │
│                                          │
│  3. LLM Explicación                      │
│     └─> "El niño presenta riesgo de      │
│         desnutrición debido a..."        │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│    Guardar en BD                         │
│                                          │
│  INSERT INTO predicciones_ml (           │
│    nin_id,                               │
│    ant_id,                               │
│    fml_id,                               │
│    pml_clasificacion = 'RIESGO',         │
│    pml_probabilidad = 0.615,             │
│    pml_score_riesgo = 0.10,              │
│    pml_prob_normal = 0.185,              │
│    pml_prob_riesgo = 0.615,              │
│    pml_prob_moderado = 0.15,             │
│    pml_prob_severo = 0.05,               │
│    pml_modelo_tipo = 'ensemble',         │
│    pml_modelo_version = 'v1.0',          │
│    pml_features_json = {...},            │
│    pml_explicacion_json = {...}          │
│  )                                       │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│    Respuesta JSON                        │
│                                          │
│  {                                       │
│    "nin_id": 123,                        │
│    "prediction": {                       │
│      "label": "RIESGO",                  │
│      "probability": 0.615,               │
│      "risk_score": 0.10,                 │
│      "probabilities": {                  │
│        "NORMAL": 0.185,                  │
│        "RIESGO": 0.615,                  │
│        "MODERADO": 0.15,                 │
│        "SEVERO": 0.05                    │
│      }                                   │
│    },                                    │
│    "explanation": "El niño presenta...", │
│    "top_features": [                     │
│      {"name": "baz", "value": -1.5},     │
│      {"name": "adherence", "value": 65}  │
│    ],                                    │
│    "model_version": "v1.0",              │
│    "timestamp": "2025-01-07T10:30:00Z"   │
│  }                                       │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────┐
│   Frontend   │
│              │
│  Muestra:    │
│  • Semáforo  │
│  • Gráfico   │
│  • Explicación│
│  • Botón     │
│    validar   │
└──────────────┘
```

---

## 🔄 Flujo de Re-entrenamiento

```
┌─────────────────────────────────────────┐
│  Trigger: Trimestral o Manual           │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  1. Extraer datos validados             │
│     └─> SELECT * FROM predicciones_ml   │
│         WHERE pml_validado = TRUE       │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  2. Combinar con dataset original       │
│     └─> Más datos = mejor modelo        │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  3. Re-entrenar modelo                  │
│     └─> train_model.py --model ensemble │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  4. Evaluar nuevo modelo                │
│     ├─> Accuracy                        │
│     ├─> Recall SEVERO                   │
│     └─> Comparar con versión anterior   │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  5. ¿Mejora métricas?                   │
│     ├─> SÍ: Desplegar nueva versión     │
│     └─> NO: Mantener versión actual     │
└─────────────────────────────────────────┘
```

---

## 📊 Arquitectura de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE PRESENTACIÓN                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Frontend │  │Dashboard │  │  API     │  │  Mobile  │   │
│  │   Web    │  │Nutrición │  │  REST    │  │   App    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE APLICACIÓN                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              FastAPI (app/main.py)                   │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ /predict   │  │ /explain   │  │ /validate  │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE LÓGICA ML                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              src/models/                             │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │   Random   │  │   Neural   │  │  Ensemble  │    │   │
│  │  │   Forest   │  │   Network  │  │            │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              src/features/                           │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │  Feature   │  │    WHO     │  │ Validator  │    │   │
│  │  │ Engineer   │  │ Calculator │  │            │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      CAPA DE DATOS                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MySQL Database                          │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │   ninos    │  │antropo-    │  │ features_  │    │   │
│  │  │            │  │metrias     │  │    ml      │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  │                                                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │predicciones│  │   menus    │  │  alergias  │    │   │
│  │  │    _ml     │  │            │  │            │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

**Fecha**: 2025-01-07  
**Versión**: 1.0
