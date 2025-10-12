#!/usr/bin/env python3
"""
Script para re-evaluar todas las clasificaciones nutricionales existentes
usando el nuevo modelo ML con 7 categorías.

Uso:
    python3 scripts/reevaluar_clasificaciones.py
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()

# Configuración de BD
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nutricion")
ML_API_URL = os.getenv("ML_API_URL", "http://localhost:8003")


def main():
    print("🔄 RE-EVALUANDO CLASIFICACIONES NUTRICIONALES")
    print("=" * 60)
    print(
        f"📊 Base de datos: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}"
    )
    print(f"🤖 API ML: {ML_API_URL}")
    print("=" * 60)
    print()

    # Conectar a BD
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Verificar que la API ML está disponible
        print("🔍 Verificando API ML...")
        with httpx.Client(timeout=5.0) as client:
            try:
                response = client.get(f"{ML_API_URL}/health")
                if response.status_code != 200:
                    print(f"❌ API ML no está disponible (status: {response.status_code})")
                    print("   Asegúrate de que esté corriendo en puerto 8003")
                    return
                print("✅ API ML disponible")
            except Exception as e:
                print(f"❌ No se puede conectar a API ML: {e}")
                print("   Ejecuta: cd modelo/ml-recomendator && ./run_api.sh")
                return

        print()

        # Obtener todos los niños con antropometrías
        query = text("""
            SELECT DISTINCT
                n.nin_id,
                n.nin_nombres,
                a.ant_id,
                a.ant_peso_kg,
                a.ant_talla_cm,
                a.ant_fecha
            FROM ninos n
            INNER JOIN antropometrias a ON n.nin_id = a.nin_id
            ORDER BY n.nin_id, a.ant_fecha DESC
        """)

        result = session.execute(query)
        rows = result.fetchall()

        if not rows:
            print("ℹ️  No hay datos antropométricos para re-evaluar")
            return

        print(f"📊 Encontrados {len(rows)} registros antropométricos")
        print()

        # Agrupar por niño (tomar solo la última medición de cada uno)
        ninos_dict = {}
        for row in rows:
            nin_id = row[0]
            if nin_id not in ninos_dict:
                ninos_dict[nin_id] = {
                    "nin_id": nin_id,
                    "nin_nombres": row[1],
                    "ant_id": row[2],
                    "peso_kg": float(row[3]),
                    "talla_cm": float(row[4]),
                    "fecha": row[5].strftime("%Y-%m-%d") if row[5] else None,
                }

        print(f"👶 Re-evaluando {len(ninos_dict)} niños...")
        print()

        # Re-evaluar cada niño
        success_count = 0
        error_count = 0

        with httpx.Client(timeout=10.0) as client:
            for nin_id, data in ninos_dict.items():
                try:
                    # Llamar a API ML
                    payload = {
                        "nin_id": nin_id,
                        "peso_kg": data["peso_kg"],
                        "talla_cm": data["talla_cm"],
                        "fecha_medicion": data["fecha"],
                    }

                    response = client.post(f"{ML_API_URL}/ml/analisis_nutricional", json=payload)

                    if response.status_code == 200:
                        ml_result = response.json()
                        clasificacion = ml_result.get("diagnostico", "DESCONOCIDO")

                        print(f"✅ {data['nin_nombres'][:30]:30} → {clasificacion}")
                        success_count += 1
                    else:
                        print(f"⚠️  {data['nin_nombres'][:30]:30} → Error {response.status_code}")
                        error_count += 1

                except Exception as e:
                    print(f"❌ {data['nin_nombres'][:30]:30} → Error: {e}")
                    error_count += 1

        print()
        print("=" * 60)
        print("📊 RESUMEN")
        print("=" * 60)
        print(f"✅ Exitosos: {success_count}")
        print(f"❌ Errores: {error_count}")
        print(f"📊 Total: {len(ninos_dict)}")
        print()

        if success_count > 0:
            print("✅ Las clasificaciones han sido actualizadas")
            print("   Recarga el frontend para ver los cambios")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()
