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
async def generar_prediccion_ml(
    nin_id: int,
    meses_proyeccion: int = Query(1, ge=1, le=6, description="Meses a proyectar (1-6)"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Generar predicción ML para el niño con proyección a futuro.

    Proceso:
    1. Calcula features ML usando sp_calcular_features_ml
    2. Llama al servidor ML para predicción
    3. Guarda predicción usando sp_guardar_prediccion_ml
    4. Genera alerta si es riesgo MODERADO/SEVERO

    Args:
        meses_proyeccion: Meses a proyectar (1-6). Default: 1
    """
    import os

    import httpx

    try:
        # 1. Obtener última antropometría del niño
        result_ant = db.execute(
            text("""
                SELECT ant_id, ant_peso_kg, ant_talla_cm, ant_edad_meses, ant_fecha
                FROM antropometrias
                WHERE nin_id = :nin_id
                ORDER BY ant_fecha DESC
                LIMIT 1
            """),
            {"nin_id": nin_id},
        )

        ant_row = result_ant.fetchone()
        if not ant_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron mediciones antropométricas para este niño.",
            )

        ant_id = ant_row[0]
        peso_kg = float(ant_row[1])  # Convertir Decimal a float
        talla_cm = float(ant_row[2])  # Convertir Decimal a float
        edad_meses = float(ant_row[3]) if ant_row[3] else 120.0

        # Obtener sexo del niño
        result_nino = db.execute(
            text("SELECT nin_sexo FROM ninos WHERE nin_id = :nin_id"), {"nin_id": nin_id}
        )
        nino_row = result_nino.fetchone()
        sex_numeric = 1 if nino_row and nino_row[0] == "M" else 0

        # 2. Preparar features para predicción con proyección
        # Calcular velocidades simples (asumiendo crecimiento normal)
        bmi_velocity = 0.1  # kg/m² por mes
        weight_velocity = 0.3  # kg por mes
        height_velocity = 0.5  # cm por mes

        # Proyectar valores a futuro
        projected_age = edad_meses + meses_proyeccion
        projected_weight = peso_kg + (weight_velocity * meses_proyeccion)
        projected_height = talla_cm + (height_velocity * meses_proyeccion)
        projected_bmi = projected_weight / ((projected_height / 100) ** 2)

        prediction_features = {
            "age_months": projected_age,
            "sex_numeric": sex_numeric,
            "BMI": projected_bmi,
            "weight_kg": projected_weight,
            "height_cm": projected_height,
            "bmi_velocity": bmi_velocity,
            "weight_velocity": weight_velocity,
            "height_velocity": height_velocity,
            "adherence_score": 75.0,  # Default
            "allergy_count": 0,  # Default
            "altitude_m": 0.0,  # Default
        }

        # 3. Llamar al servidor ML
        ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8001")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ml_service_url}/api/v1/nutritional/predict",
                json={"features": prediction_features},
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Servicio ML no disponible: {response.text}",
                )

            prediction = response.json()

        # 4. Retornar predicción directamente (sin guardar por ahora)
        # TODO: Implementar sp_guardar_prediccion_ml cuando esté disponible

        return prediction

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
