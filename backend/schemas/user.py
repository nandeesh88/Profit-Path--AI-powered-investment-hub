from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    monthly_income: float = Field(default=0, ge=0)
    risk_tolerance: Literal["low", "medium", "high"] = "medium"
    financial_goal: str = Field(default="General savings", min_length=3, max_length=200)
    age: Optional[int] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    monthly_income: float
    risk_tolerance: str
    financial_goal: str
    age: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    name: Optional[str] = None
    monthly_income: Optional[float] = None
    risk_tolerance: Optional[Literal["low", "medium", "high"]] = None
    financial_goal: Optional[str] = None
    age: Optional[int] = None
