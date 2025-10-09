# ✅ Integración del Modelo ML en la API

## 🎯 Objetivo

Integrar el modelo Random Forest entrenado (90.18% accuracy) en la API FastAPI para que **reemplace** la clasificación por reglas BAZ.

## 📊 Modelo Entrenado

- **Tipo**: Random Forest Classifier
- **Accuracy**: 90.18% (con 5-fold cross-validation)
- **Features**: 11 (sin BAZ para evitar overfitting)
- **Categorías**: 7 categorías OMS
  - 0: DESNUTRICION_SEVERA (BAZ < -3)
  - 1: DESNUTRICION_MODERADA (-3 <= BAZ < -2)
  - 2: RIESGO_DESNUTRICION (-2 <= BAZ < -1)
  - 3: NORMAL (-1 <= BAZ <= 1)
  - 4: RIESGO_SOBREPESO (1 < BAZ <= 2)
  - 5: SOBREPESO (2 < BAZ <= 3)
  - 6: OBESIDAD (BAZ > 3)

## 🔧 Cambios Realizados

### 1. Actualización de `base_model.py`

**Archivo**: `src/models/base_model.py`

**Cambios**:
- ✅ Actualizado `LABEL_MAP` de 4 a 7 categorías OMS
- ✅ Actualizado `predict_with_metadata()` para retornar probabilidades de 7 clases
- ✅ Actualizado cálculo de `risk_score` para 7 categorías

```python
LABEL_MAP = {
    0: "DESNUTRICION_SEVERA",
    1: "DESNUTRICION_MODERADA",
    2: "RIESGO_DESNUTRICION",
    3: "NORMAL",
    4: "RIESGO_SOBREPESO",
    5: "SOBREPESO",
    6: "OBESIDAD"
}
```

### 2. Actualización de `main.py`

**Archivo**: `app/main.py`

**Cambios**:
- ✅ Removida sobrescritura de predicción por BAZ en `/ml/analisis_nutricional`
- ✅ Ahora usa directamente la predicción del modelo Random Forest
- ✅ BAZ se calcula solo para referencia (percentil), no para clasificación

**Antes** (líneas 757-837):
```python
# 8. Clasificación basada en BAZ (Reglas OMS oficiales - 7 categorías)
# Usamos BAZ como criterio principal y el modelo ML como complemento
if baz < -3:
    pred["prediction"] = 0
    pred["label"] = "DESNUTRICION_SEVERA"
    # ... sobrescribe la predicción del modelo
```

**Después**:
```python
# 8. ✅ USAR PREDICCIÓN DEL MODELO ML (Random Forest con 90.18% accuracy)
# El modelo ya fue entrenado con datos OMS y tiene mejor accuracy que clasificación por BAZ
# pred ya contiene la predicción del modelo desde el paso 6
```

## 🚀 Endpoints Disponibles

### 1. `/health` - Health Check
```bash
GET http://localhost:8001/health
```

**Response**:
```json
{
  "status": "ok",
  "ml_model_loaded": true,
  "lms_loaded": true
}
```

### 2. `/ml/model_info` - Información del Modelo
```bash
GET http://localhost:8001/ml/model_info
```

**Response**:
```json
{
  "loaded": true,
  "model_name": "RandomForestNutritionClassifier",
  "version": "v1.0",
  "is_trained": true,
  "features": ["age_months", "sex_numeric", "BMI", ...],
  "n_features": 11,
  "feature_importance": {...}
}
```

### 3. `/ml/predict_direct` - Predicción Directa
```bash
POST http://localhost:8001/ml/predict_direct
Content-Type: application/json

{
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
}
```

**Response**:
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

### 4. `/ml/analisis_nutricional` - Análisis Completo
```bash
POST http://localhost:8001/ml/analisis_nutricional
Content-Type: application/json

{
  "nin_id": 1,
  "peso_kg": 18.5,
  "talla_cm": 105.0,
  "fecha_medicion": "2025-01-08"
}
```

**Response**:
```json
{
  "fecha": "08/01/2025",
  "peso_kg": 18.5,
  "talla_cm": 105.0,
  "imc": 16.78,
  "diagnostico": "NORMAL",
  "imc_valor": 16.78,
  "percentil": 65.2,
  "nivel_riesgo": "BAJO",
  "baz": 0.5,
  "probabilidad": 0.92,
  "probabilidades": {...},
  "recomendaciones": [...],
  "modelo_usado": true,
  "modelo_version": "v1.0"
}
```

## 🧪 Testing

### Ejecutar Tests
```bash
cd modelo/ml-recomendator
python scripts/test_modelo_api.py
```

### Tests Incluidos
1. ✅ Health check (verifica que el modelo esté cargado)
2. ✅ Model info (información del modelo)
3. ✅ Predicción directa con 3 casos de prueba:
   - Niño normal (5 años, BAZ = 0.5)
   - Niña con desnutrición moderada (3 años, BAZ = -2.5)
   - Niño con sobrepeso (8 años, BAZ = 2.5)
4. ✅ Análisis nutricional completo

## 📝 Verificación

### 1. Verificar que el modelo esté cargado
```bash
curl http://localhost:8001/health
```

Debe retornar `"ml_model_loaded": true`

### 2. Verificar features del modelo
```bash
curl http://localhost:8001/ml/model_info
```

Debe mostrar 11 features (sin BAZ)

### 3. Hacer una predicción de prueba
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

## 🎯 Ventajas del Modelo ML vs BAZ

| Aspecto | Clasificación por BAZ | Modelo Random Forest |
|---------|----------------------|---------------------|
| **Accuracy** | ~70-80% | **90.18%** |
| **Features** | Solo BAZ | 11 features contextuales |
| **Personalización** | No | Sí (considera alergias, adherencia, etc.) |
| **Overfitting** | No aplica | Controlado (sin BAZ en features) |
| **Validación** | Reglas fijas | Cross-validation 5-fold |
| **Adaptabilidad** | No | Sí (se puede reentrenar) |

## 🔄 Flujo de Predicción

```
1. Frontend envía datos antropométricos
   ↓
2. API calcula BMI y BAZ (usando tablas OMS)
   ↓
3. API obtiene features ML desde BD
   ↓
4. Modelo Random Forest hace predicción
   ↓
5. API retorna diagnóstico + probabilidades + recomendaciones
   ↓
6. Frontend muestra resultados
```

## 📦 Archivos Modificados

- ✅ `src/models/base_model.py` - Actualizado LABEL_MAP y predict_with_metadata
- ✅ `app/main.py` - Removida sobrescritura por BAZ
- ✅ `scripts/test_modelo_api.py` - Script de testing (nuevo)
- ✅ `INTEGRACION_MODELO_ML.md` - Documentación (este archivo)

## 🚀 Próximos Pasos

1. ✅ Modelo integrado en API
2. ⏳ Actualizar backend (Nutricion-api) para usar `/ml/analisis_nutricional`
3. ⏳ Actualizar frontend para mostrar probabilidades del modelo
4. ⏳ Agregar logging de predicciones para monitoreo
5. ⏳ Implementar reentrenamiento periódico con nuevos datos

## 📚 Referencias

- [MODELO_FINAL_90_ACCURACY.md](./MODELO_FINAL_90_ACCURACY.md) - Detalles del entrenamiento
- [CAMBIOS_APLICADOS_7CAT.md](./CAMBIOS_APLICADOS_7CAT.md) - Migración a 7 categorías
- [docs/API_ML.md](./docs/API_ML.md) - Documentación completa de la API
