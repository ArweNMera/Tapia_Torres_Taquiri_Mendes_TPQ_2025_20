#!/usr/bin/env python3
"""
Script para probar el modelo Bayesian + Random Forest
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.models.direct_classifier import cargar_modelo_directo


def test_modelo():
    """Prueba el modelo con casos de ejemplo."""

    print("=" * 70)
    print("🧪 PROBANDO MODELO BAYESIAN + RANDOM FOREST")
    print("=" * 70)

    # Cargar modelo
    print("\n📦 Cargando modelo...")
    try:
        modelo = cargar_modelo_directo()
        print("✅ Modelo cargado exitosamente")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\n💡 Primero entrena el modelo:")
        print("   ./entrenar_modelo_directo.sh")
        return

    # Casos de prueba
    casos = [
        {
            "nombre": "Niño normal de 3 años",
            "edad_meses": 36,
            "sexo": "M",
            "peso_kg": 14.5,
            "talla_cm": 95.0,
            "esperado": "NORMAL",
        },
        {
            "nombre": "Bebé con desnutrición",
            "edad_meses": 12,
            "sexo": "F",
            "peso_kg": 7.0,
            "talla_cm": 70.0,
            "esperado": "DESNUTRICION_MODERADA o SEVERA",
        },
        {
            "nombre": "Niño con sobrepeso de 8 años",
            "edad_meses": 96,
            "sexo": "M",
            "peso_kg": 35.0,
            "talla_cm": 125.0,
            "esperado": "SOBREPESO u OBESIDAD",
        },
        {
            "nombre": "Adolescente normal de 15 años",
            "edad_meses": 180,
            "sexo": "F",
            "peso_kg": 55.0,
            "talla_cm": 160.0,
            "esperado": "NORMAL",
        },
    ]

    print("\n" + "=" * 70)
    print("📊 RESULTADOS DE CLASIFICACIÓN")
    print("=" * 70)

    for i, caso in enumerate(casos, 1):
        print(f"\n{i}. {caso['nombre']}")
        print(
            f"   Datos: {caso['edad_meses']} meses, {caso['sexo']}, "
            f"{caso['peso_kg']} kg, {caso['talla_cm']} cm"
        )

        # Predecir
        resultado = modelo.predecir(
            edad_meses=caso["edad_meses"],
            sexo=caso["sexo"],
            peso_kg=caso["peso_kg"],
            talla_cm=caso["talla_cm"],
        )

        # Mostrar resultado
        print(f"   ✅ Clasificación: {resultado['clasificacion']}")
        print(f"   📊 Confianza: {resultado['confianza']:.2%}")
        print(f"   🎯 Esperado: {caso['esperado']}")

        # Top 3 probabilidades
        probs = sorted(resultado["probabilidades"].items(), key=lambda x: x[1], reverse=True)[:3]

        print("   📈 Top 3 probabilidades:")
        for cat, prob in probs:
            print(f"      - {cat}: {prob:.2%}")

    # Explicación detallada de un caso
    print("\n" + "=" * 70)
    print("🔍 EXPLICACIÓN DETALLADA (Caso 1)")
    print("=" * 70)

    caso = casos[0]
    explicacion = modelo.explicar_prediccion(
        edad_meses=caso["edad_meses"],
        sexo=caso["sexo"],
        peso_kg=caso["peso_kg"],
        talla_cm=caso["talla_cm"],
    )

    print(f"\n📝 Predicción: {explicacion['prediccion']}")
    print(f"📊 Confianza: {explicacion['confianza']:.2%}")
    print("\n📋 Datos de entrada:")
    for key, value in explicacion["datos_entrada"].items():
        print(f"   - {key}: {value}")

    print("\n💡 Contexto:")
    print(f"   {explicacion['contexto']}")

    print("\n📈 Top 3 probabilidades:")
    for item in explicacion["probabilidades_top3"]:
        print(f"   - {item['categoria']}: {item['probabilidad']:.2%}")

    print("\n" + "=" * 70)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 70)
    print("\n💡 El modelo usa:")
    print("   - Naive Bayes (Bayesian) para clasificación probabilística")
    print("   - Random Forest para clasificación robusta")
    print("   - Ensemble para combinar ambos modelos")


if __name__ == "__main__":
    test_modelo()
