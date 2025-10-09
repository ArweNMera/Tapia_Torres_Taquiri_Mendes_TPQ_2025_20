"""
Script para calcular features ML para todos los niños.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.utils import DatabaseConnector


def calcular_features_todos():
    """Calcula features ML para todos los niños con antropometría."""
    
    print("\n" + "=" * 60)
    print("🔧 CALCULANDO FEATURES ML PARA TODOS LOS NIÑOS")
    print("=" * 60)
    
    db = DatabaseConnector.from_env()
    db.connect()
    
    try:
        # Obtener todos los niños con su última antropometría
        query = """
        SELECT 
            n.nin_id,
            n.nin_nombres,
            (SELECT ant_id 
             FROM antropometrias 
             WHERE nin_id = n.nin_id 
             ORDER BY ant_fecha DESC, creado_en DESC 
             LIMIT 1) as ant_id
        FROM ninos n
        WHERE EXISTS (
            SELECT 1 FROM antropometrias a 
            WHERE a.nin_id = n.nin_id
        )
        ORDER BY n.nin_id
        """
        
        ninos = db.execute_query(query)
        total = len(ninos)
        
        print(f"\n📊 Total de niños a procesar: {total}")
        print("=" * 60)
        
        exitosos = 0
        errores = 0
        
        for idx, row in ninos.iterrows():
            nin_id = int(row['nin_id'])
            ant_id = int(row['ant_id'])
            nombre = row['nin_nombres']
            
            try:
                # Llamar procedimiento almacenado
                result = db.call_procedure('sp_calcular_features_ml', [nin_id, ant_id])
                
                if not result.empty:
                    exitosos += 1
                    print(f"✅ [{exitosos}/{total}] {nombre} (nin_id={nin_id})")
                else:
                    errores += 1
                    print(f"⚠️  [{exitosos + errores}/{total}] {nombre} - Sin resultado")
                
            except Exception as e:
                errores += 1
                print(f"❌ [{exitosos + errores}/{total}] {nombre} - Error: {str(e)[:50]}")
        
        # Resumen
        print("\n" + "=" * 60)
        print("📋 RESUMEN")
        print("=" * 60)
        print(f"✅ Exitosos: {exitosos}")
        print(f"❌ Errores: {errores}")
        print(f"📊 Total: {total}")
        print(f"📈 Tasa de éxito: {(exitosos/total*100):.1f}%")
        
        # Verificar features creados
        query_check = "SELECT COUNT(*) as total FROM features_ml"
        result = db.execute_query(query_check)
        total_features = result['total'].iloc[0]
        
        print(f"\n🔧 Features ML en base de datos: {total_features}")
        
        if exitosos > 0:
            print("\n✅ Features calculados correctamente")
            print("\n🚀 Siguiente paso:")
            print("   python src/utils/db_connector.py")
        
    except Exception as e:
        print(f"\n❌ Error general: {e}")
    
    finally:
        db.disconnect()


if __name__ == "__main__":
    calcular_features_todos()
