# 🔗 Integración ML - Backend

Documentación de la integración del modelo ML con el backend.

---

## ✅ Cambios Realizados

### 1. Nuevo Endpoint en Backend

**Archivo**: `app/api/v1/endpoints/ml.py`

Se agregaron 2 nuevos endpoints:

#### POST `/api/v1/ml/analisis_nutricional`

Análisis nutricional completo usando modelo ML (Random Forest 93.92% accuracy).

**Request**:
```json
{
  "nin_id": 202,
  "peso_kg": 45.0,
  "talla_cm": 150.0,
  "fecha_medicion": "2025-10-07"
}
```

**Response**:
```json
{
  "fecha": "07/10/2025",
  "peso_kg": 45.0,
  "talla_cm": 150.0,
  "imc": 20.0,
  "diagnostico": "NORMAL",
  "imc_valor": 20.0,
  "percentil": 60.4,
  "nivel_riesgo": "BAJO",
  "baz": 0.26,
  "probabilidad": 0.98,
  "probabilidades": {
    "NORMAL": 0.98,
    "RIESGO": 0.01,
    "MODERADO": 0.01,
    "SEVERO": 0.00
  },
  "recomendaciones": [
    {
      "icono": "✅",
      "titulo": "Mantener alimentación balanceada...",
      "descripcion": "Continuar con 3 comidas principales..."
    }
  ],
  "modelo_usado": true,
  "modelo_version": "v1.0"
}
```

#### GET `/api/v1/ml/health`

Verifica el estado de la API ML.

**Response**:
```json
{
  "status": "ok",
  "ml_api_url": "http://localhost:8003",
  "ml_api_status": "ok",
  "ml_model_loaded": true
}
```

---

### 2. Dependencias Agregadas

**Archivo**: `requirements.txt`

```txt
httpx==0.25.0  # Para llamadas HTTP asíncronas a la API ML
```

**Instalar**:
```bash
pip install httpx==0.25.0
```

---

### 3. Variables de Entorno

**Archivo**: `.env`

```env
# API ML (Modelo Random Forest)
ML_API_URL=http://localhost:8003
```

---

## 🚀 Cómo Usar

### 1. Iniciar API ML (Puerto 8003)

```bash
cd modelo/ml-recomendator
source venv/bin/activate
./run_api.sh
```

Verifica que esté corriendo:
```bash
curl http://localhost:8003/health
```

### 2. Iniciar Backend (Puerto 8000)

```bash
cd control/Nutricion-api/nutricion-api
source .venv/bin/activate  # o tu entorno virtual
uvicorn app.main:app --reload --port 8000
```

### 3. Probar Integración

```bash
# Verificar salud de ML
curl http://localhost:8000/api/v1/ml/health

# Hacer análisis nutricional
curl -X POST http://localhost:8000/api/v1/ml/analisis_nutricional \
  -H "Content-Type: application/json" \
  -d '{
    "nin_id": 202,
    "peso_kg": 45,
    "talla_cm": 150,
    "fecha_medicion": "2025-10-07"
  }'
```

---

## 🔄 Flujo Completo

```
Frontend (React)
    ↓
    POST /api/v1/ml/analisis_nutricional
    ↓
Backend (FastAPI - Puerto 8000)
    ↓
    POST http://localhost:8003/ml/analisis_nutricional
    ↓
API ML (FastAPI - Puerto 8003)
    ↓
Modelo Random Forest (93.92% accuracy)
    ↓
Base de Datos MySQL (features_ml)
    ↓
Response JSON
    ↓
Backend → Frontend
```

---

## 📊 Comparación: Antes vs Ahora

### Antes (Procedimientos Almacenados)

```python
# Backend llamaba directamente a MySQL
result = db.execute("CALL sp_analisis_nutricional(?, ?, ?)", [nin_id, peso, talla])
```

**Problemas**:
- Lógica compleja en SQL
- Difícil de mantener
- No aprende de datos históricos
- Recomendaciones genéricas

### Ahora (Modelo ML)

```python
# Backend llama a API ML
response = await httpx.post("http://localhost:8003/ml/analisis_nutricional", json={...})
```

**Ventajas**:
- Modelo ML con 93.92% accuracy
- Aprende de datos históricos
- Recomendaciones personalizadas
- Fácil de actualizar (reentrenar modelo)
- Separación de responsabilidades

---

## 🎨 Actualizar Frontend

El frontend **NO necesita cambios** si ya llamaba a un endpoint de antropometría.

Solo cambiar la URL del endpoint:

### Antes
```javascript
POST /api/v1/antropometrias
```

### Ahora
```javascript
POST /api/v1/ml/analisis_nutricional
```

El formato de response es compatible.

---

## ⚠️ Manejo de Errores

### Error 503: API ML no disponible

```json
{
  "detail": "No se puede conectar a la API ML. Verifica que esté corriendo en puerto 8003"
}
```

**Solución**: Iniciar API ML
```bash
cd modelo/ml-recomendator && ./run_api.sh
```

### Error 404: Niño no encontrado

```json
{
  "detail": "Niño con ID 999 no encontrado"
}
```

**Solución**: Verificar que el niño existe en la BD

### Error 504: Timeout

```json
{
  "detail": "Timeout al conectar con API ML"
}
```

**Solución**: Verificar que la API ML responde rápido

---

## 🧪 Testing

### Test Manual

```bash
# 1. Verificar salud
curl http://localhost:8000/api/v1/ml/health

# 2. Análisis nutricional
curl -X POST http://localhost:8000/api/v1/ml/analisis_nutricional \
  -H "Content-Type: application/json" \
  -d '{
    "nin_id": 202,
    "peso_kg": 45,
    "talla_cm": 150
  }'
```

### Test con Python

```python
import requests

# Análisis nutricional
response = requests.post(
    "http://localhost:8000/api/v1/ml/analisis_nutricional",
    json={
        "nin_id": 202,
        "peso_kg": 45,
        "talla_cm": 150,
        "fecha_medicion": "2025-10-07"
    }
)

print(response.json())
```

---

## 📈 Monitoreo

### Logs

Los logs se muestran en las terminales de:
- Backend (puerto 8000)
- API ML (puerto 8003)

### Métricas

Considera agregar:
- Tiempo de respuesta
- Tasa de errores
- Uso de CPU/memoria

---

## 🔒 Producción

### Configuración

```env
# Producción
ML_API_URL=http://ml-api:8003  # URL interna en Docker/K8s
```

### Docker Compose

```yaml
version: '3.8'
services:
  backend:
    build: ./control/Nutricion-api
    ports:
      - "8000:8000"
    environment:
      - ML_API_URL=http://ml-api:8003
    depends_on:
      - ml-api
  
  ml-api:
    build: ./modelo/ml-recomendator
    ports:
      - "8003:8003"
    volumes:
      - ./modelo/ml-recomendator/models:/app/models
```

---

## 📚 Recursos

- **API ML Docs**: http://localhost:8003/docs
- **Backend Docs**: http://localhost:8000/docs
- **Modelo**: `modelo/ml-recomendator/RESUMEN_FINAL.md`
- **Integración**: `modelo/ml-recomendator/docs/INTEGRACION_BACKEND.md`

---

## 🆘 Soporte

Si tienes problemas:

1. Verifica que ambos servicios estén corriendo:
   ```bash
   curl http://localhost:8003/health  # API ML
   curl http://localhost:8000/api/v1/ml/health  # Backend
   ```

2. Revisa logs en ambas terminales

3. Verifica variables de entorno en `.env`

---

**Última actualización**: Enero 2025  
**Versión**: 1.0  
**Estado**: ✅ Integrado y funcionando
