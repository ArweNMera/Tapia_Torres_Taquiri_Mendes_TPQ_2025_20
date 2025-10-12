from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.domain.interfaces.ninos_repository import INinosRepository
from app.domain.utils.nutrition_recommendations import (
    generar_recomendaciones_nutricionales,
    mapear_recomendacion_desde_db,
)
from app.schemas.ninos import AnthropometryCreate, NinoCreate, NinoUpdate


class NinosRepository(INinosRepository):
    def __init__(self, db: Session):
        self.db = db

    def _map_nino_row(self, row: Any) -> dict[str, Any]:
        return {
            "nin_id": row.nin_id,
            "ent_id": getattr(row, "ent_id", None),
            "nin_nombres": getattr(row, "nin_nombres", None),
            "nin_fecha_nac": row.nin_fecha_nac.isoformat()
            if getattr(row, "nin_fecha_nac", None)
            else None,
            "nin_sexo": getattr(row, "nin_sexo", None),
            "usr_id_tutor": getattr(row, "usr_id_tutor", None),
            "usr_id_propietario": getattr(row, "usr_id_propietario", None),
            "nin_autogestion": bool(getattr(row, "nin_autogestion", 0)),
            "usr_id_responsable": getattr(row, "usr_id_responsable", None),
            "usr_nombre": getattr(row, "usr_nombre", None),
            "usr_apellido": getattr(row, "usr_apellido", None),
            "usr_dni": getattr(row, "usr_dni", None),
            "usr_correo": getattr(row, "usr_correo", None),
            "telefono_resp": getattr(row, "telefono_resp", None),
            "direccion_resp": getattr(row, "direccion_resp", None),
            "genero_resp": getattr(row, "genero_resp", None),
            "idioma_resp": getattr(row, "idioma_resp", None),
            "edad_meses": getattr(row, "edad_meses", 0),
            "creado_en": row.creado_en.isoformat() if getattr(row, "creado_en", None) else None,
            "actualizado_en": row.actualizado_en.isoformat()
            if getattr(row, "actualizado_en", None)
            else None,
            "ent_nombre": getattr(row, "ent_nombre", None),
            "ent_codigo": getattr(row, "ent_codigo", None),
            "ent_direccion": getattr(row, "ent_direccion", None),
            "ent_departamento": getattr(row, "ent_departamento", None),
            "ent_provincia": getattr(row, "ent_provincia", None),
            "ent_distrito": getattr(row, "ent_distrito", None),
        }

    def _map_antropometria_row(self, row: Any) -> dict[str, Any]:
        return {
            "ant_id": row.ant_id,
            "nin_id": row.nin_id,
            "ant_fecha": row.ant_fecha,
            "ant_edad_meses": getattr(row, "ant_edad_meses", None),
            "ant_peso_kg": float(row.ant_peso_kg)
            if getattr(row, "ant_peso_kg", None) is not None
            else None,
            "ant_talla_cm": float(row.ant_talla_cm)
            if getattr(row, "ant_talla_cm", None) is not None
            else None,
            "ant_z_imc": float(row.ant_z_imc)
            if getattr(row, "ant_z_imc", None) is not None
            else None,
            "ant_z_peso_edad": float(row.ant_z_peso_edad)
            if getattr(row, "ant_z_peso_edad", None) is not None
            else None,
            "ant_z_talla_edad": float(row.ant_z_talla_edad)
            if getattr(row, "ant_z_talla_edad", None) is not None
            else None,
            "imc": float(getattr(row, "imc", None))
            if getattr(row, "imc", None) is not None
            else None,
            "creado_en": row.creado_en.isoformat() if getattr(row, "creado_en", None) else None,
        }

    def crear_nino(self, nino_data: dict[str, Any]) -> dict[str, Any] | None:
        """Crear un nuevo perfil de niño usando procedimientos almacenados."""
        try:
            import logging

            logger = logging.getLogger(__name__)

            payload = dict(nino_data or {})
            nin_fecha_nac = payload.get("nin_fecha_nac")
            if isinstance(nin_fecha_nac, str):
                nin_fecha_nac = date.fromisoformat(nin_fecha_nac)
            if nin_fecha_nac is None:
                raise ValueError("nin_fecha_nac es requerido")

            nin_sexo = payload.get("nin_sexo")
            if hasattr(nin_sexo, "value"):
                nin_sexo = nin_sexo.value
            payload["nin_sexo"] = nin_sexo

            today = date.today()
            age_years = (
                today.year
                - nin_fecha_nac.year
                - ((today.month, today.day) < (nin_fecha_nac.month, nin_fecha_nac.day))
            )

            usr_id_tutor = payload.get("usr_id_tutor")
            usr_id_propietario = payload.get("usr_id_propietario")

            params = {
                "nin_nombres": payload.get("nin_nombres"),
                "fecha_nac": nin_fecha_nac,
                "sexo": nin_sexo,
                "ent_id": payload.get("ent_id"),
                "usr_id_tutor": None,
                "usr_id_propietario": None,
            }

            if age_years >= 13:
                params["usr_id_propietario"] = usr_id_propietario or usr_id_tutor
            else:
                params["usr_id_tutor"] = usr_id_tutor or usr_id_propietario

            logger.warning("🔍 REPOSITORIO crear_nino - Parámetros a SP:")
            logger.warning(f"  nin_nombres: {params['nin_nombres']}")
            logger.warning(f"  fecha_nac: {params['fecha_nac']}")
            logger.warning(f"  sexo: {params['sexo']}")
            logger.warning(f"  edad calculada: {age_years} años")
            logger.warning(f"  usr_id_tutor: {params['usr_id_tutor']}")
            logger.warning(f"  usr_id_propietario: {params['usr_id_propietario']}")

            result = self.db.execute(
                text(
                    "CALL sp_ninos_crear(:nin_nombres, :fecha_nac, :sexo, :ent_id, :usr_id_tutor, :usr_id_propietario)"
                ),
                params,
            ).fetchone()

            self.db.commit()

            if result and getattr(result, "nin_id", None):
                return self.obtener_nino(result.nin_id)
            return None

        except Exception as exc:
            self.db.rollback()
            raise exc

    def create_nino(self, nino_data: NinoCreate, usr_id_tutor: int) -> dict[str, Any] | None:
        payload = nino_data.model_dump()
        payload["usr_id_tutor"] = usr_id_tutor
        if hasattr(nino_data.nin_sexo, "value"):
            payload["nin_sexo"] = nino_data.nin_sexo.value
        return self.crear_nino(payload)

    def obtener_nino(self, nin_id: int) -> dict[str, Any] | None:
        """Obtener un niño por su ID usando sp_ninos_get."""
        import logging

        logger = logging.getLogger(__name__)

        result = self.db.execute(
            text("CALL sp_ninos_get(:nin_id)"),
            {"nin_id": nin_id},
        ).fetchone()

        if not result:
            return None

        logger.warning(f"🔍 obtener_nino({nin_id}) - Resultado de sp_ninos_get:")
        logger.warning(f"  nin_nombres: {getattr(result, 'nin_nombres', 'N/A')}")
        logger.warning(f"  nin_fecha_nac: {getattr(result, 'nin_fecha_nac', 'N/A')}")
        logger.warning(f"  nin_sexo: {getattr(result, 'nin_sexo', 'N/A')}")

        mapped = self._map_nino_row(result)
        logger.warning("🔍 Después de _map_nino_row:")
        logger.warning(f"  nin_nombres: {mapped.get('nin_nombres')}")
        logger.warning(f"  nin_fecha_nac: {mapped.get('nin_fecha_nac')}")

        return mapped

    def get_nino_by_id(self, nin_id: int) -> dict[str, Any] | None:
        return self.obtener_nino(nin_id)

    def get_nino_by_owner(self, usr_id_propietario: int) -> dict[str, Any] | None:
        """Obtener un niño asociado como propietario (autogestión)"""
        result = self.db.execute(
            text("CALL sp_ninos_obtener_por_propietario(:usr_id_propietario)"),
            {"usr_id_propietario": usr_id_propietario},
        ).fetchone()

        if not result:
            return None

        return self._map_nino_row(result)

    def get_ninos_by_tutor(self, usr_id_tutor: int) -> list[dict[str, Any]]:
        """Obtener todos los niños asociados al usuario usando sp_ninos_obtener_por_tutor."""
        results = self.db.execute(
            text("CALL sp_ninos_obtener_por_tutor(:usr_id_tutor)"), {"usr_id_tutor": usr_id_tutor}
        ).fetchall()

        return [
            {
                "nin_id": row.nin_id,
                "usr_id_tutor": row.usr_id_tutor,
                "ent_id": row.ent_id,
                "nin_nombres": row.nin_nombres,
                "nin_fecha_nac": row.nin_fecha_nac.isoformat() if row.nin_fecha_nac else None,
                "nin_sexo": row.nin_sexo,
                "ent_nombre": row.ent_nombre if hasattr(row, "ent_nombre") else None,
                "ent_codigo": row.ent_codigo if hasattr(row, "ent_codigo") else None,
                "ent_direccion": row.ent_direccion if hasattr(row, "ent_direccion") else None,
                "ent_departamento": row.ent_departamento
                if hasattr(row, "ent_departamento")
                else None,
                "ent_provincia": row.ent_provincia if hasattr(row, "ent_provincia") else None,
                "ent_distrito": row.ent_distrito if hasattr(row, "ent_distrito") else None,
                "edad_meses": row.edad_meses,
                "creado_en": row.creado_en.isoformat() if row.creado_en else None,
                "actualizado_en": row.actualizado_en.isoformat() if row.actualizado_en else None,
            }
            for row in results
        ]

    def actualizar_nino(self, nin_id: int, nino_data: dict[str, Any]) -> dict[str, Any] | None:
        """Actualizar datos de un niño usando procedimiento almacenado."""
        try:
            payload = dict(nino_data or {})
            fecha_nac = payload.get("nin_fecha_nac")
            if isinstance(fecha_nac, str):
                fecha_nac = date.fromisoformat(fecha_nac)

            self.db.execute(
                text("CALL sp_ninos_actualizar(:nin_id, :nin_nombres, :ent_id, :nin_fecha_nac)"),
                {
                    "nin_id": nin_id,
                    "nin_nombres": payload.get("nin_nombres"),
                    "ent_id": payload.get("ent_id"),
                    "nin_fecha_nac": fecha_nac,
                },
            ).fetchone()

            self.db.commit()
            return self.obtener_nino(nin_id)

        except Exception as exc:
            self.db.rollback()
            raise exc

    def update_nino(self, nin_id: int, nino_data: NinoUpdate) -> dict[str, Any] | None:
        return self.actualizar_nino(nin_id, nino_data.model_dump(exclude_unset=True))

    def promote_child_to_owner(self, nin_id: int, usr_id_propietario: int) -> dict[str, Any] | None:
        """Promover un niño existente (donde el usuario es tutor) a propietario.
        Útil para reconciliar el perfil personal (self child).
        """
        try:
            self.db.execute(
                text(
                    "CALL sp_ninos_cambiar_responsable(:nin_id, :autogestion, :usr_id_responsable)"
                ),
                {
                    "nin_id": nin_id,
                    "autogestion": 1,
                    "usr_id_responsable": usr_id_propietario,
                },
            ).fetchone()
            self.db.commit()
            return self.obtener_nino(nin_id)
        except Exception as e:
            self.db.rollback()
            raise e

    def assign_child_to_tutor(self, nin_id: int, usr_id_tutor: int) -> dict[str, Any] | None:
        """Asociar un niño existente a un tutor/padre usando SP dedicado."""
        try:
            self.db.execute(
                text(
                    "CALL sp_ninos_cambiar_responsable(:nin_id, :autogestion, :usr_id_responsable)"
                ),
                {
                    "nin_id": nin_id,
                    "autogestion": 0,
                    "usr_id_responsable": usr_id_tutor,
                },
            ).fetchone()
            self.db.commit()
            return self.obtener_nino(nin_id)
        except Exception as e:
            self.db.rollback()
            raise e

    def agregar_antropometria(self, nin_id: int, ant_data: dict[str, Any]) -> dict[str, Any] | None:
        """Agregar datos antropométricos usando procedimiento almacenado."""
        try:
            payload = dict(ant_data or {})
            fecha = payload.get("ant_fecha")
            if isinstance(fecha, str):
                fecha = date.fromisoformat(fecha)
            if fecha is None:
                fecha = date.today()

            result = self.db.execute(
                text("CALL sp_antropometria_agregar(:nin_id, :fecha, :peso_kg, :talla_cm)"),
                {
                    "nin_id": nin_id,
                    "fecha": fecha,
                    "peso_kg": payload.get("ant_peso_kg"),
                    "talla_cm": payload.get("ant_talla_cm"),
                },
            ).fetchone()

            self.db.commit()
            return self._map_antropometria_row(result) if result else None

        except Exception as exc:
            self.db.rollback()
            raise exc

    def create_antropometria(
        self, nin_id: int, antropo_data: AnthropometryCreate
    ) -> dict[str, Any] | None:
        return self.agregar_antropometria(nin_id, antropo_data.model_dump())

    def get_antropometria_by_nino_fecha(self, nin_id: int, fecha: date) -> dict[str, Any] | None:
        """Obtener antropometría específica por niño y fecha"""
        result = self.db.execute(
            text("CALL sp_antropometria_obtener_por_fecha(:nin_id, :fecha)"),
            {"nin_id": nin_id, "fecha": fecha},
        ).fetchone()

        if not result:
            return None

        return self._map_antropometria_row(result)

    def get_antropometrias_by_nino(
        self, nin_id: int, limit: int | None = None
    ) -> list[dict[str, Any]]:
        """Obtener todas las antropometrías de un niño usando procedimiento almacenado"""
        results = self.db.execute(
            text("CALL sp_antropometria_obtener_por_nino(:nin_id, :limit)"),
            {"nin_id": nin_id, "limit": limit},
        ).fetchall()

        return [
            {
                "ant_id": row.ant_id,
                "nin_id": row.nin_id,
                "ant_fecha": row.ant_fecha,
                "ant_peso_kg": float(row.ant_peso_kg),
                "ant_talla_cm": float(row.ant_talla_cm),
                "ant_z_imc": float(row.ant_z_imc) if row.ant_z_imc else None,
                "ant_z_peso_edad": float(row.ant_z_peso_edad) if row.ant_z_peso_edad else None,
                "ant_z_talla_edad": float(row.ant_z_talla_edad) if row.ant_z_talla_edad else None,
                "imc": (
                    float(getattr(row, "imc", None) or getattr(row, "imc_calculado", None))
                    if (
                        getattr(row, "imc", None) is not None
                        or getattr(row, "imc_calculado", None) is not None
                    )
                    else None
                ),
                "creado_en": row.creado_en.isoformat() if row.creado_en else None,
            }
            for row in results
        ]

    def get_latest_antropometria(self, nin_id: int) -> dict[str, Any] | None:
        """Obtener la antropometría más reciente usando procedimiento almacenado"""
        result = self.db.execute(
            text("CALL sp_antropometria_obtener_ultima(:nin_id)"),
            {"nin_id": nin_id},
        ).fetchone()

        if not result:
            return None

        return self._map_antropometria_row(result)

    def delete_nino(self, nin_id: int) -> bool:
        """Eliminar un niño (por ahora hard delete)"""
        try:
            result = self.db.execute(
                text("CALL sp_ninos_eliminar(:nin_id)"),
                {"nin_id": nin_id},
            ).fetchone()
            self.db.commit()
            return bool(result and getattr(result, "filas_afectadas", 0))
        except Exception as e:
            self.db.rollback()
            raise e

    def evaluar_estado_nutricional(self, nin_id: int) -> dict[str, Any] | None:
        """
        Evalúa el estado nutricional usando exclusivamente el procedimiento almacenado.
        Retorna métricas normalizadas y recomendaciones generadas en base al resultado.
        """

        try:
            result = self.db.execute(
                text("CALL sp_evaluar_estado_nutricional(:nin_id)"), {"nin_id": nin_id}
            ).fetchone()
            self.db.commit()

            if not result:
                return None

            en_z_score = float(result.en_z_score_imc) if result.en_z_score_imc is not None else None
            percentil = (
                float(result.percentil_calculado)
                if result.percentil_calculado is not None
                else None
            )
            imc = float(result.imc_calculado) if result.imc_calculado is not None else None
            riesgo_pct = (
                float(result.riesgo_porcentaje)
                if getattr(result, "riesgo_porcentaje", None) is not None
                else None
            )
            edad_meses = int(result.en_edad_meses) if result.en_edad_meses is not None else 0

            recomendaciones: list[dict[str, str]] = []
            en_id = getattr(result, "en_id", None)

            if en_id:
                rec_rows = self.db.execute(
                    text("""
                        SELECT rt.rt_codigo, rt.rt_titulo, rt.rt_descripcion
                        FROM evaluaciones_recomendaciones er
                        JOIN recomendaciones_tipos rt ON rt.rt_id = er.rt_id
                        WHERE er.en_id = :en_id
                        ORDER BY rt.rt_prioridad ASC, rt.rt_id ASC
                        LIMIT 5
                    """),
                    {"en_id": en_id},
                ).fetchall()

                recomendaciones = [
                    mapear_recomendacion_desde_db(row.rt_codigo, row.rt_titulo, row.rt_descripcion)
                    for row in rec_rows
                ]

            if not recomendaciones:
                recomendaciones = generar_recomendaciones_nutricionales(
                    result.en_clasificacion, imc or 0, edad_meses
                )

            return {
                "en_id": en_id,
                "nin_id": getattr(result, "nin_id", None),
                "ant_id": getattr(result, "ant_id", None),
                "ant_fecha": getattr(result, "ant_fecha", None).isoformat()
                if getattr(result, "ant_fecha", None)
                else None,
                "en_edad_meses": edad_meses,
                "peso_kg": float(result.peso_kg)
                if getattr(result, "peso_kg", None) is not None
                else None,
                "talla_cm": float(result.talla_cm)
                if getattr(result, "talla_cm", None) is not None
                else None,
                "imc_calculado": imc,
                "en_z_score_imc": en_z_score,
                "percentil_calculado": percentil,
                "en_clasificacion": result.en_clasificacion,
                "en_nivel_riesgo": result.en_nivel_riesgo,
                "riesgo_porcentaje": riesgo_pct,
                "oms_usado": bool(result.oms_usado)
                if getattr(result, "oms_usado", None) is not None
                else False,
                "evaluado_en": result.evaluado_en.isoformat()
                if getattr(result, "evaluado_en", None)
                else None,
                "recomendaciones": recomendaciones,
                "probabilidad": riesgo_pct,
                "probabilidades": {result.en_clasificacion: 1.0}
                if result.en_clasificacion
                else None,
                "modelo_usado": False,
                "modelo_version": "procedimiento_almacenado_v2",
            }
        except Exception as exc:
            self.db.rollback()
            raise exc

    def agregar_alergia(
        self, nin_id: int, ta_codigo: str, severidad: str = "LEVE"
    ) -> dict[str, Any]:
        """Agregar alergia a un niño usando sp_ninos_agregar_alergia"""
        try:
            result = self.db.execute(
                text("CALL sp_ninos_agregar_alergia(:nin_id, :ta_codigo, :severidad)"),
                {"nin_id": nin_id, "ta_codigo": ta_codigo, "severidad": severidad},
            ).fetchall()

            self.db.commit()

            return [
                {
                    "na_id": row.na_id,
                    "nin_id": row.nin_id,
                    "ta_codigo": row.ta_codigo,
                    "ta_nombre": row.ta_nombre,
                    "ta_categoria": row.ta_categoria,
                    "na_severidad": row.na_severidad,
                    "creado_en": row.creado_en.isoformat() if row.creado_en else None,
                }
                for row in result
            ]

        except Exception as e:
            self.db.rollback()
            raise e

    def obtener_alergias(self, nin_id: int) -> list[dict[str, Any]]:
        """Obtener alergias de un niño usando sp_ninos_obtener_alergias"""
        try:
            results = self.db.execute(
                text("CALL sp_ninos_obtener_alergias(:nin_id)"), {"nin_id": nin_id}
            ).fetchall()

            return [
                {
                    "na_id": row.na_id,
                    "nin_id": row.nin_id,
                    "ta_codigo": row.ta_codigo,
                    "ta_nombre": row.ta_nombre,
                    "ta_categoria": row.ta_categoria,
                    "na_severidad": row.na_severidad,
                    "creado_en": row.creado_en.isoformat() if row.creado_en else None,
                }
                for row in results
            ]

        except Exception as e:
            raise e

    def crear_tipo_alergia(
        self, ta_codigo: str, ta_nombre: str, ta_categoria: str
    ) -> dict[str, Any]:
        """Crear nuevo tipo de alergia"""
        try:
            result = self.db.execute(
                text("CALL sp_tipos_alergias_crear(:ta_codigo, :ta_nombre, :ta_categoria)"),
                {
                    "ta_codigo": ta_codigo,
                    "ta_nombre": ta_nombre,
                    "ta_categoria": ta_categoria,
                },
            ).fetchone()

            self.db.commit()

            if not result:
                return None

            return {
                "ta_id": result.ta_id,
                "ta_codigo": result.ta_codigo,
                "ta_nombre": result.ta_nombre,
                "ta_categoria": result.ta_categoria,
                "ta_activo": bool(result.ta_activo),
                "creado_en": result.creado_en.isoformat() if result.creado_en else None,
            }

        except Exception as e:
            self.db.rollback()
            raise e

    def obtener_tipos_alergias(self, q: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        """Obtener tipos de alergias usando sp_tipos_alergias_buscar"""
        try:
            results = self.db.execute(
                text("CALL sp_tipos_alergias_buscar(:query, :limit)"), {"query": q, "limit": limit}
            ).fetchall()

            return [
                {
                    "ta_id": row.ta_id,
                    "ta_codigo": row.ta_codigo,
                    "ta_nombre": row.ta_nombre,
                    "ta_categoria": row.ta_categoria,
                    "ta_activo": bool(row.ta_activo),
                    "creado_en": row.creado_en.isoformat() if row.creado_en else None,
                }
                for row in results
            ]
        except Exception as e:
            raise e

    def get_perfil_completo(self, nin_id: int) -> dict[str, Any]:
        """Obtener perfil completo con última antropometría usando procedimiento almacenado"""
        result_sets = self.db.execute(
            text("CALL sp_ninos_perfil_completo(:nin_id)"),
            {"nin_id": nin_id},
        )

        try:
            nino_row = result_sets.fetchone()
            if not nino_row:
                return None

            perfil = {
                "nino": {
                    "nin_id": nino_row.nin_id,
                    "usr_id_tutor": getattr(nino_row, "usr_id_tutor", None),
                    "ent_id": getattr(nino_row, "ent_id", None),
                    "nin_nombres": getattr(nino_row, "nin_nombres", None),
                    "nin_fecha_nac": getattr(nino_row, "nin_fecha_nac", None),
                    "nin_sexo": getattr(nino_row, "nin_sexo", None),
                    "nin_alergias": getattr(nino_row, "nin_alergias", None),
                    "edad_meses": getattr(nino_row, "edad_meses", None),
                    "creado_en": nino_row.creado_en.isoformat()
                    if getattr(nino_row, "creado_en", None)
                    else None,
                    "actualizado_en": nino_row.actualizado_en.isoformat()
                    if getattr(nino_row, "actualizado_en", None)
                    else None,
                },
                "ultima_antropometria": None,
            }

            if result_sets.nextset():
                antropometria_row = result_sets.fetchone()
                if antropometria_row:
                    perfil["ultima_antropometria"] = self._map_antropometria_row(antropometria_row)

            return perfil
        finally:
            result_sets.close()

    def get_perfil_completo_con_datos(self, nin_id: int) -> dict[str, Any] | None:
        """
        Obtiene el perfil completo de un niño con antropometrías, alergias y estado nutricional.
        Usa SOLO procedimientos almacenados.
        """
        nino_data = self.obtener_nino(nin_id)
        if not nino_data:
            return None

        antropometrias = self.get_antropometrias_by_nino(nin_id, limit=10)

        alergias = self.obtener_alergias(nin_id)

        estado = self.evaluar_estado_nutricional(nin_id)
        ultimo_estado = None
        if estado:
            clasificacion = estado.get("en_clasificacion", "")
            imc = estado.get("imc_calculado", 0)
            edad_meses = nino_data.get("edad_meses", 0)

            ultimo_estado = {
                "imc": imc,
                "z_score_imc": estado.get("en_z_score_imc"),
                "classification": clasificacion,
                "percentile": estado.get("percentil_calculado"),
                "risk_level": estado.get("en_nivel_riesgo"),
                "recommendations": estado.get("recomendaciones")
                or generar_recomendaciones_nutricionales(clasificacion, imc, edad_meses),
            }

        return {
            "nino": nino_data,
            "antropometrias": antropometrias,
            "alergias": alergias,
            "ultimo_estado_nutricional": ultimo_estado,
        }

    def get_ninos_completos_by_tutor(self, usr_id_tutor: int) -> list[dict[str, Any]]:
        """
        Obtiene todos los niños de un tutor con perfiles completos.
        Usa SOLO procedimientos almacenados.
        """
        ninos = self.get_ninos_by_tutor(usr_id_tutor)

        result = []
        for nino_data in ninos:
            nin_id = nino_data["nin_id"]

            antropometrias = self.get_antropometrias_by_nino(nin_id, limit=10)

            alergias = self.obtener_alergias(nin_id)

            ultimo_estado = None
            if antropometrias:
                try:
                    estado = self.evaluar_estado_nutricional(nin_id)
                    if estado:
                        clasificacion = estado.get("en_clasificacion", "")
                        imc = estado.get("imc_calculado", 0)
                        edad_meses = nino_data.get("edad_meses", 0)

                        ultimo_estado = {
                            "imc": imc,
                            "z_score_imc": estado.get("en_z_score_imc"),
                            "classification": clasificacion,
                            "percentile": estado.get("percentil_calculado"),
                            "risk_level": estado.get("en_nivel_riesgo"),
                            "recommendations": estado.get("recomendaciones")
                            or generar_recomendaciones_nutricionales(
                                clasificacion, imc, edad_meses
                            ),
                        }
                except:
                    pass

            result.append(
                {
                    "nino": nino_data,
                    "antropometrias": antropometrias,
                    "alergias": alergias,
                    "ultimo_estado_nutricional": ultimo_estado,
                }
            )

        return result

    def listar_ninos_tutor(self, usr_id: int) -> list[dict[str, Any]]:
        return self.get_ninos_by_tutor(usr_id)

    def asignar_tutor(self, nin_id: int, usr_id: int) -> dict[str, Any] | None:
        return self.assign_child_to_tutor(nin_id, usr_id)
