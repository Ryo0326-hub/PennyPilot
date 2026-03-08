def categorize_transaction(description: str, amount: float) -> str:
    text = (description or "").lower().strip()

    # Payments / credit card payments
    if (
        "payment thank you" in text
        or "payment received" in text
        or text.startswith("payment ")
    ):
        return "payments"

    # Income / refunds / credits
    if amount < 0 and (
        "refund" in text
        or "deposit" in text
        or "salary" in text
        or "payroll" in text
        or "etransfer" in text
        or "e-transfer" in text
        or "interac" in text
    ):
        return "income"

    # Restaurants / cafes / food delivery
    restaurant_keywords = [
        "uber eats",
        "doordash",
        "skip",
        "skipthe",
        "mcdonald",
        "starbucks",
        "tim hortons",
        "subway",
        "restaurant",
        "pizza",
        "kfc",
        "a&w",
        "wendy",
        "burger",
        "cafe",
        "coffee",
        "flock stop",
        "freshslice",
        "pepis",
        "pepis pizza",
        "java time",
        "wusa",
        "brubakers",
        "shawarma",
    ]
    if any(keyword in text for keyword in restaurant_keywords):
        return "restaurants"

    # Groceries
    grocery_keywords = [
        "walmart",
        "costco",
        "t&t",
        "t & t",
        "nofrills",
        "no frills",
        "loblaws",
        "freshco",
        "food basics",
        "metro",
        "superstore",
        "grocery",
        "zehrs",
        "sobeys",
        "farm boy",
    ]
    if any(keyword in text for keyword in grocery_keywords):
        return "groceries"

    # Subscriptions / software
    subscription_keywords = [
        "netflix",
        "spotify",
        "apple.com/bill",
        "youtube premium",
        "disney",
        "amazon prime",
        "chatgpt",
        "openai",
        "notion",
        "canva",
        "google one",
        "icloud",
        "dropbox",
        "adobe",
        "microsoft 365",
        "nvidia",
    ]
    if any(keyword in text for keyword in subscription_keywords):
        return "subscriptions"

    # Transportation
    transport_keywords = [
        "uber trip",
        "uber",
        "lyft",
        "go transit",
        "presto",
        "shell",
        "esso",
        "petro",
        "petro-canada",
        "gas",
        "transit",
        "flixbus",
        "busbud",
        "via rail",
    ]
    if any(keyword in text for keyword in transport_keywords):
        return "transportation"

    # Telecom / phone bills
    telecom_keywords = [
        "virgin plus",
        "virgin mobile",
        "rogers",
        "bell",
        "fido",
        "telus",
        "koodo",
        "freedom mobile",
    ]
    if any(keyword in text for keyword in telecom_keywords):
        return "telecom"

    # Health / pharmacy / fitness
    health_keywords = [
        "shoppers drug mart",
        "rexall",
        "pharmacy",
        "guardian drug",
        "uw athletics",
        "athletics",
        "gym",
        "fitness",
    ]
    if any(keyword in text for keyword in health_keywords):
        return "health"

    # Shopping / retail
    shopping_keywords = [
        "amazon",
        "best buy",
        "uniqlo",
        "h&m",
        "indigo",
        "winners",
        "ikea",
        "shop",
        "canadian tire",
        "dollarama",
        "muji",
    ]
    if any(keyword in text for keyword in shopping_keywords):
        return "shopping"

    # If none matched
    return "other"