from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_size=10,  # Optimizado para min-instances=1
    max_overflow=20,  # Conexiones adicionales bajo carga
    pool_timeout=30,  # Timeout razonable
    pool_recycle=1800,  # Reciclar conexiones cada 30min
    echo_pool=False,  # Desactivar logs del pool en producción
    connect_args={
        "connect_timeout": 10,  # Timeout de conexión optimizado
        "read_timeout": 30,  # Timeout de lectura
        "write_timeout": 30,  # Timeout de escritura
    },
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
