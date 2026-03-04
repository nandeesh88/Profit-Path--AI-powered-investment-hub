from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date


INCOME_SOURCES = Literal[
    "Salary",
    "Freelance",
    "Business",
    "Investment Returns",
    "Rental Income",
    "Side Hustle",
    "Other",
]


class IncomeCreate(BaseModel):
    amount: float = Field(..., gt=0)
    source: INCOME_SOURCES = "Salary"
    description: str = Field(default="", max_length=200)
    month: str = Field(..., pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="YYYY-MM format")


class IncomeUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    source: Optional[INCOME_SOURCES] = None
    description: Optional[str] = None
    month: Optional[str] = Field(None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$")


class IncomeResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    source: str
    description: str
    month: str
    created_at: datetime


class IncomeSummary(BaseModel):
    total_income: float
    average_monthly: float
    income_count: int
    by_month: dict
    by_source: dict
