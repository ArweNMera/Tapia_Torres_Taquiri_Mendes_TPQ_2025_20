"""
Script para limpiar la tabla features_ml.
Reemplaza el comando mysql para compatibilidad con Mac.
"""

import sys
from pathlib import Path
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.utils import DatabaseConnector

def main():
    print("\n🧹 Limpiando tabla features_ml...")
    
    db = DatabaseConnector.from_env()
    db.connect()
    
    try:
        with db.engine.begin() as conn:
            result = conn.execute(text("DELETE FROM features_ml"))
            print(f"✅ {result.rowcount} registros eliminados de features_ml")
    except Exception as e:
        print(f"❌ Error al limpiar features_ml: {e}")
        raise
    finally:
        db.disconnect()

if __name__ == "__main__":
    main()
