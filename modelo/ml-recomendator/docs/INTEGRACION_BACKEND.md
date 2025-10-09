# 🔗 Integración con Backend - Reemplazar Procedimientos Almacenados

Guía para migrar de procedimientos almacenados al modelo ML.

---

## 🎯 Objetivo

Reemplazar el flujo actual que usa procedimientos almacenados para calcular estado nutricional con el modelo ML.

### Antes (Procedimientos Almacenados)
```
Frontend → Backend → MySQL Procedure → Tablas OMS → Response
```

### Ahora (Modelo ML)
```
Frontend → Backend → API ML (puerto 8003) → Modelo RF → Response
```

---

## 📡 Nuevo Endpoint

**POST** `/ml/analisis_nutricional`

Este endpoint reemplaza completamente los procedimientos almacenados y retorna exactamente el mismo formato que espera tu frontend.

---

## 🔄 Migración del Backend

### Antes (Node.js/Express con Procedimientos)

```javascript
// Ruta anterior que usaba procedimientos almacenados
router.post('/antropometria', async (req, res) => {
  const { nin_id, peso_kg, talla_cm, fecha } = req.body;
  
  try {
    // Llamar procedimiento almacenado
    const [result] = await db.query(
      'CALL sp_analisis_nutricional(?, ?, ?, ?)',
      [nin_id, peso_kg, talla_cm, fecha]
    );
    
    res.json(result[0]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

### Ahora (Node.js/Express con API ML)

```javascript
const axios = require('axios');

const ML_API_URL = 'http://localhost:8003';

router.post('/antropometria', async (req, res) => {
  const { nin_id, peso_kg, talla_cm, fecha } = req.body;
  
  try {
    // Llamar API ML
    const response = await axios.post(`${ML_API_URL}/ml/analisis_nutricional`, {
      nin_id: nin_id,
      peso_kg: peso_kg,
      talla_cm: talla_cm,
      fecha_medicion: fecha
    });
    
    // El response ya tiene el formato correcto para el frontend
    res.json(response.data);
    
  } catch (error) {
    if (error.response) {
      // Error de la API ML
      res.status(error.response.status).json({
        error: error.response.data.detail || 'Error en análisis nutricional'
      });
    } else {
      // Error de conexión
      res.status(503).json({
        error: 'Servicio ML no disponible'
      });
    }
  }
});
```

---

## 📊 Request y Response

### Request

```json
{
  "nin_id": 202,
  "peso_kg": 45,
  "talla_cm": 150,
  "fecha_medicion": "2025-10-07"
}
```

### Response (Compatible con tu Frontend)

```json
{
  "fecha": "07/10/2025",
  "peso_kg": 45.0,
  "talla_cm": 150.0,
  "imc": 20.0,
  
  "diagnostico": "NORMAL",
  "imc_valor": 20.0,
  "percentil": 60.4,
  "nivel_riesgo": "BAJO",
  "baz": 0.26,
  
  "probabilidad": 0.98,
  "probabilidades": {
    "NORMAL": 0.98,
    "RIESGO": 0.01,
    "MODERADO": 0.01,
    "SEVERO": 0.00
  },
  
  "recomendaciones": [
    {
      "icono": "✅",
      "titulo": "Mantener alimentación balanceada y variada actual",
      "descripcion": "Continuar con 3 comidas principales y 2 meriendas saludables"
    },
    {
      "icono": "🥗",
      "titulo": "Incluir diariamente: frutas, verduras, proteínas, lácteos y cereales integrales",
      "descripcion": "Hidratación adecuada con agua (evitar bebidas azucaradas)"
    },
    {
      "icono": "🏃",
      "titulo": "Fomentar actividad física regular según edad",
      "descripcion": "Limitar consumo de alimentos ultraprocesados y comida rápida"
    },
    {
      "icono": "📅",
      "titulo": "Monitoreo de crecimiento cada 3-6 meses",
      "descripcion": "Mantener buenos hábitos alimenticios y horarios regulares"
    },
    {
      "icono": "💪",
      "titulo": "Promover imagen corporal positiva y autoestima",
      "descripcion": "Educación nutricional para autonomía alimentaria"
    }
  ],
  
  "modelo_usado": true,
  "modelo_version": "v1.0"
}
```

---

## 🎨 Mapeo para el Frontend

Tu frontend ya muestra estos campos, solo necesitas mapear los nombres:

```javascript
// Frontend (React/Vue/Angular)
const analisis = response.data;

// Medición más reciente
const medicion = {
  fecha: analisis.fecha,
  peso: analisis.peso_kg,
  talla: analisis.talla_cm,
  imc: analisis.imc
};

// Estado nutricional
const estado = {
  diagnostico: analisis.diagnostico,  // "NORMAL", "RIESGO", "MODERADO", "SEVERO"
  imc: analisis.imc_valor,
  percentil: analisis.percentil,
  nivelRiesgo: analisis.nivel_riesgo  // "BAJO", "MEDIO", "ALTO"
};

// Recomendaciones (ya vienen en el formato correcto)
const recomendaciones = analisis.recomendaciones;
```

---

## 🔄 Flujo Completo

### 1. Usuario registra peso y talla en el frontend

```javascript
// Frontend
const registrarAntropometria = async (ninId, peso, talla) => {
  const response = await fetch('/api/antropometria', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      nin_id: ninId,
      peso_kg: peso,
      talla_cm: talla,
      fecha: new Date().toISOString().split('T')[0]
    })
  });
  
  const analisis = await response.json();
  mostrarAnalisis(analisis);
};
```

### 2. Backend recibe request y llama a API ML

```javascript
// Backend (Node.js/Express)
router.post('/antropometria', async (req, res) => {
  const { nin_id, peso_kg, talla_cm, fecha } = req.body;
  
  // 1. Guardar antropometría en BD (opcional)
  await db.query(
    'INSERT INTO antropometrias (nin_id, ant_peso_kg, ant_talla_cm, ant_fecha) VALUES (?, ?, ?, ?)',
    [nin_id, peso_kg, talla_cm, fecha]
  );
  
  // 2. Llamar API ML para análisis
  const mlResponse = await axios.post('http://localhost:8003/ml/analisis_nutricional', {
    nin_id,
    peso_kg,
    talla_cm,
    fecha_medicion: fecha
  });
  
  // 3. Retornar análisis al frontend
  res.json(mlResponse.data);
});
```

### 3. Frontend muestra análisis

```javascript
// Frontend
const mostrarAnalisis = (analisis) => {
  // Mostrar diagnóstico
  document.getElementById('diagnostico').textContent = analisis.diagnostico;
  document.getElementById('imc').textContent = analisis.imc;
  document.getElementById('percentil').textContent = `${analisis.percentil}%`;
  document.getElementById('nivel-riesgo').textContent = analisis.nivel_riesgo;
  
  // Mostrar recomendaciones
  const recomendacionesHTML = analisis.recomendaciones.map(rec => `
    <div class="recomendacion">
      <span class="icono">${rec.icono}</span>
      <div>
        <strong>${rec.titulo}</strong>
        <p>${rec.descripcion}</p>
      </div>
    </div>
  `).join('');
  
  document.getElementById('recomendaciones').innerHTML = recomendacionesHTML;
};
```

---

## ⚙️ Configuración

### 1. Variables de Entorno (Backend)

```env
# .env del backend
ML_API_URL=http://localhost:8003
ML_API_TIMEOUT=5000
```

### 2. Manejo de Errores

```javascript
// Backend
const llamarAPIML = async (data) => {
  try {
    const response = await axios.post(
      `${process.env.ML_API_URL}/ml/analisis_nutricional`,
      data,
      { timeout: parseInt(process.env.ML_API_TIMEOUT) }
    );
    return response.data;
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      throw new Error('Servicio ML no disponible. Verifica que esté corriendo en puerto 8003');
    }
    if (error.response?.status === 404) {
      throw new Error('Niño no encontrado');
    }
    if (error.response?.status === 503) {
      throw new Error('Modelo ML no disponible');
    }
    throw error;
  }
};
```

### 3. Fallback a Procedimientos (Opcional)

Si quieres mantener los procedimientos como fallback:

```javascript
router.post('/antropometria', async (req, res) => {
  const { nin_id, peso_kg, talla_cm, fecha } = req.body;
  
  try {
    // Intentar con API ML primero
    const mlResponse = await axios.post('http://localhost:8003/ml/analisis_nutricional', {
      nin_id, peso_kg, talla_cm, fecha_medicion: fecha
    }, { timeout: 3000 });
    
    res.json(mlResponse.data);
    
  } catch (mlError) {
    console.warn('API ML falló, usando procedimientos almacenados:', mlError.message);
    
    // Fallback a procedimientos almacenados
    const [result] = await db.query(
      'CALL sp_analisis_nutricional(?, ?, ?, ?)',
      [nin_id, peso_kg, talla_cm, fecha]
    );
    
    res.json(result[0]);
  }
});
```

---

## 🧪 Testing

### Test con cURL

```bash
curl -X POST http://localhost:8003/ml/analisis_nutricional \
  -H "Content-Type: application/json" \
  -d '{
    "nin_id": 202,
    "peso_kg": 45,
    "talla_cm": 150,
    "fecha_medicion": "2025-10-07"
  }'
```

### Test con Postman

1. **Method**: POST
2. **URL**: `http://localhost:8003/ml/analisis_nutricional`
3. **Headers**: `Content-Type: application/json`
4. **Body** (raw JSON):
```json
{
  "nin_id": 202,
  "peso_kg": 45,
  "talla_cm": 150,
  "fecha_medicion": "2025-10-07"
}
```

---

## 📈 Ventajas del Modelo ML vs Procedimientos

| Aspecto | Procedimientos | Modelo ML |
|---------|---------------|-----------|
| **Accuracy** | Basado en reglas fijas | 93.92% (aprende de datos) |
| **Personalización** | Genérica | Considera historial del niño |
| **Recomendaciones** | Estáticas | Personalizadas por caso |
| **Mantenimiento** | Difícil (SQL complejo) | Fácil (reentrenar modelo) |
| **Escalabilidad** | Limitada | Alta |
| **Interpretabilidad** | Alta | Media-Alta (feature importance) |

---

## 🚀 Pasos para Migrar

1. **Iniciar API ML**
   ```bash
   cd modelo/ml-recomendator
   source venv/bin/activate
   ./run_api.sh
   ```

2. **Actualizar Backend**
   - Instalar axios: `npm install axios`
   - Agregar variable de entorno: `ML_API_URL=http://localhost:8003`
   - Actualizar ruta de antropometría

3. **Probar Integración**
   - Registrar peso/talla desde frontend
   - Verificar que se muestre análisis correcto
   - Verificar recomendaciones

4. **Monitorear**
   - Logs de API ML
   - Tiempos de respuesta
   - Errores

5. **Desactivar Procedimientos** (opcional)
   - Una vez validado, puedes deprecar los procedimientos almacenados

---

## 🆘 Troubleshooting

### Error: "Servicio ML no disponible"
```bash
# Verificar que API ML esté corriendo
curl http://localhost:8003/health

# Si no está corriendo, iniciarla
cd modelo/ml-recomendator && ./run_api.sh
```

### Error: "Modelo ML no disponible"
```bash
# Entrenar modelo
cd modelo/ml-recomendator
./scripts/regenerar_datos.sh
```

### Error: "Niño no encontrado"
- Verificar que el `nin_id` existe en la tabla `ninos`
- Verificar conexión a BD en `.env` de la API ML

---

## 📚 Recursos

- **API Docs**: http://localhost:8003/docs
- **Documentación Completa**: `docs/API_ML.md`
- **Inicio Rápido**: `INICIO_RAPIDO.md`

---

**¿Necesitas ayuda?** Revisa los logs de la API ML o consulta la documentación completa.
