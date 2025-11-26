# Endpoints para Entrenamiento desde Colab

Base URL: `http://tu-servidor:8001`

## Flujo de Entrenamiento

### 1. Verificar Estado
```python
import requests
BASE_URL = "http://localhost:8001"

# Ver estado del sistema
response = requests.get(f"{BASE_URL}/api/v1/nutritional/status")
print(response.json())
```

### 2. Extraer CSV desde BD
```python
# Extrae datos de la BD y genera CSV
response = requests.post(f"{BASE_URL}/api/v1/nutritional/extract_csv", json={
    "min_measurements": 2,
    "lookback_months": 24,
    "include_synthetic": True,
    "target_size": 180
})
print(response.json())
# Retorna: records_count, class_distribution, csv_path
```

### 3. Entrenar Modelo
```python
# Entrena el modelo con el CSV generado
response = requests.post(f"{BASE_URL}/api/v1/nutritional/train", json={
    "validation_split": 0.3,
    "num_boost_round": 500,
    "early_stopping": 50
})
print(response.json())
# Retorna: accuracy, f1_macro, f1_weighted, model_path
```

### 4. Obtener Métricas
```python
# Obtiene métricas detalladas del modelo
response = requests.get(f"{BASE_URL}/api/v1/nutritional/metrics")
metrics = response.json()
print(f"Accuracy: {metrics['accuracy']}")
print(f"F1 Macro: {metrics['f1_macro']}")
print(f"Feature Importance: {metrics['feature_importance']}")
```

### 5. Generar Gráficas
```python
from IPython.display import Image, display
import base64

# Genera las 5 gráficas importantes
response = requests.post(f"{BASE_URL}/api/v1/nutritional/generate_plots", json={
    "plots_to_generate": [
        "feature_importance",
        "class_distribution",
        "confusion_matrix",
        "bmi_by_class",
        "correlation"
    ]
})
result = response.json()

# Mostrar gráficas en Colab
for plot_name, b64_data in result['plots_base64'].items():
    print(f"\n📊 {plot_name}")
    display(Image(data=base64.b64decode(b64_data)))
```

## Endpoints Auxiliares

### Descargar CSV
```python
response = requests.get(f"{BASE_URL}/api/v1/nutritional/download_csv")
with open("training_data.csv", "wb") as f:
    f.write(response.content)
```

### Descargar Modelo
```python
response = requests.get(f"{BASE_URL}/api/v1/nutritional/download_model")
with open("nutritional_predictor.pkl", "wb") as f:
    f.write(response.content)
```

### Descargar Gráfica Específica
```python
response = requests.get(f"{BASE_URL}/api/v1/nutritional/download_plot/feature_importance")
with open("feature_importance.png", "wb") as f:
    f.write(response.content)
```

## Health Check
```python
response = requests.get(f"{BASE_URL}/health")
print(response.json())
```
