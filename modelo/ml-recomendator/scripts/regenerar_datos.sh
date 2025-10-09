#!/bin/bash

# Script para regenerar datos de entrenamiento sin duplicados
# Uso: ./scripts/regenerar_datos.sh

echo "🔄 REGENERANDO DATOS DE ENTRENAMIENTO"
echo "======================================"

# 1. Extraer datos de BD (ahora sin duplicados)
echo ""
echo "📊 Paso 1: Extrayendo datos de BD..."
python3 src/utils/db_connector.py --output data/raw/surveys/datos_historicos.csv

# 2. Verificar duplicados
echo ""
echo "🔍 Paso 2: Verificando duplicados..."
python3 -c "
import pandas as pd
df = pd.read_csv('data/raw/surveys/datos_historicos.csv')
duplicados = df.duplicated().sum()
print(f'Total registros: {len(df)}')
print(f'Duplicados: {duplicados}')
if duplicados > 0:
    print('⚠️  Aún hay duplicados, limpiando...')
    df_clean = df.drop_duplicates()
    df_clean.to_csv('data/raw/surveys/datos_historicos.csv', index=False)
    print(f'✅ Limpiado: {len(df_clean)} registros únicos')
else:
    print('✅ No hay duplicados')
"

# 3. Entrenar modelo con CV
echo ""
echo "🎯 Paso 3: Entrenando modelo Random Forest con Cross-Validation..."
python3 src/pipeline/train_model.py \
    --data data/raw/surveys/datos_historicos.csv \
    --model rf \
    --output models/ \
    --use-cv \
    --cv-folds 5

# 4. Generar gráficas
echo ""
echo "📊 Paso 4: Generando gráficas..."
python3 scripts/generar_graficas.py

echo ""
echo "✅ PROCESO COMPLETADO"
echo "======================================"
echo ""
echo "📊 Resultados:"
echo "   - Modelo: models/rf_model.pkl"
echo "   - Métricas CV: models/cv_metrics.json"
echo "   - Gráficas: reports/figures/"
echo ""
echo "📈 Próximos pasos:"
echo "   1. Revisar gráficas en reports/figures/"
echo "   2. Verificar accuracy en models/cv_metrics.json"
echo "   3. Usar el modelo en producción"
echo ""
