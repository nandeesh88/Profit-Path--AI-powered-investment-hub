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


class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[EXPENSE_CATEGORIES] = None
    date: Optional[date] = None


class ExpenseResponse(BaseModel):
    id: str
    user_id: str
    description: str
    amount: float
    category: str
    date: date
    created_at: datetime


class ExpenseSummary(BaseModel):
    total_expenses: float
    monthly_expenses: float
    average_expense: float
    expense_count: int
    by_category: dict
