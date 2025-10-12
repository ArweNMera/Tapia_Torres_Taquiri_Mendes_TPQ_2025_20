#!/bin/bash

# Script para configurar herramientas de calidad de código

echo "=================================="
echo "🔧 CONFIGURANDO HERRAMIENTAS"
echo "   Ruff + Mypy + Pre-commit"
echo "=================================="
echo ""

# Función para configurar un proyecto
setup_project() {
    local project_path=$1
    local project_name=$2

    echo "📦 Configurando: $project_name"
    echo "   Ruta: $project_path"
    echo ""

    cd "$project_path" || exit 1

    # Instalar dependencias
    echo "   Instalando dependencias..."
    if [ "$project_name" == "Nutricion API" ]; then
        pip install ruff mypy pre-commit bandit
    else
        pip install ruff mypy pre-commit nbqa
    fi

    if [ $? -ne 0 ]; then
        echo "   ❌ Error instalando dependencias"
        return 1
    fi

    # Instalar hooks
    echo "   Instalando pre-commit hooks..."
    pre-commit install

    if [ $? -ne 0 ]; then
        echo "   ❌ Error instalando hooks"
        return 1
    fi

    # Ejecutar primera vez
    echo "   Ejecutando pre-commit por primera vez..."
    pre-commit run --all-files || true

    echo "   ✅ $project_name configurado"
    echo ""

    cd - > /dev/null || exit 1
}

# Configurar Nutricion API
if [ -d "control/Nutricion-api/nutricion-api" ]; then
    setup_project "control/Nutricion-api/nutricion-api" "Nutricion API"
else
    echo "⚠️  No se encontró Nutricion API"
fi

# Configurar ML Recomendator
if [ -d "modelo/ml-recomendator" ]; then
    setup_project "modelo/ml-recomendator" "ML Recomendator"
else
    echo "⚠️  No se encontró ML Recomendator"
fi

echo "=================================="
echo "✅ CONFIGURACIÓN COMPLETADA"
echo "=================================="
echo ""
echo "📝 Próximos pasos:"
echo "   1. Los hooks se ejecutarán automáticamente en cada commit"
echo "   2. Para ejecutar manualmente: pre-commit run --all-files"
echo "   3. Para formatear código: ruff format ."
echo "   4. Para linting: ruff check --fix ."
echo ""
echo "📚 Ver guía completa: GUIA_RUFF_MYPY_PRECOMMIT.md"
