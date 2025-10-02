ml-recomendator
================

Estructura para pipeline de ML (BAZ/BMI, RF/NN) y soporte de LLM.

- data/raw/who: Tablas WHO LMS (L,M,S) por sexo/mes.
- data/raw/surveys: Encuestas o datasets crudos de niños.
- data/interim: Datos intermedios (con BAZ calculado).
- data/processed: Datos finales para entrenar.
- models: Artefactos entrenados (rf.pkl, nn.pkl, preprocess.joblib).
- reports/figures: Gráficos generados.
- reports/metrics: Métricas JSON.
- src/pipeline: Scripts de preparación (label_dataset.py, split).
- src/models: Entrenamiento y evaluación (RF/NN).
- src/visualization: Plots para RF/NN.
- src/inference: Carga de modelos y predicción.
- src/llm: Utilidades para explicar predicciones en lenguaje sencillo.
- scripts: Wrappers CLI.
- configs: YAML de features e hiperparámetros.

Variables comunes
- WHO_DIR = data/raw/who
- SURVEYS_DIR = data/raw/surveys

LLM (capa conversacional)
- Configura un endpoint OpenAI-compatible vía variables de entorno (ver `.env.example`).
- Requeridos: `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`.
- Opcionales: `LLM_TEMPERATURE`, `LLM_MAX_TOKENS`, `LLM_TIMEOUT`.
- Ejemplo rápido:
  - Copia `.env.example` a `.env` y completa:
    - `LLM_API_KEY=gdJPqIHSLBJ6oFg1boid1BfO3Tvrdl9G` (tu clave)
    - `LLM_BASE_URL=https://TU_ENDPOINT/v1`
    - `LLM_MODEL=TU_MODELO`
  - `assist.summarize_with_llm()` usará ese endpoint si está configurado.
