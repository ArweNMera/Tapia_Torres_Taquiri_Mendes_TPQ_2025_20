from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.infrastructure.repositories.entidades_repo import EntidadesRepository

router = APIRouter()

@router.get("/")
def list_entidades(q: str | None = None, limit: int = 20, db: Session = Depends(get_db)):
    repo = EntidadesRepository(db)
    return repo.search_entidades(q=q, limit=limit)

@router.get("/tipos")
def list_entidad_tipos(db: Session = Depends(get_db)):
    repo = EntidadesRepository(db)
    return repo.get_entidad_tipos()

