# 🧪 Cómo Probar el Modelo ML Integrado

## 📋 Pre-requisitos

1. ✅ Modelo entrenado en `models/rf_model.pkl`
2. ✅ Dependencias instaladas (`pip install -r requirements.txt`)
3. ✅ Variables de entorno configuradas (`.env`)

## 🚀 Paso 1: Iniciar el Servidor

```bash
cd modelo/ml-recomendator

# Opción A: Usar script de reinicio
./restart_server.sh

# Opción B: Iniciar manualmente
uvicorn app.main:app --reload --port 8003
```

**Salida esperada**:
```
✅ Modelo ML cargado desde: models/rf_model.pkl
   Features: ['age_months', 'sex_numeric', 'BMI', ...]
INFO:     Uvicorn running on http://127.0.0.1:8001
```

## 🧪 Paso 2: Ejecutar Tests Automáticos

En otra terminal:

```bash
cd modelo/ml-recomendator
python scripts/test_modelo_api.py
```

**Salida esperada**:
```
🧪 TESTS DEL MODELO ML EN LA API
============================================================

1. TEST: Health Check
============================================================
Status: ok
ML Model Loaded: True
LMS Loaded: True
✅ Modelo ML cargado correctamente

2. TEST: Model Info
============================================================
Model Name: RandomForestNutritionClassifier
Version: v1.0
Is Trained: True
Features (11): age_months, sex_numeric, BMI, ...

Top 5 Feature Importance:
  - BMI: 0.3245
  - age_months: 0.1823
  - bmi_velocity: 0.1456
  ...

3. TEST: Predicción Directa (Modelo ML)
============================================================

📊 Niño Normal (5 años)
   BAZ: 0.5
   Predicción: NORMAL
   Probabilidad: 92.00%
   Risk Score: 0.15
   Top 3 Probabilidades:
     - NORMAL: 92.00%
     - RIESGO_DESNUTRICION: 3.00%
     - RIESGO_SOBREPESO: 1.00%
   ✅ Predicción correcta!

📊 Niña con Desnutrición Moderada (3 años)
   BAZ: -2.5
   Predicción: DESNUTRICION_MODERADA
   Probabilidad: 85.00%
   Risk Score: 0.70
   Top 3 Probabilidades:
     - DESNUTRICION_MODERADA: 85.00%
     - RIESGO_DESNUTRICION: 10.00%
     - DESNUTRICION_SEVERA: 5.00%
   ✅ Predicción correcta!

📊 Niño con Sobrepeso (8 años)
   BAZ: 2.5
   Predicción: SOBREPESO
   Probabilidad: 85.00%
   Risk Score: 0.70
   Top 3 Probabilidades:
     - SOBREPESO: 85.00%
     - RIESGO_SOBREPESO: 10.00%
     - OBESIDAD: 5.00%
   ✅ Predicción correcta!

============================================================
✅ TODOS LOS TESTS COMPLETADOS
============================================================

💡 El modelo ML está funcionando correctamente!
   Accuracy: 90.18% (con cross-validation)
   Features: 11 (sin BAZ para evitar overfitting)
```

## 🔍 Paso 3: Pruebas Manuales

### 3.1 Health Check
```bash
curl http://localhost:8001/health
```

**Esperado**:
```json
{
  "status": "ok",
  "ml_model_loaded": true,
  "lms_loaded": true
}
```

### 3.2 Información del Modelo
```bash
curl http://localhost:8001/ml/model_info
```

**Esperado**:
```json
{
  "loaded": true,
  "model_name": "RandomForestNutritionClassifier",
  "version": "v1.0",
  "is_trained": true,
  "features": [
    "age_months",
    "sex_numeric",
    "BMI",
    "bmi_velocity",
    "weight_velocity",
    "height_velocity",
    "allergy_count",
    "adherence_score",
    "symptom_frequency",
    "dietary_diversity_score",
    "altitude_m"
  ],
  "n_features": 11,
  "feature_importance": {
    "BMI": 0.3245,
    "age_months": 0.1823,
    ...
  }
}
```

### 3.3 Predicción Directa - Caso Normal
```bash
curl -X POST http://localhost:8001/ml/predict_direct \
  -H "Content-Type: application/json" \
  -d '{
    "age_months": 60,
    "sex": "M",
    "BMI": 15.5,
    "baz": 0.5,
    "bmi_velocity": 0.1,
    "weight_velocity": 0.2,
    "height_velocity": 0.5,
    "allergy_count": 0,
    "adherence_score": 80.0,
    "symptom_frequency": 0,
    "dietary_diversity_score": 70.0,
    "altitude_m": 2640.0
  }'
```

**Esperado**:
```json
{
  "nin_id": 0,
  "prediction": 3,
  "label": "NORMAL",
  "probability": 0.92,
  "probabilities": {
    "DESNUTRICION_SEVERA": 0.01,
    "DESNUTRICION_MODERADA": 0.02,
    "RIESGO_DESNUTRICION": 0.03,
    "NORMAL": 0.92,
    "RIESGO_SOBREPESO": 0.01,
    "SOBREPESO": 0.01,
    "OBESIDAD": 0.00
  },
  "risk_score": 0.15,
  "features_used": {...},
  "model_version": "v1.0"
}
```

### 3.4 Predicción Directa - Caso Desnutrición
```bash
curl -X POST http://localhost:8001/ml/predict_direct \
  -H "Content-Type: application/json" \
  -d '{
    "age_months": 36,
    "sex": "F",
    "BMI": 13.0,
    "baz": -2.5,
    "bmi_velocity": -0.2,
    "weight_velocity": -0.1,
    "height_velocity": 0.3,
    "allergy_count": 1,
    "adherence_score": 60.0,
    "symptom_frequency": 2,
    "dietary_diversity_score": 50.0,
    "altitude_m": 2640.0
  }'
```

**Esperado**:
```json
{
  "nin_id": 0,
  "prediction": 1,
  "label": "DESNUTRICION_MODERADA",
  "probability": 0.85,
  "probabilities": {
    "DESNUTRICION_SEVERA": 0.05,
    "DESNUTRICION_MODERADA": 0.85,
    "RIESGO_DESNUTRICION": 0.08,
    "NORMAL": 0.01,
    "RIESGO_SOBREPESO": 0.00,
    "SOBREPESO": 0.00,
    "OBESIDAD": 0.00
  },
  "risk_score": 0.70,
  "features_used": {...},
  "model_version": "v1.0"
}
```

## ✅ Verificación de Éxito

El modelo está funcionando correctamente si:

1. ✅ `/health` retorna `"ml_model_loaded": true`
2. ✅ `/ml/model_info` muestra 11 features (sin BAZ)
3. ✅ `/ml/predict_direct` retorna predicciones con 7 categorías
4. ✅ Las probabilidades suman ~1.0
5. ✅ El `label` corresponde a la categoría con mayor probabilidad
6. ✅ El `risk_score` está entre 0.0 y 1.0

## ❌ Troubleshooting

### Problema: "Modelo ML no disponible"
```bash
# Verificar que el modelo existe
ls -lh models/rf_model.pkl

# Si no existe, entrenar el modelo
python3 src/pipeline/train_model.py \
  --data data/raw/surveys/datos_completos_oms_reales.csv \
  --model rf \
  --output models/ \
  --use-cv \
  --cv-folds 5
```

### Problema: "DatabaseConnector no disponible"
```bash
# Verificar variables de entorno
cat .env

# Asegurarse de tener:
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASSWORD=...
# DB_NAME=nutricion_db
```

### Problema: "Error importando modelos ML"
```bash
# Verificar que las dependencias estén instaladas
pip install -r requirements.txt

# Verificar que el módulo src esté en el path
python -c "from src.models import RandomForestNutritionClassifier; print('OK')"
```

## 📊 Comparación con BAZ

Para verificar que el modelo ML es mejor que clasificación por BAZ:

```bash
# Caso límite: BAZ = -1.9 (casi desnutrición moderada)
curl -X POST http://localhost:8001/ml/predict_direct \
  -H "Content-Type: application/json" \
  -d '{
    "age_months": 48,
    "sex": "M",
    "BMI": 14.0,
    "baz": -1.9,
    "bmi_velocity": -0.1,
    "weight_velocity": 0.0,
    "height_velocity": 0.4,
    "allergy_count": 0,
    "adherence_score": 75.0,
    "symptom_frequency": 0,
    "dietary_diversity_score": 65.0,
    "altitude_m": 2640.0
  }'
```

**Clasificación por BAZ**: RIESGO_DESNUTRICION (porque -2 < BAZ < -1)

**Modelo ML**: Puede predecir RIESGO_DESNUTRICION o NORMAL dependiendo del contexto (velocidades, adherencia, etc.)

Esto demuestra que el modelo ML considera más factores que solo el BAZ.

## 🎯 Próximos Pasos

1. ✅ Modelo funcionando en API
2. ⏳ Integrar con backend (Nutricion-api)
3. ⏳ Actualizar frontend para mostrar probabilidades
4. ⏳ Agregar logging de predicciones
5. ⏳ Implementar reentrenamiento periódico

## 📚 Documentación Adicional

- [INTEGRACION_MODELO_ML.md](./INTEGRACION_MODELO_ML.md) - Documentación completa
- [RESUMEN_INTEGRACION.md](./RESUMEN_INTEGRACION.md) - Resumen de cambios
- [MODELO_FINAL_90_ACCURACY.md](./MODELO_FINAL_90_ACCURACY.md) - Detalles del entrenamiento
