from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime


class TokensRepository:
    """Repositorio para manejo de tokens revocados (lista negra)."""

    def revoke(self, db: Session, jti: str, username: str, exp: datetime):
        db.execute(
            text("""
                INSERT IGNORE INTO tokens_revocados(jti, usuario, expira_en)
                VALUES (:jti, :usuario, :expira_en)
            """),
            {"jti": jti, "usuario": username, "expira_en": exp},
        )
        db.commit()

    def is_revoked(self, db: Session, jti: str) -> bool:
        res = db.execute(
            text("SELECT 1 FROM tokens_revocados WHERE jti = :jti LIMIT 1"),
            {"jti": jti},
        ).fetchone()
        return res is not None
