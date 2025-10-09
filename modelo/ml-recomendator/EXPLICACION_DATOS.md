# 📊 Explicación de Cómo se Generan los Datos

## 🤔 ¿De dónde salieron los ~500 datos?

Actualmente el script `generar_datos_desde_oms.py` hace **2 cosas**:

### 1️⃣ Genera Datos SINTÉTICOS (5000 por defecto)
```python
# Genera niños "ficticios" pero realistas
df_sintetico = generar_datos_oms(n_samples=5000)
```

**¿Cómo?**
- Lee las tablas OMS (`oms_bmi_lms`) de tu BD MySQL
- Genera niños con medidas realistas según estándares OMS
- Calcula BAZ correctamente
- Distribuye balanceadamente entre las 7 categorías

**¿Por qué?**
- Para tener suficientes datos de entrenamiento
- Para balancear categorías (ej: si tienes pocos casos de obesidad)
- Para que el modelo aprenda patrones generales

---

### 2️⃣ Extrae Datos REALES de tu BD MySQL
```python
# Extrae niños reales de tu BD
df_real = extraer_datos_reales()
```

**¿Qué extrae?**
- Niños de la tabla `ninos`
- Mediciones de `antropometrias`
- Features de `features_ml` (si existe)
- Clasificaciones de `evaluaciones_nutricionales` (si existe)

**¿Cuántos?**
- Depende de cuántos niños tengas en tu BD
- Si tienes 10 niños → ~10-50 registros (según mediciones)
- Si tienes 100 niños → ~100-500 registros

---

### 3️⃣ Combina Ambos
```python
# Mezcla sintéticos + reales
df_combined = combinar_datos(df_sintetico, df_real)
```

**Resultado:**
- ~5000 sintéticos + tus datos reales
- Total: ~5000-5500 registros
- Guardado en: `datos_completos_oms_reales.csv`

---

## 🎯 ¿Qué Deberías Usar?

### Opción A: SOLO Datos Reales (Recomendado si tienes 100+ niños)

```bash
cd modelo/ml-recomendator
python scripts/generar_solo_datos_reales.py
```

**Ventajas:**
- ✅ Modelo aprende de TUS datos reales
- ✅ Más preciso para tu población específica
- ✅ No hay datos "inventados"

**Desventajas:**
- ❌ Necesitas al menos 100 registros
- ❌ Puede estar desbalanceado (muchos normales, pocos obesos)

---

### Opción B: Datos Reales + Sintéticos (Recomendado si tienes pocos datos)

```bash
cd modelo/ml-recomendator
python scripts/generar_datos_desde_oms.py --solo-reales
```

O para generar menos sintéticos:
```bash
python scripts/generar_datos_desde_oms.py --samples 1000
```

**Ventajas:**
- ✅ Funciona aunque tengas pocos datos reales
- ✅ Dataset balanceado
- ✅ Modelo más robusto

**Desventajas:**
- ❌ Incluye datos "inventados"
- ❌ Puede ser menos preciso para tu población

---

## 📋 Comandos Útiles

### Ver cuántos datos reales tienes
```bash
cd modelo/ml-recomendator
python -c "
from src.utils import DatabaseConnector
db = DatabaseConnector.from_env()
db.connect()
result = db.execute_query('SELECT COUNT(*) as total FROM ninos')
print(f'Niños en BD: {result.iloc[0][\"total\"]}')
result = db.execute_query('SELECT COUNT(*) as total FROM antropometrias')
print(f'Mediciones: {result.iloc[0][\"total\"]}')
db.disconnect()
"
```

---

### Generar SOLO datos reales (sin sintéticos)
```bash
cd modelo/ml-recomendator
python scripts/generar_solo_datos_reales.py
```

---

### Generar datos reales + 1000 sintéticos
```bash
cd modelo/ml-recomendator
python scripts/generar_datos_desde_oms.py --samples 1000
```

---

### Generar SOLO sintéticos (para testing)
```bash
cd modelo/ml-recomendator
python scripts/generar_datos_desde_oms.py --samples 5000
# Luego borra los datos reales del CSV manualmente
```

---

## 🔍 Verificar qué datos tienes

```bash
cd modelo/ml-recomendator

# Ver total de registros
wc -l data/raw/surveys/datos_completos_oms_reales.csv

# Ver distribución de categorías
python -c "
import pandas as pd
df = pd.read_csv('data/raw/surveys/datos_completos_oms_reales.csv')
print(f'Total registros: {len(df)}')
print('\nDistribución:')
print(df['label_name'].value_counts().sort_index())
"
```

---

## 💡 Recomendaciones

### Si tienes MENOS de 50 niños:
```bash
# Usa sintéticos + reales
python scripts/generar_datos_desde_oms.py --samples 3000
```

### Si tienes 50-100 niños:
```bash
# Usa sintéticos + reales (menos sintéticos)
python scripts/generar_datos_desde_oms.py --samples 1000
```

### Si tienes MÁS de 100 niños:
```bash
# Usa SOLO datos reales
python scripts/generar_solo_datos_reales.py
```

---

## 🚨 Importante sobre MySQL

El script ya está configurado para **MySQL** (no PostgreSQL).

Usa `TIMESTAMPDIFF` que es la función de MySQL para calcular diferencias de fechas.

Si tienes problemas de conexión, verifica tu `.env`:
```bash
cat modelo/ml-recomendator/.env
```

Debe tener:
```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=tu_base_datos
DB_USER=tu_usuario
DB_PASSWORD=tu_password
```

---

## 📊 Flujo Completo Recomendado

### 1. Generar datos (elige uno):
```bash
# Opción A: Solo reales
python scripts/generar_solo_datos_reales.py

# Opción B: Reales + sintéticos
python scripts/generar_datos_desde_oms.py --samples 1000
```

### 2. Verificar datos generados:
```bash
python -c "
import pandas as pd
df = pd.read_csv('data/raw/surveys/datos_completos_oms_reales.csv')
print(f'Total: {len(df)} registros')
print(df['label_name'].value_counts())
"
```

### 3. Entrenar modelo:
```bash
python src/pipeline/train_model.py
```

### 4. Verificar modelo:
```bash
python scripts/test_clasificacion.py
```

### 5. Generar gráficas:
```bash
./generar_graficas.sh
```

---

## 🎓 Resumen Ejecutivo

**¿De dónde vienen los ~500 datos?**
- Combinación de datos sintéticos (generados con OMS) + tus datos reales de MySQL

**¿Qué hacer si entran más niños?**
1. Regenerar datos: `python scripts/generar_solo_datos_reales.py`
2. Reentrenar modelo: `python src/pipeline/train_model.py`
3. Reiniciar API: `docker-compose restart`

**¿Usar sintéticos o solo reales?**
- **Menos de 100 niños** → Usa sintéticos + reales
- **Más de 100 niños** → Usa solo reales

**¿Cada cuánto actualizar?**
- Cada vez que agregues 50+ niños nuevos
- O semanalmente si usas el sistema activamente
