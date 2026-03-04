from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime


class InvestmentRequest(BaseModel):
    """User input for investment recommendations."""
    monthly_income: float = Field(..., gt=0, description="Monthly gross income in currency units")
    monthly_expenses: float = Field(..., ge=0, description="Monthly total expenses")
    savings: Optional[float] = Field(default=None, ge=0, description="Monthly savings (auto-calculated if not provided)")
    risk_tolerance: Literal["low", "medium", "high"] = Field(..., description="User's risk preference")
    financial_goal: str = Field(..., description="Investment goal (retirement, wealth creation, etc.)")
    age: Optional[int] = Field(default=30, ge=18, le=80, description="User's age in years")
    investment_horizon_years: Optional[int] = Field(default=5, ge=1, le=40, description="Investment time horizon")


class PortfolioAllocation(BaseModel):
    """Recommended portfolio allocation percentages."""
    stocks_percent: float = Field(..., ge=0, le=100)
    mutual_funds_percent: float = Field(..., ge=0, le=100)
    sip_percent: float = Field(..., ge=0, le=100)
    emergency_fund_percent: float = Field(..., ge=0, le=100)


class StockRecommendation(BaseModel):
    """Individual stock/equity recommendation."""
    category: str
    ticker: Optional[str] = None
    current_price: Optional[float] = None
    description: str
    risk_level: Literal["low", "medium", "high"]
    expected_return_range: str


class MutualFundRecommendation(BaseModel):
    """Mutual fund recommendation."""
    fund_type: str
    fund_name: Optional[str] = None
    description: str
    risk_level: Literal["low", "medium", "high"]
    expected_return_range: str


class SIPRecommendation(BaseModel):
    """Systematic Investment Plan (SIP) recommendation."""
    monthly_sip_amount: float
    recommended_fund: str
    expected_corpus_5yr: float
    expected_corpus_10yr: float


class InvestmentRecommendationResponse(BaseModel):
    """Complete investment recommendation response."""
    # User profiling
    user_segment: str = Field(..., description="User financial segment classification")
    risk_profile: Literal["low", "medium", "high"] = Field(..., description="Blended risk profile")
    ml_predicted_risk: Literal["low", "medium", "high"] = Field(..., description="ML model's risk prediction")
    
    # Financial analysis
    monthly_savings: float = Field(..., description="Computed monthly savings (income - expenses)")
    savings_rate_percent: float = Field(..., description="Savings as percentage of income")
    investable_amount: float = Field(..., description="Amount available for investment (80% of savings)")
    
    # Portfolio structure
    portfolio_allocation: PortfolioAllocation
    
    # Recommendations
    stock_recommendations: List[StockRecommendation]
    mutual_fund_recommendations: List[MutualFundRecommendation]
    sip_recommendation: SIPRecommendation
    
    # Return projections
    expected_return_percent: float = Field(..., description="Expected annual return percentage")
    investment_timeframe: Literal["short-term", "medium-term", "long-term"]
    
    # Guidance
    financial_advice: List[str] = Field(..., description="Personalized financial advice based on profile")
    market_context: Dict[str, Any] = Field(default_factory=dict, description="Current market metrics")
    
    # Metadata
    generated_at: datetime

