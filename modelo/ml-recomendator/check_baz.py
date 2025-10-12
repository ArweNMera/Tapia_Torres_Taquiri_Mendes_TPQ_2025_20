"""Verificar BAZ en BD"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.utils.db_connector import DatabaseConnector

db = DatabaseConnector.from_env()
db.connect()

# Ver algunos casos de la BD
query = """
SELECT
    TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as edad_meses,
    n.nin_sexo as sexo,
    a.ant_peso_kg as peso,
    a.ant_talla_cm as talla,
    a.ant_peso_kg / POWER(a.ant_talla_cm / 100, 2) as bmi,
    a.ant_z_imc as baz
FROM antropometrias a
INNER JOIN ninos n ON a.nin_id = n.nin_id
WHERE a.ant_peso_kg > 0
  AND a.ant_talla_cm > 0
  AND a.ant_z_imc IS NOT NULL
  AND TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) BETWEEN 110 AND 125
LIMIT 10
"""

df = db.execute_query(query)
print("Casos de niños de 110-125 meses en la BD:")
print(df.to_string())


# Clasificar según BAZ
def clasificar(baz):
    if baz < -3.0:
        return "DESNUT_SEV"
    elif -3.0 <= baz < -2.0:
        return "DESNUT_MOD"
    elif -2.0 <= baz < -1.0:
        return "RIESGO_DESN"
    elif -1.0 <= baz <= 1.0:
        return "NORMAL"
    elif 1.0 < baz <= 2.0:
        return "RIESGO_SOB"
    elif 2.0 < baz <= 3.0:
        return "SOBREPESO"
    else:
        return "OBESIDAD"


df["clasificacion"] = df["baz"].apply(clasificar)
print("\n\nCon clasificación:")
print(df[["edad_meses", "sexo", "peso", "talla", "bmi", "baz", "clasificacion"]].to_string())

db.disconnect()
