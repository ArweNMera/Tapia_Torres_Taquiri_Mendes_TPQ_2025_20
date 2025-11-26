"""
Endpoints para predicciones ML (PMV3)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.application.services.auth_service import get_current_user
from app.infrastructure.db.session import get_db
from app.schemas.auth import UserResponse
from app.schemas.seguimiento import (
    PrediccionMLResponse,
    ValidarPrediccionRequest,
)

router = APIRouter()


@router.post(
    "/generar/{nin_id}", response_model=PrediccionMLResponse, status_code=status.HTTP_201_CREATED
)
def generar_prediccion_ml(
    nin_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Generar predicción ML para el niño.

    Proceso:
    1. Calcula features ML usando sp_calcular_features_ml
    2. Llama al modelo LightGBM para predicción
    3. Guarda predicción usando sp_guardar_prediccion_ml
    4. Genera alerta si es riesgo MODERADO/SEVERO
    """
    try:
        # 1. Calcular features ML
        result_features = db.execute(
            text("CALL sp_calcular_features_ml(:p_nin_id)"), {"p_nin_id": nin_id}
        )

        features_row = result_features.fetchone()
        if not features_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se pudieron calcular features para este niño. Verifica que tenga mediciones antropométricas.",
            )

        # Convertir a diccionario
        columns = result_features.keys()
        features_dict = dict(zip(columns, features_row))

        # Extraer IDs necesarios
        ant_id = features_dict.get("ant_id")
        fml_id = features_dict.get("fml_id")

        if not ant_id or not fml_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Features incompletos: faltan ant_id o fml_id",
            )

        # 2. Llamar al modelo ML
        # Importar predictor (lazy loading)
        try:
            import sys
            from pathlib import Path

            # Agregar path del modelo ML
            ml_path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "modelo"
                / "ml-recomendator"
            )
            sys.path.insert(0, str(ml_path))

            from src.domain.models.nutritional_predictor import NutritionalPredictor

            # Cargar modelo (singleton)
            model_path = ml_path / "models" / "nutritional_predictor_latest.pkl"
            if not model_path.exists():
                # Buscar cualquier modelo disponible
                models_dir = ml_path / "models"
                model_files = list(models_dir.glob("nutritional_predictor_*.pkl"))
                if model_files:
                    model_path = max(model_files, key=lambda p: p.stat().st_mtime)
                else:
                    raise FileNotFoundError("No se encontró modelo entrenado")

            predictor = NutritionalPredictor.get_instance(str(model_path))

            if not predictor.is_loaded:
                raise RuntimeError("No se pudo cargar el modelo ML")

            # Preparar features para predicción
            prediction_features = {
                "age_months": features_dict.get("age_months", 120),
                "sex_numeric": features_dict.get("sex_numeric", 1),
                "BMI": features_dict.get("BMI", 18.5),
                "weight_kg": features_dict.get("weight_kg", 35.0),
                "height_cm": features_dict.get("height_cm", 140.0),
                "bmi_velocity": features_dict.get("bmi_velocity", 0.0),
                "weight_velocity": features_dict.get("weight_velocity", 0.0),
                "height_velocity": features_dict.get("height_velocity", 0.0),
                "adherence_score": features_dict.get("adherence_score", 75.0),
                "allergy_count": features_dict.get("allergy_count", 0),
                "altitude_m": features_dict.get("altitude_m", 0.0),
            }

            # Predecir
            prediction = predictor.predict_from_features(prediction_features)

        except Exception as e:
            import logging

            logging.error(f"Error en predicción ML: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al ejecutar modelo ML: {str(e)}",
            )

        # 3. Guardar predicción
        result = db.execute(
            text("""
                CALL sp_guardar_prediccion_ml(
                    :p_nin_id,
                    :p_ant_id,
                    :p_fml_id,
                    :p_clasificacion,
                    :p_probabilidad,
                    :p_score_riesgo,
                    :p_prob_normal,
                    :p_prob_riesgo,
                    :p_prob_moderado,
                    :p_prob_severo,
                    :p_modelo_tipo,
                    :p_modelo_version,
                    :p_features_json,
                    :p_explicacion_json
                )
            """),
            {
                "p_nin_id": nin_id,
                "p_ant_id": ant_id,
                "p_fml_id": fml_id,
                "p_clasificacion": prediction["clasificacion"],
                "p_probabilidad": prediction["probabilidad"],
                "p_score_riesgo": prediction["score_riesgo"],
                "p_prob_normal": prediction["prob_normal"],
                "p_prob_riesgo": prediction["prob_riesgo"],
                "p_prob_moderado": prediction["prob_moderado"],
                "p_prob_severo": prediction["prob_severo"],
                "p_modelo_tipo": "LightGBM",
                "p_modelo_version": "1.0",
                "p_features_json": str(prediction["features_usados"]),
                "p_explicacion_json": str(prediction["features_importantes"]),
            },
        )

        # Obtener predicción guardada
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo guardar la predicción",
            )

        columns = result.keys()
        prediccion_dict = dict(zip(columns, row))

        db.commit()

        return PrediccionMLResponse(**prediccion_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        import logging

        logging.error(f"Error generando predicción: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar predicción: {str(e)}",
        )


@router.get("/nino/{nin_id}", response_model=list[PrediccionMLResponse])
def obtener_predicciones_por_nino(
    nin_id: int,
    limit: int = Query(10, ge=1, le=50, description="Número máximo de predicciones a retornar"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Obtener historial de predicciones ML de un niño.

    Retorna las últimas N predicciones ordenadas por fecha descendente.
    Incluye:
    - Clasificación predicha
    - Probabilidades por categoría
    - Features utilizados
    - Información de validación (si fue validada por nutricionista)
    """
    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            """
            CALL sp_obtener_predicciones_por_nino(
                :p_nin_id,
                :p_limit
            )
            """,
            {"p_nin_id": nin_id, "p_limit": limit},
        )

        # Obtener todos los registros
        rows = result.fetchall()
        columns = result.keys()

        predicciones = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            predicciones.append(PrediccionMLResponse(**row_dict))

        db.commit()
        return predicciones

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener predicciones: {str(e)}",
        )


@router.post("/{pml_id}/validar", response_model=PrediccionMLResponse)
def validar_prediccion_ml(
    pml_id: int,
    validacion: ValidarPrediccionRequest,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Validar o rechazar una predicción ML.

    Solo nutricionistas pueden validar predicciones.
    Permite mejorar el modelo con feedback de profesionales.

    Parámetros:
    - validado: True si la predicción es correcta, False si no
    - feedback: Comentarios opcionales del nutricionista
    """
    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            """
            CALL sp_validar_prediccion_ml(
                :p_pml_id,
                :p_usr_id_validador,
                :p_validado,
                :p_feedback
            )
            """,
            {
                "p_pml_id": pml_id,
                "p_usr_id_validador": current_user.usr_id,
                "p_validado": validacion.validado,
                "p_feedback": validacion.feedback,
            },
        )

        # Obtener resultado
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Predicción no encontrada"
            )

        columns = result.keys()
        prediccion_dict = dict(zip(columns, row))

        db.commit()
        return PrediccionMLResponse(**prediccion_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "no existe" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Predicción o usuario validador no encontrado",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al validar predicción: {error_msg}",
            )
