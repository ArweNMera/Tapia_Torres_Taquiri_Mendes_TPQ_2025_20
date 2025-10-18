"""
Repositorio para gestión de planes de comidas
"""

from datetime import date
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class PlanesComidasRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_perfil_nutricional(self, nin_id: int) -> Optional[Dict]:
        """Obtiene el perfil nutricional vigente del niño"""
        query = text("""
            SELECT * FROM perfil_nutricional_nino
            WHERE nin_id = :nin_id AND pnn_vigente = TRUE
            LIMIT 1
        """)
        result = self.db.execute(query, {"nin_id": nin_id})
        row = result.first()
        return dict(row._mapping) if row else None

    def calcular_perfil_nutricional(self, nin_id: int) -> Dict:
        """Calcula y guarda el perfil nutricional del niño usando procedimiento almacenado"""
        import logging

        logger = logging.getLogger(__name__)

        try:
            logger.info(f"🔍 Llamando a sp_calcular_perfil_nutricional para niño {nin_id}")
            query = text("CALL sp_calcular_perfil_nutricional(:nin_id)")
            result = self.db.execute(query, {"nin_id": nin_id})
            self.db.commit()
            row = result.first()

            if row:
                data = dict(row._mapping)
                logger.info(f"✅ Perfil calculado: {data}")
                return data
            else:
                logger.warning("⚠️ SP no retornó datos")
                return {}
        except Exception as e:
            logger.error(f"❌ Error en calcular_perfil_nutricional: {str(e)}", exc_info=True)
            self.db.rollback()
            raise

    def obtener_recetas_candidatas(
        self, nin_id: int, tipo_comida: str, ent_id: int, periodo: str
    ) -> List[Dict]:
        """Obtiene recetas candidatas filtradas"""
        query = text("""
            CALL sp_recetas_candidatas(:nin_id, :tipo_comida, :ent_id, :periodo)
        """)
        result = self.db.execute(
            query,
            {"nin_id": nin_id, "tipo_comida": tipo_comida, "ent_id": ent_id, "periodo": periodo},
        )
        return [dict(row._mapping) for row in result]

    def crear_menu(
        self, nin_id: int, fecha_inicio: date, fecha_fin: date, generado_por: str = "IA"
    ) -> int:
        """Crea un nuevo menú"""
        query = text("""
            INSERT INTO menus (nin_id, men_generado_por, men_inicio, men_fin, men_estado)
            VALUES (:nin_id, :generado_por, :inicio, :fin, 'BORRADOR')
        """)
        result = self.db.execute(
            query,
            {
                "nin_id": nin_id,
                "generado_por": generado_por,
                "inicio": fecha_inicio,
                "fin": fecha_fin,
            },
        )
        self.db.commit()
        return result.lastrowid

    def agregar_item_menu(
        self, men_id: int, dia_idx: int, tipo_comida: str, rec_id: int, kcal: int
    ) -> int:
        """Agrega un item al menú"""
        query = text("""
            INSERT INTO menus_items (men_id, mei_dia_idx, mei_comida, rec_id, mei_kcal)
            VALUES (:men_id, :dia_idx, :comida, :rec_id, :kcal)
        """)
        result = self.db.execute(
            query,
            {
                "men_id": men_id,
                "dia_idx": dia_idx,
                "comida": tipo_comida,
                "rec_id": rec_id,
                "kcal": kcal,
            },
        )
        self.db.commit()
        return result.lastrowid

    def actualizar_calorias_menu(self, men_id: int, kcal_total: int):
        """Actualiza las calorías totales del menú"""
        query = text("""
            UPDATE menus SET men_kcal_total = :kcal WHERE men_id = :men_id
        """)
        self.db.execute(query, {"men_id": men_id, "kcal": kcal_total})
        self.db.commit()

    def obtener_datos_nino(self, nin_id: int) -> Optional[Dict]:
        """Obtiene datos básicos del niño"""
        query = text("""
            SELECT
                n.nin_id,
                n.nin_nombres,
                n.nin_fecha_nac,
                n.nin_sexo,
                n.ent_id,
                TIMESTAMPDIFF(MONTH, n.nin_fecha_nac, CURDATE()) AS edad_meses,
                e.ent_nombre,
                e.ent_distrito
            FROM ninos n
            LEFT JOIN entidades e ON e.ent_id = n.ent_id
            WHERE n.nin_id = :nin_id
        """)
        result = self.db.execute(query, {"nin_id": nin_id})
        row = result.first()
        return dict(row._mapping) if row else None

    def obtener_ingredientes_receta(self, rec_id: int) -> List[Dict]:
        """Obtiene los ingredientes de una receta"""
        query = text("""
            SELECT
                a.ali_nombre,
                ri.ri_cantidad AS cantidad,
                ri.ri_unidad AS unidad
            FROM recetas_ingredientes ri
            INNER JOIN alimentos a ON a.ali_id = ri.ali_id
            WHERE ri.rec_id = :rec_id
        """)
        result = self.db.execute(query, {"rec_id": rec_id})
        return [dict(row._mapping) for row in result]

    def listar_menus_nino(
        self, nin_id: int, estado: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """Lista los menús de un niño"""
        if estado:
            query = text("""
                SELECT * FROM menus
                WHERE nin_id = :nin_id AND men_estado = :estado
                ORDER BY men_inicio DESC
                LIMIT :limit
            """)
            params = {"nin_id": nin_id, "estado": estado, "limit": limit}
        else:
            query = text("""
                SELECT * FROM menus
                WHERE nin_id = :nin_id
                ORDER BY men_inicio DESC
                LIMIT :limit
            """)
            params = {"nin_id": nin_id, "limit": limit}

        result = self.db.execute(query, params)
        return [dict(row._mapping) for row in result]

    def obtener_detalle_menu(self, men_id: int) -> Optional[Dict]:
        """Obtiene el detalle completo de un menú"""
        query = text("""
            SELECT
                m.*,
                n.nin_nombres
            FROM menus m
            INNER JOIN ninos n ON n.nin_id = m.nin_id
            WHERE m.men_id = :men_id
        """)
        result = self.db.execute(query, {"men_id": men_id})
        row = result.first()
        return dict(row._mapping) if row else None

    def obtener_items_menu(self, men_id: int) -> List[Dict]:
        """Obtiene los items de un menú"""
        query = text("""
            SELECT
                mi.*,
                r.rec_nombre,
                r.rec_instrucciones
            FROM menus_items mi
            INNER JOIN recetas r ON r.rec_id = mi.rec_id
            WHERE mi.men_id = :men_id
            ORDER BY mi.mei_dia_idx,
                FIELD(mi.mei_comida, 'DESAYUNO', 'ALMUERZO', 'CENA', 'REFACCION')
        """)
        result = self.db.execute(query, {"men_id": men_id})
        return [dict(row._mapping) for row in result]

    def actualizar_estado_menu(self, men_id: int, estado: str):
        """Actualiza el estado de un menú"""
        query = text("""
            UPDATE menus SET men_estado = :estado WHERE men_id = :men_id
        """)
        self.db.execute(query, {"men_id": men_id, "estado": estado})
        self.db.commit()

    async def generar_plan_con_llm(
        self,
        nin_id: int,
        perfil: Dict,
        nino: Dict,
        preferencias: Dict,
        alergias: List[str],
        fecha_inicio: date,
        incluir_refacciones: bool = False,
        preferencias_adicionales: Optional[str] = None,
    ) -> Dict:
        """
        Genera un plan de comidas semanal completo usando LLM
        """
        import logging
        from datetime import timedelta

        logger = logging.getLogger(__name__)

        # 1. Obtener recetas disponibles
        recetas_disponibles = self._obtener_recetas_disponibles(nino.get("ent_id"))

        # 2. Llamar al servicio ML para generar el plan con LLM
        plan_llm = await self._llamar_llm_generar_plan(
            nin_id, perfil, nino, preferencias, alergias, recetas_disponibles, incluir_refacciones
        )

        # 4. Crear el menú en la base de datos
        fecha_fin = fecha_inicio + timedelta(days=6)
        men_id = self.crear_menu(nin_id, fecha_inicio, fecha_fin, "IA")

        # 5. Guardar los items del menú
        total_calorias = 0
        dias_plan = []

        for dia_idx, dia_data in enumerate(plan_llm.get("dias", [])):
            dia_info = {
                "dia_idx": dia_idx,
                "dia_nombre": self._get_nombre_dia(dia_idx),
                "fecha": fecha_inicio + timedelta(days=dia_idx),
                "total_dia": 0,
            }

            # Procesar cada tipo de comida
            for comida_tipo in ["desayuno", "almuerzo", "cena"]:
                if comida_tipo in dia_data:
                    comida_data = dia_data[comida_tipo]
                    rec_id = comida_data.get("rec_id")
                    kcal = comida_data.get("kcal", 0)

                    if rec_id:
                        # Guardar en BD
                        mei_id = self.agregar_item_menu(
                            men_id, dia_idx, comida_tipo.upper(), rec_id, kcal
                        )

                        # Obtener detalles de la receta
                        receta = self._obtener_detalle_receta(rec_id)

                        # Agregar al plan
                        dia_info[comida_tipo] = {
                            "mei_id": mei_id,
                            "rec_id": rec_id,
                            "rec_nombre": comida_data.get(
                                "rec_nombre", receta.get("rec_nombre", "")
                            ),
                            "rec_instrucciones": receta.get("rec_instrucciones", ""),
                            "mei_kcal": kcal,
                            "ingredientes": receta.get("ingredientes", []),
                            "match_preferencias": [],
                        }
                        dia_info["total_dia"] += kcal
                        total_calorias += kcal

            dias_plan.append(dia_info)

        # 6. Actualizar calorías totales del menú
        self.actualizar_calorias_menu(men_id, total_calorias)

        # 7. Retornar el plan completo
        return {
            "men_id": men_id,
            "nin_id": nin_id,
            "men_inicio": fecha_inicio.isoformat(),
            "men_fin": fecha_fin.isoformat(),
            "men_kcal_total": total_calorias,
            "men_estado": "BORRADOR",
            "dias": dias_plan,
            "resumen": {
                "calorias_promedio_dia": total_calorias // 7 if total_calorias > 0 else 0,
                "preferencias_respetadas": plan_llm.get("preferencias_respetadas", 0),
                "preferencias_totales": plan_llm.get("preferencias_totales", 0),
                "porcentaje_match": plan_llm.get("porcentaje_match", 0.0),
            },
        }

    def _obtener_recetas_disponibles(self, ent_id: Optional[int]) -> List[Dict]:
        """Obtiene recetas disponibles con sus tipos de comida"""
        query = text("""
            SELECT
                r.rec_id,
                r.rec_nombre,
                r.rec_instrucciones,
                GROUP_CONCAT(DISTINCT rc.rc_comida) as tipos_comida,
                COALESCE(SUM(an.an_cantidad_100 * ri.ri_cantidad / 100), 0) as calorias_aprox
            FROM recetas r
            LEFT JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
            LEFT JOIN recetas_ingredientes ri ON ri.rec_id = r.rec_id
            LEFT JOIN alimentos_nutrientes an ON an.ali_id = ri.ali_id AND an.nutri_id = 1
            WHERE r.rec_activo = 1
            GROUP BY r.rec_id, r.rec_nombre, r.rec_instrucciones
            LIMIT 100
        """)
        result = self.db.execute(query, {"ent_id": ent_id or 0})
        return [dict(row._mapping) for row in result]

    async def _llamar_llm_generar_plan(
        self,
        nin_id: int,
        perfil: Dict,
        nino: Dict,
        preferencias: Dict,
        alergias: List[str],
        recetas_disponibles: List[Dict],
        incluir_refacciones: bool,
    ) -> Dict:
        """Llama al servicio ML para generar el plan con LLM"""
        import logging
        import os

        import httpx

        logger = logging.getLogger(__name__)

        # Obtener URL del servicio ML
        ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8001")
        ml_service_url = ml_service_url.rstrip("/")
        endpoint = f"{ml_service_url}/ml/generar_plan_semanal"

        try:
            logger.info(f"Llamando al servicio ML: {endpoint}")

            # Preparar payload (convertir Decimals y datetime a tipos serializables)
            from datetime import date, datetime
            from decimal import Decimal

            def convert_to_serializable(obj):
                """Convierte Decimals y datetime a tipos serializables recursivamente"""
                if isinstance(obj, Decimal):
                    return float(obj)
                elif isinstance(obj, (datetime, date)):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_to_serializable(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_serializable(item) for item in obj]
                return obj

            payload = {
                "nin_id": nin_id,
                "perfil": convert_to_serializable(perfil),
                "nino": convert_to_serializable(nino),
                "preferencias": preferencias,
                "alergias": alergias,
                "recetas_disponibles": convert_to_serializable(recetas_disponibles),
                "incluir_refacciones": incluir_refacciones,
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    endpoint, json=payload, headers={"Content-Type": "application/json"}
                )

                if response.status_code != 200:
                    logger.error(f"Error del servicio ML: {response.status_code} - {response.text}")
                    raise Exception(f"Error del servicio ML: {response.status_code}")

                data = response.json()
                logger.info(
                    f"✅ Plan generado exitosamente con servicio ML (LLM usado: {data.get('used_llm', False)})"
                )

                return {
                    "dias": data.get("dias", []),
                    "preferencias_respetadas": data.get("preferencias_respetadas", 0),
                    "preferencias_totales": data.get("preferencias_totales", 0),
                    "porcentaje_match": data.get("porcentaje_match", 0.0),
                    "used_llm": data.get("used_llm", False),
                }

        except Exception as e:
            logger.error(f"Error llamando al servicio ML: {str(e)}", exc_info=True)
            logger.warning("Usando plan fallback sin LLM")
            return self._generar_plan_fallback()

    def _generar_plan_fallback(self) -> Dict:
        """Genera un plan básico cuando el LLM no está disponible"""
        import logging

        logger = logging.getLogger(__name__)
        logger.warning("Generando plan fallback sin LLM")

        # Obtener recetas simples
        query = text("""
            SELECT r.rec_id, r.rec_nombre, rc.rc_comida
            FROM recetas r
            INNER JOIN recetas_comidas rc ON rc.rec_id = r.rec_id
            WHERE r.rec_activo = 1
            ORDER BY RAND()
            LIMIT 21
        """)
        result = self.db.execute(query)
        recetas = [dict(row._mapping) for row in result]

        dias = []
        idx = 0
        for dia in range(7):
            dia_plan = {}
            for tipo in ["DESAYUNO", "ALMUERZO", "CENA"]:
                if idx < len(recetas):
                    rec = recetas[idx]
                    dia_plan[tipo.lower()] = {
                        "rec_id": rec["rec_id"],
                        "rec_nombre": rec["rec_nombre"],
                        "kcal": 500 if tipo == "DESAYUNO" else (800 if tipo == "ALMUERZO" else 600),
                    }
                    idx += 1
            dias.append(dia_plan)

        return {
            "dias": dias,
            "preferencias_respetadas": 0,
            "preferencias_totales": 0,
            "porcentaje_match": 0.0,
        }

    def _get_nombre_dia(self, dia_idx: int) -> str:
        """Retorna el nombre del día de la semana"""
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        return dias[dia_idx] if 0 <= dia_idx < 7 else f"Día {dia_idx + 1}"

    def _obtener_detalle_receta(self, rec_id: int) -> Dict:
        """Obtiene los detalles de una receta incluyendo ingredientes"""
        query = text("""
            SELECT
                r.rec_id,
                r.rec_nombre,
                r.rec_instrucciones
            FROM recetas r
            WHERE r.rec_id = :rec_id
        """)
        result = self.db.execute(query, {"rec_id": rec_id})
        row = result.first()

        if not row:
            return {
                "rec_nombre": "Receta no encontrada",
                "rec_instrucciones": "",
                "ingredientes": [],
            }

        # Obtener ingredientes
        ingredientes = self.obtener_ingredientes_receta(rec_id)

        return {
            "rec_nombre": row.rec_nombre,
            "rec_instrucciones": row.rec_instrucciones or "",
            "ingredientes": ingredientes,
        }
