"""
Endpoints para gestión de síntomas (PMV3)
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.application.services.auth_service import get_current_user
from app.infrastructure.db.session import get_db
from app.schemas.auth import UserResponse
from app.schemas.seguimiento import (
    SintomaCreate,
    SintomaFrecuenciaResponse,
    SintomaResponse,
    SintomaUpdate,
)

router = APIRouter()


@router.post("/registrar", response_model=SintomaResponse, status_code=status.HTTP_201_CREATED)
def registrar_sintoma(
    sintoma: SintomaCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Registrar síntoma del niño.

    Valida:
    - Niño existe
    - Severidad válida (LEVE/MODERADO/SEVERO)

    Genera alerta automática si hay más de 3 síntomas en 7 días.
    """
    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            text("""
            CALL sp_registrar_sintoma(
                :p_nin_id,
                :p_fecha,
                :p_tipo,
                :p_severidad,
                :p_duracion_dias,
                :p_relacionado_menu,
                :p_notas
            )
            """),
            {
                "p_nin_id": sintoma.nin_id,
                "p_fecha": sintoma.fecha,
                "p_tipo": sintoma.tipo,
                "p_severidad": sintoma.severidad.value,
                "p_duracion_dias": sintoma.duracion_dias,
                "p_relacionado_menu": sintoma.relacionado_menu,
                "p_notas": sintoma.notas,
            },
        )

        # Obtener resultado
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo registrar el síntoma"
            )

        columns = result.keys()
        sintoma_dict = dict(zip(columns, row))

        db.commit()
        return SintomaResponse(**sintoma_dict)

    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "no existe" in error_msg.lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Niño no encontrado")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar síntoma: {error_msg}",
            )


@router.get("/nino/{nin_id}", response_model=list[SintomaResponse])
def obtener_sintomas_por_nino(
    nin_id: int,
    fecha_inicio: date | None = Query(None, description="Fecha de inicio (default: hace 30 días)"),
    fecha_fin: date | None = Query(None, description="Fecha de fin (default: hoy)"),
    tipo: str | None = Query(None, description="Filtrar por tipo de síntoma"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Obtener historial de síntomas de un niño.

    Permite filtrar por:
    - Rango de fechas
    - Tipo de síntoma

    Retorna síntomas ordenados por fecha descendente.
    """
    # Valores por defecto
    if not fecha_fin:
        fecha_fin = date.today()
    if not fecha_inicio:
        fecha_inicio = fecha_fin - timedelta(days=30)

    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            text("""
            CALL sp_obtener_sintomas_por_nino(
                :p_nin_id,
                :p_fecha_inicio,
                :p_fecha_fin,
                :p_tipo
            )
            """),
            {
                "p_nin_id": nin_id,
                "p_fecha_inicio": fecha_inicio,
                "p_fecha_fin": fecha_fin,
                "p_tipo": tipo,
            },
        )

        rows = result.fetchall()
        columns = result.keys()

        sintomas = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            sintomas.append(SintomaResponse(**row_dict))

        db.commit()
        return sintomas

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener síntomas: {str(e)}",
        )


@router.put("/{sin_id}", response_model=SintomaResponse)
def actualizar_sintoma(
    sin_id: int,
    sintoma: SintomaUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Actualizar un registro de síntoma existente.

    Permite actualizar:
    - Tipo de síntoma
    - Severidad
    - Duración en días
    - Relación con menú
    - Notas
    """
    try:
        # Verificar que el registro existe
        check_result = db.execute(
            text("SELECT sin_id FROM sintomas WHERE sin_id = :sin_id"),
            {"sin_id": sin_id},
        )
        if not check_result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de síntoma no encontrado",
            )

        # Construir query dinámico solo con campos proporcionados
        update_fields = []
        params = {"sin_id": sin_id}

        if sintoma.tipo is not None:
            update_fields.append("sin_tipo = :tipo")
            params["tipo"] = sintoma.tipo

        if sintoma.severidad is not None:
            update_fields.append("sin_severidad = :severidad")
            params["severidad"] = sintoma.severidad.value
            # Actualizar grado según severidad
            grado_map = {"LEVE": 1, "MODERADO": 2, "SEVERO": 3}
            update_fields.append("sin_grado = :grado")
            params["grado"] = grado_map[sintoma.severidad.value]

        if sintoma.duracion_dias is not None:
            update_fields.append("sin_duracion_dias = :duracion_dias")
            params["duracion_dias"] = sintoma.duracion_dias

        if sintoma.relacionado_menu is not None:
            update_fields.append("sin_relacionado_menu = :relacionado_menu")
            params["relacionado_menu"] = sintoma.relacionado_menu

        if sintoma.notas is not None:
            update_fields.append("sin_notas = :notas")
            params["notas"] = sintoma.notas

        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        # Ejecutar actualización
        query = f"UPDATE sintomas SET {', '.join(update_fields)} WHERE sin_id = :sin_id"
        db.execute(text(query), params)

        # Obtener registro actualizado
        result = db.execute(
            text("""
                SELECT
                    sin_id, nin_id,
                    sin_fecha as fecha,
                    sin_tipo as tipo,
                    sin_severidad as severidad,
                    sin_grado as grado,
                    sin_duracion_dias as duracion_dias,
                    sin_relacionado_menu as relacionado_menu,
                    sin_notas as notas,
                    creado_en
                FROM sintomas
                WHERE sin_id = :sin_id
            """),
            {"sin_id": sin_id},
        )

        row = result.fetchone()
        columns = result.keys()
        sintoma_dict = dict(zip(columns, row))

        db.commit()
        return SintomaResponse(**sintoma_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar síntoma: {str(e)}",
        )


@router.delete("/{sin_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_sintoma(
    sin_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Eliminar un registro de síntoma.
    """
    try:
        result = db.execute(
            text("DELETE FROM sintomas WHERE sin_id = :sin_id"),
            {"sin_id": sin_id},
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de síntoma no encontrado",
            )

        db.commit()
        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar síntoma: {str(e)}",
        )


@router.get("/nino/{nin_id}/frecuencia", response_model=SintomaFrecuenciaResponse)
def calcular_frecuencia_sintomas(
    nin_id: int,
    dias: int = Query(30, ge=1, le=365, description="Número de días a analizar"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Calcular frecuencia y severidad de síntomas de los últimos N días.

    Retorna:
    - Frecuencia total de síntomas
    - Severidad promedio (1-3)
    - Síntomas en los últimos 7 días
    - Indicador de síntomas recientes
    """
    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            text("""
            CALL sp_calcular_frecuencia_sintomas(
                :p_nin_id,
                :p_dias
            )
            """),
            {"p_nin_id": nin_id, "p_dias": dias},
        )

        # Obtener resultado
        row = result.fetchone()
        if not row:
            # Si no hay síntomas, retornar valores en cero
            return SintomaFrecuenciaResponse(
                frecuencia_total=0,
                severidad_promedio=0.0,
                sintomas_recientes_7dias=0,
                tiene_sintomas_recientes=False,
            )

        columns = result.keys()
        frecuencia_dict = dict(zip(columns, row))

        db.commit()
        return SintomaFrecuenciaResponse(**frecuencia_dict)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular frecuencia de síntomas: {str(e)}",
        )
