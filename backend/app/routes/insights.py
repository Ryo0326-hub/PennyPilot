from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Statement
from app.services.summary import build_statement_summary
from app.services.llm_service import generate_spending_insights

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/{statement_id}")
def get_statement_insights(statement_id: int, db: Session = Depends(get_db)):
    statement = db.query(Statement).filter(Statement.id == statement_id).first()

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")

    summary = build_statement_summary(statement)
    insights = generate_spending_insights(summary)

    return {
        "statement_id": statement.id,
        "filename": statement.filename,
        "insights": insights,
    }