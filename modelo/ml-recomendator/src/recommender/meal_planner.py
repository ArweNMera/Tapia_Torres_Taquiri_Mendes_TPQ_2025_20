"""
Planificador de menús semanales con filtros de alergias, preferencias y estado nutricional.

Enfoque:
- Filtro duro por alergias y estado nutricional (rango de macros por slot).
- Ranking suave por preferencias, comidas favoritas y ajuste a objetivos nutricionales.
- Explicación breve por recomendación.

Este módulo está pensado para integrarse con la BD más adelante; por ahora usa
candidatos mock para demostrar la API y el algoritmo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class MealCandidate:
    """Candidato de comida (menu por slot)."""

    id: int
    nombre: str
    slot: str  # desayuno | almuerzo | cena | snack
    kcal: int
    proteina_g: float
    categorias: List[str]
    ingredientes: List[str]


@dataclass
class MealPlanItem:
    """Item recomendado dentro del plan."""

    id: int
    nombre: str
    slot: str
    kcal: int
    proteina_g: float
    score: float
    razon: str


@dataclass
class DailyMealPlan:
    """Plan diario: contiene las 4 ingestas principales."""

    items: List[MealPlanItem]

    def total_kcal(self) -> int:
        return sum(i.kcal for i in self.items)

    def total_proteina(self) -> float:
        return round(sum(i.proteina_g for i in self.items), 2)


@dataclass
class WeeklyMealPlan:
    """Plan semanal compuesto de 7 días."""

    dias: List[DailyMealPlan]

    def resumen(self) -> Dict[str, float]:
        kcal = sum(d.total_kcal() for d in self.dias)
        prot = sum(d.total_proteina() for d in self.dias)
        return {"kcal_total": kcal, "proteina_total_g": round(prot, 2)}


class MealPlanner:
    """
    Generador de plan de comidas semanal.

    Considera:
    - Perfil y estado nutricional (para fijar objetivos de macro por día y slot).
    - Alergias (filtro duro por ingredientes).
    - Preferencias y comidas favoritas (ranking suave).
    """

    # Proporción de distribución diaria por slot
    SLOT_RATIOS = {"desayuno": 0.25, "almuerzo": 0.35, "cena": 0.30, "snack": 0.10}

    def __init__(self, objetivos_diarios: Dict[str, float] | None = None):
        """
        objetivos_diarios: dict con claves 'kcal' y 'proteina_g'.
        Si no se pasan, se usan objetivos por defecto (estado NORMAL adolescente).
        """
        self.obj = objetivos_diarios or {"kcal": 1800, "proteina_g": 50.0}
        self.candidatos = self._cargar_candidatos_mock()

    def generar_plan_semanal(
        self,
        estado_nutricional: str,
        alergias: List[str],
        preferencias: Dict[str, float],
        favoritas: List[str],
        dias: int = 7,
    ) -> WeeklyMealPlan:
        """Genera un plan de comidas de N días."""
        plan_dias: List[DailyMealPlan] = []

        # Ajuste de objetivos por estado
        objetivos = self._ajustar_objetivos_por_estado(self.obj.copy(), estado_nutricional)

        for _ in range(dias):
            items: List[MealPlanItem] = []
            for slot in ["desayuno", "almuerzo", "cena", "snack"]:
                objetivo_slot = self._objetivo_slot(objetivos, slot)
                candidatos = self._filtrar_candidatos(slot, alergias)
                scored: List[Tuple[MealCandidate, float, str]] = []
                for c in candidatos:
                    score, razon = self._score(
                        c, objetivo_slot, preferencias, favoritas, estado_nutricional
                    )
                    scored.append((c, score, razon))
                scored.sort(key=lambda t: t[1], reverse=True)
                if scored:
                    c, score, razon = scored[0]
                    items.append(
                        MealPlanItem(
                            id=c.id,
                            nombre=c.nombre,
                            slot=c.slot,
                            kcal=c.kcal,
                            proteina_g=c.proteina_g,
                            score=round(score, 2),
                            razon=razon,
                        )
                    )
            plan_dias.append(DailyMealPlan(items=items))

        return WeeklyMealPlan(dias=plan_dias)

    # --------------------------- Helpers ---------------------------------

    def _ajustar_objetivos_por_estado(self, obj: Dict[str, float], estado: str) -> Dict[str, float]:
        """Ajusta objetivos diarios de acuerdo al estado nutricional."""
        estado = (estado or "NORMAL").upper()
        if estado == "SEVERO":
            obj["kcal"] *= 1.20
            obj["proteina_g"] *= 1.30
        elif estado == "MODERADO":
            obj["kcal"] *= 1.10
            obj["proteina_g"] *= 1.15
        elif estado.startswith("RIESGO"):
            obj["kcal"] *= 1.05
            obj["proteina_g"] *= 1.10
        elif estado in {"SOBREPESO", "OBESIDAD"}:
            obj["kcal"] *= 0.90
            obj["proteina_g"] *= 1.05
        return obj

    def _objetivo_slot(self, objetivos: Dict[str, float], slot: str) -> Dict[str, float]:
        ratio = self.SLOT_RATIOS.get(slot, 0.25)
        return {"kcal": objetivos["kcal"] * ratio, "proteina_g": objetivos["proteina_g"] * ratio}

    def _filtrar_candidatos(self, slot: str, alergias: List[str]) -> List[MealCandidate]:
        alergias_set = {a.lower() for a in alergias}
        out: List[MealCandidate] = []
        for c in self.candidatos:
            if c.slot != slot:
                continue
            if any(a in alergias_set for a in (ing.lower() for ing in c.ingredientes)):
                continue
            out.append(c)
        return out

    def _score(
        self,
        c: MealCandidate,
        objetivo: Dict[str, float],
        preferencias: Dict[str, float],
        favoritas: List[str],
        estado_nutricional: str,
    ) -> Tuple[float, str]:
        """Calcula el score multi‑objetivo y explica brevemente."""
        # 1) Ajuste macro (kcal/proteina) al objetivo del slot
        kcal_fit = 1.0 - min(abs(c.kcal - objetivo["kcal"]) / max(objetivo["kcal"], 1), 1.0)
        prot_fit = 1.0 - min(
            abs(c.proteina_g - objetivo["proteina_g"]) / max(objetivo["proteina_g"], 1), 1.0
        )
        macro_fit = 0.6 * kcal_fit + 0.4 * prot_fit  # ponderación simple

        # 2) Preferencias por categorías (ej. 'vegetariano', 'lacteos', 'proteico', etc.)
        pref_score = 0.0
        for cat in c.categorias:
            pref_score += preferencias.get(cat, 0.0)
        pref_score = min(pref_score, 1.0)  # normalizar

        # 3) Boost por comidas favoritas presentes en ingredientes
        fav_set = {f.lower() for f in favoritas}
        fav_hits = sum(1 for ing in c.ingredientes if ing.lower() in fav_set)
        fav_boost = min(0.2 * fav_hits, 0.4)

        # 4) Ajuste por estado (menus energéticos/proteicos cuando corresponde)
        estado = (estado_nutricional or "NORMAL").upper()
        status_adj = 0.0
        if (
            estado in {"SEVERO", "MODERADO", "RIESGO_DESNUTRICION"}
            and c.categorias
            and ("proteico" in c.categorias or "recuperacion" in c.categorias)
        ):
            status_adj = 0.1
        if estado in {"SOBREPESO", "OBESIDAD"} and (
            "ligero" in c.categorias or "alto_fibra" in c.categorias
        ):
            status_adj = 0.1

        # Ponderación final (0-100)
        score = 100.0 * (
            0.45 * macro_fit + 0.30 * pref_score + 0.15 * fav_boost + 0.10 * status_adj
        )

        razon_parts = []
        if macro_fit > 0.7:
            razon_parts.append("Ajuste nutricional adecuado")
        if pref_score > 0.3:
            razon_parts.append("Coincide con preferencias")
        if fav_boost > 0.0:
            razon_parts.append("Incluye favoritas")
        if status_adj > 0.0:
            razon_parts.append("Compatible con estado")
        if not razon_parts:
            razon_parts.append("Balance general aceptable")

        return score, " | ".join(razon_parts)

    def _cargar_candidatos_mock(self) -> List[MealCandidate]:
        """Crea un conjunto mínimo de candidatos por slot para demo y pruebas."""
        return [
            # Desayunos
            MealCandidate(
                1, "Desayuno Proteico", "desayuno", 450, 20, ["proteico"], ["huevo", "pan", "leche"]
            ),
            MealCandidate(
                2,
                "Desayuno Ligero",
                "desayuno",
                350,
                12,
                ["ligero", "alto_fibra"],
                ["yogur", "granola", "fruta"],
            ),
            MealCandidate(
                3,
                "Desayuno Vegetariano",
                "desayuno",
                400,
                15,
                ["vegetariano"],
                ["avena", "fruta", "nuez"],
            ),
            # Almuerzos
            MealCandidate(
                10,
                "Almuerzo Recuperación",
                "almuerzo",
                650,
                35,
                ["proteico", "recuperacion"],
                ["pollo", "arroz", "ensalada"],
            ),
            MealCandidate(
                11,
                "Almuerzo Balanceado",
                "almuerzo",
                550,
                25,
                ["balanceado"],
                ["carne", "quinoa", "verduras"],
            ),
            MealCandidate(
                12,
                "Almuerzo Vegetariano",
                "almuerzo",
                520,
                22,
                ["vegetariano"],
                ["legumbres", "arroz", "verduras"],
            ),
            # Cenas
            MealCandidate(
                20,
                "Cena Mantenimiento",
                "cena",
                540,
                24,
                ["balanceado"],
                ["pescado", "papa", "ensalada"],
            ),
            MealCandidate(
                21,
                "Cena Ligera",
                "cena",
                480,
                20,
                ["ligero", "alto_fibra"],
                ["sopa", "pan", "verduras"],
            ),
            MealCandidate(
                22,
                "Cena Vegetariana",
                "cena",
                500,
                21,
                ["vegetariano"],
                ["tofu", "fideos", "verduras"],
            ),
            # Snacks
            MealCandidate(
                30, "Snack Fruta y Yogur", "snack", 180, 8, ["ligero"], ["fruta", "yogur"]
            ),
            MealCandidate(
                31, "Snack Frutos Secos", "snack", 220, 7, ["alto_fibra"], ["nuez", "almendra"]
            ),
            MealCandidate(
                32,
                "Snack Sándwich Pequeño",
                "snack",
                250,
                10,
                ["proteico"],
                ["pan", "jamon", "queso"],
            ),
        ]


if __name__ == "__main__":
    preferencias = {"vegetariano": 0.4, "alto_fibra": 0.3}
    favoritas = ["fruta", "yogur"]
    planner = MealPlanner({"kcal": 1800, "proteina_g": 50.0})
    plan = planner.generar_plan_semanal(
        estado_nutricional="RIESGO_DESNUTRICION",
        alergias=["almendra"],
        preferencias=preferencias,
        favoritas=favoritas,
        dias=2,
    )
    print("Resumen semanal:", plan.resumen())
    for idx, dia in enumerate(plan.dias, 1):
        print(f"\nDía {idx}")
        for it in dia.items:
            print(
                f"- {it.slot}: {it.nombre} ({it.kcal} kcal, {it.proteina_g}g) -> {it.score} | {it.razon}"
            )
