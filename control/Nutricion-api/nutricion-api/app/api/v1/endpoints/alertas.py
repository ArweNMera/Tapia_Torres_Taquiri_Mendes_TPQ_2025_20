"""
Endpoints para gestión de alertas automáticas (PMV3)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.services.auth_service import get_current_user
from app.infrastructure.db.session import get_db
from app.schemas.auth import UserResponse
from app.schemas.seguimiento import AlertaResponse, VerificarAlertasResponse

router = APIRouter()


@router.post("/verificar/{nin_id}", response_model=VerificarAlertasResponse)
def verificar_alertas_automaticas(
    nin_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Verificar y generar alertas automáticas para un niño.

    Verifica 4 condiciones:
    1. TENDENCIA_NEGATIVA: 3 mediciones consecutivas empeorando
    2. BAJA_ADHERENCIA: <60% en últimas 2 semanas
    3. SINTOMAS_FRECUENTES: >5 síntomas en 7 días
    4. RIESGO_CRITICO_ML: Predicción de DESNUTRICION_SEVERA u OBESIDAD

    Genera notificaciones para el nutricionista asignado.
    """
    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            """
            CALL sp_verificar_alertas_automaticas(
                :p_nin_id
            )
            """,
            {"p_nin_id": nin_id},
        )

        # Obtener todas las alertas generadas
        rows = result.fetchall()
        columns = result.keys()

        alertas = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            alertas.append(AlertaResponse(**row_dict))

        db.commit()

        return VerificarAlertasResponse(alertas_generadas=alertas, total_alertas=len(alertas))

    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "no existe" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Niño no encontrado")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al verificar alertas: {error_msg}",
            )
