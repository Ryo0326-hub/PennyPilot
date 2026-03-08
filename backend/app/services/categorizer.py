import re
from difflib import SequenceMatcher


# Common location / processing tokens that should not influence categorization.
NOISE_TOKENS = {
    "ca",
    "canada",
    "on",
    "bc",
    "ab",
    "qc",
    "mb",
    "sk",
    "ns",
    "nb",
    "nl",
    "pei",
    "waterloo",
    "toronto",
    "ottawa",
    "vancouver",
    "montreal",
    "mississauga",
    "calgary",
    "edmonton",
    "online",
    "purchase",
    "pos",
    "card",
    "debit",
    "credit",
    "visa",
    "mastercard",
    "auth",
    "authorization",
}

PAYMENT_KEYWORDS = {
    "payment thank you",
    "payment received",
    "bill payment",
}

INCOME_KEYWORDS = {
    "refund",
    "deposit",
    "salary",
    "payroll",
    "etransfer",
    "e transfer",
    "interac",
    "direct deposit",
}

# Category rules are intentionally split into:
# - phrase_keywords: exact phrase hits in normalized text (high confidence)
# - token_keywords: token-level hints (more flexible for new merchants/locations)
CATEGORY_RULES = {
    "restaurants": {
        "phrase_keywords": {
            "uber eats",
            "doordash",
            "skip the dishes",
            "tim hortons",
            "bubble tea",
            "fast food",
            "food delivery",
        },
        "token_keywords": {
            "restaurant",
            "pizza",
            "burger",
            "shawarma",
            "cafe",
            "coffee",
            "bakery",
            "bistro",
            "eatery",
            "kitchen",
            "sushi",
            "ramen",
            "grill",
        },
    },
    "groceries": {
        "phrase_keywords": {
            "no frills",
            "food basics",
            "freshco",
            "farm boy",
        },
        "token_keywords": {
            "grocery",
            "groceries",
            "market",
            "supermarket",
            "produce",
            "costco",
            "walmart",
            "loblaws",
            "metro",
            "sobeys",
            "superstore",
            "zehrs",
            "nofrills",
        },
    },
    "subscriptions": {
        "phrase_keywords": {
            "youtube premium",
            "amazon prime",
            "apple com bill",
            "google one",
            "microsoft 365",
        },
        "token_keywords": {
            "subscription",
            "recurring",
            "monthly",
            "netflix",
            "spotify",
            "disney",
            "openai",
            "chatgpt",
            "notion",
            "canva",
            "icloud",
            "dropbox",
            "adobe",
        },
    },
    "transportation": {
        "phrase_keywords": {
            "uber trip",
            "go transit",
            "via rail",
        },
        "token_keywords": {
            "uber",
            "lyft",
            "transit",
            "presto",
            "taxi",
            "train",
            "bus",
            "metro",
            "fuel",
            "gas",
            "shell",
            "esso",
            "petro",
            "parking",
            "toll",
        },
    },
    "telecom": {
        "phrase_keywords": {
            "virgin plus",
            "virgin mobile",
            "freedom mobile",
        },
        "token_keywords": {
            "rogers",
            "bell",
            "fido",
            "telus",
            "koodo",
            "mobile",
            "wireless",
            "internet",
            "broadband",
        },
    },
    "health": {
        "phrase_keywords": {
            "shoppers drug mart",
            "guardian drug",
            "walk in clinic",
            "health services",
            "medical center",
        },
        "token_keywords": {
            "health",
            "medical",
            "clinic",
            "doctor",
            "dental",
            "dentist",
            "pharmacy",
            "drug",
            "hospital",
            "physio",
            "chiro",
            "optical",
            "optometrist",
            "therapy",
            "wellness",
            "gym",
            "fitness",
            "athletics",
            "rexall",
        },
    },
    "shopping": {
        "phrase_keywords": {
            "canadian tire",
            "best buy",
        },
        "token_keywords": {
            "amazon",
            "shop",
            "store",
            "retail",
            "mall",
            "winners",
            "uniqlo",
            "hm",
            "indigo",
            "ikea",
            "dollarama",
            "muji",
        },
    },
}


def _normalize_text(text: str) -> str:
    cleaned = (text or "").lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _tokenize(normalized_text: str) -> list[str]:
    tokens = normalized_text.split()
    return [t for t in tokens if t and not t.isdigit() and t not in NOISE_TOKENS]


def _is_fuzzy_match(token: str, keyword: str, threshold: float = 0.88) -> bool:
    if abs(len(token) - len(keyword)) > 2:
        return False
    return SequenceMatcher(None, token, keyword).ratio() >= threshold


def _category_score(normalized_text: str, tokens: list[str], category: str) -> int:
    rules = CATEGORY_RULES[category]
    score = 0

    for phrase in rules["phrase_keywords"]:
        if phrase in normalized_text:
            score += 3

    token_keywords = rules["token_keywords"]
    matched_tokens = 0
    for token in tokens:
        if token in token_keywords:
            matched_tokens += 1
            continue

        # Helps with OCR and short merchant variations (ex: "pharmcy", "restarant")
        if len(token) >= 5 and any(_is_fuzzy_match(token, keyword) for keyword in token_keywords):
            matched_tokens += 1

    score += min(matched_tokens, 3)
    return score


def categorize_transaction(description: str, amount: float) -> str:
    normalized_text = _normalize_text(description)
    tokens = _tokenize(normalized_text)

    if (
        any(phrase in normalized_text for phrase in PAYMENT_KEYWORDS)
        or normalized_text.startswith("payment ")
    ):
        return "payments"

    if amount < 0 and any(keyword in normalized_text for keyword in INCOME_KEYWORDS):
        return "income"

    scored = []
    for category in CATEGORY_RULES:
        scored.append((category, _category_score(normalized_text, tokens, category)))

    # Prefer the category with the highest confidence score.
    best_category, best_score = max(scored, key=lambda item: item[1])
    return best_category if best_score > 0 else "other"