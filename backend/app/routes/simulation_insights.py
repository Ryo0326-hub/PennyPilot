from __future__ import annotations

import os
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_id
from app.db.database import get_db
from app.routes._helpers import get_user_statement_or_404
from app.services.summary import build_statement_summary
from app.services.personalized_plan import build_personalized_plan
from app.services.simulation_insights import generate_simulation_insight

router = APIRouter(prefix="/simulation-insights", tags=["simulation-insights"])
ENABLE_PERSONAL_GOALS = os.getenv("ENABLE_PERSONAL_GOALS", "true").strip().lower() == "true"


class StrategyRequest(BaseModel):
    category_reductions: dict[str, float] = Field(default_factory=dict)

    @field_validator("category_reductions")
    @classmethod
    def validate_category_reductions(cls, value: dict[str, float]) -> dict[str, float]:
        if len(value) > 40:
            raise ValueError("Too many category reductions")
        for category, pct in value.items():
            if not str(category).strip():
                raise ValueError("Category name cannot be empty")
            if pct < 0 or pct > 100:
                raise ValueError("Reduction percent must be between 0 and 100")
        return value


class GoalInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=300)
    target_amount: Optional[float] = Field(default=None, gt=0)
    target_date: Optional[date] = None

    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, value: Optional[date]) -> Optional[date]:
        if value and value <= date.today():
            raise ValueError("target_date must be in the future")
        return value


class PersonalPlanRequest(BaseModel):
    strategy: Optional[StrategyRequest] = None
    goals: list[GoalInput] = Field(default_factory=list)

    @field_validator("goals")
    @classmethod
    def validate_goal_count(cls, value: list[GoalInput]) -> list[GoalInput]:
        if len(value) > 5:
            raise ValueError("A maximum of 5 goals are supported")
        return value


@router.post("/{statement_id}")
def get_simulation_insights(
    statement_id: int,
    payload: PersonalPlanRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    statement = get_user_statement_or_404(db, statement_id, user_id)

    summary = build_statement_summary(statement)

    personalized_plan = build_personalized_plan(
        summary=summary,
        goals=[goal.model_dump(mode="json") for goal in payload.goals] if ENABLE_PERSONAL_GOALS else [],
        strategy_override=payload.strategy.category_reductions if payload.strategy else None,
    )

    explanation = generate_simulation_insight(
        simulation=personalized_plan["simulation"],
        estimated_goal_costs=personalized_plan["estimated_goal_costs"],
        goal_funding_plan=personalized_plan["goal_funding_plan"],
        recommended_category_reductions=personalized_plan["recommended_category_reductions"],
        habit_challenges=personalized_plan["habit_challenges"],
    )

    return {
        "statement_id": statement.id,
        "filename": statement.filename,
        "simulation": personalized_plan["simulation"],
        "estimated_goal_costs": personalized_plan["estimated_goal_costs"],
        "goal_funding_plan": personalized_plan["goal_funding_plan"],
        "recommended_category_reductions": personalized_plan["recommended_category_reductions"],
        "habit_challenges": personalized_plan["habit_challenges"],
        "ai_explanation": explanation,
    }