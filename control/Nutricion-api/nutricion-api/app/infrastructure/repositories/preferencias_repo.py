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
        query = text("CALL sp_preferencias_listar(:nin_id, :tipo_comida)")
        params = {"nin_id": nin_id, "tipo_comida": tipo_comida}
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
        result = self.db.execute(
            text("CALL sp_preferencias_desactivar(:npc_id)"), {"npc_id": npc_id}
        )
        self.db.commit()
        row = result.fetchone()
        return bool(row and getattr(row, "affected_rows", 0))

    def obtener_resumen_preferencias(self, usr_id: int) -> List[Dict]:
        """Obtiene resumen de preferencias de todos los niños del usuario"""
        result = self.db.execute(text("CALL sp_preferencias_resumen(:usr_id)"), {"usr_id": usr_id})
        return [dict(row._mapping) for row in result]
