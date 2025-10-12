#!/usr/bin/env python3
"""
Script para verificar el cálculo de BAZ en adolescentes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import WHO_DIR, _baz_from_bmi, _load_lms, _nearest_lms

# Casos de prueba
casos = [
    {
        "nombre": "Anthony Rojas Balvin",
        "edad_meses": 15 * 12 + 4,  # 184 meses
        "sexo": "M",
        "peso_kg": 55,
        "talla_cm": 160,
        "clasificacion_esperada": "NORMAL o RIESGO_SOBREPESO",
    },
    {
        "nombre": "Jhon Quispe Torres",
        "edad_meses": 14 * 12,  # 168 meses
        "sexo": "M",
        "peso_kg": 40,
        "talla_cm": 150,
        "clasificacion_esperada": "NORMAL",
    },
    {
        "nombre": "Luis Quispe Lopeze",
        "edad_meses": 9 * 12 + 4,  # 112 meses
        "sexo": "M",
        "peso_kg": 25,
        "talla_cm": 130,
        "clasificacion_esperada": "NORMAL",
    },
    {
        "nombre": "Kevin Mendez Roca",
        "edad_meses": 11 * 12 + 4,  # 136 meses
        "sexo": "M",
        "peso_kg": 30,
        "talla_cm": 135,
        "clasificacion_esperada": "NORMAL",
    },
]

print("=" * 80)
print("VERIFICACIÓN DE CÁLCULO BAZ - ADOLESCENTES")
print("=" * 80)
print()

# Cargar tablas OMS
try:
    LMS = _load_lms(WHO_DIR)
    print(f"✅ Tablas OMS cargadas: {len(LMS)} registros")
    print(f"   Rango de edad: {LMS['month'].min()} - {LMS['month'].max()} meses")
    print()
except Exception as e:
    print(f"❌ Error cargando tablas OMS: {e}")
    sys.exit(1)

# Verificar cada caso
for caso in casos:
    print("-" * 80)
    print(f"👤 {caso['nombre']}")
    print(
        f"   Edad: {caso['edad_meses']} meses ({caso['edad_meses']//12} años {caso['edad_meses']%12} meses)"
    )
    print(f"   Sexo: {caso['sexo']}")
    print(f"   Peso: {caso['peso_kg']} kg")
    print(f"   Talla: {caso['talla_cm']} cm")
    print()

    # Calcular IMC
    altura_m = caso["talla_cm"] / 100.0
    imc = caso["peso_kg"] / (altura_m**2)
    print(f"   📊 IMC calculado: {imc:.2f}")

    # Obtener LMS
    try:
        L, M, S = _nearest_lms(LMS, caso["sexo"], caso["edad_meses"])
        print(f"   📈 Valores LMS (edad {caso['edad_meses']} meses, sexo {caso['sexo']}):")
        print(f"      L = {L:.4f}")
        print(f"      M = {M:.4f}")
        print(f"      S = {S:.4f}")

        # Calcular BAZ
        baz = _baz_from_bmi(imc, L, M, S)
        print(f"   🎯 BAZ calculado: {baz:.2f}")

        # Clasificar según BAZ
        if baz < -3:
            clasificacion = "DESNUTRICION_SEVERA"
        elif -3 <= baz < -2:
            clasificacion = "DESNUTRICION_MODERADA"
        elif -2 <= baz < -1:
            clasificacion = "RIESGO_DESNUTRICION"
        elif -1 <= baz <= 1:
            clasificacion = "NORMAL"
        elif 1 < baz <= 2:
            clasificacion = "RIESGO_SOBREPESO"
        elif 2 < baz <= 3:
            clasificacion = "SOBREPESO"
        else:
            clasificacion = "OBESIDAD"

        print(f"   ✅ Clasificación: {clasificacion}")
        print(f"   📝 Esperado: {caso['clasificacion_esperada']}")

        # Verificar si coincide
        if clasificacion in caso["clasificacion_esperada"]:
            print("   ✅ CORRECTO")
        else:
            print("   ⚠️  POSIBLE ERROR")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

print("=" * 80)
print("VERIFICACIÓN DE TABLAS OMS")
print("=" * 80)
print()

# Verificar que tenemos datos para adolescentes
for sexo in ["M", "F"]:
    datos_sexo = LMS[LMS["sex"] == sexo]
    print(f"Sexo {sexo}:")
    print(f"  Registros: {len(datos_sexo)}")
    print(f"  Rango edad: {datos_sexo['month'].min()} - {datos_sexo['month'].max()} meses")
    print(f"  Rango edad: {datos_sexo['month'].min()//12} - {datos_sexo['month'].max()//12} años")

    # Verificar si tenemos datos para 14-15 años
    edad_14 = 14 * 12
    edad_15 = 15 * 12
    tiene_14 = len(datos_sexo[datos_sexo["month"] == edad_14]) > 0
    tiene_15 = len(datos_sexo[datos_sexo["month"] == edad_15]) > 0

    print(f"  ¿Tiene datos para 14 años ({edad_14} meses)? {tiene_14}")
    print(f"  ¿Tiene datos para 15 años ({edad_15} meses)? {tiene_15}")
    print()
