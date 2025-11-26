#!/usr/bin/env python3
"""
Script para entrenar el modelo desde Colab.
Llama al endpoint del backend para entrenar el modelo.

Uso:
    python3 train_from_colab.py --backend-url http://localhost:8000
"""

import argparse
import json
import time

import requests


def train_model(backend_url: str, min_measurements: int = 2, lookback_months: int = 24):
    """Entrenar el modelo llamando al endpoint del backend."""

    endpoint = f"{backend_url.rstrip('/')}/api/v1/ml/train_model"

    payload = {
        "min_measurements": min_measurements,
        "lookback_months": lookback_months,
        "include_synthetic": True,
    }

    print("🚀 Iniciando entrenamiento del modelo...")
    print(f"   Backend: {backend_url}")
    print(f"   Endpoint: {endpoint}")
    print(f"   Parámetros: {json.dumps(payload, indent=2)}")
    print()

    try:
        start_time = time.time()
        response = requests.post(endpoint, json=payload, timeout=900)  # 15 minutos
        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            print("✅ ENTRENAMIENTO COMPLETADO")
            print(f"   Status: {result.get('status')}")
            print(f"   Mensaje: {result.get('message')}")
            print(f"   Accuracy: {result.get('accuracy', 'N/A')}")
            print(f"   F1-Score: {result.get('f1_score', 'N/A')}")
            print(f"   Dataset: {result.get('dataset_size', 'N/A')} registros")
            print(f"   Tiempo: {result.get('training_time_seconds', elapsed):.1f}s")
            print(f"   Modelo: {result.get('model_path')}")

            return True
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("❌ Timeout: El entrenamiento tardó más de 15 minutos")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar a {backend_url}")
        print("   Verifica que el backend esté corriendo")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Entrenar el modelo de predicción nutricional desde Colab"
    )
    parser.add_argument(
        "--backend-url",
        default="http://localhost:8000",
        help="URL del backend (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--min-measurements",
        type=int,
        default=2,
        help="Mínimo de mediciones por niño (default: 2)",
    )
    parser.add_argument(
        "--lookback-months",
        type=int,
        default=24,
        help="Meses hacia atrás para considerar (default: 24)",
    )

    args = parser.parse_args()

    success = train_model(
        args.backend_url,
        min_measurements=args.min_measurements,
        lookback_months=args.lookback_months,
    )

    exit(0 if success else 1)


if __name__ == "__main__":
    main()
