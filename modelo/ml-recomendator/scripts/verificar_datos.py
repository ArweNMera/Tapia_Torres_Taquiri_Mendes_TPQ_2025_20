"""
Script para verificar que hay datos en la base de datos.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.utils import DatabaseConnector


def verificar_datos():
    """Verifica que hay datos suficientes para entrenar."""

    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO DATOS EN BASE DE DATOS")
    print("=" * 60)

    db = DatabaseConnector.from_env()

    try:
        db.connect()

        # 1. Verificar niños
        query_ninos = "SELECT COUNT(*) as total FROM ninos"
        result = db.execute_query(query_ninos)
        total_ninos = result["total"].iloc[0]
        print(f"\n👶 Niños registrados: {total_ninos}")

        if total_ninos == 0:
            print("❌ No hay niños registrados. Necesitas datos para entrenar.")
            return False

        # 2. Verificar antropometrías
        query_ant = """
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT nin_id) as ninos_con_datos
        FROM antropometrias
        """
        result = db.execute_query(query_ant)
        total_ant = result["total"].iloc[0]
        ninos_con_ant = result["ninos_con_datos"].iloc[0]
        print(f"📏 Mediciones antropométricas: {total_ant}")
        print(f"   Niños con mediciones: {ninos_con_ant}")

        if total_ant == 0:
            print("❌ No hay mediciones antropométricas. Necesitas datos para entrenar.")
            return False

        # 3. Verificar features ML
        query_features = "SELECT COUNT(*) as total FROM features_ml"
        result = db.execute_query(query_features)
        total_features = result["total"].iloc[0]
        print(f"🔧 Features ML calculados: {total_features}")

        if total_features == 0:
            print("⚠️  No hay features ML calculados aún.")
            print("   Ejecuta: python scripts/calcular_features_todos.py")

        # 4. Verificar distribución de edades
        query_edades = """
        SELECT
            MIN(TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE())) as edad_min,
            MAX(TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE())) as edad_max,
            AVG(TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE())) as edad_promedio
        FROM ninos n
        JOIN antropometrias a ON n.nin_id = a.nin_id
        """
        result = db.execute_query(query_edades)
        print("\n📊 Distribución de edades:")
        print(f"   Mínima: {result['edad_min'].iloc[0]} meses")
        print(f"   Máxima: {result['edad_max'].iloc[0]} meses")
        print(f"   Promedio: {result['edad_promedio'].iloc[0]:.1f} meses")

        # 5. Verificar datos completos
        query_completos = """
        SELECT COUNT(*) as total
        FROM ninos n
        JOIN antropometrias a ON n.nin_id = a.nin_id
        WHERE a.ant_peso_kg > 0
          AND a.ant_talla_cm > 0
          AND TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) BETWEEN 0 AND 228
        """
        result = db.execute_query(query_completos)
        total_completos = result["total"].iloc[0]
        print(f"\n✅ Registros válidos para entrenamiento: {total_completos}")

        if total_completos < 50:
            print("⚠️  Tienes pocos datos (<50). El modelo puede no ser muy preciso.")
            print("   Recomendado: ≥100 registros")
        elif total_completos < 100:
            print("⚠️  Datos suficientes pero limitados. Modelo básico.")
        else:
            print("✅ Datos suficientes para entrenar un buen modelo.")

        # 6. Verificar tablas OMS en MySQL
        print("\n📚 Verificando tablas OMS en MySQL...")

        tablas_oms = ["oms_bmi_lms", "oms_bmi_zscores", "oms_bmi_percentiles"]

        tablas_encontradas = 0
        for tabla in tablas_oms:
            query = f"SELECT COUNT(*) as total FROM {tabla}"
            try:
                result = db.execute_query(query)
                total = result["total"].iloc[0]
                if total > 0:
                    tablas_encontradas += 1
                    print(f"   ✅ {tabla}: {total} registros")
                else:
                    print(f"   ⚠️  {tabla}: vacía")
            except Exception:
                print(f"   ❌ {tabla}: no existe")

        print(f"\n   Tablas OMS encontradas: {tablas_encontradas}/{len(tablas_oms)}")

        if tablas_encontradas < len(tablas_oms):
            print("⚠️  Faltan tablas OMS o están vacías.")
            print("   Verifica que ejecutaste los scripts de carga de datos OMS.")

        # Resumen
        print("\n" + "=" * 60)
        print("📋 RESUMEN")
        print("=" * 60)

        if total_completos >= 50 and tablas_encontradas == len(tablas_oms) and total_features > 0:
            print("✅ Todo listo para entrenar el modelo")
            print("\n🚀 Siguiente paso:")
            print(
                "   python3 src/utils/db_connector.py --output data/raw/surveys/datos_historicos.csv"
            )
            return True
        else:
            print("⚠️  Revisa los puntos anteriores antes de continuar")
            if total_features == 0:
                print("   → Ejecuta: python3 scripts/calcular_features_todos.py")
            if tablas_encontradas < len(tablas_oms):
                print("   → Verifica tablas OMS en MySQL")
            return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

    finally:
        db.disconnect()


if __name__ == "__main__":
    verificar_datos()
