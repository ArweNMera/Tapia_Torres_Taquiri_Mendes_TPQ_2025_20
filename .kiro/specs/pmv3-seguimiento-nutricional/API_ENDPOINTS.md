# 📚 API Endpoints - PMV3: Seguimiento y Monitoreo Nutricional

## Base URL
```
http://localhost:8000/api/v1
```

---

## 🔐 Autenticación

Todos los endpoints requieren autenticación JWT:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 📊 ADHERENCIA

### 1. Registrar Adherencia

**Endpoint**: `POST /adherencia/registrar`

**Query Params**:
- `nin_id` (int, required): ID del niño

**Body**:
```json
{
  "men_id": 1,
  "mei_id": 1,
  "fecha": "2025-01-15",
  "estado": "OK",
  "porcentaje": 95.0,
  "dificultad": "NINGUNA",
  "comentario": "Todo bien"
}
```

**Estados válidos**: `OK`, `PARCIAL`, `NO`  
**Dificultades válidas**: `NINGUNA`, `BAJA`, `MEDIA`, `ALTA`

**Response**:
```json
{
  "adh_id": 1,
  "nin_id": 1,
  "men_id": 1,
  "mei_id": 1,
  "adh_fecha": "2025-01-15",
  "adh_estado": "OK",
  "adh_porcentaje": 95.0,
  "adh_dificultad": "NINGUNA",
  "adh_comentario": "Todo bien",
  "creado_en": "2025-01-15T10:30:00",
  "actualizado_en": null,
  "men_nombre": "Plan Nutricional Enero",
  "mei_comida": "DESAYUNO"
}
```

---

### 2. Obtener Historial de Adherencia

**Endpoint**: `GET /adherencia/nino/{nin_id}`

**Query Params**:
- `fecha_inicio` (date, optional): Default: hace 30 días
- `fecha_fin` (date, optional): Default: hoy

**Response**:
```json
{
  "registros": [
    {
      "adh_id": 1,
      "nin_id": 1,
      "adh_fecha": "2025-01-15",
      "adh_estado": "OK",
      "adh_porcentaje": 95.0,
      ...
    }
  ],
  "adherencia_promedio": 87.5,
  "dias_con_dificultad_alta": 2
}
```

---

### 3. Calcular Adherencia Promedio

**Endpoint**: `GET /adherencia/nino/{nin_id}/promedio`

**Query Params**:
- `dias` (int, optional): Default: 30, Range: 1-365

**Response**:
```json
{
  "adherencia_promedio": 87.5,
  "consistencia": 12.3,
  "total_registros": 25,
  "dias_analizados": 30
}
```

---

## 🩺 SÍNTOMAS

### 1. Registrar Síntoma

**Endpoint**: `POST /sintomas/registrar`

**Query Params**:
- `nin_id` (int, required): ID del niño

**Body**:
```json
{
  "fecha": "2025-01-15",
  "tipo": "Dolor de estómago",
  "severidad": "LEVE",
  "duracion_dias": 1,
  "relacionado_menu": true,
  "notas": "Después del desayuno"
}
```

**Severidades válidas**: `LEVE`, `MODERADO`, `SEVERO`

**Response**:
```json
{
  "sin_id": 1,
  "nin_id": 1,
  "sin_fecha": "2025-01-15",
  "sin_tipo": "Dolor de estómago",
  "sin_severidad": "LEVE",
  "sin_duracion_dias": 1,
  "sin_relacionado_menu": true,
  "sin_notas": "Después del desayuno",
  "creado_en": "2025-01-15T10:30:00"
}
```

⚠️ **Alerta Automática**: Si se registran más de 3 síntomas en 7 días, se genera una notificación automática para el nutricionista.

---

### 2. Obtener Historial de Síntomas

**Endpoint**: `GET /sintomas/nino/{nin_id}`

**Query Params**:
- `fecha_inicio` (date, optional): Default: hace 30 días
- `fecha_fin` (date, optional): Default: hoy
- `tipo` (string, optional): Filtrar por tipo de síntoma

**Response**:
```json
[
  {
    "sin_id": 1,
    "nin_id": 1,
    "sin_fecha": "2025-01-15",
    "sin_tipo": "Dolor de estómago",
    "sin_severidad": "LEVE",
    ...
  }
]
```

---

### 3. Calcular Frecuencia de Síntomas

**Endpoint**: `GET /sintomas/nino/{nin_id}/frecuencia`

**Query Params**:
- `dias` (int, optional): Default: 30, Range: 1-365

**Response**:
```json
{
  "frecuencia_total": 5,
  "severidad_promedio": 1.8,
  "sintomas_recientes_7dias": 2,
  "tiene_sintomas_recientes": true
}
```

---

## 📈 EVOLUCIÓN

### 1. Obtener Evolución Nutricional

**Endpoint**: `GET /evolucion/nino/{nin_id}`

**Query Params**:
- `fecha_inicio` (date, optional): Default: hace 6 meses
- `fecha_fin` (date, optional): Default: hoy

**Response**:
```json
{
  "nin_id": 1,
  "nin_nombres": "Juan Pérez",
  "fecha_inicio": "2024-07-15",
  "fecha_fin": "2025-01-15",
  "datos": [
    {
      "ant_id": 1,
      "ant_fecha": "2024-07-15",
      "ant_peso_kg": 25.5,
      "ant_talla_cm": 120.0,
      "imc": 17.7,
      "en_z_score_imc": -0.5,
      "en_clasificacion": "NORMAL",
      "en_nivel_riesgo": "BAJO",
      "adherencia_promedio_7dias": 85.0,
      "sintomas_7dias": 1
    },
    ...
  ]
}
```

---

### 2. Calcular Tendencia Nutricional

**Endpoint**: `GET /evolucion/nino/{nin_id}/tendencia`

**Query Params**:
- `ultimas_mediciones` (int, optional): Default: 3, Range: 2-10

**Response**:
```json
{
  "tendencia": "MEJORANDO",
  "bmi_velocity": 0.15,
  "weight_velocity": 0.5,
  "height_velocity": 1.2,
  "z_score_trend": 0.08,
  "mediciones_analizadas": 3
}
```

**Tendencias posibles**: `MEJORANDO`, `ESTABLE`, `EMPEORANDO`

---

## 🤖 PREDICCIONES ML

### 1. Generar Predicción ML

**Endpoint**: `POST /predicciones/generar/{nin_id}`

⚠️ **Estado**: Pendiente de integración con servicio ML

**Response**: `501 Not Implemented`

---

### 2. Obtener Historial de Predicciones

**Endpoint**: `GET /predicciones/nino/{nin_id}`

**Query Params**:
- `limit` (int, optional): Default: 10, Range: 1-50

**Response**:
```json
[
  {
    "pml_id": 1,
    "nin_id": 1,
    "ant_id": 5,
    "fml_id": 10,
    "pml_clasificacion": "NORMAL",
    "pml_probabilidad": 0.85,
    "pml_score_riesgo": 0.15,
    "pml_prob_normal": 0.85,
    "pml_prob_riesgo": 0.10,
    "pml_prob_moderado": 0.03,
    "pml_prob_severo": 0.02,
    "pml_modelo_tipo": "RandomForest",
    "pml_modelo_version": "1.0",
    "pml_features_json": {...},
    "pml_explicacion_json": {...},
    "pml_validado": true,
    "pml_usr_id_validador": 2,
    "pml_feedback": "Predicción correcta",
    "pml_fecha_validacion": "2025-01-16T09:00:00",
    "creado_en": "2025-01-15T10:30:00",
    "ant_fecha": "2025-01-15",
    "ant_peso_kg": 26.0,
    "ant_talla_cm": 121.0,
    "validador_nombre": "Dra. María García"
  }
]
```

---

### 3. Validar Predicción ML

**Endpoint**: `POST /predicciones/{pml_id}/validar`

**Body**:
```json
{
  "validado": true,
  "feedback": "Predicción correcta, coincide con evaluación clínica"
}
```

**Response**: Misma estructura que el historial de predicciones

---

## 🚨 ALERTAS

### 1. Verificar Alertas Automáticas

**Endpoint**: `POST /alertas/verificar/{nin_id}`

**Funcionalidad**: Verifica 4 condiciones y genera alertas si aplican:
1. **TENDENCIA_NEGATIVA**: 3 mediciones consecutivas empeorando
2. **BAJA_ADHERENCIA**: <60% en últimas 2 semanas
3. **SINTOMAS_FRECUENTES**: >5 síntomas en 7 días
4. **RIESGO_CRITICO_ML**: Predicción de DESNUTRICION_SEVERA u OBESIDAD

**Response**:
```json
{
  "alertas_generadas": [
    {
      "not_id": 1,
      "not_tipo": "BAJA_ADHERENCIA",
      "not_payload": {
        "nin_id": 1,
        "adherencia_promedio": 55.0,
        "mensaje": "Adherencia por debajo del 60% en las últimas 2 semanas"
      },
      "not_leido": false,
      "creado_en": "2025-01-15T10:30:00"
    }
  ],
  "total_alertas": 1
}
```

---

## 📝 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 400 | Bad Request - Datos inválidos o fecha futura |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |
| 501 | Not Implemented - Funcionalidad pendiente |

---

## 🧪 Ejemplos con cURL

### Registrar adherencia
```bash
curl -X POST "http://localhost:8000/api/v1/adherencia/registrar?nin_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "men_id": 1,
    "mei_id": 1,
    "fecha": "2025-01-15",
    "estado": "OK",
    "porcentaje": 95.0,
    "dificultad": "NINGUNA",
    "comentario": "Todo bien"
  }'
```

### Obtener evolución
```bash
curl -X GET "http://localhost:8000/api/v1/evolucion/nino/1?fecha_inicio=2024-07-01&fecha_fin=2025-01-15" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Registrar síntoma
```bash
curl -X POST "http://localhost:8000/api/v1/sintomas/registrar?nin_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fecha": "2025-01-15",
    "tipo": "Dolor de estómago",
    "severidad": "LEVE",
    "duracion_dias": 1,
    "relacionado_menu": true,
    "notas": "Después del desayuno"
  }'
```

### Verificar alertas
```bash
curl -X POST "http://localhost:8000/api/v1/alertas/verificar/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📖 Documentación Interactiva

Accede a la documentación Swagger en:
```
http://localhost:8000/docs
```

O a la documentación ReDoc en:
```
http://localhost:8000/redoc
```

---

**Última actualización**: 2025-01-XX  
**Versión**: 1.0
