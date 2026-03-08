from __future__ import annotations

from datetime import date, datetime
from math import ceil
from typing import Any

from app.services.goal_estimator import estimate_goal_costs
from app.services.simulator import build_simulation

DEFAULT_HORIZON_MONTHS = 12

_CATEGORY_PRIORITY = {
    "subscriptions": 1,
    "restaurants": 2,
    "shopping": 3,
    "entertainment": 4,
    "travel": 5,
    "groceries": 6,
    "transport": 7,
    "miscellaneous": 8,
}

_CATEGORY_MAX_REDUCTION = {
    "subscriptions": 0.7,
    "restaurants": 0.6,
    "shopping": 0.55,
    "entertainment": 0.5,
    "travel": 0.35,
    "groceries": 0.2,
    "transport": 0.2,
    "miscellaneous": 0.25,
}


def _months_until(target_date: str | None) -> int:
    if not target_date:
        return DEFAULT_HORIZON_MONTHS

    try:
        parsed = datetime.fromisoformat(target_date).date()
    except ValueError:
        return DEFAULT_HORIZON_MONTHS

    delta_days = (parsed - date.today()).days
    if delta_days <= 0:
        return 1
    return max(1, ceil(delta_days / 30))


def _allocate_category_reductions(
    category_totals: list[dict[str, Any]],
    required_monthly_savings: float,
) -> tuple[list[dict[str, Any]], float]:
    candidates = []
    for item in category_totals:
        category = str(item.get("category", "")).lower()
        total = float(item.get("total", 0))
        priority = _CATEGORY_PRIORITY.get(category, 99)
        max_reduction_pct = _CATEGORY_MAX_REDUCTION.get(category, 0.15)
        max_reduction_amount = round(total * max_reduction_pct, 2)
        candidates.append(
            {
                "category": category,
                "current_monthly_spend": round(total, 2),
                "priority": priority,
                "max_reduction_pct": max_reduction_pct,
                "max_reduction_amount": max_reduction_amount,
            }
        )

    candidates.sort(key=lambda x: (x["priority"], -x["current_monthly_spend"]))
    remaining = round(required_monthly_savings, 2)
    recommendations: list[dict[str, Any]] = []

    for candidate in candidates:
        if remaining <= 0:
            break

        reduction = min(candidate["max_reduction_amount"], remaining)
        if reduction <= 0:
            continue

        current_spend = candidate["current_monthly_spend"]
        reduction_pct = round((reduction / current_spend) * 100, 2) if current_spend else 0.0
        recommendations.append(
            {
                "category": candidate["category"],
                "current_monthly_spend": current_spend,
                "recommended_reduction_amount": round(reduction, 2),
                "recommended_reduction_pct": reduction_pct,
                "projected_monthly_spend": round(current_spend - reduction, 2),
                "priority": candidate["priority"],
            }
        )
        remaining = round(remaining - reduction, 2)

    return recommendations, max(0.0, round(remaining, 2))


def _build_habit_challenges(
    goals: list[dict[str, Any]],
    recommendations: list[dict[str, Any]],
) -> list[str]:
    challenges: list[str] = []
    if goals:
        goal_names = ", ".join(goal["name"] for goal in goals[:2])
        challenges.append(
            f"Set up an automatic weekly transfer dedicated to: {goal_names}."
        )

    for recommendation in recommendations[:3]:
        category = recommendation["category"]
        reduction = recommendation["recommended_reduction_amount"]
        if category == "restaurants":
            challenges.append(
                f"Do a 5-day home-cooked streak this week to save about ${round(reduction / 4, 2)}."
            )
        elif category == "subscriptions":
            challenges.append("Cancel or pause one unused subscription before Sunday.")
        elif category == "shopping":
            challenges.append("Run a 72-hour wait rule on all non-essential purchases this week.")
        else:
            challenges.append(
                f"Cap {category} spending this week to stay on track with your monthly reduction target."
            )

    while len(challenges) < 3:
        challenges.append("Track every discretionary purchase for 7 straight days.")

    return challenges[:5]


def build_personalized_plan(
    summary: dict[str, Any],
    goals: list[dict[str, Any]],
    strategy_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    estimated_goal_costs = estimate_goal_costs(goals)
    funding_goals: list[dict[str, Any]] = []

    total_goal_amount = 0.0
    required_monthly_savings = 0.0
    for goal in estimated_goal_costs:
        horizon_months = _months_until(goal.get("target_date"))
        estimated_amount = float(goal["estimated_amount"])
        monthly_needed = round(estimated_amount / horizon_months, 2)

        funding_goals.append(
            {
                "name": goal["name"],
                "estimated_amount": round(estimated_amount, 2),
                "target_date": goal.get("target_date"),
                "horizon_months": horizon_months,
                "required_monthly_savings": monthly_needed,
            }
        )
        goal["horizon_months"] = horizon_months
        total_goal_amount += estimated_amount
        required_monthly_savings += monthly_needed

    required_monthly_savings = round(required_monthly_savings, 2)
    recommendations, shortfall = _allocate_category_reductions(
        summary.get("category_totals", []),
        required_monthly_savings,
    )

    auto_strategy = {
        "restaurants_reduction_pct": 0.0,
        "subscriptions_reduction_pct": 0.0,
        "shopping_reduction_pct": 0.0,
    }
    for recommendation in recommendations:
        category = recommendation["category"]
        reduction_pct = recommendation["recommended_reduction_pct"]
        if category == "restaurants":
            auto_strategy["restaurants_reduction_pct"] = reduction_pct
        elif category == "subscriptions":
            auto_strategy["subscriptions_reduction_pct"] = reduction_pct
        elif category == "shopping":
            auto_strategy["shopping_reduction_pct"] = reduction_pct

    simulation_strategy = strategy_override or auto_strategy
    simulation = build_simulation(summary, simulation_strategy)
    projected_monthly_savings = round(
        sum(item["recommended_reduction_amount"] for item in recommendations), 2
    )

    habit_challenges = _build_habit_challenges(estimated_goal_costs, recommendations)

    return {
        "simulation": simulation,
        "estimated_goal_costs": estimated_goal_costs,
        "goal_funding_plan": {
            "total_goal_amount": round(total_goal_amount, 2),
            "required_monthly_savings": required_monthly_savings,
            "projected_monthly_savings": projected_monthly_savings,
            "projected_annual_savings": round(projected_monthly_savings * 12, 2),
            "monthly_shortfall": shortfall,
            "feasible": shortfall <= 0.0,
            "goals": funding_goals,
        },
        "recommended_category_reductions": recommendations,
        "recommended_strategy": auto_strategy,
        "habit_challenges": habit_challenges,
    }
