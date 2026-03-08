import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"


def generate_simulation_insight(simulation: dict) -> str:
    prompt = f"""
You are an AI financial advisor.

A spending reduction strategy was simulated for a user's credit card statement.

Explain the result in a clear and helpful way.

Simulation results:

Original monthly spending: {simulation["original_total_spent"]}
Projected spending after strategy: {simulation["projected_total_spent"]}

Monthly savings: {simulation["monthly_savings"]}
Annual savings: {simulation["annual_savings"]}

Applied strategy:
Restaurants reduction: {simulation["applied_strategy"]["restaurants_reduction_pct"]}%
Subscriptions reduction: {simulation["applied_strategy"]["subscriptions_reduction_pct"]}%
Shopping reduction: {simulation["applied_strategy"]["shopping_reduction_pct"]}%

Category results:
{simulation["updated_category_totals"]}

Write a short explanation with:

Strategy Impact
Where Savings Come From
Practical Advice

Keep the response concise and realistic.
Do not invent numbers.
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        return f"AI simulation explanation unavailable: {str(e)}"