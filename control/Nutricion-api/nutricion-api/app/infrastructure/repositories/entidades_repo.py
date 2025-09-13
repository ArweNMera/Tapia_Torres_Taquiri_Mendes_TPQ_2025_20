from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

class EntidadesRepository:
    def __init__(self, db: Session):
        self.db = db

    def search_entidades(self, q: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        if q:
            query = text(
                """
                SELECT e.ent_id, e.ent_codigo, e.ent_nombre, e.ent_descripcion,
                       e.ent_direccion, e.ent_departamento, e.ent_provincia, e.ent_distrito,
                       t.entti_id, t.entti_codigo, t.entti_nombre
                FROM entidades e
                JOIN entidad_tipos t ON e.entti_id = t.entti_id
                WHERE e.ent_nombre LIKE :q OR e.ent_codigo LIKE :q
                ORDER BY e.ent_nombre ASC
                LIMIT :limit
                """
            )
            params = {"q": f"%{q}%", "limit": limit}
        else:
            query = text(
                """
                SELECT e.ent_id, e.ent_codigo, e.ent_nombre, e.ent_descripcion,
                       e.ent_direccion, e.ent_departamento, e.ent_provincia, e.ent_distrito,
                       t.entti_id, t.entti_codigo, t.entti_nombre
                FROM entidades e
                JOIN entidad_tipos t ON e.entti_id = t.entti_id
                ORDER BY e.ent_nombre ASC
                LIMIT :limit
                """
            )
            params = {"limit": limit}

        rows = self.db.execute(query, params).fetchall()
        return [
            {
                "ent_id": r.ent_id,
                "ent_codigo": r.ent_codigo,
                "ent_nombre": r.ent_nombre,
                "ent_descripcion": r.ent_descripcion,
                "ent_direccion": r.ent_direccion,
                "ent_departamento": r.ent_departamento,
                "ent_provincia": r.ent_provincia,
                "ent_distrito": r.ent_distrito,
                "entti_id": r.entti_id,
                "entti_codigo": r.entti_codigo,
                "entti_nombre": r.entti_nombre,
            }
            for r in rows
        ]

    def get_entidad_tipos(self) -> List[Dict[str, Any]]:
        rows = self.db.execute(text("SELECT entti_id, entti_codigo, entti_nombre FROM entidad_tipos ORDER BY entti_nombre"))
        return [
            {
                "entti_id": r.entti_id,
                "entti_codigo": r.entti_codigo,
                "entti_nombre": r.entti_nombre,
            }
            for r in rows
        ]
