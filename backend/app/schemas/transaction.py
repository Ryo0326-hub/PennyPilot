from pydantic import BaseModel
from typing import List


class ParsedTransaction(BaseModel):
    date: str
    merchant: str
    description: str
    amount: float
    direction: str
    category: str


class ParseResponse(BaseModel):
    filename: str
    statement_id: int
    row_count: int
    transactions: List[ParsedTransaction]