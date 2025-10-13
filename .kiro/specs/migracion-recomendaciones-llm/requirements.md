# Requirements Document

## Introduction

Este documento define los requisitos para migrar el sistema de recomendaciones nutricionales desde un enfoque basado en modelos de Machine Learning complejos (Random Forest, Neural Networks) hacia un sistema simplificado que utiliza:

1. **Agente LLM (CORA)** - Ya configurado en `.env` para generar recomendaciones personalizadas en lenguaje natural
2. **Procedimientos almacenados** - `sp_top_recetas_por_nombre` para consultar recetas óptimas
3. **Vistas SQL** - `v_recetas_scores_por_nino` y otras vistas para scoring nutricional

El objetivo es eliminar la complejidad del entrenamiento de modelos ML, manteniendo la calidad de las recomendaciones mediante el uso inteligente del LLM combinado con la lógica de negocio en la base de datos.

## Requirements

### Requirement 1: Simplificar la API del servicio ml-recomendator

**User Story:** Como desarrollador del backend, quiero que el servicio `ml-recomendator` solo exponga endpoints basados en LLM y procedimientos almacenados, para eliminar la dependencia de modelos ML entrenados y simplificar el mantenimiento.

#### Acceptance Criteria

1. WHEN se inicia el servicio `ml-recomendator` THEN NO debe intentar cargar modelos ML (Random Forest, Neural Networks)
2. WHEN se consulta el endpoint `/health` THEN debe reportar el estado del LLM y la conexión a BD, pero NO el estado de modelos ML
3. WHEN se elimina código relacionado con modelos ML THEN se deben remover los siguientes componentes:
   - Funciones `load_ml_model()`, `cargar_modelo_directo()`
   - Endpoints `/ml/predict`, `/ml/predict_direct`, `/ml/model_info`
   - Imports de `DirectNutritionClassifier`, `cargar_modelo_directo`
   - Variable global `ML_MODEL`
4. WHEN se mantiene funcionalidad existente THEN los siguientes endpoints deben permanecer sin cambios:
   - `/ml/predict_baz` (cálculo de BAZ usando tablas OMS)
   - `/ml/summary` (resúmenes con LLM)
   - `/ml/chat` (chat con LLM)
   - `/ml/recomendacion_personalizada` (recomendaciones personalizadas)

### Requirement 2: Optimizar el endpoint de recomendaciones personalizadas

**User Story:** Como usuario del sistema, quiero recibir recomendaciones nutricionales personalizadas basadas en el nombre del niño y tipo de comida, para que el sistema use el procedimiento almacenado `sp_top_recetas_por_nombre` y el agente LLM.

#### Acceptance Criteria

1. WHEN se llama a `/ml/recomendacion_personalizada` con `id_nino` y `tipo_comida` THEN debe:
   - Consultar datos del niño desde la tabla `ninos`
   - Ejecutar `sp_top_recetas_por_nombre(nombre_nino, tipo_comida, 5)` para obtener top 5 recetas
   - Construir un prompt detallado con datos del niño, estado nutricional y recetas
   - Enviar el prompt al agente LLM (CORA)
   - Retornar la recomendación en lenguaje natural
2. WHEN el procedimiento `sp_top_recetas_por_nombre` retorna `status='NO_MATCH'` THEN debe informar al usuario que no se encontró el niño
3. WHEN el procedimiento retorna `status='OK'` THEN debe incluir en el prompt:
   - Nombre del niño, edad, sexo, peso, talla, IMC
   - Estado nutricional (`en_clasificacion`)
   - Lista de recetas con: nombre, calorías, proteínas, hierro, fibra, costo, score
4. WHEN el LLM no está disponible THEN debe retornar un mensaje de error amigable sugiriendo consultar con un nutricionista

### Requirement 3: Actualizar la función de consulta de recetas

**User Story:** Como desarrollador, quiero que la función `consultar_recetas_por_nino` use el procedimiento almacenado `sp_top_recetas_por_nombre` correctamente, para aprovechar la lógica de scoring ya implementada en la base de datos.

#### Acceptance Criteria

1. WHEN se llama a `consultar_recetas_por_nino(id_nino, tipo_comida)` THEN debe:
   - Obtener el nombre del niño desde `consultar_datos_nino(id_nino)`
   - Normalizar `tipo_comida` a mayúsculas ('DESAYUNO', 'ALMUERZO', 'CENA')
   - Ejecutar `CALL sp_top_recetas_por_nombre(nombre_nino, tipo_comida, 5)`
   - Parsear los resultados y retornar una lista de diccionarios con las recetas
2. WHEN el procedimiento retorna columnas THEN debe mapear correctamente:
   - `rec_id` → `id`
   - `rec_nombre` → `nombre`
   - `kcal` → `calorias`
   - `proteina_g` → `proteinas`
   - `hierro_mg` → `hierro`
   - `fibra_g` → `fibra`
   - `costo_soles_aprox` → `costo`
   - `score` → `puntuacion`
3. WHEN ocurre un error en la consulta THEN debe retornar una lista vacía y loggear el error

### Requirement 4: Mejorar el prompt para el agente LLM

**User Story:** Como nutricionista virtual (LLM), quiero recibir un prompt estructurado y completo con toda la información relevante del niño y las recetas disponibles, para generar recomendaciones precisas y personalizadas.

#### Acceptance Criteria

1. WHEN se construye el prompt en `crear_prompt_recomendacion()` THEN debe incluir:
   - Sección "DATOS DEL NIÑO" con: nombre, edad en meses, sexo, peso, talla, IMC, estado nutricional, diagnóstico
   - Sección "RECETAS DISPONIBLES" con las top 5 recetas ordenadas por score
   - Para cada receta: nombre, calorías, proteínas, carbohidratos, grasas, fibra, hierro, costo, puntuación
   - Sección "INSTRUCCIONES" con guías claras para el LLM
2. WHEN el usuario proporciona una `pregunta_usuario` THEN debe incluirse en el prompt como "PREGUNTA ESPECÍFICA DEL USUARIO"
3. WHEN NO hay recetas disponibles THEN debe indicar claramente "No hay recetas específicas disponibles" y pedir recomendaciones generales
4. WHEN se envía el prompt al LLM THEN debe usar el `system_message`: "Eres un nutricionista infantil experto. Proporciona recomendaciones seguras, basadas en evidencia científica y apropiadas para la edad del niño."

### Requirement 5: Limpiar archivos y dependencias obsoletas

**User Story:** Como administrador del sistema, quiero eliminar todos los archivos, scripts y dependencias relacionados con el entrenamiento de modelos ML, para reducir la complejidad del proyecto y facilitar el mantenimiento.

#### Acceptance Criteria

1. WHEN se eliminan componentes ML THEN se deben remover los siguientes directorios:
   - `modelo/ml-recomendator/src/models/` (excepto archivos necesarios para BAZ)
   - `modelo/ml-recomendator/src/pipeline/`
   - `modelo/ml-recomendator/src/features/` (excepto `who_calculator.py` si se usa para BAZ)
   - `modelo/ml-recomendator/models/` (modelos entrenados)
   - `modelo/ml-recomendator/data/processed/`
   - `modelo/ml-recomendator/data/interim/`
2. WHEN se eliminan scripts THEN se deben remover:
   - `scripts/entrenar_sin_overfitting.sh`
   - `scripts/rebalancear_y_reentrenar.sh`
   - `scripts/regenerar_datos.sh`
   - `scripts/test_bayesian_rf.py`
   - `scripts/test_clasificacion.py`
   - `scripts/test_modelo_api.py`
   - `scripts/test_modelo_directo.py`
   - `scripts/mejorar_modelo.py`
   - `scripts/balancear_datos.py`
   - `scripts/agregar_variabilidad.py`
   - `scripts/analizar_overfitting.py`
   - `scripts/limpiar_features.py`
   - `scripts/generar_datos_sinteticos.py`
   - `scripts/generar_graficas.py`
   - `scripts/generar_graficas_simple.py`
3. WHEN se actualizan dependencias THEN se deben remover de `requirements.txt`:
   - `scikit-learn`
   - `tensorflow` o `torch` (si existen)
   - `joblib` (si solo se usa para modelos ML)
   - Cualquier librería específica de ML no usada por el LLM
4. WHEN se mantienen componentes THEN se deben conservar:
   - `src/llm/` (cliente LLM y funciones de asistencia)
   - `src/utils/db_connector.py` (conexión a BD)
   - `src/utils/classification_mapper.py` (si se usa para mapear clasificaciones OMS)
   - Scripts de verificación de datos que no dependan de modelos ML

### Requirement 6: Actualizar documentación

**User Story:** Como desarrollador nuevo en el proyecto, quiero que la documentación refleje la arquitectura simplificada basada en LLM, para entender rápidamente cómo funciona el sistema sin confundirme con referencias a modelos ML obsoletos.

#### Acceptance Criteria

1. WHEN se actualiza `README.md` THEN debe:
   - Eliminar referencias a entrenamiento de modelos ML
   - Documentar el uso del agente LLM (CORA)
   - Explicar el flujo: Usuario → API → Procedimiento almacenado → LLM → Respuesta
   - Incluir ejemplos de uso del endpoint `/ml/recomendacion_personalizada`
2. WHEN se actualizan archivos en `docs/` THEN debe:
   - Actualizar `ARQUITECTURA_ML.md` para reflejar la nueva arquitectura sin modelos ML
   - Actualizar `API_ML.md` con los endpoints activos (eliminar endpoints de predicción ML)
   - Actualizar `INTEGRACION_BACKEND.md` con el nuevo flujo de integración
3. WHEN se crea nueva documentación THEN debe incluir:
   - Guía de configuración del agente LLM en `.env`
   - Documentación del procedimiento `sp_top_recetas_por_nombre`
   - Ejemplos de prompts efectivos para el LLM
   - Troubleshooting común (LLM no disponible, BD sin conexión, etc.)

### Requirement 7: Mantener compatibilidad con el endpoint de análisis nutricional

**User Story:** Como usuario del frontend, quiero que el endpoint `/ml/analisis_nutricional` siga funcionando para calcular BAZ y clasificación nutricional, aunque ya no use modelos ML para predicción.

#### Acceptance Criteria

1. WHEN se llama a `/ml/analisis_nutricional` THEN debe:
   - Calcular BMI a partir de peso y talla
   - Calcular BAZ usando tablas OMS (función `_baz_from_bmi`)
   - Clasificar usando la función `_classify_from_baz` (7 categorías OMS)
   - Retornar diagnóstico, IMC, BAZ, percentil, nivel de riesgo
2. WHEN se generan recomendaciones THEN debe usar el LLM para crear recomendaciones personalizadas basadas en el diagnóstico
3. WHEN el modelo ML no está disponible THEN NO debe fallar, sino usar solo el cálculo de BAZ y clasificación basada en reglas
4. IF el campo `modelo_usado` en la respuesta THEN debe ser `false` (ya no se usa modelo ML)

### Requirement 8: Validar integración con el backend principal

**User Story:** Como desarrollador del backend principal (Nutricion-api), quiero que el servicio `ml-recomendator` simplificado funcione correctamente con los endpoints existentes, sin romper la integración actual.

#### Acceptance Criteria

1. WHEN el backend llama a `/ml/recomendacion_personalizada` THEN debe recibir una respuesta válida con:
   - `recomendacion`: string con texto generado por LLM
   - `datos_nino`: objeto con información del niño
   - `recetas_disponibles`: array de recetas
   - `estado_nutricional`: objeto con diagnóstico y métricas
   - `used_llm`: boolean indicando si se usó el LLM
2. WHEN el backend llama a `/ml/predict_baz` THEN debe seguir funcionando sin cambios
3. WHEN el backend llama a endpoints eliminados (`/ml/predict`, `/ml/predict_direct`) THEN debe recibir un error 404
4. WHEN se actualiza la documentación de integración THEN debe reflejar los cambios en `control/Nutricion-api/INTEGRACION_ML.md`
