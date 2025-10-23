"""
Ejemplo para Google Colab: generación de plan semanal de comidas.

Uso:
1) Subir este proyecto a Colab (zip o git clone).
2) Ejecutar este script para probar el planificador.
"""

from __future__ import annotations

from src.recommender import MealPlanner

# Preferencias del niño (categorías): pesos entre 0 y 1
preferencias = {
    "vegetariano": 0.4,
    "alto_fibra": 0.3,
    "ligero": 0.2,
}

# Comidas favoritas (ingredientes)
favoritas = ["fruta", "yogur", "huevo"]

# Alergias reportadas
alergias = ["almendra"]

# Objetivos diarios (pueden ajustarse por edad/sexo)
objetivos = {"kcal": 1800, "proteina_g": 50.0}

planner = MealPlanner(objetivos)
plan = planner.generar_plan_semanal(
    estado_nutricional="RIESGO_DESNUTRICION",
    alergias=alergias,
    preferencias=preferencias,
    favoritas=favoritas,
    dias=3,  # muestra de 3 días
)

print("Resumen:", plan.resumen())
for idx, dia in enumerate(plan.dias, 1):
    print(f"\nDía {idx}")
    for it in dia.items:
        print(
            f"- {it.slot}: {it.nombre} | {it.kcal} kcal, {it.proteina_g} g prot | Score {it.score} | {it.razon}"
        )
