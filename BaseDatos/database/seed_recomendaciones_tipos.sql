-- ============================================================================
-- Catálogo de recomendaciones nutricionales base
-- Ejecutar este script después de aplicar la estructura de tablas.
-- Se usa también por el backend para poblar evaluaciones_recomendaciones.
-- ============================================================================

INSERT INTO recomendaciones_tipos (
    rt_codigo,
    rt_titulo,
    rt_descripcion,
    rt_clasificacion,
    rt_prioridad,
    rt_activo
) VALUES
    -- Desnutrición severa
    ('DES_SEVERA_ATENCION', 'Atención médica urgente', 'Consulta inmediata con pediatra o nutricionista especializado', 'DESNUTRICION_SEVERA', 1, TRUE),
    ('DES_SEVERA_EVALUACION', 'Evaluación clínica completa', 'Descartar enfermedades subyacentes y complicaciones metabólicas', 'DESNUTRICION_SEVERA', 2, TRUE),
    ('DES_SEVERA_PLAN_RECUP', 'Plan de recuperación nutricional', 'Diseñar plan hipercalórico e hiperproteico supervisado por profesional de salud', 'DESNUTRICION_SEVERA', 3, TRUE),
    ('DES_SEVERA_SUPLEMENTOS', 'Suplementación específica', 'Evaluar uso de suplementos vitamínico-minerales bajo supervisión médica', 'DESNUTRICION_SEVERA', 4, TRUE),
    ('DES_SEVERA_MONITOREO', 'Monitoreo semanal', 'Control de peso, talla y signos vitales cada semana durante la recuperación', 'DESNUTRICION_SEVERA', 5, TRUE),

    -- Desnutrición
    ('DES_MODERADA_CONSULTA', 'Consulta nutricional prioritaria', 'Agendar cita con nutricionista pediátrico en un plazo menor a 7 días', 'DESNUTRICION', 1, TRUE),
    ('DES_MODERADA_FRECUENCIA', 'Aumentar frecuencia de comidas', 'Distribuir 5 a 6 comidas pequeñas con alta densidad energética', 'DESNUTRICION', 2, TRUE),
    ('DES_MODERADA_PROTEINAS', 'Potenciar alimentos proteicos', 'Incluir carnes magras, huevos, lácteos y legumbres en cada comida principal', 'DESNUTRICION', 3, TRUE),
    ('DES_MODERADA_GRASAS_SALUDABLES', 'Agregar grasas saludables', 'Usar palta, aceite de oliva y frutos secos para aumentar calorías de calidad', 'DESNUTRICION', 4, TRUE),
    ('DES_MODERADA_SUPLEMENTOS', 'Evaluar suplementación', 'Considerar multivitamínicos o fortificantes según indicación profesional', 'DESNUTRICION', 5, TRUE),

    -- Riesgo de desnutrición
    ('RIESGO_CONSULTA_PREVENTIVA', 'Consulta preventiva', 'Coordinar asesoría nutricional para prevenir progresión del riesgo', 'RIESGO', 1, TRUE),
    ('RIESGO_PORCIONES', 'Incremento gradual de porciones', 'Aumentar ligeramente la cantidad en comidas principales con alimentos densos en nutrientes', 'RIESGO', 2, TRUE),
    ('RIESGO_MERiENDAS', 'Meriendas saludables', 'Añadir dos meriendas nutritivas diarias con frutas, yogur o frutos secos', 'RIESGO', 3, TRUE),
    ('RIESGO_PRIORIZAR_NUTRIENTES', 'Priorizar alimentos nutritivos', 'Garantizar presencia diaria de frutas, verduras, proteínas y lácteos', 'RIESGO', 4, TRUE),
    ('RIESGO_MONITOREO', 'Monitoreo mensual', 'Controlar peso y talla cada mes para confirmar mejoría', 'RIESGO', 5, TRUE),

    -- Normal
    ('NORMAL_MANTENER_HABITOS', 'Mantener hábitos actuales', 'Conservar alimentación balanceada y horarios regulares', 'NORMAL', 1, TRUE),
    ('NORMAL_VARIAR_ALIMENTOS', 'Variedad diaria', 'Incluir frutas, verduras, proteínas, cereales integrales y lácteos cada día', 'NORMAL', 2, TRUE),
    ('NORMAL_HIDRATACION', 'Buena hidratación', 'Preferir agua sobre bebidas azucaradas y mantener consumo constante', 'NORMAL', 3, TRUE),
    ('NORMAL_ACTIVIDAD', 'Actividad física regular', 'Fomentar al menos 60 minutos diarios de actividad acorde a la edad', 'NORMAL', 4, TRUE),
    ('NORMAL_SEGUIMIENTO', 'Seguimiento periódico', 'Realizar control de crecimiento cada 3 a 6 meses', 'NORMAL', 5, TRUE),

    -- Sobrepeso
    ('SOBREPESO_CONSULTA', 'Consulta nutricional especializada', 'Diseñar un plan alimentario personalizado con nutricionista', 'SOBREPESO', 1, TRUE),
    ('SOBREPESO_PORCIONES', 'Control de porciones', 'Reducir gradualmente raciones grandes sin eliminar grupos alimenticios', 'SOBREPESO', 2, TRUE),
    ('SOBREPESO_FRUTAS_VERDURAS', 'Mayor consumo de vegetales y frutas', 'Cubrir al menos cinco porciones diarias entre frutas y verduras frescas', 'SOBREPESO', 3, TRUE),
    ('SOBREPESO_BEBIDAS', 'Eliminar bebidas azucaradas', 'Reemplazar gaseosas y jugos industrializados por agua', 'SOBREPESO', 4, TRUE),
    ('SOBREPESO_ACTIVIDAD', 'Incrementar actividad física', 'Realizar al menos 60 minutos diarios de actividad moderada', 'SOBREPESO', 5, TRUE),

    -- Obesidad
    ('OBESIDAD_CONSULTA_INTEGRAL', 'Consulta integral prioritaria', 'Atención conjunta con nutricionista, pediatra y psicología si es necesario', 'OBESIDAD', 1, TRUE),
    ('OBESIDAD_EVALUACION_METAB', 'Evaluación metabólica', 'Solicitar controles de glucosa, perfil lipídico y presión arterial', 'OBESIDAD', 2, TRUE),
    ('OBESIDAD_PLAN_FAMILIAR', 'Plan alimentario familiar', 'Implementar cambios de alimentación y estilo de vida para todo el hogar', 'OBESIDAD', 3, TRUE),
    ('OBESIDAD_ACTIVIDAD_PROGRESIVA', 'Actividad física progresiva', 'Iniciar con 30 minutos diarios y aumentar gradualmente la intensidad', 'OBESIDAD', 4, TRUE),
    ('OBESIDAD_MONITOREO_FRECUENTE', 'Monitoreo quincenal', 'Controlar peso y medidas cada 2 semanas durante los primeros 3 meses', 'OBESIDAD', 5, TRUE)
ON DUPLICATE KEY UPDATE
    rt_titulo       = VALUES(rt_titulo),
    rt_descripcion  = VALUES(rt_descripcion),
    rt_clasificacion= VALUES(rt_clasificacion),
    rt_prioridad    = VALUES(rt_prioridad),
    rt_activo       = VALUES(rt_activo);

SELECT '✅ Catálogo recomendaciones_tipos actualizado' AS status;
