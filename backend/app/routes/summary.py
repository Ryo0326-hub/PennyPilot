from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Statement
from app.services.summary import build_statement_summary

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/{statement_id}")
def get_statement_summary(statement_id: int, db: Session = Depends(get_db)):
    statement = db.query(Statement).filter(Statement.id == statement_id).first()

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")

    return build_statement_summary(statement)