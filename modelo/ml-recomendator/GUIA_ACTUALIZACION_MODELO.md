# 🔄 Guía de Actualización del Modelo ML

## ¿Cuándo actualizar el modelo?

Debes actualizar el modelo cuando:

- ✅ **Entran nuevos niños** a la base de datos
- ✅ **Se agregan nuevas mediciones** antropométricas
- ✅ **Cada semana/mes** (según tu frecuencia de uso)
- ✅ **Cuando el accuracy baja** en producción
- ✅ **Después de corregir datos** erróneos

---

## 🚀 Método Rápido (Recomendado)

### Un solo comando:
```bash
cd modelo/ml-recomendator
./actualizar_modelo.sh
```

Este script hace TODO automáticamente:
1. Exporta datos desde la BD
2. Reentrena el modelo
3. Verifica clasificaciones
4. Genera gráficas actualizadas
5. Muestra métricas del nuevo modelo

---

## 📝 Método Manual (Paso a Paso)

### Paso 1: Exportar datos desde la BD
```bash
cd modelo/ml-recomendator
python scripts/generar_datos_desde_oms.py
```

**¿Qué hace?**
- Conecta a la BD PostgreSQL
- Extrae todos los niños con sus mediciones
- Calcula Z-scores (BAZ, WAZ, HAZ)
- Genera `datos_completos_oms_reales.csv`

**Verifica:**
```bash
wc -l data/raw/surveys/datos_completos_oms_reales.csv
```

---

### Paso 2: Reentrenar el modelo
```bash
cd modelo/ml-recomendator
python src/pipeline/train_model.py
```

**¿Qué hace?**
- Lee los nuevos datos
- Divide en train/test (80/20)
- Entrena Random Forest con 100 árboles
- Aplica class_weight='balanced'
- Guarda modelo en `models/rf_model.pkl`
- Genera métricas en `models/rf_metrics.json`

**Tiempo estimado:** 30-60 segundos

---

### Paso 3: Verificar el nuevo modelo
```bash
cd modelo/ml-recomendator
python scripts/test_clasificacion.py
```

**¿Qué verifica?**
- Accuracy general
- Precision/Recall por clase
- Casos de prueba específicos

**Métricas esperadas:**
- Accuracy: > 90%
- F1-Score por clase: > 0.85

---

### Paso 4: Generar gráficas actualizadas
```bash
cd modelo/ml-recomendator
./generar_graficas.sh
```

**¿Qué genera?**
- 8 gráficas en `reports/figures/`
- Matriz de confusión actualizada
- Feature importance actualizado
- Métricas por clase actualizadas

---

### Paso 5: Reiniciar la API del modelo
```bash
cd modelo/ml-recomendator
docker-compose down
docker-compose up -d
```

**¿Por qué?**
- El contenedor Docker carga el modelo al iniciar
- Necesita reiniciarse para usar el nuevo `rf_model.pkl`

**Verifica que funciona:**
```bash
curl http://localhost:8001/health
```

---

## 📊 Comparar Modelos (Antes vs Después)

### Ver métricas del modelo anterior
```bash
# Si guardaste un backup
cat modelo/ml-recomendator/models/backup_old/rf_metrics.json
```

### Ver métricas del modelo nuevo
```bash
cat modelo/ml-recomendator/models/rf_metrics.json
```

### Comparar accuracy
```bash
echo "Modelo anterior:"
cat models/backup_old/rf_metrics.json | grep accuracy

echo "Modelo nuevo:"
cat models/rf_metrics.json | grep accuracy
```

---

## 🔍 Checklist de Validación

Después de actualizar, verifica:

- [ ] **Datos exportados correctamente**
  ```bash
  head -5 data/raw/surveys/datos_completos_oms_reales.csv
  ```

- [ ] **Modelo entrenado sin errores**
  ```bash
  ls -lh models/rf_model.pkl
  ```

- [ ] **Accuracy >= 90%**
  ```bash
  cat models/rf_metrics.json | grep accuracy
  ```

- [ ] **Gráficas generadas (8 archivos)**
  ```bash
  ls -1 reports/figures/*.png | wc -l
  ```

- [ ] **API responde correctamente**
  ```bash
  curl http://localhost:8001/health
  ```

- [ ] **Clasificación funciona**
  ```bash
  python scripts/test_modelo_api.py
  ```

---

## ⚠️ Problemas Comunes

### Error: "No se puede conectar a la BD"
**Solución:**
```bash
# Verifica que la BD esté corriendo
docker ps | grep postgres

# Verifica las credenciales en .env
cat modelo/ml-recomendator/.env
```

---

### Error: "Pocos datos para entrenar"
**Solución:**
- Necesitas al menos 100 registros por clase
- Verifica:
  ```bash
  python -c "import pandas as pd; df = pd.read_csv('data/raw/surveys/datos_completos_oms_reales.csv'); print(df['label_status'].value_counts())"
  ```

---

### Error: "Accuracy bajó después de actualizar"
**Posibles causas:**
1. **Datos nuevos tienen errores** → Revisar calidad de datos
2. **Datos desbalanceados** → Usar `scripts/balancear_datos.py`
3. **Outliers** → Revisar mediciones extremas

**Solución:**
```bash
# Verificar calidad de datos
python scripts/verificar_datos.py

# Balancear si es necesario
python scripts/balancear_datos.py
```

---

### Warning: "Modelo muy grande"
**Solución:**
- El modelo crece con más datos (normal)
- Si supera 100MB, considera:
  ```python
  # En train_model.py, reducir n_estimators
  n_estimators=50  # en vez de 100
  ```

---

## 📅 Frecuencia Recomendada de Actualización

| Escenario | Frecuencia |
|-----------|------------|
| **Desarrollo/Testing** | Cada vez que agregues datos de prueba |
| **Producción (bajo uso)** | Mensual |
| **Producción (uso medio)** | Semanal |
| **Producción (alto uso)** | Diario o cuando haya 100+ nuevos registros |

---

## 🎯 Estrategia de Actualización en Producción

### Opción 1: Actualización Manual (Recomendada para empezar)
```bash
# Cada semana/mes
./actualizar_modelo.sh
```

### Opción 2: Cron Job Automático
```bash
# Agregar a crontab (actualizar cada domingo a las 2am)
0 2 * * 0 cd /ruta/modelo/ml-recomendator && ./actualizar_modelo.sh >> logs/actualizacion.log 2>&1
```

### Opción 3: Trigger en la BD (Avanzado)
- Crear trigger que detecte N nuevos registros
- Ejecutar script de actualización automáticamente

---

## 💾 Backup del Modelo Anterior

**Antes de actualizar, guarda el modelo actual:**
```bash
cd modelo/ml-recomendator

# Crear backup con fecha
FECHA=$(date +%Y%m%d_%H%M%S)
mkdir -p models/backups
cp models/rf_model.pkl models/backups/rf_model_$FECHA.pkl
cp models/rf_metrics.json models/backups/rf_metrics_$FECHA.json

echo "✅ Backup guardado: models/backups/rf_model_$FECHA.pkl"
```

**Restaurar modelo anterior si algo sale mal:**
```bash
# Listar backups
ls -lht models/backups/

# Restaurar el último backup
cp models/backups/rf_model_YYYYMMDD_HHMMSS.pkl models/rf_model.pkl
```

---

## 📈 Monitoreo de Mejora del Modelo

### Script para comparar métricas
```bash
# Ver evolución del accuracy
echo "Historial de accuracy:"
for file in models/backups/rf_metrics_*.json; do
    echo -n "$(basename $file): "
    cat $file | grep accuracy | head -1
done
```

---

## 🚨 Cuándo NO actualizar

**NO actualices el modelo si:**
- ❌ Tienes menos de 50 registros nuevos
- ❌ Los datos nuevos tienen errores evidentes
- ❌ Estás en medio de una presentación/demo
- ❌ No has hecho backup del modelo actual
- ❌ El modelo actual tiene accuracy > 95% y funciona perfecto

---

## 📞 Resumen Ejecutivo

### Para actualizar el modelo después de agregar niños:

```bash
cd modelo/ml-recomendator
./actualizar_modelo.sh
```

### Eso es todo! 🎉

El script hace:
1. ✅ Exporta datos de la BD
2. ✅ Reentrena el modelo
3. ✅ Verifica que funciona
4. ✅ Genera gráficas
5. ✅ Muestra métricas

**Tiempo total:** 2-3 minutos

---

## 💡 Tips Pro

1. **Actualiza en horarios de bajo tráfico** (madrugada)
2. **Siempre haz backup antes** de actualizar
3. **Compara métricas** antes y después
4. **Documenta cambios significativos** en accuracy
5. **Mantén historial de modelos** (últimos 5 backups)

---

## 📚 Documentos Relacionados

- `COMO_PROBAR.md` - Cómo probar el modelo
- `GUIA_GRAFICAS.md` - Cómo generar gráficas
- `README.md` - Documentación general
- `MODELO_FINAL_90_ACCURACY.md` - Detalles del modelo
