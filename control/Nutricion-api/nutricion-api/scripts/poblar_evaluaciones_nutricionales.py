#!/usr/bin/env python3
"""
Pobla la tabla evaluaciones_nutricionales con todos los niños faltantes.
Calcula el estado nutricional usando la API ML y lo guarda en la BD.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import httpx
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

# Configuración
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/nutricion")
ML_API_URL = os.getenv("ML_API_URL", "http://localhost:8003")

# Mapeo de clasificaciones de 7 a 6 categorías (para la BD)
CLASIFICACION_MAP = {
    "DESNUTRICION_SEVERA": "DESNUTRICION_SEVERA",
    "DESNUTRICION_MODERADA": "DESNUTRICION",
    "RIESGO_DESNUTRICION": "RIESGO",
    "NORMAL": "NORMAL",
    "RIESGO_SOBREPESO": "RIESGO",
    "SOBREPESO": "SOBREPESO",
    "OBESIDAD": "OBESIDAD"
}

NIVEL_RIESGO_MAP = {
    "DESNUTRICION_SEVERA": "CRITICO",
    "DESNUTRICION_MODERADA": "ALTO",
    "RIESGO_DESNUTRICION": "MODERADO",
    "NORMAL": "BAJO",
    "RIESGO_SOBREPESO": "MODERADO",
    "SOBREPESO": "ALTO",
    "OBESIDAD": "CRITICO"
}

def main():
    print("=" * 80)
    print("ACTUALIZANDO TABLA evaluaciones_nutricionales")
    print("=" * 80)
    print(f"📊 Base de datos: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    print(f"🤖 API ML: {ML_API_URL}")
    print("=" * 80)
    print()
    
    # Preguntar si quiere limpiar evaluaciones antiguas
    print("⚠️  Este script actualizará TODAS las evaluaciones nutricionales")
    print("   con la clasificación nueva basada en BAZ (7 categorías OMS)")
    print()
    respuesta = input("¿Deseas continuar? (s/n): ").strip().lower()
    if respuesta != 's':
        print("❌ Operación cancelada")
        return
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
                    print("   Ejecuta: cd modelo/ml-recomendator && ./run_api.sh")
                    return
                print("✅ API ML disponible")
            except Exception as e:
                print(f"❌ No se puede conectar a API ML: {e}")
                print("   Ejecuta: cd modelo/ml-recomendator && ./run_api.sh")
                return
        
        print()
        
        # Limpiar evaluaciones antiguas
        print("🧹 Limpiando evaluaciones antiguas...")
        delete_query = text("DELETE FROM evaluaciones_nutricionales")
        result = session.execute(delete_query)
        session.commit()
        print(f"✅ {result.rowcount} evaluaciones antiguas eliminadas")
        print()
        
        # Obtener TODAS las antropometrías
        query = text("""
            SELECT 
                a.ant_id,
                a.nin_id,
                n.nin_nombres,
                a.ant_peso_kg,
                a.ant_talla_cm,
                a.ant_fecha,
                TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as edad_meses
            FROM antropometrias a
            INNER JOIN ninos n ON a.nin_id = n.nin_id
            WHERE a.ant_peso_kg IS NOT NULL
              AND a.ant_talla_cm IS NOT NULL
              AND a.ant_talla_cm > 0
              AND TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) >= 0
            ORDER BY a.nin_id, a.ant_fecha DESC
        """)
        
        result = session.execute(query)
        rows = result.fetchall()
        
        if not rows:
            print("ℹ️  No hay antropometrías para evaluar")
            return
        
        print(f"📊 Encontradas {len(rows)} antropometrías para evaluar")
        print(f"   Niños únicos: {len(set(row[1] for row in rows))}")
        print()
        
        # Procesar cada antropometría
        success_count = 0
        error_count = 0
        
        with httpx.Client(timeout=10.0) as client:
            for row in rows:
                ant_id = row[0]
                nin_id = row[1]
                nin_nombres = row[2]
                peso_kg = float(row[3])
                talla_cm = float(row[4])
                ant_fecha = row[5]
                edad_meses = int(row[6])
                
                try:
                    # Llamar a API ML
                    payload = {
                        "nin_id": nin_id,
                        "peso_kg": peso_kg,
                        "talla_cm": talla_cm,
                        "fecha_medicion": ant_fecha.strftime("%Y-%m-%d") if ant_fecha else None
                    }
                    
                    response = client.post(
                        f"{ML_API_URL}/ml/analisis_nutricional",
                        json=payload
                    )
                    
                    if response.status_code == 200:
                        ml_result = response.json()
                        
                        # Mapear clasificación de 7 a 6 categorías
                        clasificacion_7cat = ml_result.get("diagnostico", "NORMAL")
                        clasificacion_6cat = CLASIFICACION_MAP.get(clasificacion_7cat, "NORMAL")
                        nivel_riesgo = NIVEL_RIESGO_MAP.get(clasificacion_7cat, "BAJO")
                        
                        # Insertar en evaluaciones_nutricionales
                        insert_query = text("""
                            INSERT INTO evaluaciones_nutricionales 
                            (nin_id, ant_id, en_edad_meses, en_imc, en_z_score_imc, 
                             en_percentil_imc, en_clasificacion, en_nivel_riesgo, creado_en)
                            VALUES 
                            (:nin_id, :ant_id, :edad_meses, :imc, :baz, 
                             :percentil, :clasificacion, :nivel_riesgo, :creado_en)
                        """)
                        
                        session.execute(insert_query, {
                            "nin_id": nin_id,
                            "ant_id": ant_id,
                            "edad_meses": edad_meses,
                            "imc": ml_result.get("imc"),
                            "baz": ml_result.get("baz"),
                            "percentil": ml_result.get("percentil"),
                            "clasificacion": clasificacion_6cat,
                            "nivel_riesgo": nivel_riesgo,
                            "creado_en": datetime.now()
                        })
                        
                        session.commit()
                        
                        print(f"✅ {nin_nombres[:30]:30} → {clasificacion_7cat}")
                        success_count += 1
                    else:
                        print(f"⚠️  {nin_nombres[:30]:30} → Error {response.status_code}")
                        error_count += 1
                        
                except Exception as e:
                    print(f"❌ {nin_nombres[:30]:30} → Error: {e}")
                    error_count += 1
                    session.rollback()
        
        print()
        print("=" * 80)
        print("📊 RESUMEN")
        print("=" * 80)
        print(f"✅ Exitosos: {success_count}")
        print(f"❌ Errores: {error_count}")
        print(f"📊 Total: {len(rows)}")
        print()
        
        if success_count > 0:
            print("✅ Tabla evaluaciones_nutricionales poblada correctamente")
            print("   Ahora todos los niños tienen su evaluación guardada")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    main()
