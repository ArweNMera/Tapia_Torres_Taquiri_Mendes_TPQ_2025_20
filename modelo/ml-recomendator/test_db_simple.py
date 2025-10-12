"""
Test simple de conexión a BD
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar .env
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

print("=" * 60)
print("🔍 VERIFICANDO CREDENCIALES")
print("=" * 60)
print(f"\n.env encontrado en: {ENV_PATH}")
print(f"Existe: {ENV_PATH.exists()}")

print("\n📋 Variables de entorno:")
print(f"  DB_HOST: {os.getenv('DB_HOST')}")
print(f"  DB_PORT: {os.getenv('DB_PORT')}")
print(f"  DB_USER: {os.getenv('DB_USER')}")
print(f"  DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', ''))}")
print(f"  DB_NAME: {os.getenv('DB_NAME')}")

print("\n🔌 Intentando conectar...")

try:
    import pymysql

    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "nutricion_db"),
    )

    print("✅ CONEXIÓN EXITOSA!")

    # Probar query
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM antropometrias a
        INNER JOIN ninos n ON a.nin_id = n.nin_id
        WHERE a.ant_peso_kg > 0 AND a.ant_talla_cm > 0
    """)
    total = cursor.fetchone()[0]

    print("\n📊 Datos disponibles:")
    print(f"  Antropometrías válidas: {total}")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\n💡 Verifica:")
    print("  1. MySQL está corriendo")
    print("  2. Las credenciales en .env son correctas")
    print("  3. La base de datos 'nutricion_db' existe")
