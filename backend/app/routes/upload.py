import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_id
from app.db.database import get_db
from app.db.models import Statement, Transaction
from app.schemas.transaction import ParseResponse
from app.services.categorizer import categorize_transaction
from app.services.parser import parse_transactions_csv, parse_transactions_pdf

router = APIRouter(prefix="/upload", tags=["upload"])

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
ALLOWED_EXTENSIONS = {".csv", ".pdf"}
ALLOWED_CONTENT_TYPES = {
    "text/csv",
    "application/csv",
    "application/pdf",
    "application/octet-stream",
}


def _parse_by_extension(filename: str, content: bytes):
    lower = filename.lower()
    if lower.endswith(".csv"):
        return parse_transactions_csv(content)
    if lower.endswith(".pdf"):
        return parse_transactions_pdf(content)
    raise ValueError("Only CSV and PDF files are supported")


def _validate_upload(file: UploadFile, content: bytes) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    lower = file.filename.lower()
    if not any(lower.endswith(ext) for ext in ALLOWED_EXTENSIONS):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    if not content:
        raise HTTPException(status_code=400, detail="File is empty")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large")


async def _ingest_uploaded_statement(file: UploadFile, db: Session, owner_id: str) -> ParseResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        content = await file.read()
        _validate_upload(file, content)
        parsed_transactions = _parse_by_extension(file.filename, content)

        categorized_transactions = []
        for tx in parsed_transactions:
            category = categorize_transaction(tx["description"], tx["amount"])
            tx["category"] = category
            categorized_transactions.append(tx)

        statement = Statement(filename=file.filename, owner_id=owner_id)
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

    except ValueError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid statement format")
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Upload processing failed")


@router.post("/statement", response_model=ParseResponse)
async def upload_statement(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return await _ingest_uploaded_statement(file=file, db=db, owner_id=user_id)


@router.post("/csv", response_model=ParseResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return await _ingest_uploaded_statement(file=file, db=db, owner_id=user_id)
