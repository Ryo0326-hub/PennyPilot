from datetime import date, timedelta

import app.services.goal_estimator as goal_estimator
from app.services.personalized_plan import build_personalized_plan


def test_estimate_goal_costs_uses_web_ai_path(monkeypatch):
    monkeypatch.setattr(goal_estimator, "ENABLE_WEB_GOAL_ESTIMATION", True)
    monkeypatch.setattr(goal_estimator, "_collect_duckduckgo_snippets", lambda _query: ["sample"])
    monkeypatch.setattr(
        goal_estimator,
        "_estimate_amount_with_ai",
        lambda _goal_text, _snippets: {
            "estimated_amount": 1234.56,
            "confidence": "medium",
            "rationale": "Derived from sample web snippets.",
        },
    )

    result = goal_estimator.estimate_goal_costs([{"name": "Sony camera lens"}])

    assert len(result) == 1
    assert result[0]["estimated_amount"] == 1234.56
    assert result[0]["source"] == "web_estimate"
    assert result[0]["confidence"] == "medium"


def test_build_personalized_plan_defaults_to_12_month_horizon(monkeypatch):
    monkeypatch.setattr(
        "app.services.personalized_plan.estimate_goal_costs",
        lambda _goals: [
            {
                "name": "Camera lens",
                "description": None,
                "estimated_amount": 1200.0,
                "source": "fallback_estimate",
                "confidence": "low",
                "rationale": "Fallback",
                "target_date": None,
            }
        ],
    )
    summary = {
        "total_spent": 1500.0,
        "category_totals": [
            {"category": "restaurants", "total": 500.0},
            {"category": "subscriptions", "total": 200.0},
            {"category": "shopping", "total": 300.0},
        ],
    }

    result = build_personalized_plan(summary=summary, goals=[{"name": "Camera lens"}])

    assert result["goal_funding_plan"]["goals"][0]["horizon_months"] == 12
    assert result["goal_funding_plan"]["goals"][0]["required_monthly_savings"] == 100.0


def test_build_personalized_plan_marks_infeasible_when_shortfall_exists(monkeypatch):
    near_date = (date.today() + timedelta(days=10)).isoformat()
    monkeypatch.setattr(
        "app.services.personalized_plan.estimate_goal_costs",
        lambda _goals: [
            {
                "name": "Big vacation",
                "description": None,
                "estimated_amount": 15000.0,
                "source": "web_estimate",
                "confidence": "medium",
                "rationale": "Estimated",
                "target_date": near_date,
            }
        ],
    )
    summary = {
        "total_spent": 450.0,
        "category_totals": [
            {"category": "restaurants", "total": 120.0},
            {"category": "subscriptions", "total": 40.0},
            {"category": "shopping", "total": 60.0},
            {"category": "groceries", "total": 150.0},
            {"category": "transport", "total": 80.0},
        ],
    }

    result = build_personalized_plan(summary=summary, goals=[{"name": "Big vacation"}])

    assert result["goal_funding_plan"]["feasible"] is False
    assert result["goal_funding_plan"]["monthly_shortfall"] > 0
