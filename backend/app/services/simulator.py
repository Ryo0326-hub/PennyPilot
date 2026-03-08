from typing import Any


def build_simulation(summary: dict, strategy: dict) -> dict[str, Any]:
    """
    Simulates category reductions using summary.category_totals.

    strategy example:
    {
        "restaurants_reduction_pct": 40,
        "subscriptions_reduction_pct": 20,
        "shopping_reduction_pct": 25
    }
    """

    category_lookup = {
        item["category"]: item["total"]
        for item in summary["category_totals"]
    }

    restaurants_total = category_lookup.get("restaurants", 0.0)
    subscriptions_total = category_lookup.get("subscriptions", 0.0)
    shopping_total = category_lookup.get("shopping", 0.0)

    restaurants_pct = max(0, min(strategy.get("restaurants_reduction_pct", 0), 100))
    subscriptions_pct = max(0, min(strategy.get("subscriptions_reduction_pct", 0), 100))
    shopping_pct = max(0, min(strategy.get("shopping_reduction_pct", 0), 100))

    restaurants_savings = round(restaurants_total * (restaurants_pct / 100), 2)
    subscriptions_savings = round(subscriptions_total * (subscriptions_pct / 100), 2)
    shopping_savings = round(shopping_total * (shopping_pct / 100), 2)

    total_monthly_savings = round(
        restaurants_savings + subscriptions_savings + shopping_savings, 2
    )

    projected_spending = round(summary["total_spent"] - total_monthly_savings, 2)
    annual_savings = round(total_monthly_savings * 12, 2)

    updated_category_totals = []
    for item in summary["category_totals"]:
        category = item["category"]
        total = item["total"]

        if category == "restaurants":
            new_total = round(total - restaurants_savings, 2)
        elif category == "subscriptions":
            new_total = round(total - subscriptions_savings, 2)
        elif category == "shopping":
            new_total = round(total - shopping_savings, 2)
        else:
            new_total = total

        updated_category_totals.append(
            {
                "category": category,
                "original_total": total,
                "projected_total": new_total,
            }
        )

    return {
        "original_total_spent": summary["total_spent"],
        "projected_total_spent": projected_spending,
        "monthly_savings": total_monthly_savings,
        "annual_savings": annual_savings,
        "applied_strategy": {
            "restaurants_reduction_pct": restaurants_pct,
            "subscriptions_reduction_pct": subscriptions_pct,
            "shopping_reduction_pct": shopping_pct,
        },
        "updated_category_totals": updated_category_totals,
    }