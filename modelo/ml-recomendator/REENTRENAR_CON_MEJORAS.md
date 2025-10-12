# Reentrenar Modelo con Mejoras

## 🔍 Problemas Detectados

### 1. Warning de Feature Names
**Problema**: El scaler esperaba nombres de features pero recibía numpy array
**Solución**: Cambiar `_preparar_features()` para retornar DataFrame en vez de numpy array

### 2. Sesgo hacia SOBREPESO
**Problema**: Con solo 201 datos, el modelo clasificaba todo como SOBREPESO
**Causa**:
- Pocos datos de entrenamiento (201 registros)
- Modelo muy complejo (500 árboles, profundidad 20)
- Overfitting hacia la clase más común

**Solución Aplicada**:
- Reducir complejidad del Random Forest:
  - `n_estimators`: 500 → 200
  - `max_depth`: 20 → 10
  - `min_samples_split`: 10 → 20
  - `min_samples_leaf`: 4 → 10
- Cambiar pesos del Ensemble:
  - Naive Bayes: 1 → 2 (más peso al modelo simple)
  - Random Forest: 2 → 1

## 🚀 Pasos para Reentrenar

### 1. Reentrenar el modelo
```bash
cd modelo/ml-recomendator
./entrenar_modelo_directo.sh
```

### 2. Probar el modelo
```bash
python3 scripts/test_bayesian_rf.py
```

### 3. Verificar resultados
Deberías ver:
- ✅ Sin warnings de feature names
- ✅ Clasificaciones más variadas (no todo SOBREPESO)
- ✅ Confianzas más razonables

## 📊 Distribución de Datos Actual

```
DESNUT_SEV: 26 (12.9%)
DESNUT_MOD: 26 (12.9%)
RIESGO_DESN: 29 (14.4%)
NORMAL: 71 (35.3%)      ← Clase mayoritaria
RIESGO_SOB: 20 (10.0%)
SOBREPESO: 14 (7.0%)
OBESIDAD: 15 (7.5%)
```

## 💡 Recomendaciones para Mejorar

### Corto Plazo
1. **Reentrenar con los cambios aplicados**
2. **Probar con casos reales**
3. **Monitorear predicciones**

### Mediano Plazo
1. **Agregar más datos** (objetivo: 500+ registros)
2. **Balancear clases** con técnicas de oversampling/undersampling
3. **Validar con nutricionistas** las clasificaciones

### Largo Plazo
1. **Reentrenar periódicamente** con nuevos datos
2. **Ajustar hiperparámetros** según performance
3. **Considerar otros algoritmos** si es necesario

## 🔧 Cambios Técnicos Aplicados

### En `src/models/direct_classifier.py`:
```python
# ANTES: Retornaba numpy array
def _preparar_features(...) -> np.ndarray:
    return np.array(features).reshape(1, -1)

# DESPUÉS: Retorna DataFrame con nombres
def _preparar_features(...) -> pd.DataFrame:
    return pd.DataFrame([features], columns=feature_names)
```

### En `src/pipeline/train_model_directo.py`:
```python
# ANTES: Modelo muy complejo
RandomForestClassifier(
    n_estimators=500,
    max_depth=20,
    min_samples_split=10,
    min_samples_leaf=4,
    ...
)

# DESPUÉS: Modelo más simple
RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_split=20,
    min_samples_leaf=10,
    ...
)
```

## ✅ Verificación

Después de reentrenar, verifica:

1. **No hay warnings**:
```bash
python3 scripts/test_bayesian_rf.py 2>&1 | grep -i warning
# Debería estar vacío
```

2. **Clasificaciones variadas**:
```bash
python3 scripts/test_bayesian_rf.py | grep "Clasificación:"
# Deberías ver diferentes categorías, no solo SOBREPESO
```

3. **Accuracy razonable**:
```bash
cat models/directo/metricas_directo.json | grep accuracy_val
# Debería ser > 0.70 (70%)
```

## 📝 Notas

- Con 201 datos, es normal tener accuracy entre 70-85%
- El modelo mejorará significativamente con más datos
- El Ensemble (NB + RF) suele dar mejores resultados que modelos individuales
- Naive Bayes es más robusto con pocos datos que Random Forest
