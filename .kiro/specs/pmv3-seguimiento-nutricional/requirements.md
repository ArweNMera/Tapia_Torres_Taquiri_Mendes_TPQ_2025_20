# Requirements Document - PMV3: Seguimiento y Monitoreo Nutricional

## Introduction

El PMV3 (Producto Mínimo Viable 3) implementa el sistema de seguimiento y monitoreo nutricional continuo para niños. Este sistema permite registrar adherencia a planes nutricionales, visualizar evolución antropométrica, generar reportes exportables y predecir evolución nutricional futura mediante Machine Learning.

El sistema trabaja completamente con procedimientos almacenados en MySQL para garantizar consistencia, performance y centralización de la lógica de negocio.

## Glossary

- **Sistema**: El sistema de seguimiento y monitoreo nutricional PMV3
- **Tutor**: Usuario responsable del cuidado del niño que registra adherencia
- **Nutricionista**: Profesional de salud que supervisa y valida el seguimiento
- **Adherencia**: Grado de cumplimiento del plan nutricional por parte del niño
- **Antropometría**: Mediciones físicas del niño (peso, talla)
- **Evolución Nutricional**: Cambios en el estado nutricional del niño a lo largo del tiempo
- **Predicción ML**: Estimación del estado nutricional futuro usando Machine Learning
- **Reporte PDF**: Documento exportable con información del seguimiento
- **Panel de Seguimiento**: Interfaz visual con gráficos comparativos de evolución
- **Procedimiento Almacenado**: Función SQL ejecutada en el servidor de base de datos
- **Feature ML**: Característica calculada para el modelo de Machine Learning
- **Z-Score (BAZ)**: Puntuación estandarizada del IMC según OMS

## Requirements

### Requirement 1: Registro de Adherencia

**User Story:** Como tutor, quiero registrar diariamente si mi hijo cumplió con su plan nutricional, para que el sistema pueda monitorear su progreso

#### Acceptance Criteria

1. WHEN el tutor registra adherencia para un día específico THEN el sistema SHALL almacenar el estado (OK/PARCIAL/NO), porcentaje de cumplimiento, y comentarios opcionales
2. WHEN el tutor registra adherencia THEN el sistema SHALL asociar el registro con el menú activo del niño para esa fecha
3. WHEN el tutor intenta registrar adherencia para una fecha futura THEN el sistema SHALL rechazar el registro y mostrar un mensaje de error
4. WHEN el tutor registra adherencia THEN el sistema SHALL permitir indicar el nivel de dificultad experimentado (NINGUNA/BAJA/MEDIA/ALTA)
5. WHEN el tutor actualiza un registro de adherencia existente THEN el sistema SHALL preservar el historial de cambios mediante actualización de timestamp

### Requirement 2: Registro de Síntomas

**User Story:** Como tutor, quiero registrar síntomas que presenta mi hijo, para que el nutricionista pueda identificar posibles problemas relacionados con la alimentación

#### Acceptance Criteria

1. WHEN el tutor registra un síntoma THEN el sistema SHALL almacenar tipo, fecha, severidad (LEVE/MODERADO/SEVERO), duración en días y notas descriptivas
2. WHEN el tutor registra un síntoma THEN el sistema SHALL permitir indicar si está relacionado con el menú consumido
3. WHEN el sistema detecta síntomas frecuentes (más de 3 en 7 días) THEN el sistema SHALL generar una alerta automática para el nutricionista
4. WHEN el tutor consulta síntomas históricos THEN el sistema SHALL mostrar los síntomas ordenados por fecha descendente con filtros por tipo y severidad
5. WHEN el nutricionista revisa síntomas THEN el sistema SHALL calcular y mostrar la frecuencia y severidad promedio de los últimos 30 días

### Requirement 3: Visualización de Evolución Nutricional

**User Story:** Como nutricionista, quiero visualizar gráficamente la evolución del peso, talla y adherencia del niño, para evaluar la efectividad del tratamiento

#### Acceptance Criteria

1. WHEN el nutricionista accede al panel de seguimiento THEN el sistema SHALL mostrar gráficos de línea para peso, talla e IMC con datos de los últimos 6 meses
2. WHEN el sistema muestra gráficos de evolución THEN el sistema SHALL incluir líneas de referencia de percentiles OMS (P3, P15, P50, P85, P97)
3. WHEN el sistema muestra evolución de adherencia THEN el sistema SHALL presentar un gráfico de barras con porcentajes semanales de cumplimiento
4. WHEN el usuario selecciona un punto en el gráfico THEN el sistema SHALL mostrar detalles completos de esa medición en un tooltip
5. WHEN el sistema detecta tendencias negativas (3 mediciones consecutivas empeorando) THEN el sistema SHALL resaltar visualmente la zona de riesgo en el gráfico

### Requirement 4: Generación de Reportes PDF

**User Story:** Como nutricionista, quiero generar reportes PDF del seguimiento nutricional, para compartirlos en consultas clínicas o con otros profesionales

#### Acceptance Criteria

1. WHEN el nutricionista solicita un reporte PDF THEN el sistema SHALL generar un documento que incluya datos del niño, gráficos de evolución, tabla de mediciones y recomendaciones
2. WHEN el sistema genera un reporte PDF THEN el sistema SHALL incluir el rango de fechas seleccionado y la fecha de generación del reporte
3. WHEN el reporte PDF se genera THEN el sistema SHALL incluir interpretación automática de tendencias (mejorando/estable/empeorando)
4. WHEN el reporte incluye gráficos THEN el sistema SHALL renderizar los gráficos como imágenes embebidas en el PDF
5. WHEN el reporte se descarga THEN el sistema SHALL nombrar el archivo con formato "Reporte_[NombreNiño]_[Fecha].pdf"

### Requirement 5: Predicción de Evolución Nutricional con ML

**User Story:** Como nutricionista, quiero que el sistema prediga el estado nutricional futuro del niño, para tomar decisiones preventivas tempranas

#### Acceptance Criteria

1. WHEN el sistema calcula una predicción ML THEN el sistema SHALL usar el modelo Random Forest entrenado (rf_model.pkl) con 11 features contextuales
2. WHEN el sistema genera una predicción THEN el sistema SHALL clasificar en 7 categorías OMS (DESNUTRICION_SEVERA, DESNUTRICION_MODERADA, RIESGO_DESNUTRICION, NORMAL, RIESGO_SOBREPESO, SOBREPESO, OBESIDAD)
3. WHEN el sistema predice el estado futuro THEN el sistema SHALL calcular probabilidades para cada categoría y retornar la de mayor confianza
4. WHEN la predicción indica categorías de riesgo (DESNUTRICION_SEVERA, DESNUTRICION_MODERADA, OBESIDAD) THEN el sistema SHALL generar una alerta temprana visible en el dashboard del nutricionista
5. WHEN el nutricionista revisa una predicción THEN el sistema SHALL mostrar los top 5 features más importantes que influyen en la predicción

### Requirement 6: Cálculo Automático de Features ML

**User Story:** Como sistema, quiero calcular automáticamente las 11 características ML cuando se registran nuevas mediciones, para mantener predicciones actualizadas

#### Acceptance Criteria

1. WHEN se registra una nueva antropometría THEN el sistema SHALL calcular automáticamente los 11 features requeridos por el modelo Random Forest
2. WHEN el sistema calcula features ML THEN el sistema SHALL incluir features antropométricos (age_months, sex_numeric, BMI, weight_kg, height_cm)
3. WHEN el sistema calcula features ML THEN el sistema SHALL incluir velocidades de cambio (bmi_velocity, weight_velocity, height_velocity) de los últimos 3 meses
4. WHEN el sistema calcula features ML THEN el sistema SHALL incluir métricas de adherencia (adherence_score) de los últimos 30 días
5. WHEN el sistema calcula features ML THEN el sistema SHALL incluir información contextual (allergy_count, altitude_m) del niño y su entidad

### Requirement 7: Panel de Seguimiento con Gráficos Comparativos

**User Story:** Como nutricionista, quiero ver un panel consolidado con todos los indicadores del niño, para tener una visión integral de su progreso

#### Acceptance Criteria

1. WHEN el nutricionista accede al panel de seguimiento THEN el sistema SHALL mostrar tarjetas resumen con última medición, clasificación actual y tendencia
2. WHEN el panel muestra tendencias THEN el sistema SHALL usar indicadores visuales (flechas arriba/abajo, colores verde/amarillo/rojo) según la dirección del cambio
3. WHEN el panel incluye gráficos comparativos THEN el sistema SHALL permitir comparar hasta 3 métricas simultáneamente en el mismo gráfico
4. WHEN el usuario interactúa con el panel THEN el sistema SHALL permitir seleccionar rangos de fechas personalizados (última semana/mes/trimestre/año)
5. WHEN el panel se carga THEN el sistema SHALL obtener todos los datos mediante procedimientos almacenados para garantizar consistencia

### Requirement 8: Validación de Predicciones por Nutricionista

**User Story:** Como nutricionista, quiero validar o corregir las predicciones del modelo ML, para mejorar su precisión con el tiempo

#### Acceptance Criteria

1. WHEN el nutricionista revisa una predicción ML THEN el sistema SHALL permitir marcarla como validada o rechazada con comentarios
2. WHEN el nutricionista valida una predicción THEN el sistema SHALL almacenar el usr_id del validador y timestamp mediante procedimiento almacenado
3. WHEN el nutricionista rechaza una predicción THEN el sistema SHALL solicitar feedback obligatorio sobre por qué fue incorrecta
4. WHEN se acumulan validaciones THEN el sistema SHALL permitir re-entrenar el modelo usando el script de entrenamiento actualizado
5. WHEN el sistema muestra predicciones THEN el sistema SHALL indicar visualmente cuáles han sido validadas por un profesional y mostrar el accuracy actual del modelo (90.18%)

### Requirement 9: Alertas Tempranas Automáticas

**User Story:** Como nutricionista, quiero recibir alertas automáticas cuando un niño muestre signos de deterioro, para intervenir oportunamente

#### Acceptance Criteria

1. WHEN el sistema detecta 3 mediciones consecutivas con tendencia negativa THEN el sistema SHALL generar una alerta de "Tendencia Negativa"
2. WHEN la adherencia promedio cae por debajo del 60% en 2 semanas THEN el sistema SHALL generar una alerta de "Baja Adherencia"
3. WHEN una predicción ML indica riesgo SEVERO THEN el sistema SHALL generar una alerta de "Riesgo Crítico Detectado"
4. WHEN se registran más de 5 síntomas en 7 días THEN el sistema SHALL generar una alerta de "Síntomas Frecuentes"
5. WHEN se genera una alerta THEN el sistema SHALL notificar al nutricionista asignado mediante la tabla notificaciones

### Requirement 10: Integración con Procedimientos Almacenados

**User Story:** Como desarrollador, quiero que toda la lógica de negocio esté en procedimientos almacenados, para garantizar consistencia y performance

#### Acceptance Criteria

1. WHEN el backend necesita registrar adherencia THEN el sistema SHALL ejecutar sp_registrar_adherencia con parámetros validados
2. WHEN el backend necesita obtener evolución THEN el sistema SHALL ejecutar sp_obtener_evolucion_nutricional con filtros de fecha
3. WHEN el backend necesita calcular features ML THEN el sistema SHALL ejecutar sp_calcular_features_ml y retornar el resultado
4. WHEN el backend necesita generar predicción THEN el sistema SHALL ejecutar sp_obtener_datos_para_ml y procesar con el modelo Python
5. WHEN un procedimiento almacenado falla THEN el sistema SHALL propagar el error con SIGNAL SQLSTATE y mensaje descriptivo

### Requirement 11: Exportación de Datos para Análisis

**User Story:** Como nutricionista, quiero exportar datos de seguimiento en formato CSV, para realizar análisis estadísticos externos

#### Acceptance Criteria

1. WHEN el nutricionista solicita exportación CSV THEN el sistema SHALL generar un archivo con todas las mediciones del niño en el rango seleccionado
2. WHEN el CSV se genera THEN el sistema SHALL incluir columnas: fecha, peso, talla, IMC, z-score, adherencia, síntomas
3. WHEN el CSV incluye datos sensibles THEN el sistema SHALL anonimizar el nombre del niño usando un ID único
4. WHEN la exportación se completa THEN el sistema SHALL registrar la acción en eventos_auditoria para trazabilidad
5. WHEN el archivo CSV se descarga THEN el sistema SHALL usar codificación UTF-8 con BOM para compatibilidad con Excel

### Requirement 12: Historial de Cambios en Adherencia

**User Story:** Como nutricionista, quiero ver el historial completo de registros de adherencia, para identificar patrones de cumplimiento

#### Acceptance Criteria

1. WHEN el nutricionista consulta historial de adherencia THEN el sistema SHALL mostrar todos los registros ordenados por fecha descendente
2. WHEN el historial muestra registros THEN el sistema SHALL incluir estado, porcentaje, dificultad, comentarios y fecha de registro
3. WHEN el historial se filtra THEN el sistema SHALL permitir filtrar por rango de fechas, estado y nivel de dificultad
4. WHEN el historial se visualiza THEN el sistema SHALL calcular y mostrar estadísticas agregadas (adherencia promedio, días con dificultad alta)
5. WHEN el historial incluye comentarios del tutor THEN el sistema SHALL resaltar aquellos que mencionan problemas o efectos adversos
