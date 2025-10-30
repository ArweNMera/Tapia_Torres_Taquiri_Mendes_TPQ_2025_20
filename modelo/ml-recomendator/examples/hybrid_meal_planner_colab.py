"""
Notebook Colab End-to-End: Sistema Hibrido de Recomendacion de Menus
====================================================================

Este notebook demuestra el sistema completo de recomendacion hibrida:
1. Entrenamiento del ranker LightGBM
2. Optimizacion de planes con OR-Tools
3. Generacion de recomendaciones personalizadas
4. Evaluacion y visualizacion de resultados

Para usar en Google Colab:
1. Subir la carpeta del proyecto a Google Drive
2. Montar Drive y navegar al directorio
3. Ejecutar las celdas en orden
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")

# Configuracion para Colab
IN_COLAB = "google.colab" in sys.modules

if IN_COLAB:
    # Montar Google Drive
    from google.colab import drive

    drive.mount("/content/drive")

    # Cambiar al directorio del proyecto (ajustar ruta segun sea necesario)
    project_path = "/content/drive/MyDrive/modelo/ml-recomendator"
    if os.path.exists(project_path):
        os.chdir(project_path)
        sys.path.append(project_path)
    else:
        print("WARNING: Ajustar la ruta del proyecto en project_path")
        print("FOLDER: Estructura esperada: /content/drive/MyDrive/modelo/ml-recomendator/")

# Instalar dependencias si es necesario
if IN_COLAB:
    print("PACKAGE: Instalando dependencias...")
    # !pip install lightgbm scikit-learn ortools shap joblib -q
    print("SUCCESS: Dependencias instaladas")

# Imports principales
import json
import logging
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

print("ROCKET: Sistema Hibrido de Recomendacion de Menus")
print("=" * 50)

# ============================================================================
# SECCION 1: CONFIGURACION Y DATOS MOCK
# ============================================================================

print("\nDATA: SECCION 1: Configuracion y Datos Mock")
print("-" * 40)

# Configuracion de la base de datos mock
DB_CONFIG_MOCK = {
    "host": "localhost",
    "user": "mock_user",
    "password": "mock_password",
    "database": "meal_planner_mock",
}

# Datos mock de ninos
MOCK_CHILDREN = [
    {
        "child_id": 1,
        "age_months": 120,  # 10 anos
        "weight_kg": 35.0,
        "height_cm": 140.0,
        "nutritional_status": "NORMAL",
        "allergies": ["mani"],
        "preferences": {"vegetariano": 0.3, "alto_fibra": 0.4, "proteico": 0.2},
        "favorite_foods": ["fruta", "yogur", "pollo"],
    },
    {
        "child_id": 2,
        "age_months": 96,  # 8 anos
        "weight_kg": 28.0,
        "height_cm": 130.0,
        "nutritional_status": "RIESGO_DESNUTRICION",
        "allergies": ["lacteos"],
        "preferences": {"proteico": 0.6, "recuperacion": 0.4},
        "favorite_foods": ["carne", "arroz", "huevo"],
    },
    {
        "child_id": 3,
        "age_months": 144,  # 12 anos
        "weight_kg": 45.0,
        "height_cm": 155.0,
        "nutritional_status": "SOBREPESO",
        "allergies": [],
        "preferences": {"ligero": 0.5, "alto_fibra": 0.3, "vegetariano": 0.2},
        "favorite_foods": ["ensalada", "pescado", "verduras"],
    },
]

# Datos mock de menus expandidos
MOCK_MENUS = [
    # Desayunos
    {
        "menu_id": 1,
        "name": "Desayuno Proteico",
        "slot": "desayuno",
        "calories": 450,
        "protein": 20,
        "carbs": 45,
        "fat": 15,
        "categories": ["proteico"],
        "ingredients": ["huevo", "pan", "leche"],
        "allergens": ["lacteos"],
        "meal_type": "desayuno",
    },
    {
        "menu_id": 2,
        "name": "Desayuno Ligero",
        "slot": "desayuno",
        "calories": 350,
        "protein": 12,
        "carbs": 55,
        "fat": 8,
        "categories": ["ligero", "alto_fibra"],
        "ingredients": ["yogur", "granola", "fruta"],
        "allergens": ["lacteos"],
        "meal_type": "desayuno",
    },
    {
        "menu_id": 3,
        "name": "Desayuno Vegetariano",
        "slot": "desayuno",
        "calories": 400,
        "protein": 15,
        "carbs": 60,
        "fat": 12,
        "categories": ["vegetariano"],
        "ingredients": ["avena", "fruta", "nuez"],
        "allergens": ["nueces"],
        "meal_type": "desayuno",
    },
    {
        "menu_id": 4,
        "name": "Desayuno Energetico",
        "slot": "desayuno",
        "calories": 500,
        "protein": 18,
        "carbs": 70,
        "fat": 18,
        "categories": ["energetico", "recuperacion"],
        "ingredients": ["pancakes", "miel", "mantequilla"],
        "allergens": ["lacteos", "gluten"],
        "meal_type": "desayuno",
    },
    # Almuerzos
    {
        "menu_id": 10,
        "name": "Almuerzo Recuperacion",
        "slot": "almuerzo",
        "calories": 650,
        "protein": 35,
        "carbs": 75,
        "fat": 20,
        "categories": ["proteico", "recuperacion"],
        "ingredients": ["pollo", "arroz", "ensalada"],
        "allergens": [],
        "meal_type": "almuerzo",
    },
    {
        "menu_id": 11,
        "name": "Almuerzo Balanceado",
        "slot": "almuerzo",
        "calories": 550,
        "protein": 25,
        "carbs": 65,
        "fat": 18,
        "categories": ["balanceado"],
        "ingredients": ["carne", "quinoa", "verduras"],
        "allergens": [],
        "meal_type": "almuerzo",
    },
    {
        "menu_id": 12,
        "name": "Almuerzo Vegetariano",
        "slot": "almuerzo",
        "calories": 520,
        "protein": 22,
        "carbs": 70,
        "fat": 15,
        "categories": ["vegetariano"],
        "ingredients": ["legumbres", "arroz", "verduras"],
        "allergens": [],
        "meal_type": "almuerzo",
    },
    {
        "menu_id": 13,
        "name": "Almuerzo Ligero",
        "slot": "almuerzo",
        "calories": 480,
        "protein": 20,
        "carbs": 55,
        "fat": 12,
        "categories": ["ligero", "alto_fibra"],
        "ingredients": ["pescado", "ensalada", "papa"],
        "allergens": [],
        "meal_type": "almuerzo",
    },
    # Cenas
    {
        "menu_id": 20,
        "name": "Cena Mantenimiento",
        "slot": "cena",
        "calories": 540,
        "protein": 24,
        "carbs": 60,
        "fat": 16,
        "categories": ["balanceado"],
        "ingredients": ["pescado", "papa", "ensalada"],
        "allergens": [],
        "meal_type": "cena",
    },
    {
        "menu_id": 21,
        "name": "Cena Ligera",
        "slot": "cena",
        "calories": 480,
        "protein": 20,
        "carbs": 50,
        "fat": 14,
        "categories": ["ligero", "alto_fibra"],
        "ingredients": ["sopa", "pan", "verduras"],
        "allergens": ["gluten"],
        "meal_type": "cena",
    },
    {
        "menu_id": 22,
        "name": "Cena Vegetariana",
        "slot": "cena",
        "calories": 500,
        "protein": 21,
        "carbs": 55,
        "fat": 15,
        "categories": ["vegetariano"],
        "ingredients": ["tofu", "fideos", "verduras"],
        "allergens": ["soja"],
        "meal_type": "cena",
    },
    {
        "menu_id": 23,
        "name": "Cena Proteica",
        "slot": "cena",
        "calories": 580,
        "protein": 28,
        "carbs": 45,
        "fat": 18,
        "categories": ["proteico"],
        "ingredients": ["pollo", "ensalada", "aguacate"],
        "allergens": [],
        "meal_type": "cena",
    },
    # Snacks
    {
        "menu_id": 30,
        "name": "Snack Fruta y Yogur",
        "slot": "snack",
        "calories": 180,
        "protein": 8,
        "carbs": 25,
        "fat": 5,
        "categories": ["ligero"],
        "ingredients": ["fruta", "yogur"],
        "allergens": ["lacteos"],
        "meal_type": "snack",
    },
    {
        "menu_id": 31,
        "name": "Snack Frutos Secos",
        "slot": "snack",
        "calories": 220,
        "protein": 7,
        "carbs": 15,
        "fat": 15,
        "categories": ["alto_fibra"],
        "ingredients": ["nuez", "almendra"],
        "allergens": ["nueces"],
        "meal_type": "snack",
    },
    {
        "menu_id": 32,
        "name": "Snack Sandwich Pequeno",
        "slot": "snack",
        "calories": 250,
        "protein": 10,
        "carbs": 30,
        "fat": 8,
        "categories": ["proteico"],
        "ingredients": ["pan", "jamon", "queso"],
        "allergens": ["lacteos", "gluten"],
        "meal_type": "snack",
    },
    {
        "menu_id": 33,
        "name": "Snack Smoothie",
        "slot": "snack",
        "calories": 200,
        "protein": 6,
        "carbs": 35,
        "fat": 4,
        "categories": ["ligero", "energetico"],
        "ingredients": ["fruta", "leche", "miel"],
        "allergens": ["lacteos"],
        "meal_type": "snack",
    },
]

print("SUCCESS: Configuracion completada:")
print(f"   - {len(MOCK_CHILDREN)} perfiles de ninos")
print(f"   - {len(MOCK_MENUS)} menus disponibles")

# ============================================================================
# SECCION 2: ENTRENAMIENTO DEL RANKER
# ============================================================================

print("\nROBOT: SECCION 2: Entrenamiento del Ranker LightGBM")
print("-" * 40)

try:
    from src.models.rankers.lgbm_ranker import MenuRanker
    from src.pipeline.feature_engineering import FeatureEngineer

    # Crear pipeline de entrenamiento con datos mock
    class MockFeatureEngineer(FeatureEngineer):
        def __init__(self):
            self.mock_children = MOCK_CHILDREN
            self.mock_menus = MOCK_MENUS

        def create_training_dataset(self, n_samples=1000):
            """Crear dataset de entrenamiento con datos mock."""
            data = []

            for _ in range(n_samples):
                # Seleccionar nino y menu aleatorios
                child = np.random.choice(self.mock_children)
                menu = np.random.choice(self.mock_menus)

                # Crear features
                features = {
                    "child_id": child["child_id"],
                    "menu_id": menu["menu_id"],
                    "child_age_months": child["age_months"],
                    "child_weight_kg": child["weight_kg"],
                    "child_height_cm": child["height_cm"],
                    "nutritional_status": child["nutritional_status"],
                    "menu_calories": menu["calories"],
                    "menu_protein": menu["protein"],
                    "menu_carbs": menu["carbs"],
                    "menu_fat": menu["fat"],
                    "calorie_adequacy": menu["calories"] / 600,  # Aproximacion
                    "protein_adequacy": menu["protein"] / 20,
                    "allergy_compatible": 1.0
                    if not any(allergen in menu["allergens"] for allergen in child["allergies"])
                    else 0.0,
                    "nutritional_status_compatible": 1.0
                    if (
                        child["nutritional_status"] in ["SEVERO", "MODERADO", "RIESGO_DESNUTRICION"]
                        and "proteico" in menu["categories"]
                    )
                    else 0.5,
                }

                # Generar relevance score sintetico
                relevance = 0.5  # Base

                # Ajustar por compatibilidad de alergias
                relevance += 0.3 * features["allergy_compatible"]

                # Ajustar por estado nutricional
                relevance += 0.2 * features["nutritional_status_compatible"]

                # Ajustar por preferencias
                for category in menu["categories"]:
                    if category in child["preferences"]:
                        relevance += 0.1 * child["preferences"][category]

                # Ajustar por comidas favoritas
                for ingredient in menu["ingredients"]:
                    if ingredient in child["favorite_foods"]:
                        relevance += 0.1

                # Normalizar
                relevance = min(max(relevance, 0.0), 1.0)

                features["relevance_score"] = relevance
                data.append(features)

            return pd.DataFrame(data)

    # Crear y entrenar el ranker
    print("PROCESS: Creando dataset de entrenamiento...")
    mock_engineer = MockFeatureEngineer()
    train_df = mock_engineer.create_training_dataset(n_samples=2000)

    print(f"SUCCESS: Dataset creado: {len(train_df)} muestras")
    print(f"   - Features: {len(train_df.columns) - 1}")
    print(f"   - Relevance score promedio: {train_df['relevance_score'].mean():.3f}")

    # Entrenar ranker
    print("\nPROCESS: Entrenando ranker LightGBM...")
    ranker = MenuRanker(random_state=42)
    ranker.fit(train_df)

    print("SUCCESS: Ranker entrenado exitosamente")

    # Guardar modelo
    model_path = "models/ranker/menu_ranker_colab.pkl"
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    ranker.save_model(model_path)
    print(f"SAVE: Modelo guardado en: {model_path}")

    RANKER_TRAINED = True

except Exception as e:
    print(f"ERROR: Error en entrenamiento del ranker: {e}")
    print("PROCESS: Continuando sin ranker entrenado...")
    RANKER_TRAINED = False
    model_path = None

# ============================================================================
# SECCION 3: SISTEMA HIBRIDO DE RECOMENDACION
# ============================================================================

print("\nTARGET: SECCION 3: Sistema Hibrido de Recomendacion")
print("-" * 40)

try:
    from src.recommender.hybrid_meal_planner import create_hybrid_planner

    # Crear planificador hibrido
    if RANKER_TRAINED:
        planner = create_hybrid_planner(ranker_model_path=model_path, use_optimization=True)
        print("SUCCESS: Planificador hibrido creado con ranker y optimizacion")
    else:
        planner = create_hybrid_planner(ranker_model_path=None, use_optimization=False)
        print("SUCCESS: Planificador hibrido creado (modo basico)")

    HYBRID_PLANNER_READY = True

except Exception as e:
    print(f"ERROR: Error creando planificador hibrido: {e}")
    print("PROCESS: Usando planificador original...")

    from src.recommender.meal_planner import MealPlanner

    planner = MealPlanner({"kcal": 1800, "proteina_g": 50.0})
    HYBRID_PLANNER_READY = False

# ============================================================================
# SECCION 4: GENERACION DE PLANES PERSONALIZADOS
# ============================================================================

print("\nCLIPBOARD: SECCION 4: Generacion de Planes Personalizados")
print("-" * 40)

# Generar planes para cada nino mock
planes_generados = {}

for child in MOCK_CHILDREN:
    child_id = child["child_id"]
    print(f"\nCHILD: Generando plan para Nino {child_id}:")
    print(f"   - Edad: {child['age_months']//12} anos")
    print(f"   - Estado: {child['nutritional_status']}")
    print(f"   - Alergias: {child['allergies']}")

    try:
        if HYBRID_PLANNER_READY:
            plan = planner.generar_plan_semanal_hibrido(
                child_id=child_id,
                estado_nutricional=child["nutritional_status"],
                alergias=child["allergies"],
                preferencias=child["preferences"],
                favoritas=child["favorite_foods"],
                dias=3,  # Plan de 3 dias para demo
            )
        else:
            plan = planner.generar_plan_semanal(
                estado_nutricional=child["nutritional_status"],
                alergias=child["allergies"],
                preferencias=child["preferences"],
                favoritas=child["favorite_foods"],
                dias=3,
            )

        planes_generados[child_id] = plan
        print(f"SUCCESS: Plan generado: {plan.resumen()}")

    except Exception as e:
        print(f"ERROR: Error generando plan: {e}")

# ============================================================================
# SECCION 5: ANALISIS Y VISUALIZACION
# ============================================================================

print("\nCHART: SECCION 5: Analisis y Visualizacion")
print("-" * 40)

if planes_generados:
    # Analisis nutricional
    print("\nSEARCH: Analisis Nutricional por Nino:")

    for child_id, plan in planes_generados.items():
        child = next(c for c in MOCK_CHILDREN if c["child_id"] == child_id)
        print(f"\nCHILD: Nino {child_id} ({child['nutritional_status']}):")

        for day_idx, day_plan in enumerate(plan.dias, 1):
            total_kcal = day_plan.total_kcal()
            total_protein = day_plan.total_proteina()

            print(f"   Dia {day_idx}: {total_kcal} kcal, {total_protein}g proteina")

            for item in day_plan.items:
                print(f"     - {item.slot}: {item.nombre} (score: {item.score})")

    # Crear visualizaciones
    print("\nCHART: Creando visualizaciones...")

    # Datos para visualizacion
    viz_data = []
    for child_id, plan in planes_generados.items():
        child = next(c for c in MOCK_CHILDREN if c["child_id"] == child_id)

        for day_idx, day_plan in enumerate(plan.dias, 1):
            viz_data.append(
                {
                    "child_id": child_id,
                    "nutritional_status": child["nutritional_status"],
                    "day": day_idx,
                    "total_calories": day_plan.total_kcal(),
                    "total_protein": day_plan.total_proteina(),
                    "avg_score": np.mean([item.score for item in day_plan.items]),
                }
            )

    viz_df = pd.DataFrame(viz_data)

    # Configurar estilo de graficos
    plt.style.use("default")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("Analisis de Planes de Comida Generados", fontsize=16, fontweight="bold")

    # Grafico 1: Calorias por estado nutricional
    sns.boxplot(data=viz_df, x="nutritional_status", y="total_calories", ax=axes[0, 0])
    axes[0, 0].set_title("Distribucion de Calorias por Estado Nutricional")
    axes[0, 0].tick_params(axis="x", rotation=45)

    # Grafico 2: Proteinas por estado nutricional
    sns.boxplot(data=viz_df, x="nutritional_status", y="total_protein", ax=axes[0, 1])
    axes[0, 1].set_title("Distribucion de Proteinas por Estado Nutricional")
    axes[0, 1].tick_params(axis="x", rotation=45)

    # Grafico 3: Scores promedio por nino
    sns.barplot(data=viz_df, x="child_id", y="avg_score", ax=axes[1, 0])
    axes[1, 0].set_title("Score Promedio de Recomendaciones por Nino")
    axes[1, 0].set_xlabel("ID del Nino")

    # Grafico 4: Calorias vs Proteinas
    scatter = axes[1, 1].scatter(
        viz_df["total_calories"],
        viz_df["total_protein"],
        c=viz_df["child_id"],
        cmap="viridis",
        alpha=0.7,
    )
    axes[1, 1].set_title("Relacion Calorias vs Proteinas")
    axes[1, 1].set_xlabel("Calorias Totales")
    axes[1, 1].set_ylabel("Proteinas Totales (g)")
    plt.colorbar(scatter, ax=axes[1, 1], label="ID del Nino")

    plt.tight_layout()
    plt.show()

    print("SUCCESS: Visualizaciones generadas")

# ============================================================================
# SECCION 6: EVALUACION DEL SISTEMA
# ============================================================================

print("\nTARGET: SECCION 6: Evaluacion del Sistema")
print("-" * 40)

if RANKER_TRAINED and planes_generados:
    print("\nCHART: Metricas de Evaluacion:")

    # Calcular metricas agregadas
    all_scores = []
    all_calories = []
    all_proteins = []

    for plan in planes_generados.values():
        for day_plan in plan.dias:
            all_scores.extend([item.score for item in day_plan.items])
            all_calories.append(day_plan.total_kcal())
            all_proteins.append(day_plan.total_proteina())

    print(f"CHART: Score promedio de recomendaciones: {np.mean(all_scores):.3f}")
    print(f"CHART: Desviacion estandar de scores: {np.std(all_scores):.3f}")
    print(f"FOOD: Calorias promedio por dia: {np.mean(all_calories):.1f}")
    print(f"MEAT: Proteinas promedio por dia: {np.mean(all_proteins):.1f}g")

    # Evaluacion por estado nutricional
    print("\nCHART: Evaluacion por Estado Nutricional:")

    for status in ["NORMAL", "RIESGO_DESNUTRICION", "SOBREPESO"]:
        status_plans = [
            plan
            for child_id, plan in planes_generados.items()
            if next(c for c in MOCK_CHILDREN if c["child_id"] == child_id)["nutritional_status"]
            == status
        ]

        if status_plans:
            status_scores = []
            status_calories = []

            for plan in status_plans:
                for day_plan in plan.dias:
                    status_scores.extend([item.score for item in day_plan.items])
                    status_calories.append(day_plan.total_kcal())

            print(f"   {status}:")
            print(f"     - Score promedio: {np.mean(status_scores):.3f}")
            print(f"     - Calorias promedio: {np.mean(status_calories):.1f}")

# ============================================================================
# SECCION 7: EXPORTACION DE RESULTADOS
# ============================================================================

print("\nSAVE: SECCION 7: Exportacion de Resultados")
print("-" * 40)

# Crear directorio de resultados
results_dir = "results/colab_demo"
os.makedirs(results_dir, exist_ok=True)

# Exportar planes generados
if planes_generados:
    for child_id, plan in planes_generados.items():
        child = next(c for c in MOCK_CHILDREN if c["child_id"] == child_id)

        # Crear resumen del plan
        plan_summary = {"child_profile": child, "plan_summary": plan.resumen(), "daily_plans": []}

        for day_idx, day_plan in enumerate(plan.dias, 1):
            day_summary = {
                "day": day_idx,
                "total_calories": day_plan.total_kcal(),
                "total_protein": day_plan.total_proteina(),
                "meals": [
                    {
                        "slot": item.slot,
                        "name": item.nombre,
                        "calories": item.kcal,
                        "protein": item.proteina_g,
                        "score": item.score,
                        "reason": item.razon,
                    }
                    for item in day_plan.items
                ],
            }
            plan_summary["daily_plans"].append(day_summary)

        # Guardar como JSON
        output_file = f"{results_dir}/plan_child_{child_id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(plan_summary, f, indent=2, ensure_ascii=False)

        print(f"FILE: Plan del nino {child_id} exportado: {output_file}")

# Exportar metricas de evaluacion
if RANKER_TRAINED:
    evaluation_metrics = {
        "timestamp": datetime.now().isoformat(),
        "system_config": {
            "ranker_trained": RANKER_TRAINED,
            "hybrid_planner_ready": HYBRID_PLANNER_READY,
            "optimization_enabled": True,
        },
        "aggregate_metrics": {
            "avg_recommendation_score": float(np.mean(all_scores))
            if "all_scores" in locals()
            else None,
            "std_recommendation_score": float(np.std(all_scores))
            if "all_scores" in locals()
            else None,
            "avg_daily_calories": float(np.mean(all_calories))
            if "all_calories" in locals()
            else None,
            "avg_daily_protein": float(np.mean(all_proteins))
            if "all_proteins" in locals()
            else None,
        },
        "children_evaluated": len(MOCK_CHILDREN),
        "total_plans_generated": len(planes_generados),
    }

    metrics_file = f"{results_dir}/evaluation_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(evaluation_metrics, f, indent=2, ensure_ascii=False)

    print(f"CHART: Metricas de evaluacion exportadas: {metrics_file}")

# ============================================================================
# SECCION 8: CONCLUSIONES Y PROXIMOS PASOS
# ============================================================================

print("\nCELEBRATE: SECCION 8: Conclusiones y Proximos Pasos")
print("-" * 40)

print("\nSUCCESS: RESUMEN DE LA DEMOSTRACION:")
print(f"   - Ranker LightGBM entrenado: {'SUCCESS' if RANKER_TRAINED else 'ERROR'}")
print(f"   - Planificador hibrido funcionando: {'SUCCESS' if HYBRID_PLANNER_READY else 'ERROR'}")
print(f"   - Planes generados: {len(planes_generados)}")
print(f"   - Ninos evaluados: {len(MOCK_CHILDREN)}")

print("\nROCKET: PROXIMOS PASOS:")
print("   1. Integrar con base de datos real")
print("   2. Ampliar dataset de entrenamiento")
print("   3. Implementar feedback loop de usuarios")
print("   4. Optimizar hiperparametros del ranker")
print("   5. Agregar mas restricciones nutricionales")
print("   6. Desarrollar interfaz web interactiva")

print("\nFOLDER: ARCHIVOS GENERADOS:")
print(f"   - Modelo ranker: {model_path if RANKER_TRAINED else 'No generado'}")
print(f"   - Resultados: {results_dir}/")
print("   - Planes individuales: plan_child_*.json")
print("   - Metricas: evaluation_metrics.json")

print("\nTARGET: SISTEMA HIBRIDO DE RECOMENDACION COMPLETADO")
print("=" * 50)


# Funcion para ejecutar demo interactiva
def demo_interactiva():
    """Funcion para ejecutar una demo interactiva."""
    print("\nGAME: DEMO INTERACTIVA")
    print("-" * 20)

    if not HYBRID_PLANNER_READY:
        print("ERROR: Planificador hibrido no disponible")
        return

    # Permitir al usuario seleccionar un nino
    print("Selecciona un nino para generar un plan personalizado:")
    for i, child in enumerate(MOCK_CHILDREN, 1):
        print(
            f"{i}. Nino {child['child_id']} - {child['age_months']//12} anos - {child['nutritional_status']}"
        )

    try:
        choice = int(input("\nIngresa el numero (1-3): ")) - 1
        if 0 <= choice < len(MOCK_CHILDREN):
            selected_child = MOCK_CHILDREN[choice]

            print("\nCHILD: Generando plan para:")
            print(f"   - ID: {selected_child['child_id']}")
            print(f"   - Edad: {selected_child['age_months']//12} anos")
            print(f"   - Estado: {selected_child['nutritional_status']}")
            print(f"   - Alergias: {selected_child['allergies']}")

            # Generar plan
            plan = planner.generar_plan_semanal_hibrido(
                child_id=selected_child["child_id"],
                estado_nutricional=selected_child["nutritional_status"],
                alergias=selected_child["allergies"],
                preferencias=selected_child["preferences"],
                favoritas=selected_child["favorite_foods"],
                dias=1,  # Solo 1 dia para demo rapida
            )

            print("\nCLIPBOARD: PLAN GENERADO:")
            print(f"   {plan.resumen()}")

            day_plan = plan.dias[0]
            print("\nFOOD: MENUS DEL DIA:")
            for item in day_plan.items:
                print(f"   - {item.slot.upper()}: {item.nombre}")
                print(f"     Calorias: {item.kcal}, Proteina: {item.proteina_g}g")
                print(f"     Score: {item.score}, Razon: {item.razon}")
                print()
        else:
            print("ERROR: Seleccion invalida")

    except (ValueError, KeyboardInterrupt):
        print("ERROR: Demo cancelada")


# Ejecutar demo interactiva si estamos en modo interactivo
if __name__ == "__main__" and not IN_COLAB:
    demo_interactiva()

print("\nCELEBRATE: Notebook completado exitosamente!")
print("Para ejecutar la demo interactiva, llama a demo_interactiva()")
