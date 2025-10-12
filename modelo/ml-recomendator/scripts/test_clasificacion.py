"""
Script de prueba rápida para verificar las 7 categorías OMS.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.features import WHOCalculator


def test_clasificacion():
    """Prueba la clasificación con diferentes valores de BAZ."""

    print("\n" + "=" * 60)
    print("🧪 PRUEBA DE CLASIFICACIÓN OMS (7 CATEGORÍAS)")
    print("=" * 60)

    # Crear calculadora (sin BD, solo para clasificar)
    who_calc = WHOCalculator()

    # Casos de prueba
    test_cases = [
        (-4.5, "DESNUTRICION_SEVERA", 0),
        (-3.5, "DESNUTRICION_SEVERA", 0),
        (-2.5, "DESNUTRICION_MODERADA", 1),
        (-1.5, "RIESGO_DESNUTRICION", 2),
        (0.0, "NORMAL", 3),
        (0.5, "NORMAL", 3),
        (1.5, "RIESGO_SOBREPESO", 4),
        (2.5, "SOBREPESO", 5),
        (3.5, "OBESIDAD", 6),
        (4.0, "OBESIDAD", 6),
    ]

    print("\n📊 Probando clasificaciones:")
    print(f"{'BAZ':<8} {'Esperado':<25} {'Obtenido':<25} {'Label':<6} {'✓/✗'}")
    print("-" * 80)

    all_passed = True
    for baz, expected_class, expected_label in test_cases:
        actual_class = who_calc.classify_nutritional_status(baz)
        actual_label = who_calc.classify_to_label(baz)

        passed = actual_class == expected_class and actual_label == expected_label
        all_passed = all_passed and passed

        status = "✅" if passed else "❌"
        print(f"{baz:<8.2f} {expected_class:<25} {actual_class:<25} {actual_label:<6} {status}")

    print("-" * 80)

    if all_passed:
        print("\n✅ TODAS LAS PRUEBAS PASARON")
        print("\n🎯 Las 7 categorías OMS están correctamente implementadas:")
        print("   0: DESNUTRICION_SEVERA (z < -3.0)")
        print("   1: DESNUTRICION_MODERADA (-3.0 ≤ z < -2.0)")
        print("   2: RIESGO_DESNUTRICION (-2.0 ≤ z < -1.0)")
        print("   3: NORMAL (-1.0 ≤ z ≤ 1.0)")
        print("   4: RIESGO_SOBREPESO (1.0 < z ≤ 2.0)")
        print("   5: SOBREPESO (2.0 < z ≤ 3.0)")
        print("   6: OBESIDAD (z > 3.0)")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        return False

    print("\n" + "=" * 60)
    return True


if __name__ == "__main__":
    success = test_clasificacion()
    sys.exit(0 if success else 1)
