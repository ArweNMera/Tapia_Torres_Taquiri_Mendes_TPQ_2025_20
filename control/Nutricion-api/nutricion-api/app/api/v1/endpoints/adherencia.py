"""
Endpoints para gestión de adherencia al plan nutricional (PMV3)
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.application.services.auth_service import get_current_user
from app.infrastructure.db.session import get_db
from app.schemas.auth import UserResponse
from app.schemas.seguimiento import (
    AdherenciaCreate,
    AdherenciaHistorialResponse,
    AdherenciaPromedioResponse,
    AdherenciaResponse,
    AdherenciaUpdate,
)

router = APIRouter()


@router.post("/registrar", response_model=AdherenciaResponse, status_code=status.HTTP_201_CREATED)
def registrar_adherencia(
    adherencia: AdherenciaCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Registrar adherencia diaria al plan nutricional.

    Valida:
    - Niño y menú existen
    - Fecha no es futura
    - Porcentaje entre 0-100

    Si ya existe registro para esa fecha, lo actualiza.
    """
    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            text("""
            CALL sp_registrar_adherencia(
                :p_nin_id,
                :p_men_id,
                :p_mei_id,
                :p_fecha,
                :p_estado,
                :p_porcentaje,
                :p_dificultad,
                :p_comentario
            )
            """),
            {
                "p_nin_id": adherencia.nin_id,
                "p_men_id": adherencia.men_id,
                "p_mei_id": adherencia.mei_id,
                "p_fecha": adherencia.fecha,
                "p_estado": adherencia.estado.value,
                "p_porcentaje": adherencia.porcentaje,
                "p_dificultad": adherencia.dificultad.value,
                "p_comentario": adherencia.comentario,
            },
        )

        # Obtener resultado
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo registrar la adherencia",
            )

        # Convertir a diccionario
        columns = result.keys()
        adherencia_dict = dict(zip(columns, row))

        db.commit()
        return AdherenciaResponse(**adherencia_dict)

    except Exception as e:
        db.rollback()
        error_msg = str(e)
        if "fecha futura" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede registrar adherencia para fechas futuras",
            )
        elif "no existe" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Niño o menú no encontrado"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar adherencia: {error_msg}",
            )


@router.get("/nino/{nin_id}", response_model=AdherenciaHistorialResponse)
def obtener_adherencia_por_nino(
    nin_id: int,
    fecha_inicio: date | None = Query(None, description="Fecha de inicio (default: hace 30 días)"),
    fecha_fin: date | None = Query(None, description="Fecha de fin (default: hoy)"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Obtener historial de adherencia de un niño con estadísticas.

    Retorna:
    - Lista de registros de adherencia
    - Adherencia promedio del período
    - Días con dificultad alta
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
            CALL sp_obtener_adherencia_por_nino(
                :p_nin_id,
                :p_fecha_inicio,
                :p_fecha_fin
            )
            """),
            {"p_nin_id": nin_id, "p_fecha_inicio": fecha_inicio, "p_fecha_fin": fecha_fin},
        )

        rows = result.fetchall()
        columns = result.keys()

        registros = []
        adherencia_promedio = 0.0
        dias_con_dificultad_alta = 0

        for row in rows:
            row_dict = dict(zip(columns, row))

            # Extraer estadísticas (vienen en cada fila)
            if "adherencia_promedio" in row_dict and row_dict["adherencia_promedio"]:
                adherencia_promedio = float(row_dict["adherencia_promedio"])
            if "dias_dificultad_alta" in row_dict and row_dict["dias_dificultad_alta"]:
                dias_con_dificultad_alta = int(row_dict["dias_dificultad_alta"])

            registros.append(AdherenciaResponse(**row_dict))

        db.commit()

        return AdherenciaHistorialResponse(
            registros=registros,
            adherencia_promedio=adherencia_promedio,
            dias_con_dificultad_alta=dias_con_dificultad_alta,
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener adherencia: {str(e)}",
        )


@router.put("/{adh_id}", response_model=AdherenciaResponse)
def actualizar_adherencia(
    adh_id: int,
    adherencia: AdherenciaUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Actualizar un registro de adherencia existente.

    Permite actualizar:
    - Estado de cumplimiento
    - Porcentaje
    - Dificultad
    - Comentarios
    """
    try:
        # Verificar que el registro existe
        check_result = db.execute(
            text("SELECT adh_id FROM adherencias WHERE adh_id = :adh_id"),
            {"adh_id": adh_id},
        )
        if not check_result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de adherencia no encontrado",
            )

        # Construir query dinámico solo con campos proporcionados
        update_fields = []
        params = {"adh_id": adh_id}

        if adherencia.estado is not None:
            update_fields.append("adh_estado = :estado")
            params["estado"] = adherencia.estado.value

        if adherencia.porcentaje is not None:
            update_fields.append("adh_porcentaje = :porcentaje")
            params["porcentaje"] = adherencia.porcentaje

        if adherencia.dificultad is not None:
            update_fields.append("adh_dificultad = :dificultad")
            params["dificultad"] = adherencia.dificultad.value

        if adherencia.comentario is not None:
            update_fields.append("adh_comentario = :comentario")
            params["comentario"] = adherencia.comentario

        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionaron campos para actualizar",
            )

        # Ejecutar actualización
        query = f"UPDATE adherencias SET {', '.join(update_fields)} WHERE adh_id = :adh_id"
        db.execute(text(query), params)

        # Obtener registro actualizado
        result = db.execute(
            text("""
                SELECT
                    adh_id, nin_id, men_id, mei_id,
                    adh_fecha,
                    adh_estado,
                    adh_porcentaje,
                    adh_dificultad,
                    adh_comentario
                FROM adherencias
                WHERE adh_id = :adh_id
            """),
            {"adh_id": adh_id},
        )

        row = result.fetchone()
        columns = result.keys()
        adherencia_dict = dict(zip(columns, row))

        db.commit()
        return AdherenciaResponse(**adherencia_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar adherencia: {str(e)}",
        )


@router.delete("/{adh_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_adherencia(
    adh_id: int,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Eliminar un registro de adherencia.
    """
    try:
        result = db.execute(
            text("DELETE FROM adherencias WHERE adh_id = :adh_id"),
            {"adh_id": adh_id},
        )

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro de adherencia no encontrado",
            )

        db.commit()
        return None

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar adherencia: {str(e)}",
        )


@router.get("/nino/{nin_id}/promedio", response_model=AdherenciaPromedioResponse)
def calcular_adherencia_promedio(
    nin_id: int,
    dias: int = Query(30, ge=1, le=365, description="Número de días a analizar"),
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Calcular adherencia promedio y consistencia de los últimos N días.

    Retorna:
    - Adherencia promedio (0-100)
    - Consistencia (basada en desviación estándar)
    - Total de registros
    - Días analizados
    """
    try:
        # Ejecutar procedimiento almacenado
        result = db.execute(
            text("""
            CALL sp_calcular_adherencia_promedio(
                :p_nin_id,
                :p_dias
            )
            """),
            {"p_nin_id": nin_id, "p_dias": dias},
        )

        # Obtener resultado
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay datos de adherencia para este niño",
            )

        columns = result.keys()
        promedio_dict = dict(zip(columns, row))

        db.commit()
        return AdherenciaPromedioResponse(**promedio_dict)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular adherencia promedio: {str(e)}",
        )
