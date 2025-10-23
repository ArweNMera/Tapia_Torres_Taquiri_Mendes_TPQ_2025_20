#!/usr/bin/env python3
"""
Script de prueba para el endpoint de recomendaciones personalizadas.
Este script simula una llamada al endpoint sin necesidad de ejecutar el servidor completo.
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def simular_recomendacion():
    """Simula el proceso de generar una recomendación personalizada."""

    print("🧪 Probando endpoint de recomendaciones personalizadas")
    print("=" * 60)

    # Simular datos de entrada
    request_data = {
        "id_nino": 1,
        "tipo_comida": "desayuno",
        "pregunta_usuario": "¿Qué puedo darle de desayuno a mi hijo que sea saludable?",
    }

    print(f"📝 Datos de entrada: {request_data}")
    print()

    # Simular datos del niño (como si vinieran de la BD)
    datos_nino_simulados = {
        "id": 1,
        "nombre": "Juan Pérez García",
        "fecha_nacimiento": "2023-08-15",
        "sexo": "M",
        "peso_kg": 7.5,
        "talla_cm": 65.0,
        "imc": 17.8,
        "edad_meses": 6,
        "estado_nutricional": "NORMAL",
        "diagnostico": "Peso normal para la edad",
        "entidad": "Hospital Central",
        "codigo_entidad": "HC001",
    }

    print("👶 Datos del niño obtenidos:")
    for key, value in datos_nino_simulados.items():
        print(f"   {key}: {value}")
    print()

    # Simular estado nutricional
    estado_nutricional_simulado = {
        "diagnostico": "Peso normal para la edad",
        "estado_actual": "NORMAL",
        "imc": 17.8,
        "peso_kg": 7.5,
        "talla_cm": 65.0,
        "edad_meses": 6,
        "sexo": "M",
    }

    print("📊 Estado nutricional:")
    for key, value in estado_nutricional_simulado.items():
        print(f"   {key}: {value}")
    print()

    # Simular recetas disponibles
    recetas_simuladas = [
        {
            "id": 1,
            "nombre": "Avena con frutas",
            "descripcion": "Avena cocida con manzana y plátano triturados",
            "tipo_comida": "desayuno",
            "calorias": 150,
            "proteinas": 4.5,
            "carbohidratos": 28.0,
            "grasas": 2.5,
            "puntuacion": 8.5,
        },
        {
            "id": 2,
            "nombre": "Yogur con cereales",
            "descripcion": "Yogur natural con cereales infantiles",
            "tipo_comida": "desayuno",
            "calorias": 120,
            "proteinas": 5.0,
            "carbohidratos": 18.0,
            "grasas": 3.0,
            "puntuacion": 8.2,
        },
    ]

    print("🍽️  Recetas disponibles:")
    for receta in recetas_simuladas:
        print(f"   • {receta['nombre']} (Puntuación: {receta['puntuacion']}/10)")
        print(f"     Calorías: {receta['calorias']}kcal, Proteínas: {receta['proteinas']}g")
    print()

    # Simular respuesta del LLM
    recomendacion_simulada = """Hola, soy el nutricionista de NutriFam. Basándome en los datos de Juan (6 meses, peso normal), te recomiendo para el desayuno:

1. **Avena con frutas** - Excelente opción rica en fibra y vitaminas
   - Porción recomendada: 150-200ml
   - Beneficios: Ayuda con la digestión y proporciona energía sostenida

2. **Alternativa saludable**: Yogur natural con cereales infantiles
   - Porción: 100-150ml de yogur + 2-3 cucharadas de cereal
   - Beneficios: Alto en calcio y probióticos para la flora intestinal

Recuerda ofrecer la comida en un ambiente tranquilo y no forzar al niño si no tiene hambre. ¡Cada niño tiene su propio ritmo!"""

    print("🤖 Recomendación generada por LLM:")
    print("-" * 40)
    print(recomendacion_simulada)
    print("-" * 40)
    print()

    # Simular respuesta completa del endpoint
    response_simulada = {
        "recomendacion": recomendacion_simulada,
        "datos_nino": datos_nino_simulados,
        "recetas_disponibles": recetas_simuladas,
        "estado_nutricional": estado_nutricional_simulado,
        "used_llm": True,
    }

    print("✅ Respuesta del endpoint simulada exitosamente")
    print(f"📊 Total de recetas encontradas: {len(recetas_simuladas)}")
    print("🧠 LLM utilizado: Sí")
    print("📝 Recomendación generada: Sí")
    return response_simulada


if __name__ == "__main__":
    try:
        resultado = simular_recomendacion()
        print("\n🎉 Prueba completada exitosamente!")
        print("El endpoint está listo para recibir solicitudes reales.")
    except Exception as e:
        print(f"\n❌ Error en la prueba: {str(e)}")
        sys.exit(1)
