from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Statement
from app.services.summary import build_statement_summary
from app.services.simulator import build_simulation
from app.services.simulation_insights import generate_simulation_insight

router = APIRouter(prefix="/simulation-insights", tags=["simulation-insights"])


@router.post("/{statement_id}")
def get_simulation_insights(statement_id: int, strategy: dict, db: Session = Depends(get_db)):

    statement = db.query(Statement).filter(Statement.id == statement_id).first()

    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")

    summary = build_statement_summary(statement)

    simulation = build_simulation(summary, strategy)

    explanation = generate_simulation_insight(simulation)

    return {
        "statement_id": statement.id,
        "filename": statement.filename,
        "simulation": simulation,
        "ai_explanation": explanation
    }