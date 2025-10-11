# Solución al Sesgo hacia SOBREPESO

## 🔍 Problema Detectado

El modelo clasifica **casi todo como SOBREPESO**, incluso casos claramente normales o con desnutrición.

### Ejemplos del Problema:
- Niño 3 años (36m, 14.5kg, 95cm, BMI=16.07) → **SOBREPESO** ❌ (debería ser NORMAL)
- Bebé 1 año (12m, 7kg, 70cm, BMI=14.29) → **SOBREPESO** ❌ (debería ser DESNUTRICION)
- Adolescente 15 años (180m, 55kg, 160cm, BMI=21.48) → **SOBREPESO** ❌ (debería ser NORMAL)

## 🎯 Causa Raíz

### 1. Desbalance de Clases
```
DESNUTRICION_SEVERA:     26 (12.9%)
DESNUTRICION_MODERADA:   26 (12.9%)
RIESGO_DESNUTRICION:     29 (14.4%)
NORMAL:                  71 (35.3%)  ← Clase mayoritaria
RIESGO_SOBREPESO:        20 (10.0%)
SOBREPESO:               14 (7.0%)   ← Clase minoritaria
OBESIDAD:                15 (7.5%)
```

Con solo 201 datos y desbalance, el modelo aprende a "apostar" a las clases más comunes.

### 2. Pocos Datos
201 registros es **muy poco** para 7 clases. Idealmente necesitamos:
- Mínimo: 500+ registros
- Recomendado: 1000+ registros
- Óptimo: 5000+ registros

### 3. Modelo Muy Complejo
Con pocos datos, modelos complejos tienden a overfitting.

## ✅ Solución Implementada: SMOTE

### ¿Qué es SMOTE?
**SMOTE** (Synthetic Minority Over-sampling Technique) es una técnica que:
1. Identifica clases minoritarias
2. Genera ejemplos sintéticos interpolando entre ejemplos existentes
3. Balancea todas las clases al mismo número de muestras

### Cómo Funciona:
```python
# ANTES (desbalanceado)
NORMAL: 71 muestras
SOBREPESO: 14 muestras

# DESPUÉS de SMOTE (balanceado)
NORMAL: 71 muestras
SOBREPESO: 71 muestras (57 sintéticos + 14 reales)
```

### Ventajas:
- ✅ Balancea clases sin perder datos reales
- ✅ Genera ejemplos realistas (no aleatorios)
- ✅ Mejora significativamente el aprendizaje de clases minoritarias
- ✅ Reduce sesgo hacia clases mayoritarias

## 🚀 Implementación

### Cambios en el Código:

#### 1. Agregar Dependencia
```bash
pip install imbalanced-learn>=0.11.0
```

#### 2. Modificar `train_model_directo.py`
```python
from imblearn.over_sampling import SMOTE

# Aplicar SMOTE después de escalar
smote = SMOTE(random_state=42, k_neighbors=3)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)

# Entrenar con datos balanceados
modelo.fit(X_train_balanced, y_train_balanced)
```

### Parámetros de SMOTE:
- `k_neighbors=3`: Usa 3 vecinos más cercanos para generar sintéticos
  - Con pocos datos, usar k pequeño (3-5)
  - Con muchos datos, usar k mayor (5-10)
- `random_state=42`: Para reproducibilidad

## 📋 Pasos para Aplicar la Solución

### 1. Instalar Dependencia
```bash
cd modelo/ml-recomendator
source venv/bin/activate
pip install imbalanced-learn>=0.11.0
```

### 2. Reentrenar con SMOTE
```bash
./REENTRENAR_CON_SMOTE.sh
```

O manualmente:
```bash
python3 src/pipeline/train_model_directo.py \
    --data-source db \
    --output models/directo \
    --test-size 0.2
```

### 3. Probar el Modelo
```bash
python3 scripts/test_bayesian_rf.py
```

### 4. Verificar Resultados
Deberías ver:
- ✅ Clasificaciones más variadas (no solo SOBREPESO)
- ✅ Casos normales clasificados como NORMAL
- ✅ Casos de desnutrición detectados correctamente
- ✅ Confianzas más razonables

## 📊 Resultados Esperados

### Antes de SMOTE:
```
Caso 1 (normal):        SOBREPESO (70%)  ❌
Caso 2 (desnutrición):  SOBREPESO (71%)  ❌
Caso 3 (sobrepeso):     SOBREPESO (73%)  ✅ (correcto por suerte)
Caso 4 (normal):        SOBREPESO (79%)  ❌
```

### Después de SMOTE:
```
Caso 1 (normal):        NORMAL (65%)           ✅
Caso 2 (desnutrición):  DESNUTRICION_MOD (58%) ✅
Caso 3 (sobrepeso):     SOBREPESO (72%)        ✅
Caso 4 (normal):        NORMAL (68%)           ✅
```

## 🔧 Ajustes Adicionales

### Si SMOTE No Es Suficiente:

#### 1. Ajustar k_neighbors
```python
# Para muy pocos datos
smote = SMOTE(k_neighbors=2)

# Para más datos
smote = SMOTE(k_neighbors=5)
```

#### 2. Usar SMOTE + Tomek Links
```python
from imblearn.combine import SMOTETomek

smote_tomek = SMOTETomek(random_state=42)
X_balanced, y_balanced = smote_tomek.fit_resample(X_train, y_train)
```

#### 3. Usar ADASYN (Adaptive Synthetic)
```python
from imblearn.over_sampling import ADASYN

adasyn = ADASYN(random_state=42)
X_balanced, y_balanced = adasyn.fit_resample(X_train, y_train)
```

## 💡 Recomendaciones a Largo Plazo

### Corto Plazo (Ahora):
1. ✅ Aplicar SMOTE
2. ✅ Reentrenar modelo
3. ✅ Validar con casos reales

### Mediano Plazo (1-3 meses):
1. **Agregar más datos reales** (objetivo: 500+)
2. **Validar con nutricionistas** las clasificaciones
3. **Monitorear predicciones** en producción

### Largo Plazo (3-6 meses):
1. **Recolectar 1000+ datos**
2. **Reentrenar sin SMOTE** (con suficientes datos reales)
3. **Implementar reentrenamiento automático**

## ⚠️ Limitaciones de SMOTE

### Ventajas:
- ✅ Mejora significativamente con pocos datos
- ✅ Reduce sesgo hacia clases mayoritarias
- ✅ Genera ejemplos realistas

### Desventajas:
- ⚠️ Puede generar ejemplos "imposibles" si k es muy grande
- ⚠️ No reemplaza datos reales
- ⚠️ Puede causar overfitting si se usa mal

### Cuándo NO Usar SMOTE:
- ❌ Si tienes suficientes datos balanceados (1000+ por clase)
- ❌ Si las clases minoritarias son outliers reales
- ❌ Si el desbalance es intencional (ej: detección de fraude)

## 📚 Referencias

- **SMOTE Paper**: Chawla et al. (2002) "SMOTE: Synthetic Minority Over-sampling Technique"
- **imbalanced-learn**: https://imbalanced-learn.org/
- **Documentación SMOTE**: https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html

## ✅ Checklist

- [ ] Instalar imbalanced-learn
- [ ] Reentrenar con SMOTE
- [ ] Probar con casos de ejemplo
- [ ] Validar con casos reales
- [ ] Monitorear en producción
- [ ] Planificar recolección de más datos
