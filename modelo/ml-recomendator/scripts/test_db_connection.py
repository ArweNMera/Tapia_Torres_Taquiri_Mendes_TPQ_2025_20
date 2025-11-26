"""
Script para probar la conexión a la base de datos.
"""

import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

db_url = os.getenv("DATABASE_URL")

print("=" * 80)
print("🔍 PRUEBA DE CONEXIÓN A BASE DE DATOS")
print("=" * 80)
print(f"\n📊 DATABASE_URL: {db_url[:50]}...")

try:
    # Crear engine
    engine = create_engine(db_url)

    # Probar conexión
    with engine.connect() as conn:
        # Consulta simple
        result = conn.execute(text("SELECT COUNT(*) as total FROM ninos"))
        row = result.fetchone()
        total_ninos = row[0]

        print("\n✅ Conexión exitosa!")
        print(f"   Total de niños en BD: {total_ninos}")

        # Probar tabla antropometrias
        result = conn.execute(text("SELECT COUNT(*) as total FROM antropometrias"))
        row = result.fetchone()
        total_antropometrias = row[0]

        print(f"   Total de antropometrías: {total_antropometrias}")

        # Probar tabla adherencias
        result = conn.execute(text("SELECT COUNT(*) as total FROM adherencias"))
        row = result.fetchone()
        total_adherencias = row[0]

        print(f"   Total de adherencias: {total_adherencias}")

        print("\n✅ Base de datos lista para extracción de datos")
        print("=" * 80)

except Exception as e:
    print(f"\n❌ Error de conexión: {e}")
    print("\n💡 Verifica:")
    print("   1. DATABASE_URL en .env está correcta")
    print("   2. Credenciales de DigitalOcean son válidas")
    print("   3. Firewall permite conexión desde tu IP")
    print("=" * 80)
    sys.exit(1)
