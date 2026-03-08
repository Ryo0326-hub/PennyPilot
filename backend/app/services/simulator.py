from typing import Any


def build_simulation(summary: dict, strategy: dict) -> dict[str, Any]:
    """
    Simulates category reductions using summary.category_totals.

    strategy example:
    {
        "restaurants": 40,
        "subscriptions": 20,
        "shopping": 25
    }
    """

    category_lookup = {
        item["category"]: item["total"]
        for item in summary["category_totals"]
    }

    applied_strategy: dict[str, float] = {}
    savings_by_category: dict[str, float] = {}
    total_monthly_savings = 0.0

    for category, total in category_lookup.items():
        # Backward-compatible support for legacy strategy keys.
        raw_pct = strategy.get(category, strategy.get(f"{category}_reduction_pct", 0))
        reduction_pct = round(max(0, min(float(raw_pct), 100)), 2)
        savings = round(total * (reduction_pct / 100), 2)
        applied_strategy[category] = reduction_pct
        savings_by_category[category] = savings
        total_monthly_savings += savings

    total_monthly_savings = round(total_monthly_savings, 2)

    projected_spending = round(summary["total_spent"] - total_monthly_savings, 2)
    annual_savings = round(total_monthly_savings * 12, 2)

    updated_category_totals = []
    for item in summary["category_totals"]:
        category = item["category"]
        total = item["total"]
        new_total = round(total - savings_by_category.get(category, 0.0), 2)

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
        "applied_strategy": applied_strategy,
        "updated_category_totals": updated_category_totals,
    }