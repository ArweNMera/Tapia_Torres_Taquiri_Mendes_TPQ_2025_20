"""
Utilidades para generar recomendaciones nutricionales personalizadas.
Este módulo contiene la lógica de negocio para generar recomendaciones
basadas en el estado nutricional del niño.
"""
from typing import List


def generar_recomendaciones_nutricionales(clasificacion: str, imc: float, edad_meses: int) -> List[str]:
    """
    Genera recomendaciones personalizadas basadas en el estado nutricional.
    
    Args:
        clasificacion: Clasificación nutricional (DESNUTRICION_SEVERA, DESNUTRICION, etc.)
        imc: Índice de masa corporal
        edad_meses: Edad del niño en meses
        
    Returns:
        Lista de recomendaciones específicas
    """
    recomendaciones = []
    edad_anios = edad_meses // 12
    
    if clasificacion == "DESNUTRICION_SEVERA":
        recomendaciones = [
            "⚠️ URGENTE: Consulta inmediata con pediatra o nutricionista especializado",
            "Evaluación médica completa para descartar enfermedades subyacentes",
            "Plan de recuperación nutricional supervisado por profesional de salud",
            "Alimentación frecuente (cada 2-3 horas) con alimentos de alta densidad energética",
            "Suplementación nutricional bajo supervisión médica",
            "Monitoreo semanal de peso y talla durante la recuperación",
            "Considerar hospitalización si hay complicaciones asociadas"
        ]
    
    elif clasificacion == "DESNUTRICION":
        recomendaciones = [
            "⚠️ Consulta con nutricionista pediátrico en los próximos 7 días",
            "Aumentar frecuencia de comidas a 5-6 veces al día",
            "Incluir alimentos ricos en proteínas: carnes magras, huevos, lácteos, legumbres",
            "Agregar grasas saludables: palta, frutos secos, aceite de oliva",
            "Enriquecer preparaciones con leche en polvo, queso rallado",
            "Evitar líquidos antes de las comidas para no reducir el apetito",
            "Monitoreo de peso cada 2 semanas",
            "Evaluar suplementación vitamínica con profesional de salud"
        ]
    
    elif clasificacion == "RIESGO":
        recomendaciones = [
            "Consulta nutricional preventiva recomendada",
            "Aumentar gradualmente las porciones de alimentos",
            "Incluir meriendas saludables entre comidas principales",
            "Priorizar alimentos nutritivos: frutas, verduras, proteínas, lácteos",
            "Asegurar 3 comidas principales + 2 meriendas al día",
            "Limitar consumos de bebidas azucaradas y alimentos procesados",
            "Monitoreo mensual de crecimiento",
            "Fomentar actividad física adecuada para la edad"
        ]
    
    elif clasificacion == "NORMAL":
        recomendaciones = [
            "✅ Mantener alimentación balanceada y variada actual",
            "Continuar con 3 comidas principales y 2 meriendas saludables",
            "Incluir diariamente: frutas, verduras, proteínas, lácteos y cereales integrales",
            "Hidratación adecuada con agua (evitar bebidas azucaradas)",
            "Fomentar actividad física regular según edad",
            "Limitar consumo de alimentos ultraprocesados y comida rápida",
            "Monitoreo de crecimiento cada 3-6 meses",
            "Mantener buenos hábitos alimenticios y horarios regulares"
        ]
    
    elif clasificacion == "SOBREPESO":
        recomendaciones = [
            "Consulta con nutricionista para plan alimentario personalizado",
            "Reducir porciones gradualmente sin eliminar grupos alimenticios",
            "Aumentar consumo de frutas y verduras frescas",
            "Limitar alimentos altos en azúcares y grasas saturadas",
            "Evitar bebidas azucaradas, jugos procesados y gaseosas",
            "Incrementar actividad física: mínimo 60 minutos diarios",
            "Establecer horarios regulares de comida (evitar picoteos)",
            "Involucrar a toda la familia en cambios de estilo de vida",
            "Monitoreo mensual de peso y control cada 2 meses"
        ]
    
    elif clasificacion == "OBESIDAD":
        recomendaciones = [
            "⚠️ Consulta prioritaria con nutricionista y pediatra",
            "Evaluación médica completa para descartar comorbilidades",
            "Plan de alimentación individualizado y supervisado",
            "Reducir consumo de alimentos ultraprocesados y azúcares añadidos",
            "Eliminar bebidas azucaradas y reemplazar por agua",
            "Aumentar actividad física progresivamente (iniciar con 30 min/día)",
            "Modificar hábitos familiares de alimentación y actividad física",
            "Apoyo psicológico si es necesario para manejo emocional",
            "Monitoreo quincenal inicial, luego mensual",
            "Evaluación de factores metabólicos (glucosa, lípidos) con médico"
        ]
    
    else:
        recomendaciones = [
            "Consulta con profesional de salud para evaluación personalizada",
            "Mantener alimentación equilibrada y variada",
            "Monitoreo regular de crecimiento y desarrollo"
        ]
    
    # Agregar recomendaciones específicas por edad
    if edad_meses < 24:  # Menores de 2 años
        recomendaciones.append("💡 Lactancia materna exclusiva hasta los 6 meses (si aplica)")
        recomendaciones.append("Introducción progresiva de alimentos complementarios después de 6 meses")
    elif edad_anios < 5:  # 2-5 años
        recomendaciones.append("💡 Fomentar autonomía en la alimentación con supervisión")
        recomendaciones.append("Presentar alimentos de forma atractiva y variada")
    elif edad_anios < 12:  # 5-12 años
        recomendaciones.append("💡 Educar sobre elecciones alimentarias saludables")
        recomendaciones.append("Involucrar en preparación de alimentos saludables")
    else:  # Adolescentes
        recomendaciones.append("💡 Promover imagen corporal positiva y autoestima")
        recomendaciones.append("Educación nutricional para autonomía alimentaria")
    
    return recomendaciones
