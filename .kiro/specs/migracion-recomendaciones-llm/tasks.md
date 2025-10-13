# Implementation Plan

- [x] 1. Preparar el entorno y hacer backup
  - Crear rama git para la migración
  - Hacer backup de `modelo/ml-recomendator/app/main.py`
  - Verificar que el procedimiento `sp_top_recetas_por_nombre` existe en BD
  - Verificar que las vistas SQL están creadas
  - _Requirements: 5, 8_

- [x] 2. Mejorar el conector de base de datos
  - [x] 2.1 Modificar `execute_query` para soportar parámetros
    - Agregar parámetro `params: tuple = None` a la firma
    - Pasar `params` a `pd.read_sql()` en ambas ramas (engine y connection)
    - _Requirements: 3.2_
  
  - [x] 2.2 Verificar método `call_procedure` existe y funciona
    - Si no existe, agregarlo según el diseño
    - Probar con `sp_top_recetas_por_nombre`
    - _Requirements: 3.1_

- [x] 3. Actualizar configuración del LLM
  - [x] 3.1 Modificar `.env` para aumentar tokens
    - Cambiar `LLM_MAX_TOKENS` de 256 a 512
    - Verificar que `LLM_TEMPERATURE=0.2`
    - _Requirements: 4.4_
  
  - [x] 3.2 Verificar cliente LLM funciona
    - Ejecutar test simple de conexión
    - Verificar que retorna respuestas coherentes
    - _Requirements: 1.4, 4.4_

- [x] 4. Modificar `main.py` - Eliminar código de modelos ML
  - [x] 4.1 Eliminar imports de modelos ML
    - Remover `from src.models.direct_classifier import ...`
    - Remover imports de features engineering si existen
    - _Requirements: 1.3_
  
  - [x] 4.2 Eliminar variable global `ML_MODEL` y función `load_ml_model()`
    - Comentar o eliminar `ML_MODEL = None`
    - Eliminar función `load_ml_model()` completa
    - Eliminar llamada `load_ml_model()`
    - _Requirements: 1.3_
  
  - [x] 4.3 Actualizar endpoint `/health`
    - Eliminar `ml_model_loaded` del response
    - Agregar `llm_available` verificando `get_llm_client()`
    - Agregar `db_available` verificando `DatabaseConnector`
    - _Requirements: 1.2_
  
  - [x] 4.4 Eliminar endpoints de predicción ML
    - Eliminar `@app.post("/ml/predict")`
    - Eliminar `@app.post("/ml/predict_direct")`
    - Eliminar `@app.get("/ml/model_info")`
    - Eliminar `@app.post("/ml/analisis_nutricional")` si depende de ML_MODEL
    - Eliminar clases Pydantic asociadas: `PredictMLRequest`, `PredictMLResponse`, `PredictMLDirectRequest`
    - _Requirements: 1.3_


- [x] 5. Modificar `main.py` - Mejorar funciones de consulta
  - [x] 5.1 Reescribir `consultar_recetas_por_nino`
    - Obtener nombre del niño desde `consultar_datos_nino()`
    - Normalizar `tipo_comida` a mayúsculas
    - Ejecutar `CALL sp_top_recetas_por_nombre(nombre, tipo_comida, 5)`
    - Verificar `status` en resultado
    - Parsear recetas con mapeo correcto de columnas
    - Retornar lista vacía en caso de error
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 5.2 Mejorar `crear_prompt_recomendacion`
    - Incluir todas las columnas nutricionales de las recetas
    - Agregar costo aproximado en el prompt
    - Mejorar formato para mejor legibilidad
    - Incluir instrucciones más detalladas para el LLM
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 5.3 Mejorar `consultar_agente_llm`
    - Actualizar `system_message` con contexto peruano
    - Agregar manejo de respuestas vacías o muy cortas
    - Mejorar logging de errores
    - _Requirements: 4.4_

- [x] 6. Agregar logging en funciones críticas
  - Agregar `import logging` y `logger = logging.getLogger(__name__)`
  - Agregar logs en `consultar_recetas_por_nino` (info, warning, error)
  - Agregar logs en `consultar_agente_llm` (info, error)
  - Agregar logs en endpoint `/ml/recomendacion_personalizada`
  - _Requirements: 2.4_

- [x] 7. Eliminar archivos y directorios obsoletos
  - [x] 7.1 Eliminar directorios de modelos ML
    - Eliminar `modelo/ml-recomendator/src/models/` (completo)
    - Eliminar `modelo/ml-recomendator/src/pipeline/` (completo)
    - Eliminar `modelo/ml-recomendator/models/` (modelos entrenados)
    - _Requirements: 5.1_
  
  - [x] 7.2 Eliminar directorio de features (parcial)
    - Verificar si `src/features/who_calculator.py` se usa en `main.py`
    - Si NO se usa, eliminar `modelo/ml-recomendator/src/features/` completo
    - Si SÍ se usa, mantener solo `who_calculator.py` y eliminar el resto
    - _Requirements: 5.1_
  
  - [x] 7.3 Eliminar scripts de entrenamiento
    - Eliminar todos los scripts listados en el diseño (sección "Archivos a eliminar")
    - Mantener solo: `test_conexion.py`, `verificar_datos.py`, `generar_datos_desde_oms.py`
    - _Requirements: 5.2_
  
  - [x] 7.4 Eliminar directorios de datos procesados
    - Eliminar `modelo/ml-recomendator/data/processed/`
    - Eliminar `modelo/ml-recomendator/data/interim/`
    - Mantener `data/raw/who/` y `data/raw/surveys/`
    - _Requirements: 5.2_
  
  - [x] 7.5 Eliminar configuraciones y reportes de ML
    - Eliminar `modelo/ml-recomendator/configs/` (completo)
    - Eliminar `modelo/ml-recomendator/reports/` (completo)
    - _Requirements: 5.2_

- [x] 8. Actualizar dependencias
  - [x] 8.1 Modificar `requirements.txt`
    - Eliminar: `scikit-learn`, `tensorflow`, `torch`, `keras`, `xgboost`, `lightgbm`
    - Verificar si `joblib` se usa solo para ML, si es así eliminarlo
    - Mantener: `fastapi`, `uvicorn`, `pydantic`, `pandas`, `pymysql`, `sqlalchemy`, `httpx`, `python-dotenv`
    - _Requirements: 5.3_
  
  - [x] 8.2 Reinstalar dependencias
    - Ejecutar `pip install -r requirements.txt` en el entorno virtual
    - Verificar que no hay errores de importación
    - _Requirements: 5.3_


- [x] 9. Probar el servicio localmente
  - [x] 9.1 Iniciar el servicio
    - Ejecutar `uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload`
    - Verificar que inicia sin errores
    - Verificar logs de inicio (no debe intentar cargar modelos ML)
    - _Requirements: 1.1_
  
  - [x] 9.2 Probar endpoint `/health`
    - Ejecutar `curl http://localhost:8003/health`
    - Verificar que retorna `llm_available`, `lms_loaded`, `db_available`
    - Verificar que NO retorna `ml_model_loaded`
    - _Requirements: 1.2_
  
  - [x] 9.3 Probar endpoint `/ml/recomendacion_personalizada`
    - Ejecutar request con `id_nino` válido y `tipo_comida="DESAYUNO"`
    - Verificar que retorna recomendación del LLM
    - Verificar que `recetas_disponibles` contiene recetas
    - Verificar que `used_llm=true`
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 9.4 Probar casos de error
    - Probar con `id_nino` inexistente (debe retornar 404)
    - Probar con LLM desconectado (debe retornar mensaje de fallback)
    - Verificar logs de error
    - _Requirements: 2.4_

- [ ]* 10. Escribir tests automatizados
  - [ ]* 10.1 Tests unitarios para `consultar_datos_nino`
    - Test con niño existente
    - Test con niño inexistente (debe lanzar HTTPException 404)
    - _Requirements: 3.1_
  
  - [ ]* 10.2 Tests unitarios para `consultar_recetas_por_nino`
    - Test con resultados válidos
    - Test con `status='NO_MATCH'` (debe retornar lista vacía)
    - Test con error de BD (debe retornar lista vacía y loggear)
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ]* 10.3 Tests unitarios para `crear_prompt_recomendacion`
    - Test con recetas disponibles
    - Test sin recetas
    - Test con pregunta específica del usuario
    - Verificar que incluye todos los elementos necesarios
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [ ]* 10.4 Test de integración del endpoint completo
    - Test end-to-end con mock del LLM
    - Verificar estructura de respuesta
    - Verificar que `used_llm` es correcto
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 11. Actualizar documentación
  - [x] 11.1 Actualizar `README.md`
    - Reescribir sección de arquitectura
    - Eliminar referencias a entrenamiento de modelos
    - Documentar endpoints activos
    - Agregar ejemplos de uso
    - _Requirements: 6.1_
  
  - [x] 11.2 Actualizar `docs/ARQUITECTURA_ML.md`
    - Reescribir completamente para reflejar arquitectura LLM + BD
    - Eliminar diagramas de modelos ML
    - Agregar diagrama de flujo de recomendaciones
    - _Requirements: 6.2_
  
  - [x] 11.3 Actualizar `docs/API_ML.md`
    - Eliminar documentación de endpoints de predicción ML
    - Mantener solo endpoints activos
    - Agregar ejemplos de requests/responses
    - _Requirements: 6.2_
  
  - [x] 11.4 Crear `docs/CONFIGURACION_LLM.md`
    - Documentar variables de entorno del LLM
    - Explicar cómo configurar el agente CORA
    - Troubleshooting común
    - _Requirements: 6.3_
  
  - [x] 11.5 Actualizar `control/Nutricion-api/INTEGRACION_ML.md`
    - Documentar nuevo flujo de integración
    - Actualizar ejemplos de llamadas a la API
    - Eliminar referencias a modelos ML
    - _Requirements: 6.2, 8.4_

- [x] 12. Verificar integración con backend principal
  - [x] 12.1 Probar desde Nutricion-api
    - Verificar que el endpoint `/ml/recomendacion_personalizada` funciona desde el backend
    - Verificar que la respuesta se procesa correctamente
    - _Requirements: 8.1, 8.2_
  
  - [x] 12.2 Verificar endpoints eliminados
    - Confirmar que `/ml/predict` retorna 404
    - Confirmar que `/ml/predict_direct` retorna 404
    - Confirmar que `/ml/model_info` retorna 404
    - _Requirements: 8.3_
  
  - [x] 12.3 Verificar endpoint `/ml/predict_baz` sigue funcionando
    - Probar cálculo de BAZ con datos válidos
    - Verificar que usa tablas OMS correctamente
    - _Requirements: 7.1, 7.2, 7.3_

- [-] 13. Limpieza final y commit
  - Revisar que no quedan referencias a modelos ML en el código
  - Verificar que todos los tests pasan
  - Hacer commit con mensaje descriptivo
  - Crear pull request para revisión
  - _Requirements: 5, 6, 8_

