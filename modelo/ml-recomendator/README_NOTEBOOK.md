# 📓 Notebook de Entrenamiento y Análisis del Modelo ML

## 🎯 Descripción

Este notebook de Jupyter/Google Colab permite entrenar y analizar el modelo de recomendación de menús nutricionales mediante peticiones HTTP a la API desplegada en Google Cloud Run.

**Archivo**: `ML_Training_Notebook.ipynb`

---

## ✨ Características

### 📊 **6 Gráficas Profesionales Generadas**:

1. **Importancia de Características (Top 10)** - Barras horizontales con las variables más influyentes
2. **Métricas de Precisión** - Accuracy exacto, ±1 y R² Score
3. **Métricas NDCG** - Evaluación del ranking (General, @5, @10)
4. **Métricas de Error** - RMSE, MAE, MSE con comparación train/val
5. **Distribución de Errores** - Pie chart con categorías de error
6. **Boxplot de Predicciones** - Análisis de rangos y distribución

### 🚀 **Funcionalidades**:

- ✅ Entrenamiento automático vía API (`/api/v1/models/train/quick`)
- ✅ Obtención de métricas del último modelo entrenado
- ✅ Tabla interactiva con todas las métricas
- ✅ Visualizaciones profesionales con cajas de información
- ✅ Resumen ejecutivo en HTML
- ✅ Interpretación automática de resultados

---

## 🔗 API Endpoints Utilizados

```
Base URL: https://nutricion-modelo-ml-343042748851.us-east1.run.app

POST /api/v1/models/train/quick     - Entrenar nuevo modelo
GET  /api/v1/models/train/status    - Obtener estado y métricas
```

---

## 📦 Requisitos

### Para Google Colab:
- ✅ **Ninguno** - Todo se instala automáticamente en la primera celda

### Para Jupyter Local:
```bash
pip install requests matplotlib seaborn pandas numpy jupyter
```

---

## 🚀 Cómo Usar en Google Colab

### Opción 1: Subir el archivo manualmente

1. Ve a [Google Colab](https://colab.research.google.com/)
2. Click en **"Archivo" → "Subir notebook"**
3. Selecciona el archivo `ML_Training_Notebook.ipynb`
4. ¡Listo! Ejecuta todas las celdas: **Runtime → Run all**

### Opción 2: Abrir desde Google Drive

1. Sube el notebook a tu Google Drive
2. Click derecho → **"Abrir con" → "Google Colaboratory"**
3. Ejecuta las celdas secuencialmente

---

## 🚀 Cómo Usar en Jupyter Local

```bash
# 1. Navegar al directorio
cd modelo/ml-recomendator

# 2. Instalar dependencias
pip install requests matplotlib seaborn pandas numpy jupyter

# 3. Iniciar Jupyter
jupyter notebook

# 4. Abrir el archivo ML_Training_Notebook.ipynb en el navegador
```

---

## 📊 Estructura del Notebook

### 📦 Sección 1: Instalación
- Instala automáticamente todas las dependencias necesarias

### 📚 Sección 2: Importación de Librerías
- Importa requests, matplotlib, seaborn, pandas, numpy

### ⚙️ Sección 3: Configuración
- Define las URLs de los endpoints de la API

### 🎯 Sección 4: Entrenamiento
- Ejecuta el entrenamiento del modelo vía POST request
- ⏳ **Tiempo estimado**: 2-5 minutos
- Muestra el progreso y resultado

### 📊 Sección 5: Obtención de Métricas
- Consulta el estado del modelo más reciente
- Obtiene todas las métricas disponibles

### 📋 Sección 6: Tabla de Métricas
- Presenta todas las métricas en formato tabla
- Con descripciones y valores formateados

### 📈 Sección 7: 6 Gráficas
Genera automáticamente:
1. Feature Importance
2. Accuracy Metrics
3. NDCG Metrics
4. Error Metrics
5. Error Distribution (Pie Chart)
6. Boxplot (Prediction Range)

### 📋 Sección 8: Resumen Final
- Resumen ejecutivo en HTML
- Interpretación automática de resultados
- Recomendaciones de producción

---

## 📊 Ejemplo de Métricas Generadas

```
═══════════════════════════════════════════════════════════
📊 MÉTRICAS DEL ÚLTIMO MODELO ENTRENADO
═══════════════════════════════════════════════════════════

🆔 Nombre: production_menu_recommender
📅 Fecha: 2025-11-01T00:19:08
💾 Tamaño: 0.0 MB

─────────────────────────────────────────────────────────
📈 MÉTRICAS DE PRECISIÓN
─────────────────────────────────────────────────────────
  ✓ Accuracy Exacto:        33.92%
  ✓ Accuracy ±1:            75.77%
  ✓ R² Score:               0.1744

─────────────────────────────────────────────────────────
🎯 MÉTRICAS DE RANKING (NDCG)
─────────────────────────────────────────────────────────
  ★ NDCG General:           89.52%
  ★ NDCG@5:                 89.04%
  ★ NDCG@10:                84.98%

─────────────────────────────────────────────────────────
📦 DATOS DE ENTRENAMIENTO
─────────────────────────────────────────────────────────
  • Muestras entrenamiento: 1,814
  • Muestras validación:    454
```

---

## 🎨 Características de las Gráficas

### 📊 Gráfica 1: Feature Importance
- **Tipo**: Barras horizontales
- **Elementos**: Top 10 características
- **Información**: Valores numéricos, metadata del modelo
- **Colores**: Azul cielo con bordes negros

### 📊 Gráfica 2: Accuracy Metrics
- **Tipo**: Barras verticales
- **Elementos**: Accuracy exacto, ±1, R² Score
- **Información**: Líneas de referencia (50%, 75%, 90%)
- **Colores**: Rojo, turquesa, azul

### 🎯 Gráfica 3: NDCG Metrics
- **Tipo**: Barras verticales
- **Elementos**: NDCG general, @5, @10
- **Información**: Línea objetivo (88%), estado del modelo
- **Colores**: Naranja, morado, lila

### 📉 Gráfica 4: Error Metrics
- **Tipo**: Barras verticales
- **Elementos**: RMSE val/train, MAE, MSE
- **Información**: Descripción de métricas
- **Colores**: Rojo, azul, naranja, morado

### 🥧 Gráfica 5: Error Distribution
- **Tipo**: Pie chart
- **Elementos**: Predicciones exactas, ±1, ≥2
- **Información**: Porcentajes, calidad total
- **Colores**: Verde, naranja, rojo

### 📦 Gráfica 6: Boxplot
- **Tipo**: Boxplot doble
- **Elementos**: Predicciones del modelo, comparación con valores reales
- **Información**: Estadísticas (min, max, media), muestras
- **Colores**: Azul claro, coral

---

## 💡 Interpretación de Resultados

### ✅ **Modelo Excelente** (Producción)
- NDCG ≥ 88%
- Accuracy ±1 ≥ 75%
- RMSE ≤ 1.2

### ⚠️ **Modelo Bueno** (Optimizable)
- NDCG: 85-88%
- Accuracy ±1: 65-75%
- RMSE: 1.2-1.5

### ❌ **Modelo Requiere Mejora**
- NDCG < 85%
- Accuracy ±1 < 65%
- RMSE > 1.5

---

## 🔧 Personalización

### Cambiar la URL de la API:

Edita la celda de configuración:

```python
API_BASE_URL = "https://tu-nueva-url.run.app"
```

### Ajustar timeouts:

En la celda de entrenamiento:

```python
response = requests.post(
    TRAIN_ENDPOINT,
    timeout=600  # Cambiar este valor (segundos)
)
```

### Modificar colores de gráficas:

Cada gráfica tiene su paleta definida en la variable `colors`:

```python
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']  # Personalizar aquí
```

---

## 🐛 Solución de Problemas

### Error: "Timeout"
**Causa**: El entrenamiento toma más de 10 minutos  
**Solución**: Aumentar el timeout en la petición POST

### Error: "No hay modelos disponibles"
**Causa**: No se ha entrenado ningún modelo aún  
**Solución**: Ejecutar primero la celda de entrenamiento

### Error: "Connection refused"
**Causa**: La API no está disponible o la URL es incorrecta  
**Solución**: Verificar que la URL de la API sea correcta

### Las gráficas no se muestran
**Causa**: Matplotlib no está configurado correctamente  
**Solución**: Ejecutar `%matplotlib inline` al inicio del notebook

---

## 📝 Notas Importantes

⚠️ **Tiempo de Ejecución**:
- Entrenamiento: 2-5 minutos
- Obtención de métricas: < 5 segundos
- Generación de gráficas: < 10 segundos
- **Total estimado**: 3-6 minutos

⚠️ **Uso de Recursos**:
- El notebook es ligero y no requiere GPU
- Funciona perfectamente en Google Colab gratuito
- Las peticiones HTTP son las únicas operaciones de red

⚠️ **Compatibilidad**:
- ✅ Google Colab (recomendado)
- ✅ Jupyter Notebook
- ✅ JupyterLab
- ✅ VS Code con extensión de Jupyter

---

## 📚 Referencias

- **API Documentación**: https://nutricion-modelo-ml-343042748851.us-east1.run.app/docs
- **NDCG Metric**: https://en.wikipedia.org/wiki/Discounted_cumulative_gain
- **Matplotlib**: https://matplotlib.org/
- **Seaborn**: https://seaborn.pydata.org/

---

## 🎉 Resultado Final

Al ejecutar todas las celdas obtendrás:

✅ **1 Tabla de Métricas** - Completa y formateada  
✅ **6 Gráficas Profesionales** - Listas para presentar  
✅ **1 Resumen Ejecutivo** - En formato HTML  
✅ **Interpretación Automática** - Con recomendaciones  

**Total**: 8 visualizaciones + análisis completo del modelo ML

---

## 👨‍💻 Autor

**Sistema de Recomendación de Menús Nutricionales**  
Modelo ML desplegado en Google Cloud Run (US-EAST1)  
2025

---

## 📄 Licencia

Este notebook es parte del sistema de nutrición ML y está destinado para uso educativo y de desarrollo.
