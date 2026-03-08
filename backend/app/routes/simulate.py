from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_id
from app.db.database import get_db
from app.routes._helpers import get_user_statement_or_404
from app.services.summary import build_statement_summary
from app.services.simulator import build_simulation

router = APIRouter(prefix="/simulate", tags=["simulate"])


class StrategyRequest(BaseModel):
    category_reductions: dict[str, float] = {}


@router.post("/{statement_id}")
def simulate_statement_strategy(
    statement_id: int,
    strategy: StrategyRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    statement = get_user_statement_or_404(db, statement_id, user_id)

    summary = build_statement_summary(statement)
    simulation = build_simulation(summary, strategy.category_reductions)

    return {
        "statement_id": statement.id,
        "filename": statement.filename,
        "simulation": simulation,
    }