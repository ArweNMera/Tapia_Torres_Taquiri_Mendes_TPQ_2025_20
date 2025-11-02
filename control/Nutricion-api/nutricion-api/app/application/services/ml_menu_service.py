"""
Servicio de aplicación para generación de menús con Machine Learning
Orquesta la lógica de negocio entre el servidor ML y la persistencia
"""

import logging
from datetime import date
from typing import Any, Dict, Optional

from app.infrastructure.ml_client import ml_client
from app.infrastructure.repositories.ninos_repo import NinosRepository
from app.infrastructure.repositories.planes_comidas_repo import PlanesComidasRepository
from app.infrastructure.repositories.preferencias_repo import PreferenciasRepository

logger = logging.getLogger(__name__)


class MLMenuService:
    """
    Servicio que coordina la generación de menús usando ML
    Respeta la arquitectura hexagonal: Aplicación orquesta Infraestructura
    """

    def __init__(
        self,
        planes_repo: PlanesComidasRepository,
        ninos_repo: NinosRepository,
        prefs_repo: PreferenciasRepository,
    ):
        """
        Inicializa el servicio con sus dependencias

        Args:
            planes_repo: Repositorio de planes de comidas
            ninos_repo: Repositorio de niños
            prefs_repo: Repositorio de preferencias
        """
        self.planes_repo = planes_repo
        self.ninos_repo = ninos_repo
        self.prefs_repo = prefs_repo

    async def generar_plan_semanal_con_ml(
        self,
        nin_id: int,
        fecha_inicio: Optional[date] = None,
        incluir_refacciones: bool = False,
        dias: int = 7,
    ) -> Dict[str, Any]:
        """
        Genera un plan semanal de comidas usando el modelo ML entrenado

        Flujo:
        1. Valida que el niño tenga perfil nutricional
        2. Obtiene datos del niño, alergias y preferencias
        3. Llama al servidor ML para generar el plan
        4. Persiste el plan en la base de datos
        5. Retorna el plan generado

        Args:
            nin_id: ID del niño
            fecha_inicio: Fecha de inicio del plan (opcional)
            incluir_refacciones: Si incluir refacciones (snacks)
            dias: Número de días (1-7)

        Returns:
            Dict con el plan semanal generado y persistido

        Raises:
            ValueError: Si el niño no tiene perfil nutricional o no existe
            Exception: Si hay error en la generación o persistencia
        """
        logger.info(f"🎯 Iniciando generación de plan semanal ML para niño {nin_id}")

        # 1. Verificar perfil nutricional
        perfil = self.planes_repo.obtener_perfil_nutricional(nin_id)
        if not perfil:
            raise ValueError(
                f"El niño {nin_id} no tiene perfil nutricional vigente. "
                "Debe calcularlo primero usando POST /planes-comidas/ninos/{nin_id}/calcular-perfil"
            )

        logger.info(f"✅ Perfil nutricional: {perfil['pnn_clasificacion']}")

        # 2. Obtener datos del niño
        nino = self.planes_repo.obtener_datos_nino(nin_id)
        if not nino:
            raise ValueError(f"No se encontró el niño con ID {nin_id}")

        logger.info(f"✅ Niño: {nino.get('nin_nombres', 'N/A')}")

        # 3. Obtener alergias
        try:
            alergias = self.ninos_repo.obtener_alergias(nin_id)
            alergias_list = [a["ta_nombre"] for a in alergias]
            logger.info(f"🚫 Alergias ({len(alergias_list)}): {alergias_list}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron obtener alergias: {e}")
            alergias_list = []

        # 4. Obtener preferencias
        try:
            preferencias_data = self.prefs_repo.obtener_preferencias_nino(nin_id)
            preferencias_dict = {}
            for pref in preferencias_data:
                tipo = pref["npc_tipo_comida"]
                if tipo not in preferencias_dict:
                    preferencias_dict[tipo] = []
                preferencias_dict[tipo].append(pref["npc_preferencia"])
            logger.info(f"💚 Preferencias: {list(preferencias_dict.keys())}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron obtener preferencias: {e}")
            preferencias_dict = {}

        # 5. Llamar al servidor ML para generar el plan
        logger.info("📡 Llamando servidor ML...")
        plan_ml = await ml_client.generar_plan_semanal_ml(
            child_id=nin_id,
            nutrition_status=perfil["pnn_clasificacion"],
            allergies=alergias_list,
            preferences=preferencias_dict,
            days=min(dias, 7),
        )

        logger.info(
            f"✅ Plan ML generado: {plan_ml.get('total_days')} días, "
            f"{plan_ml.get('total_meals')} comidas"
        )

        # 6. Persistir el plan en la base de datos
        try:
            menu_persistido = await self._persistir_plan_ml(
                nin_id=nin_id,
                plan_ml=plan_ml,
                fecha_inicio=fecha_inicio,
            )
            logger.info(f"💾 Plan persistido con ID: {menu_persistido.get('men_id')}")

            # 7. Retornar el plan completo con información de persistencia
            return {
                "exito": True,
                "men_id": menu_persistido.get("men_id"),
                "nin_id": nin_id,
                "plan_ml": plan_ml,
                "menu_persistido": menu_persistido,
                "perfil": {
                    "pnn_clasificacion": perfil["pnn_clasificacion"],
                    "pnn_calorias_diarias": perfil["pnn_calorias_diarias"],
                },
                "alergias": alergias_list,
            }

        except Exception as e:
            logger.error(f"❌ Error persistiendo plan: {e}", exc_info=True)
            # Retornar el plan ML aunque no se haya persistido
            return {
                "exito": False,
                "error_persistencia": str(e),
                "plan_ml": plan_ml,
                "mensaje": "Plan generado pero no se pudo guardar en la base de datos",
            }

    async def _persistir_plan_ml(
        self,
        nin_id: int,
        plan_ml: Dict[str, Any],
        fecha_inicio: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Persiste el plan generado por ML en la base de datos

        Args:
            nin_id: ID del niño
            plan_ml: Plan generado por el servidor ML
            fecha_inicio: Fecha de inicio del plan

        Returns:
            Dict con información del menú persistido

        Raises:
            Exception: Si hay error en la persistencia
        """
        logger.info(f"💾 Persistiendo plan ML para niño {nin_id}...")

        # TODO: Implementar persistencia usando sp_menus_crear o similar
        # Por ahora retornamos un mock hasta que se implemente el SP adecuado

        logger.warning("⚠️ Persistencia de plan ML no implementada aún")

        return {
            "men_id": None,
            "nin_id": nin_id,
            "men_generado_por": "IA",
            "men_estado": "BORRADOR",
            "mensaje": "Plan generado exitosamente (persistencia pendiente de implementar)",
        }

    async def verificar_servidor_ml(self) -> Dict[str, Any]:
        """
        Verifica si el servidor ML está disponible

        Returns:
            Dict con estado del servidor ML
        """
        disponible = await ml_client.verificar_salud()

        return {
            "servidor_ml_disponible": disponible,
            "url": ml_client.base_url,
            "estado": "disponible" if disponible else "no disponible",
        }
