# Modelo de Clasificación Nutricional: Naive Bayes + Random Forest

## 🎯 Descripción

El modelo utiliza **dos algoritmos de Machine Learning** para clasificar el estado nutricional de niños según las 7 categorías de la OMS:

1. **Naive Bayes (Bayesian)**: Clasificación probabilística basada en el teorema de Bayes
2. **Random Forest**: Clasificación basada en múltiples árboles de decisión
3. **Ensemble**: Combinación de ambos modelos con votación ponderada

## 📊 Categorías de Clasificación

El modelo clasifica en **7 categorías nutricionales**:

1. **DESNUTRICION_SEVERA** (BAZ < -3.0)
2. **DESNUTRICION_MODERADA** (-3.0 ≤ BAZ < -2.0)
3. **RIESGO_DESNUTRICION** (-2.0 ≤ BAZ < -1.0)
4. **NORMAL** (-1.0 ≤ BAZ ≤ 1.0)
5. **RIESGO_SOBREPESO** (1.0 < BAZ ≤ 2.0)
6. **SOBREPESO** (2.0 < BAZ ≤ 3.0)
7. **OBESIDAD** (BAZ > 3.0)

## 🔍 Datos de Entrada

El modelo solo necesita **3 datos antropométricos**:

- **Edad** (en meses)
- **Peso** (en kilogramos)
- **Talla** (en centímetros)
- **Sexo** (M o F)

**NO necesita BAZ precalculado** - el modelo aprende los patrones de la OMS directamente.

## 🧠 Algoritmos Utilizados

### 1. Naive Bayes (Bayesian)

**Ventajas:**
- Rápido y eficiente
- Funciona bien con datos pequeños
- Proporciona probabilidades directas
- Basado en teorema de Bayes: P(clase|datos) = P(datos|clase) × P(clase) / P(datos)

**Uso en el modelo:**
- Clasificación probabilística inicial
- Bueno para capturar relaciones lineales entre features

### 2. Random Forest

**Ventajas:**
- Alta precisión
- Maneja relaciones no lineales
- Resistente al overfitting
- Proporciona importancia de features
- Funciona con múltiples árboles de decisión

**Uso en el modelo:**
- Clasificación robusta basada en 500 árboles
- Captura patrones complejos en los datos
- Balanceo de clases automático

### 3. Ensemble (Combinación)

**Estrategia:**
- Votación suave (soft voting) entre Naive Bayes y Random Forest
- Pesos: Naive Bayes (1), Random Forest (2)
- Combina las fortalezas de ambos modelos

**Ventajas:**
- Mayor precisión que modelos individuales
- Reduce varianza y sesgo
- Más robusto ante datos nuevos

## 📈 Features Utilizadas

El modelo utiliza **14 features** derivadas de los datos de entrada:

### Features Básicas:
1. `edad_meses` - Edad en meses
2. `sexo_num` - Sexo codificado (0=M, 1=F)
3. `peso_kg` - Peso en kilogramos
4. `talla_cm` - Talla en centímetros
5. `bmi` - Índice de Masa Corporal

### Features de Edad:
6. `edad_anos` - Edad en años
7. `es_bebe` - Si es bebé (0-2 años)
8. `es_preescolar` - Si es preescolar (2-5 años)
9. `es_escolar` - Si es escolar (5-10 años)
10. `es_adolescente` - Si es adolescente (10-19 años)

### Features de Ratios:
11. `peso_por_edad` - Peso / Edad
12. `talla_por_edad` - Talla / Edad

### Features de Interacción:
13. `bmi_x_edad` - BMI × Edad
14. `peso_x_talla` - Peso × Talla

## 🚀 Entrenamiento

### Comando:
```bash
./entrenar_modelo_directo.sh
```

O manualmente:
```bash
python src/pipeline/train_model_directo.py --data-source db
```

### Proceso:
1. Carga datos desde la base de datos
2. Calcula BAZ usando estándares OMS
3. Clasifica según las 7 categorías
4. Prepara features directas
5. Entrena 3 modelos: Naive Bayes, Random Forest, Ensemble
6. Selecciona el mejor modelo según accuracy de validación
7. Guarda modelo y scaler

### Salida:
- `models/directo/modelo_directo.pkl` - Modelo entrenado
- `models/directo/scaler_directo.pkl` - Scaler para normalización
- `models/directo/metricas_directo.json` - Métricas de evaluación
- `models/directo/feature_importance_directo.csv` - Importancia de features

## 📊 Métricas Esperadas

- **Accuracy**: > 85%
- **F1-Score**: > 0.83
- **Overfitting**: < 0.05

## 🔧 Uso del Modelo

### API REST:

```bash
# Clasificar
curl -X POST http://localhost:8001/clasificar \
  -H "Content-Type: application/json" \
  -d '{
    "edad_meses": 36,
    "sexo": "M",
    "peso_kg": 14.5,
    "talla_cm": 95.0
  }'
```

### Python:

```python
from src.models.direct_classifier import cargar_modelo_directo

# Cargar modelo
modelo = cargar_modelo_directo()

# Predecir
resultado = modelo.predecir(
    edad_meses=36,
    sexo='M',
    peso_kg=14.5,
    talla_cm=95.0
)

print(f"Clasificación: {resultado['clasificacion']}")
print(f"Confianza: {resultado['confianza']:.2%}")
```

## 🎯 Ventajas del Enfoque

1. **Simple**: Solo necesita edad, peso, talla
2. **Directo**: No requiere cálculos previos de BAZ
3. **Robusto**: Combina dos algoritmos complementarios
4. **Rápido**: Predicción en milisegundos
5. **Interpretable**: Proporciona probabilidades y explicaciones
6. **Preciso**: Alta accuracy en validación

## 📝 Notas Técnicas

- El modelo aprende los patrones de la OMS directamente de los datos
- Usa StandardScaler para normalizar features
- Balanceo de clases con `class_weight='balanced'`
- Validación estratificada para mantener distribución de clases
- Cross-validation para evaluar robustez

## 🔄 Actualización del Modelo

Para reentrenar con nuevos datos:

```bash
# 1. Asegurar que la BD tiene datos actualizados
# 2. Ejecutar entrenamiento
./entrenar_modelo_directo.sh

# 3. Reiniciar API
docker-compose restart modelo
```

## 📚 Referencias

- **Naive Bayes**: Clasificación probabilística bayesiana
- **Random Forest**: Breiman, L. (2001). Random Forests
- **OMS**: Estándares de crecimiento infantil WHO 2006/2007
