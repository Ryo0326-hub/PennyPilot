from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Statement
from app.services.summary import build_statement_summary
from app.services.simulator import build_simulation

router = APIRouter(prefix="/simulate", tags=["simulate"])


class StrategyRequest(BaseModel):
    restaurants_reduction_pct: int = 0
    subscriptions_reduction_pct: int = 0
    shopping_reduction_pct: int = 0


@router.post("/{statement_id}")
def simulate_statement_strategy(
    statement_id: int,
    strategy: StrategyRequest,
    db: Session = Depends(get_db),
):
    statement = db.query(Statement).filter(Statement.id == statement_id).first()

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")

    summary = build_statement_summary(statement)
    simulation = build_simulation(summary, strategy.model_dump())

    return {
        "statement_id": statement.id,
        "filename": statement.filename,
        "simulation": simulation,
    }