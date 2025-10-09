# Modelo Final - 90% Accuracy

## 📊 Información del Modelo

**Fecha de entrenamiento:** 08/10/2025  
**Archivo:** `models/rf_model.pkl`  
**Tipo:** Random Forest Classifier  
**Accuracy:** 90.18% (cross-validation 5-fold)

---

## 🎯 Características del Dataset

### Datos de Entrenamiento:
- **Total muestras:** 5,092
  - Sintéticas (OMS): 4,880
  - Reales (BD): 212
- **Distribución:**
  - DESNUTRICION_SEVERA: 10%
  - DESNUTRICION_MODERADA: 15%
  - RIESGO_DESNUTRICION: 15%
  - NORMAL: 30%
  - RIESGO_SOBREPESO: 15%
  - SOBREPESO: 10%
  - OBESIDAD: 5%

### Features Utilizados (11):
1. `age_months` - Edad en meses
2. `sex_numeric` - Sexo (1=M, 0=F)
3. `BMI` - Índice de masa corporal
4. `bmi_velocity` - Cambio de IMC
5. `weight_velocity` - Cambio de peso
6. `height_velocity` - Cambio de talla
7. `allergy_count` - Número de alergias
8. `adherence_score` - Adherencia (0-100)
9. `symptom_frequency` - Frecuencia síntomas
10. `dietary_diversity_score` - Diversidad dietética
11. `altitude_m` - Altitud

**⚠️ IMPORTANTE:** BAZ NO está incluido como feature para evitar overfitting.

---

## 📈 Métricas de Rendimiento

### Cross-Validation (5-fold):
- **Fold 1:** 89.60%
- **Fold 2:** 90.48%
- **Fold 3:** 91.36%
- **Fold 4:** 90.47%
- **Fold 5:** 89.00%
- **Promedio:** 90.18% ± 0.81%

### Validación Simple:
- **Accuracy:** 88.42%
- **F1-Score:** 88.43%

---

## ✅ Ventajas del Modelo

1. **Sin Overfitting**
   - 90% es realista (no 100%)
   - Generaliza bien a datos nuevos

2. **Basado en Estándares OMS**
   - Entrenado con datos generados desde tablas OMS oficiales
   - Aprende patrones de clasificación correctos

3. **Incluye Datos Reales**
   - 212 casos reales de la BD
   - Conoce patrones específicos del sistema

4. **Robusto**
   - Cross-validation confirma consistencia
   - Funciona bien en diferentes subconjuntos

---

## 🔄 Cómo se Usa

### En la API ML (puerto 8003):

```python
# El modelo se carga automáticamente al iniciar
ML_MODEL = RandomForestNutritionClassifier()
ML_MODEL.load(Path("models/rf_model.pkl"))

# Para hacer predicción:
result = ML_MODEL.predict_with_metadata(X)
# result["predictions"][0]["label"] → Clasificación
# result["predictions"][0]["probability"] → Confianza
```

### Clasificación Final:

El sistema usa un **enfoque híbrido**:
1. Calcula BAZ usando tablas OMS
2. Clasifica según rangos BAZ (reglas OMS)
3. El modelo ML se usa como validación adicional

---

## 📁 Archivos del Modelo

```
models/
├── rf_model.pkl              # Modelo entrenado (44 MB)
├── rf_metrics.json           # Métricas de validación
├── cv_metrics.json           # Métricas cross-validation
├── rf_feature_importance.csv # Importancia de features
└── backup_old/               # Modelos antiguos (respaldo)
    ├── ensemble_model.pkl
    ├── ensemble_model_nn.pkl
    └── ensemble_model_rf.pkl
```

---

## 🚀 Para Usar el Modelo

### 1. Reiniciar API ML:
```bash
cd modelo/ml-recomendator
./run_api.sh
```

### 2. Verificar que cargó correctamente:
```bash
curl http://localhost:8003/health
```

### 3. Probar predicción:
```bash
curl -X POST http://localhost:8003/ml/analisis_nutricional \
  -H "Content-Type: application/json" \
  -d '{
    "nin_id": 1,
    "peso_kg": 25,
    "talla_cm": 130
  }'
```

---

## 🔄 Para Re-entrenar

Si necesitas re-entrenar el modelo con datos nuevos:

```bash
# 1. Generar dataset actualizado
python3 scripts/generar_datos_desde_oms.py --samples 5000

# 2. Entrenar modelo
python3 src/pipeline/train_model.py \
  --data data/raw/surveys/datos_completos_oms_reales.csv \
  --model rf \
  --output models/ \
  --use-cv \
  --cv-folds 5

# 3. Reiniciar API
./run_api.sh
```

---

## 📝 Notas Importantes

1. **El modelo NO usa BAZ como feature** - Esto evita overfitting
2. **La clasificación final usa reglas OMS** - El modelo es complementario
3. **90% accuracy es ideal** - No es 100% (overfitting) ni <80% (underfitting)
4. **Funciona de 5-19 años** - Rango de las tablas OMS 2007

---

**Estado:** ✅ Producción  
**Última actualización:** 08/10/2025
