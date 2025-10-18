"""
Repositorio para gestión de preferencias alimentarias
"""

import json
from typing import Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class PreferenciasRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_preferencias_nino(
        self, nin_id: int, tipo_comida: Optional[str] = None
    ) -> List[Dict]:
        """Obtiene las preferencias de un niño"""
        if tipo_comida:
            query = text("""
                SELECT npc_id, npc_preferencia, creado_en
                FROM ninos_preferencias_comidas
                WHERE nin_id = :nin_id
                  AND npc_tipo_comida = :tipo_comida
                  AND npc_activo = TRUE
                ORDER BY creado_en ASC
            """)
            params = {"nin_id": nin_id, "tipo_comida": tipo_comida}
        else:
            query = text("""
                SELECT npc_id, npc_tipo_comida, npc_preferencia, creado_en
                FROM ninos_preferencias_comidas
                WHERE nin_id = :nin_id AND npc_activo = TRUE
                ORDER BY npc_tipo_comida, creado_en ASC
            """)
            params = {"nin_id": nin_id}

        result = self.db.execute(query, params)
        return [dict(row._mapping) for row in result]

    def guardar_preferencias(self, nin_id: int, tipo_comida: str, preferencias: List[str]) -> Dict:
        """Guarda las preferencias de un niño para un tipo de comida"""
        # Convertir lista a JSON
        preferencias_json = json.dumps(preferencias)

        query = text("""
            CALL sp_guardar_preferencias_nino(:nin_id, :tipo_comida, :preferencias)
        """)

        result = self.db.execute(
            query, {"nin_id": nin_id, "tipo_comida": tipo_comida, "preferencias": preferencias_json}
        )
        self.db.commit()
        row = result.first()
        return dict(row._mapping) if row else {"mensaje": "Preferencias guardadas"}

    def eliminar_preferencia(self, npc_id: int) -> bool:
        """Desactiva una preferencia específica"""
        query = text("""
            UPDATE ninos_preferencias_comidas
            SET npc_activo = FALSE
            WHERE npc_id = :npc_id
        """)

        self.db.execute(query, {"npc_id": npc_id})
        self.db.commit()
        return True

    def obtener_resumen_preferencias(self, usr_id: int) -> List[Dict]:
        """Obtiene resumen de preferencias de todos los niños del usuario"""
        query = text("""
            SELECT
                n.nin_id,
                n.nin_nombres,
                COUNT(DISTINCT npc.npc_id) > 0 AS tiene_preferencias,
                COUNT(DISTINCT npc.npc_id) AS total_preferencias,
                MAX(npc.actualizado_en) AS ultima_actualizacion
            FROM ninos n
            LEFT JOIN ninos_preferencias_comidas npc
                ON npc.nin_id = n.nin_id AND npc.npc_activo = TRUE
            WHERE n.usr_id_propietario = :usr_id OR n.usr_id_tutor = :usr_id
            GROUP BY n.nin_id, n.nin_nombres
            ORDER BY n.nin_nombres
        """)

        result = self.db.execute(query, {"usr_id": usr_id})
        return [dict(row._mapping) for row in result]
