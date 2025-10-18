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
        result = self.db.execute(
            text("CALL sp_perfil_nutricional_vigente(:nin_id)"), {"nin_id": nin_id}
        )
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
        result = self.db.execute(
            text("CALL sp_menus_crear(:nin_id, :generado_por, :inicio, :fin)"),
            {
                "nin_id": nin_id,
                "generado_por": generado_por,
                "inicio": fecha_inicio,
                "fin": fecha_fin,
            },
        )
        self.db.commit()
        row = result.fetchone()
        return int(row.men_id) if row and hasattr(row, "men_id") else 0

    def agregar_item_menu(
        self, men_id: int, dia_idx: int, tipo_comida: str, rec_id: int, kcal: int
    ) -> int:
        """Agrega un item al menú"""
        result = self.db.execute(
            text("CALL sp_menus_items_agregar(:men_id, :dia_idx, :comida, :rec_id, :kcal)"),
            {
                "men_id": men_id,
                "dia_idx": dia_idx,
                "comida": tipo_comida,
                "rec_id": rec_id,
                "kcal": kcal,
            },
        )
        self.db.commit()
        row = result.fetchone()
        return int(row.mei_id) if row and hasattr(row, "mei_id") else 0

    def actualizar_calorias_menu(self, men_id: int, kcal_total: int):
        """Actualiza las calorías totales del menú"""
        self.db.execute(
            text("CALL sp_menus_actualizar_kcal(:men_id, :kcal_total)"),
            {"men_id": men_id, "kcal_total": kcal_total},
        )
        self.db.commit()

    def obtener_datos_nino(self, nin_id: int) -> Optional[Dict]:
        """Obtiene datos básicos del niño"""
        result = self.db.execute(text("CALL sp_ninos_datos_basicos(:nin_id)"), {"nin_id": nin_id})
        row = result.first()
        return dict(row._mapping) if row else None

    def obtener_ingredientes_receta(self, rec_id: int) -> List[Dict]:
        """Obtiene los ingredientes de una receta"""
        result = self.db.execute(text("CALL sp_recetas_ingredientes(:rec_id)"), {"rec_id": rec_id})
        return [dict(row._mapping) for row in result]

    def listar_menus_nino(
        self, nin_id: int, estado: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """Lista los menús de un niño"""
        result = self.db.execute(
            text("CALL sp_menus_listar(:nin_id, :estado, :limit)"),
            {"nin_id": nin_id, "estado": estado, "limit": limit},
        )
        return [dict(row._mapping) for row in result]

    def obtener_detalle_menu(self, men_id: int) -> Optional[Dict]:
        """Obtiene el detalle completo de un menú"""
        result = self.db.execute(text("CALL sp_menus_detalle(:men_id)"), {"men_id": men_id})
        row = result.first()
        return dict(row._mapping) if row else None

    def obtener_items_menu(self, men_id: int) -> List[Dict]:
        """Obtiene los items de un menú"""
        result = self.db.execute(text("CALL sp_menus_items_listar(:men_id)"), {"men_id": men_id})
        return [dict(row._mapping) for row in result]

    def actualizar_estado_menu(self, men_id: int, estado: str):
        """Actualiza el estado de un menú"""
        self.db.execute(
            text("CALL sp_menus_cambiar_estado(:men_id, :estado)"),
            {"men_id": men_id, "estado": estado},
        )
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
        result = self.db.execute(
            text("CALL sp_recetas_disponibles(:ent_id, :limit)"),
            {"ent_id": ent_id or 0, "limit": 100},
        )
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
        result = self.db.execute(text("CALL sp_recetas_aleatorias(:limit)"), {"limit": 21})
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
        result = self.db.execute(text("CALL sp_recetas_detalle(:rec_id)"), {"rec_id": rec_id})
        row = result.first()

        if not row:
            return {
                "rec_nombre": "Receta no encontrada",
                "rec_instrucciones": "",
                "ingredientes": [],
            }

        # Obtener ingredientes
        ingredientes = self.obtener_ingredientes_receta(rec_id)
        nutrientes_row = self.db.execute(
            text("CALL sp_recetas_nutrientes(:rec_id)"), {"rec_id": rec_id}
        ).first()

        nutrientes = {}
        if nutrientes_row:
            mapping = nutrientes_row._mapping
            nutrientes = {k: float(mapping.get(k) or 0) for k in mapping.keys()}

        return {
            "rec_nombre": row.rec_nombre,
            "rec_instrucciones": row.rec_instrucciones or "",
            "rec_activo": bool(getattr(row, "rec_activo", 1)),
            "ingredientes": ingredientes,
            "nutrientes": nutrientes,
        }

    def listar_comidas_favoritas(self, nin_id: int) -> list[Dict]:
        """Retorna las comidas favoritas registradas para un niño."""
        result = self.db.execute(
            text("CALL sp_comidas_favoritas_listar(:nin_id)"), {"nin_id": nin_id}
        )
        return [dict(row._mapping) for row in result]

    def agregar_comida_favorita(self, nin_id: int, rec_id: int) -> None:
        """Agrega una comida favorita usando procedimiento almacenado."""
        try:
            self.db.execute(
                text("CALL sp_comidas_favoritas_agregar(:nin_id, :rec_id)"),
                {"nin_id": nin_id, "rec_id": rec_id},
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def eliminar_comida_favorita(self, ncf_id: int) -> bool:
        """Elimina una comida favorita."""
        result = self.db.execute(
            text("CALL sp_comidas_favoritas_eliminar(:ncf_id)"), {"ncf_id": ncf_id}
        )
        self.db.commit()
        row = result.fetchone()
        return bool(row and getattr(row, "affected_rows", 0))

    def buscar_recetas(self, query: str, tipo_comida: str | None, limit: int) -> list[Dict]:
        """Busca recetas disponibles usando stored procedure."""
        result = self.db.execute(
            text("CALL sp_recetas_buscar(:query, :tipo_comida, :limit)"),
            {"query": query, "tipo_comida": tipo_comida, "limit": limit},
        )
        return [dict(row._mapping) for row in result]

    def obtener_detalle_receta_completo(self, rec_id: int) -> Dict:
        """Obtiene detalle completo de una receta para exposición pública."""
        detalle = self._obtener_detalle_receta(rec_id)
        if "nutrientes" in detalle:
            nutrientes = detalle["nutrientes"]
            detalle["nutrientes"] = {
                "kcal": round(float(nutrientes.get("kcal", 0)), 1),
                "proteina_g": round(float(nutrientes.get("proteina_g", 0)), 1),
                "carbohidratos_g": round(float(nutrientes.get("carbohidratos_g", 0)), 1),
                "grasa_g": round(float(nutrientes.get("grasa_g", 0)), 1),
                "fibra_g": round(float(nutrientes.get("fibra_g", 0)), 1),
                "hierro_mg": round(float(nutrientes.get("hierro_mg", 0)), 2),
            }
        return detalle
