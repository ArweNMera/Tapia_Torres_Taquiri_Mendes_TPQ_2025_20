# 🔄 Cómo Reentrenar el Modelo ML

## 🎯 Un Solo Comando

Cuando entren más niños a tu BD MySQL, simplemente ejecuta:

```bash
cd modelo/ml-recomendator
./actualizar_modelo.sh
```

**Eso es todo!** 🎉

---

## 📋 Lo que Hace Automáticamente

El script `actualizar_modelo.sh` hace TODO por ti:

1. ✅ **Hace backup** del modelo actual
2. ✅ **Exporta datos** desde MySQL (solo reales)
3. ✅ **Verifica** que haya suficientes datos
4. ✅ **Reentrena** el modelo
5. ✅ **Verifica** que funcione bien
6. ✅ **Genera gráficas** actualizadas
7. ✅ **Muestra métricas** del nuevo modelo

**Tiempo:** 2-3 minutos

---

## 🎛️ Opciones

### Opción 1: Solo Datos Reales (Recomendado)
```bash
./actualizar_modelo.sh
```

Usa SOLO los niños de tu BD MySQL.

**Cuándo usar:**
- ✅ Tienes 100+ niños en la BD
- ✅ Quieres máxima precisión para tu población
- ✅ No quieres datos "inventados"

---

### Opción 2: Datos Reales + Sintéticos
```bash
./actualizar_modelo.sh --sinteticos
```

Usa tus niños reales + 1000 niños sintéticos generados con OMS.

**Cuándo usar:**
- ✅ Tienes menos de 100 niños
- ✅ Algunas categorías tienen pocos casos
- ✅ Quieres dataset balanceado

---

## 🔍 Verificar Resultados

### Ver métricas del modelo
```bash
cat models/rf_metrics.json
```

Busca:
- **Accuracy**: Debe ser > 0.90 (90%)
- **F1-Score**: Debe ser > 0.85 por clase

---

### Ver gráficas generadas
```bash
open reports/figures/
```

O en Linux:
```bash
xdg-open reports/figures/
```

Las 3 gráficas más importantes:
1. `02_confusion_matrix.png` - Precisión del modelo
2. `01_feature_importance.png` - Qué variables usa
3. `08_metricas_comparacion.png` - Rendimiento por clase

---

## 🔄 Reiniciar la API

Después de reentrenar, reinicia la API para que use el nuevo modelo:

```bash
cd modelo/ml-recomendator
docker-compose down
docker-compose up -d
```

Verifica que funciona:
```bash
curl http://localhost:8001/health
```

---

## 💾 Restaurar Modelo Anterior

Si el nuevo modelo no funciona bien:

```bash
# Ver backups disponibles
ls -lht models/backups/

# Restaurar el último backup
cp models/backups/rf_model_YYYYMMDD_HHMMSS.pkl models/rf_model.pkl

# Reiniciar API
docker-compose restart
```

---

## 📅 ¿Cada Cuánto Reentrenar?

| Situación | Frecuencia |
|-----------|------------|
| Agregaste 50+ niños nuevos | Inmediatamente |
| Uso activo del sistema | Semanal |
| Uso bajo | Mensual |
| Solo testing | Cuando sea necesario |

---

## 🚨 Troubleshooting

### Error: "No se puede conectar a la BD"
```bash
# Verifica que MySQL esté corriendo
docker ps | grep mysql

# Verifica credenciales
cat .env
```

---

### Error: "Menos de 100 registros"
Tienes 2 opciones:

**Opción A:** Agregar más niños a la BD

**Opción B:** Usar datos sintéticos
```bash
./actualizar_modelo.sh --sinteticos
```

---

### Error: "Accuracy bajó"
Posibles causas:
1. Datos nuevos tienen errores
2. Datos muy desbalanceados
3. Outliers extremos

**Solución:**
```bash
# Restaurar modelo anterior
cp models/backups/rf_model_YYYYMMDD_HHMMSS.pkl models/rf_model.pkl

# Verificar calidad de datos
python scripts/verificar_datos.py
```

---

## 📊 Ejemplo Completo

```bash
# 1. Ir al directorio
cd modelo/ml-recomendator

# 2. Reentrenar modelo
./actualizar_modelo.sh

# 3. Ver métricas
cat models/rf_metrics.json

# 4. Ver gráficas
open reports/figures/02_confusion_matrix.png

# 5. Reiniciar API
docker-compose restart

# 6. Probar que funciona
curl http://localhost:8001/health
python scripts/test_modelo_api.py
```

---

## 🎓 Resumen Ultra-Rápido

### Cuando entren más niños:
```bash
cd modelo/ml-recomendator
./actualizar_modelo.sh
docker-compose restart
```

### Eso es todo! 🚀

---

## 📚 Documentos Relacionados

- `EXPLICACION_DATOS.md` - De dónde vienen los datos
- `GUIA_ACTUALIZACION_MODELO.md` - Guía detallada
- `GUIA_GRAFICAS.md` - Explicación de gráficas
- `COMO_PROBAR.md` - Cómo probar el modelo
- `README.md` - Documentación general

---

## 💡 Tips Pro

1. **Siempre revisa las métricas** antes de usar el nuevo modelo
2. **Compara con el modelo anterior** (usa los backups)
3. **Verifica la matriz de confusión** para detectar problemas
4. **Mantén los últimos 5 backups** por seguridad
5. **Documenta cambios significativos** en accuracy

---

## ✅ Checklist Rápido

Después de reentrenar:

- [ ] Accuracy >= 90%
- [ ] F1-Score >= 0.85 por clase
- [ ] Gráficas generadas (8 archivos)
- [ ] API reiniciada
- [ ] Prueba de clasificación exitosa
- [ ] Backup guardado

---

## 🎯 TL;DR

```bash
# Cuando entren más niños a la BD:
cd modelo/ml-recomendator
./actualizar_modelo.sh
docker-compose restart

# Listo! 🎉
```
