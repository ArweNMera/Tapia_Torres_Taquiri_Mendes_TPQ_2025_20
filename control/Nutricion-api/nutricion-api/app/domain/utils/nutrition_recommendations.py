"""
Utilidades para generar recomendaciones nutricionales personalizadas.
Este módulo contiene la lógica de negocio para generar recomendaciones
basadas en el estado nutricional del niño.
"""

from typing import Any

# Catálogo base usado tanto para sugerencias dinámicas como para poblar la tabla recomendaciones_tipos
RECOMMENDATION_CATALOG: dict[str, list[dict[str, Any]]] = {
    "DESNUTRICION_SEVERA": [
        {
            "codigo": "DES_SEVERA_ATENCION",
            "icono": "⚠️",
            "titulo": "Atención médica urgente",
            "descripcion": "Consulta inmediata con pediatra o nutricionista especializado",
            "prioridad": 1,
        },
        {
            "codigo": "DES_SEVERA_EVALUACION",
            "icono": "⚠️",
            "titulo": "Evaluación clínica completa",
            "descripcion": "Descartar enfermedades subyacentes y complicaciones metabólicas",
            "prioridad": 2,
        },
        {
            "codigo": "DES_SEVERA_PLAN_RECUP",
            "icono": "🍲",
            "titulo": "Plan de recuperación nutricional",
            "descripcion": "Diseñar plan hipercalórico e hiperproteico supervisado por profesional de salud",
            "prioridad": 3,
        },
        {
            "codigo": "DES_SEVERA_SUPLEMENTOS",
            "icono": "💊",
            "titulo": "Suplementación específica",
            "descripcion": "Evaluar uso de suplementos vitamínico-minerales bajo supervisión médica",
            "prioridad": 4,
        },
        {
            "codigo": "DES_SEVERA_MONITOREO",
            "icono": "📈",
            "titulo": "Monitoreo semanal",
            "descripcion": "Control de peso, talla y signos vitales cada semana durante la recuperación",
            "prioridad": 5,
        },
    ],
    "DESNUTRICION": [
        {
            "codigo": "DES_MODERADA_CONSULTA",
            "icono": "⚠️",
            "titulo": "Consulta nutricional prioritaria",
            "descripcion": "Agendar cita con nutricionista pediátrico en un plazo menor a 7 días",
            "prioridad": 1,
        },
        {
            "codigo": "DES_MODERADA_FRECUENCIA",
            "icono": "🍽️",
            "titulo": "Aumentar frecuencia de comidas",
            "descripcion": "Distribuir 5 a 6 comidas pequeñas con alta densidad energética",
            "prioridad": 2,
        },
        {
            "codigo": "DES_MODERADA_PROTEINAS",
            "icono": "🥚",
            "titulo": "Potenciar alimentos proteicos",
            "descripcion": "Incluir carnes magras, huevos, lácteos y legumbres en cada comida principal",
            "prioridad": 3,
        },
        {
            "codigo": "DES_MODERADA_GRASAS_SALUDABLES",
            "icono": "🥑",
            "titulo": "Agregar grasas saludables",
            "descripcion": "Usar palta, aceite de oliva y frutos secos para aumentar calorías de calidad",
            "prioridad": 4,
        },
        {
            "codigo": "DES_MODERADA_SUPLEMENTOS",
            "icono": "💊",
            "titulo": "Evaluar suplementación",
            "descripcion": "Considerar multivitamínicos o fortificantes según indicación profesional",
            "prioridad": 5,
        },
    ],
    "RIESGO": [
        {
            "codigo": "RIESGO_CONSULTA_PREVENTIVA",
            "icono": "🍎",
            "titulo": "Consulta preventiva",
            "descripcion": "Coordinar asesoría nutricional para prevenir progresión del riesgo",
            "prioridad": 1,
        },
        {
            "codigo": "RIESGO_PORCIONES",
            "icono": "🥗",
            "titulo": "Incremento gradual de porciones",
            "descripcion": "Aumentar ligeramente la cantidad en comidas principales con alimentos densos en nutrientes",
            "prioridad": 2,
        },
        {
            "codigo": "RIESGO_MERiENDAS",
            "icono": "🍌",
            "titulo": "Meriendas saludables",
            "descripcion": "Añadir dos meriendas nutritivas diarios con frutas, yogur o frutos secos",
            "prioridad": 3,
        },
        {
            "codigo": "RIESGO_PRIORIZAR_NUTRIENTES",
            "icono": "🥦",
            "titulo": "Priorizar alimentos nutritivos",
            "descripcion": "Garantizar presencia diaria de frutas, verduras, proteínas y lácteos",
            "prioridad": 4,
        },
        {
            "codigo": "RIESGO_MONITOREO",
            "icono": "📈",
            "titulo": "Monitoreo mensual",
            "descripcion": "Controlar peso y talla cada mes para confirmar mejoría",
            "prioridad": 5,
        },
    ],
    "NORMAL": [
        {
            "codigo": "NORMAL_MANTENER_HABITOS",
            "icono": "✅",
            "titulo": "Mantener hábitos actuales",
            "descripcion": "Conservar alimentación balanceada y horarios regulares",
            "prioridad": 1,
        },
        {
            "codigo": "NORMAL_VARIAR_ALIMENTOS",
            "icono": "🥗",
            "titulo": "Variedad diaria",
            "descripcion": "Incluir frutas, verduras, proteínas, cereales integrales y lácteos cada día",
            "prioridad": 2,
        },
        {
            "codigo": "NORMAL_HIDRATACION",
            "icono": "💧",
            "titulo": "Buena hidratación",
            "descripcion": "Preferir agua sobre bebidas azucaradas y mantener consumo constante",
            "prioridad": 3,
        },
        {
            "codigo": "NORMAL_ACTIVIDAD",
            "icono": "⚽",
            "titulo": "Actividad física regular",
            "descripcion": "Fomentar al menos 60 minutos diarios de actividad acorde a la edad",
            "prioridad": 4,
        },
        {
            "codigo": "NORMAL_SEGUIMIENTO",
            "icono": "📅",
            "titulo": "Seguimiento periódico",
            "descripcion": "Realizar control de crecimiento cada 3 a 6 meses",
            "prioridad": 5,
        },
    ],
    "SOBREPESO": [
        {
            "codigo": "SOBREPESO_CONSULTA",
            "icono": "⚠️",
            "titulo": "Consulta nutricional especializada",
            "descripcion": "Diseñar un plan alimentario personalizado con nutricionista",
            "prioridad": 1,
        },
        {
            "codigo": "SOBREPESO_PORCIONES",
            "icono": "🍽️",
            "titulo": "Control de porciones",
            "descripcion": "Reducir gradualmente raciones grandes sin eliminar grupos alimenticios",
            "prioridad": 2,
        },
        {
            "codigo": "SOBREPESO_FRUTAS_VERDURAS",
            "icono": "🥦",
            "titulo": "Mayor consumo de vegetales y frutas",
            "descripcion": "Cubrir al menos cinco porciones diarias entre frutas y verduras frescas",
            "prioridad": 3,
        },
        {
            "codigo": "SOBREPESO_BEBIDAS",
            "icono": "🚫",
            "titulo": "Eliminar bebidas azucaradas",
            "descripcion": "Reemplazar gaseosas y jugos industrializados por agua",
            "prioridad": 4,
        },
        {
            "codigo": "SOBREPESO_ACTIVIDAD",
            "icono": "🏃",
            "titulo": "Incrementar actividad física",
            "descripcion": "Realizar al menos 60 minutos diarios de actividad moderada",
            "prioridad": 5,
        },
    ],
    "OBESIDAD": [
        {
            "codigo": "OBESIDAD_CONSULTA_INTEGRAL",
            "icono": "⚠️",
            "titulo": "Consulta integral prioritaria",
            "descripcion": "Atención conjunta con nutricionista, pediatra y psicología si es necesario",
            "prioridad": 1,
        },
        {
            "codigo": "OBESIDAD_EVALUACION_METAB",
            "icono": "🩺",
            "titulo": "Evaluación metabólica",
            "descripcion": "Solicitar controles de glucosa, perfil lipídico y presión arterial",
            "prioridad": 2,
        },
        {
            "codigo": "OBESIDAD_PLAN_FAMILIAR",
            "icono": "👨‍👩‍👧",
            "titulo": "Plan alimentario familiar",
            "descripcion": "Implementar cambios de alimentación y estilo de vida para todo el hogar",
            "prioridad": 3,
        },
        {
            "codigo": "OBESIDAD_ACTIVIDAD_PROGRESIVA",
            "icono": "🏊",
            "titulo": "Actividad física progresiva",
            "descripcion": "Iniciar con 30 minutos diarios y aumentar gradualmente la intensidad",
            "prioridad": 4,
        },
        {
            "codigo": "OBESIDAD_MONITOREO_FRECUENTE",
            "icono": "📈",
            "titulo": "Monitoreo quincenal",
            "descripcion": "Controlar peso y medidas cada 2 semanas durante los primeros 3 meses",
            "prioridad": 5,
        },
    ],
}

DEFAULT_RECOMMENDATIONS: list[dict[str, Any]] = [
    {
        "codigo": "GENERAL_EVALUACION",
        "icono": "🍎",
        "titulo": "Evaluación nutricional periódica",
        "descripcion": "Mantener controles regulares con el profesional de salud",
        "prioridad": 1,
    },
    {
        "codigo": "GENERAL_ALIMENTACION_BALANCEADA",
        "icono": "🥗",
        "titulo": "Alimentación balanceada",
        "descripcion": "Priorizar alimentos frescos y limitar los ultraprocesados",
        "prioridad": 2,
    },
    {
        "codigo": "GENERAL_HIDRATACION",
        "icono": "💧",
        "titulo": "Hidratación adecuada",
        "descripcion": "Promover el consumo de agua durante todo el día",
        "prioridad": 3,
    },
    {
        "codigo": "GENERAL_ACTIVIDAD",
        "icono": "⚽",
        "titulo": "Actividad física cotidiana",
        "descripcion": "Practicar juegos activos y actividades recreativas diarias",
        "prioridad": 4,
    },
    {
        "codigo": "GENERAL_HABITOS",
        "icono": "📅",
        "titulo": "Hábitos consistentes",
        "descripcion": "Establecer horarios regulares de comida y descanso",
        "prioridad": 5,
    },
]

RECOMMENDATION_LOOKUP: dict[str, dict[str, Any]] = {
    item["codigo"]: item
    for items in list(RECOMMENDATION_CATALOG.values()) + [DEFAULT_RECOMMENDATIONS]
    for item in items
}


def generar_recomendaciones_nutricionales(
    clasificacion: str, imc: float, edad_meses: int
) -> list[dict[str, str]]:
    """
    Genera recomendaciones personalizadas basadas en el estado nutricional.
    Usa el catálogo base y limita la salida a cinco recomendaciones.
    """
    catalog = RECOMMENDATION_CATALOG.get(clasificacion) or DEFAULT_RECOMMENDATIONS
    return [
        {
            "icono": item["icono"],
            "titulo": item["titulo"],
            "descripcion": item["descripcion"],
        }
        for item in catalog[:5]
    ]


def mapear_recomendacion_desde_db(rt_codigo: str, titulo: str, descripcion: str) -> dict[str, str]:
    """
    Ajusta la recomendación provenientes de la BD añadiendo el icono del catálogo.
    """
    base = RECOMMENDATION_LOOKUP.get(rt_codigo, {})
    return {
        "icono": base.get("icono", "🍎"),
        "titulo": titulo,
        "descripcion": descripcion,
    }
