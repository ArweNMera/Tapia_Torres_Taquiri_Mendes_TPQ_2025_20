from sqlalchemy import text
from sqlalchemy.orm import Session
from app.schemas.ninos import NinoCreate, NinoUpdate, AnthropometryCreate, AnthropometryUpdate
from datetime import date, datetime
from typing import Optional, List, Dict, Any

class NinosRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_nino(self, nino_data: NinoCreate, usr_id_tutor: int) -> Dict[str, Any]:
        """Crear un nuevo perfil de niño usando procedimiento almacenado"""
        try:
            # Calcular edad para determinar autogestión
            from datetime import date
            today = date.today()
            age_years = today.year - nino_data.nin_fecha_nac.year - (
                (today.month, today.day) < (nino_data.nin_fecha_nac.month, nino_data.nin_fecha_nac.day)
            )
            
            # Usar sp_ninos_crear sin alergias
            if age_years >= 13:
                # Autogestión - el tutor es el propietario
                result = self.db.execute(text("CALL sp_ninos_crear(:nin_nombres, :fecha_nac, :sexo, :ent_id, NULL, :usr_id_propietario)"), {
                    "nin_nombres": nino_data.nin_nombres,
                    "fecha_nac": nino_data.nin_fecha_nac,
                    "sexo": nino_data.nin_sexo.value,
                    "ent_id": nino_data.ent_id,
                    "usr_id_propietario": usr_id_tutor
                }).fetchone()
            else:
                # Menor con tutor
                result = self.db.execute(text("CALL sp_ninos_crear(:nin_nombres, :fecha_nac, :sexo, :ent_id, :usr_id_tutor, NULL)"), {
                    "nin_nombres": nino_data.nin_nombres,
                    "fecha_nac": nino_data.nin_fecha_nac,
                    "sexo": nino_data.nin_sexo.value,
                    "ent_id": nino_data.ent_id,
                    "usr_id_tutor": usr_id_tutor
                }).fetchone()
            
            self.db.commit()
            
            if result:
                # Obtener datos completos del niño creado
                nino_completo = self.get_nino_by_id(result.nin_id)
                return nino_completo
            return None
            
        except Exception as e:
            self.db.rollback()
            raise e

    def get_nino_by_id(self, nin_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un niño por su ID (considerando tutor o propietario)."""
        try:
            query = text(
                """
                SELECT 
                  n.nin_id,
                  n.usr_id_tutor,
                  n.usr_id_propietario,
                  n.ent_id,
                  COALESCE(n.nin_nombres, CONCAT('Niño ', n.nin_id)) AS nin_nombres,
                  n.nin_fecha_nac,
                  n.nin_sexo,
                  TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE()) AS edad_meses,
                  n.creado_en,
                  n.actualizado_en,
                  e.ent_nombre,
                  e.ent_codigo,
                  e.ent_direccion,
                  e.ent_departamento,
                  e.ent_provincia,
                  e.ent_distrito
                FROM ninos n
                LEFT JOIN entidades e ON e.ent_id = n.ent_id
                WHERE n.nin_id = :nin_id
                LIMIT 1
                """
            )
            result = self.db.execute(query, {"nin_id": nin_id}).fetchone()
            if result:
                return {
                    "nin_id": result.nin_id,
                    "usr_id_tutor": result.usr_id_tutor,
                    "usr_id_propietario": result.usr_id_propietario,
                    "ent_id": result.ent_id,
                    "nin_nombres": result.nin_nombres,
                    "nin_fecha_nac": result.nin_fecha_nac.isoformat() if result.nin_fecha_nac else None,
                    "nin_sexo": result.nin_sexo,
                    "edad_meses": result.edad_meses,
                    "creado_en": result.creado_en.isoformat() if result.creado_en else None,
                    "actualizado_en": result.actualizado_en.isoformat() if result.actualizado_en else None,
                    "ent_nombre": result.ent_nombre,
                    "ent_codigo": result.ent_codigo,
                    "ent_direccion": result.ent_direccion,
                    "ent_departamento": result.ent_departamento,
                    "ent_provincia": result.ent_provincia,
                    "ent_distrito": result.ent_distrito,
                }
            return None
        except Exception as e:
            raise e

    def get_nino_by_owner(self, usr_id_propietario: int) -> Optional[Dict[str, Any]]:
        """Obtener un niño asociado como propietario (autogestión)"""
        try:
            # Buscar el nin_id por propietario
            row = self.db.execute(text("SELECT nin_id FROM ninos WHERE usr_id_propietario = :uid LIMIT 1"), {
                "uid": usr_id_propietario
            }).fetchone()
            if not row:
                return None
            return self.get_nino_by_id(row.nin_id)
        except Exception as e:
            raise e

    def get_ninos_by_tutor(self, usr_id_tutor: int) -> List[Dict[str, Any]]:
        """Obtener todos los niños asociados al usuario como tutor o propietario."""
        query = text(
            """
            SELECT
              n.nin_id,
              n.usr_id_tutor,
              n.usr_id_propietario,
              n.ent_id,
              COALESCE(n.nin_nombres, CONCAT('Niño ', n.nin_id)) AS nin_nombres,
              n.nin_fecha_nac,
              n.nin_sexo,
              TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE()) AS edad_meses,
              n.creado_en,
              n.actualizado_en,
              e.ent_nombre,
              e.ent_codigo,
              e.ent_direccion,
              e.ent_departamento,
              e.ent_provincia,
              e.ent_distrito
            FROM ninos n
            LEFT JOIN entidades e ON e.ent_id = n.ent_id
            WHERE (n.usr_id_tutor = :usr_id OR n.usr_id_propietario = :usr_id)
            ORDER BY n.creado_en DESC
            """
        )

        results = self.db.execute(query, {"usr_id": usr_id_tutor}).fetchall()

        return [{
            "nin_id": row.nin_id,
            "usr_id_tutor": row.usr_id_tutor,
            "usr_id_propietario": row.usr_id_propietario,
            "ent_id": row.ent_id,
            "nin_nombres": row.nin_nombres,
            "nin_fecha_nac": row.nin_fecha_nac.isoformat() if row.nin_fecha_nac else None,
            "nin_sexo": row.nin_sexo,
            "edad_meses": row.edad_meses,
            "creado_en": row.creado_en.isoformat() if row.creado_en else None,
            "actualizado_en": row.actualizado_en.isoformat() if row.actualizado_en else None,
            "ent_nombre": row.ent_nombre,
            "ent_codigo": row.ent_codigo,
            "ent_direccion": row.ent_direccion,
            "ent_departamento": row.ent_departamento,
            "ent_provincia": row.ent_provincia,
            "ent_distrito": row.ent_distrito,
        } for row in results]

    def update_nino(self, nin_id: int, nino_data: NinoUpdate) -> Optional[Dict[str, Any]]:
        """Actualizar datos de un niño usando procedimiento almacenado"""
        try:
            self.db.execute(text("CALL sp_ninos_actualizar(:nin_id, :nin_nombres, :ent_id, :nin_fecha_nac)"), {
                "nin_id": nin_id,
                "nin_nombres": nino_data.nin_nombres,
                "ent_id": nino_data.ent_id,
                "nin_fecha_nac": nino_data.nin_fecha_nac
            }).fetchone()
            
            self.db.commit()
            
            return self.get_nino_by_id(nin_id)
            
        except Exception as e:
            self.db.rollback()
            raise e

    def promote_child_to_owner(self, nin_id: int, usr_id_propietario: int) -> Optional[Dict[str, Any]]:
        """Promover un niño existente (donde el usuario es tutor) a propietario.
        Útil para reconciliar el perfil personal (self child).
        """
        try:
            query = text("""
                UPDATE ninos
                SET usr_id_propietario = :owner
                WHERE nin_id = :nin_id AND (usr_id_propietario IS NULL OR usr_id_propietario = :owner)
            """)
            self.db.execute(query, {"owner": usr_id_propietario, "nin_id": nin_id})
            self.db.commit()
            return self.get_nino_by_id(nin_id)
        except Exception as e:
            self.db.rollback()
            raise e

    def assign_child_to_tutor(self, nin_id: int, usr_id_tutor: int) -> Optional[Dict[str, Any]]:
        """Asociar un niño existente a un tutor/padre usando SP dedicado."""
        try:
            self.db.execute(text("CALL sp_ninos_asignar_tutor(:nin_id, :usr_id_tutor)"), {
                "nin_id": nin_id,
                "usr_id_tutor": usr_id_tutor
            }).fetchall()
            self.db.commit()
            return self.get_nino_by_id(nin_id)
        except Exception as e:
            self.db.rollback()
            raise e

    def create_antropometria(self, nin_id: int, antropo_data: AnthropometryCreate) -> Dict[str, Any]:
        """Agregar datos antropométricos usando procedimiento almacenado"""
        try:
            fecha = antropo_data.ant_fecha or date.today()
            
            result = self.db.execute(text("CALL sp_antropometria_agregar(:nin_id, :fecha, :peso_kg, :talla_cm)"), {
                "nin_id": nin_id,
                "fecha": fecha,
                "peso_kg": antropo_data.ant_peso_kg,
                "talla_cm": antropo_data.ant_talla_cm
            }).fetchone()
            
            self.db.commit()
            
            if result:
                return {
                    "ant_id": result.ant_id,
                    "nin_id": result.nin_id,
                    "ant_fecha": result.ant_fecha,
                    "ant_edad_meses": result.ant_edad_meses,
                    "ant_peso_kg": float(result.ant_peso_kg),
                    "ant_talla_cm": float(result.ant_talla_cm),
                    "ant_z_imc": float(result.ant_z_imc) if result.ant_z_imc else None,
                    "ant_z_peso_edad": float(result.ant_z_peso_edad) if result.ant_z_peso_edad else None,
                    "ant_z_talla_edad": float(result.ant_z_talla_edad) if result.ant_z_talla_edad else None,
                    "imc": float(result.imc) if result.imc else None,
                    "creado_en": result.creado_en.isoformat() if result.creado_en else None
                }
            return None
            
        except Exception as e:
            self.db.rollback()
            raise e

    def get_antropometria_by_nino_fecha(self, nin_id: int, fecha: date) -> Optional[Dict[str, Any]]:
        """Obtener antropometría específica por niño y fecha"""
        query = text("""
            SELECT ant_id, nin_id, ant_fecha, ant_peso_kg, ant_talla_cm, 
                   ant_z_imc, ant_z_peso_edad, ant_z_talla_edad, creado_en,
                   ROUND(ant_peso_kg / POWER(ant_talla_cm / 100, 2), 2) as imc
            FROM antropometrias 
            WHERE nin_id = :nin_id AND ant_fecha = :fecha
        """)
        
        result = self.db.execute(query, {"nin_id": nin_id, "fecha": fecha}).fetchone()
        
        if result:
            return {
                "ant_id": result.ant_id,
                "nin_id": result.nin_id,
                "ant_fecha": result.ant_fecha,
                "ant_peso_kg": float(result.ant_peso_kg),
                "ant_talla_cm": float(result.ant_talla_cm),
                "ant_z_imc": float(result.ant_z_imc) if result.ant_z_imc else None,
                "ant_z_peso_edad": float(result.ant_z_peso_edad) if result.ant_z_peso_edad else None,
                "ant_z_talla_edad": float(result.ant_z_talla_edad) if result.ant_z_talla_edad else None,
                "imc": float(result.imc) if result.imc else None,
                "creado_en": result.creado_en.isoformat() if result.creado_en else None
            }
        return None

    def get_antropometrias_by_nino(self, nin_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener todas las antropometrías de un niño usando procedimiento almacenado"""
        results = self.db.execute(text("CALL sp_antropometria_obtener_por_nino(:nin_id, :limit)"), {
            "nin_id": nin_id,
            "limit": limit
        }).fetchall()
        
        return [{
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
                if (getattr(row, "imc", None) is not None or getattr(row, "imc_calculado", None) is not None)
                else None
            ),
            "creado_en": row.creado_en.isoformat() if row.creado_en else None
        } for row in results]

    def get_latest_antropometria(self, nin_id: int) -> Optional[Dict[str, Any]]:
        """Obtener la antropometría más reciente usando procedimiento almacenado"""
        result = self.db.execute(text("CALL sp_antropometria_obtener_ultima(:nin_id)"), {
            "nin_id": nin_id
        }).fetchone()
        
        if result:
            return {
                "ant_id": result.ant_id,
                "nin_id": result.nin_id,
                "ant_fecha": result.ant_fecha,
                "ant_peso_kg": float(result.ant_peso_kg),
                "ant_talla_cm": float(result.ant_talla_cm),
                "ant_z_imc": float(result.ant_z_imc) if result.ant_z_imc else None,
                "ant_z_peso_edad": float(result.ant_z_peso_edad) if result.ant_z_peso_edad else None,
                "ant_z_talla_edad": float(result.ant_z_talla_edad) if result.ant_z_talla_edad else None,
                "imc": (
                    float(getattr(result, "imc", None) or getattr(result, "imc_calculado", None))
                    if (getattr(result, "imc", None) is not None or getattr(result, "imc_calculado", None) is not None)
                    else None
                ),
                "creado_en": result.creado_en.isoformat() if result.creado_en else None
            }
        return None

    def delete_nino(self, nin_id: int) -> bool:
        """Eliminar un niño (por ahora hard delete)"""
        try:
            query = text("DELETE FROM ninos WHERE nin_id = :nin_id")
            result = self.db.execute(query, {"nin_id": nin_id})
            self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise e

    def evaluar_estado_nutricional(self, nin_id: int) -> Dict[str, Any]:
        """Evaluar estado nutricional usando WHO standards con sp_evaluar_estado_nutricional"""
        try:
            result = self.db.execute(text("CALL sp_evaluar_estado_nutricional(:nin_id)"), {
                "nin_id": nin_id
            }).fetchone()
            
            if result:
                return {
                    "en_id": result.en_id,
                    "nin_id": result.nin_id,
                    "ant_id": result.ant_id,
                    "en_edad_meses": result.en_edad_meses,
                    "imc_calculado": float(result.imc_calculado),
                    "en_z_score_imc": float(result.en_z_score_imc),
                    "percentil_calculado": float(result.percentil_calculado) if result.percentil_calculado else None,
                    "en_clasificacion": result.en_clasificacion,
                    "en_nivel_riesgo": result.en_nivel_riesgo,
                    "oms_usado": bool(result.oms_usado),
                    "evaluado_en": result.evaluado_en.isoformat() if result.evaluado_en else None
                }
            return None
            
        except Exception as e:
            raise e

    def agregar_alergia(self, nin_id: int, ta_codigo: str, severidad: str = "LEVE") -> Dict[str, Any]:
        """Agregar alergia a un niño usando sp_ninos_agregar_alergia"""
        try:
            result = self.db.execute(text("CALL sp_ninos_agregar_alergia(:nin_id, :ta_codigo, :severidad)"), {
                "nin_id": nin_id,
                "ta_codigo": ta_codigo,
                "severidad": severidad
            }).fetchall()  # Retorna lista de alergias
            
            self.db.commit()
            
            return [{
                "na_id": row.na_id,
                "nin_id": row.nin_id,
                "ta_codigo": row.ta_codigo,
                "ta_nombre": row.ta_nombre,
                "ta_categoria": row.ta_categoria,
                "na_severidad": row.na_severidad,
                "creado_en": row.creado_en.isoformat() if row.creado_en else None
            } for row in result]
            
        except Exception as e:
            self.db.rollback()
            raise e

    def obtener_alergias(self, nin_id: int) -> List[Dict[str, Any]]:
        """Obtener alergias de un niño usando sp_ninos_obtener_alergias"""
        try:
            results = self.db.execute(text("CALL sp_ninos_obtener_alergias(:nin_id)"), {
                "nin_id": nin_id
            }).fetchall()
            
            return [{
                "na_id": row.na_id,
                "nin_id": row.nin_id,
                "ta_codigo": row.ta_codigo,
                "ta_nombre": row.ta_nombre,
                "ta_categoria": row.ta_categoria,
                "na_severidad": row.na_severidad,
                "creado_en": row.creado_en.isoformat() if row.creado_en else None
            } for row in results]
            
        except Exception as e:
            raise e

    def crear_tipo_alergia(self, ta_codigo: str, ta_nombre: str, ta_categoria: str) -> Dict[str, Any]:
        """Crear nuevo tipo de alergia"""
        try:
            query = text("""
                INSERT INTO tipos_alergias (ta_codigo, ta_nombre, ta_categoria, ta_activo)
                VALUES (:ta_codigo, :ta_nombre, :ta_categoria, 1)
            """)
            
            result = self.db.execute(query, {
                "ta_codigo": ta_codigo,
                "ta_nombre": ta_nombre,
                "ta_categoria": ta_categoria
            })
            
            ta_id = result.lastrowid
            self.db.commit()
            
            # Retornar el tipo creado
            query_select = text("""
                SELECT ta_id, ta_codigo, ta_nombre, ta_categoria, ta_activo, creado_en
                FROM tipos_alergias 
                WHERE ta_id = :ta_id
            """)
            
            result = self.db.execute(query_select, {"ta_id": ta_id}).fetchone()
            
            return {
                "ta_id": result.ta_id,
                "ta_codigo": result.ta_codigo,
                "ta_nombre": result.ta_nombre,
                "ta_categoria": result.ta_categoria,
                "ta_activo": bool(result.ta_activo),
                "creado_en": result.creado_en.isoformat() if result.creado_en else None
            }
            
        except Exception as e:
            self.db.rollback()
            raise e

    def obtener_tipos_alergias(self, q: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener tipos de alergias con filtro opcional por nombre/código"""
        try:
            if q:
                query = text(
                    """
                    SELECT ta_id, ta_codigo, ta_nombre, ta_categoria, ta_activo, creado_en
                    FROM tipos_alergias 
                    WHERE ta_activo = 1
                      AND (ta_nombre LIKE :q OR ta_codigo LIKE :q)
                    ORDER BY ta_categoria, ta_nombre
                    LIMIT :limit
                    """
                )
                params = {"q": f"%{q}%", "limit": limit}
            else:
                query = text(
                    """
                    SELECT ta_id, ta_codigo, ta_nombre, ta_categoria, ta_activo, creado_en
                    FROM tipos_alergias 
                    WHERE ta_activo = 1
                    ORDER BY ta_categoria, ta_nombre
                    LIMIT :limit
                    """
                )
                params = {"limit": limit}

            results = self.db.execute(query, params).fetchall()
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

    def get_perfil_completo(self, nin_id: int) -> Dict[str, Any]:
        """Obtener perfil completo con última antropometría usando procedimiento almacenado"""
        try:
            # El procedimiento devuelve dos result sets
            result_sets = self.db.execute(text("CALL sp_ninos_perfil_completo(:nin_id)"), {
                "nin_id": nin_id
            })
            
            # Primer result set: datos del niño
            nino_data = result_sets.fetchone()
            
            # Segundo result set: última antropometría (necesitamos nextset())
            result_sets.nextset()
            antropometria_data = result_sets.fetchone()
            
            perfil = {
                "nino": {
                    "nin_id": nino_data.nin_id,
                    "usr_id_tutor": nino_data.usr_id_tutor,
                    "ent_id": nino_data.ent_id,
                    "nin_nombres": nino_data.nin_nombres,
                    "nin_fecha_nac": nino_data.nin_fecha_nac,
                    "nin_sexo": nino_data.nin_sexo,
                    "nin_alergias": nino_data.nin_alergias,
                    "edad_meses": nino_data.edad_meses,
                    "creado_en": nino_data.creado_en.isoformat() if nino_data.creado_en else None,
                    "actualizado_en": nino_data.actualizado_en.isoformat() if nino_data.actualizado_en else None
                },
                "ultima_antropometria": None
            }
            
            if antropometria_data:
                perfil["ultima_antropometria"] = {
                    "ant_id": antropometria_data.ant_id,
                    "nin_id": antropometria_data.nin_id,
                    "ant_fecha": antropometria_data.ant_fecha,
                    "ant_peso_kg": float(antropometria_data.ant_peso_kg),
                    "ant_talla_cm": float(antropometria_data.ant_talla_cm),
                    "ant_z_imc": float(antropometria_data.ant_z_imc) if antropometria_data.ant_z_imc else None,
                    "ant_z_peso_edad": float(antropometria_data.ant_z_peso_edad) if antropometria_data.ant_z_peso_edad else None,
                    "ant_z_talla_edad": float(antropometria_data.ant_z_talla_edad) if antropometria_data.ant_z_talla_edad else None,
                    "imc": float(antropometria_data.imc) if antropometria_data.imc else None,
                    "creado_en": antropometria_data.creado_en.isoformat() if antropometria_data.creado_en else None
                }
            
            return perfil
            
        except Exception as e:
            if "Niño no encontrado" in str(e):
                return None
            raise e
