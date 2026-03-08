from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_id
from app.db.database import get_db
from app.routes._helpers import get_user_statement_or_404
from app.services.summary import build_statement_summary

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/{statement_id}")
def get_statement_summary(
    statement_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    statement = get_user_statement_or_404(db, statement_id, user_id)

    return build_statement_summary(statement)