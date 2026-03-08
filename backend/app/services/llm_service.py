import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"


def generate_spending_insights(summary: dict) -> str:
    prompt = f"""
You are an AI personal finance assistant.

Analyze the user's credit card statement summary and provide helpful advice.

Write the response in 3 sections:

Spending Overview
Key Patterns
Suggestions

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