# 🚀 API ML - Documentación

API FastAPI para predicción de estado nutricional usando Random Forest.

## 📍 Información

- **Puerto**: 8003
- **URL Base**: `http://localhost:8003`
- **Docs Interactiva**: `http://localhost:8003/docs`
- **Modelo**: Random Forest (93.92% accuracy)

---

## 🔧 Iniciar el Servidor

```bash
cd modelo/ml-recomendator
source venv/bin/activate
./run_api.sh
```

O manualmente:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

---

## 📡 Endpoints Disponibles

### 1. Health Check

**GET** `/health`

Verifica que el servidor y modelo estén funcionando.

**Response**:
```json
{
  "status": "ok",
  "ml_model_loaded": true,
  "lms_loaded": true
}
```

---

### 2. Información del Modelo

**GET** `/ml/model_info`

Obtiene información sobre el modelo cargado.

**Response**:
```json
{
  "loaded": true,
  "model_name": "RandomForestNutritionClassifier",
  "version": "v1.0",
  "is_trained": true,
  "features": [
    "age_months",
    "BMI",
    "baz",
    "bmi_velocity",
    "weight_velocity",
    "height_velocity",
    "allergy_count",
    "adherence_score",
    "symptom_frequency",
    "dietary_diversity_score",
    "altitude_m",
    "sex_numeric"
  ],
  "n_features": 12,
  "feature_importance": {
    "baz": 0.4009,
    "BMI": 0.3467,
    "age_months": 0.1733,
    "allergy_count": 0.0491,
    "sex_numeric": 0.0301
  },
  "model_path": "models/rf_model.pkl"
}
```

---

### 3. Predicción desde BD (Recomendado)

**POST** `/ml/predict`

Predice el estado nutricional de un niño obteniendo datos desde la BD.

**Request**:
```json
{
  "nin_id": 69
}
```

**Response**:
```json
{
  "nin_id": 69,
  "prediction": 0,
  "label": "NORMAL",
  "probability": 0.98,
  "probabilities": {
    "NORMAL": 0.98,
    "RIESGO": 0.01,
    "MODERADO": 0.01,
    "SEVERO": 0.00
  },
  "risk_score": 0.005,
  "features_used": {
    "age_months": 186,
    "BMI": 22.04,
    "baz": 0.68,
    "bmi_velocity": 0.0,
    "weight_velocity": 0.0,
    "height_velocity": 0.0,
    "allergy_count": 0,
    "adherence_score": 75.0,
    "symptom_frequency": 0,
    "dietary_diversity_score": 60.0,
    "altitude_m": 0.0,
    "sex_numeric": 1
  },
  "model_version": "v1.0"
}
```

**Códigos de Estado**:
- `200`: Predicción exitosa
- `404`: Niño no encontrado
- `503`: Modelo no disponible

---

### 4. Predicción Directa (Sin BD)

**POST** `/ml/predict_direct`

Predice el estado nutricional con features proporcionados directamente.

**Request**:
```json
{
  "age_months": 84,
  "sex": "M",
  "BMI": 16.5,
  "baz": 0.5,
  "bmi_velocity": 0.2,
  "weight_velocity": 0.5,
  "height_velocity": 1.0,
  "allergy_count": 1,
  "adherence_score": 80.0,
  "symptom_frequency": 2,
  "dietary_diversity_score": 70.0,
  "altitude_m": 2400.0
}
```

**Response**: Igual que `/ml/predict` pero con `nin_id: 0`

**Campos Opcionales** (valores por defecto):
- `bmi_velocity`: 0.0
- `weight_velocity`: 0.0
- `height_velocity`: 0.0
- `allergy_count`: 0
- `adherence_score`: 75.0
- `symptom_frequency`: 0
- `dietary_diversity_score`: 60.0
- `altitude_m`: 0.0

---

### 5. Predicción BAZ (Legacy)

**POST** `/ml/predict_baz`

Endpoint legacy para calcular BAZ usando tablas OMS.

**Request**:
```json
{
  "age_months": 84,
  "sex": "M",
  "BMI": 16.5
}
```

**Response**:
```json
{
  "bmi": 16.5,
  "baz": 0.45,
  "label_status": 0,
  "label_text": "normal",
  "summary": "Clase: normal (baz=0.45).",
  "used_llm": false
}
```

---

## 🔗 Integración con Backend

### Ejemplo en Node.js/Express

```javascript
const axios = require('axios');

const ML_API_URL = 'http://localhost:8003';

async function predecirEstadoNutricional(ninId) {
  try {
    const response = await axios.post(`${ML_API_URL}/ml/predict`, {
      nin_id: ninId
    });

    const { label, probability, probabilities, risk_score } = response.data;

    console.log(`Predicción: ${label} (${(probability * 100).toFixed(1)}%)`);
    console.log(`Risk Score: ${risk_score.toFixed(3)}`);

    return response.data;
  } catch (error) {
    console.error('Error en predicción ML:', error.message);
    throw error;
  }
}

// Uso
predecirEstadoNutricional(69)
  .then(result => console.log(result))
  .catch(err => console.error(err));
```

### Ejemplo en Python

```python
import requests

ML_API_URL = 'http://localhost:8003'

def predecir_estado_nutricional(nin_id: int):
    response = requests.post(
        f'{ML_API_URL}/ml/predict',
        json={'nin_id': nin_id}
    )
    response.raise_for_status()
    return response.json()

# Uso
result = predecir_estado_nutricional(69)
print(f"Predicción: {result['label']} ({result['probability']:.1%})")
```

### Ejemplo con cURL

```bash
# Predicción desde BD
curl -X POST "http://localhost:8003/ml/predict" \
  -H "Content-Type: application/json" \
  -d '{"nin_id": 69}'

# Predicción directa
curl -X POST "http://localhost:8003/ml/predict_direct" \
  -H "Content-Type: application/json" \
  -d '{
    "age_months": 84,
    "sex": "M",
    "BMI": 16.5,
    "baz": 0.5
  }'

# Info del modelo
curl "http://localhost:8003/ml/model_info"
```

---

## 📊 Interpretación de Resultados

### Clasificaciones

| Código | Label | Descripción |
|--------|-------|-------------|
| 0 | NORMAL | Estado nutricional normal |
| 1 | RIESGO | En riesgo de desnutrición/sobrepeso |
| 2 | MODERADO | Desnutrición o sobrepeso moderado |
| 3 | SEVERO | Desnutrición severa u obesidad |

### Probabilidades

```json
"probabilities": {
  "NORMAL": 0.85,    // 85% probabilidad de ser NORMAL
  "RIESGO": 0.10,    // 10% probabilidad de ser RIESGO
  "MODERADO": 0.04,  // 4% probabilidad de ser MODERADO
  "SEVERO": 0.01     // 1% probabilidad de ser SEVERO
}
```

### Risk Score

Score ponderado de riesgo (0-1):
- `risk_score = prob_MODERADO * 0.5 + prob_SEVERO * 1.0`
- **0.0 - 0.2**: Bajo riesgo
- **0.2 - 0.5**: Riesgo moderado
- **0.5 - 1.0**: Alto riesgo

---

## ⚠️ Manejo de Errores

### Error 503: Modelo no disponible

```json
{
  "detail": "Modelo ML no disponible. Ejecuta: python src/pipeline/train_model.py"
}
```

**Solución**: Entrenar el modelo
```bash
./scripts/regenerar_datos.sh
```

### Error 404: Niño no encontrado

```json
{
  "detail": "No se encontraron datos para nin_id=999"
}
```

**Solución**: Verificar que el niño existe y tiene antropometría

### Error 400: Features faltantes

```json
{
  "detail": "Features faltantes: ['baz', 'BMI']"
}
```

**Solución**: Calcular features ML
```bash
python3 scripts/calcular_features_todos.py
```

---

## 🔒 Seguridad

### CORS

Por defecto permite todos los orígenes. Para producción, configura en `.env`:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Rate Limiting

Considera agregar rate limiting en producción:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/ml/predict")
@limiter.limit("10/minute")
def predict_ml(req: PredictMLRequest):
    ...
```

---

## 📈 Monitoreo

### Logs

Los logs se muestran en la terminal donde se ejecuta el servidor.

### Métricas

Considera agregar Prometheus/Grafana para monitoreo en producción.

---

## 🧪 Testing

### Test Manual

```bash
# 1. Iniciar servidor
./run_api.sh

# 2. En otra terminal, probar endpoints
curl http://localhost:8003/health
curl http://localhost:8003/ml/model_info
curl -X POST http://localhost:8003/ml/predict -H "Content-Type: application/json" -d '{"nin_id": 69}'
```

### Test Automatizado

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_model_info():
    response = client.get("/ml/model_info")
    assert response.status_code == 200
    assert response.json()["loaded"] == True

def test_predict_direct():
    response = client.post("/ml/predict_direct", json={
        "age_months": 84,
        "sex": "M",
        "BMI": 16.5,
        "baz": 0.5
    })
    assert response.status_code == 200
    assert "prediction" in response.json()
```

---

## 📚 Recursos Adicionales

- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc
- **OpenAPI JSON**: http://localhost:8003/openapi.json

---

## 🆘 Soporte

Si tienes problemas:

1. Verifica que el modelo esté entrenado: `ls -lh models/rf_model.pkl`
2. Revisa logs del servidor
3. Prueba `/health` y `/ml/model_info`
4. Consulta `RESUMEN_FINAL.md` y `FLUJO_ENTRENAMIENTO.md`

---

**Última actualización**: Enero 2025  
**Versión API**: 0.1.0  
**Modelo**: Random Forest v1.0 (93.92% accuracy)
