from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional


class EntidadesRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_entidades(self, q: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        rows = self.db.execute(
            text("CALL sp_entidades_buscar(:query, :limit)"),
            {"query": q, "limit": limit},
        ).fetchall()

        return [
            {
                "ent_id": r.ent_id,
                "ent_codigo": r.ent_codigo,
                "ent_nombre": r.ent_nombre,
                "ent_descripcion": getattr(r, "ent_descripcion", None),
                "ent_direccion": getattr(r, "ent_direccion", None),
                "ent_departamento": getattr(r, "ent_departamento", None),
                "ent_provincia": getattr(r, "ent_provincia", None),
                "ent_distrito": getattr(r, "ent_distrito", None),
                "entti_id": getattr(r, "entti_id", None),
                "entti_codigo": getattr(r, "entti_codigo", None),
                "entti_nombre": getattr(r, "entti_nombre", None),
            }
            for r in rows
        ]

    def get_entidad_tipos(self) -> List[Dict[str, Any]]:
        rows = self.db.execute(text("CALL sp_entidad_tipos_listar()"))
        return [
            {
                "entti_id": r.entti_id,
                "entti_codigo": r.entti_codigo,
                "entti_nombre": r.entti_nombre,
            }
            for r in rows
        ]
