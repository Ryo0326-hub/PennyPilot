from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.parse import quote_plus
from urllib.request import urlopen

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-2.5-flash"
ENABLE_WEB_GOAL_ESTIMATION = (
    os.getenv("ENABLE_WEB_GOAL_ESTIMATION", "true").strip().lower() == "true"
)

_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=_api_key) if _api_key else None


def _collect_duckduckgo_snippets(query: str) -> list[str]:
    endpoint = (
        "https://api.duckduckgo.com/?q="
        f"{quote_plus(query)}&format=json&no_redirect=1&no_html=1"
    )
    snippets: list[str] = []
    try:
        with urlopen(endpoint, timeout=4) as response:  # nosec B310
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return snippets

    abstract = str(payload.get("AbstractText", "")).strip()
    if abstract:
        snippets.append(abstract)

    related_topics = payload.get("RelatedTopics", [])
    for item in related_topics:
        if isinstance(item, dict) and "Text" in item:
            text = str(item.get("Text", "")).strip()
            if text:
                snippets.append(text)
        elif isinstance(item, dict) and "Topics" in item:
            nested = item.get("Topics", [])
            for nested_item in nested:
                text = str(nested_item.get("Text", "")).strip()
                if text:
                    snippets.append(text)
        if len(snippets) >= 4:
            break

    return snippets[:4]


def _fallback_amount_from_keywords(goal_text: str) -> float:
    normalized = goal_text.lower()
    defaults = {
        "lens": 1200.0,
        "camera": 1500.0,
        "vacation": 2500.0,
        "trip": 2200.0,
        "travel": 2400.0,
        "laptop": 1400.0,
        "phone": 900.0,
        "wedding": 5000.0,
    }
    for keyword, amount in defaults.items():
        if keyword in normalized:
            return amount
    return 1000.0


def _extract_json_block(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _estimate_amount_with_ai(goal_text: str, snippets: list[str]) -> dict[str, Any] | None:
    if not client:
        return None

    context = "\n".join(f"- {snippet}" for snippet in snippets) if snippets else "- (none)"
    prompt = f"""
You are estimating a realistic USD budget for a personal finance goal.
Use the goal text and web snippets as context.

Goal:
{goal_text}

Web snippets:
{context}

Return STRICT JSON only:
{{
  "estimated_amount": number,
  "confidence": "high" | "medium" | "low",
  "rationale": "short explanation"
}}

Rules:
- Use USD.
- If the goal is broad, choose a conservative mid-range estimate.
- Do not include markdown or extra keys.
"""
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
    except Exception:
        return None

    if not response.text:
        return None

    parsed = _extract_json_block(response.text)
    if not parsed:
        return None

    amount = parsed.get("estimated_amount")
    if not isinstance(amount, (int, float)) or amount <= 0:
        return None

    confidence = str(parsed.get("confidence", "low")).lower()
    if confidence not in {"high", "medium", "low"}:
        confidence = "low"

    rationale = str(parsed.get("rationale", "Estimated from available context.")).strip()
    return {
        "estimated_amount": float(amount),
        "confidence": confidence,
        "rationale": rationale,
    }


def estimate_goal_costs(goals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    estimated: list[dict[str, Any]] = []

    for goal in goals:
        name = str(goal.get("name", "")).strip()
        description = goal.get("description")
        goal_text = f"{name}. {description or ''}".strip()
        target_amount = goal.get("target_amount")
        target_date = goal.get("target_date")

        if isinstance(target_amount, (int, float)) and target_amount > 0:
            estimated.append(
                {
                    "name": name,
                    "description": description,
                    "estimated_amount": round(float(target_amount), 2),
                    "source": "user_input",
                    "confidence": "high",
                    "rationale": "Amount provided by user.",
                    "target_date": target_date,
                }
            )
            continue

        snippets = _collect_duckduckgo_snippets(goal_text) if ENABLE_WEB_GOAL_ESTIMATION else []
        ai_estimate = _estimate_amount_with_ai(goal_text, snippets)

        if ai_estimate:
            estimated.append(
                {
                    "name": name,
                    "description": description,
                    "estimated_amount": round(ai_estimate["estimated_amount"], 2),
                    "source": "web_estimate" if snippets else "fallback_estimate",
                    "confidence": ai_estimate["confidence"],
                    "rationale": ai_estimate["rationale"],
                    "target_date": target_date,
                }
            )
            continue

        fallback = _fallback_amount_from_keywords(goal_text)
        estimated.append(
            {
                "name": name,
                "description": description,
                "estimated_amount": round(fallback, 2),
                "source": "fallback_estimate",
                "confidence": "low",
                "rationale": "Used default estimate because web/AI estimation was unavailable.",
                "target_date": target_date,
            }
        )

    return estimated
