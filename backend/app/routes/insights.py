from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_id
from app.db.database import get_db
from app.routes._helpers import get_user_statement_or_404
from app.services.summary import build_statement_summary
from app.services.llm_service import generate_spending_insights

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/{statement_id}")
def get_statement_insights(
    statement_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    statement = get_user_statement_or_404(db, statement_id, user_id)

    summary = build_statement_summary(statement)
    insights = generate_spending_insights(summary)

    return {
        "statement_id": statement.id,
        "filename": statement.filename,
        "insights": insights,
    }