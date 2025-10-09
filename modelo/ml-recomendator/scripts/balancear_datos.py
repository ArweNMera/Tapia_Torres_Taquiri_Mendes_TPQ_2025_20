"""
Script para balancear datos antropométricos usando Python.
Reemplaza el script SQL para compatibilidad con Mac.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.utils import DatabaseConnector

def main():
    print("\n" + "=" * 60)
    print("📊 BALANCEANDO DATOS ANTROPOMÉTRICOS")
    print("=" * 60)
    
    db = DatabaseConnector.from_env()
    db.connect()
    
    try:
        # 1. Crear backup
        print("\n💾 Creando backup...")
        with db.engine.begin() as conn:
            # Primero eliminar backup anterior si existe
            conn.execute(text("DROP TABLE IF EXISTS antropometrias_backup_original"))
            conn.execute(text("""
                CREATE TABLE antropometrias_backup_original 
                AS SELECT * FROM antropometrias
            """))
        print("✅ Backup creado")
        
        # 2. Obtener niños únicos con antropometría
        print("\n📋 Obteniendo niños...")
        query = text("""
            SELECT DISTINCT n.nin_id, n.nin_nombres, n.nin_sexo, n.nin_fecha_nac
            FROM ninos n
            JOIN antropometrias a ON n.nin_id = a.nin_id
            ORDER BY RAND()
        """)
        ninos_df = pd.read_sql(query, db.engine)
        print(f"   Total niños disponibles: {len(ninos_df)}")
        
        # 3. Asignar categorías
        print("\n🎯 Asignando categorías...")
        
        categorias = {
            'NORMAL': {'cantidad': 70, 'baz_min': -0.8, 'baz_max': 0.8},
            'RIESGO_DESNUTRICION': {'cantidad': 30, 'baz_min': -1.9, 'baz_max': -1.0},
            'DESNUTRICION_MODERADA': {'cantidad': 25, 'baz_min': -2.9, 'baz_max': -2.0},
            'DESNUTRICION_SEVERA': {'cantidad': 25, 'baz_min': -4.5, 'baz_max': -3.3},
            'RIESGO_SOBREPESO': {'cantidad': 20, 'baz_min': 1.1, 'baz_max': 1.9},
            'SOBREPESO': {'cantidad': 15, 'baz_min': 2.1, 'baz_max': 2.9},
            'OBESIDAD': {'cantidad': 15, 'baz_min': 3.2, 'baz_max': 4.7}
        }
        
        asignaciones = []
        ninos_usados = set()
        
        for categoria, config in categorias.items():
            # Seleccionar niños aleatorios que no han sido usados
            disponibles = ninos_df[~ninos_df['nin_id'].isin(ninos_usados)]
            seleccionados = disponibles.sample(n=min(config['cantidad'], len(disponibles)))
            
            for _, nino in seleccionados.iterrows():
                # Generar BAZ aleatorio en el rango
                target_baz = np.random.uniform(config['baz_min'], config['baz_max'])
                
                asignaciones.append({
                    'nin_id': nino['nin_id'],
                    'categoria': categoria,
                    'target_baz': round(target_baz, 2)
                })
                ninos_usados.add(nino['nin_id'])
            
            print(f"   {categoria}: {len(seleccionados)} niños")
        
        asignaciones_df = pd.DataFrame(asignaciones)
        print(f"\n✅ Total asignados: {len(asignaciones_df)} niños")
        
        # 4. Calcular pesos realistas usando tablas OMS
        print("\n🔢 Calculando pesos realistas...")
        
        actualizaciones = 0
        errores = 0
        
        # Usar una sola conexión con transacción para todas las actualizaciones
        with db.engine.begin() as conn:
            for _, asig in asignaciones_df.iterrows():
                try:
                    # Obtener última antropometría y datos del niño
                    query = text("""
                        SELECT 
                            a.ant_id,
                            a.ant_talla_cm,
                            n.nin_sexo,
                            TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as edad_meses,
                            lms.M,
                            lms.L,
                            lms.S
                        FROM antropometrias a
                        JOIN ninos n ON a.nin_id = n.nin_id
                        LEFT JOIN oms_bmi_lms lms ON 
                            lms.sexo = n.nin_sexo 
                            AND lms.edad_meses = TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha)
                            AND lms.version = 'OMS_2007'
                        WHERE a.nin_id = :nin_id
                        ORDER BY a.ant_fecha DESC, a.creado_en DESC
                        LIMIT 1
                    """)
                    
                    result = conn.execute(query, {'nin_id': int(asig['nin_id'])}).fetchone()
                    
                    if result and result.M is not None:
                        # Calcular BMI objetivo usando fórmula inversa de BAZ
                        # BMI = M * (1 + L*S*Z)^(1/L)
                        L, M, S = float(result.L), float(result.M), float(result.S)
                        Z = float(asig['target_baz'])
                        
                        if L != 0:
                            bmi_objetivo = M * ((1 + L * S * Z) ** (1 / L))
                        else:
                            bmi_objetivo = M * np.exp(S * Z)
                        
                        # Calcular peso: peso = BMI * (talla_m)^2
                        talla_m = float(result.ant_talla_cm) / 100
                        peso_objetivo = bmi_objetivo * (talla_m ** 2)
                        
                        # Validar que el peso sea realista
                        if 5 <= peso_objetivo <= 150:  # Rango razonable
                            # Actualizar antropometría
                            update_query = text("""
                                UPDATE antropometrias
                                SET ant_peso_kg = :peso,
                                    ant_z_imc = :baz,
                                    actualizado_en = NOW()
                                WHERE ant_id = :ant_id
                            """)
                            
                            conn.execute(update_query, {
                                'peso': round(peso_objetivo, 2),
                                'baz': Z,
                                'ant_id': result.ant_id
                            })
                            
                            actualizaciones += 1
                        else:
                            errores += 1
                    else:
                        errores += 1
                        
                except Exception as e:
                    errores += 1
                    print(f"   ⚠️  Error en nin_id={asig['nin_id']}: {e}")
        
        print(f"\n✅ Actualizaciones exitosas: {actualizaciones}")
        if errores > 0:
            print(f"⚠️  Errores: {errores}")
        
        # 5. Mostrar resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN POR CATEGORÍA")
        print("=" * 60)
        
        for categoria in categorias.keys():
            cat_data = asignaciones_df[asignaciones_df['categoria'] == categoria]
            if len(cat_data) > 0:
                print(f"\n{categoria}:")
                print(f"   Cantidad: {len(cat_data)}")
                print(f"   BAZ promedio: {cat_data['target_baz'].mean():.2f}")
                print(f"   BAZ rango: [{cat_data['target_baz'].min():.2f}, {cat_data['target_baz'].max():.2f}]")
        
        print("\n" + "=" * 60)
        print("✅ BALANCEO COMPLETADO")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
