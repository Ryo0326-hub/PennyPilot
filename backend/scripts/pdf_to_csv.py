#!/usr/bin/env python3
import argparse
import csv
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a credit card statement PDF into normalized CSV rows."
    )
    parser.add_argument("pdf_path", help="Path to input PDF statement")
    parser.add_argument(
        "--out",
        dest="out_path",
        default=None,
        help="Optional output CSV path (default: same name as input with .csv)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf_path).expanduser()

    if not pdf_path.exists():
        print(f"File not found: {pdf_path}", file=sys.stderr)
        return 1

    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from app.services.parser import parse_transactions_pdf  # pylint: disable=import-outside-toplevel

    output_path = (
        Path(args.out_path).expanduser()
        if args.out_path
        else pdf_path.with_suffix(".csv")
    )

    transactions = parse_transactions_pdf(pdf_path.read_bytes())

    with output_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=["date", "description", "amount"])
        writer.writeheader()
        for tx in transactions:
            writer.writerow(
                {
                    "date": tx["date"],
                    "description": tx["description"],
                    "amount": tx["amount"],
                }
            )

    print(f"Wrote {len(transactions)} rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
