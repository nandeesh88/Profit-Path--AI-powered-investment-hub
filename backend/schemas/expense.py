from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date


EXPENSE_CATEGORIES = Literal[
    "Food & Dining",
    "Transportation",
    "Housing",
    "Healthcare",
    "Entertainment",
    "Shopping",
    "Education",
    "Utilities",
    "Travel",
    "Other",
]


class ExpenseCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    category: EXPENSE_CATEGORIES
    date: date
    transaction_type: Literal["debit"] = "debit"
    bank_reference_id: Optional[str] = Field(default=None, max_length=80)
    source_document_id: Optional[str] = None


class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[EXPENSE_CATEGORIES] = None
    date: Optional[date] = None
    transaction_type: Optional[Literal["debit"]] = None
    bank_reference_id: Optional[str] = Field(default=None, max_length=80)
    source_document_id: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: str
    user_id: str
    description: str
    amount: float
    category: str
    date: date
    transaction_type: Literal["debit"] = "debit"
    bank_reference_id: Optional[str] = None
    source_document_id: Optional[str] = None
    created_at: datetime


class ExtractedTransaction(BaseModel):
    amount: float
    transaction_date: date
    merchant_name: str
    transaction_type: Literal["debit"] = "debit"
    bank_reference_id: Optional[str] = None
    is_duplicate: bool = False


class ExpenseExtractionResponse(BaseModel):
    upload_id: str
    filename: str
    transactions: list[ExtractedTransaction]


class ExpenseFromExtractionCreate(BaseModel):
    upload_id: str
    description: str = Field(..., min_length=1, max_length=200)
    amount: float = Field(..., gt=0)
    category: EXPENSE_CATEGORIES
    date: date
    transaction_type: Literal["debit"] = "debit"
    bank_reference_id: Optional[str] = Field(default=None, max_length=80)


class ExpenseSummary(BaseModel):
    total_expenses: float
    monthly_expenses: float
    average_expense: float
    expense_count: int
    by_category: dict
