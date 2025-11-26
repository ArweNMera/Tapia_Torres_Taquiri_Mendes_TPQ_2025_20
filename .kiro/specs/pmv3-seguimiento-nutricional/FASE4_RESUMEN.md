# Fase 4: Frontend - Análisis de Riesgos

## ✅ Backend Completado

### 1. Servidor ML (modelo/ml-recomendator)
- ✅ Endpoint `/api/v1/nutritional/extract_csv` - Extrae CSV desde BD
- ✅ Endpoint `/api/v1/nutritional/train` - Entrena modelo
- ✅ Endpoint `/api/v1/nutritional/metrics` - Obtiene métricas
- ✅ Endpoint `/api/v1/nutritional/generate_plots` - Genera gráficas
- ✅ Endpoint `/api/v1/nutritional/predict` - Predicción nutricional
- ✅ Notebook Colab para entrenamiento

### 2. Backend Principal (control/Nutricion-api)
- ✅ Endpoint `/api/v1/predicciones/generar/{nin_id}` - Genera predicción con proyección 1-6 meses
- ✅ Integración con servidor ML
- ✅ Proyección de features a futuro
- ✅ Guardado en BD con procedimientos almacenados

## 📋 Frontend Pendiente

### Pantalla: Análisis de Riesgos

**Ubicación:** `vista/AppSaludable/src/components/screens/RiskAnalysisScreen.tsx`

#### Componentes Necesarios:

1. **Lista de Niños** (similar a Datos Clínicos)
   - Tabla con niños del nutricionista
   - Columnas: Nombre, Edad, Última medición, Estado actual, Acciones
   - Filtros: Por estado nutricional, por riesgo
   - Búsqueda por nombre

2. **Modales de Acciones:**

   a) **AdherenciaModal.tsx**
   - Formulario para registrar adherencia
   - Selector de fecha
   - Estado: OK/PARCIAL/NO
   - Porcentaje (slider 0-100%)
   - Dificultad: NINGUNA/BAJA/MEDIA/ALTA
   - Comentarios
   - API: `POST /api/v1/adherencia/registrar`

   b) **SintomasModal.tsx**
   - Formulario para registrar síntomas
   - Selector de fecha
   - Tipo de síntoma (input text)
   - Severidad: LEVE/MODERADO/SEVERO
   - Duración en días
   - ¿Relacionado con menú? (checkbox)
   - Notas
   - API: `POST /api/v1/sintomas/registrar`

   c) **PrediccionModal.tsx**
   - Selector de meses a proyectar (1-6)
   - Botón "Generar Predicción"
   - Mostrar resultado:
     - Clasificación predicha
     - Probabilidad
     - Score de riesgo
     - Gráfico de probabilidades por clase
     - Features más importantes
   - API: `POST /api/v1/predicciones/generar/{nin_id}?meses_proyeccion=X`

   d) **PerfilNutricionalModal.tsx** (reutilizar del Plan de Comidas)
   - Mostrar perfil nutricional actual
   - Alergias
   - Comidas favoritas
   - Preferencias

3. **Historial de Predicciones**
   - Lista de predicciones anteriores
   - Fecha, clasificación, probabilidad
   - Validación por nutricionista
   - API: `GET /api/v1/predicciones/nino/{nin_id}`

### Pantalla: Progreso (Evolución)

**Ubicación:** `vista/AppSaludable/src/components/screens/ProgressScreen.tsx`

#### Componentes Necesarios:

1. **Selector de Niño**
   - Dropdown con niños del nutricionista

2. **Gráficos de Evolución**
   - Gráfico de Peso vs Tiempo
   - Gráfico de Talla vs Tiempo
   - Gráfico de IMC vs Tiempo
   - Gráfico de Z-Score vs Tiempo
   - Líneas de referencia OMS
   - API: `GET /api/v1/evolucion/nino/{nin_id}`

3. **Indicadores de Tendencia**
   - Tendencia: MEJORANDO/ESTABLE/EMPEORANDO
   - Velocidades de cambio
   - API: `GET /api/v1/evolucion/nino/{nin_id}/tendencia`

4. **Historial de Adherencia**
   - Gráfico de barras con adherencia diaria
   - Promedio de adherencia
   - API: `GET /api/v1/adherencia/nino/{nin_id}`

5. **Historial de Síntomas**
   - Lista de síntomas recientes
   - Frecuencia de síntomas
   - API: `GET /api/v1/sintomas/nino/{nin_id}`

## 🎨 Diseño UI

### Análisis de Riesgos
```
┌─────────────────────────────────────────────────────┐
│ Análisis de Riesgos                                 │
│ Predicción de riesgos nutricionales                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│ [Buscar...] [Filtro: Todos ▼] [Estado: Todos ▼]   │
│                                                      │
│ ┌──────────────────────────────────────────────┐   │
│ │ Nombre    │ Edad │ Última │ Estado │ Acciones│   │
│ ├──────────────────────────────────────────────┤   │
│ │ Juan P.   │ 8a   │ 15/01  │ NORMAL │ [Botones]│   │
│ │ María G.  │ 10a  │ 10/01  │ RIESGO │ [Botones]│   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ Botones por niño:                                   │
│ [📊 Adherencia] [🩺 Síntomas] [🔮 Predicción]      │
│ [👤 Perfil]                                         │
└─────────────────────────────────────────────────────┘
```

### Modal de Predicción
```
┌─────────────────────────────────────────────────────┐
│ Predicción Nutricional - Juan Pérez                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Proyectar a: [1 mes ▼] [2 meses] [3 meses] ...     │
│                                                      │
│ [Generar Predicción]                                │
│                                                      │
│ ┌──────────────────────────────────────────────┐   │
│ │ Resultado:                                    │   │
│ │                                               │   │
│ │ Clasificación: RIESGO_DESNUTRICION           │   │
│ │ Probabilidad: 65%                            │   │
│ │ Score de Riesgo: 0.45                        │   │
│ │                                               │   │
│ │ [Gráfico de barras con probabilidades]       │   │
│ │                                               │   │
│ │ Features más importantes:                     │   │
│ │ 1. BMI: 15.2                                 │   │
│ │ 2. Adherencia: 55%                           │   │
│ │ 3. Velocidad BMI: -0.3                       │   │
│ └──────────────────────────────────────────────┘   │
│                                                      │
│ [Cerrar] [Guardar]                                  │
└─────────────────────────────────────────────────────┘
```

## 📦 Librerías Necesarias

```json
{
  "recharts": "^2.10.0",  // Gráficos
  "date-fns": "^3.0.0",   // Manejo de fechas
  "react-hook-form": "^7.49.0",  // Formularios
  "zod": "^3.22.0"  // Validación
}
```

## 🔗 APIs a Integrar

### Adherencia
- `POST /api/v1/adherencia/registrar`
- `GET /api/v1/adherencia/nino/{nin_id}`
- `GET /api/v1/adherencia/nino/{nin_id}/promedio`

### Síntomas
- `POST /api/v1/sintomas/registrar`
- `GET /api/v1/sintomas/nino/{nin_id}`
- `GET /api/v1/sintomas/nino/{nin_id}/frecuencia`

### Predicciones
- `POST /api/v1/predicciones/generar/{nin_id}?meses_proyeccion=X`
- `GET /api/v1/predicciones/nino/{nin_id}`
- `POST /api/v1/predicciones/{pml_id}/validar`

### Evolución
- `GET /api/v1/evolucion/nino/{nin_id}`
- `GET /api/v1/evolucion/nino/{nin_id}/tendencia`

### Alertas
- `POST /api/v1/alertas/verificar/{nin_id}`

## ✅ Checklist de Implementación

### Backend
- [x] Servidor ML con endpoints de entrenamiento
- [x] Endpoint de predicción en servidor ML
- [x] Integración backend principal con servidor ML
- [x] Proyección de features a futuro (1-6 meses)
- [x] Notebook Colab para entrenamiento

### Frontend
- [ ] Pantalla RiskAnalysisScreen
- [ ] Componente lista de niños
- [ ] Modal AdherenciaModal
- [ ] Modal SintomasModal
- [ ] Modal PrediccionModal
- [ ] Reutilizar PerfilNutricionalModal
- [ ] Pantalla ProgressScreen
- [ ] Gráficos de evolución (Recharts)
- [ ] Historial de adherencia
- [ ] Historial de síntomas
- [ ] Integración con APIs
- [ ] Manejo de errores
- [ ] Loading states
- [ ] Validación de formularios

## 🚀 Próximos Pasos

1. Instalar dependencias en frontend
2. Crear tipos TypeScript para las APIs
3. Implementar RiskAnalysisScreen con lista de niños
4. Implementar modales uno por uno
5. Implementar ProgressScreen con gráficos
6. Testing e2e
7. Ajustes de UI/UX

## 📝 Notas

- El backend ya está 100% listo
- El modelo ML se entrena desde Colab
- Las predicciones se hacen con proyección a futuro
- Los procedimientos almacenados ya están implementados
- Solo falta el frontend para completar la Fase 4
