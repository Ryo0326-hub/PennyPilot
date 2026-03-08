import io
import math
import re
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd

def _add_local_venv_site_packages():
    """
    Makes parser imports resilient when the API server is launched with a Python
    interpreter different from `backend/venv/bin/python`.
    """
    backend_root = Path(__file__).resolve().parents[2]
    site_packages_dirs = sorted((backend_root / "venv" / "lib").glob("python*/site-packages"))
    for directory in site_packages_dirs:
        directory_str = str(directory)
        if directory_str not in sys.path:
            sys.path.append(directory_str)


def _import_pdf_libs():
    pdfplumber_module = None
    pypdf_reader = None

    try:
        import pdfplumber as _pdfplumber  # type: ignore

        pdfplumber_module = _pdfplumber
    except ImportError:
        pass

    try:
        from pypdf import PdfReader as _PdfReader  # type: ignore

        pypdf_reader = _PdfReader
    except ImportError:
        pass

    if pdfplumber_module is None and pypdf_reader is None:
        _add_local_venv_site_packages()
        try:
            import pdfplumber as _pdfplumber  # type: ignore

            pdfplumber_module = _pdfplumber
        except ImportError:
            pass

        try:
            from pypdf import PdfReader as _PdfReader  # type: ignore

            pypdf_reader = _PdfReader
        except ImportError:
            pass

    return pdfplumber_module, pypdf_reader


pdfplumber, PdfReader = _import_pdf_libs()

MONTH_TO_NUM = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}

MONTH_ALIASES = {
    "JAN": 1,
    "JANUARY": 1,
    "FEB": 2,
    "FEBRUARY": 2,
    "MAR": 3,
    "MARCH": 3,
    "APR": 4,
    "APRIL": 4,
    "MAY": 5,
    "JUN": 6,
    "JUNE": 6,
    "JUL": 7,
    "JULY": 7,
    "AUG": 8,
    "AUGUST": 8,
    "SEP": 9,
    "SEPT": 9,
    "SEPTEMBER": 9,
    "OCT": 10,
    "OCTOBER": 10,
    "NOV": 11,
    "NOVEMBER": 11,
    "DEC": 12,
    "DECEMBER": 12,
}

STATEMENT_RANGE_RE = re.compile(
    r"STATEMENT\s+FROM\s+([A-Z]{3})\s+\d{1,2}\s+TO\s+([A-Z]{3})\s+\d{1,2},\s+(\d{4})",
    re.IGNORECASE,
)
STATEMENT_RANGE_RE_GENERIC = re.compile(
    r"(?:STATEMENT(?:\s+PERIOD)?\s*(?:FROM)?\s*)"
    r"([A-Z]{3,9})\s+\d{1,2}\s+TO\s+([A-Z]{3,9})\s+\d{1,2},\s+(\d{4})",
    re.IGNORECASE,
)

TRANSACTION_LINE_RE = re.compile(
    r"^(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{1,2})\s+"
    r"(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\s+(\d{1,2})\s+"
    r"(.+?)\s+(-?\$[\d,]+\.\d{2})$",
    re.IGNORECASE,
)

TRANSACTION_START_RE = re.compile(
    r"^([A-Z]{3,9})\s+(\d{1,2})\s+([A-Z]{3,9})\s+(\d{1,2})\s+(.+)$",
    re.IGNORECASE,
)
AMOUNT_END_RE = re.compile(r"(-?\$?\d[\d,]*\.\d{2})$")

KNOWN_SPEND_CATEGORIES = [
    "Health and Education",
    "Transportation",
    "Personal and Household Expenses",
    "Professional and Financial Services",
    "Retail and Grocery",
    "Hotel, Entertainment and Recreation",
    "Restaurants",
    "Travel",
    "Groceries",
]


def _clean_string(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).strip()


def _clean_amount(value) -> float:
    """
    Handles values like:
    54.21
    "$54.21"
    "-$256.71"
    "(54.21)"
    """
    if value is None:
        raise ValueError("Amount is missing")

    text = str(value).strip()
    text = text.replace(",", "").replace("$", "")

    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]

    return float(text)


def _is_payment_like(description: str) -> bool:
    lowered = description.lower()
    return (
        "payment" in lowered
        and "thank you" in lowered
        or "paiement" in lowered
        or "payment received" in lowered
    )


def _normalize_direction(amount: float) -> str:
    return "credit" if amount < 0 else "debit"


def _extract_merchant(description: str) -> str:
    """
    Very simple first-pass merchant extraction:
    take the first chunk before extra symbols/details.
    """
    if not description:
        return "UNKNOWN"

    simplified = description.split("  ")[0]
    simplified = simplified.split("/")[0]
    simplified = simplified.strip()

    if len(simplified) > 40:
        simplified = simplified[:40].strip()

    return simplified or "UNKNOWN"


def _normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _infer_statement_years(statement_text: str) -> tuple[int, int, int, int]:
    """
    Returns (start_month, end_month, start_year, end_year).
    """
    match = STATEMENT_RANGE_RE.search(statement_text)
    if not match:
        match = STATEMENT_RANGE_RE_GENERIC.search(statement_text)
    if not match:
        current_year = datetime.now().year
        return 1, 12, current_year, current_year

    start_month_code = match.group(1).upper()
    end_month_code = match.group(2).upper()
    end_year = int(match.group(3))

    start_month = MONTH_ALIASES.get(start_month_code, 1)
    end_month = MONTH_ALIASES.get(end_month_code, 12)

    start_year = end_year if start_month <= end_month else end_year - 1
    return start_month, end_month, start_year, end_year


def _year_for_month(
    month_num: int, start_month: int, end_month: int, start_year: int, end_year: int
) -> int:
    if start_year == end_year:
        return end_year

    # Statement spans year boundary (e.g., Dec -> Jan).
    if month_num >= start_month:
        return start_year
    if month_num <= end_month:
        return end_year
    return end_year


def parse_transactions_csv(file_bytes: bytes):
    """
    Expected CSV columns for this milestone:
    - date
    - description
    - amount

    Example:
    date,description,amount
    2026-02-01,WALMART,54.21
    2026-02-02,UBER EATS,23.11
    """
    decoded = file_bytes.decode("utf-8-sig")
    df = pd.read_csv(io.StringIO(decoded))

    required_columns = {"date", "description", "amount"}
    missing = required_columns - set(df.columns.str.lower())

    # Make column lookup case-insensitive
    lower_to_original = {col.lower(): col for col in df.columns}

    if missing:
        raise ValueError(
            f"CSV is missing required columns: {', '.join(sorted(missing))}"
        )

    date_col = lower_to_original["date"]
    description_col = lower_to_original["description"]
    amount_col = lower_to_original["amount"]

    transactions = []

    for _, row in df.iterrows():
        date = _clean_string(row[date_col])
        description = _clean_string(row[description_col])

        if not date and not description:
            continue

        amount = _clean_amount(row[amount_col])
        merchant = _extract_merchant(description)
        direction = _normalize_direction(amount)

        transactions.append(
            {
                "date": date,
                "merchant": merchant,
                "description": description,
                "amount": amount,
                "direction": direction,
            }
        )

    return transactions


def _parse_pdf_with_pdfplumber(file_bytes: bytes):
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        page_texts = [page.extract_text() or "" for page in pdf.pages]
        pages = list(pdf.pages)
    full_text = "\n".join(page_texts)
    start_month, end_month, start_year, end_year = _infer_statement_years(full_text)
    transactions = []
    for page in pages:
        words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
        table_words = [
            word for word in words if float(word["x0"]) < 390
        ]  # ignore right-side statement details

        table_words.sort(key=lambda word: (float(word["top"]), float(word["x0"])))

        rows: list[list[dict]] = []
        for word in table_words:
            if not rows:
                rows.append([word])
                continue

            prev_top = float(rows[-1][0]["top"])
            current_top = float(word["top"])
            if abs(current_top - prev_top) <= 2.2:
                rows[-1].append(word)
            else:
                rows.append([word])

        for row in rows:
            ordered = sorted(row, key=lambda word: float(word["x0"]))
            tokens = [_clean_string(word["text"]) for word in ordered]
            tokens = [token for token in tokens if token]

            if len(tokens) < 6:
                continue

            if tokens[0].upper() not in MONTH_TO_NUM:
                continue
            if tokens[2].upper() not in MONTH_TO_NUM:
                continue
            if not tokens[1].isdigit() or not tokens[3].isdigit():
                continue

            amount_index = None
            for i in range(len(tokens) - 1, -1, -1):
                if re.fullmatch(r"-?\$[\d,]+\.\d{2}", tokens[i]):
                    amount_index = i
                    break

            if amount_index is None or amount_index <= 4:
                continue

            activity_month = tokens[0].upper()
            activity_day = int(tokens[1])
            description = _normalize_spaces(" ".join(tokens[4:amount_index]))
            amount_text = tokens[amount_index]

            month_num = MONTH_TO_NUM[activity_month]
            year = _year_for_month(
                month_num=month_num,
                start_month=start_month,
                end_month=end_month,
                start_year=start_year,
                end_year=end_year,
            )

            iso_date = f"{year:04d}-{month_num:02d}-{activity_day:02d}"
            amount = _clean_amount(amount_text)

            transactions.append(
                {
                    "date": iso_date,
                    "merchant": _extract_merchant(description),
                    "description": description,
                    "amount": amount,
                    "direction": _normalize_direction(amount),
                }
            )
    return transactions


def _parse_pdf_from_text_pages(page_texts: list[str]):
    full_text = "\n".join(page_texts)
    start_month, end_month, start_year, end_year = _infer_statement_years(full_text)
    transactions = []
    for text in page_texts:
        pending: dict | None = None
        section = ""
        for raw_line in text.splitlines():
            line = _normalize_spaces(raw_line)
            if not line:
                continue

            upper_line = line.upper()
            if "YOUR PAYMENTS" in upper_line:
                section = "payments"
            elif "YOUR NEW CHARGES" in upper_line or "TRANSACTIONS" in upper_line:
                section = "charges"

            start_match = TRANSACTION_START_RE.match(line)
            if start_match:
                month_1 = start_match.group(1).upper()
                month_2 = start_match.group(3).upper()
                if month_1 not in MONTH_ALIASES or month_2 not in MONTH_ALIASES:
                    continue
                pending = {
                    "month": month_1,
                    "day": int(start_match.group(2)),
                    "description": start_match.group(5).strip(),
                    "section": section,
                }

                amount_inline = AMOUNT_END_RE.search(pending["description"])
                if amount_inline:
                    amount_text = amount_inline.group(1)
                    description = pending["description"][: amount_inline.start()].strip()
                    for category in KNOWN_SPEND_CATEGORIES:
                        if description.endswith(category):
                            description = description[: -len(category)].strip()
                            break
                    month_num = MONTH_ALIASES[pending["month"]]
                    year = _year_for_month(
                        month_num=month_num,
                        start_month=start_month,
                        end_month=end_month,
                        start_year=start_year,
                        end_year=end_year,
                    )
                    iso_date = f"{year:04d}-{month_num:02d}-{pending['day']:02d}"
                    amount = _clean_amount(amount_text)
                    if pending["section"] == "payments" or _is_payment_like(description):
                        amount = -abs(amount)
                    transactions.append(
                        {
                            "date": iso_date,
                            "merchant": _extract_merchant(description),
                            "description": description,
                            "amount": amount,
                            "direction": _normalize_direction(amount),
                        }
                    )
                    pending = None
                continue

            if pending is None:
                continue

            if re.fullmatch(r"\d{12,}", line):
                continue
            if line.upper().startswith("FOREIGN CURRENCY"):
                continue

            amount_match = re.fullmatch(r"-?\$?\d[\d,]*\.\d{2}", line)
            if amount_match:
                month_num = MONTH_ALIASES[pending["month"]]
                year = _year_for_month(
                    month_num=month_num,
                    start_month=start_month,
                    end_month=end_month,
                    start_year=start_year,
                    end_year=end_year,
                )
                iso_date = f"{year:04d}-{month_num:02d}-{pending['day']:02d}"
                amount = _clean_amount(amount_match.group(0))
                description = _normalize_spaces(pending["description"])
                for category in KNOWN_SPEND_CATEGORIES:
                    if description.endswith(category):
                        description = description[: -len(category)].strip()
                        break
                if pending["section"] == "payments" or _is_payment_like(description):
                    amount = -abs(amount)
                transactions.append(
                    {
                        "date": iso_date,
                        "merchant": _extract_merchant(description),
                        "description": description,
                        "amount": amount,
                        "direction": _normalize_direction(amount),
                    }
                )
                pending = None
                continue

            # Some statements wrap merchant names across multiple lines.
            if not TRANSACTION_START_RE.match(line):
                pending["description"] = f"{pending['description']} {line}".strip()

    return transactions


def parse_transactions_pdf(file_bytes: bytes):
    transactions = []
    if pdfplumber is not None:
        transactions = _parse_pdf_with_pdfplumber(file_bytes)
        if not transactions:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                page_texts = [page.extract_text() or "" for page in pdf.pages]
            transactions = _parse_pdf_from_text_pages(page_texts)
    elif PdfReader is not None:
        reader = PdfReader(io.BytesIO(file_bytes))
        page_texts = [page.extract_text() or "" for page in reader.pages]
        transactions = _parse_pdf_from_text_pages(page_texts)
    else:
        raise ValueError(
            "PDF parsing dependency is missing. Install pdfplumber or pypdf to enable PDF uploads."
        )

    if not transactions:
        raise ValueError(
            "No transactions found in PDF. Ensure the statement includes a readable transaction table."
        )

    return transactions
