"""
Test simple de conexión a MySQL.
"""

import pymysql

# Credenciales directas
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root123456',
    'database': 'nutricion'
}

print("🔌 Intentando conectar a MySQL...")
print(f"   Host: {config['host']}")
print(f"   Puerto: {config['port']}")
print(f"   Usuario: {config['user']}")
print(f"   Base de datos: {config['database']}")

try:
    connection = pymysql.connect(**config)
    print("\n✅ Conexión exitosa!")
    
    # Probar una query simple
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM ninos")
    result = cursor.fetchone()
    print(f"✅ Niños en BD: {result[0]}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"\n❌ Error de conexión: {e}")
    print("\n💡 Posibles soluciones:")
    print("   1. Verifica que MySQL esté corriendo")
    print("   2. Verifica el password: root123456")
    print("   3. Verifica que la BD 'nutricion' existe")
