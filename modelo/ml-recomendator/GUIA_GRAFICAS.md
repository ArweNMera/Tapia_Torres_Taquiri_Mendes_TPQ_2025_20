# 📊 Guía de Gráficas del Modelo ML

## 🚀 Cómo Generar las Gráficas

### Opción 1: Script Bash (Recomendado)
```bash
cd modelo/ml-recomendator
./generar_graficas.sh
```

### Opción 2: Python Directo
```bash
cd modelo/ml-recomendator
python scripts/generar_graficas.py
```

Las gráficas se guardarán en: `modelo/ml-recomendator/reports/figures/`

---

## 📈 Las 8 Gráficas Generadas

### 🔥 **GRÁFICAS CRUCIALES** (Imprescindibles para presentación)

#### 1️⃣ **Feature Importance** ⭐⭐⭐⭐⭐
**Archivo:** `01_feature_importance.png`

**¿Qué muestra?**
- Las 10 características más importantes que el modelo usa para clasificar
- Muestra qué variables tienen más peso en las predicciones

**¿Por qué es crucial?**
- Demuestra que el modelo usa variables médicamente relevantes (BAZ, edad, BMI)
- Valida que el modelo no está usando ruido o variables irrelevantes
- Es la gráfica más importante para explicar cómo funciona el modelo

**Interpretación:**
- BAZ (Z-score) debería ser el feature más importante
- Edad y BMI también deberían tener alta importancia

---

#### 2️⃣ **Matriz de Confusión** ⭐⭐⭐⭐⭐
**Archivo:** `02_confusion_matrix.png`

**¿Qué muestra?**
- Comparación entre predicciones del modelo vs realidad
- Diagonal = predicciones correctas
- Fuera de diagonal = errores

**¿Por qué es crucial?**
- Muestra la precisión del modelo por cada categoría
- Identifica qué clases confunde el modelo
- Es la métrica visual más importante de rendimiento

**Interpretación:**
- Números altos en la diagonal = buen modelo
- Confusiones entre clases adyacentes (ej: NORMAL ↔ RIESGO_SOB) son aceptables
- Confusiones entre extremos (ej: OBESIDAD ↔ DESNUT_SEV) serían graves

---

#### 8️⃣ **Métricas por Clase** ⭐⭐⭐⭐⭐
**Archivo:** `08_metricas_comparacion.png`

**¿Qué muestra?**
- Precision, Recall y F1-Score para cada categoría
- Compara el rendimiento del modelo en cada clase

**¿Por qué es crucial?**
- Muestra si el modelo funciona bien en TODAS las categorías
- Identifica clases problemáticas
- Métricas > 0.85 son excelentes

**Interpretación:**
- Precision: De lo que predice como X, ¿cuánto es realmente X?
- Recall: De todo lo que es X, ¿cuánto detecta el modelo?
- F1-Score: Balance entre precision y recall

---

### 📊 **GRÁFICAS IMPORTANTES** (Útiles para análisis)

#### 3️⃣ **Distribución de Clases** ⭐⭐⭐⭐
**Archivo:** `03_distribucion_clases.png`

**¿Qué muestra?**
- Cuántos niños hay en cada categoría nutricional
- Balance del dataset

**¿Por qué es importante?**
- Muestra si el dataset está balanceado
- Identifica clases minoritarias
- Explica por qué algunas clases tienen mejor rendimiento

---

#### 6️⃣ **Distribución de BAZ** ⭐⭐⭐⭐
**Archivo:** `06_distribucion_baz.png`

**¿Qué muestra?**
- Cómo se distribuye el Z-score (BAZ) en cada categoría
- Histograma y boxplot

**¿Por qué es importante?**
- Valida que las categorías están bien separadas
- Muestra los rangos de Z-score por categoría
- Confirma que sigue estándares OMS

---

### 📉 **GRÁFICAS COMPLEMENTARIAS** (Análisis adicional)

#### 4️⃣ **Árbol de Decisión** ⭐⭐⭐
**Archivo:** `04_arbol_decision.png`

**¿Qué muestra?**
- Visualización de uno de los árboles del Random Forest
- Cómo el modelo toma decisiones

**¿Por qué es útil?**
- Muestra la lógica interna del modelo
- Ayuda a entender las reglas de clasificación
- Útil para debugging

---

#### 5️⃣ **Correlación entre Features** ⭐⭐⭐
**Archivo:** `05_correlacion_features.png`

**¿Qué muestra?**
- Relación entre variables del modelo
- Identifica redundancias

**¿Por qué es útil?**
- Detecta multicolinealidad
- Ayuda a optimizar features
- Valida independencia de variables

---

#### 7️⃣ **Edad vs BMI** ⭐⭐⭐
**Archivo:** `07_edad_vs_bmi.png`

**¿Qué muestra?**
- Scatter plot de edad vs BMI coloreado por clase
- Patrones de crecimiento

**¿Por qué es útil?**
- Muestra separación visual de clases
- Identifica patrones de edad
- Valida que el modelo captura tendencias reales

---

## 🎯 Resumen: Top 3 Gráficas Imprescindibles

Si solo puedes mostrar 3 gráficas, usa estas:

1. **Matriz de Confusión** (02) - Muestra precisión del modelo
2. **Feature Importance** (01) - Explica qué usa el modelo
3. **Métricas por Clase** (08) - Demuestra rendimiento balanceado

---

## 📋 Checklist de Validación

Después de generar las gráficas, verifica:

- [ ] Feature Importance: BAZ es el feature más importante
- [ ] Matriz de Confusión: Diagonal tiene valores altos
- [ ] Métricas: F1-Score > 0.85 en todas las clases
- [ ] Distribución: Dataset tiene suficientes ejemplos por clase
- [ ] BAZ: Rangos coinciden con estándares OMS
- [ ] Todas las 8 gráficas se generaron sin errores

---

## 🔧 Troubleshooting

### Error: "No such file or directory: datos_historicos.csv"
✅ **Solucionado:** El script ahora usa `datos_completos_oms_reales.csv`

### Error: "No module named 'src.models'"
```bash
cd modelo/ml-recomendator
export PYTHONPATH=$PYTHONPATH:$(pwd)
python scripts/generar_graficas.py
```

### Error: "rf_model.pkl not found"
Primero entrena el modelo:
```bash
cd modelo/ml-recomendator
python src/pipeline/train_model.py
```

---

## 📁 Estructura de Salida

```
modelo/ml-recomendator/reports/figures/
├── 01_feature_importance.png      ⭐⭐⭐⭐⭐
├── 02_confusion_matrix.png        ⭐⭐⭐⭐⭐
├── 03_distribucion_clases.png     ⭐⭐⭐⭐
├── 04_arbol_decision.png          ⭐⭐⭐
├── 05_correlacion_features.png    ⭐⭐⭐
├── 06_distribucion_baz.png        ⭐⭐⭐⭐
├── 07_edad_vs_bmi.png             ⭐⭐⭐
└── 08_metricas_comparacion.png    ⭐⭐⭐⭐⭐
```

---

## 💡 Tips para Presentación

1. **Orden recomendado:**
   - Empieza con Distribución de Clases (contexto)
   - Muestra Feature Importance (qué usa el modelo)
   - Presenta Matriz de Confusión (rendimiento)
   - Cierra con Métricas por Clase (validación)

2. **Puntos clave a destacar:**
   - Accuracy > 90%
   - Modelo usa variables médicamente relevantes
   - Funciona bien en todas las categorías
   - Sigue estándares OMS

3. **Preguntas frecuentes:**
   - ¿Por qué Random Forest? → Balance entre precisión e interpretabilidad
   - ¿Cómo validan el modelo? → Cross-validation + métricas por clase
   - ¿Qué pasa con clases desbalanceadas? → Usamos class_weight='balanced'
