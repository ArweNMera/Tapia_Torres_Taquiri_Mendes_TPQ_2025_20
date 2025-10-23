# ml-recomendator

Sistema de Machine Learning para evaluación nutricional infantil (0-19 años).

## 🚀 Inicio Rápido

### Reentrenar Modelo (Cuando entren más niños)
```bash
cd modelo/ml-recomendator
./actualizar_modelo.sh
docker-compose restart
```

### Generar Gráficas
```bash
./generar_graficas.sh
```

### Verificar que Todo Funciona
```bash
./verificar_integracion.sh
```

📖 **[Ver Guía Rápida Completa →](GUIA_RAPIDA.md)**

---

## 🎯 Modelo Implementado

**✅ Random Forest Classifier - 90.18% Accuracy (INTEGRADO)**

- ✅ **Accuracy**: 90.18% (5-fold cross-validation)
- ✅ **Features**: 11 (sin BAZ para evitar overfitting)
- ✅ **Categorías**: 7 categorías OMS
- ✅ **Estado**: Completamente integrado en API FastAPI
- ✅ **Archivo**: `models/rf_model.pkl` (44MB)

### 📊 Comparación con Clasificación por BAZ

| Aspecto | BAZ | Random Forest |
|---------|-----|---------------|
| Accuracy | ~70-80% | **90.18%** ✅ |
| Features | 1 (solo BAZ) | 11 (contextuales) |
| Personalización | No | Sí |
| Contexto | No | Sí (alergias, adherencia, velocidades) |

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| **[GUIA_RAPIDA.md](GUIA_RAPIDA.md)** | 🚀 Comandos esenciales y flujos comunes |
| **[REENTRENAR_MODELO.md](REENTRENAR_MODELO.md)** | 🔄 Cómo actualizar el modelo con nuevos datos |
| **[GUIA_GRAFICAS.md](GUIA_GRAFICAS.md)** | 📊 Cómo generar y entender las gráficas |
| **[EXPLICACION_DATOS.md](EXPLICACION_DATOS.md)** | 📈 De dónde vienen los datos |
| **[COMO_PROBAR.md](COMO_PROBAR.md)** | ✅ Cómo probar que todo funciona |

## 📁 Estructura del Proyecto

```
modelo/ml-recomendator/
├── docs/                           # 📚 Documentación
│   ├── ARQUITECTURA_ML.md          # Arquitectura completa del sistema
│   ├── MIGRACIONES_BD.sql          # Scripts SQL para base de datos
│   └── RESUMEN_IMPLEMENTACION.md   # Guía de implementación
│
├── src/
│   ├── models/                     # 🤖 Modelos ML
│   │   ├── base_model.py           # Clase base abstracta
│   │   ├── rf_classifier.py        # Random Forest
│   │   ├── nn_classifier.py        # Red Neuronal (PyTorch)
│   │   └── ensemble.py             # Ensemble RF+NN
│   │
│   ├── features/                   # 🔧 Feature Engineering
│   │   ├── engineering.py          # Generación de features
│   │   ├── who_calculator.py       # Cálculos OMS (BAZ, percentiles)
│   │   └── validators.py           # Validación de datos
│   │
│   ├── pipeline/                   # 🔄 Pipeline de datos
│   │   ├── label_dataset.py        # Etiquetado con OMS
│   │   └── train_model.py          # Entrenamiento
│   │
│   ├── inference/                  # 🎯 Predicción
│   └── llm/                        # 💬 Explicaciones con LLM
│
├── configs/                        # ⚙️ Configuraciones
│   ├── rf.yaml                     # Config Random Forest
│   └── nn.yaml                     # Config Red Neuronal
│
├── data/
│   ├── raw/who/                    # Tablas OMS LMS
│   ├── raw/surveys/                # Datos crudos
│   ├── interim/                    # Datos procesados
│   └── processed/                  # Datos finales
│
├── models/                         # 💾 Modelos entrenados
└── reports/                        # 📊 Métricas y visualizaciones
```

## 🚀 Inicio Rápido

### 1. Instalación

```bash
cd modelo/ml-recomendator
pip install -r requirements.txt
```

### 2. Configurar Base de Datos

```bash
# Ejecutar migraciones
mysql -u root -p nutricion < docs/MIGRACIONES_BD.sql
```

### 3. Preparar Datos

```bash
# Etiquetar dataset con estándares OMS
python src/pipeline/label_dataset.py \
  --in data/raw/surveys \
  --who data/raw/who \
  --out data/interim/labeled_data.csv
```

### 4. Entrenar Modelo

```bash
# Entrenar Ensemble (recomendado)
python src/pipeline/train_model.py \
  --data data/interim/labeled_data.csv \
  --model ensemble \
  --output models/

# O entrenar modelos individuales
python src/pipeline/train_model.py --model rf    # Random Forest
python src/pipeline/train_model.py --model nn    # Red Neuronal
```

### 5. Usar en Producción

```python
from pathlib import Path
from src.models import EnsembleNutritionClassifier
import pandas as pd

# Cargar modelo
model = EnsembleNutritionClassifier()
model.load(Path("models/ensemble_model.pkl"))

# Preparar datos
data = pd.DataFrame({
    "age_months": [36],
    "sex_numeric": [0],
    "BMI": [15.2],
    "baz": [-1.5],
    # ... otros features
})

# Predecir
result = model.predict_with_metadata(data)
print(result["predictions"][0]["label"])  # "RIESGO"
```

## 📊 Features del Modelo

### Básicos
- Antropométricos: `age_months`, `sex`, `BMI`, `baz`, `weight_kg`, `height_cm`

### Temporales (Tendencias)
- `bmi_velocity`, `weight_velocity`, `height_velocity`
- `baz_trend`, `measurements_count`

### Adherencia
- `adherence_score`, `adherence_consistency`, `menu_completion_rate`

### Alergias
- `allergy_count`, `allergy_severity_max`, `food_allergy_count`

### Síntomas
- `symptom_frequency`, `symptom_severity_avg`, `has_recent_symptoms`

### Nutricionales
- `dietary_diversity_score`, `menu_kcal_avg`, `protein_intake_score`

### Contextuales
- `altitude_m`, `entity_type`, `region`

## 🎯 Clasificación (7 Categorías OMS)

| Label | Clasificación | Z-Score BAZ | Descripción |
|-------|---------------|-------------|-------------|
| 0 | DESNUTRICION_SEVERA | < -3 | Desnutrición severa |
| 1 | DESNUTRICION_MODERADA | -3 a -2 | Desnutrición moderada |
| 2 | RIESGO_DESNUTRICION | -2 a -1 | Riesgo de desnutrición |
| 3 | NORMAL | -1 a +1 | Estado nutricional adecuado |
| 4 | RIESGO_SOBREPESO | +1 a +2 | Riesgo de sobrepeso |
| 5 | SOBREPESO | +2 a +3 | Sobrepeso |
| 6 | OBESIDAD | > +3 | Obesidad |

## 📈 Métricas Alcanzadas

| Métrica | Objetivo | Alcanzado |
|---------|----------|-----------|
| Accuracy global | ≥ 85% | **90.18%** ✅ |
| F1-Score promedio | ≥ 0.83 | **0.8843** ✅ |
| Cross-validation | 5-fold | **Completado** ✅ |
| Tiempo inferencia | < 100ms | **< 50ms** ✅ |

### Top 5 Features por Importancia
1. BMI: 32.45%
2. age_months: 18.23%
3. bmi_velocity: 14.56%
4. weight_velocity: 11.34%
5. height_velocity: 9.87%

## 🔧 API FastAPI

El modelo está **completamente integrado** en la API FastAPI:

```bash
# Iniciar servidor
./restart_server.sh
# O manualmente:
uvicorn app.main:app --reload --port 8001

# Verificar integración
bash verificar_integracion.sh

# Ejecutar tests
python scripts/test_modelo_api.py
```

### Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check (verifica modelo cargado) |
| `/ml/model_info` | GET | Información del modelo |
| `/ml/predict_direct` | POST | Predicción directa (sin BD) |
| `/ml/analisis_nutricional` | POST | Análisis completo (con BD) |
| `/ml/predict_baz` | POST | Predicción con BAZ (legacy) |
| `/ml/summary` | POST | Resumen con LLM |
| `/ml/chat` | POST | Chat con LLM |

### Ejemplo de Uso

```bash
# Health check
curl http://localhost:8001/health

# Predicción directa
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

## 💬 LLM (Explicaciones)

Configura un endpoint OpenAI-compatible vía variables de entorno:

```bash
# .env
LLM_API_KEY=tu_clave
LLM_BASE_URL=https://tu_endpoint/v1
LLM_MODEL=tu_modelo
LLM_TEMPERATURE=0.7
```

## 🧭 Plan de Trabajo — Planificador de Menús
- Definir objetivos diarios por perfil y estado nutricional (kcal, proteína).
- Implementar filtro duro por alergias y restricciones.
- Diseñar ranking suave: ajuste a objetivos + preferencias + favoritas + estado.
- Generar plan semanal: 4 slots por día (desayuno, almuerzo, cena, snack).
- Explicar cada recomendación con razones breves.
- Integrar datos reales de BD (nutrientes por menú/ingrediente) en siguiente fase.
- Validar con nutricionistas y crear feedback loop.

## ☁️ Guía Colab — Planificador de Menús
1) Subir la carpeta `modelo/ml-recomendator` a Google Drive o como .zip.
2) En Colab, montar Drive:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   ```
3) Ir al directorio del proyecto:
   ```bash
   cd /content/drive/MyDrive/<ruta>/modelo/ml-recomendator
   ```
4) (Opcional) Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
5) Ejecutar el ejemplo del planificador:
   ```bash
   python examples/colab_meal_planner.py
   ```
6) Personalizar preferencias y alergias directamente en el script de ejemplo.

### API Rápida
```python
from src.recommender import MealPlanner
planner = MealPlanner({"kcal": 1800, "proteina_g": 50.0})
plan = planner.generar_plan_semanal(
    estado_nutricional="MODERADO",
    alergias=["maní"],
    preferencias={"vegetariano": 0.5, "alto_fibra": 0.3},
    favoritas=["fruta", "yogur"],
    dias=7,
)
print(plan.resumen())
```
