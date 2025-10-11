# Modelo de Clasificación Nutricional DIRECTO

## 🎯 Concepto

Este modelo aprende **DIRECTAMENTE** de los datos antropométricos básicos:
- Edad (meses)
- Sexo (M/F)
- Peso (kg)
- Talla (cm)

**NO necesita calcular BAZ** (BMI-for-age Z-score) previamente. El modelo aprende los patrones de clasificación de la OMS por sí mismo.

## 🆚 Diferencia con el Modelo Anterior

### Modelo Anterior (con BAZ)
```
Datos → Calcular BAZ → Clasificar según BAZ → Resultado
```
- Requiere tablas LMS de la OMS
- Calcula BAZ usando fórmulas complejas
- Clasifica según rangos de BAZ predefinidos
- **Problema**: Si BAZ está mal calculado, todo falla

### Modelo Directo (sin BAZ)
```
Datos → Modelo ML → Resultado
```
- Solo necesita edad, sexo, peso, talla
- El modelo aprende los patrones de la OMS
- Clasifica directamente en 7 categorías
- **Ventaja**: Más robusto, aprende de los datos reales

## 📊 Cómo Funciona

### 1. Features que Usa el Modelo

El modelo crea features inteligentes a partir de los datos básicos:

**Features básicas:**
- `edad_meses`: Edad en meses
- `sexo_num`: 0=Masculino, 1=Femenino
- `peso_kg`: Peso en kilogramos
- `talla_cm`: Talla en centímetros
- `bmi`: Índice de masa corporal (peso/altura²)

**Features de contexto de edad:**
- `edad_anos`: Edad en años
- `es_bebe`: 1 si < 2 años, 0 si no
- `es_preescolar`: 1 si 2-5 años, 0 si no
- `es_escolar`: 1 si 5-10 años, 0 si no
- `es_adolescente`: 1 si ≥ 10 años, 0 si no

**Features de ratios:**
- `peso_por_edad`: peso_kg / edad_meses
- `talla_por_edad`: talla_cm / edad_meses

**Features de interacción:**
- `bmi_x_edad`: BMI × edad_meses
- `peso_x_talla`: peso_kg × talla_cm

### 2. Proceso de Entrenamiento

```python
# 1. Cargar datos desde BD
datos = cargar_desde_mysql()
# Obtiene: edad, sexo, peso, talla, clasificación_oms

# 2. Preparar features
datos_preparados = preparar_features_directas(datos)
# Crea las 14 features mencionadas arriba

# 3. Entrenar modelos
# Prueba RandomForest y GradientBoosting
# Selecciona el mejor según accuracy de validación

# 4. Guardar modelo y scaler
# modelo_directo.pkl
# scaler_directo.pkl
```

### 3. Proceso de Predicción

```python
# 1. Recibir datos básicos
edad_meses = 84  # 7 años
sexo = 'F'
peso_kg = 30.0
talla_cm = 120.0

# 2. Preparar features automáticamente
features = modelo._preparar_features(edad_meses, sexo, peso_kg, talla_cm)

# 3. Escalar features
features_scaled = scaler.transform(features)

# 4. Predecir
resultado = modelo.predict(features_scaled)
# → "NORMAL" con 85% de confianza
```

## 🚀 Uso

### Entrenar el Modelo

```bash
# Desde la base de datos
python src/pipeline/train_model_directo.py --data-source db

# Desde un CSV
python src/pipeline/train_model_directo.py \
  --data-source csv \
  --csv-path datos/evaluaciones.csv
```

### Probar el Modelo

```bash
python scripts/test_modelo_directo.py
```

### Usar en Código Python

```python
from src.models.direct_classifier import cargar_modelo_directo

# Cargar modelo
modelo = cargar_modelo_directo()

# Predecir para un niño
resultado = modelo.predecir(
    edad_meses=84,
    sexo='F',
    peso_kg=30.0,
    talla_cm=120.0
)

print(resultado['clasificacion'])  # → "NORMAL"
print(resultado['confianza'])      # → 0.85
print(resultado['probabilidades']) # → Dict con todas las probabilidades
```

### Explicar una Predicción

```python
explicacion = modelo.explicar_prediccion(
    edad_meses=84,
    sexo='F',
    peso_kg=30.0,
    talla_cm=120.0
)

print(explicacion['contexto'])
# → "Niño/a de 7.0 años (escolar) con BMI de 20.83. Clasificación: NORMAL"

print(explicacion['probabilidades_top3'])
# → Top 3 categorías más probables con sus probabilidades
```

### Predicción en Batch

```python
import pandas as pd

# DataFrame con múltiples niños
df = pd.DataFrame({
    'edad_meses': [12, 60, 96],
    'sexo': ['M', 'F', 'M'],
    'peso_kg': [10.0, 20.0, 30.0],
    'talla_cm': [75.0, 110.0, 135.0]
})

# Predecir para todos
resultados = modelo.predecir_batch(df)

print(resultados[['edad_meses', 'clasificacion_pred', 'confianza_pred']])
```

## 📈 Ventajas

1. **Simplicidad**: Solo necesita 4 datos básicos
2. **Robustez**: No depende de cálculos intermedios
3. **Aprendizaje**: Aprende patrones complejos de los datos
4. **Flexibilidad**: Puede mejorar con más datos
5. **Velocidad**: Predicción instantánea

## 🎓 Por Qué Funciona

El modelo aprende a reconocer patrones como:

- "Un niño de 12 meses con 10kg y 75cm es NORMAL"
- "Un niño de 60 meses con 25kg y 110cm tiene SOBREPESO"
- "Una niña de 96 meses con 26kg y 128cm es NORMAL"

Estos patrones son los mismos que usa la OMS, pero el modelo los aprende de los datos en lugar de usar fórmulas predefinidas.

## 🔄 Integración con el Sistema

### En el Backend (FastAPI)

```python
# En app/api/v1/endpoints/ml.py

from src.models.direct_classifier import cargar_modelo_directo

# Cargar modelo al iniciar
modelo_directo = cargar_modelo_directo()

@router.post("/clasificar-directo")
async def clasificar_directo(
    edad_meses: int,
    sexo: str,
    peso_kg: float,
    talla_cm: float
):
    resultado = modelo_directo.predecir(
        edad_meses=edad_meses,
        sexo=sexo,
        peso_kg=peso_kg,
        talla_cm=talla_cm
    )
    
    return {
        "clasificacion": resultado['clasificacion'],
        "confianza": resultado['confianza'],
        "probabilidades": resultado['probabilidades']
    }
```

### En el Frontend (React)

```typescript
// Llamar al endpoint
const clasificar = async (datos: {
  edad_meses: number;
  sexo: string;
  peso_kg: number;
  talla_cm: number;
}) => {
  const response = await api.post('/ml/clasificar-directo', datos);
  return response.data;
};

// Usar
const resultado = await clasificar({
  edad_meses: 84,
  sexo: 'F',
  peso_kg: 30.0,
  talla_cm: 120.0
});

console.log(resultado.clasificacion); // "NORMAL"
console.log(resultado.confianza);     // 0.85
```

## 📊 Métricas Esperadas

Con datos balanceados y suficientes:

- **Accuracy**: 85-92%
- **F1-Score**: 0.83-0.90
- **Confianza promedio**: 75-85%

## 🔧 Mejora Continua

El modelo puede mejorar con:

1. **Más datos**: Más evaluaciones nutricionales
2. **Datos balanceados**: Igual cantidad de cada categoría
3. **Features adicionales**: Alergias, adherencia, etc.
4. **Ajuste de hiperparámetros**: Optimización del modelo

## 📝 Archivos Generados

Después del entrenamiento:

```
models/directo/
├── modelo_directo.pkl              # Modelo entrenado
├── scaler_directo.pkl              # Scaler para normalización
├── metricas_directo.json           # Métricas de evaluación
└── feature_importance_directo.csv  # Importancia de features
```

## 🎯 Próximos Pasos

1. Entrenar el modelo con datos reales
2. Evaluar accuracy en validación
3. Integrar en el backend
4. Probar en producción con casos reales
5. Monitorear y mejorar continuamente
