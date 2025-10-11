#!/bin/bash

echo "🔧 RECALCULANDO BAZ EN LA BASE DE DATOS"
echo "========================================"
echo ""
echo "Este script:"
echo "1. Recalcula BAZ usando tablas OMS correctas"
echo "2. Actualiza la BD con los valores correctos"
echo "3. Reentrena el modelo con datos correctos"
echo ""

read -p "¿Continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]
then
    exit 1
fi

# Activar entorno
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 1. Recalcular BAZ
echo ""
echo "📊 Paso 1: Recalculando BAZ..."
python -c "
from src.utils.db_connector import DatabaseConnector
from src.features.who_calculator import WHOCalculator
import pandas as pd

db = DatabaseConnector.from_env()
db.connect()

# Obtener todas las antropometrías
query = '''
SELECT 
    a.ant_id,
    n.nin_sexo as sexo,
    TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) as edad_meses,
    a.ant_peso_kg as peso_kg,
    a.ant_talla_cm as talla_cm
FROM antropometrias a
INNER JOIN ninos n ON a.nin_id = n.nin_id
WHERE a.ant_peso_kg > 0 
  AND a.ant_talla_cm > 0
  AND TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, a.ant_fecha) BETWEEN 0 AND 228
'''

df = db.execute_query(query)
print(f'Total registros a actualizar: {len(df)}')

# Calcular BAZ correcto
who_calc = WHOCalculator(db_connector=db)

actualizados = 0
for idx, row in df.iterrows():
    try:
        bmi = row['peso_kg'] / (row['talla_cm'] / 100) ** 2
        baz = who_calc.calculate_baz(bmi, int(row['edad_meses']), row['sexo'])
        
        # Actualizar en BD
        update_query = f'''
        UPDATE antropometrias 
        SET ant_z_imc = {baz}
        WHERE ant_id = {row['ant_id']}
        '''
        db.execute_query(update_query)
        actualizados += 1
        
        if actualizados % 10 == 0:
            print(f'  Actualizados: {actualizados}/{len(df)}')
    except Exception as e:
        print(f'  Error en ant_id={row[\"ant_id\"]}: {e}')

print(f'✅ Total actualizados: {actualizados}')
db.disconnect()
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BAZ recalculado correctamente"
    echo ""
    echo "📊 Paso 2: Reentrenando modelo..."
    ./ENTRENAR_AHORA.sh
else
    echo ""
    echo "❌ Error recalculando BAZ"
    exit 1
fi
