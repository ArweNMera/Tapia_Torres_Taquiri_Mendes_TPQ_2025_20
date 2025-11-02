"""
Servicio de cálculo nutricional
Maneja cálculos de macronutrientes y requisitos calóricos
"""

from typing import Any, Dict, List, Optional

from src.domain.interfaces.recommender import MacroCalculatorInterface


class NutritionCalculatorService:
    """
    Servicio para cálculos nutricionales
    Calcula macronutrientes, calorías y requisitos basados en edad/sexo/peso
    """

    def __init__(self, calculator: Optional[MacroCalculatorInterface] = None):
        """
        Inicializar servicio

        Args:
            calculator: Implementación del calculador de macros
        """
        self.calculator = calculator

    def calcular_requerimientos(
        self, age_months: int, sex: str, weight_kg: float, activity_level: str = "moderate"
    ) -> Dict[str, Any]:
        """
        Calcular requerimientos nutricionales según edad y sexo

        Args:
            age_months: Edad en meses
            sex: Sexo (M/F)
            weight_kg: Peso en kg
            activity_level: Nivel de actividad (low/moderate/high)

        Returns:
            Requerimientos calóricos y de macronutrientes
        """
        try:
            if not self.calculator:
                raise RuntimeError("Calculador no inicializado")

            # Validaciones
            if age_months < 0 or age_months > 240:
                raise ValueError("age_months debe estar entre 0 y 240")

            if sex not in ["M", "F"]:
                raise ValueError("sex debe ser M o F")

            if weight_kg <= 0:
                raise ValueError("weight_kg debe ser mayor a 0")

            # Calcular
            requirements = self.calculator.calculate_macro_requirements(
                age_months=age_months, sex=sex, weight_kg=weight_kg, activity_level=activity_level
            )

            return {
                "success": True,
                "requirements": requirements,
                "age_months": age_months,
                "weight_kg": weight_kg,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def validar_comida(
        self, meal_data: Dict[str, Any], age_months: int, nutrition_status: str
    ) -> Dict[str, Any]:
        """
        Validar si una comida es apropiada para el niño

        Args:
            meal_data: Datos de la comida (proteína, calorías, etc)
            age_months: Edad del niño
            nutrition_status: Estado nutricional

        Returns:
            Validación con recomendaciones
        """
        try:
            validation = {
                "success": True,
                "meal_id": meal_data.get("id"),
                "appropriate": True,
                "reasons": [],
                "warnings": [],
            }

            # Validar edad apropiada
            min_age = meal_data.get("min_age_months", 0)
            max_age = meal_data.get("max_age_months", 240)

            if age_months < min_age or age_months > max_age:
                validation["appropriate"] = False
                validation["reasons"].append(f"Edad fuera del rango: {min_age}-{max_age} meses")

            # Validar alergias
            allergies_in_meal = meal_data.get("allergens", [])
            if allergies_in_meal:
                validation["warnings"].append(f"Contiene alérgenos: {', '.join(allergies_in_meal)}")

            # Validar valor nutricional según estado
            calories = meal_data.get("calories", 0)
            protein_g = meal_data.get("protein_g", 0)

            if nutrition_status == "DESNUTRICION" and calories < 300:
                validation["warnings"].append("Calorías bajas para niño con desnutrición")

            if protein_g < 5:
                validation["warnings"].append("Proteína baja (menos de 5g)")

            return validation

        except Exception as e:
            return {"success": False, "error": str(e)}

    def calcular_composicion_plan(
        self, meals: List[Dict[str, Any]], days: int = 7
    ) -> Dict[str, Any]:
        """
        Calcular composición nutricional de un plan de menús

        Args:
            meals: Lista de comidas en el plan
            days: Días en el plan

        Returns:
            Totales y promedios nutricionales
        """
        try:
            if not meals:
                raise ValueError("meals no puede estar vacío")

            # Agregar nutrientes
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fat = 0
            meal_count = 0

            for meal in meals:
                total_calories += meal.get("calories", 0)
                total_protein += meal.get("protein_g", 0)
                total_carbs += meal.get("carbs_g", 0)
                total_fat += meal.get("fat_g", 0)
                meal_count += 1

            # Calcular promedios
            avg_meals_per_day = meal_count / days if days > 0 else 0

            composition = {
                "success": True,
                "total_calories": round(total_calories, 2),
                "total_protein_g": round(total_protein, 2),
                "total_carbs_g": round(total_carbs, 2),
                "total_fat_g": round(total_fat, 2),
                "average_calories_per_meal": round(total_calories / meal_count, 2)
                if meal_count > 0
                else 0,
                "average_protein_per_meal": round(total_protein / meal_count, 2)
                if meal_count > 0
                else 0,
                "meals_count": meal_count,
                "days": days,
                "average_meals_per_day": round(avg_meals_per_day, 2),
            }

            return composition

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generar_reporte_nutricional(
        self, child_data: Dict[str, Any], meals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generar reporte nutricional completo

        Args:
            child_data: Datos del niño (edad, peso, sexo, estado)
            meals: Menús recomendados

        Returns:
            Reporte nutricional estructurado
        """
        try:
            # Calcular requerimientos
            requirements = self.calcular_requerimientos(
                age_months=child_data.get("age_months", 60),
                sex=child_data.get("sex", "M"),
                weight_kg=child_data.get("weight_kg", 20),
            )

            # Calcular composición
            composition = self.calcular_composicion_plan(meals=meals, days=7)

            # Construir reporte
            reporte = {
                "success": True,
                "child_info": child_data,
                "requirements": requirements.get("requirements", {}),
                "composition": composition,
                "recommendations": [],
                "warnings": [],
            }

            # Análisis y recomendaciones
            if requirements.get("success"):
                req_calories = requirements.get("requirements", {}).get("calories", 0)
                actual_calories = composition.get("average_calories_per_meal", 0)

                if actual_calories < req_calories * 0.8:
                    reporte["warnings"].append("Calorías por comida por debajo de lo recomendado")
                elif actual_calories > req_calories * 1.2:
                    reporte["recommendations"].append(
                        "Calorías por comida por encima de lo recomendado"
                    )

            return reporte

        except Exception as e:
            return {"success": False, "error": str(e)}
