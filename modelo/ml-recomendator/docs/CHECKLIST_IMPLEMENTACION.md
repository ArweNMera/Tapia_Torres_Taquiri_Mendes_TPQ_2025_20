# ✅ Checklist de Implementación

## Fase 1: Preparación de Base de Datos

### 1.1 Ejecutar Migraciones
- [ ] Hacer backup de la base de datos actual
- [ ] Ejecutar `MIGRACIONES_BD.sql` en base de datos de desarrollo
- [ ] Verificar que todas las tablas se crearon correctamente
  ```sql
  SHOW TABLES LIKE 'features_ml';
  SHOW TABLES LIKE 'menus_nutrientes';
  SHOW TABLES LIKE 'predicciones_ml';
  ```
- [ ] Verificar que las columnas nuevas existen
  ```sql
  DESCRIBE entidades;
  DESCRIBE adherencias;
  DESCRIBE sintomas;
  ```

### 1.2 Poblar Datos Iniciales
- [ ] Insertar datos de altitud para entidades existentes
  ```sql
  UPDATE entidades SET ent_altitud_m = 2400 WHERE ent_departamento = 'CUSCO';
  UPDATE entidades SET ent_zona = 'URBANA' WHERE ent_tipo = 'HOSPITAL';
  ```
- [ ] Calcular features ML para niños existentes
  ```sql
  -- Por cada niño con antropometría
  CALL sp_calcular_features_ml(nin_id, ant_id);
  ```

### 1.3 Validar Datos
- [ ] Verificar que hay suficientes datos para entrenar (mínimo 100 casos)
- [ ] Verificar distribución de clases (NORMAL, RIESGO, MODERADO, SEVERO)
- [ ] Identificar y corregir datos faltantes críticos

---

## Fase 2: Preparación del Entorno ML

### 2.1 Instalación de Dependencias
- [ ] Crear entorno virtual
  ```bash
  cd modelo/ml-recomendator
  python -m venv .venv
  source .venv/bin/activate  # Linux/Mac
  # o .venv\Scripts\activate  # Windows
  ```
- [ ] Instalar dependencias
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Verificar instalación de PyTorch (opcional, para Red Neuronal)
  ```bash
  python -c "import torch; print(torch.__version__)"
  ```

### 2.2 Configuración
- [ ] Copiar `.env.example` a `.env`
- [ ] Configurar variables de entorno (LLM, base de datos)
- [ ] Verificar rutas en configs (`rf.yaml`, `nn.yaml`)

### 2.3 Datos OMS
- [ ] Verificar que existen tablas OMS en `data/raw/who/`
  - `bmi_boys_0-to-2-years_zcores_1.csv`
  - `bmi_boys_2-to-5-years_zscores.csv`
  - `bmifa-boys-5-19years-z.csv`
  - `tab_bmi_girls_p_0_2.csv`
  - `tab_bmi_girls_p_2_5.csv`
  - `bmifa-girls-5-19years-z.csv`

---

## Fase 3: Preparación de Datos

### 3.1 Extracción desde Base de Datos
- [ ] Crear script para extraer datos de MySQL a CSV
  ```python
  # Extraer datos de niños con antropometría y features
  SELECT 
    n.nin_id, n.nin_fecha_nac, n.nin_sexo,
    a.ant_peso_kg, a.ant_talla_cm, a.ant_fecha,
    f.*
  FROM ninos n
  JOIN antropometrias a ON n.nin_id = a.nin_id
  LEFT JOIN features_ml f ON a.ant_id = f.ant_id
  ```
- [ ] Guardar en `data/raw/surveys/datos_historicos.csv`

### 3.2 Etiquetado con OMS
- [ ] Ejecutar script de etiquetado
  ```bash
  python src/pipeline/label_dataset.py \
    --in data/raw/surveys \
    --who data/raw/who \
    --out data/interim/labeled_data.csv
  ```
- [ ] Verificar que se generó `labeled_data.csv`
- [ ] Verificar columnas: `baz`, `label_status`, `classification`

### 3.3 Validación de Datos
- [ ] Ejecutar validación
  ```python
  from src.features import DataValidator
  validator = DataValidator()
  result = validator.validate_anthropometric_data(df)
  print(result)
  ```
- [ ] Corregir problemas identificados
- [ ] Verificar distribución de clases (no muy desbalanceada)

---

## Fase 4: Entrenamiento de Modelos

### 4.1 Baseline: Random Forest
- [ ] Entrenar modelo RF
  ```bash
  python src/pipeline/train_model.py \
    --data data/interim/labeled_data.csv \
    --model rf \
    --output models/
  ```
- [ ] Verificar métricas en `models/rf_metrics.json`
  - Accuracy > 80%
  - Recall SEVERO > 85%
- [ ] Revisar feature importance en `models/rf_feature_importance.csv`
- [ ] Identificar features más importantes

### 4.2 Red Neuronal
- [ ] Entrenar modelo NN
  ```bash
  python src/pipeline/train_model.py \
    --data data/interim/labeled_data.csv \
    --model nn \
    --output models/
  ```
- [ ] Verificar métricas en `models/nn_metrics.json`
- [ ] Comparar con Random Forest

### 4.3 Ensemble
- [ ] Entrenar ensemble
  ```bash
  python src/pipeline/train_model.py \
    --data data/interim/labeled_data.csv \
    --model ensemble \
    --output models/
  ```
- [ ] Verificar métricas en `models/ensemble_metrics.json`
- [ ] Confirmar que ensemble supera modelos individuales

### 4.4 Validación
- [ ] Ejecutar ejemplos
  ```bash
  python examples/ejemplo_completo.py
  ```
- [ ] Verificar predicciones en casos conocidos
- [ ] Validar con nutricionistas (casos de prueba)

---

## Fase 5: Integración con API

### 5.1 Actualizar API FastAPI
- [ ] Agregar endpoint de predicción ML
  ```python
  @app.post("/ml/predict_nutrition")
  def predict_nutrition(nin_id: int):
      # Cargar features desde BD
      # Predecir con modelo
      # Guardar en predicciones_ml
      # Retornar resultado
  ```
- [ ] Agregar endpoint de explicación
  ```python
  @app.post("/ml/explain")
  def explain_prediction(pml_id: int):
      # Cargar predicción
      # Generar explicación con SHAP/LLM
      # Retornar explicación
  ```

### 5.2 Testing de API
- [ ] Probar endpoint de predicción
  ```bash
  curl -X POST http://localhost:8000/ml/predict_nutrition \
    -H "Content-Type: application/json" \
    -d '{"nin_id": 123}'
  ```
- [ ] Verificar que se guarda en `predicciones_ml`
- [ ] Probar con diferentes casos (NORMAL, RIESGO, SEVERO)

### 5.3 Integración con Frontend
- [ ] Agregar botón "Evaluar con ML" en perfil de niño
- [ ] Mostrar predicción y probabilidades
- [ ] Mostrar explicación en lenguaje natural
- [ ] Permitir feedback de nutricionista

---

## Fase 6: Monitoreo y Mejora

### 6.1 Monitoreo
- [ ] Crear dashboard de métricas
  - Predicciones por día
  - Distribución de clases predichas
  - Acuerdo con evaluación manual
- [ ] Configurar alertas para casos SEVEROS
- [ ] Logging de predicciones

### 6.2 Feedback Loop
- [ ] Implementar sistema de validación por nutricionistas
  ```sql
  UPDATE predicciones_ml 
  SET pml_validado = TRUE, 
      pml_validado_por = ?,
      pml_feedback = ?
  WHERE pml_id = ?;
  ```
- [ ] Recopilar casos donde el modelo falla
- [ ] Analizar patrones de error

### 6.3 Re-entrenamiento
- [ ] Programar re-entrenamiento trimestral
- [ ] Incluir datos validados en nuevo entrenamiento
- [ ] Comparar métricas con versión anterior
- [ ] Desplegar nueva versión si mejora

---

## Fase 7: Documentación y Capacitación

### 7.1 Documentación Técnica
- [ ] Documentar API endpoints
- [ ] Documentar procedimientos almacenados
- [ ] Documentar proceso de re-entrenamiento
- [ ] Crear guía de troubleshooting

### 7.2 Documentación de Usuario
- [ ] Manual de uso para nutricionistas
- [ ] Guía de interpretación de predicciones
- [ ] FAQ sobre el modelo ML
- [ ] Videos tutoriales

### 7.3 Capacitación
- [ ] Capacitar a nutricionistas en uso del sistema
- [ ] Explicar cómo interpretar predicciones
- [ ] Entrenar en validación de predicciones
- [ ] Recopilar feedback inicial

---

## Fase 8: Producción

### 8.1 Pre-producción
- [ ] Ejecutar migraciones en base de datos de producción
- [ ] Desplegar modelos entrenados
- [ ] Configurar variables de entorno
- [ ] Probar en ambiente de staging

### 8.2 Despliegue
- [ ] Hacer backup completo
- [ ] Desplegar API actualizada
- [ ] Verificar que endpoints funcionan
- [ ] Monitorear logs por 24 horas

### 8.3 Post-despliegue
- [ ] Verificar primeras predicciones
- [ ] Recopilar feedback de usuarios
- [ ] Ajustar umbrales si es necesario
- [ ] Documentar lecciones aprendidas

---

## Métricas de Éxito

### Técnicas
- [ ] Accuracy ≥ 85%
- [ ] Recall SEVERO ≥ 90%
- [ ] Precision NORMAL ≥ 80%
- [ ] Tiempo de inferencia < 100ms
- [ ] Uptime API > 99%

### Negocio
- [ ] Reducción de falsos negativos ≥ 30%
- [ ] Satisfacción de nutricionistas ≥ 4/5
- [ ] Adopción del sistema ≥ 70%
- [ ] Tiempo de evaluación reducido ≥ 50%

### Calidad
- [ ] Acuerdo con evaluación manual ≥ 85%
- [ ] Feedback positivo de nutricionistas ≥ 80%
- [ ] Casos críticos detectados ≥ 95%

---

## Notas Importantes

### ⚠️ Antes de Producción
1. **Validar con nutricionistas**: El modelo debe ser validado por expertos
2. **No reemplazar juicio clínico**: El modelo es una herramienta de apoyo
3. **Monitorear constantemente**: Revisar predicciones regularmente
4. **Feedback loop**: Implementar sistema de mejora continua

### 🔒 Seguridad
1. **Datos sensibles**: Proteger información de niños
2. **Acceso controlado**: Solo personal autorizado
3. **Auditoría**: Registrar todas las predicciones
4. **Backup**: Respaldar modelos y datos regularmente

### 📊 Mejora Continua
1. **Recopilar datos**: Más datos = mejor modelo
2. **Validar predicciones**: Feedback de nutricionistas
3. **Re-entrenar**: Actualizar modelo trimestralmente
4. **Experimentar**: Probar nuevos features y modelos

---

**Última actualización**: 2025-01-07  
**Versión**: 1.0
