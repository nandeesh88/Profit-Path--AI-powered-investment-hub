from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date


class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    target_amount: float = Field(..., gt=0)
    current_amount: float = Field(default=0, ge=0)
    target_date: date
    category: Literal["Emergency Fund", "Retirement", "Education", "Home", "Travel", "Investment", "Other"] = "Other"
    priority: Optional[Literal["low", "medium", "high"]] = "medium"


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    target_date: Optional[date] = None
    category: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None


class GoalResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    target_amount: float
    current_amount: float
    progress_percentage: float
    target_date: date
    category: str
    priority: str = "medium"
    created_at: datetime
