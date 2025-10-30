"""
Módulo de optimización para ensamblar planes de comida usando OR-Tools CP-SAT.
Combina las predicciones del ranker con restricciones nutricionales y de variedad.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from ortools.sat.python import cp_model

logger = logging.getLogger(__name__)


@dataclass
class NutritionalConstraints:
    """Restricciones nutricionales para la optimización."""

    min_calories: float
    max_calories: float
    min_protein: float
    max_protein: float
    min_carbs: float
    max_carbs: float
    min_fat: float
    max_fat: float
    min_fiber: Optional[float] = None
    max_sodium: Optional[float] = None
    min_calcium: Optional[float] = None
    min_iron: Optional[float] = None


@dataclass
class MealPlanConstraints:
    """Restricciones del plan de comidas."""

    days: int = 7  # Número de días
    meals_per_day: int = 3  # Comidas por día (desayuno, almuerzo, cena)
    max_repetitions: int = 2  # Máximo de repeticiones del mismo menú
    min_variety_score: float = 0.7  # Puntuación mínima de variedad
    allergen_restrictions: List[str] = None  # Lista de alérgenos a evitar

    def __post_init__(self):
        if self.allergen_restrictions is None:
            self.allergen_restrictions = []


class MealPlanOptimizer:
    """Optimizador de planes de comida usando CP-SAT de OR-Tools."""

    def __init__(
        self,
        nutritional_constraints: NutritionalConstraints,
        plan_constraints: MealPlanConstraints,
        solver_time_limit: int = 300,
    ):
        """
        Inicializar el optimizador.

        Args:
            nutritional_constraints: Restricciones nutricionales
            plan_constraints: Restricciones del plan de comidas
            solver_time_limit: Límite de tiempo del solver en segundos
        """
        self.nutritional_constraints = nutritional_constraints
        self.plan_constraints = plan_constraints
        self.solver_time_limit = solver_time_limit

    def _calculate_variety_score(
        self, selected_menus: List[Dict], menu_features: pd.DataFrame
    ) -> float:
        """
        Calcular puntuación de variedad basada en diversidad de ingredientes y tipos de comida.

        Args:
            selected_menus: Lista de menús seleccionados
            menu_features: DataFrame con características de los menús

        Returns:
            Puntuación de variedad (0-1)
        """
        if not selected_menus:
            return 0.0

        menu_ids = [menu["menu_id"] for menu in selected_menus]
        selected_features = menu_features[menu_features["menu_id"].isin(menu_ids)]

        # Calcular diversidad de tipos de comida
        meal_types = (
            selected_features["meal_type"].unique()
            if "meal_type" in selected_features.columns
            else []
        )
        type_diversity = (
            len(meal_types) / max(len(selected_features["meal_type"].unique()), 1)
            if "meal_type" in selected_features.columns
            else 0.5
        )

        # Calcular diversidad nutricional (varianza normalizada)
        nutritional_cols = ["calories", "protein", "carbs", "fat"]
        available_cols = [col for col in nutritional_cols if col in selected_features.columns]

        if available_cols:
            nutritional_variance = selected_features[available_cols].var().mean()
            # Normalizar la varianza (esto es una aproximación)
            nutritional_diversity = min(nutritional_variance / 1000, 1.0)
        else:
            nutritional_diversity = 0.5

        # Calcular diversidad de ingredientes (si está disponible)
        ingredient_diversity = 0.5  # Valor por defecto
        if "main_ingredients" in selected_features.columns:
            all_ingredients = set()
            for ingredients in selected_features["main_ingredients"].dropna():
                if isinstance(ingredients, str):
                    all_ingredients.update(ingredients.split(","))
            ingredient_diversity = min(len(all_ingredients) / (len(selected_menus) * 3), 1.0)

        # Combinar las diversidades
        variety_score = (
            type_diversity * 0.4 + nutritional_diversity * 0.3 + ingredient_diversity * 0.3
        )

        return min(variety_score, 1.0)

    def _check_allergen_compatibility(self, menu: Dict, allergen_restrictions: List[str]) -> bool:
        """
        Verificar si un menú es compatible con las restricciones de alérgenos.

        Args:
            menu: Diccionario con información del menú
            allergen_restrictions: Lista de alérgenos a evitar

        Returns:
            True si es compatible, False en caso contrario
        """
        if not allergen_restrictions:
            return True

        menu_allergens = menu.get("allergens", [])
        if isinstance(menu_allergens, str):
            menu_allergens = menu_allergens.split(",")

        # Verificar si hay intersección entre alérgenos del menú y restricciones
        return not bool(set(menu_allergens) & set(allergen_restrictions))

    def optimize_meal_plan(
        self, candidate_menus: List[Dict], ranker_scores: List[float], child_profile: Dict
    ) -> Tuple[List[Dict], Dict]:
        """
        Optimizar el plan de comidas usando CP-SAT.

        Args:
            candidate_menus: Lista de menús candidatos
            ranker_scores: Puntuaciones del ranker para cada menú
            child_profile: Perfil del niño con información nutricional

        Returns:
            Tuple con (plan_optimizado, métricas_optimización)
        """
        logger.info(f"Optimizando plan de comidas con {len(candidate_menus)} candidatos...")

        # Crear el modelo
        model = cp_model.CpModel()

        # Variables de decisión: x[i][d][m] = 1 si el menú i se asigna al día d, comida m
        num_menus = len(candidate_menus)
        num_days = self.plan_constraints.days
        num_meals = self.plan_constraints.meals_per_day

        x = {}
        for i in range(num_menus):
            for d in range(num_days):
                for m in range(num_meals):
                    x[i, d, m] = model.NewBoolVar(f"menu_{i}_day_{d}_meal_{m}")

        # Restricción: exactamente un menú por comida por día
        for d in range(num_days):
            for m in range(num_meals):
                model.Add(sum(x[i, d, m] for i in range(num_menus)) == 1)

        # Restricción: máximo de repeticiones por menú
        for i in range(num_menus):
            model.Add(
                sum(x[i, d, m] for d in range(num_days) for m in range(num_meals))
                <= self.plan_constraints.max_repetitions
            )

        # Restricciones nutricionales diarias
        for d in range(num_days):
            # Calorías diarias
            daily_calories = sum(
                candidate_menus[i].get("calories", 0) * x[i, d, m]
                for i in range(num_menus)
                for m in range(num_meals)
            )
            model.Add(daily_calories >= self.nutritional_constraints.min_calories)
            model.Add(daily_calories <= self.nutritional_constraints.max_calories)

            # Proteínas diarias
            daily_protein = sum(
                candidate_menus[i].get("protein", 0) * x[i, d, m]
                for i in range(num_menus)
                for m in range(num_meals)
            )
            model.Add(daily_protein >= self.nutritional_constraints.min_protein)
            model.Add(daily_protein <= self.nutritional_constraints.max_protein)

            # Carbohidratos diarios
            daily_carbs = sum(
                candidate_menus[i].get("carbs", 0) * x[i, d, m]
                for i in range(num_menus)
                for m in range(num_meals)
            )
            model.Add(daily_carbs >= self.nutritional_constraints.min_carbs)
            model.Add(daily_carbs <= self.nutritional_constraints.max_carbs)

            # Grasas diarias
            daily_fat = sum(
                candidate_menus[i].get("fat", 0) * x[i, d, m]
                for i in range(num_menus)
                for m in range(num_meals)
            )
            model.Add(daily_fat >= self.nutritional_constraints.min_fat)
            model.Add(daily_fat <= self.nutritional_constraints.max_fat)

        # Restricciones de alérgenos
        for i in range(num_menus):
            if not self._check_allergen_compatibility(
                candidate_menus[i], self.plan_constraints.allergen_restrictions
            ):
                # Prohibir este menú
                for d in range(num_days):
                    for m in range(num_meals):
                        model.Add(x[i, d, m] == 0)

        # Función objetivo: maximizar puntuaciones del ranker
        objective = sum(
            ranker_scores[i] * x[i, d, m]
            for i in range(num_menus)
            for d in range(num_days)
            for m in range(num_meals)
        )
        model.Maximize(objective)

        # Resolver el modelo
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.solver_time_limit

        logger.info("Resolviendo modelo de optimización...")
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info(f"Solución encontrada (status: {solver.StatusName(status)})")

            # Extraer la solución
            meal_plan = []
            for d in range(num_days):
                day_meals = []
                for m in range(num_meals):
                    for i in range(num_menus):
                        if solver.Value(x[i, d, m]) == 1:
                            menu_info = candidate_menus[i].copy()
                            menu_info["day"] = d + 1
                            menu_info["meal"] = m + 1
                            menu_info["ranker_score"] = ranker_scores[i]
                            day_meals.append(menu_info)
                            break
                meal_plan.extend(day_meals)

            # Calcular métricas
            total_score = solver.ObjectiveValue()
            variety_score = self._calculate_variety_score(meal_plan, pd.DataFrame(candidate_menus))

            # Calcular estadísticas nutricionales
            daily_nutrition = []
            for d in range(num_days):
                day_menus = [menu for menu in meal_plan if menu["day"] == d + 1]
                daily_calories = sum(menu.get("calories", 0) for menu in day_menus)
                daily_protein = sum(menu.get("protein", 0) for menu in day_menus)
                daily_carbs = sum(menu.get("carbs", 0) for menu in day_menus)
                daily_fat = sum(menu.get("fat", 0) for menu in day_menus)

                daily_nutrition.append(
                    {
                        "day": d + 1,
                        "calories": daily_calories,
                        "protein": daily_protein,
                        "carbs": daily_carbs,
                        "fat": daily_fat,
                    }
                )

            metrics = {
                "optimization_status": solver.StatusName(status),
                "total_ranker_score": total_score,
                "variety_score": variety_score,
                "solve_time_seconds": solver.WallTime(),
                "daily_nutrition": daily_nutrition,
                "constraints_satisfied": True,
            }

            logger.info("Plan optimizado generado exitosamente:")
            logger.info(f"  - Puntuación total del ranker: {total_score:.2f}")
            logger.info(f"  - Puntuación de variedad: {variety_score:.2f}")
            logger.info(f"  - Tiempo de resolución: {solver.WallTime():.2f}s")

            return meal_plan, metrics

        else:
            logger.error(
                f"No se pudo encontrar una solución factible (status: {solver.StatusName(status)})"
            )

            # Retornar plan básico usando solo las mejores puntuaciones
            sorted_indices = np.argsort(ranker_scores)[::-1]
            basic_plan = []

            meals_needed = num_days * num_meals
            for i in range(min(meals_needed, len(candidate_menus))):
                menu_idx = sorted_indices[i % len(sorted_indices)]
                menu_info = candidate_menus[menu_idx].copy()
                menu_info["day"] = (i // num_meals) + 1
                menu_info["meal"] = (i % num_meals) + 1
                menu_info["ranker_score"] = ranker_scores[menu_idx]
                basic_plan.append(menu_info)

            metrics = {
                "optimization_status": solver.StatusName(status),
                "total_ranker_score": 0,
                "variety_score": 0,
                "solve_time_seconds": solver.WallTime(),
                "daily_nutrition": [],
                "constraints_satisfied": False,
            }

            return basic_plan, metrics


class SimpleLinearOptimizer:
    """Optimizador alternativo usando programación lineal simple con PuLP."""

    def __init__(
        self, nutritional_constraints: NutritionalConstraints, plan_constraints: MealPlanConstraints
    ):
        """
        Inicializar el optimizador lineal.

        Args:
            nutritional_constraints: Restricciones nutricionales
            plan_constraints: Restricciones del plan de comidas
        """
        self.nutritional_constraints = nutritional_constraints
        self.plan_constraints = plan_constraints

        try:
            import pulp

            self.pulp = pulp
            self.available = True
        except ImportError:
            logger.warning("PuLP no está disponible. Usar MealPlanOptimizer en su lugar.")
            self.available = False

    def optimize_meal_plan(
        self, candidate_menus: List[Dict], ranker_scores: List[float], child_profile: Dict
    ) -> Tuple[List[Dict], Dict]:
        """
        Optimizar usando programación lineal simple.

        Args:
            candidate_menus: Lista de menús candidatos
            ranker_scores: Puntuaciones del ranker
            child_profile: Perfil del niño

        Returns:
            Tuple con (plan_optimizado, métricas)
        """
        if not self.available:
            raise ImportError("PuLP no está disponible")

        logger.info("Optimizando con programación lineal simple...")

        # Crear problema de maximización
        prob = self.pulp.LpProblem("MealPlan", self.pulp.LpMaximize)

        # Variables de decisión
        num_menus = len(candidate_menus)
        x = [self.pulp.LpVariable(f"menu_{i}", cat="Binary") for i in range(num_menus)]

        # Función objetivo
        prob += self.pulp.lpSum([ranker_scores[i] * x[i] for i in range(num_menus)])

        # Restricciones básicas
        total_meals = self.plan_constraints.days * self.plan_constraints.meals_per_day
        prob += self.pulp.lpSum(x) == total_meals

        # Restricciones nutricionales promedio
        avg_calories = (
            self.pulp.lpSum(
                [candidate_menus[i].get("calories", 0) * x[i] for i in range(num_menus)]
            )
            / total_meals
        )
        prob += (
            avg_calories
            >= self.nutritional_constraints.min_calories / self.plan_constraints.meals_per_day
        )
        prob += (
            avg_calories
            <= self.nutritional_constraints.max_calories / self.plan_constraints.meals_per_day
        )

        # Resolver
        prob.solve(self.pulp.PULP_CBC_CMD(msg=0))

        if prob.status == 1:  # Optimal
            selected_menus = []
            for i in range(num_menus):
                if x[i].varValue == 1:
                    menu_info = candidate_menus[i].copy()
                    menu_info["ranker_score"] = ranker_scores[i]
                    selected_menus.append(menu_info)

            # Asignar días y comidas
            for idx, menu in enumerate(selected_menus):
                menu["day"] = (idx // self.plan_constraints.meals_per_day) + 1
                menu["meal"] = (idx % self.plan_constraints.meals_per_day) + 1

            metrics = {
                "optimization_status": "OPTIMAL",
                "total_ranker_score": self.pulp.value(prob.objective),
                "constraints_satisfied": True,
            }

            return selected_menus, metrics

        else:
            logger.error("No se pudo resolver el problema de optimización lineal")
            return [], {"optimization_status": "INFEASIBLE", "constraints_satisfied": False}
