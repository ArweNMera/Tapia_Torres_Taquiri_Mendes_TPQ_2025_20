"""
Verificar caso específico
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.features.who_calculator import WHOCalculator
from src.utils.db_connector import DatabaseConnector

# Datos del caso
edad_meses = 118  # 9.8 años
sexo = 'M'
peso_kg = 40
talla_cm = 145
bmi = peso_kg / (talla_cm / 100) ** 2

print("=" * 60)
print("VERIFICANDO CASO")
print("=" * 60)
print(f"\nDatos:")
print(f"  Edad: {edad_meses} meses ({edad_meses/12:.1f} años)")
print(f"  Sexo: {sexo}")
print(f"  Peso: {peso_kg} kg")
print(f"  Talla: {talla_cm} cm")
print(f"  BMI: {bmi:.2f}")

# Calcular BAZ usando tablas OMS
print("\n🔢 Calculando BAZ con tablas OMS...")
db = DatabaseConnector.from_env()
db.connect()

who_calc = WHOCalculator(db_connector=db)

try:
    baz = who_calc.calculate_baz(bmi, edad_meses, sexo)
    clasificacion = who_calc.classify_nutritional_status(baz)
    
    print(f"\n✅ Resultado OMS:")
    print(f"  BAZ: {baz:.2f}")
    print(f"  Clasificación: {clasificacion}")
    
    # Verificar rangos
    print(f"\n📊 Rangos OMS:")
    print(f"  < -3.0: DESNUTRICION_SEVERA")
    print(f"  -3.0 a -2.0: DESNUTRICION_MODERADA")
    print(f"  -2.0 a -1.0: RIESGO_DESNUTRICION")
    print(f"  -1.0 a 1.0: NORMAL ✅")
    print(f"  1.0 a 2.0: RIESGO_SOBREPESO")
    print(f"  2.0 a 3.0: SOBREPESO")
    print(f"  > 3.0: OBESIDAD")
    
    # Comparar con lo que predijo el modelo
    print(f"\n🤖 El modelo predijo: DESNUTRICION_SEVERA")
    print(f"   Esto sugiere que el modelo aprendió mal o los datos de entrenamiento están incorrectos")
    
except Exception as e:
    print(f"❌ Error: {e}")

db.disconnect()

print("\n" + "=" * 60)
print("CONCLUSIÓN")
print("=" * 60)
print("El modelo necesita ser reentrenado con datos correctos.")
print("Los datos de entrenamiento probablemente tienen BAZ mal calculado.")
