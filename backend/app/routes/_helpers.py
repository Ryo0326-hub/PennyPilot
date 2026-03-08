from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Statement


def get_user_statement_or_404(db: Session, statement_id: int, owner_id: str) -> Statement:
    statement = (
        db.query(Statement)
        .filter(Statement.id == statement_id, Statement.owner_id == owner_id)
        .first()
    )
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    return statement
