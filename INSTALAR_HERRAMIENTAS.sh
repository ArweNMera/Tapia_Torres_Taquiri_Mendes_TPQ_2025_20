#!/bin/bash

# Script para instalar herramientas de calidad de código

echo "=================================="
echo "📦 INSTALANDO HERRAMIENTAS"
echo "   Ruff + Mypy + Pre-commit"
echo "=================================="
echo ""

# Verificar que estamos en un entorno virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  No estás en un entorno virtual"
    echo "   Activando venv..."

    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "❌ No se encontró entorno virtual (venv o .venv)"
        echo "   Crea uno con: python3 -m venv venv"
        exit 1
    fi
fi

echo "✅ Entorno virtual activo: $VIRTUAL_ENV"
echo ""

# Instalar herramientas
echo "📦 Instalando ruff, mypy, pre-commit, bandit, nbqa..."
pip install ruff mypy pre-commit bandit nbqa

if [ $? -ne 0 ]; then
    echo "❌ Error instalando herramientas"
    exit 1
fi

echo ""
echo "✅ Herramientas instaladas correctamente"
echo ""

# Instalar hooks de pre-commit
echo "🔧 Instalando pre-commit hooks..."
pre-commit install

if [ $? -ne 0 ]; then
    echo "❌ Error instalando hooks"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ INSTALACIÓN COMPLETADA"
echo "=================================="
echo ""
echo "📝 Herramientas instaladas:"
echo "   • ruff (linter + formatter)"
echo "   • mypy (type checker)"
echo "   • pre-commit (automatización)"
echo "   • bandit (seguridad)"
echo "   • nbqa (notebooks)"
echo ""
echo "🎯 Próximos pasos:"
echo "   1. Ejecutar primera vez: pre-commit run --all-files"
echo "   2. Los hooks se ejecutarán automáticamente en cada commit"
echo ""
echo "📚 Ver guía: GUIA_RUFF_MYPY_PRECOMMIT.md"
