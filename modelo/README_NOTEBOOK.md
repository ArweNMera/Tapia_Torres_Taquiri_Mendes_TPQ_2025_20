# 📓 Notebook de Entrenamiento y Análisis del Modelo ML

## 🎯 Descripción

Este notebook permite entrenar y analizar el modelo ML de recomendación nutricional mediante peticiones API al servidor desplegado en Google Cloud Run.

**Archivo**: `Entrenamiento_y_Metricas_Modelo_ML.ipynb`

## 🚀 Cómo Usar en Google Colab

### Paso 1: Subir el Notebook a Colab

1. Ve a [Google Colab](https://colab.research.google.com/)
2. Click en **File** → **Upload notebook**
3. Arrastra el archivo `Entrenamiento_y_Metricas_Modelo_ML.ipynb`

### Paso 2: Ejecutar el Notebook

#### Opción A: Ejecutar Todo de Una Vez
- Click en **Runtime** → **Run all** (Ctrl+F9)
- Espera 2-5 minutos para el entrenamiento

#### Opción B: Ejecutar Paso a Paso
1. **Celda 1**: Instalar dependencias (30 segundos)
2. **Celda 2**: Configuración e imports
3. **Celda 3**: Entrenar modelo (2-5 minutos) ⏳
4. **Celda 4**: Obtener métricas del último modelo
5. **Celdas 5-10**: Generar 6 gráficas
6. **Celda 11**: Resumen ejecutivo
7. **Celda 12**: Comparación con modelos anteriores

## 📊 Gráficas Generadas

El notebook genera **6 gráficas clave**:

### 1. 🎯 Accuracy del Modelo
- **Accuracy Exacto**: % de predicciones 100% correctas
- **Accuracy ±1**: % de predicciones con error máximo de 1 punto
- **Caja informativa**: Resume los porcentajes

### 2. 📉 Métricas de Error
- **RMSE Validación**: Error cuadrático medio en validación
- **RMSE Entrenamiento**: Error en datos de entrenamiento
- **MAE**: Error absoluto medio
- **MSE**: Error cuadrático medio
- **Caja informativa**: Explica qué significan

### 3. 🎯 NDCG - Calidad del Ranking
- **NDCG General**: Calidad global del ranking
- **NDCG@5**: Calidad de las top 5 recomendaciones
- **NDCG@10**: Calidad de las top 10 recomendaciones
- **Caja informativa**: Promedio y explicación

### 4. 📊 Distribución de Errores
- **Pie Chart** con 3 segmentos:
  - Predicciones exactas
  - Error ±1
  - Error ≥2
- **Leyenda**: Porcentajes detallados

### 5. 📦 Dataset: Entrenamiento vs Validación
- **Muestras de entrenamiento**: Cantidad de datos para entrenar
- **Muestras de validación**: Cantidad de datos para validar
- **Caja informativa**: Total y porcentaje de validación

### 6. 🎲 Rango de Predicciones
- **Mínimo**: Menor predicción del modelo
- **Media**: Predicción promedio
- **Máximo**: Mayor predicción del modelo
- **Caja informativa**: Rango total y escala

## 📋 Métricas Clave Explicadas

### Accuracy
- **Exacto**: Predicciones que aciertan 100%
- **±1**: Predicciones con error de máximo 1 punto
- **Meta**: >30% exacto, >70% ±1

### NDCG (Normalized Discounted Cumulative Gain)
- Mide qué tan bien **ordena** las recomendaciones
- Rango: 0-100%
- **Meta**: >85% (excelente), >90% (excepcional)

### RMSE (Root Mean Square Error)
- Error promedio de las predicciones
- **Menor es mejor**
- Rango típico: 1.0-1.5

### R² Score
- Qué % de la varianza explica el modelo
- Rango: 0-1 (1 es perfecto)
- **Meta**: >0.15

## 🎨 Características Visuales

### Colores
- 🟢 **Verde**: Métricas positivas (accuracy, NDCG alto)
- 🔵 **Azul**: Datos neutrales (entrenamiento)
- 🟡 **Amarillo**: Advertencias (errores moderados)
- 🔴 **Rojo**: Errores o métricas bajas

### Cajas Informativas
Cada gráfica incluye una **caja con información clave**:
- Fondo semi-transparente
- Texto explicativo
- Valores destacados

### Formato
- **Títulos**: Grandes, en negrita con emojis
- **Valores**: Mostrados sobre cada barra
- **Grid**: Líneas punteadas para facilitar lectura
- **Bordes**: Negros y gruesos para destacar

## 📈 Resumen Ejecutivo

Al final del notebook se genera un **resumen ejecutivo** con:

### Tabla de Métricas
| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| Accuracy Exacto | XX.XX% | 🎯 Predicciones perfectas |
| NDCG General | XX.XX% | ⭐ Calidad del ranking |
| ... | ... | ... |

### Análisis Automático
El notebook evalúa automáticamente:
- ✅ **EXCELENTE**: NDCG ≥90%
- ✅ **MUY BUENO**: NDCG ≥85%
- ⚠️ **BUENO**: NDCG ≥80%
- ⚠️ **MEJORABLE**: NDCG <80%

### Recomendación Final
- 📌 **Listo para producción** (si NDCG ≥85%)
- ⚠️ **Reentrenar** (si NDCG <85%)

## 🔄 Comparación con Modelos Anteriores

El notebook BONUS compara:
- Todos los modelos entrenados
- Métricas clave de cada uno
- Identifica el **mejor modelo** por NDCG

## 🛠️ Requisitos

### Librerías (se instalan automáticamente)
```python
requests        # Peticiones HTTP
matplotlib      # Gráficas
seaborn         # Estilos visuales
pandas          # Tablas
numpy           # Cálculos
plotly          # Gráficas interactivas (opcional)
```

### Conexión
- ✅ Internet (para peticiones API)
- ✅ Servidor ML en Cloud Run (US-EAST1)

## 📡 Endpoints Usados

### 1. Entrenar Modelo
```
POST https://nutricion-modelo-ml-343042748851.us-east1.run.app/api/v1/models/train/quick
```
- **Tiempo**: 2-5 minutos
- **Retorna**: Modelo entrenado + métricas

### 2. Obtener Estado
```
GET https://nutricion-modelo-ml-343042748851.us-east1.run.app/api/v1/models/train/status
```
- **Tiempo**: <5 segundos
- **Retorna**: Lista de todos los modelos + métricas

## ⚠️ Notas Importantes

### Tiempo de Ejecución
- **Total**: ~3-6 minutos
- **Entrenamiento**: 2-5 minutos (varía según carga del servidor)
- **Gráficas**: <30 segundos

### Si el Entrenamiento Falla
1. Ejecutar solo la celda de métricas (sin entrenar)
2. Analizar los modelos existentes
3. Reintentar entrenamiento más tarde

### Límites
- **Timeout**: 10 minutos (configurable)
- **Min-instances**: 1 (sin cold start)
- **Modelos máximos**: Ilimitados (se sobrescriben)

## 🎯 Casos de Uso

### 1. Entrenamiento Periódico
- Ejecutar cada vez que se agregan datos nuevos
- Comparar métricas con modelo anterior
- Decidir si actualizar en producción

### 2. Análisis de Rendimiento
- Solo ejecutar celdas de métricas y gráficas
- Sin entrenar nuevo modelo
- Evaluar modelo actual

### 3. Experimentación
- Entrenar múltiples veces
- Comparar resultados
- Seleccionar mejor modelo

## 📚 Recursos Adicionales

### Documentación
- [Métricas de ML](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [NDCG Explicado](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)
- [Matplotlib Docs](https://matplotlib.org/)

### Archivos Relacionados
- `src/api/endpoints/training.py` - Código del endpoint
- `src/application/services/model_training_service.py` - Lógica de entrenamiento
- `ARQUITECTURA_FINAL_VERIFICADA.md` - Arquitectura del modelo

## 🎉 Resultado Final

Al ejecutar todo el notebook obtendrás:

1. ✅ **Modelo entrenado** (si ejecutaste entrenamiento)
2. 📊 **6 gráficas profesionales** con cajas informativas
3. 📋 **Tabla de métricas** detallada
4. 💡 **Análisis automático** del rendimiento
5. 🏆 **Comparación** con modelos anteriores
6. 📌 **Recomendación** sobre uso en producción

---

## 🚀 ¡Comienza Ahora!

1. Abre el notebook en Google Colab
2. Ejecuta todas las celdas (Runtime → Run all)
3. Espera 3-6 minutos
4. Disfruta de las visualizaciones 📊

**¡Éxito con tu modelo ML!** 🎉
