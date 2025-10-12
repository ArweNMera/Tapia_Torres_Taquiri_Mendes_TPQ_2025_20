"""
Mapeo de clasificaciones nutricionales OMS.
Centraliza la conversión entre labels numéricos y nombres de categorías.
"""

# Mapeo de labels a nombres de categorías (7 categorías OMS)
LABEL_TO_CATEGORY = {
    0: "DESNUTRICION_SEVERA",
    1: "DESNUTRICION_MODERADA",
    2: "RIESGO_DESNUTRICION",
    3: "NORMAL",
    4: "RIESGO_SOBREPESO",
    5: "SOBREPESO",
    6: "OBESIDAD",
}

# Mapeo inverso
CATEGORY_TO_LABEL = {v: k for k, v in LABEL_TO_CATEGORY.items()}

# Nombres amigables para mostrar en UI
CATEGORY_DISPLAY_NAMES = {
    "DESNUTRICION_SEVERA": "Desnutrición Severa",
    "DESNUTRICION_MODERADA": "Desnutrición Moderada",
    "RIESGO_DESNUTRICION": "Riesgo de Desnutrición",
    "NORMAL": "Normal",
    "RIESGO_SOBREPESO": "Riesgo de Sobrepeso",
    "SOBREPESO": "Sobrepeso",
    "OBESIDAD": "Obesidad",
}

# Nombres cortos para gráficas
CATEGORY_SHORT_NAMES = {
    "DESNUTRICION_SEVERA": "DESNUT_SEV",
    "DESNUTRICION_MODERADA": "DESNUT_MOD",
    "RIESGO_DESNUTRICION": "RIESGO_DESN",
    "NORMAL": "NORMAL",
    "RIESGO_SOBREPESO": "RIESGO_SOB",
    "SOBREPESO": "SOBREPESO",
    "OBESIDAD": "OBESIDAD",
}

# Colores para cada categoría (para gráficas)
CATEGORY_COLORS = {
    "DESNUTRICION_SEVERA": "#c0392b",
    "DESNUTRICION_MODERADA": "#e74c3c",
    "RIESGO_DESNUTRICION": "#e67e22",
    "NORMAL": "#2ecc71",
    "RIESGO_SOBREPESO": "#f39c12",
    "SOBREPESO": "#d35400",
    "OBESIDAD": "#8e44ad",
}

# Niveles de severidad (para ordenamiento)
CATEGORY_SEVERITY = {
    "DESNUTRICION_SEVERA": 6,
    "DESNUTRICION_MODERADA": 5,
    "RIESGO_DESNUTRICION": 4,
    "NORMAL": 0,
    "RIESGO_SOBREPESO": 1,
    "SOBREPESO": 2,
    "OBESIDAD": 3,
}


def label_to_category(label: int) -> str:
    """Convierte label numérico a nombre de categoría."""
    return LABEL_TO_CATEGORY.get(label, "UNKNOWN")


def category_to_label(category: str) -> int:
    """Convierte nombre de categoría a label numérico."""
    return CATEGORY_TO_LABEL.get(category, -1)


def get_display_name(category: str) -> str:
    """Obtiene nombre amigable para mostrar."""
    return CATEGORY_DISPLAY_NAMES.get(category, category)


def get_short_name(category: str) -> str:
    """Obtiene nombre corto para gráficas."""
    return CATEGORY_SHORT_NAMES.get(category, category)


def get_color(category: str) -> str:
    """Obtiene color para la categoría."""
    return CATEGORY_COLORS.get(category, "#95a5a6")


def get_all_categories() -> list:
    """Retorna lista de todas las categorías en orden."""
    return [
        "DESNUTRICION_SEVERA",
        "DESNUTRICION_MODERADA",
        "RIESGO_DESNUTRICION",
        "NORMAL",
        "RIESGO_SOBREPESO",
        "SOBREPESO",
        "OBESIDAD",
    ]


def get_all_labels() -> list:
    """Retorna lista de todos los labels en orden."""
    return list(range(7))
