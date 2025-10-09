# 📋 Resumen de Scripts y Documentación

## 🎯 Scripts Principales (Los que usarás)

### 1. `actualizar_modelo.sh` ⭐⭐⭐⭐⭐
**Para qué:** Reentrenar el modelo cuando entren más niños a la BD

```bash
./actualizar_modelo.sh              # Solo datos reales
./actualizar_modelo.sh --sinteticos # Incluye sintéticos
```

**Qué hace:**
- ✅ Hace backup del modelo actual
- ✅ Exporta datos desde MySQL
- ✅ Reentrena el modelo
- ✅ Verifica que funcione
- ✅ Genera gráficas
- ✅ Muestra métricas

**Cuándo usar:** Cada vez que agregues 50+ niños nuevos, o semanalmente

---

### 2. `generar_graficas.sh` ⭐⭐⭐⭐
**Para qué:** Generar las 8 gráficas del modelo

```bash
./generar_graficas.sh
```

**Qué genera:**
- 01_feature_importance.png
- 02_confusion_matrix.png ⭐ (La más importante)
- 03_distribucion_clases.png
- 04_arbol_decision.png
- 05_correlacion_features.png
- 06_distribucion_baz.png
- 07_edad_vs_bmi.png
- 08_metricas_comparacion.png ⭐

**Cuándo usar:** Para presentaciones, reportes, o después de reentrenar

---

### 3. `verificar_integracion.sh` ⭐⭐⭐
**Para qué:** Verificar que todo esté integrado correctamente

```bash
./verificar_integracion.sh
```

**Qué verifica:**
- ✅ BD MySQL conecta
- ✅ Tablas OMS existen
- ✅ Modelo está entrenado
- ✅ API responde
- ✅ Clasificación funciona

**Cuándo usar:** Después de cambios, o para debugging

---

### 4. `restart_server.sh` ⭐⭐
**Para qué:** Reiniciar el servidor de la API

```bash
./restart_server.sh
```

**Cuándo usar:** Después de reentrenar el modelo

---

## 📚 Documentación Principal

### 1. `GUIA_RAPIDA.md` ⭐⭐⭐⭐⭐
**Qué es:** Comandos esenciales y flujos comunes

**Lee esto si:**
- ✅ Quieres saber qué comando usar
- ✅ Necesitas resolver algo rápido
- ✅ No quieres leer mucho

---

### 2. `REENTRENAR_MODELO.md` ⭐⭐⭐⭐⭐
**Qué es:** Guía completa de cómo reentrenar el modelo

**Lee esto si:**
- ✅ Agregaste niños a la BD
- ✅ Quieres actualizar el modelo
- ✅ Necesitas entender el proceso completo

---

### 3. `GUIA_GRAFICAS.md` ⭐⭐⭐⭐
**Qué es:** Explicación de las 8 gráficas del modelo

**Lee esto si:**
- ✅ Vas a hacer una presentación
- ✅ Necesitas entender las gráficas
- ✅ Quieres saber cuáles son las más importantes

---

### 4. `EXPLICACION_DATOS.md` ⭐⭐⭐⭐
**Qué es:** De dónde vienen los datos (reales vs sintéticos)

**Lee esto si:**
- ✅ Quieres entender cómo se generan los datos
- ✅ Te preguntas de dónde salieron los ~500 registros
- ✅ Quieres saber si usar sintéticos o solo reales

---

### 5. `COMO_PROBAR.md` ⭐⭐⭐
**Qué es:** Guía completa de cómo probar el modelo

**Lee esto si:**
- ✅ Quieres verificar que todo funciona
- ✅ Necesitas hacer pruebas
- ✅ Estás debuggeando problemas

---

### 6. `README.md` ⭐⭐⭐
**Qué es:** Documentación técnica completa

**Lee esto si:**
- ✅ Quieres entender la arquitectura
- ✅ Necesitas detalles técnicos
- ✅ Vas a modificar el código

---

## 🗑️ Documentos Antiguos (Ya no necesitas)

Estos documentos fueron útiles durante el desarrollo, pero ya no son necesarios:

- ~~GUIA_ACTUALIZACION_MODELO.md~~ → Usa `REENTRENAR_MODELO.md`
- ~~INTEGRACION_MODELO_ML.md~~ → Ya está integrado
- ~~MODELO_FINAL_90_ACCURACY.md~~ → Info incluida en README

---

## 🎯 Flujo de Trabajo Típico

### Escenario 1: Agregaste Niños a la BD
```bash
# 1. Reentrenar
./actualizar_modelo.sh

# 2. Verificar
cat models/rf_metrics.json

# 3. Reiniciar API
docker-compose restart

# 4. Probar
python scripts/test_modelo_api.py
```

**Documentos a leer:**
- REENTRENAR_MODELO.md

---

### Escenario 2: Necesitas Gráficas para Presentación
```bash
# 1. Generar gráficas
./generar_graficas.sh

# 2. Abrir carpeta
open reports/figures/
```

**Documentos a leer:**
- GUIA_GRAFICAS.md

---

### Escenario 3: Algo No Funciona
```bash
# 1. Verificar integración
./verificar_integracion.sh

# 2. Ver logs
docker-compose logs -f
```

**Documentos a leer:**
- COMO_PROBAR.md
- GUIA_RAPIDA.md (sección Troubleshooting)

---

## 📊 Archivos Importantes del Sistema

```
modelo/ml-recomendator/
├── 🔧 Scripts Ejecutables
│   ├── actualizar_modelo.sh        ⭐⭐⭐⭐⭐ Reentrenar modelo
│   ├── generar_graficas.sh         ⭐⭐⭐⭐ Generar gráficas
│   ├── verificar_integracion.sh    ⭐⭐⭐ Verificar todo
│   └── restart_server.sh           ⭐⭐ Reiniciar API
│
├── 📚 Documentación
│   ├── GUIA_RAPIDA.md              ⭐⭐⭐⭐⭐ Comandos esenciales
│   ├── REENTRENAR_MODELO.md        ⭐⭐⭐⭐⭐ Cómo reentrenar
│   ├── GUIA_GRAFICAS.md            ⭐⭐⭐⭐ Explicación gráficas
│   ├── EXPLICACION_DATOS.md        ⭐⭐⭐⭐ De dónde vienen datos
│   ├── COMO_PROBAR.md              ⭐⭐⭐ Cómo probar
│   └── README.md                   ⭐⭐⭐ Documentación técnica
│
├── 🤖 Modelo y Datos
│   ├── models/rf_model.pkl         Modelo entrenado
│   ├── models/rf_metrics.json      Métricas del modelo
│   ├── models/backups/             Backups de modelos
│   └── data/raw/surveys/           Datos de entrenamiento
│
└── 📊 Resultados
    └── reports/figures/            8 gráficas del modelo
```

---

## 💡 Consejos

1. **Empieza con GUIA_RAPIDA.md** - Tiene todo lo esencial
2. **Usa `actualizar_modelo.sh`** - Hace todo automáticamente
3. **Revisa las gráficas** - Especialmente la matriz de confusión
4. **Mantén backups** - El script lo hace automático
5. **Lee solo lo que necesitas** - No tienes que leer todo

---

## 🎓 TL;DR

### Para reentrenar:
```bash
./actualizar_modelo.sh
```

### Para gráficas:
```bash
./generar_graficas.sh
```

### Para verificar:
```bash
./verificar_integracion.sh
```

### Para aprender:
Lee `GUIA_RAPIDA.md` primero, luego los demás según necesites.

---

**¿Dudas?** Empieza con `GUIA_RAPIDA.md` 🚀
