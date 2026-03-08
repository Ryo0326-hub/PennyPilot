from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Statement, Transaction
from app.schemas.transaction import ParseResponse
from app.services.categorizer import categorize_transaction
from app.services.parser import parse_transactions_csv, parse_transactions_pdf

router = APIRouter(prefix="/upload", tags=["upload"])


def _parse_by_extension(filename: str, content: bytes):
    lower = filename.lower()
    if lower.endswith(".csv"):
        return parse_transactions_csv(content)
    if lower.endswith(".pdf"):
        return parse_transactions_pdf(content)
    raise ValueError("Only CSV and PDF files are supported")


async def _ingest_uploaded_statement(file: UploadFile, db: Session) -> ParseResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        content = await file.read()
        parsed_transactions = _parse_by_extension(file.filename, content)

        categorized_transactions = []
        for tx in parsed_transactions:
            category = categorize_transaction(tx["description"], tx["amount"])
            tx["category"] = category
            categorized_transactions.append(tx)

        statement = Statement(filename=file.filename)
        db.add(statement)
        db.commit()
        db.refresh(statement)

        for tx in categorized_transactions:
            transaction = Transaction(
                statement_id=statement.id,
                date=tx["date"],
                merchant=tx["merchant"],
                description=tx["description"],
                amount=tx["amount"],
                direction=tx["direction"],
                category=tx["category"],
            )
            db.add(transaction)

        db.commit()

        return ParseResponse(
            filename=file.filename,
            statement_id=statement.id,
            row_count=len(categorized_transactions),
            transactions=categorized_transactions,
        )

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")


@router.post("/statement", response_model=ParseResponse)
async def upload_statement(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await _ingest_uploaded_statement(file=file, db=db)


@router.post("/csv", response_model=ParseResponse)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await _ingest_uploaded_statement(file=file, db=db)
