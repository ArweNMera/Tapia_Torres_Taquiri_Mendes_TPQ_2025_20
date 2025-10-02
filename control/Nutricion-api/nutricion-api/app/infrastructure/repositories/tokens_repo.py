from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime


class TokensRepository:
    """Repositorio para manejo de tokens revocados (lista negra)."""

    def revoke(self, db: Session, jti: str, username: str, exp: datetime):
        db.execute(
            text("CALL sp_tokens_revocar(:jti, :usuario, :expira_en)"),
            {"jti": jti, "usuario": username, "expira_en": exp},
        ).fetchone()
        db.commit()

    def is_revoked(self, db: Session, jti: str) -> bool:
        res = db.execute(
            text("CALL sp_tokens_esta_revocado(:jti)"),
            {"jti": jti},
        ).fetchone()
        return bool(res and getattr(res, "esta_revocado", 0))
