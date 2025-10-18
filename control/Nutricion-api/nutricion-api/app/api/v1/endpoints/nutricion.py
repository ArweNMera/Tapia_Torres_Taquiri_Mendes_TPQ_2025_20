"""
Endpoints para el módulo de nutrición (alimentos, recetas, nutrientes).
Endpoints PÚBLICOS - No requieren autenticación.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.nutricion_repo import NutricionRepository
from app.schemas.nutricion import (
    AlimentoConNutrientesResponse,
    AlimentoCreate,
    AlimentoNutrienteCreate,
    AlimentoResponse,
    AlimentoUpdate,
    DisponibilidadAlimentoCreate,
    DisponibilidadAlimentoResponse,
    DisponibilidadAlimentoUpdate,
    NutrienteCreate,
    NutrienteResponse,
    NutrienteUpdate,
    RecetaComidaCreate,
    RecetaCompletaResponse,
    RecetaCreate,
    RecetaIngredienteCreate,
    RecetaIngredienteUpdate,
    RecetaResponse,
    RecetaUpdate,
)

router = APIRouter()


# ========== NUTRIENTES ==========
@router.get("/nutrientes", response_model=list[NutrienteResponse])
def get_nutrientes(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Obtener todos los nutrientes."""
    repo = NutricionRepository(db)
    nutrientes = repo.get_nutrientes(limit=limit)
    return [NutrienteResponse(**n) for n in nutrientes]


@router.get("/nutrientes/{nutri_id}", response_model=NutrienteResponse)
def get_nutriente(
    nutri_id: int,
    db: Session = Depends(get_db),
):
    """Obtener un nutriente por ID."""
    repo = NutricionRepository(db)
    nutriente = repo.get_nutriente_by_id(nutri_id)
    if not nutriente:
        raise HTTPException(status_code=404, detail="Nutriente no encontrado")
    return NutrienteResponse(**nutriente)


@router.post("/nutrientes", response_model=NutrienteResponse, status_code=status.HTTP_201_CREATED)
def create_nutriente(
    nutriente_data: NutrienteCreate,
    db: Session = Depends(get_db),
):
    """Crear un nuevo nutriente."""
    repo = NutricionRepository(db)
    nutriente = repo.create_nutriente(nutriente_data.model_dump())
    if not nutriente:
        raise HTTPException(status_code=400, detail="Error al crear el nutriente")
    return NutrienteResponse(**nutriente)


@router.put("/nutrientes/{nutri_id}", response_model=NutrienteResponse)
def update_nutriente(
    nutri_id: int,
    nutriente_data: NutrienteUpdate,
    db: Session = Depends(get_db),
):
    """Actualizar un nutriente."""
    repo = NutricionRepository(db)
    nutriente = repo.update_nutriente(nutri_id, nutriente_data.model_dump(exclude_unset=True))
    if not nutriente:
        raise HTTPException(status_code=404, detail="Nutriente no encontrado")
    return NutrienteResponse(**nutriente)


@router.delete("/nutrientes/{nutri_id}")
def delete_nutriente(
    nutri_id: int,
    db: Session = Depends(get_db),
):
    """Eliminar un nutriente."""
    repo = NutricionRepository(db)
    success = repo.delete_nutriente(nutri_id)
    if not success:
        raise HTTPException(status_code=404, detail="Nutriente no encontrado")
    return {"message": "Nutriente eliminado exitosamente"}


# ========== ALIMENTOS ==========
@router.get("/alimentos", response_model=list[AlimentoResponse])
def get_alimentos(
    q: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Obtener alimentos con búsqueda opcional."""
    repo = NutricionRepository(db)
    alimentos = repo.get_alimentos(q=q, limit=limit)
    return [AlimentoResponse(**a) for a in alimentos]


@router.get("/alimentos/{ali_id}", response_model=AlimentoConNutrientesResponse)
def get_alimento(
    ali_id: int,
    db: Session = Depends(get_db),
):
    """Obtener un alimento con sus nutrientes."""
    repo = NutricionRepository(db)
    alimento = repo.get_alimento_con_nutrientes(ali_id)
    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")
    return AlimentoConNutrientesResponse(**alimento)


@router.post("/alimentos", response_model=AlimentoResponse, status_code=status.HTTP_201_CREATED)
def create_alimento(
    alimento_data: AlimentoCreate,
    db: Session = Depends(get_db),
):
    """Crear un nuevo alimento."""
    repo = NutricionRepository(db)
    alimento = repo.create_alimento(alimento_data.model_dump())
    if not alimento:
        raise HTTPException(status_code=400, detail="Error al crear el alimento")
    return AlimentoResponse(**alimento)


@router.put("/alimentos/{ali_id}", response_model=AlimentoResponse)
def update_alimento(
    ali_id: int,
    alimento_data: AlimentoUpdate,
    db: Session = Depends(get_db),
):
    """Actualizar un alimento."""
    repo = NutricionRepository(db)
    alimento = repo.update_alimento(ali_id, alimento_data.model_dump(exclude_unset=True))
    if not alimento:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")
    return AlimentoResponse(**alimento)


@router.delete("/alimentos/{ali_id}")
def delete_alimento(
    ali_id: int,
    db: Session = Depends(get_db),
):
    """Eliminar (desactivar) un alimento."""
    repo = NutricionRepository(db)
    success = repo.delete_alimento(ali_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alimento no encontrado")
    return {"message": "Alimento eliminado exitosamente"}


# ========== ALIMENTOS_NUTRIENTES ==========
@router.post("/alimentos/{ali_id}/nutrientes", status_code=status.HTTP_201_CREATED)
def add_nutriente_to_alimento(
    ali_id: int,
    nutriente_data: AlimentoNutrienteCreate,
    db: Session = Depends(get_db),
):
    """Agregar información nutricional a un alimento."""
    if nutriente_data.ali_id != ali_id:
        raise HTTPException(status_code=400, detail="ID de alimento no coincide")

    repo = NutricionRepository(db)
    success = repo.create_alimento_nutriente(nutriente_data.model_dump())
    if not success:
        raise HTTPException(status_code=400, detail="Error al agregar nutriente")
    return {"message": "Nutriente agregado exitosamente"}


@router.delete("/alimentos/{ali_id}/nutrientes/{nutri_id}")
def delete_nutriente_from_alimento(
    ali_id: int,
    nutri_id: int,
    db: Session = Depends(get_db),
):
    """Eliminar información nutricional de un alimento."""
    repo = NutricionRepository(db)
    success = repo.delete_alimento_nutriente(ali_id, nutri_id)
    if not success:
        raise HTTPException(status_code=404, detail="Relación no encontrada")
    return {"message": "Nutriente eliminado del alimento"}


# ========== RECETAS ==========
@router.get("/recetas", response_model=list[RecetaResponse])
def get_recetas(
    tipo_comida: str | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Obtener recetas con filtro opcional por tipo de comida."""
    repo = NutricionRepository(db)
    recetas = repo.get_recetas(tipo_comida=tipo_comida, limit=limit)
    return [RecetaResponse(**r) for r in recetas]


@router.get("/recetas/{rec_id}", response_model=RecetaCompletaResponse)
def get_receta(
    rec_id: int,
    db: Session = Depends(get_db),
):
    """Obtener una receta con ingredientes y tipo de comida."""
    repo = NutricionRepository(db)
    receta = repo.get_receta_completa(rec_id)
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return RecetaCompletaResponse(**receta)


@router.post("/recetas", response_model=RecetaResponse, status_code=status.HTTP_201_CREATED)
def create_receta(
    receta_data: RecetaCreate,
    db: Session = Depends(get_db),
):
    """Crear una nueva receta."""
    repo = NutricionRepository(db)
    receta = repo.create_receta(receta_data.model_dump())
    if not receta:
        raise HTTPException(status_code=400, detail="Error al crear la receta")
    return RecetaResponse(**receta)


@router.put("/recetas/{rec_id}", response_model=RecetaResponse)
def update_receta(
    rec_id: int,
    receta_data: RecetaUpdate,
    db: Session = Depends(get_db),
):
    """Actualizar una receta."""
    repo = NutricionRepository(db)
    receta = repo.update_receta(rec_id, receta_data.model_dump(exclude_unset=True))
    if not receta:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return RecetaResponse(**receta)


@router.delete("/recetas/{rec_id}")
def delete_receta(
    rec_id: int,
    db: Session = Depends(get_db),
):
    """Eliminar (desactivar) una receta."""
    repo = NutricionRepository(db)
    success = repo.delete_receta(rec_id)
    if not success:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return {"message": "Receta eliminada exitosamente"}


# ========== RECETAS_INGREDIENTES ==========
@router.post("/recetas/{rec_id}/ingredientes", status_code=status.HTTP_201_CREATED)
def add_ingrediente_to_receta(
    rec_id: int,
    ingrediente_data: RecetaIngredienteCreate,
    db: Session = Depends(get_db),
):
    """Agregar un ingrediente a una receta."""
    if ingrediente_data.rec_id != rec_id:
        raise HTTPException(status_code=400, detail="ID de receta no coincide")

    repo = NutricionRepository(db)
    success = repo.add_ingrediente_receta(ingrediente_data.model_dump())
    if not success:
        raise HTTPException(status_code=400, detail="Error al agregar ingrediente")
    return {"message": "Ingrediente agregado exitosamente"}


@router.put("/recetas/{rec_id}/ingredientes/{ali_id}")
def update_ingrediente_receta(
    rec_id: int,
    ali_id: int,
    ingrediente_data: RecetaIngredienteUpdate,
    db: Session = Depends(get_db),
):
    """Actualizar cantidad/unidad de un ingrediente en una receta."""
    repo = NutricionRepository(db)
    success = repo.update_ingrediente_receta(
        rec_id, ali_id, ingrediente_data.model_dump(exclude_unset=True)
    )
    if not success:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado en la receta")
    return {"message": "Ingrediente actualizado exitosamente"}


@router.delete("/recetas/{rec_id}/ingredientes/{ali_id}")
def delete_ingrediente_from_receta(
    rec_id: int,
    ali_id: int,
    db: Session = Depends(get_db),
):
    """Eliminar un ingrediente de una receta."""
    repo = NutricionRepository(db)
    success = repo.delete_ingrediente_receta(rec_id, ali_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado en la receta")
    return {"message": "Ingrediente eliminado de la receta"}


# ========== RECETAS_COMIDAS ==========
@router.post("/recetas/{rec_id}/tipos-comida", status_code=status.HTTP_201_CREATED)
def add_tipo_comida_to_receta(
    rec_id: int,
    comida_data: RecetaComidaCreate,
    db: Session = Depends(get_db),
):
    """Agregar un tipo de comida a una receta (DESAYUNO, ALMUERZO, CENA)."""
    if comida_data.rec_id != rec_id:
        raise HTTPException(status_code=400, detail="ID de receta no coincide")

    repo = NutricionRepository(db)
    success = repo.add_tipo_comida_receta(rec_id, comida_data.rc_comida)
    if not success:
        raise HTTPException(status_code=400, detail="Error al agregar tipo de comida")
    return {"message": "Tipo de comida agregado exitosamente"}


@router.delete("/recetas/{rec_id}/tipos-comida/{tipo_comida}")
def delete_tipo_comida_from_receta(
    rec_id: int,
    tipo_comida: str,
    db: Session = Depends(get_db),
):
    """Eliminar un tipo de comida de una receta."""
    repo = NutricionRepository(db)
    success = repo.delete_tipo_comida_receta(rec_id, tipo_comida)
    if not success:
        raise HTTPException(status_code=404, detail="Tipo de comida no encontrado en la receta")
    return {"message": "Tipo de comida eliminado de la receta"}


# ========== DISPONIBILIDAD_ALIMENTOS ==========
@router.get("/disponibilidad", response_model=list[DisponibilidadAlimentoResponse])
def get_disponibilidad_alimentos(
    ent_id: int | None = None,
    ali_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Obtener disponibilidad de alimentos filtrada por entidad o alimento."""
    repo = NutricionRepository(db)
    disponibilidad = repo.get_disponibilidad_alimentos(ent_id=ent_id, ali_id=ali_id)
    return [DisponibilidadAlimentoResponse(**d) for d in disponibilidad]


@router.post(
    "/disponibilidad",
    response_model=DisponibilidadAlimentoResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_disponibilidad_alimento(
    disponibilidad_data: DisponibilidadAlimentoCreate,
    db: Session = Depends(get_db),
):
    """Crear registro de disponibilidad de alimento."""
    repo = NutricionRepository(db)
    disponibilidad = repo.create_disponibilidad_alimento(disponibilidad_data.model_dump())
    if not disponibilidad:
        raise HTTPException(status_code=400, detail="Error al crear disponibilidad")
    return DisponibilidadAlimentoResponse(**disponibilidad)


@router.put("/disponibilidad/{dis_id}")
def update_disponibilidad_alimento(
    dis_id: int,
    disponibilidad_data: DisponibilidadAlimentoUpdate,
    db: Session = Depends(get_db),
):
    """Actualizar disponibilidad de alimento."""
    repo = NutricionRepository(db)
    success = repo.update_disponibilidad_alimento(
        dis_id, disponibilidad_data.model_dump(exclude_unset=True)
    )
    if not success:
        raise HTTPException(status_code=404, detail="Disponibilidad no encontrada")
    return {"message": "Disponibilidad actualizada exitosamente"}


@router.delete("/disponibilidad/{dis_id}")
def delete_disponibilidad_alimento(
    dis_id: int,
    db: Session = Depends(get_db),
):
    """Eliminar disponibilidad de alimento."""
    repo = NutricionRepository(db)
    success = repo.delete_disponibilidad_alimento(dis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Disponibilidad no encontrada")
    return {"message": "Disponibilidad eliminada exitosamente"}
