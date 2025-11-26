"""
Endpoints para visualización de evolución nutricional (PMV3)
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.services.auth_service import get_current_user
from app.infrastructure.db.session import get_db
from app.schemas.auth import UserResponse
from app.schemas.seguimiento import (
    EvolucionDataPoint,
    EvolucionResponse,
    TendenciaResponse,
)

router = APIRouter()


@router.get("/nino/{nin_id}", response_model=EvolucionResponse)
def obtener_evolucion_nutricional(
    nin_id: int,
    fecha_inicio: date | None = Query(None, description="Fecha de inicio (default: hace 6 meses)"),
    fecha_fin: date | None = Query(None, description="Fecha de fin (default: hoy)"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Obtener evolución nutricional completa de un niño.

    Incluye:
    - Antropometrías (peso, talla, IMC)
    - Evaluaciones nutricionales (z-score, clasificación)
    - Adherencia promedio de 7 días por medición
    - Conteo de síntomas de 7 días por medición

    Permite visualizar gráficos de evolución con contexto completo.
    """
    # Valores por defecto
    if not fecha_fin:
        fecha_fin = date.today()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=180)  # 6 meses

    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            """
            CALL sp_obtener_evolucion_nutricional(
                :p_nin_id,
                :p_fecha_inicio,
                :p_fecha_fin
            )
            """,
            {"p_nin_id": nin_id, "p_fecha_inicio": fecha_inicio, "p_fecha_fin": fecha_fin},
        )

        # Obtener todos los registros
        rows = result.fetchall()
        columns = result.keys()

        if not rows:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay datos de evolución para este niño en el rango especificado",
            )

        datos = []
        nin_nombres = None

        for row in rows:
            row_dict = dict(zip(columns, row))

            # Extraer nombre del niño (viene en cada fila)
            if not nin_nombres and "nin_nombres" in row_dict:
                nin_nombres = row_dict.get("nin_nombres")

            # Crear punto de datos
            datos.append(EvolucionDataPoint(**row_dict))

        db.commit()

        return EvolucionResponse(
            nin_id=nin_id,
            nin_nombres=nin_nombres or "Desconocido",
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            datos=datos,
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener evolución nutricional: {str(e)}",
        )


@router.get("/nino/{nin_id}/tendencia", response_model=TendenciaResponse)
def calcular_tendencia_nutricional(
    nin_id: int,
    ultimas_mediciones: int = Query(3, ge=2, le=10, description="Número de mediciones a analizar"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Calcular tendencia nutricional del niño.

    Analiza las últimas N mediciones para determinar:
    - Tendencia general (MEJORANDO/ESTABLE/EMPEORANDO)
    - Velocidades de cambio (BMI, peso, talla, z-score)

    Útil para detectar deterioro o mejora temprana.
    """
    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            """
            CALL sp_calcular_tendencia_nutricional(
                :p_nin_id,
                :p_ultimas_mediciones
            )
            """,
            {"p_nin_id": nin_id, "p_ultimas_mediciones": ultimas_mediciones},
        )

        # Obtener resultado
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay suficientes datos para calcular tendencia",
            )

        columns = result.keys()
        tendencia_dict = dict(zip(columns, row))

        # Agregar número de mediciones analizadas
        tendencia_dict["mediciones_analizadas"] = ultimas_mediciones

        db.commit()
        return TendenciaResponse(**tendencia_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "datos insuficientes" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay suficientes mediciones para calcular tendencia",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al calcular tendencia: {error_msg}",
            )
