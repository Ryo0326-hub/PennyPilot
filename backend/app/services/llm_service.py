import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"


def _format_category_list(categories: list[str]) -> str:
    if not categories:
        return "your top categories"
    if len(categories) == 1:
        return categories[0]
    if len(categories) == 2:
        return f"{categories[0]} and {categories[1]}"
    return f"{categories[0]}, {categories[1]}, and {categories[2]}"


def generate_spending_insights(summary: dict) -> str:
    top_categories = [
        item["category"]
        for item in sorted(
            summary.get("category_totals", []),
            key=lambda item: item.get("total", 0),
            reverse=True,
        )[:3]
    ]
    top_categories_text = _format_category_list(top_categories)

    prompt = f"""
You are an AI personal finance assistant.

Analyze the user's credit card statement summary and provide helpful advice.

Write the response in 3 sections:

Spending Overview
Key Patterns
Suggestions

Critical formatting rules:
- In "Spending Overview", write 2 short paragraphs only (no bullets, no numbered list).
- The second paragraph must end with this exact sentence pattern:
  "Your spending was primarily concentrated in {top_categories_text}."
- Mention only 2-3 categories in that concentration sentence.
- Keep the existing style for "Key Patterns" and "Suggestions" (bullets are allowed there).
- In "Key Patterns", include top merchant ranking (Top 3 merchants in order).

Data:

Filename: {summary["filename"]}
Total spent: {summary["total_spent"]}
Transaction count: {summary["transaction_count"]}
Debit count: {summary["debit_count"]}
Credit count: {summary["credit_count"]}

Category totals:
{summary["category_totals"]}

Top merchants:
{summary["top_merchants"]}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )

        return response.text.strip()

    except Exception as e:
        return f"AI insights unavailable: {str(e)}"