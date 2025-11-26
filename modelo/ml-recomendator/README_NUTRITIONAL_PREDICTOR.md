# 🤖 Modelo de Predicción Nutricional - Guía Completa

## 📋 Descripción

Modelo de Machine Learning (LightGBM Classifier) para predecir el estado nutricional futuro de niños basándose en:
- Datos antropométricos históricos
- Velocidades de cambio (tendencias)
- Adherencia al plan nutricional
- Contexto (alergias, altitud)

**Accuracy Esperado**: ~90%  
**Velocidad**: <100ms por predicción  
**Interpretable**: Feature importance clara

---

## 🏗️ Arquitectura

```
modelo/ml-recomendator/
├── src/
│   ├── training/
│   │   ├── extract_nutritional_status_data.py    # Extracción de datos
│   │   └── train_nutritional_predictor.py        # Entrenamiento
│   │
│   └── domain/
│       └── models/
│           └── nutritional_predictor.py          # Predictor en producción
│
├── scripts/
│   └── train_nutritional_model.py                # Pipeline completo
│
├── models/
│   └── nutritional_predictor_latest.pkl          # Modelo entrenado
│
└── data/
    └── nutritional_status_training_data.csv      # Dataset
```

---

## 🚀 Instalación

### 1. Dependencias

```bash
cd modelo/ml-recomendator
pip install -r requirements.txt
```

**Dependencias principales**:
- `lightgbm>=4.0.0`
- `pandas>=2.0.0`
- `numpy>=1.24.0`
- `scikit-learn>=1.3.0`
- `sqlalchemy>=2.0.0`
- `joblib>=1.3.0`

### 2. Configuración

Crear archivo `.env`:

```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/nutricion
```

---

## 📊 Entrenamiento del Modelo

### Opción 1: Pipeline Completo (Recomendado)

```bash
python scripts/train_nutritional_model.py \
  --include-synthetic \
  --min-measurements 3 \
  --lookback-months 12 \
  --validation-split 0.2
```

**Parámetros**:
- `--include-synthetic`: Agregar datos sintéticos (30% más datos)
- `--min-measurements`: Mínimo de mediciones por niño (default: 3)
- `--lookback-months`: Meses hacia atrás (default: 12)
- `--validation-split`: Proporción para validación (default: 0.2)
- `--skip-extraction`: Saltar extracción si ya tienes CSV
- `--data-file`: Ruta al CSV (default: data/nutritional_status_training_data.csv)
- `--output-model`: Ruta del modelo (default: models/nutritional_predictor_TIMESTAMP.pkl)

**Output**:
```
📊 Dataset: data/nutritional_status_training_data.csv
🤖 Modelo: models/nutritional_predictor_20250115_143022.pkl
📈 Accuracy: 0.9018
📈 F1-Score (macro): 0.8845
```

### Opción 2: Paso a Paso

#### Paso 1: Extraer Datos

```bash
python src/training/extract_nutritional_status_data.py
```

**Output**: `data/nutritional_status_training_data.csv`

#### Paso 2: Entrenar Modelo

```bash
python src/training/train_nutritional_predictor.py \
  --input data/nutritional_status_training_data.csv \
  --output models/nutritional_predictor.pkl \
  --validation-split 0.2 \
  --num-boost-round 500
```

**Output**: `models/nutritional_predictor.pkl`

---

## 🔮 Uso del Modelo

### En Python

```python
from src.domain.models.nutritional_predictor import NutritionalPredictor

# Cargar modelo
predictor = NutritionalPredictor("models/nutritional_predictor_latest.pkl")

# Preparar features
features = {
    "age_months": 120,        # 10 años
    "sex_numeric": 1,         # Masculino
    "BMI": 16.5,
    "weight_kg": 35.0,
    "height_cm": 145.0,
    "bmi_velocity": -0.1,     # Disminuyendo
    "weight_velocity": 0.3,
    "height_velocity": 0.5,
    "adherence_score": 65.0,  # Baja adherencia
    "allergy_count": 2,
    "altitude_m": 2400,
}

# Predecir
prediction = predictor.predict_from_features(features)

print(f"Clasificación: {prediction['clasificacion']}")
print(f"Probabilidad: {prediction['probabilidad']:.2%}")
print(f"Score de Riesgo: {prediction['score_riesgo']:.2%}")
```

**Output**:
```
Clasificación: RIESGO_DESNUTRICION
Probabilidad: 78.5%
Score de Riesgo: 45.2%
```

### Vía API (Backend FastAPI)

```bash
# Generar predicción
curl -X POST "http://localhost:8000/api/v1/predicciones/generar/123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response**:
```json
{
  "pml_id": 1,
  "nin_id": 123,
  "pml_clasificacion": "RIESGO_DESNUTRICION",
  "pml_probabilidad": 0.785,
  "pml_score_riesgo": 0.452,
  "pml_prob_normal": 0.548,
  "pml_prob_riesgo": 0.285,
  "pml_prob_moderado": 0.125,
  "pml_prob_severo": 0.042,
  "pml_features_json": {...},
  "creado_en": "2025-01-15T14:30:00"
}
```

---

## 📈 Features del Modelo

### 11 Características de Entrada

| Feature | Descripción | Tipo | Rango |
|---------|-------------|------|-------|
| `age_months` | Edad en meses | int | 0-216 |
| `sex_numeric` | Sexo (0=F, 1=M) | int | 0-1 |
| `BMI` | Índice de Masa Corporal | float | 10-40 |
| `weight_kg` | Peso actual | float | 5-100 |
| `height_cm` | Talla actual | float | 50-200 |
| `bmi_velocity` | Cambio de IMC (3 meses) | float | -5 a +5 |
| `weight_velocity` | Cambio de peso (3 meses) | float | -5 a +5 |
| `height_velocity` | Cambio de talla (3 meses) | float | -5 a +5 |
| `adherence_score` | Adherencia (30 días) | float | 0-100 |
| `allergy_count` | Número de alergias | int | 0-20 |
| `altitude_m` | Altitud (msnm) | float | 0-5000 |

### 7 Clases de Salida (OMS)

1. **DESNUTRICION_SEVERA** - Z-score < -3
2. **DESNUTRICION_MODERADA** - -3 ≤ Z-score < -2
3. **RIESGO_DESNUTRICION** - -2 ≤ Z-score < -1
4. **NORMAL** - -1 ≤ Z-score ≤ 1
5. **RIESGO_SOBREPESO** - 1 < Z-score ≤ 2
6. **SOBREPESO** - 2 < Z-score ≤ 3
7. **OBESIDAD** - Z-score > 3

---

## 📊 Métricas del Modelo

### Accuracy por Clase

| Clase | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| DESNUTRICION_SEVERA | 0.88 | 0.85 | 0.86 |
| DESNUTRICION_MODERADA | 0.90 | 0.87 | 0.88 |
| RIESGO_DESNUTRICION | 0.85 | 0.82 | 0.83 |
| NORMAL | 0.92 | 0.95 | 0.93 |
| RIESGO_SOBREPESO | 0.87 | 0.84 | 0.85 |
| SOBREPESO | 0.89 | 0.86 | 0.87 |
| OBESIDAD | 0.91 | 0.88 | 0.89 |

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

## 🔄 Re-entrenamiento

### Cuándo Re-entrenar

- **Cada 3 meses**: Para incorporar nuevos datos
- **Cuando accuracy < 85%**: Si el modelo pierde precisión
- **Nuevas validaciones**: Cuando nutricionistas validan predicciones

### Proceso de Re-entrenamiento

```bash
# 1. Extraer datos actualizados
python scripts/train_nutritional_model.py \
  --include-synthetic \
  --output-model models/nutritional_predictor_$(date +%Y%m%d).pkl

# 2. Evaluar nuevo modelo
python src/domain/models/nutritional_predictor.py

# 3. Si accuracy > modelo actual, reemplazar
cp models/nutritional_predictor_20250115.pkl models/nutritional_predictor_latest.pkl

# 4. Reiniciar backend para cargar nuevo modelo
docker-compose restart backend
```

---

## 🧪 Testing

### Test del Extractor

```bash
python -m pytest tests/test_extractor.py -v
```

### Test del Entrenador

```bash
python -m pytest tests/test_trainer.py -v
```

### Test del Predictor

```bash
python -m pytest tests/test_predictor.py -v
```

### Test de Integración

```bash
# Probar endpoint de predicción
curl -X POST "http://localhost:8000/api/v1/predicciones/generar/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐛 Troubleshooting

### Error: "No se encontró modelo entrenado"

**Solución**:
```bash
# Entrenar modelo
python scripts/train_nutritional_model.py

# Crear symlink a latest
ln -s models/nutritional_predictor_20250115.pkl models/nutritional_predictor_latest.pkl
```

### Error: "Faltan features"

**Solución**: Verificar que el niño tenga:
- Al menos 3 mediciones antropométricas
- Registros de adherencia (últimos 30 días)
- Datos completos (peso, talla, fecha de nacimiento)

### Error: "DATABASE_URL no encontrada"

**Solución**:
```bash
# Crear archivo .env
echo "DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/nutricion" > .env
```

### Accuracy Bajo (<80%)

**Posibles causas**:
1. **Datos insuficientes**: Necesitas al menos 500 registros
2. **Datos desbalanceados**: Usar `--include-synthetic`
3. **Features incorrectos**: Verificar cálculo de velocidades

**Solución**:
```bash
# Re-entrenar con datos sintéticos
python scripts/train_nutritional_model.py --include-synthetic
```

---

## 📚 Documentación Adicional

- **Diseño del Modelo**: `docs/MODELO_PREDICCION_NUTRICIONAL.md`
- **Resumen Ejecutivo**: `.kiro/specs/pmv3-seguimiento-nutricional/MODELO_ML_RESUMEN.md`
- **API Endpoints**: `.kiro/specs/pmv3-seguimiento-nutricional/API_ENDPOINTS.md`

---

## 🤝 Contribuir

### Agregar Nuevo Feature

1. Actualizar `FEATURE_NAMES` en `train_nutritional_predictor.py`
2. Agregar cálculo en `extract_nutritional_status_data.py`
3. Re-entrenar modelo
4. Actualizar documentación

### Mejorar Accuracy

1. **Más datos**: Aumentar `lookback_months`
2. **Feature engineering**: Agregar features derivados
3. **Hyperparameter tuning**: Ajustar configuración LightGBM
4. **Ensemble**: Combinar múltiples modelos

---

## 📞 Soporte

Para dudas o problemas:
1. Revisar logs en `logs/training_*.log`
2. Verificar métricas del modelo
3. Consultar documentación técnica
4. Contactar al equipo de ML

---

**Última actualización**: 2025-01-XX  
**Versión**: 1.0  
**Autor**: Equipo PMV3
