"""
Repositorio para operaciones de nutrición usando procedimientos almacenados.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session


class NutricionRepository:
    """Repositorio que usa procedimientos almacenados para operaciones de nutrición"""

    def __init__(self, db: Session):
        self.db = db

    def _call_sp(self, sp_name: str, params: List[Any] = None) -> List[Dict]:
        """
        Ejecuta un procedimiento almacenado y retorna los resultados.

        Args:
            sp_name: Nombre del procedimiento almacenado
            params: Lista de parámetros (en orden) para el SP

        Returns:
            Lista de diccionarios con los resultados
        """
        if params is None:
            params = []

        # Construir la llamada con placeholders
        placeholders = ", ".join([":param" + str(i) for i in range(len(params))])
        query = f"CALL {sp_name}({placeholders})" if params else f"CALL {sp_name}()"

        # Crear diccionario de parámetros
        param_dict = {f"param{i}": val for i, val in enumerate(params)}

        result = self.db.execute(text(query), param_dict)
        self.db.commit()

        # Convertir resultados a lista de diccionarios
        if result.returns_rows:
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
        return []

    # ========== NUTRIENTES ==========

    def get_nutrientes(self, q: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Listar nutrientes con filtro opcional"""
        return self._call_sp("sp_nutrientes_listar", [q, limit])

    def get_nutriente_by_id(self, nut_id: int) -> Optional[Dict]:
        """Obtener un nutriente por ID"""
        results = self._call_sp("sp_nutrientes_obtener", [nut_id])
        return results[0] if results else None

    def create_nutriente(self, data: dict) -> Optional[Dict]:
        """Crear un nuevo nutriente"""
        results = self._call_sp(
            "sp_nutrientes_crear",
            [data.get("nutri_codigo", "NUTR"), data.get("nutri_nombre"), data.get("nutri_unidad")],
        )
        return results[0] if results else None

    def update_nutriente(self, nutri_id: int, data: dict) -> Optional[Dict]:
        """Actualizar un nutriente"""
        results = self._call_sp(
            "sp_nutrientes_actualizar",
            [
                nutri_id,
                data.get("nutri_codigo", "NUTR"),
                data.get("nutri_nombre"),
                data.get("nutri_unidad"),
            ],
        )
        return results[0] if results else None

    def delete_nutriente(self, nutri_id: int) -> bool:
        """Eliminar un nutriente"""
        results = self._call_sp("sp_nutrientes_eliminar", [nutri_id])
        return results[0].get("affected_rows", 0) > 0 if results else False

    # ========== ALIMENTOS ==========

    def get_alimentos(self, q: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Listar alimentos con filtro opcional"""
        return self._call_sp("sp_alimentos_listar", [q, limit])

    def get_alimento_by_id(self, ali_id: int) -> Optional[Dict]:
        """Obtener un alimento por ID"""
        results = self._call_sp("sp_alimentos_obtener", [ali_id])
        return results[0] if results else None

    def create_alimento(self, data: dict) -> Optional[Dict]:
        """Crear un nuevo alimento"""
        results = self._call_sp(
            "sp_alimentos_crear",
            [
                data.get("ali_nombre"),
                data.get("ali_nombre_cientifico"),
                data.get("ali_grupo"),
                data.get("ali_unidad"),
            ],
        )
        return results[0] if results else None

    def update_alimento(self, ali_id: int, data: dict) -> Optional[Dict]:
        """Actualizar un alimento"""
        results = self._call_sp(
            "sp_alimentos_actualizar",
            [
                ali_id,
                data.get("ali_nombre"),
                data.get("ali_nombre_cientifico"),
                data.get("ali_grupo"),
                data.get("ali_unidad"),
                data.get("ali_activo", 1),
            ],
        )
        return results[0] if results else None

    def delete_alimento(self, ali_id: int) -> bool:
        """Eliminar un alimento"""
        results = self._call_sp("sp_alimentos_eliminar", [ali_id])
        return results[0].get("affected_rows", 0) > 0 if results else False

    def get_alimento_con_nutrientes(self, ali_id: int) -> Optional[Dict]:
        """Obtener alimento con sus nutrientes usando procedimiento almacenado"""
        # Este SP retorna múltiples result sets
        placeholders = ":param0"
        query = f"CALL sp_alimentos_con_nutrientes_obtener({placeholders})"
        param_dict = {"param0": ali_id}

        result = self.db.execute(text(query), param_dict)

        # Primera result set: información del alimento
        alimento_data = None
        if result.returns_rows:
            columns = result.keys()
            row = result.fetchone()
            if row:
                alimento_data = dict(zip(columns, row))

        if not alimento_data:
            return None

        # Obtener segunda result set (nutrientes)
        try:
            if result.cursor.nextset():
                columns = [desc[0] for desc in result.cursor.description]
                nutrientes = [dict(zip(columns, row)) for row in result.cursor.fetchall()]
                alimento_data["nutrientes"] = nutrientes
            else:
                alimento_data["nutrientes"] = []
        except Exception:
            alimento_data["nutrientes"] = []

        self.db.commit()
        return alimento_data

    # ========== ALIMENTOS_NUTRIENTES ==========

    def create_alimento_nutriente(self, data: dict) -> bool:
        """Crear relación alimento-nutriente"""
        results = self._call_sp(
            "sp_alimentos_nutrientes_crear",
            [
                data.get("ali_id"),
                data.get("nutri_id"),
                data.get("an_cantidad_100"),
                data.get("an_fuente"),
            ],
        )
        return len(results) > 0

    def delete_alimento_nutriente(self, ali_id: int, nutri_id: int) -> bool:
        """Eliminar relación alimento-nutriente"""
        # Usar la PRIMARY KEY compuesta (ali_id, nutri_id)
        results = self._call_sp("sp_alimentos_nutrientes_eliminar", [ali_id, nutri_id])
        return results[0].get("affected_rows", 0) > 0 if results else False

    def update_alimento_nutriente(self, ali_id: int, nutri_id: int, data: dict) -> bool:
        """Actualizar relación alimento-nutriente"""
        results = self._call_sp(
            "sp_alimentos_nutrientes_actualizar",
            [ali_id, nutri_id, data.get("an_cantidad_100"), data.get("an_fuente")],
        )
        return len(results) > 0

    # ========== RECETAS ==========

    def get_recetas(self, tipo_comida: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Listar recetas con filtro opcional por tipo de comida"""
        if tipo_comida:
            return self._call_sp("sp_recetas_por_tipo_comida_listar", [tipo_comida, limit])
        else:
            return self._call_sp("sp_recetas_listar", [None, limit])

    def get_receta_by_id(self, rec_id: int) -> Optional[Dict]:
        """Obtener una receta por ID"""
        results = self._call_sp("sp_recetas_obtener", [rec_id])
        return results[0] if results else None

    def create_receta(self, data: dict) -> Optional[Dict]:
        """Crear una nueva receta"""
        results = self._call_sp(
            "sp_recetas_crear", [data.get("rec_nombre"), data.get("rec_instrucciones")]
        )
        return results[0] if results else None

    def update_receta(self, rec_id: int, data: dict) -> Optional[Dict]:
        """Actualizar una receta"""
        results = self._call_sp(
            "sp_recetas_actualizar",
            [
                rec_id,
                data.get("rec_nombre"),
                data.get("rec_instrucciones"),
                data.get("rec_activo", 1),
            ],
        )
        return results[0] if results else None

    def delete_receta(self, rec_id: int) -> bool:
        """Eliminar una receta"""
        results = self._call_sp("sp_recetas_eliminar", [rec_id])
        return results[0].get("affected_rows", 0) > 0 if results else False

    def get_receta_completa(self, rec_id: int) -> Optional[Dict]:
        """Obtener receta completa con ingredientes usando procedimiento almacenado"""
        placeholders = ":param0"
        query = f"CALL sp_recetas_completa_obtener({placeholders})"
        param_dict = {"param0": rec_id}

        result = self.db.execute(text(query), param_dict)

        receta_data = None
        if result.returns_rows:
            columns = result.keys()
            row = result.fetchone()
            if row:
                receta_data = dict(zip(columns, row))

        if not receta_data:
            return None
        try:
            if result.cursor.nextset():
                columns = [desc[0] for desc in result.cursor.description]
                ingredientes = [dict(zip(columns, row)) for row in result.cursor.fetchall()]
                receta_data["ingredientes"] = ingredientes
            else:
                receta_data["ingredientes"] = []
        except Exception:
            receta_data["ingredientes"] = []

        self.db.commit()
        return receta_data

    def add_ingrediente_receta(self, data: dict) -> bool:
        """Agregar ingrediente a receta"""
        results = self._call_sp(
            "sp_recetas_ingredientes_crear",
            [
                data.get("rec_id"),
                data.get("ali_id"),
                data.get("ri_cantidad"),
                data.get("ri_unidad"),
            ],
        )
        return len(results) > 0

    def update_ingrediente_receta(self, rec_id: int, ali_id: int, data: dict) -> bool:
        """Actualizar ingrediente de receta"""
        results = self._call_sp(
            "sp_recetas_ingredientes_actualizar",
            [rec_id, ali_id, data.get("ri_cantidad"), data.get("ri_unidad")],
        )
        return len(results) > 0

    def delete_ingrediente_receta(self, rec_id: int, ali_id: int) -> bool:
        """Eliminar ingrediente de receta"""
        results = self._call_sp("sp_recetas_ingredientes_eliminar", [rec_id, ali_id])
        return results[0].get("affected_rows", 0) > 0 if results else False

    def add_tipo_comida_receta(self, rec_id: int, tipo_comida: str) -> bool:
        """Asociar receta con tipo de comida"""
        results = self._call_sp("sp_recetas_comidas_crear", [rec_id, tipo_comida])
        return len(results) > 0

    def delete_tipo_comida_receta(self, rec_id: int, rc_id: int) -> bool:
        """Eliminar asociación receta-tipo de comida por rc_id"""
        results = self._call_sp("sp_recetas_comidas_eliminar", [rc_id])
        return results[0].get("affected_rows", 0) > 0 if results else False

    def get_disponibilidad_alimentos(
        self, region: Optional[str] = None, periodo: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """Listar disponibilidad de alimentos usando procedimiento almacenado"""
        return self._call_sp("sp_disponibilidad_listar", [region, periodo, limit])

    def create_disponibilidad_alimento(self, data: dict) -> Optional[Dict]:
        """Crear disponibilidad de alimento"""
        results = self._call_sp(
            "sp_disponibilidad_crear",
            [
                data.get("ali_id"),
                data.get("ent_id"),
                data.get("dis_periodo"),
                data.get("dis_disponible"),
                data.get("dis_precio_promedio"),
                data.get("dis_region"),
            ],
        )
        return results[0] if results else None

    def update_disponibilidad_alimento(self, dis_id: int, data: dict) -> bool:
        """Actualizar disponibilidad de alimento"""
        results = self._call_sp(
            "sp_disponibilidad_actualizar",
            [dis_id, data.get("dis_disponible"), data.get("dis_precio_promedio")],
        )
        return len(results) > 0

    def delete_disponibilidad_alimento(self, dis_id: int) -> bool:
        """Eliminar disponibilidad de alimento"""
        results = self._call_sp("sp_disponibilidad_eliminar", [dis_id])
        return results[0].get("affected_rows", 0) > 0 if results else False
