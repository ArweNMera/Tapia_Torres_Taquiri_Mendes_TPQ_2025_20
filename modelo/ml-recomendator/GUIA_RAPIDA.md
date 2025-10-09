# 🚀 Guía Rápida del Modelo ML

## 📋 Comandos Esenciales

### 🔄 Reentrenar Modelo (Cuando entren más niños)
```bash
cd modelo/ml-recomendator
./actualizar_modelo.sh
docker-compose restart
```

---

### 📊 Generar Gráficas
```bash
cd modelo/ml-recomendator
./generar_graficas.sh
```

---

### ✅ Probar el Modelo
```bash
cd modelo/ml-recomendator
python scripts/test_clasificacion.py
```

---

### 🔍 Verificar Integración
```bash
cd modelo/ml-recomendator
./verificar_integracion.sh
```

---

## 📚 Documentación Completa

| Documento | Para Qué |
|-----------|----------|
| **REENTRENAR_MODELO.md** | 🔄 Cómo actualizar el modelo con nuevos datos |
| **GUIA_GRAFICAS.md** | 📊 Cómo generar y entender las gráficas |
| **EXPLICACION_DATOS.md** | 📈 De dónde vienen los datos (reales vs sintéticos) |
| **COMO_PROBAR.md** | ✅ Cómo probar que todo funciona |
| **README.md** | 📖 Documentación técnica completa |

---

## 🎯 Flujos Comunes

### Flujo 1: Agregaste Niños a la BD
```bash
# 1. Reentrenar
./actualizar_modelo.sh

# 2. Verificar métricas
cat models/rf_metrics.json

# 3. Reiniciar API
docker-compose restart

# 4. Probar
python scripts/test_modelo_api.py
```

---

### Flujo 2: Generar Gráficas para Presentación
```bash
# 1. Generar todas las gráficas
./generar_graficas.sh

# 2. Abrir carpeta
open reports/figures/

# Las 3 más importantes:
# - 02_confusion_matrix.png
# - 01_feature_importance.png
# - 08_metricas_comparacion.png
```

---

### Flujo 3: Verificar que Todo Funciona
```bash
# 1. Verificar integración completa
./verificar_integracion.sh

# 2. Probar clasificación
python scripts/test_clasificacion.py

# 3. Probar API
curl http://localhost:8001/health
```

---

## 🔧 Scripts Disponibles

| Script | Qué Hace |
|--------|----------|
| `actualizar_modelo.sh` | Reentrena el modelo con nuevos datos |
| `generar_graficas.sh` | Genera las 8 gráficas del modelo |
| `verificar_integracion.sh` | Verifica que todo esté integrado |
| `restart_server.sh` | Reinicia el servidor de la API |

---

## 📊 Archivos Importantes

```
modelo/ml-recomendator/
├── models/
│   ├── rf_model.pkl              # Modelo entrenado
│   ├── rf_metrics.json           # Métricas del modelo
│   └── backups/                  # Backups de modelos anteriores
├── data/raw/surveys/
│   └── datos_completos_oms_reales.csv  # Datos de entrenamiento
├── reports/figures/
│   ├── 01_feature_importance.png
│   ├── 02_confusion_matrix.png
│   └── ... (8 gráficas en total)
└── scripts/
    ├── generar_solo_datos_reales.py
    ├── test_clasificacion.py
    └── generar_graficas.py
```

---

## 🎓 Casos de Uso

### Caso 1: "Agregué 50 niños nuevos"
```bash
./actualizar_modelo.sh
docker-compose restart
```

### Caso 2: "Necesito gráficas para una presentación"
```bash
./generar_graficas.sh
open reports/figures/
```

### Caso 3: "¿El modelo está funcionando bien?"
```bash
python scripts/test_clasificacion.py
cat models/rf_metrics.json
```

### Caso 4: "¿Está todo integrado correctamente?"
```bash
./verificar_integracion.sh
```

---

## 💡 Tips Rápidos

1. **Reentrenar cada semana** si usas el sistema activamente
2. **Hacer backup** antes de reentrenar (el script lo hace automático)
3. **Verificar accuracy** después de reentrenar (debe ser > 90%)
4. **Mantener últimos 5 backups** por seguridad
5. **Generar gráficas** después de cada reentrenamiento

---

## 🚨 Problemas Comunes

### "No se puede conectar a MySQL"
```bash
# Verifica que MySQL esté corriendo
docker ps | grep mysql

# Verifica credenciales
cat .env
```

### "Accuracy bajó después de reentrenar"
```bash
# Restaurar backup anterior
ls -lht models/backups/
cp models/backups/rf_model_YYYYMMDD_HHMMSS.pkl models/rf_model.pkl
docker-compose restart
```

### "Pocas muestras para entrenar"
```bash
# Usar datos sintéticos
./actualizar_modelo.sh --sinteticos
```

---

## 📞 Resumen Ultra-Rápido

### Cuando entren más niños:
```bash
cd modelo/ml-recomendator
./actualizar_modelo.sh
docker-compose restart
```

### Para generar gráficas:
```bash
cd modelo/ml-recomendator
./generar_graficas.sh
```

### Para verificar todo:
```bash
cd modelo/ml-recomendator
./verificar_integracion.sh
```

---

## 🎯 Métricas Objetivo

- ✅ **Accuracy**: > 90%
- ✅ **F1-Score**: > 0.85 por clase
- ✅ **Precision**: > 0.85 por clase
- ✅ **Recall**: > 0.85 por clase

---

## 📚 Lee Más

- **REENTRENAR_MODELO.md** - Guía detallada de reentrenamiento
- **GUIA_GRAFICAS.md** - Explicación de cada gráfica
- **EXPLICACION_DATOS.md** - Cómo se generan los datos
- **COMO_PROBAR.md** - Guía completa de pruebas

---

**¿Dudas?** Lee la documentación completa en los archivos `.md` 📖
