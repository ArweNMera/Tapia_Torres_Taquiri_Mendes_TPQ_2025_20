# Cambios: Modelo Directo Integrado

## ✅ Cambios Realizados

### 1. Actualización de `app/main.py`

**Antes:**
- Usaba `RandomForestNutritionClassifier`
- Requería muchos features (BAZ, velocidades, alergias, etc.)
- Modelo complejo con riesgo de overfitting

**Ahora:**
- Usa `DirectNutritionClassifier`
- Solo requiere: edad, sexo, peso, talla
- Modelo más simple y directo

### 2. Endpoint `/ml/predict_direct` Actualizado

**Request simplificado:**
```json
{
  "age_months": 84,
  "sex": "F",
  "weight_kg": 30.0,
  "height_cm": 120.0
}
```

**Response:**
```json
{
  "nin_id": 0,
  "prediction": 3,
  "label": "NORMAL",
  "probability": 0.85,
  "probabilities": {
    "DESNUTRICION_SEVERA": 0.01,
    "DESNUTRICION_MODERADA": 0.02,
    "RIESGO_DESNUTRICION": 0.05,
    "NORMAL": 0.85,
    "RIESGO_SOBREPESO": 0.04,
    "SOBREPESO": 0.02,
    "OBESIDAD": 0.01
  },
  "risk_score": 0.0,
  "features_used": {
    "edad_meses": 84,
    "sexo": "F",
    "peso_kg": 30.0,
    "talla_cm": 120.0,
    "bmi": 20.83
  },
  "model_version": "2.0.0-directo"
}
```

### 3. Endpoint `/ml/model_info` Actualizado

Ahora retorna información del modelo directo:
```json
{
  "loaded": true,
  "model_name": "DirectNutritionClassifier",
  "model_type": "Modelo Directo (aprende de edad, peso, talla)",
  "version": "2.0.0-directo",
  "categorias": [
    "DESNUTRICION_SEVERA",
    "DESNUTRICION_MODERADA",
    "RIESGO_DESNUTRICION",
    "NORMAL",
    "RIESGO_SOBREPESO",
    "SOBREPESO",
    "OBESIDAD"
  ],
  "features_basicas": ["edad_meses", "sexo", "peso_kg", "talla_cm"],
  "descripcion": "Modelo que aprende DIRECTAMENTE de datos antropométricos básicos"
}
```

## 🚀 Cómo Usar

### 1. Entrenar el Modelo

```bash
cd modelo/ml-recomendator
source venv/bin/activate
./ENTRENAR_AHORA.sh
```

### 2. Iniciar el Servidor

```bash
# Opción 1: Servidor normal
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Opción 2: Script dedicado (si lo prefieres)
./iniciar_servidor_directo.sh
```

### 3. Probar el Endpoint

```bash
curl -X POST "http://localhost:8001/ml/predict_direct" \
  -H "Content-Type: application/json" \
  -d '{
    "age_months": 84,
    "sex": "F",
    "weight_kg": 30.0,
    "height_cm": 120.0
  }'
```

### 4. Ver Documentación Interactiva

Abre en tu navegador:
- http://localhost:8001/docs (Swagger UI)
- http://localhost:8001/redoc (ReDoc)

## 📊 Ventajas del Modelo Directo

1. **Más Simple**: Solo 4 datos de entrada
2. **Más Rápido**: No necesita calcular features complejos
3. **Más Robusto**: Menos dependencias, menos puntos de falla
4. **Más Fácil de Integrar**: API más simple para el frontend
5. **Aprende Patrones OMS**: El modelo aprende directamente de los datos

## 🔄 Compatibilidad

El endpoint `/ml/predict_direct` es **retrocompatible** pero ahora es más simple:

**Antes** (requería muchos parámetros):
```json
{
  "age_months": 84,
  "sex": "F",
  "BMI": 20.83,
  "baz": 0.5,
  "bmi_velocity": 0.1,
  "weight_velocity": 0.2,
  ...
}
```

**Ahora** (solo lo esencial):
```json
{
  "age_months": 84,
  "sex": "F",
  "weight_kg": 30.0,
  "height_cm": 120.0
}
```

## 📝 Notas

- El modelo anterior (`RandomForestNutritionClassifier`) sigue disponible en `app/main_old_backup.py`
- Los endpoints de BAZ (`/ml/predict_baz`) siguen funcionando igual
- El endpoint `/ml/predict` (con nin_id) necesita actualización si quieres usarlo con el modelo directo
