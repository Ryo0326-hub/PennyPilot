from collections import defaultdict
from typing import Any


def build_statement_summary(statement) -> dict[str, Any]:
    """
    Builds a summary from a Statement SQLAlchemy object.

    Rules for this milestone:
    - 'Spending' means debit transactions only
    - credit transactions are excluded from total spending/category totals
    """

    debit_transactions = [tx for tx in statement.transactions if tx.direction == "debit"]

    total_spent = round(sum(tx.amount for tx in debit_transactions), 2)

    category_totals_map = defaultdict(float)
    merchant_totals_map = defaultdict(float)

    for tx in debit_transactions:
        category_totals_map[tx.category] += tx.amount
        merchant_totals_map[tx.merchant] += tx.amount

    category_totals = [
        {
            "category": category,
            "total": round(total, 2),
        }
        for category, total in sorted(
            category_totals_map.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

    top_merchants = [
        {
            "merchant": merchant,
            "total": round(total, 2),
        }
        for merchant, total in sorted(
            merchant_totals_map.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ][:5]

    transaction_count = len(statement.transactions)
    debit_count = len(debit_transactions)
    credit_count = transaction_count - debit_count

    return {
        "statement_id": statement.id,
        "filename": statement.filename,
        "total_spent": total_spent,
        "transaction_count": transaction_count,
        "debit_count": debit_count,
        "credit_count": credit_count,
        "category_totals": category_totals,
        "top_merchants": top_merchants,
    }