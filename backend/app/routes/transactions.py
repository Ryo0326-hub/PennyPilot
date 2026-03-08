from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_id
from app.db.database import get_db
from app.routes._helpers import get_user_statement_or_404

router = APIRouter(prefix="/statements", tags=["statements"])


@router.get("/{statement_id}")
def get_statement_transactions(
    statement_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    statement = get_user_statement_or_404(db, statement_id, user_id)

    return {
        "statement_id": statement.id,
        "filename": statement.filename,
        "uploaded_at": statement.uploaded_at,
        "transactions": [
            {
                "id": tx.id,
                "date": tx.date,
                "merchant": tx.merchant,
                "description": tx.description,
                "amount": tx.amount,
                "direction": tx.direction,
            }
            for tx in statement.transactions
        ],
    }