from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Statement

router = APIRouter(prefix="/statements", tags=["statements"])


@router.get("/{statement_id}")
def get_statement_transactions(statement_id: int, db: Session = Depends(get_db)):
    statement = db.query(Statement).filter(Statement.id == statement_id).first()

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")

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