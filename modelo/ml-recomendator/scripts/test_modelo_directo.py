"""
Script para probar el modelo DIRECTO.
Predice clasificación nutricional sin calcular BAZ.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.models.direct_classifier import cargar_modelo_directo


def test_casos_ejemplo():
    """Prueba el modelo con casos de ejemplo."""
    
    print("\n" + "=" * 70)
    print("🧪 PROBANDO MODELO DIRECTO")
    print("=" * 70)
    
    # Cargar modelo
    print("\n📦 Cargando modelo...")
    try:
        modelo = cargar_modelo_directo()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Primero entrena el modelo:")
        print("   python src/pipeline/train_model_directo.py --data-source db")
        return
    
    # Casos de prueba
    casos = [
        {
            'nombre': 'Bebé normal (12 meses)',
            'edad_meses': 12,
            'sexo': 'M',
            'peso_kg': 10.0,
            'talla_cm': 75.0
        },
        {
            'nombre': 'Niño con sobrepeso (5 años)',
            'edad_meses': 60,
            'sexo': 'M',
            'peso_kg': 25.0,
            'talla_cm': 110.0
        },
        {
            'nombre': 'Niña normal (8 años)',
            'edad_meses': 96,
            'sexo': 'F',
            'peso_kg': 26.0,
            'talla_cm': 128.0
        },
        {
            'nombre': 'Adolescente con obesidad (14 años)',
            'edad_meses': 168,
            'sexo': 'M',
            'peso_kg': 85.0,
            'talla_cm': 165.0
        },
        {
            'nombre': 'Niño con desnutrición (3 años)',
            'edad_meses': 36,
            'sexo': 'M',
            'peso_kg': 10.0,
            'talla_cm': 85.0
        }
    ]
    
    print("\n" + "=" * 70)
    print("📊 RESULTADOS DE PREDICCIONES")
    print("=" * 70)
    
    for caso in casos:
        print(f"\n{'─' * 70}")
        print(f"📌 {caso['nombre']}")
        print(f"{'─' * 70}")
        
        # Predecir
        resultado = modelo.predecir(
            edad_meses=caso['edad_meses'],
            sexo=caso['sexo'],
            peso_kg=caso['peso_kg'],
            talla_cm=caso['talla_cm']
        )
        
        # Mostrar resultado
        print(f"\n   Datos:")
        print(f"   • Edad: {caso['edad_meses']} meses ({caso['edad_meses']/12:.1f} años)")
        print(f"   • Sexo: {caso['sexo']}")
        print(f"   • Peso: {caso['peso_kg']} kg")
        print(f"   • Talla: {caso['talla_cm']} cm")
        
        bmi = caso['peso_kg'] / (caso['talla_cm'] / 100) ** 2
        print(f"   • BMI: {bmi:.2f}")
        
        print(f"\n   Predicción:")
        print(f"   🎯 Clasificación: {resultado['clasificacion']}")
        print(f"   📊 Confianza: {resultado['confianza']:.1%}")
        
        # Top 3 probabilidades
        print(f"\n   Top 3 probabilidades:")
        probas_sorted = sorted(
            resultado['probabilidades'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for cat, prob in probas_sorted:
            barra = '█' * int(prob * 20)
            print(f"   {cat:25s} {prob:6.1%} {barra}")
    
    print("\n" + "=" * 70)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 70)
    print("\n💡 El modelo predice DIRECTAMENTE sin calcular BAZ")
    print("   Solo necesita: edad, sexo, peso y talla")


def test_explicacion():
    """Prueba la función de explicación."""
    
    print("\n" + "=" * 70)
    print("📖 PROBANDO EXPLICACIONES")
    print("=" * 70)
    
    try:
        modelo = cargar_modelo_directo()
    except FileNotFoundError:
        print("\n❌ Modelo no encontrado. Entrena primero el modelo.")
        return
    
    # Caso de ejemplo
    explicacion = modelo.explicar_prediccion(
        edad_meses=84,  # 7 años
        sexo='F',
        peso_kg=30.0,
        talla_cm=120.0
    )
    
    print(f"\n📌 Caso: Niña de 7 años")
    print(f"{'─' * 70}")
    
    print(f"\n🎯 Predicción: {explicacion['prediccion']}")
    print(f"📊 Confianza: {explicacion['confianza']:.1%}")
    
    print(f"\n📋 Datos de entrada:")
    for key, value in explicacion['datos_entrada'].items():
        print(f"   • {key}: {value}")
    
    print(f"\n💬 Contexto:")
    print(f"   {explicacion['contexto']}")
    
    print(f"\n📊 Top 3 probabilidades:")
    for item in explicacion['probabilidades_top3']:
        print(f"   • {item['categoria']}: {item['probabilidad']:.1%}")


if __name__ == "__main__":
    test_casos_ejemplo()
    test_explicacion()
